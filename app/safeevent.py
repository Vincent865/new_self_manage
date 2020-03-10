#!/usr/bin/python
# -*- coding: UTF-8 -*-
from flask import render_template
from flask import request
from flask import Response
from flask import jsonify
from flask import Blueprint
from flask import current_app
from global_function.log_oper import *
import time
import logging
#flask-login
from flask_login.utils import login_required

safeevent_page = Blueprint('safeevent_page', __name__, template_folder='templates')

RISK_LOW = 0
RISK_MID = 1
RISK_HIG = 2
RISK_UNKNOW = 3
SIG_WHITELIST = 1
SIG_BLACKLIST = 2
SIG_IPMAC = 3
SIG_TRAFFIC = 4
SIG_MACFILTER = 5
SIG_DEV = 6
SIG_ANOMAL_PCAP = 7


@safeevent_page.route('/trafficEventRecordDetail')
@login_required
def mw_traffic_event_recorddetail():
    db_proxy = DbProxy()
    record_id = request.args.get('recordid')
    table_num = request.args.get('tablenum')
    # 字段复用：protocolDetail-180个时间点，signatureMessage-180个值，dpiIp-低阈值，boxId-高阈值，memo-当前流量值
    sel_cmd = "select protocolDetail,signatureMessage,dpiIp,boxId,memo,timestamp " \
              "from incidents_%s where incidentId=%s" % (table_num, record_id)
    result, rows = db_proxy.read_db(sel_cmd)
    time_list = eval(rows[0][0])
    real_time_points = [time_elem.split(' ')[1] for time_elem in time_list]
    bytes_list = eval(rows[0][1])
    bytes_list = [float(val) for val in bytes_list]
    alarm_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(rows[0][5])))
    alarm_val = float(rows[0][4])
    max_bytes = float(max(bytes_list))
    if max_bytes < float(rows[0][3]):
        max_bytes = float(rows[0][3])
    return jsonify({'time_list': real_time_points, 'bytes_list': bytes_list, 'low': float(rows[0][2]),
                    'high': float(rows[0][3]), 'traffic': float(rows[0][4]), 'max': max_bytes,
                    'alarm_time': alarm_time, 'alarm_val': alarm_val})


@safeevent_page.route('/devEventRecordDetail')
@login_required
def mw_devevent_recorddetail():
    db_proxy = DbProxy()
    record_id = request.args.get('recordid')
    table_num = request.args.get('tablenum')
    sql_str = "select timestamp,sourceName,dpi,matchedKey,action from incidents_%s " \
              "where incidentId=%s" % (table_num, str(record_id))
    _, rows = db_proxy.read_db(sql_str)
    return jsonify({'rows': rows})

@safeevent_page.route('/safeEventDetail')
@login_required
def mw_safeevent_detail():
    db_proxy = DbProxy()
    recordid = request.args.get('recordid')
    table_num = request.args.get('tablenum')
    try:
        sel_cmd = "select action,timestamp,matchedKey from incidents_%s where incidentId=%s" % (table_num, str(recordid))
        result, rows = db_proxy.read_db(sel_cmd)
        values = []
        if result == 0 and len(rows[0]) > 0:
            for row in rows:
                row = list(row)
                row[1] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row[1])))
                values.append(row)
            return jsonify({'values':values[0],'status':1})
    except:
        current_app.logger.error("get safeEventRecordDetail error.")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'status':1})

