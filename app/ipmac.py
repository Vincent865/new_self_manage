#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import struct
import MySQLdb
import math
import csv
import codecs
import os
import sys
import traceback
import ipaddress

from flask import Flask
from flask import request
from flask import jsonify
from flask import Blueprint
from flask import current_app
from global_function.cmdline_oper import *
from global_function.log_oper import *
# flask-login
from flask_login.utils import login_required
import ipaddress
from global_function.global_var import get_oper_ip_info
from flask import send_from_directory
from werkzeug import secure_filename



ipmac_page = Blueprint('ipmac_page', __name__, template_folder='templates')
ALLOWED_EXTENSIONS = set(['csv'])
UPLOAD_FOLDER = '/data/rules/'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@ipmac_page.route('/ipMacRes')
@login_required
def mw_ipmac_res():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    page = request.args.get('page', 0, type=int)
    dev_name = request.args.get('name', '')
    ip = request.args.get('ip', '')
    mac = request.args.get('mac', '')
    data = []
    total = 0
    option_str = ''
    if len(dev_name) > 0:
        option_str += ' and device_name like "%%%s%%"'%dev_name
    if len(ip) > 0:
        option_str += ' and ip like "%%%s%%"'%ip
    if len(mac) > 0:
        option_str += ' and mac like "%%%s%%"'%mac

    add_str = ' order by ipmac_id desc limit ' + str((page-1)*10)+',10;'
    sql_str = "select * from ipmaclist where ipmac_id>1"+ option_str + add_str
    result,rows = db_proxy.read_db(sql_str)
    for row in rows:
        row = list(row)
        if len(row[2]) > 16:
            row.append(6)
        else:
            row.append(4)
        data.append(row)
    sum_str = "SELECT count(*) from ipmaclist"
    result,rows = db_proxy.read_db(sum_str)
    for s in rows:
        total = s[0]
    return jsonify({'rows': data, 'total': total-1, 'page': page})


@ipmac_page.route('/getIpmacAction')
@login_required
def mw_ipmac_getaction():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select action from ipmaclist limit 0,1"
    result,rows = db_proxy.read_db(sql_str)
    action = 0
    for act in rows:
        action = act[0]
    return jsonify({'action': action})


@ipmac_page.route('/updateIpmacAction', methods=['GET', 'POST'])
@login_required
def mw_ipmac_update_action():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        cur_action = request.args.get("action")
    else:
        post_data = request.get_json()
        cur_action = post_data['action']
    sql_str = "update ipmaclist set action=%s where ipmac_id = 1" % cur_action
    db_proxy.write_db(sql_str)
    mw_ipmac_deploy()
    return jsonify({'status':1})


