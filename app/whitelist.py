#!/usr/bin/python
# -*- coding: UTF-8 -*-
from flask import request
from flask import jsonify
from flask import Blueprint
from flask import current_app
from global_function.self_white_list import *
from werkzeug import secure_filename
from global_function.log_oper import *
#flask-login
from flask_login.utils import login_required

ALLOWED_EXTENSIONS = set(['csv'])
LOAD_RULES_OPTIONS_NUM = 3
whitelist_page = Blueprint('whitelist_page', __name__,template_folder='templates')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


start_timer = threading.Timer(0, 0)
tmp_timer = threading.Timer(0, 0)


@whitelist_page.route('/whitelistDevice')
@login_required
def mw_whitelist_device():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    page = request.args.get('page', 0, type=int)
    data = []
    total = 0
    add_str = ' limit ' + str((page-1)*10)+',10;'
    sql_str = "select distinct SrcIp,SrcMac,proto from rules"+add_str
    result,rows = db_proxy.read_db(sql_str)
    for row in rows:
        row = list(row)
        tmp_name = get_devname_by_ipmac(row[0],row[1])
        row.insert(0,tmp_name)
        row.insert(0,0)
        data.append(row)
    sum_str = "SELECT count(*) from (select distinct SrcIp,SrcMac,proto from rules) as total"
    result,rows = db_proxy.read_db(sum_str)
    for s in rows:
        total=s[0]
    num_str = "select count(*) from rules"
    result,rows = db_proxy.read_db(num_str)
    num = rows[0][0]

    result,rows = db_proxy.read_db("select id from rules where deleted=1")
    tmp_check_list = []
    for sid in rows:
        tmp_check_list.append(sid[0])
    result, allinfo = db_proxy.read_db("select id from rules")
    tmp_all_list = []
    for sid in allinfo:
        tmp_all_list.append(sid[0])
    return jsonify({'rows': data, 'total': total, 'page': page, 'num': num, 'checklist': tmp_check_list, 'alllist': tmp_all_list})


@whitelist_page.route('/whitelistRes', methods=['GET', 'POST'])
@login_required
def mw_whitelist_res():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        page = request.args.get('page', 0, type=int)
        mac = request.args.get("mac")
        ip = request.args.get("ip")
        proto = request.args.get("proto", 0, type=int)
    elif request.method == 'POST':
        post_data = request.get_json()
        page = int(post_data['page'])
        proto = int(post_data['proto'])
        mac = post_data['mac']
        ip = post_data['ip']
    data = []
    total = 0
    add_str = ' limit ' + str((page-1)*10)+',10;'
    sql_str = "SELECT ruleName,fields,deleted,id FROM rules where srcIp='%s' and srcMac='%s' and proto=%d ORDER BY ruleId DESC %s" % (ip,mac,proto,add_str)
    result,rows = db_proxy.read_db(sql_str)
    for row in rows:
        row = list(row)
        if row[0].find('tls') != -1 :
            row[0] = row[0].replace('tls', 'https')
            row[1] = row[1].replace('tls', 'https')
        data.append(row)
    sum_str = "SELECT count(*) FROM rules where srcIp='%s' and srcMac='%s' and proto=%d" % (ip,mac,proto)
    result,rows = db_proxy.read_db(sum_str)
    for s in rows:
        total=s[0]
    return jsonify({'rows':data,'total':total,'page':page})


def white_list_stop_timer():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str ="update whiteliststudy set status=0 where id=1"
    result = db_proxy.write_db(sql_str)
    set_whitelist_study_status(0)
    switch_whitelist_status(0)
    sock = socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
    sock.sendto("2", dst_machine_learn_ctl_addr)


def white_list_start_timer(clear_flag):
    global tmp_timer
    set_whitelist_study_status(1)
    switch_whitelist_status(1)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    sock.sendto("1,%d"%clear_flag, dst_machine_learn_ctl_addr)


@whitelist_page.route('/whitelist-deviceip')
@login_required
def mw_whitelist_deviceip():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select ip from ipmaclist limit 1,-1"
    data = []
    result,rows = db_proxy.read_db(sql_str)
    for row in rows:
        data.append(row)
    return jsonify({'rows': data})


@whitelist_page.route('/whitelist-showdeviceinfo')
@login_required
def mw_whitelist_showdeviceinfo():
    sql_str = "select device_name,ip,mac from ipmaclist where is_study=1"
    data = []
    db_proxy = DbProxy(CONFIG_DB_NAME)
    result,rows = db_proxy.read_db(sql_str)
    for row in rows:
        data.append(row)
    return jsonify({'rows': data})


@whitelist_page.route('/whitelist-deleteIpMacStudy',methods=['GET', 'POST'])
@login_required
def mw_whitelist_deleteIpMacStudy():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        ip = request.args.get("ip")
    elif request.method == 'POST':
        post_data = request.get_json()
        ip = post_data['ip']
    sql_str = "update ipmaclist set is_study=0 where ip='%s'" % ip
    result = db_proxy.write_db(sql_str)
    return jsonify({'status': 1})