@safeevent_page.route('/safeEventRecordDetail')
@login_required
def mw_safeevent_recorddetail():
    db_proxy = DbProxy()
    recordid = request.args.get('recordid')
    table_num = request.args.get('tablenum')
    sel_cmd = "select action,signatureName,timestamp,protocol,appLayerProtocol,protocolDetail," \
              "signatureMessage,matchedKey,packetLength,packet " \
              "from incidents_%s where incidentId=%s" % (table_num, str(recordid))
    values = []
    try:
        # rows = incident_send_read_cmd(TYPE_EVENT_SOCKET,sel_cmd)
        result, rows = db_proxy.read_db(sel_cmd)
        for row in rows:
            row = list(row)
            row[1] = int(row[1])
            if row[1] == SIG_TRAFFIC:                 #流量告警：低级
                row[1] = RISK_LOW
            elif row[1] == SIG_WHITELIST or row[1] == SIG_IPMAC or row[1] == SIG_MACFILTER or row[1] == SIG_ANOMAL_PCAP:          #白名单，IPMAC：中级
                row[1] = RISK_MID
            elif row[1] == SIG_BLACKLIST:               #黑名单：高级
                row[1] = RISK_HIG
            else:
                row[1] = RISK_MID
            row[2] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row[2])))
            if row[4] == 'tls':
                row[4] = 'https'
                row[5] = row[5].replace('tls', 'https')
            values.append(row)

        packstr = values[0][9]
        values[0] = list(values[0])
        del values[0][9]
        current_app.logger.info("get safeEventRecordDetail success.")
        return jsonify({'values': values[0], 'packstr': packstr})
    except:
        current_app.logger.error("get safeEventRecordDetail error.")
        current_app.logger.error(traceback.format_exc())
        return


