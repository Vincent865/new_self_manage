#!/usr/bin/python
# -*- coding:UTF-8 -*-
from flask import render_template
from flask import request
from flask import jsonify
from flask import Blueprint
from global_function.global_var import *
#flask-login
from flask_login.utils import login_required

operlog_page = Blueprint('operlog_page', __name__, template_folder='templates')


@operlog_page.route('/getLogCount')
@login_required
def mw_count_log():
    db_proxy = DbProxy()
    oper_str =  "SELECT count(*) from dpiuseroperationlogs inner join operationlogs opl on opl.operationLogId=dpiuseroperationlogs.operationLogId"
    result,rows = db_proxy.read_db(oper_str)
    for s in rows:
        operlog_num=s[0]
    sys_str =  "SELECT count(*) from events"
    result,rows = db_proxy.read_db(sys_str)
    for s in rows:
        syslog_num=s[0]
    return jsonify({'operlog_num': operlog_num, 'syslog_num': syslog_num})


@operlog_page.route('/operLogRes')
@login_required
def mw_operlog_res():
    db_proxy = DbProxy()
    page = request.args.get('page', 0, type=int)
    data = []
    total = 0
    add_str = ' limit ' + str((page-1)*10)+',10;'
    sql_str = "SELECT dpiuseroperationlogs.timestamp,user,user_ip,oper,oper_result from dpiuseroperationlogs inner join operationlogs opl on opl.operationLogId=dpiuseroperationlogs.operationLogId order by dpiuseroperationlogs.timestamp desc"+add_str
    result,rows = db_proxy.read_db(sql_str)
    for row in rows:
        data.append(row)
    sum_str = "SELECT count(*) from dpiuseroperationlogs inner join operationlogs opl on opl.operationLogId=dpiuseroperationlogs.operationLogId"
    result,rows = db_proxy.read_db(sum_str)
    for s in rows:
        total=s[0]
    return jsonify({'rows':data,'total':total,'page':page})


@operlog_page.route('/operLogExportData')
@login_required
def mw_operlog_exportdata():
    sql_cmd = 'SELECT dpiuseroperationlogs.timestamp,user,user_ip,oper,oper_result from dpiuseroperationlogs inner join operationlogs opl on opl.operationLogId=dpiuseroperationlogs.operationLogId order by dpiuseroperationlogs.timestamp desc'
    data = send_file_cmd(TYPE_EVENT_SOCKET,sql_cmd)
    return jsonify({'status':1,'filename':data})


@operlog_page.route('/operLogSearch', methods=['GET', 'POST'])
@login_required
def mw_operlog_search():
    db_proxy = DbProxy()
    data = []
    if request.method == 'GET':
        start_time = request.args.get('starttime')
        end_time = request.args.get('endtime')
        ip = request.args.get('ip')
        user = request.args.get('user')
        oper = request.args.get('oper')
        oper_result = request.args.get('oper_result')    
        start_time = start_time.encode('utf-8')
        end_time = end_time.encode('utf-8')
        ip = ip.encode('utf-8')
        user = user.encode('utf-8')
        oper = oper.encode('utf-8')
        oper_result = oper_result.encode('utf-8')
        page = request.args.get('page', 0, type=int)
    elif request.method == 'POST':
        post_data = request.get_json()
        start_time = post_data['starttime'].encode('utf-8')
        end_time = post_data['endtime'].encode('utf-8')
        ip = post_data['ip'].encode('utf-8')
        user = post_data['user'].encode('utf-8')
        oper = post_data['oper'].encode('utf-8')
        oper_result = post_data['oper_result'].encode('utf-8')
        page = post_data['page']
    
    add_str = ' limit ' + str((page-1)*10)+',10;'
    sql_str = "SELECT dpiuseroperationlogs.timestamp,user,user_ip,oper,oper_result from dpiuseroperationlogs inner join operationlogs opl on opl.operationLogId=dpiuseroperationlogs.operationLogId "
    sum_str = "SELECT count(*) from dpiuseroperationlogs inner join operationlogs opl on opl.operationLogId=dpiuseroperationlogs.operationLogId "
    option_str = "where 1=1 "
    if len(start_time)>0:
        startarr = start_time.split(' ')
        start_time = startarr[0] + 'T' + startarr[1] + 'Z'        
        option_str += " and dpiuseroperationlogs.timestamp>"+"\""+start_time+"\""
    if len(end_time)>0:
        endarr = end_time.split(' ')
        end_time = endarr[0] + 'T' + endarr[1] + 'Z'
        option_str += " and dpiuseroperationlogs.timestamp<"+"\""+end_time+"\""
    if len(ip)>0:
        option_str += " and user_ip like "+"\"%"+ip+"%\""
    if len(user)>0:
        option_str += " and user like "+"\"%"+user+"%\""
    if len(oper)>0:
        option_str += " and oper like "+"\"%"+oper+"%\""
    if len(oper_result)>0:
        option_str += " and oper_result="+"\""+oper_result+"\""
    option_str += " order by dpiuseroperationlogs.timestamp desc"
    sql_str+=option_str
    sql_str+=add_str
    result,rows = db_proxy.read_db(sql_str)
    for row in rows:
        data.append(row)
    sum_str+=option_str
    result,rows = db_proxy.read_db(sum_str)
    for s in rows:
        total=s[0]
    return jsonify({'rows':data,'total':total,'page':page})
