#!/usr/bin/python
# -*- coding: UTF-8 -*-
import collections
import json
import math
import csv
import codecs
import os
import sys
import traceback
import ipaddress

from flask import request
from flask import jsonify
from flask import Blueprint
from flask import current_app

from global_function.dev_auto_identify import devAutoIdentify
from global_function.log_oper import *
from global_function.cmdline_oper import *
# flask-login
from flask_login.utils import login_required

from global_function.top_oper import TopOper
from protocolAudit import get_cusproto_list
from flask import send_from_directory
from global_function.global_var import get_oper_ip_info
from werkzeug import secure_filename

topdev_page = Blueprint('topdev_page', __name__, template_folder='templates', url_prefix='/topo')
TOP_DEV_LIMIT = 50
ALLOWED_EXTENSIONS = set(['csv'])
VENDOR_ALLOWED_EXTENSIONS = set(['json'])
UPLOAD_FOLDER = '/data/rules/'
VENDOR_UPLOAD_FOLDER = '/data/vendorinfo/'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def vendor_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in VENDOR_ALLOWED_EXTENSIONS


def judge_exist(ip,mac,db_proxy):
    cmd_str = "select count(*) from ipmaclist where ip='{}' and mac='{}'".format(ip,mac)
    res, rows = db_proxy.read_db(cmd_str)
    if not ip:
        return 1
    elif res == 0 and rows[0][0] > 0:
        return 1
    else:
        return 0


def get_dev_map(db):
    cmd_str = "select type_id,device_name from dev_type"
    _, rows = db.read_db(cmd_str)
    dev_map_dict = {}
    if len(rows) > 0:
        dev_map_dict = dict(rows)
    dev_map_dict.update({0:"未知"})
    return dev_map_dict


def verify():
    with io.open('/data/vendorinfo/tmp_vendor.json', 'r', encoding='unicode_escape') as f:
        try:
            vendor_info = json.load(f)
            return True
        except:
            return False


def check_mac(mac):
    if mac is None:
        return False
    tmp_list = mac.split(',')
    for m in tmp_list:
        try:
            tmp_list = m.split(':')
            if len(tmp_list) < 3:
                return False
            for t in tmp_list:
                if t != "":
                    if len(t) != 2:
                        return False
                    tmp_num = int(t, 16)
                    if tmp_num < 0 or tmp_num > 255:
                        return False
        except:
            return False
    return True


@topdev_page.route('/get_topdev_list', methods=['POST'])
@login_required
def mw_topdev_list():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    post_data = request.get_json()
    page = post_data.get('page', 0)
    ip = post_data.get('ip', '').encode('utf-8')
    mac = post_data.get('mac', '').encode('utf-8')
    name = post_data.get('name', '').encode('utf-8')
    dev_type = post_data.get('type', None)
    is_topo = post_data.get('is_topo', None)
    is_unknown = post_data.get('unknown', None)
    vender = post_data.get('vender', '').encode('utf-8')
    sql_str = 'select id,name,ip,mac,proto,dev_desc,is_topo,category_info,dev_type,is_unknown,dev_mode,auto_flag from topdevice where 1=1 '
    num_str = 'select count(*) from topdevice where 1=1 '
    if ip:
        sql_str += " and ip like '%%%s%%'" % ip
        num_str += " and ip like '%%%s%%'" % ip
    if mac:
        sql_str += " and mac like '%%%s%%'" % mac
        num_str += " and mac like '%%%s%%'" % mac
    if name:
        sql_str += " and name like '%%%s%%'" % name
        num_str += " and name like '%%%s%%'" % name
    if dev_type or dev_type == 0:
        sql_str += " and dev_type=%s" % dev_type
        num_str += " and dev_type=%s" % dev_type
    if is_topo or is_topo == 0:
        sql_str += " and is_topo=%s" % is_topo
        num_str += " and is_topo=%s" % is_topo
    if is_unknown or is_unknown == 0:
        sql_str += " and is_unknown=%s" % is_unknown
        num_str += " and is_unknown=%s" % is_unknown
    if vender:
        sql_str += " and category_info like '%%%s%%'" % vender
        num_str += " and category_info like '%%%s%%'" % vender
    if page:
        limit_str = ' order by id desc limit ' + str((page - 1) * 10) + ',10;'
        sql_str += limit_str
    dev_map_dict = get_dev_map(db_proxy)
    current_app.logger.info(dev_map_dict)
    res, rows = db_proxy.read_db(sql_str)
    res, count = db_proxy.read_db(num_str)
    row_list = []
    for row in rows:
        row = list(row)
        res = judge_exist(row[2], row[3], db_proxy)
        row.append(res)
        row[3] = row[3].upper()
        try:
            row.append(dev_map_dict[int(row[8])])
        except KeyError:
            row.append("未知")
        row_list.append(row)
    total = count[0][0]
    return jsonify({'rows': row_list, 'num': total, 'page': page})


@topdev_page.route('/add_to_ipmac', methods=['POST'])
@login_required
def add_to_ipmac():
    # send operation log
    msg={}
    userip = get_oper_ip_info(request)
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    db_proxy = DbProxy(CONFIG_DB_NAME)
    post_data = request.get_json()
    ip = post_data.get('ip', '').encode('utf-8')
    mac = post_data.get('mac', '').encode('utf-8')
    loginuser = post_data.get('loginuser', '').encode('utf-8')
    msg['UserName'] = loginuser
    msg['Operate'] = u"添加IPMAC规则:(IP: " + ip + ",MAC: " + mac + ")"
    sql_str = "insert into ipmaclist (enabled,ip,mac,is_study,interface) values (0,'{}','{}',0,{})".format(ip, mac, 2)
    result = db_proxy.write_db(sql_str)
    if result != 0:
        msg['Result']='1'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({"status": 0, "msg": u"应用失败"})
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({"status": 1, "msg": u"应用成功"})