def get_search_option(start_time, end_time, action, sourceIp, destinationIp, appLayerProtocol, status, signatureName, srcDevName, dstDevName, riskLevel):
    option_str = ""
    if len(start_time) > 0:
        start_time_int = int(time.mktime(time.strptime(start_time,'%Y-%m-%d %H:%M:%S')))
        option_str += " and timestamp >= " + str(start_time_int)
    if len(end_time) > 0:
        end_time_int = int(time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M:%S')))
        option_str += " and timestamp < " + str(end_time_int)
    if len(action) > 0 and action != "0":
        option_str += " and action=" + "\"" + action + "\""
    if len(sourceIp) > 0:
        if ":" in sourceIp:
            item_list = sourceIp.split(":")
            mac_flag = True
            for i in item_list:
                if len(i) > 2:
                    mac_flag = False
                    break
            if item_list[1:-1]:
                for i in item_list[1:-1]:
                    if len(i) != 2:
                        mac_flag = False
                        break
            if mac_flag:
                smac = sourceIp.replace(":", "")
                option_str += " and (dpi like " + "\"" + sourceIp + "%\"" + "or dpi like " + "\"%" + smac + "%\")"
            else:
                option_str+=" and dpi like " + "\"" + sourceIp + "%\""
        else:
            option_str+=" and dpi like " + "\"" + sourceIp + "%\""
    if len(destinationIp) > 0:
        if ":" in destinationIp:
            item_list=destinationIp.split(":")
            mac_flag=True
            for i in item_list:
                if len(i) > 2:
                    mac_flag=False
                    break
            if item_list[1:-1]:
                for i in item_list[1:-1]:
                    if len(i) != 2:
                        mac_flag=False
                        break
            if mac_flag:
                dmac=destinationIp.replace(":", "")
                option_str+=" and (dpiName like " + "\"" + destinationIp + "%\"" + "or dpiName like " + "\"%" + dmac + "%\")"
            else:
                option_str+=" and dpiName like " + "\"" + destinationIp + "%\""
        else:
            option_str += " and dpiName like " + "\"" + destinationIp + "%\""
    if len(status) > 0:
        option_str += " and status=" + "\"" + status + "\""
    if len(appLayerProtocol) > 0 and appLayerProtocol != 'null':
        if appLayerProtocol == 'https':
            appLayerProtocol = 'tls'
        option_str += " and appLayerProtocol= '%s' " % appLayerProtocol
    if len(signatureName) > 0 and signatureName != "0":
        option_str += " and signatureName=" + "\"" + signatureName + "\""
    if len(riskLevel) > 0:
        if int(riskLevel) == RISK_LOW:
            option_str += " and signatureName in ('%s')"%(SIG_TRAFFIC)
        elif int(riskLevel) == RISK_MID:
            option_str += " and signatureName in ('%s','%s','%s','%s','%s')"%(SIG_WHITELIST,SIG_IPMAC,SIG_MACFILTER,SIG_DEV,SIG_ANOMAL_PCAP)
        elif int(riskLevel) == RISK_HIG:
            option_str += " and signatureName in ('%s')"%(SIG_BLACKLIST)
    if len(srcDevName) > 0 and srcDevName != "0":
        tmp_str = ""
        first_flag = 1
        src_ipmac_list = get_ipmac_list_by_devname(srcDevName.encode("UTF-8"))
        # current_app.logger.info("src_ipmac_list: " + str(src_ipmac_list))
        for elem in src_ipmac_list:
            if first_flag == 0:
                tmp_str += " or "
            first_flag = 0

            if elem[0] == "any":
                src_ip_str = " sourceIp like \"" + "%%" + "\""
            elif elem[0] == "":
                src_ip_str = " sourceIp = '' "
            else:
                src_ip_str = " sourceIp = \"" + elem[0] + "\""

            if elem[1] == "any":
                src_mac_str = " sourceMac like \"" + "%%" + "\""
            elif elem[1] == "":
                src_mac_str = " sourceMac = '' "
            else:
                src_mac_str=" sourceMac = \"" + elem[1].replace(":", "") + "\""

            tmp_str += "(" + src_ip_str + " and " + src_mac_str + ")"

        if tmp_str != "":
            option_str += " and (" + tmp_str + ")"
    if len(dstDevName) > 0 and dstDevName != "0":
        tmp_str = ""
        first_flag = 1
        dst_ipmac_list = get_ipmac_list_by_devname(dstDevName.encode("UTF-8"))
        for elem in dst_ipmac_list:
            if first_flag == 0:
                tmp_str += " or "
            first_flag = 0

            if elem[0] == "any":
                dst_ip_str = " destinationIp like \"" + "%%" + "\""
            elif elem[0] == "":
                dst_ip_str = " destinationIp = '' "
            else:
                dst_ip_str = " destinationIp = \"" + elem[0] + "\""

            if elem[1] == "any":
                dst_mac_str = " destinationMac like \"" + "%%" + "\""
            elif elem[1] == "":
                dst_mac_str = " destinationMac = '' "
            else:
                dst_mac_str=" destinationMac = \"" + elem[1].replace(":", "") + "\""
            tmp_str += "(" + dst_ip_str + " and " + dst_mac_str + ")"
        if tmp_str != "":
            option_str += " and (" + tmp_str + ")"
    return option_str


@safeevent_page.route('/safeEventSearch', methods=['GET', 'POST'])
@login_required
def mw_safeevent_search():
    try:
        db_proxy = DbProxy()
        data = []
        total = 0
        if request.method == "GET":
            start_time = request.args.get('starttime')
            end_time = request.args.get('endtime')
            action = request.args.get('action')
            sourceIp = request.args.get('sourceIp')
            destinationIp = request.args.get('destinationIp')
            appLayerProtocol = request.args.get('appLayerProtocol')
            status = request.args.get('status')
            signatureName = request.args.get('signatureName','')
            srcDevName = request.args.get('sourceName','')
            dstDevName = request.args.get('destinationName','')
            riskLevel = request.args.get('riskLevel','')
            page = request.args.get('page', 0, type=int)

        if request.method == "POST":
            post_data = request.get_json()
            start_time = post_data['starttime']
            end_time = post_data['endtime']
            action = post_data['action']
            sourceIp = post_data['sourceIp']
            destinationIp = post_data['destinationIp']
            appLayerProtocol = post_data['appLayerProtocol']
            status = post_data['status']
            signatureName = post_data['signatureName']
            srcDevName = post_data['sourceName']
            dstDevName = post_data['destinationName']
            riskLevel = post_data['riskLevel']
            page = int(post_data['page'])

        # 时间戳存在重复问题,出现重复的安全事件,采用timestampint排序可以避免该问题
        add_str = ' order by timestampint desc LIMIT 10 OFFSET ' + str((page-1)*10)
        sql_str = "SELECT timestampint FROM incidents "
        content_sql_str = "SELECT  sourceIp,destinationIp,appLayerProtocol,timestamp,action,status,incidentId,tableNum,signatureName,deviceId,sourceMac, destinationMac,signatureId, dpi, dpiName FROM incidents "
        sum_str = "SELECT count(*) from incidents "
        option_str = "where 1=1"
        option_str += get_search_option(start_time, end_time, action, sourceIp, destinationIp, appLayerProtocol, status,
                                        signatureName, srcDevName, dstDevName, riskLevel)
        sql_str+=option_str
        sum_str+=option_str
        unread_str=sum_str + ' and status=0'
        sql_str+=add_str
        current_app.logger.info("safeEventSearch sql_str:%s" % (sql_str))

        result,rows = db_proxy.read_db(sql_str)
        time_str_list = [row[0] for row in rows]
        time_str = str(tuple(time_str_list)).replace("L","")

        if time_str_list == []:
            return jsonify({'rows':[],'total':0,'page':page})
        else:
            if time_str[-2] == ",":
                time_str = time_str[0:-2] + ")"
            content_sql_str = content_sql_str + " where timestampint in " + time_str + " order by timestampint desc limit 10"

        # current_app.logger.info(content_sql_str)
        result, rows = db_proxy.read_db(content_sql_str)
        # 读出的数据web显示处理
        for row in rows:
            row = list(row)
            if row[2] == 'tls':
                row[2] = 'https'
            row[3] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row[3])))
            row[8] = int(row[8])
            if row[8] == SIG_TRAFFIC:                 #流量告警：低级
                riskLevel = RISK_LOW
            elif row[8] == SIG_IPMAC or row[8] == SIG_WHITELIST or row[8] == SIG_MACFILTER or row[8] == SIG_ANOMAL_PCAP:          #白名单，IPMAC,MACFILTER：中级
                riskLevel = RISK_MID
            elif row[8] == SIG_BLACKLIST:               #黑名单：高级
                riskLevel = RISK_HIG
            else:
                riskLevel = RISK_MID

            # add dev_name info
            if( "." not in row[0]) and (":" not in row[0]):
                src_ip_str = ""
            else:
                src_ip_str = row[0]
            src_mac_str = row[10]
            src_dev_name = get_devname_by_ipmac(src_ip_str, src_mac_str)

            if( "." not in row[1]) and (":" not in row[1]):
                dst_ip_str = ""
            else:
                dst_ip_str = row[1]
            dst_mac_str = row[11]
            dst_dev_name = get_devname_by_ipmac(dst_ip_str, dst_mac_str)
            # 源地址放在后边赋值以免影响通过ip和mac获取设备名称
            row[0] = row[13] or "NA"
            row[1] = row[14] or "NA"
            row = row[:-2]

            if ('.' not in row[0]) and (len(row[0])<18):
                if ":" not in row[0]:
                    row[0] = (':'.join(row[0][i:i + 2] for i in range(0, len(row[0]), 2))).upper()
                else:
                    row[0] = row[0].upper()
            if ('.' not in row[1]) and (len(row[1])<18):
                if ":" not in row[1]:
                    row[1] = (':'.join(row[1][i:i + 2] for i in range(0, len(row[1]), 2))).upper()
                else:
                    row[1] = row[1].upper()
            row.extend([src_dev_name, dst_dev_name, riskLevel])
            data.append(row)

        rows = send_read_cmd(TYPE_EVENT_SOCKET, sum_str)
        for s in rows:
            total = s[0]

        result, rows = db_proxy.read_db("select sum(count),sum(incidentstat.read) from incidentstat")
        if result == 0 and rows[0][0]:
            allNum = int(rows[0][0])
            readNum = int(rows[0][1])
            unread_num = allNum - readNum
        else:
            unread_num = total

        return jsonify({'rows': data, 'total': total, 'page': page, 'num': unread_num})
    except:
        current_app.logger.exception("Exception Logged")
        return jsonify({'rows': {}, 'total': 0, 'page': 0, 'num': 0})


