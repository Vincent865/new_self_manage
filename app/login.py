#!/usr/bin/python
# -*- coding:UTF-8 -*-
import ctypes
import hashlib

from flask import render_template
from flask import request
from flask import jsonify
from flask import Blueprint
from flask import current_app
from werkzeug.security import check_password_hash
from global_function.log_oper import *
from global_function.global_var import *

from flask_login.utils import login_required, login_user, logout_user


login_page = Blueprint('login_page', __name__, template_folder='templates')


@login_page.route("/")
def mw_login():
    return render_template('/login.html')


@login_page.route("/logout")
@login_required
def logout():
    loginuser = request.args.get("loginuser")
    userip = get_oper_ip_info(request)
    if get_log_switch():
        send2icsp_content = LOGIN_CONTENT % (loginuser, userip)
        send_logout_to_icsp(send2icsp_content)
    logout_user()
    return render_template('/login.html')


@login_page.route('/getUser')
@login_required
def mw_getuser():
    name = request.args.get('username')
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select name,lockedAt from users where name='%s'" % name
    # rows = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
    _, rows = db_proxy.read_db(sql_str)
    if len(rows) == 0:
        return jsonify({'status': 0})
    if rows[0][1] != 0:
        return jsonify({'status': 0})
    return jsonify({'status': 1})

def check_pin_valid(pin_val):
    so = ctypes.CDLL('/lib/x86_64-linux-gnu/libukey.so')
    res = so.sfw_ukey_verify(pin_val)
    return res

PIN_ERRORCODE = ('成功', 'ukey认证失败', '没有发现ukey', 'ukey认证失败', 'ukey认证失败')

