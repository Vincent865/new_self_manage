#!/usr/bin/python
# -*- coding: UTF-8 -*-
import fcntl
import ftplib
import commands
from datetime import time
import threading
import psutil
import socket
import ipaddress
import os
import MySQLdb
from flask import request
from flask import Response
from flask import jsonify
from flask import send_from_directory
from flask import Blueprint
from flask import session
from flask import make_response
from flask import current_app
from werkzeug.utils import secure_filename
from werkzeug.exceptions import *
from shelljob import proc
from global_function.upgrade_image import *
from global_function.log_oper import *
# flask-login
from flask_login.utils import login_required
from subprocess import Popen, PIPE
from collections import OrderedDict
from global_function.global_var import get_webdpi_obj
from global_function.global_var import DbProxy, CONFIG_DB_NAME, UPLOAD_FOLDER, get_oper_ip_info

deviceinfo_page = Blueprint('deviceinfo_page', __name__, template_folder='templates')
webDpi = get_webdpi_obj()

UPDATE_ALLOWED_EXTENSIONS = set(['tgz', 'bin'])
g_dpiip, g_pro_info, g_ver_info, g_sn_info, g_mw_ip = webDpi.getdpiinfo()
CONF_UPDATE_ALLOWED_EXTENSIONS = set(['sql'])

def update_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in UPDATE_ALLOWED_EXTENSIONS

def conf_update_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in CONF_UPDATE_ALLOWED_EXTENSIONS


@deviceinfo_page.route('/getUserName')
@login_required
def mw_getUserName():
    return jsonify({'username': session['username']})


def get_center_mode():
    db = DbProxy()
    cmd_str = "select center_mode from audit_center_mode"
    _, res = db.read_db(cmd_str)
    return res[0][0]

@deviceinfo_page.route('/getDeviceInfo')
@login_required
def mw_get_deviceinfo():
    run_time = int(time.time()) - int(psutil.boot_time())
    res = commands.getoutput('ifconfig agl0')
    start_res = res.find('inet addr:')
    stop_res = res.find('Bcast')
    start = start_res + 10
    stop = stop_res - 2
    dpiip = res[start:stop]
    # addr_type = ""
    # if res.find('Scope:Site') != -1:
    #     addr_type = "Scope:Site"
    # elif res.find('Scope:Global') != -1:
    #     addr_type = "Scope:Global"
    # else:
    #     pass
    #
    # if addr_type == "":
    #     ip6 = ""
    # else:
    #     stop_ip6_link = res.find('Scope:Link') - 4
    #     stop_ip6 = res.find(addr_type) - 4
    #     if stop_ip6_link > stop_ip6:
    #         start_ip6 = res.find('inet6 addr:') + 11
    #     else:
    #         start_ip6 = res.find('inet6 addr:',stop_ip6_link) + 11
    #     ip6 = res[start_ip6:stop_ip6]
    ip6, prefix=getip6_prefix_from_interfaces()
    run_mode = get_center_mode() # 0-审计分中心 1-审计中心
    dpiInfo = {'ip': dpiip, 'product': g_pro_info, 'version': g_ver_info, 'SN': g_sn_info, 'mwIp': g_mw_ip,
               'runtime': run_time, 'ip6': ip6, 'runmode': run_mode}
    return jsonify(dpiInfo=dpiInfo)


@deviceinfo_page.route('/getdbcleanconfig')
@login_required
def mw_get_db_clean_config():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    # rows = new_send_cmd(TYPE_APP_SOCKET, "select volumenthreshold, dataperiod from dbcleanconfig where id=1", 1)
    _, rows = db_proxy.read_db("select volumenthreshold, dataperiod from dbcleanconfig where id=1")
    threshold = rows[0][0]
    period = rows[0][1]
    return jsonify({'volumenthreshold': threshold, 'dataperiod': period})


@deviceinfo_page.route('/setdbcleanconfig', methods=['GET', 'POST'])
@login_required
def mw_set_db_clean_config():
    if request.method == 'GET':
        threshold = request.args.get('volumenthreshold', 80, type=int)
        period = request.args.get('dataperiod', 90, type=int)
        loginuser = request.args.get('loginuser')
    else:
        post_data = request.get_json()
        threshold = post_data['volumenthreshold']
        period = post_data['dataperiod']
        loginuser = post_data['loginuser']
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_cmd = "UPDATE dbcleanconfig set volumenthreshold=%d,dataperiod=%d where id=1" % (threshold, period)
    # new_send_cmd(TYPE_APP_SOCKET, sql_cmd, 2)
    db_proxy.write_db(sql_cmd)
    conf_save_flag_set()
    # send operation log
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    if str(period) == '0':
        msg['Operate'] = "设置自动删除策略,存储管理配置:".decode("utf8") + str(threshold) + \
                         "%,定期删除信息周期:永久".decode("utf8")
    else:
        msg['Operate'] = "设置自动删除策略,存储管理配置:".decode("utf8") + str(threshold) + \
                         "%,定期删除信息周期:".decode("utf8") + str(period) + "天".decode("utf8")
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@deviceinfo_page.route('/isOpenRemoteCtl')
@login_required
def mw_isOpenRemoteCtl():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    _, rows = db_proxy.read_db("select remotecontrol from managementmode")
    # rows = new_send_cmd(TYPE_APP_SOCKET, "select remotecontrol from managementmode", 1)
    isRemoteCtl = rows[0][0]
    # rows = new_send_cmd(TYPE_APP_SOCKET, "select accessIp from ipaccessrestrict where ipId=1", 1)
    _, rows = db_proxy.read_db("select accessIp from ipaccessrestrict where ipId=1")
    if len(rows) > 0:
        if 'ipv4' in rows[0][0]:
            iplist = json.loads(rows[0][0])
            return jsonify({'isRemoteCtl': isRemoteCtl, 'ipv4': iplist['ipv4'], 'ipv6': iplist['ipv6']})
        else:
            return jsonify({'isRemoteCtl': isRemoteCtl, 'ipv4': rows[0][0], 'ipv6': ''})
    return jsonify({'isRemoteCtl': isRemoteCtl})


@deviceinfo_page.route('/updateCtlFlag', methods=['GET', 'POST'])
@login_required
def mw_updateCtlFlag():
    # remote IP control mode;   open:1,close:0(default)
    if request.method == 'GET':
        flag = request.args.get('flag')
        loginuser = request.args.get('loginuser')
    else:
        post_data = request.get_json()
        flag = post_data['flag']
        loginuser = post_data['loginuser']
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if flag == '0':
        os.system("iptables -D INPUT -p tcp --dport 443 -j HTTPS_CHAIN")
        os.system("iptables -F HTTPS_CHAIN")
        os.system("ip6tables -D INPUT -p tcp --dport 443 -j HTTPS_CHAIN")
        os.system("ip6tables -F HTTPS_CHAIN")
        os.system("sed -i '/HTTPS_CHAIN/d' /etc/iptables_init")
        sql_cmd = "UPDATE managementmode set remotecontrol=" + flag
        # new_send_cmd(TYPE_APP_SOCKET, sql_cmd, 2)
        db_proxy.write_db(sql_cmd)
        conf_save_flag_set()
        # send operation log
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['Operate'] = u"远程登录IP控制关闭"
        msg['ManageStyle'] = 'WEB'
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@deviceinfo_page.route('/getLoginPara')
@login_required
def mw_getLoginPara():
    name = request.args.get('loginuser')
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sel_cmd = "select logoutTime,loginAttemptCount,pwSafeLevel from users where name='%s'" % name
    # rows = new_send_cmd(TYPE_APP_SOCKET, sel_cmd, 1)
    _, rows = db_proxy.read_db(sel_cmd)
    values = rows[0]
    return jsonify({'logoutTime': values[0], 'loginAttemptCount': values[1], 'pwSafeLevel': values[2]})


@deviceinfo_page.route('/loginSetting', methods=['GET', 'POST'])
@login_required
def mw_loginSetting():
    if request.method == 'GET':
        logoutMinute = request.args.get('logoutMinute')
        tryLogTimes = request.args.get('tryLogTimes')
        safeLevel = request.args.get('safeLevel')
        loginuser = request.args.get('loginuser')
    else:
        post_data = request.get_json()
        logoutMinute = post_data['logoutMinute']
        tryLogTimes = post_data['tryLogTimes']
        safeLevel = post_data['safeLevel']
        loginuser = post_data['loginuser']
    db_proxy = DbProxy(CONFIG_DB_NAME)
    update_cmd = "update users set logoutTime=" + logoutMinute + ",loginAttemptCount=\
        " + tryLogTimes + ",pwSafeLevel=" + safeLevel + ",updatedAt=" + str(tryLogTimes)
    # new_send_cmd(TYPE_APP_SOCKET, update_cmd, 2)
    db_proxy.write_db(update_cmd)
    conf_save_flag_set()
    # send operation log
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = "设置登录安全,强制登出时间:".decode("utf8") + logoutMinute + \
                     "分钟,可尝试登录次数:".decode("utf8") + str(tryLogTimes)
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@deviceinfo_page.route('/setDpiIp', methods=['GET', 'POST'])
@login_required
def mw_setdpiip():
    if request.method == 'GET':
        newdpiip = request.args.get('Newdpiip')
        newdpimask = request.args.get('newdpimask')
        newdpigateway = request.args.get('newdpigateway')
        loginuser = request.args.get('loginuser')
    else:
        post_data = request.get_json()
        newdpiip = post_data['Newdpiip']
        newdpimask = post_data['newdpimask']
        newdpigateway = post_data['newdpigateway']
        loginuser = post_data['loginuser']
    webDpi.setdpiip(newdpiip, newdpimask, newdpigateway)
    time.sleep(5)
    # send operation log
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = "设置设备IP:".decode("utf8") + newdpiip + ",子网掩码:".decode("utf8") + \
                     newdpimask + ",网关:".decode("utf8") + newdpigateway
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@deviceinfo_page.route('/setDpiIp6', methods=['GET', 'POST'])
@login_required
def mw_setdpiip6():
    try:
        # 1、获取请求参数
        if request.method == 'GET':
            newdpiip6 = request.args.get('newdpiip6')
            newdpiPrefix6 = request.args.get('newdpiPrefix')
            newdpigateway6 = request.args.get('newdpigateway')
            loginuser = request.args.get('loginuser')
        else:
            post_data = request.get_json()
            newdpiip6 = post_data['newdpiip6']
            newdpiPrefix6 = post_data['newdpiPrefix']
            newdpigateway6 = post_data['newdpigateway']
            loginuser = post_data['loginuser']

        # 2、参数校验
        try:
            if not is_ipv6(newdpiip6):
                return jsonify({'status': 0, 'msg': 'ipv6格式错误'})
        except Exception:
            return jsonify({'status': 0, 'msg': 'ipv6格式错误'})
        try:
            if not check_ip(newdpigateway6):
                return jsonify({'status': 0, 'msg': '网关格式错误'})
        except Exception:
            return jsonify({'status': 0, 'msg': '网关格式错误'})
        try:
            if type(eval(newdpiPrefix6)) == int:
                prefix = int(newdpiPrefix6)
                if prefix < 0 or prefix > 128:
                    return jsonify({'status': 0, 'msg': '前缀格式错误'})
            else:
                return jsonify({'status': 0, 'msg': '前缀格式错误'})
        except SyntaxError:
            return jsonify({'status': 0, 'msg': '前缀格式错误'})



        # 4、删除旧ipv6 删除旧默认路由
        # while True:
        #     res = commands.getoutput('ifconfig agl0')
        #     add_type = ""
        #     if res.find('Scope:Site') != -1:
        #         add_type = "Scope:Site"
        #     elif res.find('Scope:Global') != -1:
        #         add_type = "Scope:Global"
        #     else:
        #         break
        #
        #     if add_type != "":
        #         stop_ip6 = res.find(add_type) - 1
        #         stop_ip6_link = res.find('Scope:Link') - 1
        #         if stop_ip6 > stop_ip6_link:
        #             start_ip6 = res.find('inet6 addr:',stop_ip6_link) + 11
        #         else:
        #             start_ip6 = res.find('inet6 addr:') + 11
        #         ip6 = res[start_ip6:stop_ip6]
        #         if os.system('ifconfig agl0 inet6 del %s' % (ip6))!=0:
        #             return jsonify({'status': 0, 'msg': '删除旧ipv6失败'})

        ip6, prefix = getip6_prefix_from_interfaces()
        if ip6:
            if os.system('ifconfig agl0 inet6 del %s/%s' % (ip6, prefix)) != 0:
                return jsonify({'status': 0, 'msg': '删除旧ipv6失败'})

        # 4、 修改网卡文件
        modify_interfaces(newdpiip6, newdpiPrefix6, newdpigateway6)

        # 删除默认路由
        # 循环删除多条默认路由 没有do while ,使用 while break模拟do while
        while True:
            r = os.system('route -A inet6 del default')
            if r == 256:
                break
            if r !=0:
                return jsonify({'status': 0, 'msg': '删除默认路由失败'})




        # 5、配置新ip
        if os.system('ifconfig agl0 inet6 add %s/%s' % (newdpiip6, newdpiPrefix6)) != 0 and os.system(
                        'ifconfig agl0 inet6 add %s/%s' % (newdpiip6, newdpiPrefix6)) != 256:
            return jsonify({'status': 0, 'msg': '设置ipv6失败'})

        # if os.system('ifconfig agl0 down')!=0:
        #     return jsonify({'status': 0, 'msg': '关闭网卡失败'})
        # time.sleep(1)
        # if os.system('ifconfig agl0 up')!=0:
        #     return jsonify({'status': 0, 'msg': '启动网卡失败'})

        # 6、配置默认路由
        if os.system('route -A inet6 add default gw %s' % (newdpigateway6)) != 0 and os.system(
                        'route -A inet6 add default gw %s' % (newdpigateway6)) != 256:
            return jsonify({'status': 0, 'msg': '设置默认路由失败'})

        # send operation log
        # 7、操作记录
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['Operate'] = "设置设备IP:".decode("utf8") + newdpiip6 + ",子网掩码:".decode("utf8") + newdpiPrefix6 + ",网关:".decode(
            "utf8") + newdpigateway6
        msg['ManageStyle'] = 'WEB'
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
    except:
        current_app.logger.error(traceback.format_exc())
        return jsonify({'status': 0, 'msg': '设置ipv6失败'})
    return jsonify({'status': 1, 'msg': '设置ipv6成功'})


