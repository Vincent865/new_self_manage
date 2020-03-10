#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
system backup FLASK module
author:HanFei
'''
import os
import sys
path = os.path.split(os.path.realpath(__file__))[0]
dirs = os.path.dirname(path)
sys.path.append(dirs)
from flask import request
from flask import jsonify
from flask import send_from_directory
from flask import Blueprint
from flask import current_app
from global_function.log_oper import *
#flask-login
from flask_login.utils import login_required




sysbackup_page = Blueprint('sysbackup_page', __name__, template_folder='templates')
SYS_CONF_MAX_NUM = 5


def sys_backup_init():
    '''
    system backup init function
    '''
    db_proxy = DbProxy(CONFIG_DB_NAME)
    os.system("mkdir -p /data/sysbackup")
    if g_dpi_plat_type == DEV_PLT_MIPS:
        os.system("mkdir -p /usr/local/etc/cron/crontabs/")
        os.system("touch %s" % CROND_PATH)
    sql_str = "select auto_enable from nsm_sysbackupmode"
    # res = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
    _, res = db_proxy.read_db(sql_str)
    if res is None or res == []:
        return
    else:
        mode = res[0][0]
        os.system("sed -ir '/.*sysbackup_proc.py.*/d' %s" % CROND_PATH)
        if mode == 1:
            os.system("echo \"0 0 * * 1 python %s/sysbackup_proc.pyc\" >> %s" % (APP_PY_PATH, CROND_PATH))
        os.system("crontab -c %s %s" % (CROND_CONF, CROND_PATH))

        return


def sys_backup_handle():
    '''
    system backup handle function
    '''
    ticks = int(time.time())
    time_str = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(ticks))
    date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ticks))
    child = subprocess.Popen("bash /usr/bin/config_backup.sh", shell=True)
    child.wait()
    path_str = "/data/sysbackup/" + "SYSCONF_" + time_str + ".tar.gz"
    rel_file = "SYSCONF_" + time_str + ".tar.gz"
    if os.path.exists(path_str) == True:
        os.system("rm -f %s" % path_str)
    child = subprocess.Popen("tar -zcf %s /shadow/config_bak/current/" % path_str, shell=True)
    child.wait()
    if os.path.exists(path_str) == True:
        db_proxy = DbProxy(CONFIG_DB_NAME)
        sql_str = "select count(*) from nsm_sysbackupinfo"
        res, sql_res = db_proxy.read_db(sql_str)
        if res == 0:
            total_num = sql_res[0][0]
        else:
            return 1
        if total_num >= SYS_CONF_MAX_NUM:
            sql_str = "select * from nsm_sysbackupinfo order by id asc limit 1"
            res, sql_res = db_proxy.read_db(sql_str)
            if res == 0:
                id_num = sql_res[0][0]
                filename = sql_res[0][2]
                os.system("rm -f %s" % filename)
                sql_str = "delete from nsm_sysbackupinfo where id = %d" % id_num
                db_proxy.write_db(sql_str)
            else:
                return 1
        sql_str = "insert into nsm_sysbackupinfo values(default,'%s','%s','%s','')" \
                  % (date_str, path_str, rel_file)
        db_proxy.write_db(sql_str)
        return 0
    else:
        return 1



@sysbackup_page.route('/sysBackupRes')
@login_required
def mw_sysbackup_res():
    '''
    get system backup info for UI
    '''
    page = request.args.get('page', 1, type=int)
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select * from nsm_sysbackupinfo order by id desc limit 10 offset %d" % ((page-1)*10)
    res1, sysbackup_info = db_proxy.read_db(sql_str)
    sql_str = "select count(*) from nsm_sysbackupinfo"
    res2, sql_res = db_proxy.read_db(sql_str)
    if res1 == 0 and res2 == 0:
        num = sql_res[0][0]
        return jsonify({'status': 1, 'rows': sysbackup_info, 'total':num, 'page':page})
    else:
        return jsonify({'status': 0, 'rows': [], 'total':0, 'page':page})


@sysbackup_page.route('/sysBackupModeRes')
@login_required
def mw_sysbackup_mode_res():
    '''
    get system backup mode for UI
    '''
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select auto_enable from nsm_sysbackupmode"
    # res = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
    _, res = db_proxy.read_db(sql_str)
    if res is None or res == []:
        return jsonify({'status': 0, "mode": 0})
    else:
        return jsonify({'status': 1, "mode": res[0][0]})


@sysbackup_page.route('/sysBackupSetmode', methods=['GET', 'POST'])
@login_required
def mw_sysbackup_setmode():
    '''
    set system backup mode for UI
    '''
    if request.method == 'GET':
        auto_flag = request.args.get('auto', 0, type=int)
        loginuser = request.args.get('loginuser','')
    else:
        post_data = request.get_json()
        auto_flag = int(post_data['auto'])
        loginuser = post_data.get('loginuser','')
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "update nsm_sysbackupmode set auto_enable = %d" % auto_flag
    # new_send_cmd(TYPE_APP_SOCKET, sql_str, 2)
    db_proxy.write_db(sql_str)

    print "sed -ir '/.*sysbackup_proc.py.*/d' %s" % CROND_PATH
    print "echo \"0 0 * * 1 python %s/sysbackup_proc.pyc\" >> %s" % (APP_PY_PATH, CROND_PATH)
    print "crontab %s" % CROND_PATH
    os.system("sed -ir '/.*sysbackup_proc.py.*/d' %s" % CROND_PATH)
    if auto_flag == 1:
        os.system("echo \"0 0 * * 1 python %s/sysbackup_proc.pyc\" >> %s" % (APP_PY_PATH, CROND_PATH))
    os.system("crontab -c %s %s" % (CROND_CONF, CROND_PATH))
    conf_save_flag_set()
    # send operation log
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    if auto_flag == 1:
        msg['Operate'] = "开启系统配置自动备份".decode("utf8")
    else:
        msg['Operate'] = "关闭系统配置自动备份".decode("utf8")
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})



@sysbackup_page.route('/sysBackuphdl')
@login_required
def mw_sysbackup_handle():
    '''
    manual system backup for UI
    '''
    sys_backup_handle()

    #send operation log
    msg={}
    userip = get_oper_ip_info(request)
    if request.method == 'GET':
        loginuser = request.args.get('loginuser','')
    elif request.method == 'POST':
        data = request.get_json()
        loginuser = data.get('loginuser', '')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = "进行手动系统配置备份".decode("utf8")
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    
    return jsonify({'status': 1})


@sysbackup_page.route('/sysbackupdownload/<file_name>', methods=['POST', 'GET'])
@login_required
def mw_sysbackup_download(file_name):
    '''
    system backup compressed file download
    '''
    curdir = "/data/sysbackup"

    #send operation log
    msg={}
    userip = get_oper_ip_info(request)
    loginuser = request.args.get('loginuser','')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = "下载备份系统配置文件,文件名:".decode("utf8") + str(file_name)
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    
    return send_from_directory(curdir, file_name, as_attachment=True)

@sysbackup_page.route('/sysBackupModDesc', methods=['POST', 'GET'])
@login_required
def mw_sysbackup_mod_desc():
    '''
    modify system backup file description
    '''
    try:
        if request.method == "GET":
            id_num = request.args.get('id', 0, type=int)
            unicode_str = request.args.get('desc', "")
        if request.method == "POST":
            post_data = request.get_json()
            id_num = int(post_data['id'])
            unicode_str = post_data['desc']

        utf8_str = unicode_str.encode("utf-8")
        db_proxy = DbProxy(CONFIG_DB_NAME)
        sql_str = "update nsm_sysbackupinfo set desc_text = '%s' where id = %d" % (utf8_str, id_num)
        db_proxy.write_db(sql_str)
        return jsonify({'status': 1})
    except:
        current_app.logger.exception("Exception Logged")
        return jsonify({'status': 0})

@sysbackup_page.route('/sysBackupDel')
@login_required
def mw_sysbackup_del():
    '''
    delete system backup info for UI
    '''
    try:
        id_str = request.args.get('id', "", type=str)
        id_list = id_str.split(",")
        option_str = "where 1 = 2"
        for elem in id_list:
            option_str += " or id = %d" % int(elem)

        db_proxy = DbProxy(CONFIG_DB_NAME)
        # delete the file
        sql_str = "select * from nsm_sysbackupinfo %s" % option_str
        res, sql_res = db_proxy.read_db(sql_str)
        for row in sql_res:
            os.system("rm -f %s" % row[2])
        # delete the db.table
        sql_str = "delete from nsm_sysbackupinfo %s" % option_str
        db_proxy.write_db(sql_str)

        #send operation log
        msg={}
        userip = get_oper_ip_info(request)
        if request.method == 'GET':
            loginuser = request.args.get('loginuser','')
        elif request.method == 'POST':
            data = request.get_json()
            loginuser = data.get('loginuser', '')
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['Operate'] = "删除备份系统配置文件, id=".decode("utf8") + str(id_str)
        msg['ManageStyle'] = 'WEB'
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)

        return jsonify({'status': 1})
    except:
        current_app.logger.exception("Exception Logged")
        return jsonify({'status': 0})


