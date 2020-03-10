#!/usr/bin/python
# -*- coding:UTF-8 -*-
from flask import request
from flask import jsonify
from flask import Blueprint
from global_function.log_oper import *
# flask-login
from flask_login.utils import login_required
from flask import current_app
import ipaddress
auditstrategy_page = Blueprint('auditstrategy_page', __name__, template_folder='templates')

ADUITSTRATEGY_RULE_PATH = '/data/rules/traffic-capture-dpi/traffic.rules'
ADUITSTRATEGY_PROTO = ('any', '6', '17')


@auditstrategy_page.route('/auditstrategySearch', methods=['GET', 'POST'])
@login_required
def mw_auditstrategy_search():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    data = []
    status = 1
    sql_str = "select * from auditstrategy where 1=1 "
    num_str = "select count(*) from auditstrategy where 1=1 "
    if request.method == 'POST':
        post_data = request.get_json()
        src_ip = post_data['srcip']
        dst_ip = post_data['dstip']
        src_mac = post_data['srcmac']
        dst_mac = post_data['dstmac']
        dst_port = post_data['port']
        proto = int(post_data['proto'])
        page = int(post_data['page'])
    elif request.method == 'GET':
        page = request.args.get("page", 1, type=int)
        src_ip = request.args.get('srcip', '')
        dst_ip = request.args.get('dstip', '')
        src_mac = request.args.get('srcmac', '')
        dst_mac = request.args.get('dstmac', '')
        dst_port = request.args.get('port', '')
        proto = request.args.get('proto', 0, type=int)
    else:
        page = 1
        src_ip = ''
        dst_ip = ''
        src_mac = ''
        dst_mac = ''
        dst_port = ''
        proto = 0
    add_str = ' order by id asc limit ' + str((page - 1) * 10) + ',10;'
    if src_ip is not None and len(src_ip) > 0:
        sql_str += " and srcip='%s'" % (src_ip)
        num_str += " and srcip='%s'" % (src_ip)
    if dst_ip is not None and len(dst_ip) > 0:
        sql_str += " and dstip='%s'" % (dst_ip)
        num_str += " and dstip='%s'" % (dst_ip)
    if src_mac is not None and len(src_mac) > 0:
        sql_str += " and srcmac='%s'" % (src_mac)
        num_str += " and srcmac='%s'" % (src_mac)
    if dst_mac is not None and len(dst_mac) > 0:
        sql_str += " and dstmac='%s'" % (dst_mac)
        num_str += " and dstmac='%s'" % (dst_mac)
    if dst_port is not None and len(dst_port) > 0:
        sql_str += " and dstport='%s'" % (dst_port)
        num_str += " and dstport='%s'" % (dst_port)
    if proto > 0:
        sql_str += " and proto=%d" % (proto)
        num_str += " and proto=%d" % (proto)
    sql_str += add_str
    result, rows = db_proxy.read_db(sql_str)
    for row in rows:
        data.append(row)
    result, rows = db_proxy.read_db(num_str)
    total = rows[0][0]
    return jsonify({'status': status, 'rows': data, 'total': total, 'page': page})