def modify_interfaces(ip, prefix, gateway):
    """
    修改网卡文件
    :param ip:
    :param prefix:
    :param gateway:
    :return:
    """
    try:
        interfaces_file_path = r'/app/etc/network/interfaces'
        file_handler = open(interfaces_file_path, "r")
        network_content = file_handler.read()
        file_handler.close()

        content_split = network_content.split('\n')

        # 三个属性要有都有，要没有都没有
        if network_content.find("inet6 static") == -1:
            network_content = "iface agl0 inet6 static\nipv6addr %s\nprefix %s\nipv6gw %s\n" % (ip, prefix, gateway)+network_content
        else:
            flag = False
            for i, content in enumerate(content_split):
                if content.find('inet6') != -1:
                    flag = True
                if flag:
                    if content.find("ipv6addr") != -1:
                        content_split[i] = "ipv6addr %s" % (ip)
                    if content.find("prefix") != -1:
                        content_split[i] = "prefix %s" % (prefix)
                    if content.find("ipv6gw") != -1:
                        content_split[i] = "ipv6gw %s" % (gateway)

            network_content = '\n'.join(content_split)
        with open(interfaces_file_path, "w") as f:
            f.write(network_content)
    except Exception, e:
        raise e


def is_ipv4(ip):
    try:
        socket.inet_pton(socket.AF_INET, ip)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(ip)
        except socket.error:
            return False
        return ip.count('.') == 3
    except socket.error:  # not a valid ip
        return False
    return True


def is_ipv6(ip):
    try:
        socket.inet_pton(socket.AF_INET6, ip)
    except socket.error:  # not a valid ip
        return False
    return True

def is_link_ipv6(ip):
    try:
        ip_0 = ip.split(":")[0]
        if bin(int(ip_0,16)).lstrip('0b')[:10] == '1111111010':
            return True
        else:
            return False
    except:
        return False

def check_ip(ip):
    return is_ipv4(ip) or is_ipv6(ip)


def getip6_prefix_from_interfaces():
    try:
        interfaces_file_path = r'/app/etc/network/interfaces'
        file_handler = open(interfaces_file_path, "r")
        network_content = file_handler.read()
        file_handler.close()

        index_ip6addr = network_content.find('ipv6addr')
        if index_ip6addr == -1:
            return '', ''
        else:
            index_ip6addr_end = network_content.find('\n', index_ip6addr)
            index_ip6addr_start = index_ip6addr

            index_prefix_start = network_content.find('prefix')
            index_prefix_end = network_content.find('\n', index_prefix_start)
            return (network_content[index_ip6addr_start:index_ip6addr_end].strip().split(' ')[1],
                    network_content[index_prefix_start:index_prefix_end].strip().split(' ')[1])
    except Exception, e:
        raise e


@deviceinfo_page.route('/rebootDpi')
@login_required
def mw_rebootdpi():
    msg = {}
    userip = get_oper_ip_info(request)
    loginuser = request.args.get('loginuser')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = u"重启设备"
    msg['ManageStyle'] = 'WEB'
    try:
        current_app.logger.info('----------reboot system--------------')
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        subprocess.Popen(['vtysh', '-c', 'config t', '-c', 'reboot'])
    except:
        current_app.logger.info('reboot system failed')
        tb = traceback.format_exc()
        current_app.logger.error(tb)
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 0})
    return jsonify({'status': 1})


@deviceinfo_page.route('/closeDpi')
@login_required
def mw_closedpi():
    msg = {}
    userip = get_oper_ip_info(request)
    loginuser = request.args.get('loginuser')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = u"关闭设备"
    msg['ManageStyle'] = 'WEB'
    try:
        current_app.logger.info('-----------------------power off system--------------')
        subprocess.Popen(['vtysh', '-c', 'config t', '-c', 'poweroff'])
    except:
        current_app.logger.error('power off system failed')
        tb = traceback.format_exc()
        current_app.logger.error(tb)
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 0})
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@deviceinfo_page.route('/defaultPara')
@login_required
def mw_setParaDefault():
    if g_dpi_plat_type == DEV_PLT_X86:
        msg = {}
        userip = get_oper_ip_info(request)
        loginuser = request.args.get('loginuser')
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['Operate'] = u"恢复出厂设置"
        msg['ManageStyle'] = 'WEB'
        db_proxy = DbProxy(CONFIG_DB_NAME)
        try:
            commands.getoutput("rm -f /app/db_flag/mysql_check_error.flag")
            commands.getoutput("rm -f /conf/db/devconfig.db")
            commands.getoutput("cp -f /app/local/share/new_self_manage/devconfig.db /conf/db/devconfig.db")
            subprocess.call(['vtysh', '-c', 'config t', '-c', 'factory-reset'])
            # wait for DPI factory reset done!
            time.sleep(5)
            # update sqlite and dpi config
            # init_sqlite()
            if RUN_MODE == 'ips':
                sql_str = "update dpi_mode set mode=2"
                # mode_rows = new_send_cmd(TYPE_APP_SOCKET, sql_str, 2)
                _, mode_rows = db_proxy.read_db(sql_str)
                proto_switch = "update nsm_protoswitch set proto_bit_map=0"
                # swithc_rows = new_send_cmd(TYPE_APP_SOCKET, proto_switch, 2)
                db_proxy.write_db(proto_switch)
                subprocess.call(['vtysh', '-c', 'config t', '-c', 'start dpi'])
                time.sleep(5)
                subprocess.call(['vtysh', '-c', 'config t', '-c', 'dpi industry_protocol 0'])
                time.sleep(10)
                subprocess.call(['vtysh', '-c', 'config t', '-c', 'stop dpi'])
                time.sleep(5)
            else:
                sql_str = "update dpi_mode set mode=1"
                # mode_rows = new_send_cmd(TYPE_APP_SOCKET, sql_str, 2)
                db_proxy.write_db(sql_str)
                os.system("/app/bin/conf_bakup.sh")
            msg['Result'] = '0'
            os.system("/app/sbin/factory_reset_mysql.sh")
            # 以下三行代码是指设备恢复出厂设置后不需要再进行license授权，创建文件用于中间件识别
            if not os.path.exists('/data/licsystemreset'):
                os.system("mkdir -p /data/licsystemreset")
            os.system("touch /data/licsystemreset/system_reset.lic")
            time.sleep(1)
            mw_rebootdpi()
        except:
            current_app.logger.error('Factory reset Failed')
            tb = traceback.format_exc()
            current_app.logger.error(tb)
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0})
        return jsonify({'status': 1})
    else:
        msg = {}
        userip = get_oper_ip_info(request)
        loginuser = request.args.get('loginuser', '')
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['Operate'] = u"恢复出厂设置"
        msg['ManageStyle'] = 'WEB'

        try:
            commands.getoutput("rm -f /data/db/devconfig.db")
            commands.getoutput("cp -f /data/db/devconfig.db.bak /data/db/devconfig.db")

            commands.getoutput("iptables -D INPUT -p tcp --dport 443 -j HTTPS_CHAIN")
            commands.getoutput("iptables -F HTTPS_CHAIN")
            commands.getoutput("ip6tables -D INPUT -p tcp --dport 443 -j HTTPS_CHAIN")
            commands.getoutput("ip6tables -F HTTPS_CHAIN")
            commands.getoutput("sed -i '/HTTPS_CHAIN/d' /etc/iptables_init")

            commands.getoutput('rm -rf /data/dbg_collect/*')
            commands.getoutput('rm -rf /data/sysbackup/*')

            msg['Result'] = '0'
            send_log_db(MODULE_OPERATION, msg)
            time.sleep(5)
            os.system("touch /data/mysql/mysql_rebuild.flag")
            # 以下三行代码是指设备恢复出厂设置后不需要再进行license授权，创建文件用于中间件识别
            if not os.path.exists('/data/licsystemreset'):
                os.system("mkdir -p /data/licsystemreset")
            os.system("touch /data/licsystemreset/system_reset.lic")
            time.sleep(1)
            subprocess.Popen(['vtysh', '-c', 'config t', '-c', 'factory-reset'])
            time.sleep(1)
            mw_rebootdpi()
        except:
            current_app.logger.error('Factory reset Failed')
            tb = traceback.format_exc()
            current_app.logger.error(tb)
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0})
        return jsonify({'status': 1})

def update_events():
    """
    触发器函数更新
    :return:
    """
    process = Popen(
        '/app/local/mysql-5.6.31-linux-glibc2.5-x86_64/bin/mysql -ukeystone -pOptValley@4312',
        stdout=PIPE, stdin=PIPE, shell=True)
    try:
        process.stdin.write('use keystone\n')
        process.stdin.write(
            'source /app/local/share/new_self_manage/common/update_events.sql\n')
        process.stdin.write('exit\n')
        process.wait()
        logger.info("source update_events.sql ok")
    except:
        logger.error('source update_events.sql error')
        logger.error(traceback.format_exc())

@deviceinfo_page.route('/setTimeSynManualInput', methods=['GET', 'POST'])
@login_required
def mw_setTimeSynManualInput():
    msg = {}
    userip = get_oper_ip_info(request)
    if request.method == 'GET':
        loginuser = request.args.get('loginuser')
        inputTime = request.args.get('inputTime')
    else:
        post_data = request.get_json()
        loginuser = post_data['loginuser']
        inputTime = post_data['inputTime']
    db_proxy = DbProxy(CONFIG_DB_NAME)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    # stop ntp syn
    # new_send_cmd(TYPE_APP_SOCKET, "UPDATE managementmode set synDestIp='127.0.0.1'", 2)
    db_proxy.write_db("UPDATE managementmode set synDestIp='127.0.0.1'")
    conf_save_flag_set()
    os.system("ntpd -qn -p 127.0.0.1")
    # start date -s
    inputTimeCmd = "date -s " + "\"" + inputTime + "\""
    os.system(inputTimeCmd)
    os.system('hwclock -w -u')
    # send operation log
    msg['Operate'] = "设置手动时间同步:".decode("utf8") + inputTime
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    update_events()
    return jsonify({'status': 1})


@deviceinfo_page.route('/setTimeSynAuto', methods=['GET', 'POST'])
@login_required
def mw_setTimeSynAuto():
    msg = {}
    userip = get_oper_ip_info(request)
    if request.method == 'GET':
        loginuser = request.args.get('loginuser')
        destIp = request.args.get('destIp')
    else:
        post_data = request.get_json()
        loginuser = post_data['loginuser']
        destIp = post_data['destIp']
    db_proxy = DbProxy(CONFIG_DB_NAME)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    # sql_cmd = "UPDATE managementmode set synDestIp=" + "\"" + str(destIp) + "\""
    # new_send_cmd(TYPE_APP_SOCKET, sql_cmd, 2)
    sql_cmd = "UPDATE managementmode set synDestIp='%s'" % str(destIp)
    db_proxy.write_db(sql_cmd)
    conf_save_flag_set()
    # send operation log
    msg['Operate'] = "设置NTP自动时间同步, IP:".decode("utf8") + destIp
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    update_events()
    return jsonify({'status': 1})


@deviceinfo_page.route('/getTimeSynDestIp')
@login_required
def mw_getTimeSynDestIp():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    mode = 1
    # rows = new_send_cmd(TYPE_APP_SOCKET, "select synDestIp from managementmode", 1)
    _, rows = db_proxy.read_db("select synDestIp from managementmode")
    synDestIp = rows[0][0]
    if synDestIp == '127.0.0.1':
        mode = 0
    return jsonify({'mode': mode, 'serverIp': synDestIp})