@ipmac_page.route('/updateIpMac', methods=['GET', 'POST'])
@login_required
def mw_ipmac_update():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        ip = request.args.get('ip')
        mac = request.args.get('mac')
        name = request.args.get('devname')
        ip = ip.encode('utf-8')
        mac = mac.encode('utf-8')
        name = name.encode('utf-8')
        id = request.args.get('id')
        loginuser = request.args.get('loginuser')
        enable = request.args.get('enable', 0, type=int)
    else:
        post_data = request.get_json()
        ip = post_data['ip'].encode('utf-8')
        mac = post_data['mac'].encode('utf-8')
        name = post_data['devname'].encode('utf-8')
        id = post_data['id']
        loginuser = post_data['loginuser']
        enable = int(post_data['enable'])
    # send log to mysql db
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u"修改IP/MAC规则 IP-" + ip + u" MAC-" + mac
    sta_str = "select status from whiteliststudy where id=1"
    result, rows = db_proxy.read_db(sta_str)
    tmp_status = rows[0][0]
    if tmp_status == 1:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 2, 'msg': u"白名单正在学习中,请稍后操作..."})

    tmp_str = "select ipmac_id from ipmaclist where ip='%s' and mac='%s'" % (ip, mac)
    result, rows = db_proxy.read_db(tmp_str)
    now_num = 0                                                                                                                      
    for n in rows:                                                                                                                
        now_num = n[0]                                                                                                           
    if now_num != int(id) and now_num != 0:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': -1})
    # sql_str = "UPDATE ipmaclist set ip="+"\""+ip+"\""+", mac="+"\""+mac+"\"" +", device_name="+"\""+name+"\""+",enabled="+str(enable)+" where ipmac_id="+id
    sql_str = "UPDATE ipmaclist set ip='%s',mac='%s',device_name='%s',enabled=%d " \
              "where ipmac_id=%d" % (ip, mac, name, enable, id)
    db_proxy.write_db(sql_str)
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@ipmac_page.route('/addIpMac',methods=['GET', 'POST', 'PUT'])
@login_required
def mw_ipmac_add():
    # send log to mysql db
    msg = {}
    userip = get_oper_ip_info(request)
    if request.method == 'POST':
        data = request.get_json()
        loginuser = data.get('loginuser','')
        ip = data.get('ip','').encode('utf-8')
        mac = data.get('mac','').encode('utf-8')
        name = data.get('name','').encode('utf-8')
        intf = data.get('intf','-1').encode('utf-8')
        ip_type = int(data.get('iptype'))
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'

        if ip_type ==4:
            # min_ip=socket.ntohl(struct.unpack("I",socket.inet_aton("224.0.0.0"))[0])
            # max_ip = socket.ntohl(struct.unpack("I", socket.inet_aton("239.255.255.255"))[0])
            # current_ip=socket.ntohl(struct.unpack("I", socket.inet_aton(ip))[0])
            #
            # if min_ip <=current_ip <= max_ip:
            #     return jsonify({'status': 0, 'msg': "请输入正确的IPV4地址"})
            try:
                ipv4_split1=int(ip.split('.')[0])
                if ipv4_split1 >=224:
                    return jsonify({'status': 0, 'msg': "请输入正确的IPV4地址"})

            except:
                return jsonify({'status': 0, 'msg': "请输入正确的IPV4地址"})

        name = name.replace('\'', '\'\'')
        db_proxy = DbProxy(CONFIG_DB_NAME)
        sta_str = "select status from whiteliststudy where id=1"
        result, rows = db_proxy.read_db(sta_str)
        tmp_status = rows[0][0]
        if tmp_status == 1:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 2, 'msg': u"白名单正在学习中,请稍后操作..."})
        total = 0
        sum_str = "SELECT count(*) from ipmaclist"
        res,rows = db_proxy.read_db(sum_str)
        for s in rows:
            total=s[0]
        num_limit = db_record_limit["device"] + 1
        if total>=num_limit:
            return jsonify({'status': 0})

        '''check ip address'''
        try:
            if ip_type == 4:
                ipaddress.IPv4Address(unicode(ip))
            elif ip_type == 6:
                ipaddress.IPv6Address(unicode(ip))
            else:
                return jsonify({'status': 0})
        except:
            ip_msg = None
            if ip_type == 4:
                ip_msg = u"请输入正确的IPV4地址"
            elif ip_type == 6:
                ip_msg = u"请输入正确的IPV6地址"

            msg['Operate'] = "添加IP/MAC规则:" + name + "," + ip + "," + mac
            msg['Operate'] = msg['Operate'].decode("utf-8")
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0, 'msg': ip_msg})

        if ip_type == 6:
            ip_net6 = ipaddress.ip_network(unicode(ip))
            ip = ip_net6.exploded.split('/')[0]

        # tmp_str = "select count(*) from ipmaclist where ip="+"\""+ip+"\""+" and mac="+"\""+mac+"\""
        tmp_str = "select count(*) from ipmaclist where ip="+"\""+ip+"\""
        #rows = send_read_cmd(TYPE_APP_SOCKET,tmp_str)

        result,rows = db_proxy.read_db(tmp_str)
        now_num = 0
        for n in rows:
            now_num = n[0]
        if now_num>0:
            msg['Operate'] = "添加IP/MAC规则:" + name + ","+ ip + "," + mac
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status':-1, 'msg': u'当前规则已存在'})

        sql_str = "insert into ipmaclist (enabled,ip,mac,device_name,is_study,interface) " \
                  "values (0,'%s','%s','%s',0,%s)" % (ip, mac, name, intf)
        #send_write_cmd(TYPE_APP_SOCKET,sql_str)
        result = db_proxy.write_db(sql_str)
         #topdevice is exist
        # tmp_str = "select count(*) from topdevice where ip='%s' and mac='%s'"%(ip,mac)
        # result,rows = db_proxy.read_db(tmp_str)
        # now_num = 0
        # for n in rows:
        #     now_num = n[0]
        # if now_num == 0:
        #     tmp_sql_str = "insert into topdevice (name,ip,mac,proto,dev_type,is_study,dev_interface) " \
        #                   "values ('%s','%s','%s',0,0,0,%s)" % (name, ip, mac, intf)
        #     result = db_proxy.write_db(tmp_sql_str)
        # else:
        #     top_sql_str = "update topdevice set name = '%s' where ip='%s' and mac='%s'" % (name, ip, mac)
        #     result = db_proxy.write_db(top_sql_str)
        # set_devname_by_ipmac(ip, mac, name)
        # time.sleep(3)
        #res = mw_ipmac_deploy()
        #if res == -1:
        #    return jsonify({'status':2})
        msg['Operate'] = "添加IP/MAC规则:" + name + ","+ ip + "," + mac
        msg['Operate'] = msg['Operate'].decode("utf-8")
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status':1})

    elif request.method == 'PUT':
        '''edit single ip/mac rules'''
        data = request.get_json()
        loginuser = data.get('loginuser','')
        id = data.get('id','').encode('utf-8')
        ip = data.get('ip','').encode('utf-8')
        mac = data.get('mac','').encode('utf-8')
        name = data.get('name','').encode('utf-8')
        intf = data.get('intf', '-1').encode('utf-8')
        ip_type = int(data.get('iptype'))
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'
        msg['Operate']=u"编辑IP/MAC规则:" + name + "," + ip + "," + mac
        msg['Operate']=msg['Operate'].decode("utf-8")
        name = name.replace('\'', '\'\'')
        db_proxy = DbProxy(CONFIG_DB_NAME)
        sta_str = "select status from whiteliststudy where id=1"
        result, rows = db_proxy.read_db(sta_str)
        tmp_status = rows[0][0]
        if tmp_status == 1:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 2, 'msg': u"白名单正在学习中,请稍后操作..."})

        '''check ip address'''
        try:
            if ip_type == 4:
                ipaddress.IPv4Address(unicode(ip))
            elif ip_type == 6:
                ipaddress.IPv6Address(unicode(ip))
            else:
                return jsonify({'status': 0})
        except:
            ip_msg = None
            if ip_type == 4:
                ip_msg = u"请输入正确的IPV4地址"
            elif ip_type == 6:
                ip_msg = u"请输入正确的IPV6地址"
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0, 'msg': ip_msg})

        if ip_type == 6:
            ip_net6 = ipaddress.ip_network(unicode(ip))
            ip = ip_net6.exploded.split('/')[0]

        sql_str = "select ip, mac, device_name, enabled from ipmaclist where ipmac_id=%d" % int(id)
        res, rows = db_proxy.read_db(sql_str)
        if res != 0:
            msg['Result']='1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({"status": 0})
        if rows[0][0] == ip and rows[0][1] == mac and rows[0][2] == name:
            return jsonify({"status": 1})

        tmp_str = "select count(*) from ipmaclist where ip='%s' and ipmac_id != %d" % (ip, int(id))
        current_app.logger.info(tmp_str)
        result, num_rows = db_proxy.read_db(tmp_str)
        now_num = 0
        for n in num_rows:
            now_num = n[0]
        if now_num>0:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            msg = u"当前ip已存在"
            return jsonify({'status': -1, 'msg': msg})

        update_str = "update ipmaclist set ip='%s',mac='%s',device_name='%s' where ipmac_id=%d" % (ip, mac, name, int(id))
        res = db_proxy.write_db(update_str)
        if res != 0:
            msg['Result']='1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({"status": 0, "msg": u"编辑失败"})
        if int(rows[0][3]) != 0:
            res=mw_ipmac_deploy()
            if res == -1:
                msg['Result']='1'
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({'status': 0, 'msg': u'编辑失败'})
        msg['Result']='0'
        send_log_db(MODULE_OPERATION, msg)

        # tmp_str = "select count(*) from topdevice where ip='%s' and mac='%s'"%(ip,mac)
        # result,rows = db_proxy.read_db(tmp_str)
        # now_num = 0
        # for n in rows:
        #     now_num = n[0]
        # if now_num == 0:
        #     tmp_sql_str = "insert into topdevice (name,ip,mac,proto,dev_type,is_study,dev_interface) " \
        #                   "values ('%s','%s','%s',0,0,0,%s)" % (name, ip, mac, intf)
        #     result = db_proxy.write_db(tmp_sql_str)
        # else:
        #     top_sql_str = "update topdevice set name = '%s' where ip='%s' and mac='%s'"%(name,ip,mac)
        #     result = db_proxy.write_db(top_sql_str)
        # set_devname_by_ipmac(ip, mac, name)
        # time.sleep(3)
        return jsonify({'status': 1})


