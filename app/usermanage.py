#!/usr/bin/python
# -*- coding: UTF-8 -*-
from flask import request
from flask import jsonify
from flask import Blueprint
from flask import session
from flask import current_app
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from global_function.log_oper import *
#flask-login
from flask_login.utils import login_required
import time


usermanage_page = Blueprint('usermanage_page', __name__,template_folder='templates')


@usermanage_page.route('/getAllUser')
@login_required
def mw_getAllUser():
    page = request.args.get('page', 0, type=int)
    #cursor = conn.cursor()
    #try:
    #   cursor.execute("SELECT userId,name,lastLogin FROM users")
    #except sqlite3.Error,e:
    #   logging.error("mw_getAllUser SELECT all user error.")
    #values = cursor.fetchall()
    db_proxy = DbProxy(CONFIG_DB_NAME)
    try:
        # values = new_send_cmd(TYPE_APP_SOCKET, "SELECT userId,name,lastLogin, authority, editAt FROM users", 1)
        _, values = db_proxy.read_db("SELECT userId,name,lastLogin, authority, editAt FROM users")
        values = list(values)
        value_list = []
        for value in values:
            value = list(value)
            if value[4]:
                tl = time.localtime(int(value[4]))
                value[4] = time.strftime("%Y-%m-%d %H:%M:%S", tl)
            else:
                pass
            value_list.append(value)
        total = len(value_list)
        current_app.logger.info("getAllUser all user success.")
        return jsonify({'rows': value_list, 'total': total, 'page': page})
    except:
        current_app.logger.error("mw_getAllUser SELECT all user error.")
        current_app.logger.error(traceback.format_exc())
        return


@usermanage_page.route('/addUser', methods=['GET', 'POST'])
@login_required
def mw_addUser():
    if request.method == 'GET':
        username = request.args.get('user')
        password = request.args.get('password')
        loginuser = request.args.get('loginuser')
        authority = int(request.args.get('authority'))
    else:
        data = request.get_json()
        username = data['user']
        password = data['password']
        loginuser = data['loginuser']
        authority = data['authority']
    db_proxy = DbProxy(CONFIG_DB_NAME)
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = u"添加用户:" + username
    msg['ManageStyle'] = 'WEB'
    
    #check user num in db
    # rows = new_send_cmd(TYPE_APP_SOCKET, "select count(*) from users", 1)
    _, rows = db_proxy.read_db("select count(*) from users")
    userNum = rows[0][0]
    if userNum > 10:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 0})
    #check if have the username already
    time.sleep(3)
    sel_cmd = "select count(*) from users where name=" + "\"" + username + "\""
    # rows = new_send_cmd(TYPE_APP_SOCKET,sel_cmd,1)
    _, rows = db_proxy.read_db(sel_cmd)
    isExist = rows[0][0]
    if isExist > 0:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 1})

    #get logoutTime,loginAttemptCount,pwSafeLevel from authority
    # rows = new_send_cmd(TYPE_APP_SOCKET,"select logoutTime,loginAttemptCount,pwSafeLevel from users where authority='1'",1)
    _, rows = db_proxy.read_db("select logoutTime,loginAttemptCount,pwSafeLevel from users where authority='1'")
    safepara = rows[0]
    #add user to db
    password = generate_password_hash(password)
    edit_time = int(time.time())
    current_app.logger.info(edit_time)
    add_cmd = "INSERT INTO users (name,passwordHash,lastLogin,logoutTime,loginAttemptCount,pwSafeLevel,updatedAt,lockedAt,authority,editAt) values(\
        " + "\"" + username + "\"," + "\"" + password + "\"," + "\"" + "---" + "\","+ str(safepara[0]) + ",\
        " + str(safepara[1])+ "," + str(safepara[2]) + ","+ str(safepara[1]) + ",\"" + str(0) + "\"," + str(authority) + ",\"" + str(edit_time) + "\"" + ")"
    current_app.logger.info(add_cmd)
    # new_send_cmd(TYPE_APP_SOCKET,add_cmd,2)
    db_proxy.write_db(add_cmd)
    conf_save_flag_set()
    
    #send log to mysql db
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 2})

