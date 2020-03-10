#! /usr/bin/env python
#coding=utf-8
import os
import sys
import datetime
import base64
# import xmltodict
from xml.etree import ElementTree
import time
from flask import request
from flask import jsonify
from flask import Blueprint
from flask import current_app
#flask-login
from flask_login.utils import login_required

sys.path.append(os.path.abspath(__file__).split('app')[0])
from global_function.global_var import *

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)


protAudit_page = Blueprint('protAudit_page', __name__,template_folder='templates')


sqlserver_optype_desc = (
    '',
    'SQL命令或批处理',
    '预登录(TDS 4.2)',
    '远程存储过程调用',
    '服务器对客户端数据响应',
    '',
    '提醒消息',
    '批量数据操作',
    '',
    '',
    '',
    '',
    '',
    '',
    '事务管理请求',
    '登录请求',
    'SSL加密数据',
    '预登录(TDS 7)'
)


def get_cusproto_list(db_proxy_config):
    custom_proto_list=[]
    cmd_str="select proto_name from self_define_proto_config where proto_id > 500"
    res, rows=db_proxy_config.read_db(cmd_str)
    for row in rows:
        custom_proto_list.append(row[0])
    return custom_proto_list


def get_cusproto_id(db, proto):
    cmd_str = "select proto_id from self_define_proto_config where proto_name='{}'".format(proto)
    res, rows = db.read_db(cmd_str)
    try:
        if res == 0 and rows[0][0]:
            return int(rows[0][0])
        else:
            return 0
    except:
        return 0


#=============================== page start ===================================

#=============================== page end =====================================