@safeevent_page.route('/safeEventReadTag', methods=['GET', 'POST'])
@login_required
def mw_safeevent_readtag():
    db_proxy = DbProxy()
    # use session variable for statement trigger, instead of row trigger,
    # to update the statistc more faster
    msg = {}
    userip = get_oper_ip_info(request)
    loginuser=request.get_json().get('loginuser')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u'设置安全事件为已读'
    msg['Result']='0'
    db_proxy.execute('set @g_has_update_statistic = 0')
    result = db_proxy.write_db("UPDATE incidents set status=1 where status=0")
    db_proxy.execute('set @g_has_update_statistic = 0')
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@safeevent_page.route('/safeEventClearTag', methods=['GET', 'POST'])
@login_required
def mw_safeevent_cleartag():
    db_proxy = DbProxy()
    # use session variable for statement trigger, instead of row trigger,
    # to update the statistc more faster
    db_proxy.execute('set @g_has_delete_statistic = 0')
    result = db_proxy.write_db("DELETE FROM incidents")
    db_proxy.execute('set @g_has_delete_statistic = 0')
    time.sleep(5)
    msg={}
    userip = get_oper_ip_info(request)
    if request.method == 'GET':
        loginuser = request.args.get('loginuser')
    elif request.method == 'POST':
        post_data = request.get_json()
        loginuser = post_data['loginuser']
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = u"清空所有安全事件"
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@safeevent_page.route('/safeOneEventRead')
@login_required
def mw_safeOneEventRead():
    db_proxy = DbProxy()
    recordindex = request.args.get('recordindex')
    table_num = request.args.get('tablenum')
    update_cmd = "UPDATE incidents_%s set status=1 where incidentId=%s"%(table_num,recordindex)
    #incident_send_read_cmd(TYPE_EVENT_SOCKET,update_cmd)
    result = db_proxy.write_db(update_cmd)
    return jsonify({'status':1})