@topdev_page.route('/get_topdev_detail')
@login_required
def mw_topdev_detail():
    db_proxy = DbProxy()
    config_db_proxy = DbProxy(CONFIG_DB_NAME)
    ip = request.args.get('ip')
    mac = request.args.get('mac')
    num = request.args.get('num', 10, type=int)
    inc_src_str = "select distinct destinationIp,destinationMac from incidents where sourceIp='%s' and sourceMac='%s'" % (ip, mac)
    inc_dst_str = "select distinct sourceIp,sourceMac from incidents where destinationIp='%s' and destinationMac='%s'" % (ip, mac)
    res_list = []
    _, src_rows = db_proxy.read_db(inc_src_str)
    _, dst_rows = db_proxy.read_db(inc_dst_str)
    for r in src_rows:
        tmp_r = "%s;%s" % (r[0], r[1])
        if tmp_r not in res_list:
            res_list.append(tmp_r)
    for r in dst_rows:
        tmp_r = "%s;%s" % (r[0], r[1])
        if tmp_r not in res_list:
            res_list.append(tmp_r)
    if not ip:
        tmp_ip = 'NULL'
    else:
        tmp_ip = ip
    audit_src_str = "select distinct destinationIp,destinationMac from flowdataheads " \
                    "where sourceIp='%s' and sourceMac='%s'" % (tmp_ip, mac)
    audit_dst_str = "select distinct sourceIp,sourceMac from flowdataheads " \
                    "where destinationIp='%s' and destinationMac='%s'" % (tmp_ip, mac)
    _, src_rows = db_proxy.read_db(audit_src_str)
    _, dst_rows = db_proxy.read_db(audit_dst_str)
    for r in src_rows:
        tmp_r = "%s;%s" % (r[0], r[1])
        if tmp_r not in res_list:
            res_list.append(tmp_r)
    for r in dst_rows:
        tmp_r = "%s;%s" % (r[0], r[1])
        if tmp_r not in res_list:
            res_list.append(tmp_r)
    sql_str = "select ip,mac,name,is_live,dev_type,category_info,dev_desc,is_unknown,dev_mode from topdevice " \
              "where (ip,mac) in (('',''),"
    for res in res_list:
        tmp_l = res.split(';')
        tmp_ip = tmp_l[0]
        tmp_mac = tmp_l[1]
        if tmp_ip == 'NULL':
            tmp_ip = ""
        tmp_str = "('%s','%s')," % (tmp_ip, tmp_mac)
        sql_str += tmp_str
    sql_str = sql_str[:-1]
    sql_str += ') limit %d' % num
    _, res_rows = config_db_proxy.read_db(sql_str)
    dev_list = []
    mapdict = get_dev_map(config_db_proxy)
    current_app.logger.info(mapdict)
    for r in res_rows:
        tmp_dict = {}
        tmp_dict['dev_name'] = r[2]
        tmp_dict['ip_addr'] = r[0]
        tmp_dict['mac_addr'] = r[1]
        tmp_dict['online'] = r[3]
        tmp_dict['dev_type'] = r[4]
        tmp_dict['vender_info'] = r[5]
        tmp_dict['desc'] = r[6]
        tmp_dict['unknown'] = r[7]
        tmp_dict['mode'] = r[8]
        try:
            tmp_dict['type_name'] = mapdict[int(tmp_dict['dev_type'])]
        except KeyError:
            tmp_dict['type_name'] = "未知"
        dev_list.append(tmp_dict)
    if not ip:
        tmp_ip = 'NULL'
    else:
        tmp_ip = ip
    id_str = "select icDeviceId from icdevicetrafficstats where iCDeviceIp='%s' and iCDeviceMac='%s'" % (tmp_ip, mac)
    _, id_rows = db_proxy.read_db(id_str)
    tmp_id = 0
    if id_rows:
        tmp_id = id_rows[0][0]
    return jsonify({'rows': dev_list, 'dev_id': tmp_id})


@topdev_page.route('/get_topdev_rule_detail')
@login_required
def mw_topdev_rule_detail():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    ip = request.args.get('ip')
    mac = request.args.get('mac')
    page = request.args.get('page', 1, type=int)
    add_str = ' limit ' + str((page-1)*10)+',10;'
    sql_str = "select ruleName,fields,action,proto from rules where srcIp='%s' and srcMac='%s'" % (ip, mac)
    sql_str += add_str
    _, rows = db_proxy.read_db(sql_str)
    num_str = "select count(*) from rules where srcIp='%s' and srcMac='%s'" % (ip, mac)
    _, nums = db_proxy.read_db(num_str)
    total = nums[0][0]
    return jsonify({'rows': rows, 'total': total, 'page': page})


@topdev_page.route('/get_topdev_inc_detail')
@login_required
def mw_topdev_inc_detail():
    db_proxy = DbProxy()
    res = []
    ip = request.args.get('ip')
    mac = request.args.get('mac')
    page = request.args.get('page', 1, type=int)
    tmp_mac = mac
    mac = mac.replace(":", "")
    add_str = ' order by timestamp desc limit ' + str((page - 1) * 10) + ',10;'
    sql_str = "SELECT  sourceIp,destinationIp,appLayerProtocol,timestamp,action,status,incidentId," \
                      "signatureName,sourceMac, destinationMac,signatureId, dpi, dpiName FROM incidents  " \
                      "where (sourceIp='%s' and sourceMac='%s') " \
              "or (destinationIp='%s' and destinationMac='%s')" % (ip, mac, ip, mac)
    sql_str += add_str
    _, rows = db_proxy.read_db(sql_str)
    for r in rows:
        tmp_r = list(r)
        tmp_src_name = get_devname_by_ipmac(tmp_r[0], tmp_r[8])
        tmp_dst_name = get_devname_by_ipmac(tmp_r[1], tmp_r[9])
        tmp_r.append(tmp_src_name)
        tmp_r.append(tmp_dst_name)

        # 返回资产所在交换机信息（交换机名称#端口#位置）
        config_db_proxy = DbProxy(CONFIG_DB_NAME)
        sql_str = "select a.locate, b.switch_name, b.port from switch_info as a  inner join switch_mac_port as b where a.name = b.switch_name and b.mac like '%{}%'".format(tmp_mac)
        _, rows = config_db_proxy.read_db(sql_str)
        current_app.logger.info(sql_str)
        switch_info = []
        if len(rows) > 0:
            for row in rows:
                tmp_switch_info = row[1] + "#" + str(row[2]) + "#" + row[0]
                switch_info.append(tmp_switch_info)
            tmp_r.append(switch_info)
        res.append(tmp_r)
    num_str = "select count(*) from incidents where (sourceIp='%s' and sourceMac='%s') " \
              "or (destinationIp='%s' and destinationMac='%s')" % (ip, mac, ip, mac)
    _, nums = db_proxy.read_db(num_str)
    total = nums[0][0]
    return jsonify({'rows': res, 'total': total, 'page': page})