@whitelist_page.route('/whitelist-set-ipmacstudy',methods=['GET', 'POST'])
@login_required
def mw_whitelist_set_ipmacstudy():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        ip = request.args.get("ip")
    elif request.method == 'POST':
        post_data = request.get_json()
        ip = post_data['ip']
    sql_str = "update ipmaclist set is_study=1 where ip='%s'" % ip
    result = db_proxy.write_db(sql_str)
    return jsonify({'status':1})


@whitelist_page.route('/whiteliststartstudy', methods=['GET', 'POST'])
@login_required
def mw_whitelist_startstudy():
    ISOTIMEFORMAT='%Y-%m-%d %X'
    global start_timer
    global tmp_timer
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        start_time = request.args.get("start")
        dur_time = request.args.get("dur", 0, type=int)
        clear = request.args.get("flag", 0, type=int)
        loginuser = request.args.get('loginuser')
    else:
        post_data = request.get_json()
        start_time = post_data['start']
        dur_time = int(post_data['dur'])
        clear = int(post_data['flag'])
        loginuser = post_data['loginuser']
    timeArray = time.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(timeArray)
    timestamp += dur_time*60

    if int(timestamp) <= int(time.time()):
        return jsonify({'status': 1})

    sql_str = "update whiteliststudy set startTime='%s',durTime='%s',status=1 where id=1" % (start_time, str(dur_time))
    result = db_proxy.write_db(sql_str)
    update_sql_str = "UPDATE rules set deleted=0"
    result = db_proxy.write_db(update_sql_str)
    update_sql_str = "update ipmaclist set enabled=0 where ipmac_id>1"
    result = db_proxy.write_db(update_sql_str)
    update_sql_str = "update mac_filter set enable=0"
    result = db_proxy.write_db(update_sql_str)
    if clear == 1:
        clear_ipmac_str = "delete from ipmaclist where ipmac_id>1 and is_study=1"
        clear_top_str="delete from topdevice where is_study=1 and is_topo=0"
        # clear_topshow_str = "update topshow set xml_info='' where id=1"
        clear_whitelist_str="delete from rules"
        clear_macfilter_str = 'delete from mac_filter'
        result = db_proxy.write_db(clear_ipmac_str)
        result = db_proxy.write_db(clear_top_str)
        # result = db_proxy.write_db(clear_topshow_str)
        result = db_proxy.write_db(clear_whitelist_str)
        result = db_proxy.write_db(clear_macfilter_str)
    try:
        file_handle = open(WHITE_LIST_PATH,"w")
        file_handle.close()
        file_oper = open(IPMAC_LIST_PATH,"w")
        file_oper.close()
        file_oper = open(MAC_FILTER_PATH, "w")
        file_oper.close()
        # switch_ipmac_extraip(0)
        realod_all_rules()
        reload_macfilter_rules(db_proxy)
    except:
        current_app.logger.error("mw_whitelist_deleteall %s file oper error.", WHITE_LIST_PATH)
    ret = web_send_msg_to_commandhander({'type': 'scheduler', 'cmd': 'start_whitelist_study', 'starttime': start_time, 'duration': dur_time, 'clear': clear})

    # send operation log
    msg={}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = u"开启白名单规则自学习"
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    
    return jsonify(ret)


@whitelist_page.route('/whiteliststopstudy', methods=['GET', 'POST'])
@login_required
def mw_whitelist_stopstudy():
    global tmp_timer
    global start_timer
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str ="update whiteliststudy set status=0 where id=1"
    result = db_proxy.write_db(sql_str)
    set_whitelist_study_status(0)
    switch_whitelist_status(0)
    ret = web_send_msg_to_commandhander({'type': 'scheduler', 'cmd': 'stop_whitelist_study'})

    # send operation log
    msg={}
    userip = get_oper_ip_info(request)
    if request.method == 'GET':
        loginuser = request.args.get('loginuser')
    elif request.method == 'POST':
        post_data = request.get_json()
        loginuser = post_data['loginuser']
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = u"停止白名单规则自学习"
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify(ret)


@whitelist_page.route('/whiteliststatus')
@login_required
def mw_whitelist_status():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select startTime,durTime,status from whiteliststudy where id=1"
    result,rows = db_proxy.read_db(sql_str)
    start_time=""
    dur_time=0
    status=0
    flag=1
    try:
        for row in rows:
            start_time = row[0]
            dur_time = row[1]
            status = row[2]
    except:
        flag=0
    return jsonify({'status': flag, 'start': start_time, 'dur': dur_time, 'state': status})

@whitelist_page.route('/whitelistAddRes')
@login_required
def mw_whitelist_addres():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    page = request.args.get('addPage', 0, type=int)
    data = []
    tmp_all = request.args.get('isAll', 0, type=int)
    print tmp_all
    if tmp_all == 1:
        sql_str = "SELECT ruleName,action,riskLevel,id,fields FROM rules"
        result,rows = db_proxy.read_db(sql_str)
        for row in rows:
            data.append(row)
    else:
        add_str = ' limit ' + str((page-1)*10)+',10;'
        sql_str = "SELECT ruleName,action,riskLevel,id,fields FROM rules ORDER BY ruleId DESC" + add_str
        result,rows = db_proxy.read_db(sql_str)
        for row in rows:
            data.append(row)
    return jsonify({'rows': data})