@safeevent_page.route('/eventCountRefresh')
@login_required
def mw_event_countrefresh():
    db_proxy = DbProxy()
    safeevent_allSafeEvent = 0
    readNum = 0
    safeevent_todaySafeEvent = 0

    result, rows = db_proxy.read_db("SELECT count(*) from incidents")
    if result == 0 and rows[0][0]:
        safeevent_allSafeEvent = rows[0][0]

    result, rows = db_proxy.read_db("select sum(incidentstat.read) from incidentstat")
    if result == 0 and rows[0][0]:
        readNum = rows[0][0]

    safeevent_noReadSafeEvent = safeevent_allSafeEvent - readNum

    today = datetime.date.today()
    todayTime = str(today) + ' 00:00:00'
    tomorrowTime = str(today) + ' 23:59:59'
    tup_todayTime = time.strptime(todayTime, "%Y-%m-%d %H:%M:%S")
    tmp_todayTime = int(time.mktime(tup_todayTime))
    tup_tomorrowTime = time.strptime(tomorrowTime, "%Y-%m-%d %H:%M:%S")
    tmp_tomorrowTime = int(time.mktime(tup_tomorrowTime))
    sql_cmd = "SELECT sum(count) from incidentstat where timestamp>=" + str(tmp_todayTime) +" and timestamp<=" + str(tmp_tomorrowTime)
    result, rows = db_proxy.read_db(sql_cmd)
    if result == 0 and rows[0][0]:
        safeevent_todaySafeEvent = rows[0]

    safeevent_highestPeriod="---"

    #high_sql = "select timestamp from incidentstat where timestamp like " + "\"" + str(today) + "%\" order by count desc limit 1"
    #result,rows = db_proxy.read_db(high_sql)
    #try:
    #    #get 15 from '2017-01-13 15:00:00'
    #    if result == 0 and rows[0][0]:
    #        high_str = rows[0][0]
    #        high_str = high_str.split(' ')[1].split(':')[0]
    #        high_str2 = "00:00"
    #        if int(high_str)+1 < 24:
    #            high_str2 = str(int(high_str)+1)+':00'
    #        safeevent_highestPeriod = high_str + ':00-' + high_str2
    #except:
        #safeevent_highestPeriod = "---"

    safeeventinfo={}
    safeeventinfo['allSafeEvent'] = safeevent_allSafeEvent
    safeeventinfo['noReadSafeEvent'] = safeevent_noReadSafeEvent
    safeeventinfo['todaySafeEvent'] = safeevent_todaySafeEvent
    safeeventinfo['highestPeriod'] = safeevent_highestPeriod

    syseventinfo={}
    syseventinfo['allSafeEvent'] = 0
    syseventinfo['noReadSafeEvent'] = 0
    syseventinfo['todaySafeEvent'] = 0
    syseventinfo['highestPeriod'] = '---'
    return jsonify(safeeventinfo=safeeventinfo,syseventinfo=syseventinfo)