@topdev_page.route('/get_topdev_audit_detail')
@login_required
def mw_topdev_audit_detail():
    db_proxy = DbProxy()
    config_db_proxy = DbProxy(CONFIG_DB_NAME)
    ip = request.args.get('ip')
    mac = request.args.get('mac')
    res = {}
    count_dict = OrderedDict()
    if not ip:
        tmp_ip = 'NULL'
    else:
        tmp_ip = ip
    sql_str = "select distinct protocolSourceName,destinationIp,destinationMac,count(*) as val from flowdataheads " \
              "where sourceIp='%s' and sourceMac='%s' group by protocolSourceName,destinationIp," \
              "destinationMac union all(select distinct protocolSourceName,sourceIp,sourceMac,count(*) as val from " \
              "flowdataheads  where destinationIp='%s' and destinationMac='%s' " \
              "group by protocolSourceName,sourceIp,sourceMac)" % (tmp_ip, mac, tmp_ip, mac)
    _, rows = db_proxy.read_db(sql_str)
    data_default = {}
    try:
        protocol_list = list(protocol_names)
        cusproto_list = get_cusproto_list(config_db_proxy)
        protocol_list.extend(cusproto_list)
        for p in protocol_list:
            data_default[p] = 0
        for r in rows:
            r = list(r)
            if "," in r[0]:
                id_name=r[0].split(",")
                cus_id, cusname=id_name
                cmd_str="select proto_name from self_define_proto_config where proto_id = {}".format(cus_id)
                _, rows=config_db_proxy.read_db(cmd_str)
                try:
                    if rows[0][0]:
                        r[0] = rows[0][0]
                    else:
                        r[0] = 'NA'
                except:
                    r[0] = 'NA'
            tmp_proto = r[0]
            tmp_ip = r[1]
            tmp_mac = r[2]
            tmp_val = r[3]
            if tmp_ip == 'NULL':
                tmp_ip = ''
            tmp_name = get_devname_by_ipmac(tmp_ip, tmp_mac)
            if count_dict.has_key(tmp_name):
                count_dict[tmp_name] += tmp_val
            else:
                count_dict[tmp_name] = tmp_val
            if res.has_key(tmp_name):
                tmp_data = res[tmp_name]
                tmp_data[tmp_proto] += tmp_val
            else:
                res[tmp_name] = data_default.copy()
                tmp_data = res[tmp_name]
                tmp_data[tmp_proto] += tmp_val
        # data merge
        res_data = []
        count_dict = OrderedDict(sorted(count_dict.items(), key=lambda t: t[1], reverse=False))
        for p in protocol_list:
            tmp_dict = {}
            tmp_dict['prot'] = p
            tmp_dict['data'] = {}
            tmp_dict['data']['devs'] = count_dict.keys()
            tmp_dict['data']['val'] = []
            for name in tmp_dict['data']['devs']:
                tmp_dict['data']['val'].append(res[name][p])
            if sum(tmp_dict['data']['val']) > 0:
                res_data.append(tmp_dict)
        return jsonify({'status': 1, 'rows': res_data})
    except:
        current_app.logger.error(traceback.format_exc())
        return jsonify({'status': 0, 'rows': []})


@topdev_page.route('/get_topdev_audit_proto')
@login_required
def mw_topdev_audit_proto():
    db_proxy = DbProxy()
    db_proxy_config = DbProxy(CONFIG_DB_NAME)
    ip = request.args.get('ip')
    mac = request.args.get('mac')
    if not ip:
        tmp_ip = 'NULL'
    else:
        tmp_ip = ip
    sql_str = "select protocolSourceName,count(*) from flowdataheads where sourceIp='%s' and sourceMac='%s' " \
              "or destinationIp='%s' and destinationMac='%s' group by protocolSourceName" % (tmp_ip, mac, tmp_ip, mac)
    _, rows = db_proxy.read_db(sql_str)
    res_data = {}
    res_data['prots'] = []
    res_data['vals'] = []
    for r in rows:
        r = list(r)
        if "," in r[0]:
            id_name = r[0].split(",")
            cus_id, cusname = id_name
            cmd_str = "select proto_name from self_define_proto_config where proto_id = {}".format(cus_id)
            res, rows = db_proxy_config.read_db(cmd_str)
            try:
                if rows[0][0]:
                    r[0]=rows[0][0]
                else:
                    r[0]='通用网络协议'
            except:
                r[0]='通用网络协议'
        if r[0] in res_data['prots']:
            res_data['vals'][res_data['prots'].index(r[0])] += r[1]
        else:
            res_data['prots'].append(r[0])
            res_data['vals'].append(r[1])
    return jsonify({'status': 1, 'rows': res_data})