@whitelist_page.route('/whitelistCheckAddRes')
@login_required
def mw_whitelist_checkaddres():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sids = request.args.get('sids')
    data = []
    sql_str = "SELECT ruleName,action,riskLevel,id,fields FROM rules where (1=2"
    tmp_sids = sids.split(",")
    for sid in tmp_sids:
        tmp_str = " or id="+sid
        sql_str += tmp_str
    sql_str += ")"
    result,rows = db_proxy.read_db(sql_str)
    for row in rows:
        data.append(row)
    return jsonify({'rows': data})

@whitelist_page.route('/whitelistUpdate', methods=['GET', 'POST'])
@login_required
def mw_whitelist_update():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        action = request.args.get('action', 0, type=int)
        risk = request.args.get('risk', 0, type=int)
        sid = request.args.get('sid')
    elif request.method == 'POST':
        post_data = request.get_json()
        action = int(post_data['action'])
        risk = int(post_data['risk'])
        sid = post_data['sid']
    sql_str = "update rules set action="+str(action)+",riskLevel="+str(risk)+" where id="+sid
    result = db_proxy.write_db(sql_str)
    return jsonify({'status': 1})


@whitelist_page.route('/whitelistSetAll', methods=['GET', 'POST'])
@login_required
def mw_whitelist_setall():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        sids = request.args.get('sids')
        action = request.args.get('action')
        loginuser = request.args.get('loginuser')
    elif request.method == 'POST':
        post_data = request.get_json()
        sids = post_data['sids']
        action = post_data['action']
        loginuser = post_data['loginuser']
    sql_str = "UPDATE rules set action="+action+" where id in("
    tmp_sids = sids.split(",")
    for sid in tmp_sids:
        sql_str += sid
        sql_str += ","
    sql_str = sql_str[:-1]+")"
    result = db_proxy.write_db(sql_str)
    send_deploy_cmd(TYPE_APP_SOCKET, "rules")
    realod_all_rules()
 # send operation log
    msg={}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = u"设置白名单规则的动作为:" + str(action)
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@whitelist_page.route('/whitelistDeploy', methods=['GET', 'POST'])
@login_required
def mw_whitelist_deploy():
    #send operation log
    msg={}
    userip = get_oper_ip_info(request)
    data = request.get_json()
    loginuser = data['loginuser']
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sta_str = "select status from whiteliststudy where id=1"
    result,rows = db_proxy.read_db(sta_str)
    tmp_status = rows[0][0]
    if tmp_status == 1:
        msg['Result'] = '1'
        msg['Operate'] = u"部署白名单规则"
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 2})

    sids = data['sids']
    status = data['status']
    if status == 1:
        clear_str = "update rules set deleted=0"
        result = db_proxy.write_db(clear_str)
        sql_str = "UPDATE rules set deleted=1 where id in(0,"
        for sid in sids:
            sql_str += "%s," % sid
        sql_str = sql_str[:-1]+")"
        result = db_proxy.write_db(sql_str)
        send_deploy_cmd(TYPE_APP_SOCKET, "rules")
        realod_all_rules()
        msg['Operate'] = u"部署白名单规则"
    else:
        sql_str = "delete from rules where id in(0,"
        for sid in sids:
            sql_str += "%s," % sid
        sql_str = sql_str[:-1]+")"
        result = db_proxy.write_db(sql_str)
        send_deploy_cmd(TYPE_APP_SOCKET, "rules")
        realod_all_rules()
        msg['Operate'] = u"删除白名单规则"

    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@whitelist_page.route('/whitelistShowDeploy')
@login_required
def mw_whitelist_showdeploy():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    page = request.args.get('page', 0, type=int)
    data = []
    total = 0
    add_str = ' limit ' + str((page-1)*10)+',10;'
    sql_str = "SELECT ruleName,fields,action,riskLevel FROM rules where deleted=1"+add_str
    result,rows = db_proxy.read_db(sql_str)
    for row in rows:
        data.append(row)
    sum_str = "SELECT count(*) FROM rules where deleted=1"
    result,rows = db_proxy.read_db(sum_str)
    for s in rows:
        total=s[0]
    return jsonify({'rows': data, 'total': total, 'page': page})


@whitelist_page.route('/whitelistClear', methods=['GET', 'POST'])
@login_required
def mw_whitelist_clear():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "UPDATE rules set deleted=0"
    result = db_proxy.write_db(sql_str)
    try:
        file_handle = open(WHITE_LIST_PATH, "w")
        file_handle.close()
    except:
        current_app.logger.error("mw_whitelist_clear %s file error.", WHITE_LIST_PATH)
    realod_all_rules()
	# send operation log
    msg={}
    userip = get_oper_ip_info(request)
    if request.method == 'GET':
        loginuser = request.args.get('loginuser')
    elif request.method == 'POST':
        post_data = request.get_json()
        loginuser = post_data['loginuser']
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = u"清空所有白名单部署规则"
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)   
    return jsonify({'status': 1})


