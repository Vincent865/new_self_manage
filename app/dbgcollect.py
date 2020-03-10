#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Debug info collect Flask
author: HanFei
'''
import sys
sys.path.append("..")
from flask import jsonify
from flask import request
from flask import send_from_directory
from flask import Blueprint
from global_function.log_oper import *
#flask-login
from flask_login.utils import login_required

dbgcollect_page = Blueprint('dbgcollect_page', __name__, template_folder='templates')


@dbgcollect_page.route('/dbgCollectRes')
@login_required
def mw_dbgcollect_res():
    '''
    Show debug collect info for UI
    '''
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select * from nsm_dbgcollect"
    res, sql_res = db_proxy.read_db(sql_str)
    if res == 0:
        timestamp = sql_res[0][0]
        status = sql_res[0][1]
        filename = sql_res[0][2]
        rel_file = sql_res[0][3]
        return jsonify({'status': 1, 'timestamp': timestamp, "collectstatus": status,
                        'filename': filename, "rel_file": rel_file})
    else:
        return jsonify({'status': 0, 'timestamp': "", "collectstatus": 0,
                        'filename': "", "rel_file": ""})


@dbgcollect_page.route('/dbgdownload/<file_name>', methods=['POST', 'GET'])
@login_required
def mw_dbg_download(file_name):
    '''
    dbg collect info download
    '''
    curdir = "/data/dbg_collect"
    return send_from_directory(curdir, file_name, as_attachment=True)


@dbgcollect_page.route('/dbgCollectReq')
@login_required
def mw_dbgcollect_req():
    '''
    Receive dbg collect handle req from UI
    '''
    timestamp, status, filename, rel_file = dbgcollect_proc()
    # send operation log
    msg = {}
    userip = get_oper_ip_info(request)
    loginuser = request.args.get('loginuser')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = "执行调试信息收集".decode("utf8")
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1, 'timestamp': timestamp, "collectstatus": status,
                    'filename': filename, "rel_file": rel_file})


def dbgcollect_proc():
    '''
    dbg collect handle
    '''
    # summary one hour data and delete one week ago data
    start_time = int(time.time())
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
    path_str = "/data/dbg_collect"
    origin_path = "/tmp/debug_log"
    if os.path.exists(path_str) is True:
        file_list = os.listdir(path_str)
        for elem in file_list:
            del_file = path_str + "/" + elem
            os.remove(del_file)
    else:
        os.mkdir(path_str)
    child = subprocess.Popen("bash /usr/bin/troubleshooting_debug.sh 127.0.0.1 sn0001 1",
                             shell=True)
    child.wait()
    status = 0
    gz_file = ""
    if os.path.exists(origin_path) == True:
        file_list = os.listdir(origin_path)
        for elem in file_list:
            if ".tar.gz" in elem:
                os.system("cd %s && cp *.tar.gz %s" % (origin_path, path_str))
                gz_file = elem
                status = 1
                break
    if status == 1:
        abs_path = path_str + "/" + gz_file
    else:
        abs_path = ""
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "update nsm_dbgcollect set timestamp = '%s', collect_status = %d, \
               collect_file = '%s', rel_file = '%s'" \
               % (timestamp, status, abs_path, gz_file)
    db_proxy.write_db(sql_str)
    return timestamp, status, abs_path, gz_file