@deviceinfo_page.route('/accessIp')
@login_required
def mw_accessIp():
    page = request.args.get('page', 0, type=int)
    total = 0
    value = ""
    db_proxy = DbProxy(CONFIG_DB_NAME)
    add_str = ' LIMIT 1 OFFSET 0'
    sql_str = "select * from ipaccessrestrict " + add_str
    # rows = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
    _, rows = db_proxy.read_db(sql_str)
    try:
        value = rows[0][1]
    except:
        value = ""
    return jsonify({'data': value})


def check_login_config_ip(ip, ip_type):
    if ip_type == 4:
        try:
            ipaddress.IPv4Address(unicode(ip))
        except:
            return 4
    if ip_type == 6:
        try:
            ipaddress.IPv6Address(unicode(ip))
        except:
            return 6


@deviceinfo_page.route('/addAccessIp', methods=['GET', 'POST'])
@login_required
def mw_addaccessip():
    if request.method == 'GET':
        accessIp = request.args.get('accessIp')
        loginuser = request.args.get('loginuser')
    else:
        post_data = request.get_json()
        accessIpv4 = post_data['ipv4']
        loginuser = post_data['loginuser']
        accessIpv6 = post_data['ipv6']

    db_proxy = DbProxy(CONFIG_DB_NAME)
    #send operation log
    msg={}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = u"远程登录IP控制开启"
    msg['ManageStyle'] = 'WEB'
    #check if have the accessip
    ipv4_json = '''"ipv4":""'''
    ipv6_json = '''"ipv6":""'''

    # if accessIpv4:
    #     for accessip in accessIpv4.split(","):
    #         try:
    #             ipaddress.ip_interface(accessip)
    #         except:
    #             return jsonify({"status": 0, "msg": u"ip地址/掩码格式不正确"})
    #         break

    if accessIpv4 and accessIpv6:
        status = setRestrictInIptables(accessIpv4, 4)

        if status == 4:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0, 'msg':u'请输入正确的IPV4地址'})
        ipv4_json = '''"ipv4":"%s"''' % accessIpv4
        status = setRestrictInIptables(accessIpv6, 6)
        if status == 6:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0, 'msg':u'请输入正确的IPV6地址'})
        ipv6_json = '''"ipv6":"%s"''' % accessIpv6
    elif accessIpv4:
        status = setRestrictInIptables(accessIpv4, 4)
        if status == 4:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0, 'msg':u'请输入正确的IPV4地址'})
        os.system("ip6tables -F")
        os.system("ip6tables -D INPUT -p tcp --dport 443 -j HTTPS_CHAIN")
        ipv4_json = '''"ipv4":"%s"''' % accessIpv4
    elif accessIpv6:
        status = setRestrictInIptables(accessIpv6, 6)
        if status == 6:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0, 'msg':u'请输入正确的IPV6地址'})
        os.system("iptables -F HTTPS_CHAIN")
        os.system("iptables -D INPUT -p tcp --dport 443 -j HTTPS_CHAIN")
        ipv6_json = '''"ipv6":"%s"''' % accessIpv6
    else:
        status = 0

    if status == 0:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': status, 'msg':u"添加登录设置IP失败"})

    count_str = "select count(*) from ipaccessrestrict"
    # rows = new_send_cmd(TYPE_APP_SOCKET, count_str, 1)
    _, rows = db_proxy.read_db(count_str)
    num = rows[0][0]
    if num == 0:
        try:
            sql_str = """insert into ipaccessrestrict (accessIp) values ('{%s,%s}')""" % (ipv4_json, ipv6_json)
            # new_send_cmd(TYPE_APP_SOCKET, sql_str, 2)
            db_proxy.write_db(sql_str)
            conf_save_flag_set()
            current_app.logger.info(sql_str)
        except:
            current_app.logger.error(traceback.format_exc())
    else:
        try:
            sql_str = """UPDATE ipaccessrestrict set accessIp='{%s,%s}'""" % (ipv4_json, ipv6_json)
            # new_send_cmd(TYPE_APP_SOCKET, sql_str, 2)
            db_proxy.write_db(sql_str)
            conf_save_flag_set()
            current_app.logger.info(sql_str)
        except:
            current_app.logger.error(traceback.format_exc())
    sql_cmd = "UPDATE managementmode set remotecontrol=1"
    # new_send_cmd(TYPE_APP_SOCKET, sql_cmd, 2)
    db_proxy.write_db(sql_cmd)
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': status})


@deviceinfo_page.route('/updateAccessIp', methods=['GET', 'POST'])
@login_required
def mw_updateaccessip():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        accessIp = request.args.get('ip')
        ipId = request.args.get('id')
    elif request.method == 'POST':
        post_data = request.get_json()
        accessIp = post_data['ip']
        ipId = post_data['id']
    sql_str = "UPDATE ipaccessrestrict set accessIp=" + "\"" + accessIp + "\"" + " where ipId=" + ipId
    result = db_proxy.write_db(sql_str)
    return jsonify({'status': 1})


@deviceinfo_page.route('/deployAccessIp')
@login_required
def mw_deployaccessip():
    ret = 0
    return jsonify({'status': ret})