@protAudit_page.route('/getFlowDataHeadSearch', methods=['GET', 'POST'])
@login_required
def getFlowDataHeadSearch():
    try:
        if request.method == 'GET':
            srcIp = request.args.get('srcIp')
            srcPort = request.args.get('srcPort')
            srcMac = request.args.get('srcMac')
            destIp = request.args.get('destIp')
            destPort = request.args.get('destPort')
            destMac = request.args.get('destMac')
            protocol = request.args.get('protocol')
            timeDelta = request.args.get('timeDelta', 0, type=int)
            srcDevName = request.args.get('sourceName','')
            dstDevName = request.args.get('destinationName','')
            page = request.args.get('page', 0, type=int)
        elif request.method == 'POST':
            post_data = request.get_json()
            srcIp = post_data['srcIp']
            srcPort = post_data['srcPort']
            srcMac= post_data['srcMac']
            destIp = post_data['destIp']
            destPort = post_data['destPort']
            destMac = post_data['destMac']
            protocol = post_data['protocol']
            timeDelta = int(post_data['timeDelta'])
            srcDevName = post_data['sourceName']
            dstDevName = post_data['destinationName']
            page = int(post_data['page'])

        db_proxy = DbProxy()
        db_proxy_config = DbProxy(CONFIG_DB_NAME)
        limit_str = 'limit 10 offset %d'%((page-1)*10)
        option_str = "where 1=1"

        custom_proto_list = get_cusproto_list(db_proxy_config)
        proto_list = list(protocol_names)
        proto_list.extend(custom_proto_list)

        if len(srcIp) > 0:
            option_str += " and sourceIp like '%%%s%%'"%(srcIp)
        if len(srcPort) > 0:
            option_str += " and sourcePort like '%%%s%%'"%(srcPort)
        if len(srcMac) > 0:
            option_str += " and sourceMac like '%%%s%%'"%(srcMac)
        if len(destIp) > 0:
            option_str += " and destinationIp like '%%%s%%'"%(destIp)
        if len(destPort) > 0:
            option_str += " and destinationPort like '%%%s%%'"%(destPort)
        if len(destMac) > 0:
            option_str += " and destinationMac like '%%%s%%'"%(destMac)
        if len(protocol) > 0:
            option_str += " and protocolSourceName like '%%%s'"%(protocol)
        if timeDelta > 0:
            nowtime = datetime.datetime.now()
            preHours = nowtime + datetime.timedelta(hours=-timeDelta)
            time_int = int(time.mktime(time.strptime(preHours.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")))
            # option_str += " and packetTimestamp >= %d"%(time_int)
            option_str += " and packetTimestampint >= %d"%(int(str(time_int)+'000000'))
        """
        if len(srcDevName)>0 and srcDevName != "0":
            try:
                tmp_str = ""
                first_flag = 1
                src_ipmac_list = get_ipmac_list_by_devname(srcDevName.encode("UTF-8"))
                current_app.logger.info("src_ipmac_list:%s" % str(src_ipmac_list))
                for elem in src_ipmac_list:
                    if first_flag== 0:
                        tmp_str += " or "
                    first_flag = 0
                    trans_mac = ""
                    if elem[1] != "" and elem[1] != "any":
                        for i in range (0,12):
                            trans_mac += elem[1][i]
                            if( i % 2 == 1 and i != 11 ):
                                trans_mac += ":"
                    #src_ip_str = ""
                    #src_mac_str = ""
                    #if elem[0] != "":
                    #src_ip_str = " sourceIp like " + "\"%"+elem[0]+"%\" and"
                    #if trans_mac != "":
                    #src_mac_str = " sourceMac like " + "\"%"+trans_mac+"%\""
                    if elem[0] == "":
                        src_ip_str = " sourceIp = 'NULL' "
                    elif elem[0] == "any":
                        src_ip_str = " sourceIp like \""+ "%%" + "\""
                    else:
                        src_ip_str = " sourceIp = \""+ elem[0] + "\""

                    if elem[1] == "":
                        src_mac_str = " sourceMac = 'NULL' "
                    elif elem[1] == "any":
                        src_mac_str = " sourceMac like \""+ "%%" + "\""
                    else:
                        src_mac_str = " sourceMac = \""+ trans_mac.replace(":", "") + "\""

                        current_app.logger.info("src_ip_str = %s, src_mac_str = %s" % (src_ip_str, src_mac_str))
                    tmp_str += "(" + src_ip_str + " and " + src_mac_str + ")"
                if tmp_str != "":
                    option_str += " and (" + tmp_str + ")"
            except:
                current_app.logger.info("getFlowDataHeadSearch input sourceName error. sourceName = %s" % srcDevName)
        if len(dstDevName)>0 and dstDevName != "0":
            try:
                tmp_str = ""
                first_flag = 1
                dst_ipmac_list = get_ipmac_list_by_devname(dstDevName.encode("UTF-8"))
                current_app.logger.info("dst_ipmac_list:%s" % str(dst_ipmac_list))
                for elem in dst_ipmac_list:
                    if first_flag== 0:
                        tmp_str += " or "
                    first_flag = 0
                    trans_mac = ""
                    if elem[1] != "" and elem[1] != "any":
                        for i in range (0,12):
                            trans_mac += elem[1][i]
                            if( i % 2 == 1 and i != 11 ):
                                trans_mac += ":"

                    #dst_ip_str = ""
                    #dst_mac_str = ""
                    #if elem[0] != "":
                    #dst_ip_str = " destinationIp = \"" + elem[0] + "\""
                    #dst_mac_str = " destinationMac = \"" + trans_mac + "\""
                    if elem[0] == "":
                        dst_ip_str = " destinationIp = 'NULL' "
                    elif elem[0] == "any":
                        dst_ip_str = " destinationIp like \""+ "%%" + "\""
                    else:
                        dst_ip_str = " destinationIp = \""+ elem[0] + "\""

                    if elem[1] == "":
                        dst_mac_str = " destinationMac = 'NULL' "
                    elif elem[1] == "any":
                        dst_mac_str = " destinationMac like \""+ "%%" + "\""
                    else:
                        dst_mac_str = " destinationMac = \""+ trans_mac.replace(":", "") + "\""
                        current_app.logger.info("dst_ip_str = %s, dst_mac_str = %s" % (dst_ip_str, dst_mac_str))
                    tmp_str += "(" + dst_ip_str + " and " + dst_mac_str + ")"
                if tmp_str != "":
                    option_str += " and (" + tmp_str + ")"
            except:
                current_app.logger.info("getFlowDataHeadSearch input dstDevName error. dstDevName = %s" % dstDevName)
        """
        if len(srcDevName) > 0 and srcDevName != "0":
            tmp_str=""
            first_flag=1
            src_ipmac_list=get_ipmac_list_by_devname(srcDevName.encode("UTF-8"))
            for elem in src_ipmac_list:
                if first_flag == 0:
                    tmp_str+=" or "
                first_flag=0
                if elem[0] == "any":
                    src_ip_str=" sourceIp like \"" + "%%" + "\""
                elif elem[0] == "":
                    src_ip_str=" sourceIp = 'NULL' "
                else:
                    src_ip_str=" sourceIp = \"" + elem[0] + "\""

                if elem[1] == "any":
                    src_mac_str=" sourceMac like \"" + "%%" + "\""
                elif elem[1] == "":
                    src_mac_str=" sourceMac = '' "
                else:
                    src_mac_str=" sourceMac = \"" + elem[1] + "\""
                tmp_str += " (" + src_ip_str + " and " + src_mac_str + ") "
            if tmp_str != "":
                option_str += " and (" + tmp_str + ")"
        if len(dstDevName) > 0 and dstDevName != "0":
            tmp_str=""
            first_flag=1
            dst_ipmac_list=get_ipmac_list_by_devname(dstDevName.encode("UTF-8"))
            for elem in dst_ipmac_list:
                if first_flag == 0:
                    tmp_str+=" or "
                first_flag=0
                if elem[0] == "any":
                    dst_ip_str=" destinationIp like \"" + "%%" + "\""
                elif elem[0] == "":
                    dst_ip_str=" destinationIp ='NULL' "
                else:
                    dst_ip_str=" destinationIp = \"" + elem[0] + "\""
                if elem[1] == "any":
                    dst_mac_str=" destinationMac like \"" + "%%" + "\""
                elif elem[1] == "":
                    dst_mac_str=" destinationMac = '' "
                else:
                    dst_mac_str=" destinationMac = \"" + elem[1] + "\""
                tmp_str += " (" + dst_ip_str + " and " + dst_mac_str + ") "
            if tmp_str != "":
                option_str += " and (" + tmp_str + ") "

        sql_str = "select * from flowdataheads %s order by packetTimestampint desc %s"%(option_str,limit_str)
        current_app.logger.info("search_str: " + sql_str)
        sum_str = "select count(*) from flowdataheads %s"%(option_str)

        # current_app.logger.info("getFlowDataHeadSearch sql_str:%s" % sql_str)

        flowDataHeads = [[]]
        total = 0
        flow_rows = []
        try:
            #flowDataHeads = audit_send_read_cmd(TYPE_AUDIT_APP_SOCKET,sql_str)
            result,flowDataHeads = db_proxy.read_db(sql_str)
            for elem in flowDataHeads:
                src_ip_str = trans_db_ipmac_to_local(elem[6])
                src_mac_str = trans_db_ipmac_to_local(elem[3])
                dst_ip_str = trans_db_ipmac_to_local(elem[8])
                dst_mac_str = trans_db_ipmac_to_local(elem[4])
                src_dev_name = get_devname_by_ipmac(src_ip_str, src_mac_str)
                dst_dev_name = get_devname_by_ipmac(dst_ip_str, dst_mac_str)
                target_elem = list(elem)
                if "," in target_elem[-3]:
                    id_name = target_elem[-3].split(",")
                    cus_id, cusname = id_name
                    cmd_str = "select proto_name from self_define_proto_config where proto_id = {}".format(cus_id)
                    res, rows = db_proxy_config.read_db(cmd_str)
                    try:
                        if rows[0][0]:
                            target_elem[-3] = rows[0][0]
                        else:
                            target_elem[-3]='NA'
                    except:
                        target_elem[-3] = 'NA'
                target_elem[2] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(target_elem[2])))
                target_elem[1] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(str(target_elem[-1])[:-6])))
                target_elem.extend([src_dev_name, dst_dev_name])
                if target_elem[-5] != 'NA' or (not protocol):
                    flow_rows.append(target_elem)

            #rows =  audit_send_read_cmd(TYPE_AUDIT_APP_SOCKET,sum_str)
            result,rows = db_proxy.read_db(sum_str)
            total = rows[0][0]
        except:
            current_app.logger.error(traceback.format_exc())

        # return jsonify({'rows': flow_rows,'total':total,'page':page})
        return jsonify({'rows': flow_rows, 'proto_list': custom_proto_list, 'total': total, 'page': page})
    except:
        current_app.logger.exception("Exception Logged")
        return jsonify({'rows':{},'total':0,'page':0})