# 新增资产
@topdev_page.route('/topdev_info', methods=['POST', 'PUT', 'DELETE'])
@login_required
def mw_topdev_info():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sta_str = "select status from whiteliststudy where id=1"
    result, rows = db_proxy.read_db(sta_str)
    tmp_status = rows[0][0]
    if tmp_status == 1:
        return jsonify({'status': 0, 'msg': '学习时不能操作资产'})
    if request.method == 'POST':
        post_data = request.get_json()
        ip = post_data.get('ip', '').encode('utf-8')
        mac = post_data.get('mac', '').encode('utf-8')
        name = post_data.get('name', '').encode('utf-8')
        dev_type = post_data.get('type', 0)
        desc = post_data.get('desc', '').encode('utf-8')
        mode = post_data.get('mode', '').encode('utf-8')
        vendor = post_data.get('vendor', '').encode('utf-8')
        auto_flag = post_data.get('auto_flag', 1)
        loginuser = post_data.get('loginuser', '')
        mac = mac.lower()
        if len(name) > 64:
            return jsonify({'status': 0, 'msg': 'name长度不合法'})
        count_str = "select count(*) from topdevice"
        _, rows = db_proxy.read_db(count_str)
        tmp_num = rows[0][0]
        if tmp_num >= db_record_limit["device"]:
            return jsonify({'status': 0, 'msg': '设备数量超出上限'})
        name_str = "select count(*) from topdevice where name='%s'" % name
        _, rows = db_proxy.read_db(name_str)
        tmp_num = rows[0][0]
        if tmp_num > 0:
            return jsonify({'status': 0, 'msg': '设备名已存在，添加失败'})
        if ip and check_ip_valid(ip) is False:
            return jsonify({'status': 0, 'msg': 'ip格式不合法'})
        if check_mac_valid(mac) is False:
            return jsonify({'status': 0, 'msg': 'mac格式不合法'})
        if len(desc) > 64:
            return jsonify({'status': 0, 'msg': '描述长度不合法'})
        if len(mode) > 64:
            return jsonify({'status': 0, 'msg': '模式长度不合法'})

        if ":" in ip:
            ip_net6 = ipaddress.ip_network(unicode(ip))
            ip = str(ip_net6.exploded.split('/')[0])

        if ip:
            tmp_str = "select count(*) from topdevice where ip='%s'" % ip
            _, rows = db_proxy.read_db(tmp_str)
            tmp_num = rows[0][0]
            if tmp_num > 0:
                return jsonify({'status': 0, 'msg': 'ip重复，添加失败'})
        else:
            tmp_str = "select count(*) from topdevice where ip='%s' and mac='%s'" %(ip,mac)
            _, rows = db_proxy.read_db(tmp_str)
            tmp_num = rows[0][0]
            if tmp_num > 0:
                return jsonify({'status': 0, 'msg': 'mac重复，添加失败'})
        tmp_mac = mac.replace(':', '')
        # 新增资产计算厂商，类型，型号
        dev_pro_list = []
        custom_default_flag = "1"
        if auto_flag == 1:  # 自动识别
            auto_mac = "'"+mac+"'"
            vendor, dev_type, mode, custom_default_flag = devAutoIdentify.calculate_dev_info(auto_mac, dev_pro_list,current_app.logger)
        sql_str = """insert into topdevice(ip,mac,name,dev_type,dev_desc,category_info,dev_mode,auto_flag,proto_info,custom_default_flag) 
                        values('%s','%s','%s',%d,'%s','%s','%s','%d',"%s",'%s')""" % (
            ip, mac, name, dev_type, desc, vendor, mode, auto_flag, dev_pro_list, custom_default_flag)
        _ = db_proxy.write_db(sql_str)
        # send operation log
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['Operate'] = u"添加资产" + name
        msg['ManageStyle'] = 'WEB'
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 1, 'msg': '添加成功'})
    elif request.method == 'PUT':
        post_data = request.get_json()
        dev_id = post_data.get('id', '')
        name = post_data.get('name', '').encode('utf-8')
        dev_type = post_data.get('type', 0)
        desc = post_data.get('desc', '').encode('utf-8')
        vendor = post_data.get('vender', '').encode('utf-8')
        mode = post_data.get('mode', '').encode('utf-8')
        auto_flag = post_data.get('auto_flag', 1)
        is_unknown = post_data.get('unknown', '')
        loginuser = post_data.get('loginuser', '')
        if len(name) > 64:
            return jsonify({'status': 0, 'msg': 'name长度不合法'})
        name_str = "select count(*) from topdevice where name='%s' and id<>%d" % (name, dev_id)
        _, rows = db_proxy.read_db(name_str)
        tmp_num = rows[0][0]
        if tmp_num > 0:
            return jsonify({'status': 0, 'msg': '设备名已存在，编辑失败'})
        if len(desc) > 64:
            return jsonify({'status': 0, 'msg': '描述长度不合法'})
        if len(mode) > 64:
            return jsonify({'status': 0, 'msg': '模式长度不合法'})
        sql_str = "select ip, mac,proto_info, custom_default_flag from topdevice where id = '%d'" % (dev_id)
        _, rows = db_proxy.read_db(sql_str)
        dev_pro_list = eval(rows[0][2])
        custom_default_flag = rows[0][3]
        # 修改资产为手动时需要再次计算资产信息
        if auto_flag == 1:  # 自动识别
            auto_mac = "'"+rows[0][1]+"'"
            dev_pro_list = eval(rows[0][2])
            vendor, dev_type, mode, custom_default_flag = devAutoIdentify.calculate_dev_info(auto_mac, dev_pro_list, current_app.logger)

        sql_str = '''update topdevice set name='%s',dev_type=%d,dev_desc='%s',category_info='%s',is_unknown=%d,dev_mode='%s',auto_flag='%d',proto_info="%s",custom_default_flag='%s' where id=%d''' % \
                  (name, dev_type, desc, vendor, is_unknown, mode, auto_flag, dev_pro_list, custom_default_flag, dev_id)
        _ = db_proxy.write_db(sql_str)
        # send operation log
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['Operate'] = u"修改资产信息" + name
        msg['ManageStyle'] = 'WEB'
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 1, 'msg': '修改成功'})
    else:
        post_data = request.get_json()
        dev_ids = post_data.get('ids', '')
        loginuser = post_data.get('loginuser', '')
        count_str = "select count(*) from topdevice where id in('%s') and is_topo=1"
        _, count_rows = db_proxy.read_db(count_str)
        tmp_num = count_rows[0][0]
        if tmp_num > 0:
            return jsonify({'status': 0, 'msg': '存在已经加入topo设备，删除失败'})
        sql_str = "delete from topdevice where id in(%s)" % dev_ids
        _ = db_proxy.write_db(sql_str)
        # send operation log
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['Operate'] = u"删除资产"
        msg['ManageStyle'] = 'WEB'
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 1, 'msg': '删除成功'})


@topdev_page.route('/join_toposhow', methods=['POST'])
@login_required
def join_topo():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    post_data = request.get_json()
    is_topo = post_data.get('is_topo', 0)
    dev_id = post_data.get('id', '0')
    loginuser = post_data.get('loginuser', '')
    count_str = "select count(*) from topdevice where is_topo=1"
    id_list = dev_id.split(',')
    id_list_len = len(id_list)
    _, rows = db_proxy.read_db(count_str)
    num = rows[0][0]
    if is_topo == 1 and num+id_list_len > TOP_DEV_LIMIT:
        msg = "拓扑设备数量超出上限50"
        return jsonify({'status': 0, 'msg': msg})
    sql_str = "update topdevice set is_topo=%d where id in (%s)" % (is_topo, dev_id)
    _ = db_proxy.write_db(sql_str)
    # send operation log
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    if is_topo == 0:
        tmp_msg = '移出topo成功'
        msg['Operate'] = u"设备移出topo"
    else:
        tmp_msg = '加入topo成功'
        msg['Operate'] = u"设备加入topo"
    if dev_id and dev_id != '0':
        send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1, 'msg': tmp_msg})


@topdev_page.route('/topo_show_info', methods=['GET', 'PUT'])
@login_required
def show_topo_info():
    config_db_proxy = DbProxy(CONFIG_DB_NAME)
    db_proxy = DbProxy()
    if request.method == 'GET':
        sql_str = 'select xml_info from topshow where id=1'
        _, rows = config_db_proxy.read_db(sql_str)
        xml_info = rows[0][0]
        dev_data = TopOper.get_topo_dict(config_db_proxy, db_proxy,1)
        for dev in dev_data:
            mapdict = get_dev_map(config_db_proxy)
            try:
                dev["device_info"]["type_name"] = mapdict[int(dev["device_info"]["dev_type"])]
            except KeyError:
                dev["device_info"]["type_name"] = "未知"
        return jsonify({'status': 1, 'xml_info': xml_info, 'dev_info': dev_data})
    else:
        post_data = request.get_json()
        xml_info = post_data.get('xml_info', '').encode('utf-8')
        sql_str = "update topshow set xml_info='%s' where id=1" % xml_info
        _ = config_db_proxy.write_db(sql_str)
        return jsonify({'status': 1, 'msg': '保存成功'})


@topdev_page.route('/get_add_device')
@login_required
def mw_add_topo():
    config_db_proxy = DbProxy(CONFIG_DB_NAME)
    db_proxy = DbProxy()
    dev_data = TopOper.get_topo_dict(config_db_proxy, db_proxy, 0)
    for dev in dev_data:
        mapdict = get_dev_map(config_db_proxy)
        try:
            dev["device_info"]["type_name"]=mapdict[int(dev["device_info"]["dev_type"])]
        except KeyError:
            dev["device_info"]["type_name"]="未知"
    return jsonify({'status': 1, 'device_list': dev_data})