@deviceinfo_page.route('/ipv6FunctionSwitch', methods=['GET', 'POST'])
@login_required
def update_ipv6_function_switch():
    try:
        db_proxy = DbProxy(CONFIG_DB_NAME)
        if request.method == 'GET':
            sql_str = "select ipv6Switch from ipv6_function_switch"
            # rows = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
            res, rows = db_proxy.read_db(sql_str)
            return jsonify({'status': 1, 'switch': rows[0][0]})
        else:
            post_data = request.get_json()
            loginuser = post_data.get('loginuser', '')
            switch = int(post_data.get('switch'))
            msg={}
            userip = get_oper_ip_info(request)
            msg['UserIP'] = userip
            ret_msg = None
            vtysh_str = None
            msg['UserName'] = loginuser
            if switch == 0:
                msg['Operate'] = u"关闭IPV6功能"
                ret_msg = u"关闭IPV6功能成功"
                vtysh_str = "dpi ipv6-function off"
            else:
                msg['Operate'] = u"开启IPV6功能"
                ret_msg = u"开启IPV6功能成功"
                vtysh_str = "dpi ipv6-function on"
            msg['ManageStyle'] = 'WEB'

            sql_str = "UPDATE ipv6_function_switch set ipv6Switch =%d"%(switch)
            db_proxy.write_db(sql_str)
            msg['Result'] = '0'
            send_log_db(MODULE_OPERATION, msg)
            process = subprocess.Popen(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', vtysh_str])
            process.wait()
            return jsonify({'status': 1, 'msg':ret_msg})
    except:
        current_app.logger.error(traceback.format_exc())
        return jsonify({'status': 0, 'msg': '设置ipv6开关失败'})

def getiptype(ip):
    if ip.find('-') >= 0:
        return 1
    elif ip.find('/') >= 0:
        return 2
    return 0


def write_single_ip(ip, file_handle, ip_type):
    if ip_type == 4:
        iptablescmd = "iptables -I HTTPS_CHAIN -s " + ip + " -p tcp --dport 443 -j ACCEPT"
    else:
        iptablescmd = "ip6tables -I HTTPS_CHAIN -s " + ip + " -p tcp --dport 443 -j ACCEPT"
    res = commands.getoutput(iptablescmd)
    status = True
    file_handle.write(iptablescmd + '\n')
    if (len(res) > 0):
        status = False
        current_app.logger.error(ip_type)
    return status


def write_range_ip(iprange, file_handle, ip_type):
    res = ""
    if ip_type == 4:
        iptablescmd = "iptables -I HTTPS_CHAIN -m iprange --src-range "+iprange+" -p tcp --dport 443 -j ACCEPT"
    else:
        iptablescmd = "ip6tables -I HTTPS_CHAIN -m iprange --src-range "+iprange+" -p tcp --dport 443 -j ACCEPT"
    res = commands.getoutput(iptablescmd)
    file_handle.write(iptablescmd + '\n')
    status = True
    if res.find("xt_iprange") >= 0 or len(res) > 0:
        status = False
        current_app.logger.error(ip_type)
    return status

    
def write_mask_ip(ipmask, file_handle, ip_type):
    if ip_type == 4:
        iptablescmd = "iptables -I HTTPS_CHAIN -p tcp --dport 443 --src "+ipmask+" -j ACCEPT"
    else:
        iptablescmd = "ip6tables -I HTTPS_CHAIN -p tcp --dport 443 --src " + ipmask + " -j ACCEPT"
    status = True
    res = commands.getoutput(iptablescmd)
    file_handle.write(iptablescmd + '\n')
    if (len(res) > 0):
        status = False
        current_app.logger.error(ip_type)
    return status

    
def setRestrictInIptables(ipinfo, ip_type):
    ret = 0
    if ip_type == 4:
        os.system("iptables -N HTTPS_CHAIN")
        os.system("iptables -D INPUT -p tcp --dport 443 -j HTTPS_CHAIN")
        os.system("iptables -I INPUT -p tcp --dport 443 -j HTTPS_CHAIN")
        os.system("iptables -F HTTPS_CHAIN")
    else:
        os.system("ip6tables -N HTTPS_CHAIN")
        os.system("ip6tables -D INPUT -p tcp --dport 443 -j HTTPS_CHAIN")
        os.system("ip6tables -I INPUT -p tcp --dport 443 -j HTTPS_CHAIN")
        os.system("ip6tables -F HTTPS_CHAIN")
    os.system("sed -i '/HTTPS_CHAIN/d' /etc/iptables_init")
    try:
        file_oper = open('/etc/iptables_init',"a")
        if ip_type == 4:
            file_oper.write("iptables -N HTTPS_CHAIN\n")
            file_oper.write("iptables -D INPUT -p tcp --dport 443 -j HTTPS_CHAIN\n")
            file_oper.write("iptables -I INPUT -p tcp --dport 443 -j HTTPS_CHAIN\n")
            file_oper.write("iptables -F HTTPS_CHAIN\n")
        else:
            file_oper.write("ip6tables -N HTTPS_CHAIN\n")
            file_oper.write("ip6tables -D INPUT -p tcp --dport 443 -j HTTPS_CHAIN\n")
            file_oper.write("ip6tables -I INPUT -p tcp --dport 443 -j HTTPS_CHAIN\n")
            file_oper.write("ip6tables -F HTTPS_CHAIN\n")
        ip_list = ipinfo.split(',')
        status = True
        for ip in ip_list:
            type = getiptype(ip)
            if type == 0:
                ret = check_login_config_ip(ip, ip_type)
                if ret == 4 or ret == 6:
                    return ret
                status = write_single_ip(ip, file_oper, ip_type)
            elif type == 1:
                ip_temp = ip.split('-')
                while i < 2:
                    ret = check_login_config_ip(ip_temp[i], ip_type)
                    if ret == 4 or ret == 6:
                        return ret
                status = write_range_ip(ip, file_oper, ip_type)
            else:
                ret = check_login_config_ip(ip.split('/')[0], ip_type)
                if ret == 4 or ret == 6:
                    return ret
                status = write_mask_ip(ip, file_oper, ip_type)
            if status is False:
                break
        if ip_type == 4:
            file_oper.write("iptables -A HTTPS_CHAIN -j DROP\n")
            os.system("iptables -A HTTPS_CHAIN -j DROP")
        else:
            file_oper.write("ip6tables -A HTTPS_CHAIN -j DROP\n")
            os.system("ip6tables -A HTTPS_CHAIN -j DROP")
        file_oper.close()
    except:
        file_oper.close()
        current_app.logger.error("setRestrictInIptables iptables_init file oper error.")
        current_app.logger.error(traceback.format_exc())
        return 0
    if status is False:
        if ip_type == 4:
            os.system("iptables -D INPUT -p tcp --dport 443 -j HTTPS_CHAIN")
            os.system("iptables -F HTTPS_CHAIN")
        else:
            os.system("ip6tables -D INPUT -p tcp --dport 443 -j HTTPS_CHAIN")
            os.system("ip6tables -F HTTPS_CHAIN")
        # write iptables_init
        os.system("sed -i '/HTTPS_CHAIN/d' /etc/iptables_init")
        return 0
    return 1


def accessIp_init():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select count(*) from managementmode WHERE remotecontrol=1"
    # rows = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
    res, rows = db_proxy.read_db(sql_str)
    if rows[0][0] > 0:
        sql_str2 = "select accessIp from ipaccessrestrict"
        # rows2 = new_send_cmd(TYPE_APP_SOCKET, sql_str2, 1)
        _, rows2 = db_proxy.read_db(sql_str2)
        if len(rows2) > 0:
            try:
                dict_t = json.loads(rows2[0][0])
            except:
                return 0
            if 'ipv4' in dict_t.keys() and len(dict_t['ipv4']) > 0:
                setRestrictInIptables(dict_t['ipv4'], 4)
            if 'ipv6' in dict_t.keys() and len(dict_t['ipv6']) > 0:
                setRestrictInIptables(dict_t['ipv6'], 6)
    else:
        pass


@deviceinfo_page.route('/deleteAccessIp')
@login_required
def mw_deleteAccessIp():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    id = request.args.get('id')
    result = 0
    # del from iptables -L
    sel_cmd = 'select accessIp from ipaccessrestrict where ipId=' + id
    result, rows = db_proxy.read_db(sel_cmd)
    for row in rows:
        delIp = row[0]
    res = commands.getoutput('iptables -L')
    if res.find(delIp) != -1:
        del_cmd = "iptables -D INPUT -s " + delIp + " -p tcp --dport 443  -j ACCEPT"
        os.system(del_cmd)

    # write file
    sed_cmd = "sed -i '/" + delIp + "/d'" + " /etc/iptables_init"
    os.system(sed_cmd)

    # delete delIp form db
    sql_str = "delete from ipaccessrestrict where ipId=" + id
    result = db_proxy.write_db(sql_str)
    return jsonify({'status': 1})


@deviceinfo_page.route('/closeIpRestrict', methods=['GET', 'POST'])
@login_required
def mw_closeIpRestrict():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    os.system("iptables -D INPUT -p tcp --dport 443 -j HTTPS_CHAIN")
    os.system("iptables -F HTTPS_CHAIN")
    os.system("ip6tables -D INPUT -p tcp --dport 443 -j HTTPS_CHAIN")
    os.system("ip6tables -F HTTPS_CHAIN")
    # write iptables_init
    os.system("sed -i '/HTTPS_CHAIN/d' /etc/iptables_init")
    # remote IP control mode;   open:1,close:0(default)
    # new_send_cmd(TYPE_APP_SOCKET, 'UPDATE managementmode set remotecontrol=0', 2)
    db_proxy.write_db('UPDATE managementmode set remotecontrol=0')
    conf_save_flag_set()
    return jsonify({'status': 1})


@deviceinfo_page.route('/getCurMode')
@login_required
def mw_getCurMode():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "SELECT mode,mwIp,dhcp from managementmode"
    # rows = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
    _, rows = db_proxy.read_db(sql_str)
    values = rows[0]
    return jsonify({'curMode': values[0], 'curMwIp': values[1], 'curDhcp': values[2]})


@deviceinfo_page.route('/changeModelRes', methods=['GET', 'POST'])
@login_required
def mw_changemodel_res():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    selfManageInfo = {'valid': 'valid', 'tips': 'different', 'status': 0}
    post_data = request.get_json()
    controlMode = post_data['controlMode']
    # get db control mode and mwip
    # rows = new_send_cmd(TYPE_APP_SOCKET, "SELECT * from managementmode", 1)
    _, rows = db_proxy.read_db("SELECT * from managementmode")
    values = rows[0]
    # send operation log
    msg = {}
    userip = get_oper_ip_info(request)
    loginuser = post_data['loginuser']
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'

    # self:1  centralize:0
    if controlMode == '1':
        if values[0] == 1:
            selfManageInfo['tips'] = 'same'
            selfManageInfo['status'] = 0
            msg['Result'] = '1'
        else:
            try:
                # 1:close dhcp 2:update db, 3:set mwip loop, 4:set dpi flag, 5:restart
                current_app.logger.info('----------SELF MANAGEMENT,DHCP CLOSE--------------')
                # subprocess.Popen(['vtysh', '-c', 'config t', '-c', 'dpi auto-discovery off'])
                # send_write_cmd(TYPE_APP_SOCKET,"UPDATE managementmode set mode=1, mwIp='127.0.0.1',dhcp=0")
                # new_send_cmd(TYPE_APP_SOCKET, "UPDATE managementmode set mode=1, mwIp='127.0.0.1', dhcp=0", 2)
                db_proxy.write_db("UPDATE managementmode set mode=1, mwIp='127.0.0.1', dhcp=0")
                conf_save_flag_set()
                webDpi.setmwip('127.0.0.1')
                #webDpi.setdpiflag(1)
                time.sleep(10)
                if g_dpi_plat_type == DEV_PLT_X86:
                    os.system('/etc/stop_app x86')
                else:
                    os.system('/etc/stop_app')
                time.sleep(3)
                os.system('/etc/start_app')
                selfManageInfo['tips'] = 'ok'
                selfManageInfo['status'] = 1
                msg['Result'] = '0'
            except:
                msg['Result'] = '1'
                current_app.logger.error(traceback.format_exc())
        msg['Operate'] = u"管理模式切换为:自管理"
    else:
        # dhcp 0:close  1:open
        dhcp = post_data['dhcp']
        if str(dhcp) == '1':
            try:
                # new_send_cmd(TYPE_APP_SOCKET, "UPDATE managementmode set mode=0, dhcp=1", 2)
                db_proxy.write_db("UPDATE managementmode set mode=0, dhcp=1")
                conf_save_flag_set()
                #webDpi.setdpiflag(0)
                current_app.logger.info('----------CENTRALIZE MANAGEMENT,DHCP OPEN--------------')
                time.sleep(10)
                if g_dpi_plat_type == DEV_PLT_X86:
                    os.system('/etc/stop_app x86')
                else:
                    os.system('/etc/stop_app')
                time.sleep(3)
                os.system('/etc/start_app')
                selfManageInfo['tips'] = 'ok'
                selfManageInfo['status'] = 1
                msg['Result'] = '0'
            except:
                msg['Result'] = '1'
                current_app.logger.error(traceback.format_exc())
        else:
            current_app.logger.info('----------CENTRALIZE MANAGEMENT,DHCP CLOSE--------------')
            mwip = post_data['mwip']
            if values[0] == 0 and mwip == values[1]:
                selfManageInfo['tips'] = 'same'
                selfManageInfo['status'] = 0
                msg['Result'] = '1'
            else:
                try:
                    # 1:update db, 2:set dpi flag, 3:set mwip loop, 4:restart
                    # new_send_cmd(TYPE_APP_SOCKET, "UPDATE managementmode set mode=0, mwIp='%s',dhcp=0" % (mwip), 2)
                    db_proxy.write_db("UPDATE managementmode set mode=0, mwIp='%s',dhcp=0" % mwip)
                    conf_save_flag_set()
                    #webDpi.setdpiflag(0)
                    webDpi.setmwip(mwip)
                    #child = subprocess.Popen(['vtysh', '-c', 'write file'])
                    #child.wait()
                    time.sleep(10)
                    if g_dpi_plat_type == DEV_PLT_X86:
                        os.system('/etc/stop_app x86')
                    else:
                        os.system('/etc/stop_app')
                    time.sleep(3)
                    os.system('/etc/start_app')
                    selfManageInfo['tips'] = 'ok'
                    selfManageInfo['status'] = 1
                    msg['Result'] = '0'
                except:
                    msg['Result'] = '1'
                    current_app.logger.error(traceback.format_exc())
        msg['Operate'] = u"管理模式切换为:集中管理"
    send_log_db(MODULE_OPERATION, msg)
    return jsonify(selfManageInfo=selfManageInfo)


def prepare_dpi_upgrade(upgrade_handle):
    res = upgrade_handle.prepare_down_image()
    if res == False:
        current_app.logger.error("update dpi prepare_down_image error!")
        return 0
    return 1


def start_dpi_upgrade(upgrade_handle, filename):
    res = upgrade_handle.check_image_sign(filename)
    if res == False:
        current_app.logger.error("update dpi check_image_sign error!")
        return 0
    res = upgrade_handle.update_image_file(filename)
    if res == False:
        current_app.logger.error("update dpi update_image_file error!")
        return 0
    if upgrade_handle.package_upgrade_flag:
        current_app.logger.info("package upgrade mode!")
        return 2
    current_app.logger.info("dpi upgrade successfully!")
    return 1


def prepare_dpi_upgrade_MIPS(upgrade_handle, filename):
    pos = filename.find('-')
    if -1 == pos:
        current_app.logger.error("update dpi get version error!")
        return 0
    now_version = filename[0:pos]
    res, error = upgrade_handle.check_image_version(now_version)
    if res == False:
        current_app.logger.error("update dpi check_image_version error!")
        return 0
    res = upgrade_handle.prepare_down_image()
    if res == False:
        current_app.logger.error("update dpi prepare_down_image error!")
        return 0
    return 1


def start_dpi_upgrade_MIPS(upgrade_handle, filename):
    res = upgrade_handle.check_image_md5(filename)
    if res == False:
        current_app.logger.error("update dpi check_image_md5 error!")
        return 0
    res = upgrade_handle.update_image_file(filename)
    if res == False:
        current_app.logger.error("update dpi update_image_file error!")
        return 0
    commands.getoutput("reboot")
    return 1


@deviceinfo_page.route('/checkupdatespace')
@login_required
def mw_checkupdatespace():
    status = 0
    if g_dpi_plat_type == DEV_PLT_X86:
        upgrade_path = "/app"
    else:
        upgrade_path = "/boot"
    disk2 = os.statvfs(upgrade_path)
    avail_disk = (disk2.f_bsize * disk2.f_bavail) / (1024 * 1024)
    if (g_dpi_plat_type == DEV_PLT_X86 and avail_disk < 500) or (g_dpi_plat_type == DEV_PLT_MIPS and avail_disk < 300):
        status = 0
    else:
        status = 1
    return jsonify({'status': status})


# def make_sql_ver_flag():
#     """
#     从keystone_new.sql中获取当前版本sql_version信息,并存储到upgrade_info.json文件中以备使用
#     :return:
#     """
#     sqlpath = "/app/share/keystone_new.sql"
#     tag = "SQL file version: "
#     sqlverion = "V1.0"
#     try:
#         if os.path.exists("/data/mysql/sql_upgrade_error.flag"):
#             if os.path.exists("/data/mysql/upgrade_info.json"):
#                 return
#         with open(sqlpath, "r+") as f:
#             for line in f.readlines():
#                 if tag in line:
#                     sqlverion = line.split(tag)[1].strip()
#         versionpath = "/data/mysql/upgrade_info.json"
#         if not os.path.exists(versionpath):
#             command = "touch %s" % versionpath
#             os.system(command)
#         dict = {"from_ver": sqlverion}
#         with open(versionpath, "w+") as f:
#             f.write(json.dumps(dict))
#         current_app.logger.info("get mysql from_version success.")
#         return
#     except:
#         current_app.logger.error(traceback.format_exc())
#         return


@deviceinfo_page.route('/dpiUpdate', methods=['GET', 'POST'])
@login_required
def mw_dpiUpdate():
    if g_dpi_plat_type == DEV_PLT_X86:
        status = 0
        # send operation log
        msg = {}
        userip = get_oper_ip_info(request)
        if request.method == 'GET':
            loginuser = request.args.get('loginuser')
        elif request.method == 'POST':
            loginuser = request.form.get('loginuser')
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'
        msg['Operate'] = u"系统升级操作"
        if request.method == 'POST':
            file = request.files['system_upgrade_fileUpload']
            if file and update_allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upgrade_handle = UpgradeImage()
                command = "mkdir -p %s" % (UPDATE_FOLDER)
                os.system(command)
                file.save(os.path.join(UPDATE_FOLDER, filename))
                # 执行该方法将升级前mysql版本信息存储到/data/mysql/upgrade_info.json
                # make_sql_ver_flag()
                status = start_dpi_upgrade(upgrade_handle, filename)
                if status == 0:
                    msg['Result'] = '1'
                elif status == 1:
                    msg['Result'] = '0'
                    send_log_db(MODULE_OPERATION, msg)
                    commands.getoutput("reboot")
                elif status == 2:
                    msg['Result'] = '0'
                    send_log_db(MODULE_OPERATION, msg)
                    upgrade_handle.package_upgrade()
                return Response(json.dumps({'status': status}), content_type='text/html')
            else:
                msg['Result'] = '1'
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({'status': status})

        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': status})
    else:
        status = 0
        # send operation log
        msg = {}
        userip = get_oper_ip_info(request)
        loginuser = request.form.get('loginuser')
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'
        msg['Operate'] = u"系统升级操作"
        disk2 = os.statvfs(UPDATE_FOLDER)
        avail_disk = (disk2.f_bsize * disk2.f_bavail) / (1024 * 1024)
        if avail_disk < 300:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return Response(json.dumps({'status': 2}), content_type='text/html')
        if request.method == 'POST':
            file = request.files['system_upgrade_fileUpload']
            if file and update_allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upgrade_handle = UpgradeImage_MIPS()
                res = prepare_dpi_upgrade_MIPS(upgrade_handle, filename)
                if 0 == res:
                    msg['Result'] = '1'
                    send_log_db(MODULE_OPERATION, msg)
                    return Response(json.dumps({'status': 0}), content_type='text/html')
                file.save(os.path.join(UPDATE_FOLDER, filename))

                msg['Result'] = '0'
                send_log_db(MODULE_OPERATION, msg)
                status = start_dpi_upgrade_MIPS(upgrade_handle, filename)
                return Response(json.dumps({'status': status}), content_type='text/html')
            else:
                msg['Result'] = '1'
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({'status': status})
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': status})


@deviceinfo_page.route('/confSaveRes', methods=['GET', 'POST'])
@login_required
def mw_confSave_res():
    return jsonify({'status': 1, 'flag': conf_save_flag_get()})


@deviceinfo_page.route('/confSaveOper', methods=['GET', 'POST'])
@login_required
def mw_confSave_oper():
    # subprocess.Popen(['vtysh', '-c', 'config t', '-c', "write file"])
    conf_save_flag_unset()

    # send operation log
    msg = {}
    userip = get_oper_ip_info(request)
    if request.method == 'GET':
        loginuser = request.args.get('loginuser')
    elif request.method == 'POST':
        post_data = request.get_json()
        loginuser = post_data['loginuser']
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = u"保存当前配置"
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)

    return jsonify({'status': 1})


