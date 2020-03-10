# coding:utf-8
from flask import render_template
from flask import request
from flask import jsonify
from flask import send_from_directory
from flask import Blueprint
from global_function.global_var import *
#flask-login
from flask_login.utils import login_required

from global_function.log_oper import send_log_db, MODULE_OPERATION

sysevent_page = Blueprint('sysevent_page', __name__,template_folder='templates')

@sysevent_page.route('/sysEventRes')
@login_required
def mw_sysEvent_res():
    db_proxy = DbProxy()
    page = request.args.get('page', 0, type=int)
    data = []
    total = 0
    add_str = ' LIMIT 10 OFFSET ' + str((page-1)*10)
    sql_str = "SELECT level,type,timestamp,content,eventID FROM events order by timestamp desc "+add_str
    
    result,rows = db_proxy.read_db(sql_str)
    for row in rows:
        data.append(row)
    sum_str = "SELECT count(*) FROM events"
    result,rows = db_proxy.read_db(sum_str)
    for s in rows:
        total=s[0]

    return jsonify({'rows':data,'total':total,'page':page})


@sysevent_page.route('/sysEventSearch', methods=['GET', 'POST'])
@login_required
def mw_sysevent_search():
    db_proxy = DbProxy()
    data = []
    if request.method == 'GET':  
        start_time = request.args.get('starttime')
        start_time = start_time.encode('utf-8')   
        end_time = request.args.get('endtime')
        end_time = end_time.encode('utf-8')       
        level = request.args.get('level')
        level = level.encode('utf-8')
        content = request.args.get('content')
        content = content.encode('utf-8')
        page = request.args.get('page', 0, type=int)
    elif request.method == 'POST':
        post_data = request.get_json()
        start_time = post_data['starttime'].encode('utf-8')
        end_time = post_data['endtime'].encode('utf-8')
        level = post_data['level'].encode('utf-8')      
        content = post_data['content'].encode('utf-8')
        page = post_data['page']
    
    add_str = ' order by timestamp desc LIMIT 10 OFFSET ' + str((page-1)*10)
    sql_str = "SELECT  level,type,timestamp,content,status,eventId FROM events "
    sum_str = "SELECT count(*) from events "
    option_str = "where 1=1"
    if len(start_time)>0:
        startarr = start_time.split(' ')
        start_time = startarr[0] + 'T' + startarr[1] + 'Z'        
        option_str += " and timestamp>"+"\""+start_time+"\""
    if len(end_time)>0:
        endarr = end_time.split(' ')
        end_time = endarr[0] + 'T' + endarr[1] + 'Z'
        option_str += " and timestamp<"+"\""+end_time+"\""
    if len(level)>0 and level != "3":
        option_str += " and level="+"\""+level+"\""
    #if len(status)>0:
    #    option_str += " and status="+"\""+status+"\""
    if len(content)>0 and content != "all":
        option_str += " and content like "+"\"%"+content+"%\""
    sql_str+=option_str
    sum_str+=option_str
    sql_str+=add_str
    result,rows = db_proxy.read_db(sql_str)

    for row in rows:
        data.append(row)
    result,rows = db_proxy.read_db(sum_str)
    for s in rows:
        total=s[0]
    return jsonify({'rows':data,'total':total,'page':page})

@sysevent_page.route('/sysEventExportData')
@login_required
def mw_sysevent_exportdata():
    sql_cmd = 'select timestamp,level,type,content from events order by timestamp desc'
    data = send_file_cmd(TYPE_EVENT_SOCKET,sql_cmd)
    return jsonify({'status':1,'filename':data})

@sysevent_page.route('/download/<file_name>', methods=['POST', 'GET'])
@login_required
def download(file_name):
    curdir = "/data/download"
    msg={}
    userip=get_oper_ip_info(request)
    loginuser=request.args.get('loginuser')
    msg['UserName']=loginuser
    msg['UserIP']=userip
    msg['ManageStyle']='WEB'
    msg['Result']='0'
    if "operlog" in file_name:
        msg['Operate']=u'导出操作日志'
        send_log_db(MODULE_OPERATION, msg)
    if "sysevent" in file_name:
        msg['Operate']=u'导出系统日志'
        send_log_db(MODULE_OPERATION, msg)
    return send_from_directory(curdir, file_name, as_attachment=True)

@sysevent_page.route('/sysEventClearTag')
@login_required
def mw_sysevent_cleartag():
    db_proxy = DbProxy()
    delete_cmd = "DELETE FROM events"
    result = db_proxy.write_db(delete_cmd)
    return jsonify({'status':1})