def mw_ipmac_deploy():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select ip,mac from ipmaclist where enabled=1 and ipmac_id!=1"
    result,rows = db_proxy.read_db(sql_str)
    try:
        file_oper = open(IPMAC_LIST_PATH, "w")
        #action_str = "select action from ipmaclist where ipmac_id=1"
        # make sure action status has been commited
        # time.sleep(3)
        #result, values = db_proxy.read_db(action_str)
        #current_app.logger.info(values)
        #current_app.logger.info(result)

        #action_str = 'alert'
        #if values[0][0] == 2:
        #    action_str = 'drop'
        for row in rows:
            res_str = ""
            if len(row[0]) <= 0:
                continue
            res_str += row[0]
            res_str += " "
            res_str += row[1].replace(":", "")
            res_str += " "
            #res_str += action_str
            res_str += "alert alert\n"
            file_oper.write(res_str)
        file_oper.close()
    except:
        current_app.logger.exception("Exception Logged")
        current_app.logger.error("mw_ipmac_deploy %s file write error", IPMAC_LIST_PATH)
        return -1
    # switch_ipmac_extraip(1)
    status = reload_ipmac_rules()
    return 0


@ipmac_page.route('/clearAllIpMac', methods=['GET', 'POST'])
@login_required
def mw_ipmac_clearall():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sta_str = "select status from whiteliststudy where id=1"
    result, rows = db_proxy.read_db(sta_str)
    tmp_status = rows[0][0]
    if tmp_status == 1:
        return jsonify({'status': 2, 'msg': u"白名单正在学习中,请稍后操作..."})
    sql_str = "update ipmaclist set enabled=0 where ipmac_id>1"
    db_proxy.write_db(sql_str)
    try:
        file_oper = open(IPMAC_LIST_PATH, "w")
        file_oper.close()
    except:
        current_app.logger.error("mw_ipmac_clearall %s file clear error", IPMAC_LIST_PATH)
    # switch_ipmac_extraip(0)
    status = reload_ipmac_rules()
    # send log to mysql db
    msg = {}
    userip = get_oper_ip_info(request)
    if request.method == 'GET':
        loginuser = request.args.get('loginuser')
    else:
        post_data = request.get_json()
        loginuser = post_data['loginuser']
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u"清空已部署IP/MAC规则"
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})