def make_error_msg(err_list):
    error_msg = ""
    for err_info in err_list:
        error_msg = error_msg + str(err_info)
        error_msg = error_msg + ","
    error_msg = error_msg[0:-1]
    return "格式错误，请检查行:%s" % error_msg


def check_rulesfile_format(db_proxy, path):
    line_num = 0
    err_num = 0
    err_list = []
    err_msg = ""
    status = 0
    try:
        data = open(path).read()
        if data[:3] == codecs.BOM_UTF8:
            reader = csv.reader(codecs.open(path, 'rb','utf_8_sig'))
        else:
            reader = csv.reader(codecs.open(path, 'rb'))
    except:
        return status, err_msg
    try:
        for line in reader:
            line_num = line_num + 1
            if len(line) != LOAD_RULES_OPTIONS_NUM:
                err_num = err_num + 1
                err_list.append(line_num)
                if err_num >= 10:
                    err_msg = make_error_msg(err_list)
                    status = 1
                    return status, err_msg
                continue
            if int(line[1]) > 2 or int(line[1]) < 0:
                err_num = err_num + 1
                err_list.append(line_num)
                if err_num >= 10:
                    err_msg = make_error_msg(err_list)
                    status = 1
                    return status, err_msg
                continue
            if line[2]!= 'any':
                if int(line[2])< 1 or int(line[2])> 65535:
                    err_num = err_num + 1
                    err_list.append(line_num)
                    if err_num >= 10:
                        err_msg = make_error_msg(err_list)
                        status = 1
                        return status, err_msg
                    continue
            res = check_opercode_format(line[0])
            if res == 1:
                err_num = err_num + 1
                err_list.append(line_num)
                if err_num >= 10:
                    err_msg = make_error_msg(err_list)
                    status = 1
                    return status, err_msg
                continue
    except:
        status = 1
        err_msg = "文件内容错误"
        return status, err_msg
    if err_num > 0:
        status = 1
        err_msg = make_error_msg(err_list)
        return status, err_msg
    if line_num > 50000:
        status = 1
        err_msg = "规则总条数超过最大限制:50000条"
        return status, err_msg
    if line_num == 0:
        status = 1
        err_msg = "不能导入空文件"
        return status, err_msg
    return status, err_msg


def check_opercode_format(oper_info):
    status = 0
    try:
        flow_data_start = oper_info.find('{')
        flow_data_end = oper_info.rfind('}')
        flow_data_list = oper_info[flow_data_start + 1:flow_data_end]
        sip = oper_info.split(";")[0]
        dip = oper_info.split(";")[1]
        #global user_defined_device
        #user_defined_device.add(sip)
        #user_defined_device.add(dip)
        #if len(user_defined_device) > user_defined_max_num:
        #    return 2
        tmp_iplist = sip.split('-')
        if len(tmp_iplist)>1:
            compare_res = ipCompareValue(tmp_iplist[0],tmp_iplist[1])
            if compare_res !=0:
                status = 1
                return status
            for tmp_ip in tmp_iplist:
                if ipFormatChk(tmp_ip) == False and tmp_ip != 'any':
                    status = 1
                    return status
        tmp_iplist = dip.split('-')
        if len(tmp_iplist)>1:
            compare_res = ipCompareValue(tmp_iplist[0],tmp_iplist[1])
            if compare_res !=0:
                status = 1
                return status
            for tmp_ip in tmp_iplist:
                if ipFormatChk(tmp_ip) == False and tmp_ip != 'any':
                    status = 1
                    return status
        smac = oper_info.split(";")[2]
        dmac = oper_info.split(";")[3]
        if len(sip) == 0 and len(dip)==0 and len(smac) == 0 and len(dmac) == 0:
            status = 1
            return status
        if ipFormatChk(sip) == False or ipFormatChk(dip) == False:
            if len(sip) != 0 or len(dip)!=0:
                status = 1
                return status
        if macFormatChk(smac) == False or macFormatChk(dmac) == False:
            if len(smac) != 0 or len(dmac) != 0:
                status = 1
                return status
        #res, show_str = pangu_check_oper_content(flow_data_list)
        #if not res:
        #    status = 1
        #    return status
    except:
        status = 1
    return status


def ipFormatChk(ip_str):
    if ip_str == 'any':
        return True
    pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    if re.match(pattern, ip_str):
        return True
    return False


def macFormatChk(mac_str):
    if mac_str == 'any':
        return True
    #pattern = r"^\s*([0-9a-fA-F]{2,2}:){5,5}[0-9a-fA-F]{2,2}\s*$"
    pattern2 = r"^\s*([0-9a-fA-F]{2,2}){5,5}[0-9a-fA-F]{2,2}\s*$"
    #if re.match(pattern, mac_str):
    #    return True
    if re.match(pattern2, mac_str):
        return True
    else:
        return False


