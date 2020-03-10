#!/usr/bin/python
# -*- coding:UTF-8 -*-
from flask import render_template
from flask import request
from flask import jsonify
from flask import Blueprint
from global_function.global_var import *
#flask-login
from flask_login.utils import login_required

loginlog_page = Blueprint('loginlog_page', __name__,template_folder='templates')

'''
@loginlog_page.route('/getLogCount')
def mw_count_log():
    db_proxy = DbProxy()
    login_str = "SELECT count(*) from dpiuserlogins inner join operationlogs opl on opl.operationLogId=dpiuserlogins.operationLogId"
    oper_str =  "SELECT count(*) from dpiuseroperationlogs inner join operationlogs opl on opl.operationLogId=dpiuseroperationlogs.operationLogId"

    result,rows = db_proxy.read_db(login_str)
    for s in rows:
        loginlog_num=s[0]

    result,rows = db_proxy.read_db(oper_str)
    for s in rows:
        operlog_num=s[0]
    return jsonify({'loginlog_num':loginlog_num,'operlog_num':operlog_num})    
 '''   
    
@loginlog_page.route('/loginLogRes')
@login_required
def mw_loginlog_res():
    db_proxy = DbProxy()
    page = request.args.get('page', 0, type=int)
    data = []
    total = 0
    add_str = ' limit ' + str((page-1)*10)+',10;'
    sql_str = "SELECT dpiuserlogins.timestamp,user,user_ip,login_result,reason from dpiuserlogins inner join operationlogs opl on opl.operationLogId=dpiuserlogins.operationLogId order by dpiuserlogins.timestamp desc"+add_str
    result,rows = db_proxy.read_db(sql_str)
    for row in rows:
        data.append(row)
    sum_str = "SELECT count(*) from dpiuserlogins inner join operationlogs opl on opl.operationLogId=dpiuserlogins.operationLogId"
    result,rows = db_proxy.read_db(sum_str)
    for s in rows:
        total=s[0]
    return jsonify({'rows':data,'total':total,'page':page})

@loginlog_page.route('/loginLogExportData')
@login_required
def mw_loginlog_exportdata():
    sql_cmd = 'SELECT dpiuserlogins.timestamp,user,user_ip,login_result,reason from dpiuserlogins inner join operationlogs opl on opl.operationLogId=dpiuserlogins.operationLogId'
    data = send_file_cmd(TYPE_EVENT_SOCKET,sql_cmd)
    return jsonify({'status':1,'filename':data})

@loginlog_page.route('/loginLogSearch',methods=['GET', 'POST'])
@login_required
def mw_loginlog_search():
    db_proxy = DbProxy()
    data = []
    if request.method == 'GET':
        start_time = request.args.get('starttime')
        end_time = request.args.get('endtime')
        ip = request.args.get('ip')
        user = request.args.get('user')
        status = request.args.get('status')
        reason = request.args.get('reason')
        page = request.args.get('page', 0, type=int)
    elif request.method == 'POST':
        post_data = request.get_json()
        start_time = post_data['start_time']
        endtime = post_data['endtime']
        ip = post_data['ip']
        user = post_data['user']
        status = post_data['status']
        reason = post_data['reason']
        page = post_data['page']
    
    add_str = ' limit ' + str((page-1)*10)+',10;'
    sql_str = "SELECT dpiuserlogins.timestamp,user,user_ip,login_result,reason from dpiuserlogins inner join operationlogs opl on opl.operationLogId=dpiuserlogins.operationLogId "
    sum_str = "SELECT count(*) from dpiuserlogins inner join operationlogs opl on opl.operationLogId=dpiuserlogins.operationLogId "
    option_str = "where 1=1"
    if len(start_time)>0:
        startarr = start_time.split(' ')
        start_time = startarr[0] + 'T' + startarr[1] + 'Z'        
        option_str += " and dpiuserlogins.timestamp>"+"\""+start_time+"\""
    if len(end_time)>0:
        endarr = end_time.split(' ')
        end_time = endarr[0] + 'T' + endarr[1] + 'Z'        
        option_str += " and dpiuserlogins.timestamp<"+"\""+end_time+"\""
    if len(ip)>0:
        option_str += " and user_ip like "+"\"%"+ip+"%\""
    if len(user)>0:
        option_str += " and user like "+"\"%"+user+"%\""
    if len(status)>0:
        option_str += " and login_result="+"\""+status+"\""
    if len(reason)>0:
        option_str += " and reason like "+"\"%"+reason+"%\""
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