@ipmac_page.route('/startAllIpMac', methods=['GET', 'POST'])
@login_required
def mw_ipmac_startall():
    # send log to mysql db
    msg = {}
    userip = get_oper_ip_info(request)
    if request.method == 'GET':
        loginuser = request.args.get('loginuser')
    else:
        post_data = request.get_json()
        loginuser = post_data['loginuser']
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u"启用所有IP/MAC规则"
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sta_str = "select status from whiteliststudy where id=1"
    result, rows = db_proxy.read_db(sta_str)
    tmp_status = rows[0][0]
    if tmp_status == 1:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 2, 'msg': u"白名单正在学习中,请稍后操作..."})
    sql_str = "update ipmaclist set enabled=1 where ipmac_id>1"
    db_proxy.write_db(sql_str)
    time.sleep(3)
    res = mw_ipmac_deploy()
    if res == -1:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 0})
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@ipmac_page.route('/deleteIpMac', methods=['POST'])
@login_required
def mw_ipmac_delete():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == "POST":
        # send log to mysql db
        msg = {}
        userip = get_oper_ip_info(request)
        post_data = request.get_json()
        loginuser = post_data['loginuser']
        id = post_data['id']
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'
        sta_str = "select status from whiteliststudy where id=1"
        result, rows = db_proxy.read_db(sta_str)
        tmp_status = rows[0][0]
        if tmp_status == 1:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 2, 'msg': u"白名单正在学习中,请稍后操作..."})
        if id == 'all':
            msg['Operate'] = u"删除全部IP/MAC规则"
            sql_str = "DELETE FROM ipmaclist where ipmac_id!=1"
        else:
            top_str = "select ip,mac from ipmaclist where ipmac_id=%s"%(id)
            res, rows_top = db_proxy.read_db(top_str)
            ip = rows_top[0][0]
            mac = rows_top[0][1]
            msg['Operate'] = u"删除单条IP/MAC规则 IP-" + ip + u" MAC-" + mac
            sql_str = "delete from ipmaclist where ipmac_id="
            sql_str += id
        # send_write_cmd(TYPE_APP_SOCKET,sql_str)
        result = db_proxy.write_db(sql_str)
        res = mw_ipmac_deploy()
        if res == -1:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0})
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 1})
    else:
        current_app.logger.info("method not allowed.")
        return jsonify({'status': 0})