@login_page.route('/checkUser', methods=['GET', 'POST'])
def mw_checkUser():
    try:
        db_proxy = DbProxy(CONFIG_DB_NAME)
        post_data = request.get_json()
        username = post_data['username']
        password = post_data['pw']

        userip = get_oper_ip_info(request)
        values = None
        msg = {}
        msg['UserIP'] = get_oper_ip_info(request)
        msg['UserName'] = username
        msg['Operate'] = u'用户网页登录'
        msg['ManageStyle'] = 'WEB'
        
        reset_web_pw_or_not(username, db_proxy)

        result, auth_values = db_proxy.read_db("SELECT auth_switch FROM ukey_auth")
        if result != 0 or len(auth_values) == 0:
            return jsonify({'status': 0})

        auth_active = auth_values[0][0]

        getpw_cmd = "SELECT userId,passwordHash,logoutTime,loginAttemptCount,updatedAt,lockedAt,last_update FROM users where name='{}'".format(username)
        _, rows = db_proxy.read_db(getpw_cmd)
        if len(rows) != 0:
            values = rows[0]
        if values is None:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            current_app.logger.error("login username is not exist,login fail")
            if get_log_switch():
                send2icsp_content = LOGIN_CONTENT % (msg['UserName'], msg['UserIP'])
                send_login_failed_to_icsp(send2icsp_content)
            return jsonify({'status': 0, 'msg': u'用户不存在'})
        dbPwHash = values[1]
        res = None
        leftAttemptTimes = values[4]
        lockedAt = values[5]
        loginAttemptCount = values[3]
        last_update = values[6]
        if last_update:
            time_now = int(time.time() * 1000)
            if time_now - int(last_update) < 31000 and (time_now - int(last_update) > 0):
                return jsonify({"status": -1, "msg": u"该账号已登录,请退出后重试"})

        if leftAttemptTimes <= 0:
            nowtime = int(time.time())
            if lockedAt == 0:
                # locked,update lockedAt
                after5min = nowtime + 5 * 60
                update_lockedAt="update users set lockedAt=%d where name='%s'" % (after5min, username)
                db_proxy.write_db(update_lockedAt)
                return jsonify({'status': 1})
            else:
                if nowtime < lockedAt:
                    return jsonify({'status': 1, 'msg': u'账号处于锁定状态'})
                else:
                    # after 5 mins,release the lock
                    update_cmd = "UPDATE users set lockedAt=0,updatedAt=%s " \
                                 "where name='%s'" % (str(loginAttemptCount), username)
                    db_proxy.write_db(update_cmd)
                    leftAttemptTimes = loginAttemptCount

        auth_result = 0
        checkResult = True
        if auth_active == 1:
            pin_val = post_data['pin']
            auth_result = check_pin_valid(str(pin_val))
            if auth_result == 0:
                checkResult = check_password_hash(dbPwHash, password)
            else:
                checkResult = False
        else:
            checkResult = check_password_hash(dbPwHash, password)

        login_result = checkResult and "0" or "1"
        msg['Result'] = str(login_result)
        send_log_db(MODULE_OPERATION, msg)
        #set session attributes
        if checkResult == True:
            login_info = {}
            curTime = datetime.datetime.now()
            curTime = str(curTime).split('.')[0]
            # update_cmd = "UPDATE users set lastLogin=" + "\"" + curTime + "\"" + " where name=" + "\"" + username + "\""
            # new_send_cmd(TYPE_APP_SOCKET, update_cmd, 2)
            update_cmd = "UPDATE users set lastLogin='%s' where name='%s'" % (curTime, username)
            db_proxy.write_db(update_cmd)
            # rows = new_send_cmd(TYPE_APP_SOCKET, "SELECT userId,name,lastLogin, authority FROM users where name="+ "\"" + username + "\"", 1)
            _, rows = db_proxy.read_db("SELECT userId,name,lastLogin, authority FROM users where name='%s'" % username)
            login_info['username'] = rows[0][1]
            login_info['userId'] = rows[0][0]
            login_info['lastLogin'] = rows[0][2]
            # login_info['authority'] = rows[0][3]
            m = hashlib.md5()
            m.update(str(rows[0][2]) + str(rows[0][3]))
            login_info['authority'] = m.hexdigest()
            # rows = new_send_cmd(TYPE_APP_SOCKET, "SELECT logoutTime FROM users where userId=1", 1)
            _, rows = db_proxy.read_db("SELECT logoutTime FROM users where userId=1")
            login_info['logouttime'] = rows[0][0]
            # set logout time
            # rows = new_send_cmd(TYPE_APP_SOCKET, "SELECT mode FROM managementmode", 1)
            _, rows = db_proxy.read_db("SELECT mode FROM managementmode")
            login_info['mode'] = rows[0][0]
            login_info['runmode'] = RUN_MODE
            # update_cmd = "UPDATE users set lockedAt=0,updatedAt=" + str(loginAttemptCount) + " where name=" + "\"" + username + "\""
            update_cmd = "UPDATE users set lockedAt=0,updatedAt=%s where name='%s'" % (str(loginAttemptCount), username)
            # new_send_cmd(TYPE_APP_SOCKET, update_cmd, 2)
            db_proxy.write_db(update_cmd)
            user = User(login_info['userId'])
            login_user(user,remember = False)
            # add judge pwd aging code
            # edit_rows = new_send_cmd(TYPE_APP_SOCKET, "select editAt from users where name=" + "\"" + username + "\"", 1)
            _, edit_rows = db_proxy.read_db("select editAt from users where name='%s'" % username)
            try:
                edit_time = int(edit_rows[0][0])
            except:
                edit_time = None
            current_app.logger.info(edit_time)
            if not edit_time:
                return jsonify({'status': 2, 'msg': u'登陆成功'}, login_info=login_info)
            db = DbProxy(CONFIG_DB_NAME)
            sql_str = "select valid_type from pwd_aging"
            res, row = db.read_db(sql_str)
            type_time = 0
            if res == 0:
                type_time = int(row[0][0])
            now_time = int(time.time())
            if type_time == 1:
                time_long = 1 * 365 * 24 * 60 * 60
            elif type_time == 3:
                time_long = 3 * 30 * 24 * 60 * 60
            elif type_time == 6:
                time_long = 6 * 30 * 24 * 60 * 60
            else:
                if get_log_switch():
                    send2icsp_content = LOGIN_CONTENT % (msg['UserName'], msg['UserIP'])
                    send_login_success_to_icsp(send2icsp_content)
                current_app.logger.info("login success.")
                return jsonify({'status': 2, 'msg': u'登陆成功'}, login_info=login_info)
            current_app.logger.info(type_time)
            if now_time - edit_time >= time_long:
                current_app.logger.info("now_time - edit_time >= time_long")
                login_info["redirect"] = 1
                return jsonify({'status': 4, 'msg': u'密码超出时效'}, login_info=login_info)
            else:
                if get_log_switch():
                    send2icsp_content = LOGIN_CONTENT % (msg['UserName'], msg['UserIP'])
                    send_login_success_to_icsp(send2icsp_content)
                return jsonify({'status': 2, 'msg': u'登陆成功'}, login_info=login_info)
        else:
            #try:
            leftAttemptTimes = leftAttemptTimes-1
            update_cmd = "UPDATE users set updatedAt=" + str(leftAttemptTimes) + " where name=" + "\"" + username + "\""
            # new_send_cmd(TYPE_APP_SOCKET, update_cmd, 2)
            db_proxy.write_db(update_cmd)
        if get_log_switch():
            send2icsp_content = LOGIN_CONTENT % (msg['UserName'], msg['UserIP'])
            send_login_failed_to_icsp(send2icsp_content)
        if auth_result != 0:
            return jsonify({'status': 7, 'msg': PIN_ERRORCODE[auth_result], 'times': leftAttemptTimes})
        else:
            return jsonify({'status': 3, 'msg': leftAttemptTimes})
    except:
        current_app.logger.exception(traceback.format_exc())
        return jsonify({'status': 5, 'msg': u'登陆失败'})


def reset_web_pw_or_not(username, db_proxy):
    if username == "sysadmin" and os.path.exists('/data/reset_pw_flag'):
        pw_hash = "pbkdf2:sha1:1000$WYaD510N$2cd3c6284017fa21b67d6a776316c9923036c9d9"
        # updatedAt:剩余登录次数，lockedAt：解锁时间，
        reset_cmd = "update users set updatedAt=5, lockedAt=0, passwordHash='%s' where name='sysadmin'" % pw_hash
        # new_send_cmd(TYPE_APP_SOCKET,reset_cmd,2)
        db_proxy.write_db(reset_cmd)
        os.system("rm -f /data/reset_pw_flag")
        # 防止修改后立即点击不能进入
        time.sleep(3)

    if username == "admin" and os.path.exists('/data/reset_pw_flag'):
        pw_hash = "pbkdf2:sha1:1000$tQb14ujW$cba216b49e1a0bd23e309566fac50c9da98a8892"
        # updatedAt:剩余登录次数，lockedAt：解锁时间，
        reset_cmd = "update users set updatedAt=5, lockedAt=0, passwordHash='%s' where name='admin'" % pw_hash
        # new_send_cmd(TYPE_APP_SOCKET,reset_cmd,2)
        db_proxy.write_db(reset_cmd)
        os.system("rm -f /data/reset_pw_flag")
        # 防止修改后立即点击不能进入
        time.sleep(3)    
