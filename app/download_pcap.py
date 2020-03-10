#!/usr/bin/python
# -*- coding:UTF-8 -*-
import os
import time

from flask import Blueprint, jsonify, request, Response
from global_function.get_tcpdump_result import pcap_cur_status
from global_function.global_var import DbProxy, CONFIG_DB_NAME, logger, get_oper_ip_info
from flask_login.utils import login_required

from global_function.log_oper import send_log_db, MODULE_OPERATION

start_pcap_page = Blueprint('start_pcap_page', __name__, template_folder='templates')


@start_pcap_page.route('/search_status_pcap')
@login_required
def search_status_pcap():
    status = 0
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_search = "SELECT * from pcap_down_status;"
    result, rows = db_proxy.read_db(sql_search)
    flag = rows[0][1]
    pcap_name = rows[0][2]
    pcap_orig_size = rows[0][3]
    pcap_orig_time = rows[0][4]
    pcap_cur_size = rows[0][5]
    pcap_cur_time = rows[0][6]

    if flag == 1:
        status = 1
        data = {
            'status': status,
            'pcap_name': pcap_name,
            'pcap_orig_size': pcap_orig_size,
            'pcap_orig_time': pcap_orig_time,
            'pcap_cur_size': pcap_cur_size,
            'pcap_cur_time': pcap_cur_time
        }
        return jsonify(data)
    else:
        return jsonify({'status': status})


@start_pcap_page.route('/start_pcap', methods=['POST'])
@login_required
def start_pcap():
    if request.method == 'POST':
        result = request.get_json()
        pcap_name = result['pcap_name']
        pcap_orig_size = result['pcap_orig_size']
        pcap_orig_time = result['pcap_orig_time']

    # 记录日志
    msg = {}
    userip = get_oper_ip_info(request)
    data = request.get_json()
    loginuser = data.get('loginuser', '')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u'开始在线抓包'

    # 判断文件名是否重复
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select pcap_name from pcap_down_data"
    sql_count = "select count(*) from pcap_down_data "
    res, name_result = db_proxy.read_db(sql_str)
    pcap_name = pcap_name + '.pcap'
    for name in name_result:
        if pcap_name == name[0]:
            return jsonify({'status': 0, 'msg': '文件名重复'})
        else:
            continue

    # 判断数据库数据是否超过10条
    res, count_rows = db_proxy.read_db(sql_count)
    total = count_rows[0][0]
    if int(total) >= 10:
        return jsonify({'status': 0, 'msg': '文件总数超过10条'})
    else:
        pcap_start_time = int(time.time())
        sql_str = "update pcap_down_status set flag=1,pcap_name='%s',pcap_orig_size='%s',pcap_orig_time='%s',pcap_start_time='%s';" % (
            pcap_name, pcap_orig_size, pcap_orig_time, pcap_start_time)
        res = db_proxy.write_db(sql_str)
        if res == 0:
            msg['Result'] = '0'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 1, 'msg': '开始抓包成功'})
        else:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0, 'msg': '开始抓包失败'})


@start_pcap_page.route('/stop_pcap')
@login_required
def stop_pcap():
    # 记录日志
    msg = {}
    userip = get_oper_ip_info(request)
    loginuser = request.args.get('loginuser')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u'停止在线抓包'

    status = 0
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select * from pcap_down_status"
    _, result = db_proxy.read_db(sql_str)
    pcap_name = result[0][2]
    start_pcap_time = int(result[0][7])
    pcap_cur_size = pcap_cur_status(pcap_name)
    pcap_path = '/data/tcpdumpdata/' + pcap_name
    os.system('kill -9 $(pidof tcpdump)')
    finish_time = int(time.time())
    # 抓包运行时间
    pcap_cur_time = finish_time - start_pcap_time

    sql_str = "insert into pcap_down_data(finish_time,pcap_cur_size,pcap_cur_time,pcap_name,pcap_path) values ('%s','%s','%s', '%s','%s')" % (
        finish_time, pcap_cur_size, pcap_cur_time, pcap_name, pcap_path)
    db_proxy.write_db(sql_str)

    sql_update = "update pcap_down_status set flag=0,pcap_name='',pcap_cur_time=0,pcap_cur_size=0,pcap_orig_size=0,pcap_orig_time=0,pcap_start_time=0"
    res = db_proxy.write_db(sql_update)
    if res == 0:
        status = 1
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': status, 'msg': '停止抓包成功'})
    else:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': status, 'msg': '停止抓包失败'})


@start_pcap_page.route('/detail_pcap')
@login_required
def detail_pcap():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "SELECT * from pcap_down_data order by finish_time desc"
    sql_count = "select count(*) from pcap_down_data "
    result, rows = db_proxy.read_db(sql_str)
    rows = list(rows)
    pcap_detail = list()
    for i in rows:
        detail = {}
        detail["id"] = i[0]
        detail["pcap_name"] = i[2]
        detail["pcap_cur_size"] = i[3]
        detail["pcap_cur_time"] = i[4]
        pcap_detail.append(detail)

    res, count_rows = db_proxy.read_db(sql_count)
    total = count_rows[0][0]
    return jsonify({'rows': pcap_detail, 'total': total})


@start_pcap_page.route('/download_pcap')
@login_required
def download_pcap():
    pcap_name = request.args.get('pcap_name')
    pcap_name = '/data/tcpdumpdata/' + pcap_name
    fullfilenamelist = pcap_name.split('/')
    filename = fullfilenamelist[-1]

    def send_file():
        with open(pcap_name, 'rb') as targetfile:
            while 1:
                data = targetfile.read(1024 * 1024)
                if not data:
                    break
                yield data

    response = Response(send_file(), content_type='application/octet-stream')
    response.headers["Content-disposition"] = 'attachment; filename=%s' % filename
    return response


@start_pcap_page.route('/delete_pcap', methods=['DELETE'])
@login_required
def delete_pcap():
    # 记录日志
    msg = {}
    userip = get_oper_ip_info(request)
    data = request.get_json()
    loginuser = data.get('loginuser', '')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u'删除数据包'

    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'DELETE':
        result = request.get_json()
        ids = result.get('id', '')
        id_list = ids.split(",")

    for i in id_list:
        sql_name_str = "select pcap_name from pcap_down_data where id ='%s'" % i
        name_res, name_rows = db_proxy.read_db(sql_name_str)
        if name_res == 0:
            for name in name_rows:
                addr = '/data/tcpdumpdata/' + name[0]
                if os.path.exists(addr):
                    os.remove(addr)
                else:
                    logger.error("%s file not exist" % addr)

        sql_str = "delete from pcap_down_data where id='%s'" % i
        res = db_proxy.write_db(sql_str)
        if res != 0:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0, 'msg': '删除失败'})
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1, 'msg': '删除成功'})