@protAudit_page.route('/getDetail')
@login_required
def getDetail():
    db_proxy = DbProxy()
    db_proxy_config = DbProxy(CONFIG_DB_NAME)
    page = request.args.get('page', 0, type=int)
    flowdataHeadId = request.args.get('flowdataHeadId', 0, type=int)
    protocol = request.args.get('protocol')
    limit_str = 'order by packetTimestampint desc limit 10 offset %d'%((page-1)*10)
    flowDetail = []
    total = 0
    proto_id = get_cusproto_id(db_proxy_config, protocol)
    if proto_id > 500:
        cmd_str = "select protocolDetail,packetTimestamp from cusprotoflowdatas where proto_id = {} and flowdataHeadId={} {}".format(proto_id, flowdataHeadId, limit_str)
        result, rows = db_proxy.read_db(cmd_str)
        for detail in rows:
            item = {}
            item["date"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(detail[1])))
            item["detail"] =detail[0]
            flowDetail.append(item)
        count_str = "select count(*) from cusprotoflowdatas where proto_id = {} and flowdataHeadId={}".format(proto_id, flowdataHeadId)
        current_app.logger.info(count_str)
        res, rows = db_proxy.read_db(count_str)
        try:
            total = rows[0][0]
        except:
            total = 0

    elif protocol in protocol_names:
        try:
            #flowDetail = audit_send_read_cmd(TYPE_AUDIT_APP_SOCKET,"select * from %sflowdatas where flowdataHeadId=%d %s"%(protocol,flowdataHeadId,limit_str))
            result,flowDetail = db_proxy.read_db("select * from %sflowdatas where flowdataHeadId=%d %s"%(protocol,flowdataHeadId,limit_str))

            #protocol_list = ['s7', 'sip', 'sqlserver']
            if protocol == "http":
                url_detail = []
                for detail in flowDetail:
                    detail = list(detail)
                    detail[2] = base64.b64decode(detail[2])
                    url_detail.append(detail)
                flowDetail = url_detail
                flowDetail = get_protocol_segment_meaning(protocol, flowDetail)
            elif protocol == 'telnet':
                url_detail = []
                for detail in flowDetail:
                    detail = list(detail)
                    detail[2] = detail[2].decode("latin-1")
                    detail[3] = detail[3].decode('latin-1')
                    url_detail.append(detail)
                flowDetail = url_detail
                flowDetail = get_protocol_segment_meaning(protocol, flowDetail)
            elif protocol in protocol_names:
                flowDetail = get_protocol_segment_meaning(protocol, flowDetail)
            for detail in flowDetail:
                if protocol == 'mms':
                    detail[-7] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(detail[-7])))
                else:
                    detail[-6] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(detail[-6])))
            rows = send_read_cmd(TYPE_APP_SOCKET,"select count(*) from %sflowdatas where flowdataHeadId=%d"%(protocol,flowdataHeadId))
            total = rows[0][0]
        except:
            current_app.logger.error(traceback.format_exc())

    else:
        flowDetail = []
        total = 0
        page = 1
    return jsonify({'rows': flowDetail,'total': total,'page': page})