@deviceinfo_page.route('/getPhyInterface')
@login_required
def mw_get_phy_interface():
    int_array = []
    ok, map = mw_get_interface_map()
    if ok == 1:
        for key, value in map.items():
            int_array.append(key)
    else:
        phy_interfaces = os.popen("cat /proc/net/dev | awk -F: '/eth[0-9]/{print $1}'").read().strip('\n')
        int_array = phy_interfaces.replace('\n', ',').replace(' ', '').replace('eth', 'p').split(',')
    return jsonify({'status': 1, 'phy_interfaces': sorted(int_array)})


@deviceinfo_page.route('/setPcapSave', methods=['GET', 'POST'])
@login_required
def mw_set_pcapsave():
    if g_dpi_plat_type == DEV_PLT_X86:
        interfaces = []
        status = 0
        operate = u''
        switch = 10  # no special meaning

        if request.method == 'GET':
            switch = request.args.get('switch', 0, type=int)
            loginuser = request.args.get('loginuser', '')
        elif request.method == 'POST':
            post_data = request.get_json()
            switch = int(post_data.get('switch', '0'))
            loginuser = post_data.get('loginuser', '')

        # send operation log
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'

        try_count = 0
        while True:
            try_count += 1
            child = subprocess.Popen('vtysh -N', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            child.stdin.write('config t\n')
            child.stdin.write('dpi\n')

            if switch == 1 or switch == 2:
                operate = u'开启审计追踪功能'
                cmd = 'start pcap_save_all '
                if switch == '2':
                    cmd += ' clear'
                cmd += '\n'
                child.stdin.write(cmd)
                status = 1
            elif switch == 0:
                operate = u'关闭审计追踪功能'
                cmd = 'stop pcap_save_all \n'
                child.stdin.write(cmd)
                status = 1
            else:
                status = 0

            msg['Operate'] = operate

            child.stdin.write('exit\n')
            child.stdin.write('exit\n')
            child.stdin.write('exit\n')

            line_out = str(child.stdout.readlines())
            line_err = str(child.stderr.readlines())
            if len(line_out) > 2:
                current_app.logger.info("stdout[%d]:%s" % (len(line_out), line_out))
            if len(line_err) > 2:
                current_app.logger.info("stderr[%d]:%s" % (len(line_err), line_err))

            if line_out.find("pcap_save ok") != -1:
                break
            elif line_err.find("I/O error") != -1:
                time.sleep(5)
                continue
            elif try_count > 3:
                break
            else:
                time.sleep(5)

        ok, map = mw_get_interface_map()
        if ok == 1:
            for key, value in map.items():
                interfaces.append(value)
        else:
            interfaces = os.popen("cat /proc/net/dev | awk -F: '/eth[0-9]/{print $1}'").read().strip('\n').replace(' ',
                                                                                                                   '').split(
                '\n')

        current_app.logger.info("interfaces:%s" % (interfaces))
        for interface in interfaces:
            wait_time = 0
            while True:
                exist = 0
                return_code, output = commands.getstatusoutput('ps -auxw')
                current_app.logger.info("get pcap_save %s'tcpdump :%d" % (
                    interface, output.find("tcpdump -i %s -s0 -C 10 -W 10000" % (interface))))
                if output.find("tcpdump -i %s -s0 -C 10 -W 10000" % (interface)) != -1:
                    exist = 1
                if switch == 1 or switch == 2:
                    if exist == 1:
                        break
                elif switch == 0:
                    if exist == 0:
                        break
                time.sleep(1)
                wait_time += 1
                if wait_time > 30:
                    status = 0
                    msg['Result'] = (status == 1 and '0' or '1')
                    send_log_db(MODULE_OPERATION, msg)
                    return jsonify({'status': status})

        child = subprocess.Popen('vtysh -N', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        # child.stdin.write('config t\n')
        # child.stdin.write('write file\n\n')
        # child.stdin.write('exit\n')
        child.stdin.write('exit\n')

        msg['Result'] = (status == 1 and '0' or '1')
        send_log_db(MODULE_OPERATION, msg)

        return jsonify({'status': status})
    else:
        interfaces = []
        status = 0
        operate = u''
        loginuser = u''
        vtysh = ['vtysh']

        ok, map = mw_get_interface_map()
        if ok == 1:
            for key, value in map.items():
                interfaces.append(value)
        else:
            interfaces = os.popen("cat /proc/net/dev | awk -F: '/eth[0-9]/{print $1}'").read().strip('\n').replace(' ',
                                                                                                                   '').split(
                '\n')
        vtysh.append('-c')
        vtysh.append('configure terminal')
        vtysh.append('-c')
        vtysh.append('dpi')

        if request.method == 'GET':
            switch = request.args.get('switch', "")
            loginuser = request.args.get('loginuser')
        elif request.method == 'POST':
            post_data = request.get_json()
            switch = post_data['switch']
            loginuser = post_data['loginuser']

        if switch == '1' or switch == '2':
            operate = u'开启审计追踪功能'
            for interface in interfaces:
                cmd = 'start pcap_save '
                if interface != None:
                    cmd += 'interface '
                    cmd += interface
                    if switch == '2':
                        cmd += ' clear'
                    vtysh.append('-c')
                    vtysh.append(cmd)
        elif switch == '0':
            operate = u'关闭审计追踪功能'
            for interface in interfaces:
                cmd = 'stop pcap_save '
                if interface != None:
                    cmd += 'interface '
                    cmd += interface
                    vtysh.append('-c')
                    vtysh.append(cmd)
        else:
            status = 0
        vtysh.append('-c')
        vtysh.append('exit')
        # vtysh.append('-c')
        # vtysh.append('write file')
        vtysh.append('-c')
        vtysh.append('exit')
        vtysh.append('-c')
        vtysh.append('exit')
        try:
            subprocess.Popen(vtysh)
            status = 1
        except:
            status = 0
        # send operation log
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['Operate'] = operate
        msg['ManageStyle'] = 'WEB'
        msg['Result'] = (status == 1 and '0' or '1')
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': status})


@deviceinfo_page.route('/getPcapSave')
@login_required
def mw_get_pcapsave():
    ret = {}
    if g_dpi_plat_type == DEV_PLT_X86:
        ret_status, output = commands.getstatusoutput('ps -auxw | grep tcpdump')
    else:
        ret_status, output = commands.getstatusoutput('ps -w | grep tcpdump')

    if output.find('/data/pcap_save/p') != -1:
        ret['switch'] = 1
    else:
        ret['switch'] = 0

    ret['status'] = 1
    return jsonify(**ret)


@deviceinfo_page.route('/savePcapSaveExportServer', methods=['GET', 'POST'])
@login_required
def mw_save_PcapSaveExportServer():
    status = 0
    switch = 0
    host = ''
    username = ''
    password = ''

    if request.method == 'GET':
        switch = request.args.get('switch', 0, type=int)
        host = request.args.get('host', '')
        username = request.args.get('username', '')
        password = request.args.get('password', '')
    elif request.method == 'POST':
        data = request.get_json()
        switch = int(data.get('switch', '0'))
        host = data.get('host', '')
        username = data.get('username', '')
        password = data.get('password', '')

    db_proxy = DbProxy()
    sql = "update pcapsave_export_server_config set switch=%d,host='%s',username='%s',password='%s' where id = 1" % (
        switch, host, username, password)
    res = db_proxy.write_db(sql)
    if res == 0:
        status = 1

    return jsonify({'status': status})


@deviceinfo_page.route('/getPcapSaveExportServer', methods=['GET', 'POST'])
@login_required
def mw_get_PcapSaveExportServer():
    ret = {}

    db_proxy = DbProxy()
    sql = "select switch,host,username,password from pcapsave_export_server_config where id = 1"
    res, rows = db_proxy.read_db(sql)
    if res == 0:
        ret['switch'] = int(rows[0][0])
        ret['host'] = rows[0][1]
        ret['username'] = rows[0][2]
        ret['password'] = rows[0][3]
        ret['status'] = 1
        return jsonify(**ret)

    ret['status'] = 0
    return jsonify(**ret)


def mw_get_pcap_files(page, interface, starttime, endtime, exclude_files_id):
    status = 0
    data = []
    sum_count = 0
    sum_size = 0
    db_proxy = DbProxy()
    filter_str = ''
    exclude_files_list = exclude_files_id.split(',')
    sql_str = 'select filename,interface,starttime,endtime,id,size from pcap_info'
    count_str = 'select count(*),COALESCE(sum(size),0) from pcap_info'

    if len(interface) <= 0:
        return status, data, sum_count, sum_size

    interface_str = ''
    for intf in interface.split(','):
        if len(interface_str) > 0:
            interface_str += ","
        interface_str += "'" + intf + "'"

    filter_str += ' where interface in (' + interface_str + ')'

    if len(starttime) > 0 and len(endtime) > 0:
        filter_str += "and ((TIMESTAMPDIFF(second, pcap_info.starttime,'" + endtime + "') >= 0 and TIMESTAMPDIFF(second,'" + starttime + "',pcap_info.endtime) >= 0)) "
    elif len(starttime) > 0:
        filter_str += " and TIMESTAMPDIFF(second,'" + starttime + "',pcap_info.endtime) >= 0 "
    elif len(endtime) > 0:
        filter_str += " and TIMESTAMPDIFF(second,pcap_info.starttime,'" + endtime + "') >= 0 "

    filter_str += ' order by starttime desc,id desc'

    if page > 0:
        filter_str += ' limit ' + str((page - 1) * 10) + ',10'

    count_str += filter_str + ';'
    result, rows = db_proxy.read_db(count_str)
    for row in rows:
        sum_count = row[0]
        sum_size = row[1]
    sql_str += filter_str + ';'
    result, rows = db_proxy.read_db(sql_str)
    for row in rows:
        if row[0] != 0:
            if str(row[4]) not in exclude_files_list:
                data.append(row)
            else:
                sum_count -= 1
                sum_size -= int(row[5])

    status = 1
    return status, data, sum_count, sum_size


# /getPcapInfo?interface=p0,p1&starttime=2016-11-08%2017:02:07&endtime=2016-11-08%2017:02:07
@deviceinfo_page.route('/getPcapInfo', methods=['GET', 'POST'])
@login_required
def mw_get_pcapinfo():
    '''
    select filename,interface,starttime,endtime from pcap_info
    where interface in ('p0','p1') and starttime >= '2016-11-04T10:36:00Z' and endtime <= '2016-11-05T10:36:00Z'
    order by starttime
    limit 0,10;
    '''
    ret = {}
    data = []
    total = 0
    exclude_files_id = ''

    if request.method == 'GET':
        page = request.args.get('page', 1, int)
        interface = request.args.get('interface', '')
        starttime = request.args.get('starttime', '')
        endtime = request.args.get('endtime', '')
        exclude_files_id = request.args.get('file', '')  # for test
    elif request.method == 'POST':
        post_data = request.get_json()
        page = int(post_data['page'])
        interface = post_data['interface']
        starttime = post_data['starttime']
        endtime = post_data['endtime']

    ret['interface'] = interface
    ret['starttime'] = starttime
    ret['endtime'] = endtime

    status, data, total, sum_size = mw_get_pcap_files(page, interface, starttime, endtime, exclude_files_id)

    ret['rows'] = data
    ret['total'] = total
    ret['status'] = status
    ret['sum_size'] = int(sum_size)
    ret['support_download_max_size'] = mw_get_support_download_max_size()
    return jsonify(**ret)


# /pcapfile/p0/p0_20161110092448_20161110092701_f3.pcap
@deviceinfo_page.route('/pcapfile/<interface_name>/<file_name>', methods=['POST', 'GET'])
@login_required
def mw_pcap_download(interface_name, file_name):
    ret = 1
    response = None
    strerr = u''
    curdir = "/data/pcap_save/" + interface_name + "/"
    try:
        response = send_from_directory(curdir, file_name, as_attachment=True)
        ret = 0
    except NotFound, e:
        if e.code == 404:
            response = make_response('', 410)
            strerr = u'(该文件可能已被移至别处或遭到删除)'

    # send operation log
    msg = {}
    userip = get_oper_ip_info(request)
    loginuser = request.args.get('loginuser', '')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = u'下载' + file_name + strerr
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = ret
    send_log_db(MODULE_OPERATION, msg)

    return response


def mw_get_pcap_by_fileid(file_id_list):
    id_opt = ""
    sum_count = 0
    sum_size = 0
    db_proxy = DbProxy()

    for id in file_id_list.split(','):
        if len(id) <= 0:
            continue
        id_opt += " or id=" + id

    sql_statistic = 'select count(*),COALESCE(sum(size),0) from pcap_info where 1=2 %s' % id_opt
    result, rows_statistic = db_proxy.read_db(sql_statistic)
    if result == 0:
        sum_count = rows_statistic[0][0]
        sum_size = rows_statistic[0][1]

    sql = 'select filename from pcap_info where 1=2 %s' % id_opt
    result, rows = db_proxy.read_db(sql)
    return result, rows, sum_count, sum_size


def mv_download_pcap_process_count(op_type=None, op_val=0):
    count = 0
    download_multi_pcap_process_count = '/tmp/download_multi_pcap_process_count'
    if os.path.exists(download_multi_pcap_process_count) == False:
        os.system("echo 0 > /tmp/download_multi_pcap_process_count")
    with open(download_multi_pcap_process_count, 'r+') as fp:
        fcntl.flock(fp.fileno(), fcntl.LOCK_EX)  # locks the file
        count = int(fp.read())
        if op_type == '+':
            fp.seek(0)
            fp.write(str(count + int(op_val)))
        elif op_type == '-':
            fp.seek(0)
            fp.write(str(count - int(op_val)))
        elif op_type == '=':
            fp.seek(0)
            fp.write(str(op_val))
        else:
            # default case
            # read current process count
            pass
    return count


def mw_get_support_download_max_size():
    support_download_max_size = 500 * 1024 * 1024

    dev_type = get_dev_type()
    if dev_type == "IMAP":
        support_download_max_size = 1 * 1024 * 1024 * 1024
    elif dev_type == "KEA-U1000":
        support_download_max_size = 3 * 1024 * 1024 * 1024
    elif dev_type == "KEA-C200":
        support_download_max_size = 240 * 1024 * 1024
    return support_download_max_size


def mw_get_support_download_process_count():
    support_download_process_count = 1
    dev_type = get_dev_type()
    if dev_type == "IMAP":
        support_download_process_count = 3
    elif dev_type == "KEA-U1000":
        support_download_process_count = 3
    elif dev_type == "KEA-C200":
        support_download_process_count = 1
    return support_download_process_count


@deviceinfo_page.route('/request_download_or_export_multi_pcaps', methods=['GET', 'POST'])
@login_required
def mw_request_download_multi_pcap():
    ret = {}
    status = 1
    data = []
    sum_count = 0
    sum_size = 0
    download_process_count = mv_download_pcap_process_count()
    support_download_process_count = mw_get_support_download_process_count()
    support_download_max_size = mw_get_support_download_max_size()
    # TODO: how to make it precise
    # use 1 second to download 10M pcap file
    if g_dpi_plat_type == DEV_PLT_X86:
        download_time_10M = 8
    else:
        download_time_10M = 30

    login_user = None
    login_ip = get_oper_ip_info(request)
    if request.method == 'GET':
        files = request.args.get('files', '')
        login_user = request.args.get('loginuser', '')
        interface = request.args.get('interface', '')
        starttime = request.args.get('starttime', '')
        endtime = request.args.get('endtime', '')
        select_all = request.args.get('select_all', '0')
    elif request.method == 'POST':
        data = request.get_json()
        files = data.get('files', '')
        login_user = data.get('loginuser', '')
        interface = data.get('interface', '')
        starttime = data.get('starttime', '')
        endtime = data.get('endtime', '')
        select_all = data.get('select_all', '0')

    if int(select_all) == 1:
        page = 0  # stand for all pages
        status, data, sum_count, sum_size = mw_get_pcap_files(page, interface, starttime, endtime, files)
    else:
        status, data, sum_count, sum_size = mw_get_pcap_by_fileid(files)

    status = 1
    if int(sum_size) > support_download_max_size:
        status = 2  # the pcaps that will be downloaded is too big

    if download_process_count >= support_download_process_count:
        status = 3  # download process too many just now

    estimate_download_time = int(round((float((sum_size) / (10 * 1024 * 1024))) * download_time_10M))

    ret['sum_count'] = sum_count
    ret['sum_size'] = int(sum_size)
    ret['downloading_process_count'] = download_process_count
    ret['support_download_process_max_count'] = support_download_process_count
    ret['support_download_max_size'] = support_download_max_size
    ret['estimate_download_time'] = estimate_download_time
    ret['status'] = status
    return jsonify(**ret)


# construct the following command to download multi pcaps:
# 1. select all
# cd /data/pcap_save;tar cf - `cd /data/pcap_save;ls -l p*/* | awk '{print $9}' | awk -v starttime=0 -v endtime=20170309151008 -F[_/] '($2 ~ /p[0,1]/ && (($3>=starttime && $3<endtime) || ($4>starttime && $4<=endtime))){print $0}'|grep -v -E '^p0.*f410\..*|^p1.*f2\..*'`
# 2. don't select all, just select part
# cd /data/pcap_save;tar cf - `cd /data/pcap_save;ls -l p*/* | awk '{print $9}' | grep -E '^p0.*f410\..*|^p1.*f2\..*'`
#
@deviceinfo_page.route('/download_multi_pcaps', methods=['GET', 'POST'])
@login_required
def mw_download_multi_pcap():
    ret = {}
    cmd = ""
    tar_file_name = 'pcap'

    mv_download_pcap_process_count('+', 1)

    login_user = None
    login_ip = get_oper_ip_info(request)
    if request.method == 'GET':
        files = request.args.get('files', '')
        login_user = request.args.get('loginuser', '')
        interface = request.args.get('interface', '')
        starttime = request.args.get('starttime', '')
        endtime = request.args.get('endtime', '')
        select_all = request.args.get('select_all', '0')
    elif request.method == 'POST':
        data = request.get_json()
        files = data.get('files', '')
        login_user = data.get('loginuser', '')
        interface = data.get('interface', '')
        starttime = data.get('starttime', '')
        endtime = data.get('endtime', '')
        select_all = data.get('select_all', '0')

    current_app.logger.info("files:%s,interface:%s,starttime:%s,endtime:%s,select_all:%s" % (
        files, interface, starttime, endtime, select_all))
    starttime = starttime.replace('-', '').replace(':', '').replace(' ', '').strip()
    endtime = endtime.replace('-', '').replace(':', '').replace(' ', '').strip()

    files_opt = ""
    if len(files) > 0:
        result, rows, sum_count, sum_size = mw_get_pcap_by_fileid(files)
        if result == 0:
            for row in rows:
                filename = row[0]
                filename_list = filename.split('_')  # p0_20170105154407_20170105154424_f1.pcap
                interface_name = filename_list[0]  # p0
                file_index = filename_list[3].split('.')[0]  # f1
                files_opt += "^" + interface_name + ".*" + file_index + "\..*|"  # ^p0.*f1.*|
    if len(files_opt) > 0:
        files_opt = files_opt[:-1]  # del the last '|', to ^p0.*f410.*|^p1.*f2.*'

    if int(select_all) == 1:
        # select all: select the files by query condition, then tar them
        interface_opt = interface.replace('p', '').strip()
        if len(interface_opt) <= 0:
            interface_opt = ''
        else:
            interface_opt = "$2 ~ /p[" + interface_opt + "]/"  # $2 ~ /p[0,1]/

        cmd = "cd /data/pcap_save;tar cf - `cd /data/pcap_save;ls -l p*/* | awk '{print $9}' | awk"

        if len(starttime) <= 0 and len(endtime) <= 0:
            if len(interface_opt) <= 0:
                cmd += " -F[_/] '{print $0}' "
            else:
                cmd += " -F[_/] '(" + interface_opt + ") {print $0}' "
        elif len(starttime) > 0 and len(endtime) <= 0:
            if len(interface_opt) <= 0:
                cmd += " -v starttime=" + starttime + " -F[_/] '($4>=starttime){print $0}' "
            else:
                cmd += " -v starttime=" + starttime + " -F[_/] '(" + interface_opt + " && ($4>=starttime)) {print $0}' "
        elif len(starttime) <= 0 and len(endtime) > 0:
            if len(interface_opt) <= 0:
                cmd += " -v endtime=" + endtime + " -F[_/] '($3<=endtime){print $0}' "
            else:
                cmd += " -v endtime=" + endtime + " -F[_/] '(" + interface_opt + " && ($3<=endtime)) {print $0}' "
        elif len(starttime) > 0 and len(endtime) > 0:
            if len(interface_opt) <= 0:
                cmd += " -v starttime=" + starttime + " -v endtime=" + endtime + " -F[_/] '(($3>=starttime && $3<endtime) || ($4>starttime && $4<=endtime)){print $0}' "
            else:
                cmd += " -v starttime=" + starttime + " -v endtime=" + endtime + " -F[_/] '(" + interface_opt + " && (($3>=starttime && $3<endtime) || ($4>starttime && $4<=endtime))) {print $0}' "

        if len(files_opt) > 0:
            files_opt = "|grep -v -E '" + files_opt + "'"  # |grep -v -E '^p0.*f410.*|^p1.*f2.*'
            cmd += files_opt

        cmd += '`'

        # for tar file name to be saved
        tar_file_name += '_' + interface.replace(',', '_').strip()
        if len(starttime) > 0:
            tar_file_name += "_s" + starttime
        if len(endtime) > 0:
            tar_file_name += "_e" + endtime
    else:
        #  don't select all, just select part. tar the files by the file id
        cmd = "cd /data/pcap_save;tar cf - `cd /data/pcap_save;ls -l p*/* | awk '{print $9}'"
        if len(files_opt) > 0:
            files_opt = "|grep -E '" + files_opt + "'"  # |grep -E '^p0.*f410.*|^p1.*f2.*'
            cmd += files_opt
        cmd += '`'

    # for tar file name to be saved
    tar_file_name += '_download_at_' + time.strftime("%Y%m%d%H%M%S", time.localtime(time.time())) + '.tar'
    current_app.logger.info("cmd:%s,tar_file_name:%s" % (cmd, tar_file_name))

    # send operation log
    msg = {}
    msg['UserName'] = login_user
    msg['UserIP'] = login_ip
    msg['Operate'] = u'开始下载' + tar_file_name
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = 0
    send_log_db(MODULE_OPERATION, msg)

    g = proc.Group()
    child = g.run(["bash", "-c", cmd])

    def read_process():
        try:
            while g.is_pending():
                lines = g.readlines()
                for proc, line in lines:
                    time.sleep(0.00001)
                    yield line
            mv_download_pcap_process_count('-', 1)
            msg['Operate'] = tar_file_name + u'下载完成'
            send_log_db(MODULE_OPERATION, msg)
            current_app.logger.info('download %s over' % tar_file_name)
        except:
            msg['Operate'] = tar_file_name + u'下载失败(用户取消或网络异常)'
            msg['Result'] = 1
            send_log_db(MODULE_OPERATION, msg)
            current_app.logger.error('download %s except' % tar_file_name)
            current_app.logger.error(traceback.format_exc())
            child.kill()
            mv_download_pcap_process_count('-', 1)

    try:
        return Response(read_process(), 200, {'Content-Disposition': 'attachment;filename=' + tar_file_name})
    except:
        msg['Operate'] = tar_file_name + u'下载失败(用户取消或网络异常)'
        msg['Result'] = 1
        send_log_db(MODULE_OPERATION, msg)
        current_app.logger.error('download %s except' % tar_file_name)
        current_app.logger.error(traceback.format_exc())
        child.kill()
        mv_download_pcap_process_count('-', 1)


def test_ftp_server(host, username, password):
    ftp_ok = 1
    ftp = ftplib.FTP()
    try:
        ftp.connect(host, timeout=5)
    except:
        ftp_ok = 2  # ftp server is not available
        return ftp_ok

    try:
        data = ftp.login(username, password)
        ftp_ok = 1  # ftp server is ok
        ftp.quit()
    except:
        ftp_ok = 3  # user or passwd is wrong
        ftp.close()
    return ftp_ok


def pcap_export2ftp_thread_handler(login_user, login_ip, host, username, password, files_id):
    ftp = ftplib.FTP(host, username, password)
    db_proxy = DbProxy()
    fp = None
    status = 0
    sum_count = 0
    success_count = 0

    # send operation log
    msg = {}
    msg['UserName'] = login_user
    msg['UserIP'] = login_ip
    msg['Operate'] = u'开始向FTP服务器(' + username + u'@' + host + u')上传pcap数据包'
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = status
    send_log_db(MODULE_OPERATION, msg)

    for id in files_id.split(','):
        if len(id) <= 0:
            continue
        sql = 'select filename from pcap_info where id = %d' % int(id)
        result, rows = db_proxy.read_db(sql)
        for row in rows:
            if len(row) <= 0:
                continue;
            sum_count += 1
            file_name = row[0]
            file = '/data/pcap_save/' + file_name.split('_')[0] + '/' + file_name
            strerr = u'向FTP服务器(' + username + u'@' + host + u')上传' + file_name + u'失败'
            '''
            global current_upload_file
            global current_upload_file_size
            current_upload_file = file
            try:
                current_upload_file_size = os.path.getsize(file)
            except Exception, e:
                continue
            '''
            try:
                fp = open(file, 'rb')
            except:
                msg['Operate'] = strerr + u'(读取文件失败)'
                msg['Result'] = 1
                # send_log_db(MODULE_OPERATION, msg)
                continue

            try:
                # ftp.storbinary('STOR %s' % file_name, fp, callback=update_file_upload_to_ftp_process)
                ftp.storbinary('STOR %s' % file_name, fp)
            except:
                current_app.logger.info('upload %s failed.' % file_name)
                current_app.logger.error(traceback.format_exc())
                fp.close()
                msg['Operate'] = strerr + u'(FTP操作失败)'
                msg['Result'] = 1
                # send_log_db(MODULE_OPERATION, msg)
                continue
            fp.close()
            success_count += 1
    try:
        ftp.quit()
    except:
        current_app.logger.error(traceback.format_exc())

    if sum_count == success_count:
        msg['Operate'] = u'向FTP服务器(' + username + u'@' + host + u')上传pcap数据包完成'
        msg['Result'] = 0
    else:
        msg['Operate'] = u'向FTP服务器(' + username + u'@' + host + u')上传pcap数据包失败' + u'(请求' + str(
            sum_count) + u'个文件，' + str(sum_count - success_count) + u'个上传失败)'
        msg['Result'] = 1
    send_log_db(MODULE_OPERATION, msg)


# /testFtpServer?host=192.168.81.32&username=admin&password=12345678
@deviceinfo_page.route('/testFtpServer', methods=['GET', 'POST'])
@login_required
def mw_test_ftpserver():
    ret = {}
    if request.method == 'GET':
        host = request.args.get('host', '')
        username = request.args.get('username', '')
        password = request.args.get('password', '')
    elif request.method == 'POST':
        data = request.get_json()
        host = data['host']
        username = data['username']
        password = data['password']
    else:
        host = ''
        username = ''
        password = ''

    if len(host) == 0:
        ret['status'] = 0
        return jsonify(**ret)

    ret['status'] = 1
    ret['result'] = test_ftp_server(host, username, password)
    return jsonify(**ret)


current_upload_file = ''
current_upload_file_size = 0
sent_size = 0

'''no used, just for test the upload process'''


def update_file_upload_to_ftp_process(data):
    global file_size
    global sent_size
    sent_size += len(data)
    # print 'process:%.4f, %d, %d\n' % (sent_size/float(current_upload_file_size), sent_size, current_upload_file_size)


# /pcapExport2Ftp?host=192.168.81.32&username=admin&password=12345678&files=eth0_20161107110351_20161107110450_f3.pcap
@deviceinfo_page.route('/pcapExport2Ftp', methods=['GET', 'POST'])
@login_required
def mw_pcap_export2ftp():
    ret = {}

    login_user = None
    login_ip = get_oper_ip_info(request)
    if request.method == 'GET':
        host = request.args.get('host', '')
        username = request.args.get('username', '')
        password = request.args.get('password', '')
        files = request.args.get('files', '')
        login_user = request.args.get('loginuser', '')
        interface = request.args.get('interface', '')
        starttime = request.args.get('starttime', '')
        endtime = request.args.get('endtime', '')
        select_all = request.args.get('select_all', '0')
    elif request.method == 'POST':
        data = request.get_json()
        host = data.get('host', '')
        username = data.get('username', '')
        password = data.get('password', '')
        files = data.get('files', '')
        login_user = data.get('loginuser', '')
        interface = data.get('interface', '')
        starttime = data.get('starttime', '')
        endtime = data.get('endtime', '')
        select_all = data.get('select_all', '0')

    if len(host) == 0:
        ret['status'] = 0
        return jsonify(**ret)

    if len(username) <= 0:
        username = 'anonymous'

    if int(select_all) == 0 and len(files) == 0:
        ret['status'] = 1
        return jsonify(**ret)

    ret['status'] = 1
    test_ftp = test_ftp_server(host, username, password)

    if test_ftp != 1:
        ret['result'] = test_ftp
        return jsonify(**ret)

    if int(select_all) == 1:
        page = 0  # stand for all pages
        status, data, total, sum_size = mw_get_pcap_files(page, interface, starttime, endtime, files)
        if status == 1:
            files = ",".join(str(f[4]) for f in data)
    t = threading.Thread(target=pcap_export2ftp_thread_handler,
                         args=(login_user, login_ip, host, username, password, files))
    t.setDaemon(True)
    t.start()

    ret['result'] = 1
    return jsonify(**ret)


@deviceinfo_page.route('/getdbstatus', methods=['GET', 'POST'])
@login_required
def mw_get_db_status():
    status = 0
    disk_status = 0
    cur_status = 0
    disk_info = commands.getoutput("fdisk -l | awk '{print $1}'")
    disk_info = disk_info.split('\n')
    mount_info = commands.getoutput("mount -v | awk '{print $1}'")
    mount_info = mount_info.split('\n')
    if g_dpi_plat_type == DEV_PLT_X86:
        if '/dev/sda1' in disk_info and '/dev/sda2' in disk_info and '/dev/sda3' in disk_info:
            disk_status = 1
    else:
        if '/dev/mmcblk0p1' in disk_info and '/dev/mmcblk0p2' in disk_info and '/dev/mmcblk0p4' in disk_info and '/dev/mmcblk0p3' in disk_info:
            disk_status = 1

    if disk_status == 1:
        db_proxy = DbProxy()
        conn_status = db_proxy.get_connect_status()
        del db_proxy

        work_status = 1
        if os.path.exists("%s/mysql_check_error.flag" % DB_FLAG_PATH):
            work_status = 0

        if conn_status == 1 and work_status == 1:
            cur_status = 1
        else:
            cur_status = 0

    # 先判断数据库连接状态，再判断磁盘连接状态
    if cur_status == 0:
        status = 2
    if disk_status == 0:
        status = 3

    return jsonify({'status': status})


@deviceinfo_page.route('/getFunctionRunMode')
@login_required
def get_func_run_mode():
    '''
    funciton:get dpi run mode ips or ids
    Returns:status (0 is failed 1 success) mode(1 is ids,2 is ips)
    '''
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select mode from dpi_mode"
    # rows = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
    _, rows = db_proxy.read_db(sql_str)
    mode = 0
    if len(rows) == 0:
        return jsonify({'status': 0, 'runmode': mode})
    mode = rows[0][0]
    return jsonify({'status': 1, 'runmode': mode})


@deviceinfo_page.route('/setFuncRunMode', methods=['GET', 'POST'])
@login_required
def set_func_run_mode():
    '''
    funciton:set dpi run mode ips or ids, 1 is ids 2 is ips
    Returns:status (0 is failed 1 success)
    '''
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        run_mode = request.args.get('runmode', 0, type=int)
        loginuser = request.args.get('loginuser')
    else:
        post_data = request.get_json()
        run_mode = post_data['runmode']
        loginuser = post_data['loginuser']
    # send operation log
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'

    if run_mode == 1 or run_mode == 2:
        subprocess.call(['vtysh', '-c', 'config t', '-c', 'factory-reset'])
        time.sleep(1)
        sql_str = None
        proto_switch = None
        if run_mode == 1:
            subprocess.call(['vtysh', '-c', 'config t', '-c', 'dpi switch-mode ids'])
            time.sleep(5)
            sql_str = "update dpi_mode set mode=1"
            proto_switch = "update nsm_protoswitch set proto_bit_map=16777215"
            msg['Operate'] = "功能模式切换为:监测审计".decode("utf8")
        else:
            subprocess.call(['vtysh', '-c', 'config t', '-c', 'dpi switch-mode ips'])
            time.sleep(5)
            sql_str = "update dpi_mode set mode=2"
            proto_switch = "update nsm_protoswitch set proto_bit_map=0"
            msg['Operate'] = "功能模式切换为:智能保护".decode("utf8")
        try:
            commands.getoutput("rm -f /conf/db/devconfig.db")
            commands.getoutput("cp -f /conf/db/devconfig.db.bak /conf/db/devconfig.db")
            # init_sqlite()
            # rows = new_send_cmd(TYPE_APP_SOCKET, sql_str, 2)
            db_proxy.write_db(sql_str)
            db_proxy.write_db(proto_switch)
            # swithc_rows = new_send_cmd(TYPE_APP_SOCKET, proto_switch, 2)
            if run_mode == 1:
                subprocess.call(['vtysh', '-c', 'config t', '-c', 'dpi industry_protocol 16777215'])
            time.sleep(10)
            subprocess.call(['vtysh', '-c', 'config t', '-c', 'stop dpi'])
            time.sleep(5)
            msg['Result'] = '0'
            send_log_db(MODULE_OPERATION, msg)
            # mw_rebootdpi()
            time.sleep(2)
            os.system("/app/sbin/factory_reset_mysql.sh")
        except:
            current_app.logger.error('change func mode failed and Factory reset Failed')
            tb = traceback.format_exc()
            current_app.logger.error(tb)
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0})
    return jsonify({'status': 1})


