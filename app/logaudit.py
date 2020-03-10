#!/usr/bin/python
# -*- coding:UTF-8 -*-

import socket
import struct
from flask import request
from flask import jsonify
import base64
from flask import Blueprint
from flask import current_app
from global_function.cmdline_oper import *
from global_function.log_oper import *
# flask-login
from flask_login.utils import login_required
from deviceinfo import *
import ipaddress


logaudit_page = Blueprint('log_audit', __name__, template_folder='templates')
@logaudit_page.route('/SetLogAudit', methods=['GET', 'POST'])
@login_required
def SetLogAudit():
    if g_hw_type == "1":
        eth_num = 5
    else:
        eth_num = 3
    if request.method == 'GET':
        db_proxy = DbProxy(CONFIG_DB_NAME)
        ip_cmd = "ifconfig eth%d | grep \"inet addr\" | awk '{print $2}' | awk -F ':' '{print $2}'"%eth_num
        mask_cmd = "ifconfig eth%d | grep \"inet addr\" | awk '{print $4}' | awk -F ':' '{print $2}'"%eth_num
        ip = commands.getoutput(ip_cmd)
        mask = commands.getoutput(mask_cmd)
        sta_str = "select serverdev_dcport,protectdev_dcport from comm_param where id=1"
        result, rows = db_proxy.read_db(sta_str)
        row = list(rows[0])
        Info = {'status': 1, 'ip': ip, 'mask': mask,'serverdev_dcport': row[0],'protectdev_dcport': rows[0][1]}
        return jsonify(Info)
    else:
        db_proxy = DbProxy(CONFIG_DB_NAME)
        post_data = request.get_json()
        newip = post_data['ip']
        newmask = post_data['mask']
        serverdev_dcport = post_data['serverdev_dcport']
        protectdev_dcport = post_data['protectdev_dcport']
        loginuser = post_data['loginuser']

        if newmask != '' and newmask.find('.') == -1:
            newmask = exchange_maskint(int(newmask))
        if newip != '' is not  None:
            try:
                if not is_ipv4(newip):
                    return jsonify({'status': 0, 'msg': 'ipv4格式错误'})
            except Exception:
                return jsonify({'status': 0, 'msg': 'ipv4格式错误'})
        sta_str = "update comm_param set serverdev_dcport=%d,protectdev_dcport=%d where id=1" % (serverdev_dcport,protectdev_dcport)
        db_proxy.write_db(sta_str)
        LogAuditApply(newip, newmask, eth_num)
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['Operate'] = "设置日志审计接口IP:".decode("utf8") + newip + ",子网掩码:".decode("utf8") + newmask + "服务器采集端口" + str(serverdev_dcport) + "安全设备采集端口" + str(protectdev_dcport)
        msg['ManageStyle'] = 'WEB'
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 1})

def LogAuditApply(ip, netmask, intf):
    if ip  == '':
        cmd = "ifconfig eth%d | grep \"inet addr\" | awk '{print $2}' | awk -F ':' '{print $2}'"%intf
        oldip = commands.getoutput(cmd)
        cmd_str = "ip addr del {} dev eth{}".format(oldip, intf)
        commands.getoutput(cmd_str)
    else:
        cmd_str = "ifconfig eth%d %s netmask %s" % (intf, ip, netmask)
        commands.getoutput(cmd_str)
    update_logip_file(ip, netmask, intf)
    cmd_str = "killall -9 datacollector"
    commands.getoutput(cmd_str)



def exchange_maskint(mask_int):
    bin_arr = ['0' for i in range(32)]
    for i in range(mask_int):
        bin_arr[i] = '1'
    tmpmask = [''.join(bin_arr[i * 8:i * 8 + 8]) for i in range(4)]
    tmpmask = [str(int(tmpstr, 2)) for tmpstr in tmpmask]
    return '.'.join(tmpmask)

@logaudit_page.route('/LogAuditSearch', methods=['GET'])
@login_required
def mw_logaudit_search():
    db_proxy = DbProxy()
    page = request.args.get('page', 0, type=int)
    start_time = request.args.get('starttime',type=int)
    end_time = request.args.get('endtime',type=int)
    level = request.args.get('level', '')
    devtype = request.args.get('devtype', '')
    data = []
    total = 0
    option_str = ''
    if start_time > 0:
        option_str += " and timestamp>%d" % start_time
    if end_time > 0:
        option_str += " and timestamp<%d" % end_time
    if len(level):
        option_str += ' and level in (%s)'% level
    if len(devtype) > 0:
        option_str += ' and devtype in (%s)'% devtype

    add_str = ' order by timestamp desc limit ' + str((page-1)*10)+',10;'
    sql_str = "select level,timestamp,hostname,ip,devtype,detailinfo from da_31992_data_acquire where id>0"+ option_str + add_str
    result,rows = db_proxy.read_db(sql_str)
    for row in rows:
        row = list(row)
        row[3] = socket.inet_ntoa(struct.pack("!I",row[3]))
        row[5] = base64.b64encode(row[5])
        data.append(row)
    sum_str = "SELECT count(*) from da_31992_data_acquire where 1=1"
    sum_str += option_str
    result,rows = db_proxy.read_db(sum_str)
    for s in rows:
        total = s[0]
    current_app.logger.error(type(data))
    return jsonify({'rows': data, 'total': total, 'page': page})


def update_logip_file(ip, netmask, intf):
    """
    修改网卡文件
    :param ip:
    :param netmask:
    :return:
    """
    try:
        interfaces_file_path = r'/app/etc/network/interfaces'
        file_handler = open(interfaces_file_path, "r")
        network_content = file_handler.read()
        file_handler.close()

        content_split = network_content.split('\n')

        # 三个属性要有都有，要没有都没有
        part_str = "iface eth{} inet static".format(intf)
        if network_content.find(part_str) == -1:
            network_content += "\niface eth%d inet static\neth3_ip %s\neth3_mask %s\n" % (intf, ip, netmask)
        else:
            flag = False
            for i, content in enumerate(content_split):
                part_str1 = 'iface eth{} inet static'.format(intf)
                if content.find(part_str1) != -1:
                    flag = True
                if flag:
                    if content.find("eth3_ip") != -1:
                        content_split[i] = "eth3_ip %s" % (ip)
                    if content.find("eth3_mask") != -1:
                        content_split[i] = "eth3_mask %s" % (netmask)

            network_content = '\n'.join(content_split)
        with open(interfaces_file_path, "w") as f:
            f.write(network_content)
    except:
        current_app.logger.error(traceback.format_exc())