@ipmac_page.route('/startIpMacOne', methods=['GET', 'POST'])
@login_required
def mw_ipmac_startone():
    # send log to mysql db
    msg = {}
    userip = get_oper_ip_info(request)
    if request.method == 'GET':
        loginuser = request.args.get('loginuser')
        id = request.args.get('id')
        state = request.args.get('status', 0, type=int)
    else:
        post_data = request.get_json()
        loginuser = post_data['loginuser']
        state = int(post_data['status'])
        id = post_data['id']
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sta_str = "select status from whiteliststudy where id=1"
    result, rows = db_proxy.read_db(sta_str)
    tmp_status = rows[0][0]
    if tmp_status == 1:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 2, 'msg': u"白名单正在学习中,请稍后操作..."})
    sql_str = "select ip,mac from ipmaclist where ipmac_id=%s" % id
    result, rows = db_proxy.read_db(sql_str)
    ip = rows[0][0]
    mac = rows[0][1]
    if state == 1:
        sql_str = "update ipmaclist set enabled=1 where ipmac_id="
        sql_str += id
        db_proxy.write_db(sql_str)
        res = mw_ipmac_deploy()
        msg['Operate'] = u"启用单条IP/MAC规则 IP-" + ip + u" MAC-" + mac
    else:
        sql_str = "update ipmaclist set enabled=0 where ipmac_id="
        sql_str += id
        db_proxy.write_db(sql_str)
        res = mw_ipmac_deploy()
        msg['Operate'] = u"禁用单条IP/MAC规则 IP-" + ip + u" MAC-" + mac
    if res == -1:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 0})
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})