@safeevent_page.route('/safeEventExportData', methods=['GET', 'POST'])
@login_required
def mw_safeevent_exportdata():
    #   时间戳 源设备名 目的设备名 源IP 目的IP 源MAC 目的MAC 事件处理 协议名 规则名 协议细节 事件来源
    sql_cmd = "select sourceIp,destinationIp,action,appLayerProtocol,protocolDetail," \
              "matchedKey,timestamp,dpiIp,boxId,memo,signatureName,sourceMac,destinationMac from incidents order by timestamp desc"
    file_name = "incidents-" + time.strftime("%Y-%m-%d_%H:%M:%S",time.localtime(time.time()))+".csv"

    msg={}
    userip = get_oper_ip_info(request)
    loginuser = request.args.get('loginuser')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = u"导出所有安全事件"
    msg['ManageStyle'] = 'WEB'

    conn = MySQLdb.connect(host='localhost', port=3306, user='keystone', passwd='OptValley@4312', db='keystone',
                           cursorclass=MySQLdb.cursors.SSCursor)
    cur = conn.cursor()
    cur.execute(sql_cmd)
    dev_name_dict = get_dev_dict()
    incident_from = [U"白名单".encode("utf-8-sig"), U"黑名单".encode("utf-8-sig"), U"IP/MAC".encode("utf-8-sig"), U"流量告警".encode("utf-8-sig"), U"MAC过滤".encode("utf-8-sig"), U"资产告警".encode("utf-8-sig"), U"不合规报文告警".encode("utf-8-sig")]
    incident_action = [U"通过".encode("utf-8-sig"), U"警告".encode("utf-8-sig"), U"阻断".encode("utf-8-sig"), U"通知".encode("utf-8-sig")]

    def generate_safeevent_logfile():
        try:
            col_list = [U"时间戳".encode("utf-8-sig"), U"源设备名".encode("utf-8-sig"), U"目的设备名".encode("utf-8-sig"),
                        U"源IP".encode("utf-8-sig"), U"目的IP".encode("utf-8-sig"), U"源MAC".encode("utf-8-sig"), U"目的MAC".encode("utf-8-sig"),
                        U"事件处理".encode("utf-8-sig"), U"协议名".encode("utf-8-sig"), U"规则名".encode("utf-8-sig"), U"协议细节".encode("utf-8-sig"),
                        U"事件来源".encode("utf-8-sig")]
            yield ','.join(map(str, col_list)) + '\n'
            rows = cur.fetchall()
            for row in rows:
                row = list(row)
                if row[10] == "4":
                    row[4] = "low_line = %skbps high_line = %skbps band = %skbps" % (
                    str(row[7]), str(row[8]), str(row[9]))

                src_ip_str = trans_db_ipmac_to_local(row[0])
                src_mac_str = trans_db_ipmac_to_local(row[11])
                dst_ip_str = trans_db_ipmac_to_local(row[1])
                dst_mac_str = trans_db_ipmac_to_local(row[12])
                if (src_ip_str + src_mac_str) in dev_name_dict:
                    src_dev_name = dev_name_dict[src_ip_str + src_mac_str]
                else:
                    src_dev_name = get_default_devname_by_ipmac(src_ip_str, src_mac_str)

                if (dst_ip_str + dst_mac_str) in dev_name_dict:
                    dst_dev_name = dev_name_dict[dst_ip_str + dst_mac_str]
                else:
                    dst_dev_name = get_default_devname_by_ipmac(dst_ip_str, dst_mac_str)
                # csv列已逗号区分
                if row[4] is None:
                    row[4] = "NA"
                else:
                    row[4] = row[4].replace(",", " ")
                if row[5] is None:
                    row[5] = "NA"
                else:
                    row[5] = row[5].replace(",", " ")
                src_dev_name = src_dev_name.decode("utf8").encode("utf-8-sig")
                dst_dev_name = dst_dev_name.decode("utf8").encode("utf-8-sig")
                alarm_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row[6])))
                # [U"时间戳", U"源设备名", U"目的设备名", U"源IP", U"目的IP", U"源MAC", U"目的MAC", U"事件处理",U"协议名", U"规则名", U"协议细节", U"事件来源"]
                row_format = [alarm_time, src_dev_name, dst_dev_name, row[0], row[1], row[11], row[12],
                              incident_action[int(row[2])], get_ui_proto_name(row[3]), row[5], row[4],
                              incident_from[int(row[10]) - 1]]
                yield ','.join(map(str, row_format)) + '\n'
            msg['Result'] = 0
            send_log_db(MODULE_OPERATION, msg)
        except:
            msg['Result'] = 1
            send_log_db(MODULE_OPERATION, msg)
            current_app.logger.error('download %s except' % file_name)
            current_app.logger.error(traceback.format_exc())
        cur.close()
        conn.close()

    try:
        return Response(generate_safeevent_logfile(), 200, {'Content-Disposition': 'attachment;filename=' + file_name,
                                                            'Content-Type': 'text/csv; charset=utf-8-sig'})
    except:
        cur.close()
        conn.close()

        msg['Result'] = 1
        send_log_db(MODULE_OPERATION, msg)
        current_app.logger.error('download %s except' % file_name)
        current_app.logger.error(traceback.format_exc())