def deal_protocol_segment_mms(seg_list, flowDetail):
    detail_tmp = []
    for row in flowDetail:
        show_msg = ""
        if row[2] is not None and len(row[2]) > 0:
            show_msg += "%s:%s" % (seg_list[0].decode("utf8"), str(row[2]))
        if row[8] is not None and len(row[8]) > 0:
            show_msg += ", %s:%s" % (seg_list[1].decode("utf8"), str(row[8]))
        row = list(row)
        row[2] = show_msg
        detail_tmp.append(row)
    return detail_tmp


def get_protocol_segment_meaning(protocol, flowDetail):
    '''后期统一在C端进行优化: 将所有字段拼接完成后，传输给python;数据库只保留一个字段:详情'''
    detail_tmp = []
    if AUDIT_SEG_DICT.has_key(protocol):
        seg_list = AUDIT_SEG_DICT[protocol]
        if protocol == "sqlserver":
            detail_tmp = deal_protocol_segment_sqlserver(seg_list, flowDetail)
        elif protocol == "mms":
                detail_tmp = deal_protocol_segment_mms(seg_list, flowDetail)
        elif protocol == "goose":
            seg_list = [u'数据集', u'GO标识符', u'allData']
            # seg_list.append('allData')
            detail_tmp = deal_protocol_segment(seg_list, flowDetail)
        else:
            detail_tmp = deal_protocol_segment(seg_list, flowDetail)
    return detail_tmp