@topdev_page.route('/device_type', methods=["GET", "POST", "PUT", "DELETE"])
@login_required
def mw_device_name():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == "GET":
        cmd_str = "select type_id,device_name,pre_define from dev_type"
        _, rows = db_proxy.read_db(cmd_str)
        data = []
        if len(rows) > 0:
            for row in rows:
                name_dict = {}
                name_dict["id"] = row[0]
                name_dict["name"] = row[1]
                name_dict["pre_define"] = row[2]
                data.append(name_dict)
        return jsonify({"data": data, "status": 1, "msg": "获取成功"})

    elif request.method == "POST":
        data = request.get_json()
        name = data.get("device_name")
        if len(name.encode("utf-8")) > 64:
            return jsonify({"status": 0, "msg": u"设备类型长度不能超过64字节"})
        loginuser = data.get("loginuser")
        userip = get_oper_ip_info(request)
        msg = {}
        msg['UserName']=loginuser
        msg['UserIP']=userip
        msg['ManageStyle']='WEB'
        msg['Result']='0'
        msg['Operate'] = u"添加设备类型: " + name
        sql_str = "select count(*) from dev_type where device_name='{}'".format(name)
        _, rows = db_proxy.read_db(sql_str)
        if rows[0][0] > 0:
            return jsonify({"status": 0, "msg": u"设备类型已存在"})

        sql_str = "select count(*) from dev_type"
        _, rows = db_proxy.read_db(sql_str)
        if rows[0][0] > 50:
            return jsonify({"status": 0, "msg": u"达到50个设备类型上限"})

        add_str = "insert into dev_type (device_name, pre_define) values ('{}', 0)".format(name)
        res = db_proxy.write_db(add_str)
        if res != 0:
            msg['Result']='1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({"status": 0, "msg": u"添加失败"})
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({"status": 1, "msg": u"添加成功"})

    elif request.method == "DELETE":
        data = request.get_json()
        ids = int(data.get("ids"))
        if not ids:
            return jsonify({"status": 0, "msg": u"未选中任何数据"})
        loginuser = data.get("loginuser")
        userip = get_oper_ip_info(request)
        msg={}
        msg['UserName']=loginuser
        msg['UserIP']=userip
        msg['ManageStyle']='WEB'
        msg['Result']='0'
        msg['Operate'] = u"删除设备类型: "

        sql_str = "select pre_define from dev_type where type_id in ({})".format(ids)
        res, rows = db_proxy.read_db(sql_str)
        if int(rows[0][0]) == 1:
            return jsonify({"status": 0, "msg": u"不能删除预定义的设备类型"})
        sql_str = "select device_name from dev_type where type_id in ({})".format(ids)
        res, rows = db_proxy.read_db(sql_str)
        if len(rows) > 0:
            name_str = ",".join([row[0] for row in rows])
            msg['Operate'] += name_str
        del_str = "delete from dev_type where type_id in ({})".format(ids)
        res = db_proxy.write_db(del_str)
        if res != 0:
            msg['Result']='1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({"status": 0, "msg": u"删除失败"})
        alter_atr = "update topdevice set dev_type=0 where dev_type={}".format(ids)
        db_proxy.write_db(alter_atr)
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({"status": 1, "msg": u"删除成功"})

    else:
        return jsonify({"status": 0, "msg": "method not allowed"})


def get_id_by_devtype(type_name, db):
    if type_name == "未知":
        return 0
    cmd_str = "select type_id from dev_type where device_name = '{}'".format(type_name)
    res,rows = db.read_db(cmd_str)
    if len(rows) > 0:
        return rows[0][0]
    else:
        cmd_str = "insert into dev_type (device_name) values ('{}')".format(type_name)
        db.write_db(cmd_str)
        cmd_str = "select type_id from dev_type where device_name = '{}'".format(type_name)
        res, rows = db.read_db(cmd_str)
        return rows[0][0]


@topdev_page.route('/dev_listImport',methods=['GET','POST'])
@login_required
def mw_dev_listImport():
    if request.method == 'POST':
        db_proxy = DbProxy(CONFIG_DB_NAME)
        loginuser = request.form.get('loginuser')
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserIP'] = userip
        msg['UserName'] = loginuser
        msg['ManageStyle'] = 'WEB'
        sta_str = "select status from whiteliststudy where id=1"
        result, rows = db_proxy.read_db(sta_str)
        tmp_status = rows[0][0]
        if tmp_status == 1:
            msg['Operate'] = u"导入dev_list"
            msg['Result'] = '1' 
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 2, 'msg': u"白名单正在学习中,请稍后操作..."})

        try:
            file = request.files['file']
            if not file or not allowed_file(file.filename):
                return jsonify({'status': 0})
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            FileName = '%s%s'%(UPLOAD_FOLDER, filename)
            csvfile = open(FileName,'rb')
            reader = csv.reader(csvfile,dialect='excel')
            rows = [row for row in reader]
            # current_app.logger.info(rows[0])
            # current_app.logger.info(rows)
            if rows[0] != ['\xef\xbb\xbf设备名','ip','mac','厂商信息','设备类型','设备型号']:
                msg['Operate'] = u"导入dev_list"
                msg['Result'] = '1'
                send_log_db(MODULE_OPERATION, msg)
                os.system("rm '%s'"%(FileName))
                return jsonify({'status': 2, 'msg': u"导入文件格式错误"})

            for data in rows[1:]:
                # current_app.logger.info(rows[1:])
                name,ip,mac,category_info,dev_type,dev_mode = data
                try:
                    if len(name) == 0 or len(mac) == 0:#首先设备名和Mac地址不能为空
                        continue
                    tmp_sql="select name from topdevice where name='%s'"%(name)
                    # current_app.logger.info(tmp_sql)
                    result,rows = db_proxy.read_db(tmp_sql)
                    if len(rows) == 0:
                        if len(ip) > 0:#如果ip不为空，判断是否重复
                            addr = ipaddress.ip_address(unicode(ip))
                            ip_type = addr.version
                            if ip_type == 6:
                                ip_net6 = ipaddress.ip_network(unicode(ip))
                                ip = str(ip_net6.exploded.split('/')[0])
                            sql="select ip from topdevice where ip='%s'"%(ip)
                            # current_app.logger.info(sql)
                            result,rows = db_proxy.read_db(sql)
                            if len(rows)>0:#如果重复，跳过
                                pass
                            else:#如果不重复，导入
                                # 手动导入时设置厂商，设备类型，型号为手动识别auto_flag = 0
                                auto_flag = 0
                                custom_default_flag = "1"
                                dev_type = get_id_by_devtype(dev_type, db_proxy)
                                sql_str = "insert into topdevice(name,ip,mac,category_info,dev_type,dev_mode,auto_flag,custom_default_flag)values('%s','%s','%s','%s','%s','%s','%d','%s')" % (
                                name, ip, mac, category_info, dev_type, dev_mode, auto_flag, custom_default_flag)
                                db_proxy.write_db(sql_str)
                        else:#如果ip为空，则判断mac是否重复
                            sql="select mac from topdevice where ip='' and mac='%s'"%(mac)
                            """select mac from topdevice where ip='' and mac='00:50:56:2a:ce:ee'"""
                            result,rows = db_proxy.read_db(sql)
                            if len(rows)>0:#如果重复，跳过
                                pass
                            else:#不重复导入
                                # 手动导入时设置厂商，设备类型，型号为手动识别auto_flag = 0
                                auto_flag = 0
                                dev_type = get_id_by_devtype(dev_type, db_proxy)
                                custom_default_flag = "1"
                                sql_str = "insert into topdevice(name,ip,mac,category_info,dev_type,dev_mode,auto_flag,custom_default_flag)values('%s','%s','%s','%s','%s','%s','%d','%s')" % (
                                    name, ip, mac, category_info, dev_type, dev_mode, auto_flag, custom_default_flag)
                                db_proxy.write_db(sql_str)

                except:
                    current_app.logger.error(traceback.format_exc())
                    continue
            os.system("rm '%s'"%(FileName))
            msg['Operate'] = u"导入dev_list"
            msg['Result'] = '0'
            send_log_db(MODULE_OPERATION, msg)
            status = 1
            return jsonify({'status': status})
        except:
            current_app.logger.error(traceback.format_exc())
            msg['Operate'] = u"导入dev_list"
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            # os.system("rm '%s'"%(FileName))
            status = 0
            return jsonify({'status': status})