@safeevent_page.route('/safeeventPercent', methods=['GET', 'POST'])
@login_required
def mw_safeevent_percent():
    db_proxy = DbProxy()
    # sql_cmd = "select count(*) totalCount," \
    #           "count(case when signatureName='1' then 1 else null end) whitelistcount," \
    #           "count(case when signatureName='2' then 1 else null end) blacklistcount," \
    #           "count(case when signatureName='3' then 1 else null end) ipmaccount," \
    #           "count(case when signatureName='4' then 1 else null end) twarningcount," \
    #           "count(case when signatureName='5' then 1 else null end) macfiltercount," \
    #           "count(case when signatureName='6' then 1 else null end) devalert from incidents"
    sql_cmd = """select sum(icd_count)/2 totalCount,sum(icd_wl_count)/2 whitelistcount,sum(icd_bl_count)/2 blacklistcount,sum(icd_im_count)/2 ipmaccount,sum(icd_flow_count)/2 twarningcount,sum(icd_mf_count)/2 macfiltercount,sum(icd_dev_count)/2 devalert,sum(icd_pcap_count)/2 pcapalert from incidentstat_bydev;"""
    result, rows = db_proxy.read_db(sql_cmd)
    if result != 0 or len(rows) == 0:
        return jsonify({'rows': []})
    tmp_rows = rows
    rows = []
    if tmp_rows[0][0]:
        if tmp_rows[0][1]:
            tmp_per = float(tmp_rows[0][1])/float(tmp_rows[0][0])
            row_tmp = [1, tmp_per]
        else:
            row_tmp=[1, 0]
        rows.append(row_tmp)
        if tmp_rows[0][2]:
            tmp_per = float(tmp_rows[0][2])/float(tmp_rows[0][0])
            row_tmp = [2, tmp_per]
        else:
            row_tmp=[2, 0]
        rows.append(row_tmp)
        if tmp_rows[0][3]:
            tmp_per = float(tmp_rows[0][3])/float(tmp_rows[0][0])
            row_tmp = [3, tmp_per]
        else:
            row_tmp=[3, 0]
        rows.append(row_tmp)
        if tmp_rows[0][4]:
            tmp_per = float(tmp_rows[0][4])/float(tmp_rows[0][0])
            row_tmp = [4, tmp_per]
        else:
            row_tmp=[4, 0]
        rows.append(row_tmp)
        if tmp_rows[0][5]:
            tmp_per = float(tmp_rows[0][5])/float(tmp_rows[0][0])
            row_tmp = [5, tmp_per]
        else:
            row_tmp=[5, 0]
        rows.append(row_tmp)
        if tmp_rows[0][6]:
            tmp_per = float(tmp_rows[0][6])/float(tmp_rows[0][0])
            row_tmp = [6, tmp_per]
        else:
            row_tmp=[6, 0]
        rows.append(row_tmp)
        if tmp_rows[0][7]:
            tmp_per = float(tmp_rows[0][7])/float(tmp_rows[0][0])
            row_tmp = [7, tmp_per]
        else:
            row_tmp=[7, 0]
        rows.append(row_tmp)
    current_app.logger.info(rows)
    return jsonify({'rows': rows})