def deal_protocol_segment(seg_list, flowDetail):
    detail_tmp = []
    for row in flowDetail:
        show_msg = ""
        for i, val in enumerate(seg_list):
            if row[i+2] is not None and len(str(row[i+2])) > 0:
                goose_str = str(row[i+2])
                # current_app.logger.info("goose_str" + goose_str)
                if 'allData' in goose_str:
                    try:
                        # current_app.logger.info(goose_str)
                        root = ElementTree.fromstring(goose_str).getiterator()
                        data_list = []
                        for item in root:
                            data_dict = {}
                            if item.tag != "allData":
                                data_dict[item.tag] = str(item.text).strip()
                                data_list.append(data_dict)
                        for data in data_list:
                            if "boolean" in data:
                                data["boolean"] = [dict_key for dict_key in data_list[(data_list.index(data) + 1)].keys()][0]
                        for data in data_list:
                            if "false" in data:
                                data_list.remove(data)
                            if "true" in data:
                                data_list.remove(data)
                        # doc = xmltodict.parse(goose_str)
                        # doc = doc.get('allData')
                        # goose_str_1 = json.dumps(doc)
                        goose_str = str(data_list)
                        # current_app.logger.info(goose_str)
                    except:
                        goose_str = "{}"
                show_msg += "%s:%s, " % (val.decode("utf8"), goose_str)
        row = list(row)
        row[2] = show_msg[0:-2].replace("allData", "<br>allData")
        detail_tmp.append(row)
    return detail_tmp


def deal_protocol_segment_sqlserver(seg_list, flowDetail):
    sqlserver_detail = []
    sqlstr = ""
    for detail in flowDetail:
        detail = list(detail)
        if detail[2] == 1:
            sqlstr = "操作类型:".decode("utf8") + sqlserver_optype_desc[1].decode("utf8") + ", SQL语句:".decode("utf8") + detail[4].encode("utf8")
            detail.insert(0, detail[9])
            detail.insert(1, sqlstr)
            sqlserver_detail.append(detail)
        elif detail[2] == 4:
            if detail[3] == 1:
                sqlstr = "操作类型:".decode("utf8") + sqlserver_optype_desc[4].decode("utf8") + ", 执行结果:失败".decode("utf8")
            elif detail[5] >= 0:
                sqlstr = "操作类型:".decode("utf8") + sqlserver_optype_desc[4].decode("utf8") + ", 执行结果:成功, 查询行数:%d".decode("utf8")%detail[5]
            else:
                continue
            detail.insert(0, detail[9])
            detail.insert(1, sqlstr)
            sqlserver_detail.append(detail)
        else:
            continue
            
    return sqlserver_detail