@ipmac_page.route('/ipmacImport',methods=['GET','POST'])
@login_required
def ipmac_Import():
    if request.method == 'POST':
        loginuser = request.form.get('loginuser')
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserIP'] = userip
        msg['UserName'] = loginuser
        msg['ManageStyle'] = 'WEB'
        db_proxy = DbProxy(CONFIG_DB_NAME)
        sta_str = "select status from whiteliststudy where id=1"  #判断是否在学习，如果在学习，返回错误码并记录日志
        result, rows = db_proxy.read_db(sta_str)
        tmp_status = rows[0][0]
        if tmp_status == 1:
            msg['Operate'] = u"导入ipmaclist"
            msg['Result'] = '1' 
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 2, 'msg': u"白名单正在学习中,请稍后操作..."}) 
        else:  
            try:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(UPLOAD_FOLDER, filename)) #设置文件路径
                    FileName = '%s%s'%(UPLOAD_FOLDER, filename)
                    csvfile = open(FileName,'rb')
                    reader = csv.reader(csvfile,dialect='excel')#将CSV文件的内容存到rows当中
                    rows = [row for row in reader]
                    if rows[0] != ['\xef\xbb\xbfip', 'mac', 'enabled']:#判断表头格式是否正确
                        msg['Operate'] = u"导入ipmaclist"
                        msg['Result'] = '1' 
                        send_log_db(MODULE_OPERATION, msg)
                        os.system("rm '%s'"%(FileName))
                        return jsonify({'status': 2, 'msg': u"导入文件格式错误"}) 
                    else:
                        for data in rows[1:]:
                            ip, mac, enabled = data
                            try: #判断ip是否合法，如果合法再判断ip类型
                                addr = ipaddress.ip_address(unicode(ip))
                                ip_type = addr.version
                                if ip_type == 6: #如果ip类型为ipv6，扩展
                                    ip_net6 = ipaddress.ip_network(unicode(ip))
                                    ip = ip_net6.exploded.split('/')[0]
                                tmp_str = "select ip,mac,enabled from ipmaclist where ip='%s'" % (ip) #查询ip，mac和enabled的值如果不存在直接导入
                                #如果存在，如果mac,enabled值相同，跳过   如果mac,enabled值不同，update
                                result,rows = db_proxy.read_db(tmp_str)                   
                                #判断是否存在
                                if len(rows) > 0:
                                    for row in rows:
                                        ip,mac1,enabled1 = row
                                        if enabled == enabled1 and mac == mac1:#ip和mac都相同则跳过
                                            pass
                                        else: #有不同则update
                                            up_sql="update ipmaclist set mac='%s',enabled='%s' where ip='%s'"%(mac,enabled,ip)
                                            result = db_proxy.write_db(up_sql)
                                else:#如果不存在则直接导入
                                    insert_sql="insert into ipmaclist(ip,mac,enabled)values('%s','%s','%s')"%(ip,mac,enabled)
                                    result = db_proxy.write_db(insert_sql)
                            except:#如果不合法，记录错误日志并跳过这一条继续
                                current_app.logger.error(traceback.format_exc())
                                continue
                        os.system("rm '%s'"%(FileName))
                        msg['Operate'] = u"导入ipmaclist"
                        msg['Result'] = '0'
                        send_log_db(MODULE_OPERATION, msg)
                        status = 1
                        mw_ipmac_deploy()
                        return jsonify({'status': status})
            except:
                current_app.logger.error(traceback.format_exc())
                msg['Operate'] = u"导入ipmaclist"
                msg['Result'] = '1'
                send_log_db(MODULE_OPERATION, msg)
                os.system("rm '%s'"%(FileName))
                status = 0
                return jsonify({'status': status})


@ipmac_page.route('/ipmacExport', methods=['GET','POST'])
@login_required
def ipmac_Export():
    if request.method == 'GET':
        loginuser = request.args.get('loginuser')
        action = request.args.get('action', type=int)
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserIP'] = userip
        msg['UserName'] = loginuser
        msg['ManageStyle'] = 'WEB'
        db_proxy = DbProxy(CONFIG_DB_NAME)
        if action == 0:
            #判断是否学习， 如果在学习，返回错误码，并且记录下载失败日志
            sta_str = "select status from whiteliststudy where id=1"
            result, rows = db_proxy.read_db(sta_str)
            tmp_status = rows[0][0]
            if tmp_status == 1:
                msg['Operate'] = u"导出ipmaclist"
                msg['Result'] = '1' 
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({'status': 2, 'msg': u"白名单正在学习中,请稍后操作..."})   
            else:
                status = 1
                return jsonify({'status':status})
        else:
                # 正常下载
            try:
                csvfile = open('/data/rules/ipmaclist.csv','wb')
                csvfile.write(codecs.BOM_UTF8)
                writer = csv.writer(csvfile,dialect='excel')
                writer.writerow(['ip','mac','enabled'])#写入头文件名
                sql="select ip,mac,enabled from ipmaclist where ipmac_id!=1"
                current_app.logger.info(sql)
                result, rows = db_proxy.read_db(sql)
                writer.writerows(rows)
                csvfile.close()
                #下载文件并记录日志
                msg['Operate'] = u"导出ipmaclist"
                msg['Result'] = '0'
                send_log_db(MODULE_OPERATION, msg)
                return send_from_directory("/data/rules/", "ipmaclist.csv", as_attachment=True)
            except:
                current_app.logger.error(traceback.format_exc())
                msg['Operate'] = u"导出ipmaclist"
                msg['Result'] = '1'
                send_log_db(MODULE_OPERATION, msg)
                status = 0
                return jsonify({'status': status})   
