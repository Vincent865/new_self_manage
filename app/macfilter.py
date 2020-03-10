#!/usr/bin/python
# -*- coding:UTF-8 -*-
from flask import request
from flask import jsonify
from flask import Blueprint
from flask import current_app
from global_function.cmdline_oper import *
from global_function.log_oper import *
# flask-login
from flask_login.utils import login_required


macfilter_page = Blueprint('macfilter_page', __name__, template_folder='templates')
# todo：添加操作日志


@macfilter_page.route('/macfilter', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def mac_filter():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method != 'GET':
        sta_str = "select status from whiteliststudy where id=1"
        result, rows = db_proxy.read_db(sta_str)
        tmp_status = rows[0][0]
        if tmp_status == 1:
            return jsonify({'status': 2, 'msg': u"白名单正在学习中,请稍后操作..."})
    if request.method == 'GET':
        data = []
        total = 0
        page = request.args.get('page', 0, type=int)
        mac = request.args.get('mac', '')
        add_str = ' limit ' + str((page - 1) * 10) + ',10;'
        search_str = "where mac like '%%%s%%' " % mac
        sql_str = 'select id,mac,enable from mac_filter '
        if mac:
            sql_str += search_str
        sql_str += add_str
        res, rows = db_proxy.read_db(sql_str)
        for row in rows:
            data.append(row)
        sum_str = "SELECT count(*) from mac_filter"
        result, rows = db_proxy.read_db(sum_str)
        for s in rows:
            total = s[0]
        return jsonify({'rows': data, 'total': total, 'page': page})
    elif request.method == 'POST':
        status = 0
        post_data = request.get_json()
        mac = post_data['mac'].encode('utf8')
        loginuser = post_data['loginuser']
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'
        msg['Operate'] = u"新增MAC%s过滤规则" % mac
        if mac == "00:00:00:00:00:00" or check_mac_valid(mac) is False:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': status, 'msg': 'mac地址格式错误'})
        num_str = "select count(*) from mac_filter where mac='%s'" % mac
        res, rows = db_proxy.read_db(num_str)
        mac_num = rows[0][0]
        if mac_num:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': status, 'msg': 'mac地址已经存在'})
        if (int(mac[0:2],16) & int('0x01', 16)) == int('0x01', 16):
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': status, 'msg': '不能添加多播MAC地址'})
        sql_str = "insert into mac_filter(mac,enable) VALUES('%s',0)" % mac
        res = db_proxy.write_db(sql_str)
        if res:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': status, 'msg': '插入失败'})
        status = 1
        # send log to mysql db
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': status, 'msg': '插入成功'})
    elif request.method == 'PUT':
        status = 0
        post_data = request.get_json()
        gid = post_data['id']
        enable = post_data['enable']
        loginuser = post_data['loginuser']
        top_str = "select mac from mac_filter where id=%s" % (gid)
        res, rows_top = db_proxy.read_db(top_str)
        if res:
            return jsonify({'status': status, 'msg': '删除失败'})
        mac = rows_top[0][0]
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'
        if enable == 1:
            msg['Operate'] = u"启用单条MAC地址过滤规则 MAC-%s" % mac
        else:
            msg['Operate'] = u"禁用单条MAC地址过滤规则 MAC-%s" % mac
        sql_str = 'update mac_filter set enable=%d where id=%d' % (enable, gid)
        res = db_proxy.write_db(sql_str)
        if res:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': status, 'msg': '修改失败'})
        reload_macfilter_rules(db_proxy)
        status = 1
        # send log to mysql db
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': status, 'msg': '修改成功'})
    else:
        status = 0
        post_data = request.get_json()
        ids = post_data['ids']
        loginuser = post_data['loginuser']
        top_str = "select mac from mac_filter where id=%s" % (ids)
        res, rows_top = db_proxy.read_db(top_str)
        if res:
            return jsonify({'status': status, 'msg': '删除失败'})

        mac = rows_top[0][0]
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'
        msg['Operate'] = u"删除单条MAC地址过滤规则 MAC-%s" % mac
        ''''''
        sql_str = "delete from mac_filter where id in (%s)" % ids
        res = db_proxy.write_db(sql_str)
        if res:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': status, 'msg': '删除失败'})
        reload_macfilter_rules(db_proxy)
        status = 1
        # send log to mysql db
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': status, 'msg': '删除成功'})


@macfilter_page.route('/macfilterall', methods=['PUT'])
@login_required
def mac_filter_all():
    status = 0
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sta_str = "select status from whiteliststudy where id=1"
    result, rows = db_proxy.read_db(sta_str)
    tmp_status = rows[0][0]
    if tmp_status == 1:
        return jsonify({'status': 2, 'msg': u"白名单正在学习中,请稍后操作..."})
    post_data = request.get_json()
    action = post_data['action']
    loginuser = post_data['loginuser']
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    if action == 1:
        msg['Operate'] = u"启用全部MAC过滤规则"
    else:
        msg['Operate'] = u"禁用全部MAC过滤规则"
    #  1 启用所有规则 0 禁用所有
    sql_str = 'update mac_filter set enable=%d' % action
    res = db_proxy.write_db(sql_str)
    if res:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': status, 'msg': '操作失败'})
    reload_macfilter_rules(db_proxy)
    status = 1
    # send log to mysql db
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': status, 'msg': '操作成功'})