@protAudit_page.route('/getBhvDataHeadSearch', methods=['GET', 'POST'])
@login_required
def getBhvDataHeadSearch():
    try:
        if request.method == 'GET':
            srcIp=request.args.get('srcIp')
            srcPort=request.args.get('srcPort')
            srcMac=request.args.get('srcMac')
            destIp=request.args.get('destIp')
            destPort=request.args.get('destPort')
            destMac=request.args.get('destMac')
            protocol=request.args.get('protocol')
            # timeDelta=request.args.get('timeDelta', 0, type=int)
            srcDevName=request.args.get('sourceName', '')
            dstDevName=request.args.get('destinationName', '')
            page=request.args.get('page', 0, type=int)
            start_time=request.args.get('starttime')
            end_time=request.args.get('endtime')
        elif request.method == 'POST':
            post_data=request.get_json()
            srcIp=post_data['srcIp']
            srcPort=post_data['srcPort']
            srcMac=post_data['srcMac']
            destIp=post_data['destIp']
            destPort=post_data['destPort']
            destMac=post_data['destMac']
            protocol=post_data['protocol']
            # timeDelta=int(post_data['timeDelta'])
            srcDevName=post_data['sourceName']
            dstDevName=post_data['destinationName']
            page=int(post_data['page'])
            start_time=post_data['starttime']
            end_time=post_data['endtime']

        db_proxy=DbProxy()
        limit_str='limit 10 offset %d' % ((page - 1) * 10)
        option_str="where 1=1"

        if len(start_time) > 0:
            start_timestamp=int(time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S')))
            option_str+=" and packetTimestamp >= %d" % (start_timestamp)
        if len(end_time) > 0:
            end_timestamp=int(time.mktime(time.strptime(end_time, '%Y-%m-%d %H:%M:%S')))
            option_str+=" and packetTimestamp < %d" % (end_timestamp)
        if len(srcIp) > 0:
            option_str+=" and sourceIp like '%%%s%%'" % (srcIp)
        if len(srcPort) > 0:
            option_str+=" and sourcePort like '%%%s%%'" % (srcPort)
        if len(srcMac) > 0:
            option_str+=" and sourceMac like '%%%s%%'" % (srcMac)
        if len(destIp) > 0:
            option_str+=" and destinationIp like '%%%s%%'" % (destIp)
        if len(destPort) > 0:
            option_str+=" and destinationPort like '%%%s%%'" % (destPort)
        if len(destMac) > 0:
            option_str+=" and destinationMac like '%%%s%%'" % (destMac)
        if len(protocol) > 0:
            option_str+=" and protocolSourceName like '%%%s'" % (protocol)
        if len(srcDevName) > 0 and srcDevName != "0":
            tmp_str=""
            first_flag=1
            src_ipmac_list=get_ipmac_list_by_devname(srcDevName.encode("UTF-8"))
            for elem in src_ipmac_list:
                if first_flag == 0:
                    tmp_str+=" or "
                first_flag=0
                if elem[0] == "any":
                    src_ip_str=" sourceIp like \"" + "%%" + "\""
                elif elem[0] == "":
                    src_ip_str=" sourceIp = '' "
                else:
                    src_ip_str=" sourceIp = \"" + elem[0] + "\""

                if elem[1] == "any":
                    src_mac_str=" sourceMac like \"" + "%%" + "\""
                elif elem[1] == "":
                    src_mac_str=" sourceMac = '' "
                else:
                    src_mac_str=" sourceMac = \"" + elem[1] + "\""
                tmp_str += " (" + src_ip_str + " and " + src_mac_str + ") "
            if tmp_str != "":
                option_str += " and (" + tmp_str + ")"
        if len(dstDevName) > 0 and dstDevName != "0":
            tmp_str=""
            first_flag=1
            dst_ipmac_list=get_ipmac_list_by_devname(dstDevName.encode("UTF-8"))
            for elem in dst_ipmac_list:
                if first_flag == 0:
                    tmp_str+=" or "
                first_flag=0
                if elem[0] == "any":
                    dst_ip_str=" destinationIp like \"" + "%%" + "\""
                elif elem[0] == "":
                    dst_ip_str=" destinationIp = '' "
                else:
                    dst_ip_str=" destinationIp = \"" + elem[0] + "\""
                if elem[1] == "any":
                    dst_mac_str=" destinationMac like \"" + "%%" + "\""
                elif elem[1] == "":
                    dst_mac_str=" destinationMac = '' "
                else:
                    dst_mac_str=" destinationMac = \"" + elem[1] + "\""
                tmp_str += " (" + dst_ip_str + " and " + dst_mac_str + ") "
            if tmp_str != "":
                option_str += " and (" + tmp_str + ") "
        sql_str="select * from bhvflowdataheads %s order by packetTimestampint desc %s" % (option_str, limit_str)
        sum_str="select count(*) from bhvflowdataheads %s" % (option_str)

        # current_app.logger.info("getFlowDataHeadSearch sql_str:%s" % sql_str)

        flowDataHeads=[[]]
        total=0
        flow_rows=[]
        try:
            # flowDataHeads = audit_send_read_cmd(TYPE_AUDIT_APP_SOCKET,sql_str)
            result, flowDataHeads=db_proxy.read_db(sql_str)
            for elem in flowDataHeads:
                src_ip_str=trans_db_ipmac_to_local(elem[6])
                src_mac_str=trans_db_ipmac_to_local(elem[3])
                dst_ip_str=trans_db_ipmac_to_local(elem[8])
                dst_mac_str=trans_db_ipmac_to_local(elem[4])
                src_dev_name=get_devname_by_ipmac(src_ip_str, src_mac_str)
                dst_dev_name=get_devname_by_ipmac(dst_ip_str, dst_mac_str)
                target_elem=list(elem)
                target_elem[2]=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(target_elem[2])))
                target_elem[1]=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(str(target_elem[-1])[:-6])))
                target_elem.extend([src_dev_name, dst_dev_name])
                flow_rows.append(target_elem)

            # rows =  audit_send_read_cmd(TYPE_AUDIT_APP_SOCKET,sum_str)
            result, rows=db_proxy.read_db(sum_str)
            total=rows[0][0]
        except:
            current_app.logger.error(traceback.format_exc())

        return jsonify({'rows': flow_rows, 'total': total, 'page': page})
    except:
        current_app.logger.exception("Exception Logged")
        return jsonify({'rows': {}, 'total': 0, 'page': 0})