@deviceinfo_page.route('/raidStauasRes', methods=['POST', 'GET'])
@login_required
def raid_status_res():
    '''
    funciton:get raid status
    '''
    sql_str = "select * from nsm_raidstatus"
    db_proxy = DbProxy(CONFIG_DB_NAME)
    res, sql_res = db_proxy.read_db(sql_str)
    if res != 0:
        return jsonify({'status': 0, "raidstatus1": [], "raidstatus2": []})

    return jsonify({'status': 1,
                    "raidstatus1": [sql_res[0][0], sql_res[0][1], sql_res[0][2]],
                    "raidstatus2": [sql_res[0][3], sql_res[0][4], sql_res[0][5]]})


# 发送消息到集中管理平台
@deviceinfo_page.route('/testCentreServerStatus', methods=['POST', 'GET'])
@login_required
def mw_centre_test_server():
    if request.method == 'GET':
        server_ip = request.args.get('ip', '')
        server_port = request.args.get('port', '')
    elif request.method == 'POST':
        data = request.get_json()
        server_ip = data['ip']
        server_port = data['port']
    else:
        server_ip = ''
        server_port = ''
    if len(server_ip) == 0 or len(server_port) == 0:
        return jsonify({'status': 0})
    try:
        ipaddress.ip_address(server_ip)
    except:
        return jsonify({'status': 0})

    try:
        if server_ip.find(':') < 0:
            cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cli_socket.connect((server_ip, int(server_port)))
        else:
            cli_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            cli_socket.connect((server_ip, int(server_port)))
    except:
        cli_socket.close()
        return jsonify({'status': 0})
    cli_socket.close()
    return jsonify({'status': 1})