def ipCompareValue(ip1, ip2):
    lamba_str = lambda x:sum([256**j*int(i) for j,i in enumerate(x.split('.')[::-1])])
    try:
        val1 = lamba_str(ip1)
        val2 = lamba_str(ip2)
        if val1>val2:
            return 2
        elif val1 == val2:
            return 1
        else:
            return 0
    except:
        return -1


def insert_rules_from_file(db_proxy, path):
    sid = 300000
    try:
        data = open(path).read()
        if data[:3] == codecs.BOM_UTF8:
            reader = csv.reader(codecs.open(path, 'rb','utf_8_sig'))
        else:
            reader = csv.reader(codecs.open(path, 'rb'))
    except:
        current_app.logger.error("load files and insert customrules error")
    line_list = []
    proto_list = []
    clear_str = "delete from definedprotocol"
    db_proxy.write_db(clear_str)
    #modbus_oper_dict = get_modbus_oper_dict()
    for line in reader:
        if line[0] not in line_list:
            flow_data_start = line[0].find('{')
            flow_data_end = line[0].rfind('}')
            flow_data_db = line[0][flow_data_start + 1:flow_data_end]
            sip = line[0].split(";")[0]
            dip = line[0].split(";")[1]
            smac = line[0].split(";")[2]
            dmac = line[0].split(";")[3]
            data_rule = list_to_str(line[0].split(";")[4][1: line[0].split(";")[4].rfind('}')].split(','))
            protocol = data_rule.split(".")[0]
            if protocol == "goose" or protocol == "sv" or protocol == 'pnrtdcp':
                data_rule = data_rule.replace("whitelist", "L2whitelist")
                sip = smac
                dip = dmac
            if protocol == "opcda":
                protocol = "dcerpc"
            if protocol == "profinetio":
                protocol = "dcerpcudp"
            if protocol == "dcerpc":
                data_rule = data_rule.replace("dcerpc", "opcda")
            if protocol == "dcerpcudp":
                data_rule = data_rule.replace("dcerpcudp", "profinetio")
            tmp_protocol = protocol
            if line[2] != 'any':
                tmp_protocol +='_'
                tmp_protocol +=line[2]
            if protocol =='tcp' or protocol == 'udp':
                if tmp_protocol not in proto_list:
                    tmp_sql_str = "insert into definedprotocol (name,protocol,port) values('%s','%s','%s')"%(tmp_protocol,protocol,line[2])
                    db_proxy.write_db(tmp_sql_str)
                    proto_list.append(tmp_protocol)
            data_str = "%s %s %s any -> %s %s (%s; policy:1; sid:%d; rev:1;)" % (\
                ACTION_LIST[int(line[1])], protocol, sip, dip,line[2], data_rule, sid)
            data_str = base64.b64encode(data_str)
            filterfields_str = base64.b64encode(line[0])
            tmp_oper_start = data_rule.find('"')
            tmp_oper_end = data_rule.find('"',tmp_oper_start+1)
            tmp_oper = data_rule[tmp_oper_start+1:tmp_oper_end]
            #oper_code, flag = pangu_get_opercode(flow_data_db, modbus_oper_dict)
            sql_str = "insert into customrules (srcaddr,dstaddr,fields,filterfields,body,action,id,deleted,operation,port,protocol) values ('%s','%s','%s','%s','%s',%d,%d,1,'%s','%s','%s')" % (
                sip, dip, flow_data_db, filterfields_str, data_str, int(line[1]), sid, tmp_oper,line[2],tmp_protocol)
            db_proxy.write_db(sql_str)
            sid = sid + 1
            line_list.append(line[0])


def get_protocol_whitelist_content(proto):
    if proto == 'dcerpcudp':
        content = "profinetio.whitelist"
    elif proto == 'dcerpc':
        content = "opcda.whitelist"
    elif proto == 'goose' or proto == 'sv' or proto == 'pnrtdcp':
        content = "%s.L2whitelist" % proto
    else:
        content = "%s.whitelist" % proto
    return content