@topdev_page.route('/dev_listExport',methods=['GET','POST'])
@login_required
def mw_dev_listExport():
    if request.method == 'GET':
        db_proxy = DbProxy(CONFIG_DB_NAME)
        loginuser = request.args.get('loginuser')
        action = request.args.get('action', type=int)
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserIP'] = userip
        msg['UserName'] = loginuser
        msg['ManageStyle'] = 'WEB'
        current_app.logger.info(action)
        if action == 0:#传入action,如果action为0 判断是否在学习
            sta_str = "select status from whiteliststudy where id=1"
            result, rows = db_proxy.read_db(sta_str)
            tmp_status = rows[0][0]
            if tmp_status == 1:
                msg['Operate'] = u"导出dev_list"
                msg['Result'] = '1' 
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({'status': 2, 'msg': u"白名单正在学习中,请稍后操作..."}) 
            else:#没有学习返回1
                status = 1
                return jsonify({'status':status})
        else: #正常导出下载
            try:
                os.system('rm /data/rules/dev_list.csv')
                csvfile = open('/data/rules/dev_list.csv','wb')
                csvfile.write(codecs.BOM_UTF8)
                writer = csv.writer(csvfile,dialect='excel')
                writer.writerow(['设备名','ip','mac','厂商信息','设备类型','设备型号'])
                sql="select name,ip,mac,category_info,dev_type,dev_mode from topdevice"
                current_app.logger.info(sql)
                result, rows = db_proxy.read_db(sql)
                dev_map = get_dev_map(db_proxy)
                for row in rows:
                    row = list(row)
                    row[4] = dev_map[row[4]]
                    writer.writerow(row)
                csvfile.close()
                msg['Operate'] = u"导出dev_list"
                msg['Result'] = '0'
                send_log_db(MODULE_OPERATION, msg)
                return send_from_directory("/data/rules/", "dev_list.csv", as_attachment=True)
            except:
                current_app.logger.error(traceback.format_exc())
                msg['Operate'] = u"导出dev_list"
                msg['Result'] = '1'
                send_log_db(MODULE_OPERATION, msg)
                status = 0
                return jsonify({'status': status})


# 厂商信息导入上传
@topdev_page.route('/vendor_fileImport', methods=['GET', 'POST'])
@login_required
def mw_vendor_fileImport():
    if request.method == 'POST':
        db_proxy = DbProxy(CONFIG_DB_NAME)
        loginuser = request.form.get('loginuser')
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserIP'] = userip
        msg['UserName'] = loginuser
        msg['ManageStyle'] = 'WEB'
        sta_str = "select status from whiteliststudy where id=1"
        result, rows = db_proxy.read_db(sta_str)
        tmp_status = rows[0][0]
        if tmp_status == 1:
            msg['Operate'] = u"导入厂商信息"
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            status = 2
            return jsonify({'status': status, 'msg': u"白名单正在学习中,请稍后操作..."})
        try:
            if not os.path.exists(VENDOR_UPLOAD_FOLDER):
                os.makedirs(VENDOR_UPLOAD_FOLDER)
            file = request.files['vendor_file']
            if not file or not vendor_allowed_file(file.filename):
                return jsonify({'status': 0, 'msg': '文件格式非法，请上传json格式文件！'})
            if file:
                # 将新文件保存到路径下(所有上传文件重新命名为vendor.json)
                tmp_vendorfile = 'tmp_vendor.json'
                file.save(os.path.join(VENDOR_UPLOAD_FOLDER, tmp_vendorfile))
                # 判断数据是否是json格式，简单做一个验证
                check_result = verify()
                if check_result:
                    os.system("cp /data/vendorinfo/tmp_vendor.json /data/vendorinfo/vendor.json")
                    os.system("rm -rf /data/vendorinfo/tmp_vendor.json")
                    msg['Operate'] = u"导入厂商信息"
                    msg['Result'] = '0'
                    send_log_db(MODULE_OPERATION, msg)
                    status = 1
                    return jsonify({'status': status, 'msg': '导入厂商信息成功'})
                else:
                    os.system("rm -rf /data/vendorinfo/tmp_vendor.json")
                    msg['Operate'] = u"导入厂商信息"
                    msg['Result'] = '1'
                    send_log_db(MODULE_OPERATION, msg)
                    status = 0
                    return jsonify({'status': status, 'msg': '厂商信息内容格式不合法'})
        except:
            current_app.logger.error(traceback.format_exc())
            msg['Operate'] = u"导入厂商信息"
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            status = 0
            return jsonify({'status': status, 'msg': '导入厂商信息失败'})


# 厂商信息导出下载
@topdev_page.route('/vendor_fileExport', methods=['GET', 'POST'])
@login_required
def mw_venndor_fileExport():
    if request.method == 'GET':
        db_proxy = DbProxy(CONFIG_DB_NAME)
        loginuser = request.args.get('loginuser')
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserIP'] = userip
        msg['UserName'] = loginuser
        msg['ManageStyle'] = 'WEB'
        try:
            if not os.path.exists(VENDOR_UPLOAD_FOLDER + 'vendor.json'):
                os.system("touch -f /data/vendorinfo/vendor.json")
            msg['Operate'] = u"导出厂商信息"
            msg['Result'] = '0'
            send_log_db(MODULE_OPERATION, msg)
            return send_from_directory(VENDOR_UPLOAD_FOLDER, "vendor.json", as_attachment=True)
        except:
            current_app.logger.error(traceback.format_exc())
            msg['Operate'] = u"导出厂商信息"
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            status = 0
            return jsonify({'status': status})