@deviceinfo_page.route('/getCentreServerConfig', methods=['POST', 'GET'])
@login_required
def mw_centre_get_serverinfo():
    # connectstatus:连接状态 mwIp 服务器ip dhcp 服务器端口
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select connectstatus,mwIp,mwPort from managementmode"
    res = {}
    # rows = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
    _, rows = db_proxy.read_db(sql_str)
    res['status'] = rows[0][0]
    res['ip'] = rows[0][1]
    res['port'] = rows[0][2]
    return jsonify({'status': 1, 'res': res})


@deviceinfo_page.route('/connectCentreServer', methods=['POST', 'GET'])
@login_required
def mw_centre_connect_server():
    if request.method == 'GET':
        server_ip = request.args.get('ip', '')
        server_port = request.args.get('port', '')
        login_user = request.args.get('loginuser', '')
        con_status = request.args.get('status', 0, type=int)
    elif request.method == 'POST':
        data = request.get_json()
        server_ip = data['ip']
        server_port = data['port']
        login_user = data['loginuser']
        con_status = int(data['status'])
    else:
        server_ip = ''
        server_port = ''
        login_user = ''
        con_status = 0
    db_proxy = DbProxy(CONFIG_DB_NAME)
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = login_user
    msg['UserIP'] = userip
    msg['Operate'] = u"集中管理注册:ip:%s port:%s" % (server_ip, server_port)
    msg['ManageStyle'] = 'WEB'

    try:
        ipaddress.ip_address(server_ip)
    except:
        return jsonify({'status': 0})

    try:
        tmp_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        tmp_addr = '/data/sock/icsp_agent_sock'
        '''type = 0 is send plartform config'''
        tmp_msg = {"type": 0, "ip": server_ip, "port": int(server_port), "enable": con_status}
        data = json.dumps(tmp_msg)
        tmp_sock.sendto(data, tmp_addr)
    except:
        tmp_sock.close()
        current_app.logger.error(traceback.format_exc())
        return jsonify({'status': 0})
    tmp_str = "update managementmode set mwIp='%s',mwPort=%s,connectstatus=%d"%(server_ip, server_port, con_status)
    # 创建文件发送flag供中间件使用
    try:
        if con_status:
            os.system('touch /data/send_icspd.flag')
        else:
            if os.path.exists('/data/send_icspd.flag'):
                os.system('rm /data/send_icspd.flag')
    except:
        current_app.logger.error('set /data/send_icspd.flag error.')
    # new_send_cmd(TYPE_APP_SOCKET, tmp_str, 2)
    db_proxy.write_db(tmp_str)
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@deviceinfo_page.route('/getSyslogServerConfig', methods=['GET'])
@login_required
def get_syslog_server_config():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    try:
        sql_str = "select syslogIp, port, logSwitch from syslog_server"
        res = {}
        # rows = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
        _, rows = db_proxy.read_db(sql_str)
        res['ip'] = rows[0][0]
        res['port'] = rows[0][1]
        res['switch'] = rows[0][2]
        return jsonify({'status': 1, 'res': res})
    except:
        return jsonify({'status': 1, 'res': {'ip': '127.0.0.1', 'port': 514, 'switch': 0}})