@whitelist_page.route('/add_new_white_rule', methods=['GET', 'POST'])
@login_required
def add_new_white_rule():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    # studying
    result, rows = db_proxy.read_db("select status from whiteliststudy where id=1")
    if rows[0][0] == 1:
        return jsonify({'status': 2})
    # max num: 10000
    result, rows = db_proxy.read_db("select count(*) from customrules")
    if rows[0][0] >= 50000:
        return jsonify({'status': 3})
    if request.method == 'GET':
        srcaddr = request.args.get('srcaddr').encode('utf-8')
        dstaddr = request.args.get('dstaddr').encode('utf-8')
        protocol = request.args.get('protocol').encode('utf-8')
        user_defined = request.args.get('user_defined', 0, type=int)
        action = request.args.get('action', 0, type=int)
    elif request.method == 'POST':
        post_data = request.get_json()
        srcaddr = post_data['srcaddr'].encode('utf-8')
        dstaddr = post_data['dstaddr'].encode('utf-8')
        protocol = post_data['protocol'].encode('utf-8')
        user_defined = int(post_data['user_defined'])
        action = int(post_data['action'])
    if len(srcaddr) == 0:
        srcaddr = "any"
    if len(dstaddr) == 0:
        dstaddr = "any"
    # protocol may be modbus or tcp_001, tcp_001 need to be translated protocol and port    
    if protocol == 'https' :
        protocol = 'tls'   
    port = "any"
    name = "undefined"
    if user_defined == 1:
        if request.method == 'GET':
            name = request.args.get('name').encode('utf-8')
            port = request.args.get('port').encode('utf-8')
        elif request.method == 'POST':
            name = post_data['name'].encode('utf-8')
            port = post_data['port'].encode('utf-8')
        # insert into user defined table
        result, rows = db_proxy.read_db("select count(*) from definedprotocol where name='%s' " % name)
        if rows[0][0] > 0:
            return jsonify({'status': 4})
        db_proxy.write_db("insert into definedprotocol (name, protocol, port) values ('%s', '%s', '%s')" % (name, protocol, port))
    elif user_defined == 2:
        result, rows = db_proxy.read_db("select protocol, port from definedprotocol where name='%s'" % protocol)
        name = protocol
        protocol = rows[0][0]
        port = rows[0][1]

    fields = "protocol:%s" % protocol
    time.sleep(3)
    result, max_id = db_proxy.read_db("select max(id) from customrules")
    max_id = max_id[0][0]
    if max_id is None:
        id = 300000
    else:
        id = max_id + 1
    # pass modbus 192.168.5.2 any -> 195.3.3.2 any (modbus.whitelist:"modbus.whitelist:"func:{3}|startaddr:{188}|endaddr:{199}|}""; policy:1; sid:300000; rev:1;)
    content = get_protocol_whitelist_content(protocol)
    if protocol == 'goose' or protocol == 'sv' or protocol == 'pnrtdcp':
        body = '''%s %s %s any -> %s %s (%s:""; policy:1; sid:%d; rev:1;)''' % (
            ACTION_LIST[action], protocol, srcaddr.replace(":", ""), dstaddr.replace(":",""), port, content, id)
        filter_fields = ";;%s;%s;{protocol:%s}" % (srcaddr.replace(":", ""), dstaddr.replace(":",""), protocol)
    else:
        body = '''%s %s %s any -> %s %s (%s:""; policy:1; sid:%d; rev:1;)''' % (
            ACTION_LIST[action], protocol, srcaddr, dstaddr, port, content, id)
        filter_fields = "%s;%s;;;{protocol:%s}" % (srcaddr, dstaddr, protocol)
    base64_body = base64.b64encode(body)
    base64_filter_fields = base64.b64encode(filter_fields)
    db_pro_list = [protocol, name, name]
    insert_sql = "insert into customrules (fields,body,action,deleted,id,filterfields,srcaddr,dstaddr,port,protocol,operation) \
    values ('%s','%s',%d,1,%d,'%s','%s','%s','%s','%s','')" % (
        fields, base64_body, action, id, base64_filter_fields, srcaddr.replace(":", ""), dstaddr.replace(":",""), port, db_pro_list[user_defined])
    db_proxy.write_db(insert_sql)
    send_deploy_cmd(TYPE_APP_SOCKET, "rules")
    realod_all_rules()
    return jsonify({'status': 1})


@whitelist_page.route('/manual_white_list_res')
@login_required
def manual_white_list_res():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    page = request.args.get('page', 0, type=int)
    limit_str = 'limit 10 offset %d' % ((page - 1) * 10)
    sql_str = "SELECT srcaddr,dstaddr,protocol,operation,action,deleted,id FROM customrules order by ruleId desc %s" % limit_str
    result, rows = db_proxy.read_db(sql_str)
    data = []
    l2_protocol = ['goose', 'sv', 'pnrtdcp']
    for row in rows :
        row = list(row)
        if row[2] == 'tls' :
            row[2] = 'https'
        elif row[2] in l2_protocol:
            if row[0] != "any":
                src_mac = []
                for i in range(0, 12, 2):
                    src_mac.append(row[0][i:i+2])
                row[0] = ':'.join(src_mac)
            if row[1] != "any":
                dst_mac = []
                for i in range(0, 12, 2):
                    dst_mac.append(row[1][i:i+2])
                row[1] = ':'.join(dst_mac)
        data.append(row)
    result, id_list = db_proxy.read_db("SELECT id FROM customrules")
    total = len(id_list)
    sid_list = []
    for sid in id_list:
        sid_list.append(sid[0])
    return jsonify({'rows': data, 'sid_list': sid_list, 'total': total, 'page': page})