# 设备指纹配置
@topdev_page.route('/dev_fingerprint', methods=['GET', 'POST', 'DELETE', 'PUT'])
@login_required
def mw_dev_fingerprint():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    oper_msg = {}
    userip = get_oper_ip_info(request)
    # 主页面及详情页面获取全部
    if request.method == 'GET':
        page = request.args.get('page', 0, type=int)
        add_str = ' order by id desc limit ' + str((page - 1) * 10) + ',10'
        info = []

        cmd_str = "select * from self_define_fingerprint" + add_str
        try:
            res, rows = db_proxy.read_db(cmd_str)
            for row in rows:
                item = {}
                item["content_id"] = row[0]
                timeArray = time.localtime(row[1])
                item["update_time"] = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                item["rule_name"] = row[3]
                item["vendor"] = row[4]
                item["dev_type"] = row[5]
                item["dev_model"] = row[6]
                item["mac_sets"] = []
                for i in eval(row[2]):
                    tmp_item = {}
                    tmp_item["mac"] = i
                    item["mac_sets"].append(tmp_item)
                item["proto_port_set"] = []
                for k in eval(row[7]):
                    tmp_dict = {}
                    tmp_dict["proto_name"] = k[0]
                    tmp_dict["proto_port"] = k[1]
                    tmp_dict["cli_server_type"] = k[2]
                    item["proto_port_set"].append(tmp_dict)
                info.append(item)

            total_str = "select count(*) from self_define_fingerprint"
            res, rows = db_proxy.read_db(total_str)
            if res == 0:
                total_num = rows[0][0]
            else:
                total_num = 0
            return jsonify({'data': info, 'total': total_num, 'status': 1})
        except:
            current_app.logger.error(traceback.format_exc())
            return jsonify({'data': [], 'total': 0, 'status': 1})

    # 详情页面新增
    elif request.method == 'POST':
        data = request.get_json()
        try:
            rule_name = data.get("rule_name")
            vendor = data.get("vendor")
            dev_type = data.get("dev_type")
            dev_model = data.get("dev_model")
            mac_sets = data.get("mac_sets")
            proto_port_set = data.get("proto_port_set")
            loginuser = data.get("loginuser")
            mac_count = len(mac_sets)
            proto_count = len(proto_port_set)
            if len(rule_name.encode("utf-8")) > 128:
                return jsonify({"status": 0, "msg": u"指纹名称不能超过128字节"})
            if len(vendor.encode("utf-8")) > 128:
                return jsonify({"status": 0, "msg": u"厂商名称不能超过128字节"})
            if mac_count == 0:
                return jsonify({"status": 0, "msg": u"MAC地址信息不能为空！"})
            if mac_count > 5:
                return jsonify({"status": 0, "msg": u"MAC配置条数最多配置5条！"})
            if proto_count > 5:
                return jsonify({"status": 0, "msg": u"协议配置条数最多配置5条！"})
        except:
            current_app.logger.error(traceback.format_exc())
            return jsonify({"status": 0, "msg": u"参数错误"})
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        oper_msg['Operate'] = "添加自定义协议内容:" + rule_name
        oper_msg['Result'] = '1'
        try:
            count_str = "select count(*) from self_define_fingerprint where rule_name = '{}'".format(rule_name)
            res, rows = db_proxy.read_db(count_str)
            if res == 0 and rows[0][0] > 0:
                return jsonify({"status": 0, "msg": u"指纹名称已存在"})

            count_str = "select count(*) from self_define_fingerprint"
            res, rows = db_proxy.read_db(count_str)
            if res == 0 and rows[0][0] > 200:
                return jsonify({"status": 0, "msg": u"指纹配置条数上限为200条"})

            vendor = vendor if vendor else "未知"
            dev_type = dev_type if dev_type else 0
            dev_model = dev_model if dev_model else "未知"

            tmp_mac_list = []
            for mac_elm in mac_sets:
                mac_elm["mac"] = mac_elm["mac"].lower()
                if check_mac(mac_elm["mac"]) is False:
                    return jsonify({'status': 0, "msg": u"MAC地址格式不合法"})
                tmp_mac_list.append("'"+mac_elm["mac"]+"'")
            mac_str = "["+(",".join(tmp_mac_list))+"]"

            tmp_proto_list = []
            for pro_elm in proto_port_set:
                if pro_elm["proto_name"] == "" and pro_elm["proto_port"] == "":
                    return jsonify({"status": 0, "msg": u"协议和端口至少配置一个"})
                # cli_server_type 0\1\2代表：双选中\只客户端选中\只服务端选中
                tmp_proto_list.append("['" + pro_elm["proto_name"] + "','" + pro_elm["proto_port"] + "'," + pro_elm["cli_server_type"] + "]")
            proto_port_str = "[" + (",".join(tmp_proto_list)) + "]"
            update_time = int(time.time())
            cmd_str = '''insert into self_define_fingerprint (update_time,mac,rule_name,vendor,dev_type,dev_model,proto_port_attr) values ({},"{}",'{}','{}',{},'{}',"{}")'''.format(
                update_time, mac_str, rule_name, vendor, dev_type, dev_model, proto_port_str)
            res = db_proxy.write_db(cmd_str)
            if res != 0:
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({"status": 0, "msg": u"添加失败"})

            # 新增这条指纹成功后，与这条指纹mac相关的设备需要重新计算厂商，类型，型号；待优化：后台计算，页面先返回消息
            # 去重后列表遍历
            ip_mac_list = []
            for mac in mac_sets:
                mac = mac["mac"]
                mac = mac[0:8].upper()
                sql_str = '''select ip,mac from topdevice where mac like "%s%%"''' % (mac)
                res, rows = db_proxy.read_db(sql_str)
                for row in rows:
                    tmp_mac_list = []
                    tmp_mac_list.append(row[0])
                    tmp_mac_list.append(row[1])
                    ip_mac_list.append(tmp_mac_list)
            # 多重列表去重 [['192.168.1.21', '00:50:56:2a:ce:ee'], ['192.168.0.86', '00:50:56:2a:ce:ee']]
            new_list = [list(t) for t in set(tuple(i) for i in ip_mac_list)]
            new_list.sort(key=ip_mac_list.index)

            for data in new_list:
                ip = data[0]
                mac = "'" + data[1] + "'"
                sql_str = "select proto_info, custom_default_flag,ip from topdevice where ip = '%s' and mac = %s" % (ip,mac)
                res, rows = db_proxy.read_db(sql_str)
                for row in rows:
                    dev_pro_list = eval(row[0])
                    ip = row[2]
                vendor, dev_type, dev_model, custom_default_flag = devAutoIdentify.calculate_dev_info(mac, dev_pro_list,current_app.logger)

                # 记录厂商，类型，型号
                update_str = '''update topdevice set category_info = "%s", dev_mode = "%s",dev_type = %d, custom_default_flag = "%s" where ip = "%s" and mac = %s''' % (
                    vendor, dev_model, dev_type, custom_default_flag, ip, mac)
                db_proxy.write_db(str(update_str))

            oper_msg['Result'] = '0'
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 1, "msg": u"添加成功"})
        except:
            current_app.logger.error(traceback.format_exc())
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": u"添加失败"})

    # 详情页面的修改和删除
    elif request.method == 'PUT':
        data = request.get_json()
        try:
            content_id = data.get("content_id")
            rule_name = data.get("rule_name")
            vendor = data.get("vendor")
            dev_type = data.get("dev_type")
            dev_model = data.get("dev_model")
            mac_sets = data.get("mac_sets")
            proto_port_set = data.get("proto_port_set")
            loginuser = data.get("loginuser")
            mac_count = len(mac_sets)
            proto_count = len(proto_port_set)
            if len(rule_name.encode("utf-8")) > 128:
                return jsonify({"status": 0, "msg": u"指纹名称不能超过128字节"})
            if len(vendor.encode("utf-8")) > 128:
                return jsonify({"status": 0, "msg": u"厂商名称不能超过128字节"})
            if mac_count == 0:
                return jsonify({"status": 0, "msg": u"MAC地址信息不能为空！"})
            if mac_count > 5:
                return jsonify({"status": 0, "msg": u"MAC配置条数最多配置5条！"})
            if proto_count > 5:
                return jsonify({"status": 0, "msg": u"协议配置条数最多配置5条！"})
        except:
            current_app.logger.error(traceback.format_exc())
            return jsonify({"status": 0, "msg": u"参数错误"})
        try:
            cmd_str = "select rule_name from self_define_fingerprint where id={}".format(content_id)
            res, rows = db_proxy.read_db(cmd_str)
            old_name = rows[0][0]
            if res != 0:
                return jsonify({"status": 0, "msg": u"不存在的id"})
            count_str = "select count(*) from self_define_fingerprint where rule_name = '{}' and id != {}".format(rule_name,content_id)
            res, rows = db_proxy.read_db(count_str)
            if res == 0 and rows[0][0] > 0:
                return jsonify({"status": 0, "msg": u"指纹名称已存在"})
            oper_msg['UserName'] = loginuser
            oper_msg['UserIP'] = userip
            oper_msg['ManageStyle'] = 'WEB'
            oper_msg['Operate'] = "编辑指纹内容:" + old_name

            vendor = vendor if vendor else "未知"
            dev_type = dev_type if dev_type else 0
            dev_model = dev_model if dev_model else "未知"

            tmp_mac_list = []
            for i in mac_sets:
                i["mac"] = i["mac"].lower()
                if check_mac(i["mac"]) is False:
                    return jsonify({'status': 0, "msg": u"MAC地址格式不合法"})
                tmp_mac_list.append("'" + i["mac"] + "'")
            mac_str = "[" + (",".join(tmp_mac_list)) + "]"

            tmp_proto_list = []
            for j in proto_port_set:
                if j["proto_name"] == "" and j["proto_port"] == "":
                    return jsonify({"status": 0, "msg": u"协议和端口至少配置一个"})
                tmp_proto_list.append("['" + j["proto_name"] + "','" + j["proto_port"] + "'," + j["cli_server_type"] + "]")
            proto_port_str = "[" + (",".join(tmp_proto_list)) + "]"

            # delete and add
            del_str = "delete from self_define_fingerprint where id={}".format(content_id)
            db_proxy.write_db(del_str)
            update_time = (int(time.time()))
            cmd_str = '''insert into self_define_fingerprint (update_time,mac,rule_name,vendor,dev_type,dev_model,proto_port_attr) values ({},"{}",'{}','{}',{},'{}',"{}")'''.format(
                update_time, mac_str, rule_name, vendor, dev_type, dev_model, proto_port_str)
            res = db_proxy.write_db(cmd_str)
            if res != 0:
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({"status": 0, "msg": u"编辑失败"})

            # 这条修改成功后，所有自动的设备厂商，类型，型号，需要都匹配一遍这条信息
            sql_str = "select proto_info,mac,ip, auto_flag from topdevice "
            res, rows = db_proxy.read_db(sql_str)
            for row in rows:
                auto_flag = row[3]
                if auto_flag:
                    dev_pro_list = eval(row[0])
                    mac = "'" + row[1] + "'"
                    ip = row[2]
                    vendor, dev_type, dev_model, custom_default_flag = devAutoIdentify.calculate_dev_info(mac, dev_pro_list,current_app.logger)

                    # 记录厂商，类型，型号
                    update_str = '''update topdevice set category_info = "%s", dev_mode = "%s",dev_type = %d, custom_default_flag = "%s" where ip = '%s' and mac = %s''' % (
                        vendor, dev_model, dev_type, custom_default_flag, ip, mac)
                    db_proxy.write_db(str(update_str))

            oper_msg['Result'] = '0'
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 1, "msg": u"编辑成功"})
        except:
            current_app.logger.error(traceback.format_exc())
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": u"编辑失败"})

    # 主页面的删除
    elif request.method == "DELETE":
        data = request.get_json()
        loginuser = data.get("loginuser")
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        try:
            content_id = data.get("content_id")
            cmd_str = "select rule_name from self_define_fingerprint where id in ({})".format(content_id)
            res, rows = db_proxy.read_db(cmd_str)
            name_list = [row[0] for row in rows]
            content_name_str = ",".join(name_list)
            oper_msg['Operate'] = "删除指纹内容:" + content_name_str
            oper_msg['Result'] = '1'
            del_str = "delete from self_define_fingerprint where id in ({})".format(content_id)
            res = db_proxy.write_db(del_str)
            if res != 0:
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({"status": 0, "msg": u"删除失败"})
            oper_msg['Result'] = '0'
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 1, "msg": u"删除成功"})
        except:
            current_app.logger.error(traceback.format_exc())
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": u"删除失败"})


# 获取自定义协议信息
@topdev_page.route('/get_selfproto', methods=['GET', 'POST'])
@login_required
def get_selfproto():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    cmd_str = "select proto_id ,proto_name from self_define_proto_config"
    info=[]
    try:
        res, rows = db_proxy.read_db(cmd_str)
        for row in rows:
            info.append(row[1])

        total_str = "select count(*) from self_define_proto_config"
        res, rows = db_proxy.read_db(total_str)
        if res == 0:
            total_num = rows[0][0]
        else:
            total_num = 0
        return jsonify({'data': info, 'total': total_num, 'status': 1})
    except:
        current_app.logger.error(traceback.format_exc())
        return jsonify({'data': [], 'total': 0, 'status': 1})