S7AUDIT_MAP_DICT = {1: u"PLC操作信息", 2: u"PLC运行信息", 3: u"OB组织块操作", 4: u"FC功能块操作", 5: u"FB功能块操作", 6: u"DB数据块操作", 7: u"内部变量操作", 8: u"输入变量操作", 9: u"输出变量操作", 10: u"其他"}


@protAudit_page.route('/getBhvDetail')
@login_required
def getBhvDetail():
    db_proxy=DbProxy()
    page=request.args.get('page', 1, type=int)
    flowdataHeadId=request.args.get('flowdataHeadId', '', type=int)
    protocol=request.args.get('protocol', '')
    type = request.args.get('type', '')
    start_time = request.args.get('starttime', '')
    end_time = request.args.get('endtime', '')
    limit_str = ' where 1=1'
    if len(str(flowdataHeadId)) > 0:
        limit_str += ' and flowdataHeadId=%d' % int(flowdataHeadId)
    if len(str(type)) > 0:
        limit_str += ' and type=%d' % int(type)
    if len(start_time) > 0:
        start_timestamp=int(time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S')))
        limit_str += " and packetTimestampint >= %d" % (start_timestamp*1000000)
    if len(end_time) > 0:
        end_timestamp = int(time.mktime(time.strptime(end_time, '%Y-%m-%d %H:%M:%S')))
        limit_str += " and packetTimestampint < %d" % (end_timestamp*1000000)
    limit_str += ' order by packetTimestampint desc limit 10 offset %d' % ((page - 1) * 10)

    flowDetail=[[]]
    total = 0
    try:
        sql_str = "select * from s7bhvAduitdatas" + limit_str
        current_app.logger.info(sql_str)
        result, rows = db_proxy.read_db(sql_str)
        rows = list(rows)
        flowDetail = list()
        for detail in rows:
            detail = list(detail)
            detail[2] = S7AUDIT_MAP_DICT[int(detail[2])]
            detail[-6] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(detail[-6])))
            # current_app.logger.info(detail)
            flowDetail.append(detail)
        sql_str = "select count(*) from s7bhvAduitdatas " + limit_str
        current_app.logger.info(sql_str)
        res, rows = db_proxy.read_db(sql_str)
        current_app.logger.info(rows)
        total = rows[0][0]
    except:
        current_app.logger.error(traceback.format_exc())
    return jsonify({'rows': flowDetail, 'total': total, 'page': page})