@usermanage_page.route('/changePassword', methods=['GET', 'POST'])
@login_required
def mw_changePassword():
    data = request.get_json()
    username = data['username']
    old_pw = data['oldpwd']
    new_pw = data['newpwd']
    db_proxy = DbProxy(CONFIG_DB_NAME)

    #send log to mysql db
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = username
    msg['UserIP'] = userip
    oper_str = u"修改用户:" + username + u" 密码"
    msg['Operate'] = oper_str
    msg['ManageStyle'] = 'WEB'
    
    check_str = "select passwordHash from users where name='%s'"%(username)
    # rows = new_send_cmd(TYPE_APP_SOCKET, check_str, 1)
    _, rows = db_proxy.read_db(check_str)
    tmp_res = None
    try:
        tmp_pwd = rows[0][0]
        tmp_res = check_password_hash(tmp_pwd,old_pw)   
    except:
        tmp_res = False
    if tmp_res==False:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status':0})
    new_pw = generate_password_hash(new_pw)
    change_cmd = "UPDATE users set passwordHash='%s' where name='%s'"%(new_pw,username)
    # new_send_cmd(TYPE_APP_SOCKET,change_cmd,2)
    db_proxy.write_db(change_cmd)
    edit_time = int(time.time())
    change_time_cmd = "UPDATE users set editAt='%s' where name='%s'"%(str(edit_time),username)
    # new_send_cmd(TYPE_APP_SOCKET, change_time_cmd, 2)
    db_proxy.write_db(change_time_cmd)
    conf_save_flag_set()

    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status':1})

@usermanage_page.route('/deleteUser')
@login_required
def mw_deleteUser():
    id = request.args.get('id')
    db_proxy = DbProxy(CONFIG_DB_NAME)
    # get usename for userId
    check_str = "select name from users where userId=" + id
    # username = new_send_cmd(TYPE_APP_SOCKET,check_str,1)
    _, username = db_proxy.read_db(check_str)

    # delete user info
    del_str = "delete from users where userId=" + id
    # new_send_cmd(TYPE_APP_SOCKET, del_str, 2)
    db_proxy.write_db(del_str)
    conf_save_flag_set()

    #send log to mysql db
    msg={}
    loginuser = request.args.get('loginuser')
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    oper_str = u"删除用户: " + str(username[0][0])
    msg['Operate'] = oper_str
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status':1})

@usermanage_page.route('/userLogout')
@login_required
def mw_userLogout():
    #send log to mysql db
    msg={}
    userip = get_oper_ip_info(request)
    loginuser = request.args.get('loginuser')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    oper_str = u"退出登录"
    msg['Operate'] = oper_str
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)

    session.pop('username', None)
    return jsonify({'status':1})

@usermanage_page.route('/getPwSafeLevel')
@login_required
def mw_getPwSafeLevel():
    sel_cmd = "select pwSafeLevel from users where authority='1'"
    #try:
    #   cursor.execute(sel_cmd)
    #except sqlite3.Error,e:
    #   logging.error("mw_getPwSafeLevel sel_cmd error.sel_cmd=%s",sel_cmd)
    db_proxy = DbProxy(CONFIG_DB_NAME)
    # rows = new_send_cmd(TYPE_APP_SOCKET, sel_cmd, 1)
    _, rows = db_proxy.read_db(sel_cmd)
    pwSafeLevel = rows[0][0]
    return jsonify({'pwSafeLevel':pwSafeLevel})


@usermanage_page.route('/pwd_aging', methods=['GET', 'POST'])
@login_required
def pwd_valid_type():
    db = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        sql_str = "select * from pwd_aging"
        res, rows = db.read_db(sql_str)
        if rows:
            type = int(rows[0][0])
        else:
            type = 0
        return jsonify({"type": type})
    else:
        data = request.get_json()
        type = int(data.get("type", 0))
        loginuser = data.get("loginuser")
        msg={}
        userip=get_oper_ip_info(request)
        msg['UserName']=loginuser
        msg['UserIP']=userip
        msg['ManageStyle']='WEB'
        msg['Operate']=u'设置密码时效'
        msg['Result']='0'
        try:
            sql_str = "update pwd_aging set valid_type=%d"%type
            res = db.write_db(sql_str)
            if res == 0:
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({"status": 1})
            else:
                msg['Result']='1'
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({"status": 0})
        except:
            msg['Result']='1'
            send_log_db(MODULE_OPERATION, msg)
            current_app.logger.error(traceback.format_exc())
            current_app.logger.error("set password validType error.")
            return jsonify({"status": 0})