@auditstrategy_page.route('/addAuditstrategy', methods=['GET', 'POST'])
@login_required
def mw_auditstrategy_add():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    msg = {}
    src_result = 0
    dst_result = 0
    user_ip = get_oper_ip_info(request)
    if request.method == 'POST':
        post_data = request.get_json()
        src_ip = post_data['srcip'].encode('utf-8')
        dst_ip = post_data['dstip'].encode('utf-8')
        src_mac = post_data['srcmac'].encode('utf-8')
        dst_mac = post_data['dstmac'].encode('utf-8')
        dst_port = post_data['port'].encode('utf-8')
        ip_type = int(post_data['iptype'])
        proto = int(post_data['proto'])
        loginuser = post_data['loginuser'].encode('utf-8')
    elif request.method == 'GET':
        src_ip = request.args.get('srcip', '').encode('utf-8')
        dst_ip = request.args.get('dstip', '').encode('utf-8')
        src_mac = request.args.get('srcmac', '').encode('utf-8')
        dst_mac = request.args.get('dstmac', '').encode('utf-8')
        dst_port = request.args.get('port', '').encode('utf-8')
        proto = request.args.get('proto', 0, type=int)
        loginuser = request.args.get('loginuser', '').encode('utf-8')
    else:
        src_ip = ''
        dst_ip = ''
        src_mac = ''
        dst_mac = ''
        dst_port = ''
        proto = 0
        ip_type = 0
        loginuser = ''

    msg['UserName'] = loginuser
    msg['UserIP'] = user_ip
    msg['ManageStyle'] = 'WEB'
    if src_ip is None or len(src_ip) == 0:
        src_ip = 'any'
    else:
        '''we need to check ip address'''
        try:
            if ip_type == 4:
                ipaddress.IPv4Address(unicode(src_ip))
            elif ip_type == 6:
                ipaddress.IPv6Address(unicode(src_ip))
                # we need to switch '::' or '0' as '0000'
                src_net6 = ipaddress.ip_network(unicode(src_ip))
                src_ip = src_net6.exploded.split('/')[0]
        except:
            current_app.logger.info('audit strategy config src_ip unlawful')
            tb = traceback.format_exc()
            current_app.logger.error(tb)
            src_result = -1

    if dst_ip is None or len(dst_ip) == 0:
        dst_ip = 'any'
    else:
        '''we need to check ip address'''
        try:
            if ip_type == 4:
                ipaddress.IPv4Address(unicode(dst_ip))
            elif ip_type == 6:
                ipaddress.IPv6Address(unicode(dst_ip))
                # we need to switch '::' or '0' as '0000'
                dst_net6 = ipaddress.ip_network(unicode(dst_ip))
                dst_ip = dst_net6.exploded.split('/')[0]
        except:
            current_app.logger.info('audit strategy config dst_ip unlawful')
            tb = traceback.format_exc()
            current_app.logger.error(tb)
            dst_result = -1

    if src_mac is None or len(src_mac) == 0:
        src_mac = 'any'
    if dst_mac is None or len(dst_mac) == 0:
       dst_mac = 'any'
    if dst_port is None or len(dst_port) == 0:
        dst_port = 'any'

    msg['Operate'] = "添加审计策略规则:srcip=%s,dstip=%s,scrmac=%s,dstmac=%s,dstport=%s,proto=%s"\
                        % (src_ip, dst_ip, src_mac, dst_mac, dst_port, ADUITSTRATEGY_PROTO[proto])
    msg['Operate'] = msg['Operate'].decode("utf-8")
    if src_result == -1 or dst_result:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        if src_result == -1 and dst_result == -1:
            js_msg = u'请输入正确的源IP地址和目的IP地址'
        elif src_result == -1:
            js_msg = u'请输入正确的源IP地址'
        else:
            js_msg = u'请输入正确的目的IP地址'
        return jsonify({'status': 0, 'msg': js_msg})

    tmp_str = "select count(*) from auditstrategy where srcip='%s' and dstip='%s' and srcmac='%s' and dstmac='%s' and dstport='%s' and proto=%d" \
              % (src_ip, dst_ip, src_mac, dst_mac, dst_port, proto)
    result, rows = db_proxy.read_db(tmp_str)
    if rows[0][0] > 0:
        return jsonify({'status': 0, 'msg': u'添加的策略已存在'})
    sql_str = "insert into auditstrategy (srcip, dstip, srcmac, dstmac, dstport, proto, enabled) values('%s','%s','%s','%s','%s', %d, %d)"\
                % (src_ip, dst_ip, src_mac, dst_mac, dst_port, proto, 0)
    db_proxy.write_db(sql_str)
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@auditstrategy_page.route('/delAuditstrategy', methods=['GET', 'POST'])
@login_required
def mw_auditstrategy_del():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    msg = {}
    user_ip = get_oper_ip_info(request)
    src_ip = ''
    dst_ip = ''
    src_mac = ''
    dst_mac = ''
    dst_port = ''
    proto = 0
    enable = 0
    if request.method == 'POST':
        post_data = request.get_json()
        id = int(post_data['id'])
        loginuser = post_data['loginuser'].encode('utf-8')
    elif request.method == 'GET':
        id = request.args.get('id', 0, type=int)
        loginuser = request.args.get('loginuser', '').encode('utf-8')
    else:
        loginuser = ''
        id = 0
    tmp_str = 'select srcip,dstip,srcmac,dstmac,dstport,proto,enabled from auditstrategy where id=%d'%(id)
    result, rows = db_proxy.read_db(tmp_str)
    for row in rows:
        src_ip = row[0]
        dst_ip = row[1]
        src_mac = row[2]
        dst_mac = row[3]
        dst_port = row[4]
        proto = row[5]
        enable = row[6]
    sql_str = "delete from auditstrategy where id=%d"%(id)
    db_proxy.write_db(sql_str)
    if 1 == enable:
        deploy_audit_strategy()
    msg['UserName'] = loginuser
    msg['UserIP'] = user_ip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = "删除审计策略规则:srcip=%s,dstip=%s,scrmac=%s,dstmac=%s,dstport=%s,proto=%s" \
                     % (src_ip, dst_ip, src_mac, dst_mac, dst_port, ADUITSTRATEGY_PROTO[proto])
    msg['Operate'] = msg['Operate'].decode("utf-8")
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@auditstrategy_page.route('/deployAuditstrategy', methods=['GET', 'POST'])
@login_required
def mw_auditstrategy_deploy():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    msg = {}
    src_ip = ''
    dst_ip = ''
    src_mac = ''
    dst_mac = ''
    dst_port = ''
    proto = 0
    user_ip = get_oper_ip_info(request)
    if request.method == 'POST':
        post_data = request.get_json()
        loginuser = post_data['loginuser'].encode('utf-8')
        id = int(post_data['id'])
        is_all = int(post_data['isall'])
        start = int(post_data['status'])
    elif request.method == 'GET':
        loginuser = request.args.get('loginuser', '').encode('utf-8')
        id = request.args.get('id', 0, type=int)
        is_all = request.args.get('isall', 0, type=int)
        start = request.args.get('status', 0, type=int)
    else:
        loginuser = ''
        id = 0
        is_all = 0
        start = 0
    if is_all == 0:
        tmp_str = 'select srcip,dstip,srcmac,dstmac,dstport,proto from auditstrategy where id=%d' % (id)
        result, rows = db_proxy.read_db(tmp_str)
        for row in rows:
            src_ip = row[0]
            dst_ip = row[1]
            src_mac = row[2]
            dst_mac = row[3]
            dst_port = row[4]
            proto = row[5]
        if start == 1:
            sql_str = "update auditstrategy set enabled=1 where id=%d"%(id)
            msg['Operate'] = "部署审计策略规则:srcip=%s,dstip=%s,scrmac=%s,dstmac=%s,dstport=%s,proto=%s" \
                            % (src_ip, dst_ip, src_mac, dst_mac, dst_port, ADUITSTRATEGY_PROTO[proto])
        else:
            sql_str = "update auditstrategy set enabled=0 where id=%d" % (id)
            msg['Operate'] = "关闭审计策略规则:srcip=%s,dstip=%s,scrmac=%s,dstmac=%s,dstport=%s,proto=%s" \
                             % (src_ip, dst_ip, src_mac, dst_mac, dst_port, ADUITSTRATEGY_PROTO[proto])
    else:
        if start == 1:
            sql_str = "update auditstrategy set enabled=1"
            msg['Operate'] = "部署全部审计策略规则"
        else:
            sql_str = "update auditstrategy set enabled=0"
            msg['Operate'] = "关闭全部审计策略规则"
    db_proxy.read_db(sql_str)
    deploy_audit_strategy()
    msg['UserName'] = loginuser
    msg['UserIP'] = user_ip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = msg['Operate'].decode("utf-8")
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


def deploy_audit_strategy():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = 'select srcip,dstip,srcmac,dstmac,dstport,proto from auditstrategy where enabled=1'
    result, rows = db_proxy.read_db(sql_str)
    with open(ADUITSTRATEGY_RULE_PATH, 'w') as f:
        for row in rows:
            tmp_str = "%s %s %s %s %s %s\n" % (row[0], row[1], row[2].replace(":", ""),
                                               row[3].replace(":", ""), row[4], ADUITSTRATEGY_PROTO[row[5]])
            f.write(tmp_str)
    commands.getstatusoutput("vtysh -c 'con t' -c 'dpi' -c 'dpi reload-rules traffic_capture'")