@whitelist_page.route('/manual_white_list_deploy_one',methods=['GET', 'POST'])
@login_required
def manual_white_list_deploy_one():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    result, rows = db_proxy.read_db("select status from whiteliststudy where id=1")
    if rows[0][0] == 1:
        return jsonify({'status': 2})
    if request.method == 'GET':
        sid = request.args.get('sid', 0, type=int)
        status = request.args.get('status', 0, type=int)
    elif request.method == 'POST':
        post_data = request.get_json()
        sid = int(post_data['sid'])
        status = int(post_data['status'])
    sql_str = "UPDATE customrules set deleted=%d where id=%d" % (status, sid)
    db_proxy.write_db(sql_str)
    time.sleep(1)
    send_deploy_cmd(TYPE_APP_SOCKET, "rules")
    realod_all_rules()
    return jsonify({'status': 1})


@whitelist_page.route('/manual_white_list_delete_one',methods=['GET', 'POST'])
@login_required
def manual_white_list_delete_one():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    result, rows = db_proxy.read_db("select status from whiteliststudy where id=1")
    if rows[0][0] == 1:
        return jsonify({'status': 2})
    if request.method == 'GET':
        sid = request.args.get('sid', 0, type=int)
    elif request.method == 'POST':
        post_data = request.get_json()
        sid = int(post_data['sid'])
    sql_str = "delete from customrules where id=%d" % (sid)
    db_proxy.write_db(sql_str)
    time.sleep(1)
    send_deploy_cmd(TYPE_APP_SOCKET, "rules")
    realod_all_rules()
    return jsonify({'status': 1})


@whitelist_page.route('/manual_white_list_delete_some', methods=['GET', 'POST'])
@login_required
def manual_white_list_delete_some():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    result, rows = db_proxy.read_db("select status from whiteliststudy where id=1")
    if rows[0][0] == 1:
        return jsonify({'status': 2})
    data = request.get_json()
    sids = data['sids']
    sql_str = "delete from customrules where id in ("
    for sid in sids:
        sql_str += "%s," % sid
    sql_str = sql_str[:-1] + ")"
    db_proxy.write_db(sql_str)
    time.sleep(1)
    send_deploy_cmd(TYPE_APP_SOCKET, "rules")
    realod_all_rules()
    return jsonify({'status': 1})


@whitelist_page.route('/manual_white_list_action_update_one', methods=['GET', 'POST'])
@login_required
def manual_white_list_action_update():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    result, rows = db_proxy.read_db("select status from whiteliststudy where id=1")
    if rows[0][0] == 1:
        return jsonify({'status': 2})
    if request.method == 'GET':
        action = request.args.get('action', 0, type=int)
        sid = request.args.get('sid', 0, type=int)
    elif request.method == 'POST':
        post_data = request.get_json()
        action = int(post_data['action'])
        sid = int(post_data['sid'])
    sql_str = "update customrules set action=%d where id=%d" % (action, sid)
    db_proxy.write_db(sql_str)

    sel_cmd = "select deleted from customrules where id = %d" % (sid)
    result, res = db_proxy.read_db(sel_cmd)
    # this sid rule is on
    if res[0][0] == 1:
        send_deploy_cmd(TYPE_APP_SOCKET, "rules")
        realod_all_rules()
    return jsonify({'status': 1})


@whitelist_page.route('/manual_white_list_action_update_all', methods=['GET', 'POST'])
@login_required
def manual_white_list_action_update_all():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    result, rows = db_proxy.read_db("select status from whiteliststudy where id=1")
    if rows[0][0] == 1:
        return jsonify({'status': 2})
    if request.method == 'GET':
        act = request.args.get('action', 0, type=int)
    elif request.method == 'POST':
        post_data = request.get_json()
        act = int(post_data['action'])
    sql_str = "update customrules set action=%d " % act
    db_proxy.write_db(sql_str)
    send_deploy_cmd(TYPE_APP_SOCKET, "rules")
    realod_all_rules()
    return jsonify({'status': 1})