@deviceinfo_page.route('/saveSyslogServerConfig', methods=['POST'])
@login_required
def save_syslog_server_config():
    if request.method == 'POST':
        data = request.get_json()
        server_ip = data['ip']
        server_port = int(data['port'])
        login_user = data['loginuser']
        con_status = int(data['status'])
    else:
        server_ip = ''
        server_port = 0
        login_user = ''
        con_status = 0
    db_proxy = DbProxy(CONFIG_DB_NAME)
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = login_user
    msg['UserIP'] = userip
    msg['Operate'] = u"syslog服务配置:ip:%s port:%s"%(server_ip, server_port)
    msg['ManageStyle'] = 'WEB'
    try:
        tmp_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    except:
        return jsonify({'status': 0})
    try:
        tmp_addr = '/data/sock/icsp_agent_sock'
        '''type = 1 is send syslog server config'''
        tmp_msg = {"type": 1, "ip": server_ip, "port": int(server_port), "enable": con_status}
        data = json.dumps(tmp_msg)
        tmp_sock.sendto(data, tmp_addr)
        if not con_status:
            tmp_sock.sendto("0", syslog_incident_ctl_addr)
            tmp_sock.sendto("0", syslog_traffic_incident_ctl_addr)
            # tmp_sock.sendto("6", dst_machine_learn_ctl_addr)
        else:
            tmp_sock.sendto("1", syslog_incident_ctl_addr)
            tmp_sock.sendto("1", syslog_traffic_incident_ctl_addr)
            # tmp_sock.sendto("7", dst_machine_learn_ctl_addr)
    except:
        current_app.logger.error(traceback.format_exc())
        tmp_sock.close()
        return jsonify({'status': 0})
    tmp_str = "update syslog_server set syslogIp='%s',port=%s,logSwitch=%d" % (server_ip, server_port, con_status)
    # new_send_cmd(TYPE_APP_SOCKET, tmp_str, 2)
    db_proxy.write_db(tmp_str)
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@deviceinfo_page.route('/debugInfo', methods=['GET'])
@login_required
def mw_debugInfo():
    if request.method == 'GET':
        loginuser = request.args.get('loginuser')
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserIP'] = userip
        msg['UserName'] = loginuser
        msg['ManageStyle'] = 'WEB'
        os.system('rm /data/debugInfo.tar.gz')
        os.system('mkdir /data/debugInfo')
        os.system('mkdir /data/debugInfo/python_log')
        os.system('mysqlhotcopy keystone_config /data/debugInfo')
        os.system('cp -r /data/log/engines/dpi /data/debugInfo')
        os.system('cp /data/log/{flask_db_socket.log,flask_engine.log*,flask_mw.log*,icspd.log,bati_error.log,owen_error.log} /data/debugInfo/python_log')
        os.system('tar -czvf /data/debugInfo.tar.gz /data/debugInfo')
        os.system('rm -r /data/debugInfo')
        msg['Operate'] = u"调试信息一键收集"
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return send_from_directory("/data/", "debugInfo.tar.gz", as_attachment=True)




@deviceinfo_page.route('/flow_switch', methods=['GET','POST'])
@login_required
def mw_flow_switch():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':   
        msg = {}
        loginuser = request.args.get('loginuser')
        userip = get_oper_ip_info(request)
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'      
        msg['UserName'] = loginuser
        get_sql='select flow_status from alarm_switch'
        result, rows = db_proxy.read_db(get_sql)
        action = rows[0][0]
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'action': action})
    if request.method == 'POST':
        msg = {}
        data = request.get_json()
        loginuser = data.get('loginuser','')
        userip = get_oper_ip_info(request)
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'
        msg['UserName'] = loginuser
        action = int(data.get('action'))
        try:
            sql="update alarm_switch set flow_status='%d'"%(action)
            current_app.logger.info(sql)
            db_proxy.write_db(sql)
            msg['Operate'] = u"流量告警设置"
            msg['Result'] = '0'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 1,"msg": u"流量告警设置成功"})
        except:
            msg['Operate'] = u"流量告警设置"
            msg['Result'] = '1'
            current_app.logger.error(traceback.format_exc())
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0,"msg": u"流量告警设置失败"})



@deviceinfo_page.route('/dev_checktime',methods=['GET','POST'])
@login_required
def mw_dev_checktime():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        msg = {}
        loginuser = request.args.get('loginuser')
        userip = get_oper_ip_info(request)
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'
        msg['UserName'] = loginuser
        get_sql = 'select check_time from top_config where id=1'
        result, rows = db_proxy.read_db(get_sql)
        check_time = rows[0][0]
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'check_time': check_time})
    if request.method == 'POST':
        msg = {}
        data = request.get_json()
        loginuser = data.get('loginuser','')
        userip = get_oper_ip_info(request)
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'
        msg['UserName'] = loginuser
        check_time = int(data.get('check_time'))
        try:
            if 1<=check_time<=60:
                sql="update top_config set check_time='%d' where id=1"%(check_time)
                db_proxy.write_db(sql)
                msg['Operate'] = u"资产告警周期设置"
                msg['Result'] = '0'
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({'status': 1,"msg": u"资产告警周期设置成功"})
            else:
                msg['Operate'] = u"资产告警周期设置"
                msg['Result'] = '0'
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({'status': 0,"msg": u"超出范围"})
        except:
            current_app.logger.error(traceback.format_exc())
            msg['Operate'] = u"资产告警周期设置"
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0,"msg": u"资产告警周期设置失败"})



@deviceinfo_page.route('/device_data_migration', methods=['GET', 'POST'])
@login_required
def mw_load_device_conf():
    status = 0
    db_proxy = DbProxy(CONFIG_DB_NAME)
    # work_mode, dpi_mode = get_hsfw_mode(db_proxy)
    if request.method == 'POST':
        sta_str = "select status from whiteliststudy where id=1"
        result, rows = db_proxy.read_db(sta_str)
        tmp_status = rows[0][0]
        username = request.form.get('loginuser', '')
        file = request.files['system_confexport_ConfImportMedia']  #接收sql文件
        if tmp_status == 1:
            return jsonify({'status': 0, 'msg': u'学习的时候无法导入配置'})
        if file and conf_update_allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = 'import_config.sql'
            # file_path = shutil.move(file,UPLOAD_FOLDER)
            file.save(os.path.join(UPLOAD_FOLDER, filename)) #将文件命名后保存到data/rules/路径下

            msg = {}
            userip = get_oper_ip_info(request)
            msg['UserName'] = username
            msg['UserIP'] = userip
            msg['Operate'] = u"导入配置文件"
            msg['ManageStyle'] = 'WEB'
            try:
                check_file = os.path.join(UPLOAD_FOLDER, filename)
                res = check_conf_file(check_file)  #验证文件版本是否匹配
                if res == -1:
                    status = 0
                    err_msg = "配置文件版本不匹配，导入失败"
                    msg['Result'] = '1'
                # elif res == -2:
                #     status = 0
                #     err_msg = "设备版本不一致，导入失败"
                #     msg['Result'] = '1'
                # elif res == -3:
                #     status = 0
                #     err_msg = "模式不匹配，请先切换防火墙模式，导入失败"
                #     msg['Result'] = '1'
                # elif res == -4:
                #     status = 0
                #     err_msg = "卡槽插卡情形不匹配，导入失败"
                #     msg['Result'] = '1'
                else:
                    # 文件头部加上用户名和ip
                    with open(UPLOAD_FOLDER + filename, 'r+') as f:
                        content = f.read()
                        f.seek(0, 0)
                        info_str = '-- info:%s;%s\n' % (userip, username)
                        f.write(info_str + content)
                    make_conf_file('/data/rules/import_config_bak.sql',db_proxy) #生成回滚文件
                    # current_app.logger.info('111')
                    msg['Result'] = '0'
                    status = 1
                    err_msg = "上传成功，正在重启"
                    # return jsonify({'status': status, 'msg': err_msg})
                    time.sleep(3)
                    commands.getoutput('reboot')

            except:
                status = 0
                msg['Result'] = '1'
                err_msg = '导入失败'
                current_app.logger.error(traceback.format_exc())
            if status != 1:
                commands.getoutput("rm -f /data/rules/conf*.sql")
                send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': status, 'msg': err_msg})
        else:
            err_msg = '文件格式不正确'
            return jsonify({'status': status, 'msg': err_msg})
    else:
        username = request.args.get('loginuser', '')
        now_time = time.strftime('%Y-%m-%d_%H:%M:%S')

        file_path = "/data/download/"
        file_name = "conf_%s.sql" % now_time
        filename = os.path.join(file_path,file_name)
        commands.getoutput("rm -f /data/download/conf*.sql")  #删除已有的sql文件
        try:
            make_conf_file(filename,db_proxy)     #生成sql文件
        except:
            return jsonify({'status': 0, 'msg': '生成配置文件出错，导出失败'})
        # send operation log
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserName'] = username
        msg['UserIP'] = userip
        msg['Operate'] = u"导出配置文件"
        msg['ManageStyle'] = 'WEB'
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return send_from_directory(file_path, file_name, as_attachment=True)



def check_conf_file(check_file):
    status = 0
    # sn_num = get_serial_num()[0:6]
    with open(check_file, 'r+') as f:
        ver_str = f.readline()
        # check device_version
        start_pos = ver_str.find("device_version:")
        if start_pos == -1:
            status = -1  # 没找到device_version
            return status
        start_pos += len('device_version:')
        end_pos = ver_str.find(" ", start_pos)
        ver = ver_str[start_pos:end_pos]
        if ver != g_ver_info:
            status = -2  # device_version不匹配
            return status


def make_conf_file(filename,db_proxy):
    '''
    tablename_tuple = ("addr_list_manage", "addr_group_manage", "service_info", "service_group_manage",
                       "packetfilter_rule", "packetfilter_config", "ipmaclist", "tb_static_route_config",
                       "sfw_working_mode", "attack_protect_config",
                       "interface_cfg", "snat_transform", "dnat_transform")
    cmd_str = "mysqldump -t keystone --tables addr_list_manage addr_group_manage service_info service_group_manage \
                        packetfilter_rule packetfilter_config ipmaclist tb_static_route_config sfw_working_mode \
                        attack_protect_config interface_cfg snat_transform \
                        dnat_transform -ukeystone -pOptValley@4312 > %s" % filename
    '''
    tablename_tuple = []
    # sn_num = get_serial_num()[0:6]
    _, rows = db_proxy.read_db('show tables')
    for r in rows:
        tablename_tuple.append(r[0])
        # current_app.logger.info(tablename_tuple)
    # cmd_str = "mysqldump -t keystone_config "\
    #           "--ignore-table=keystone_config.whiteliststudy"\
    #           "--ignore-table=keystone_config.license_info" \
    #           "--ignore-table=keystone_config.topshow "\
    #           "--ignore-table=keystone_config.ukey_auth "\
    #           "--ignore-table=keystone_config.pcap_down_status "\
    #           "-ukeystone -pOptValley@4312 > %s" % filename

    cmd_str = "mysqldump -t keystone_config --ignore-table=keystone_config.whiteliststudy --ignore-table=keystone_config.license_info --ignore-table=keystone_config.topshow --ignore-table=keystone_config.ukey_auth --ignore-table=keystone_config.pcap_down_status --default-character-set=utf8 -ukeystone -pOptValley@4312 >%s" % filename

    commands.getoutput(cmd_str)
    content_list = []
    append_str = "-- device_version:%s \n" % g_ver_info
    # append_str = "-- run_mode:%s \n" % dpi_mode
    content_list.append(append_str)
    # if sn_num == "HSFW03":
    #     slot_nic_pci = commands.getoutput('lspci -nn | grep Ethernet')
    #     slot_nic_md5 = hashlib.md5(slot_nic_pci.encode('utf8')).hexdigest()
    #     append_str = "-- slot_nic_md5:%s \n" % slot_nic_md5
    #     content_list.append(append_str)
    with open(filename, 'r+') as f:
        for line in f:
            for name in tablename_tuple:
                find_str = "LOCK TABLES `%s` WRITE;" % name

                pos = line.find(find_str)
                if pos >= 0:
                    append_str = "TRUNCATE TABLE %s;\n" % name

                    content_list.append(append_str)
            content_list.append(line)
    with open(filename, 'w+') as f:
        f.writelines(content_list)