@whitelist_page.route('/edit_manual_white_list', methods=['GET', 'POST'])
@login_required
def edit_manual_white_list():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    # studying
    result, rows = db_proxy.read_db("select status from whiteliststudy where id=1")
    if rows[0][0] == 1:
        return jsonify({'status': 2})
    if request.method == 'GET':
        srcaddr = request.args.get('srcaddr').encode('utf-8')
        dstaddr = request.args.get('dstaddr').encode('utf-8')
        protocol = request.args.get('protocol').encode('utf-8')
        user_defined = request.args.get('user_defined', 0, type=int)
        action = request.args.get('action', 0, type=int)
        sid = request.args.get('sid', 0, type=int)
    elif request.method == 'POST':
        post_data = request.get_json()
        srcaddr = post_data['srcaddr'].encode('utf-8')
        dstaddr = post_data['dstaddr'].encode('utf-8')
        protocol = post_data['protocol'].encode('utf-8')
        user_defined = int(post_data['protocol'])
        action = int(post_data['action'])
        sid = int(post_data['sid'])
    if len(srcaddr) == 0:
        srcaddr = "any"
    if len(dstaddr) == 0:
        dstaddr = "any"
    
    if protocol == 'https' :
        protocol = 'tls'
    port = "any"
    name = "undefined"
    if user_defined == 1:
        if request.method == 'GET':
            name = request.args.get('name').encode('utf-8')
            port = request.args.get('port').encode('utf-8')
        elif request.method == 'POST':
            name = post_data['name'].encode('utf-8')
            port = post_data['port'].encode('utf-8')
        # insert into user defined table
        result, rows = db_proxy.read_db("select count(*) from definedprotocol where name='%s' " % name)
        if rows[0][0] > 0:
            return jsonify({'status': 4})
        db_proxy.write_db("insert into definedprotocol (name, protocol, port) values ('%s', '%s', '%s')" % (name, protocol, port))
    elif user_defined == 2:
        result, rows = db_proxy.read_db("select protocol, port from definedprotocol where name='%s'" % protocol)
        name = protocol
        protocol = rows[0][0]
        port = rows[0][1]

    # rule_edit(srcaddr, dstaddr, action, operation, sid)
    fields = "protocol:%s" % protocol
    content = get_protocol_whitelist_content(protocol)
    if protocol == 'goose' or protocol == 'sv' or protocol == 'pnrtdcp':
        body = '''%s %s %s any -> %s %s (%s:""; policy:1; sid:%d; rev:1;)''' % (
            ACTION_LIST[action], protocol, srcaddr.replace(":", ""), dstaddr.replace(":",""), port, content, sid)
        filter_fields = ";;%s;%s;{protocol:%s}" % (srcaddr.replace(":", ""), dstaddr.replace(":", ""), protocol)
    else:
        body = '''%s %s %s any -> %s %s (%s:""; policy:1; sid:%d; rev:1;)''' % (
            ACTION_LIST[action], protocol, srcaddr, dstaddr, port, content, sid)
        filter_fields = "%s;%s;;;{protocol:%s}" % (srcaddr, dstaddr, protocol)
    base64_body = base64.b64encode(body)
    base64_filter_fields = base64.b64encode(filter_fields)
    db_pro_list = [protocol, name, name]
    update_sql = "update customrules set fields='%s',body='%s',action=%d, filterfields='%s',srcaddr='%s',dstaddr='%s',\
    protocol='%s', port='%s' where id=%d" % (
        fields, base64_body, action, base64_filter_fields, srcaddr.replace(":", ""), dstaddr.replace(":", ""), db_pro_list[user_defined], port, sid)
    db_proxy.write_db(update_sql)

    sel_cmd = "select deleted from customrules where id = %d" % (sid)
    result, res = db_proxy.read_db(sel_cmd)
    # this sid rule is on
    if res[0][0] == 1:
        send_deploy_cmd(TYPE_APP_SOCKET, "rules")
        realod_all_rules()
    return jsonify({'status': 1})


@whitelist_page.route('/get_protocol_list')
@login_required
def get_protocol_list():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    result, rows = db_proxy.read_db("select * from definedprotocol")
    return jsonify({'rows': rows})


@whitelist_page.route('/delete_defined_protocol',methods=['GET', 'POST'])
@login_required
def delete_defined_protocol():
    if request.method == 'GET':
        name = request.args.get('name')
    elif request.method == 'POST':
        post_data = request.get_json()
        name = post_data['name']
    db_proxy = DbProxy(CONFIG_DB_NAME)
    db_proxy.write_db("delete from definedprotocol where name='%s'" % name)
    return jsonify({"status": 1})


@whitelist_page.route('/exportWhitelistRules')
@login_required
def mw_whitelist_export():
    custom_sql_str = "select filterfields,action,port from customrules;select filterfields,action from rules"
    data = send_file_cmd(TYPE_APP_SOCKET, custom_sql_str)
    status = 0
    if len(data) > 0:
        status = 1
    return jsonify({'status': status, 'filename': data})


@whitelist_page.route('/wlitelistUpload', methods=['GET', 'POST'])
@login_required
def mw_whitelist_load_file():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    result,rows = db_proxy.read_db("select status from whiteliststudy where id=1")
    if rows[0][0] == 1:
        return jsonify({'status': 3,'errmsg':"学习时不能导入白名单！"})
    error = None
    status = 0
    if request.method == 'POST':
        file = request.files['whitelist_define_fileUpload']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            res, err_msg = check_rulesfile_format(db_proxy,UPLOAD_FOLDER + filename)
            if res == 0:
                clear_sql_str = "delete from customrules"
                db_proxy.write_db(clear_sql_str)
                insert_rules_from_file(db_proxy,UPLOAD_FOLDER + filename)
                send_deploy_cmd(TYPE_APP_SOCKET, "rules")
                realod_all_rules()
                status = 1
            else:
                return jsonify({'status': status, 'errmsg': err_msg})
            return jsonify({'status': status, 'errmsg': err_msg})
        else:
            status = 2
            return jsonify({'status': status, 'errmsg': ""})
    status = 2
    return jsonify({'status': status, 'errmsg': ""})
