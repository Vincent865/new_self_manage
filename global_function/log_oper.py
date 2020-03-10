#!/usr/bin/python
# -*- coding:UTF-8 -*-
import datetime
import socket
from global_var import *
import logging
import threading
import shlex
import time

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
'''
author: wuxx
function point:
1. support the API interface to send log(operation log and system log) and save db.
'''
logger = logging.getLogger('flask_mw_log')

LOG_EMERG = 0
LOG_ALERT = 1
LOG_CRIT = 2
LOG_ERR = 3
LOG_WARNING = 4
LOG_NOTICE = 5
LOG_INFO = 6
LOG_DEBUG = 7


MODULE_OPERATION = 25
MODULE_SYSTEM = 26


DEVICE_TYPE = 1
IFSTATUS_TYPE = 2
SYSTEM_TYPE = 3
SERVICE_TYPE = 4
BYPASSSTATUS_TYPE = 5

TYPE_MANAGEMENT_LOG = 0
TYPE_SYSTEM_LOG = 1
TYPE_SECURITY_LOG = 3

SUBTYPE_MANAGEMENT_LOGIN_SUCCESS = 1
SUBTYPE_MANAGEMENT_LOGOUT = 2
SUBTYPE_MANAGEMENT_LOGIN_FAILED = 3
SUBTYPE_MANAGEMENT_EDIT_RULE = 4

SUBTYPE_SYSTEM_CPU_USAGE = 1
SUBTYPE_SYSTEM_MEM_USAGE = 2
SUBTYPE_SYSTEM_ETH_LINKDOWN = 7
SUBTYPE_SYSTEM_ETH_LINKUP = 8


SUBTYPE_SECURITY_ACCESS = 1
SUBTYPE_SECURITY_ATTACK_WARING = 2

logserver_addr = '/data/sock/fw_log_agent_sock'
logserver_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)


# LOG_GB31992_STR = '<%d> %s panguOS FW %d %d %s'
LOG_GB31992_STR = '<{}> {} panguOS AD {} {} {}'
LOGIN_CONTENT = '%s %s'


ALARM_SRC_DICT = {"1": u"白名单", "2": u"黑名单", "3": u"IP/MAC", "4": u"流量告警", "5": u"MAC过滤", "6": u"资产告警", "7":U"不合规报文告警"}
CONTENT_DICT = {"content_list": Queue.Queue(maxsize=10000), "content_traffic_list": Queue.Queue(maxsize=10000)}

if g_dpi_plat_type == DEV_PLT_X86:
    OPER_LOG_MAX_NUM = 50000000
else:
    OPER_LOG_MAX_NUM = 50000

SYS_LOG_MAX_NUM = 30000


def send_log_db(logtype, msg):
    '''
    send_log_db function is send log msg to store db
    logtype: log type of the log message belong to MODULE_OPERATION or MODULE_SYSTEM
    msg: log msg detail content
    '''

    db_proxy = DbProxy()

    nowtime = datetime.datetime.now()
    nowTimeNyr = nowtime.strftime("%Y-%m-%d") + "T" + nowtime.strftime("%H:%M:%S") + "Z"

    if(logtype == MODULE_OPERATION):
        '''
            Msg = {"UserIP":"192.168.81.16", "UserName": "admin", "Operate": "show interface ",
                        "ManageStyle": "console", "Result": 0}
        '''
        try:
            result,count_db = db_proxy.read_db("select count(*) from operationlogs")
            for row in count_db:
                num_event = row[0]
            if num_event >= OPER_LOG_MAX_NUM:
                result,op_db = db_proxy.read_db("select min(operationLogId) from  operationlogs")
                for log_id in op_db:
                    message_id = log_id[0]
                result = db_proxy.write_db("delete from operationlogs where operationLogId in (select operationLogId from operationlogs limit 0,1)")
                result = db_proxy.write_db("delete from dpiuseroperationlogs where operationLogId ="+str(message_id))

            user_ip = msg['UserIP'].encode('utf-8')
            user_name = msg['UserName'].encode('utf-8')
            user_operate = msg['Operate'].encode('utf-8')
            operlog_cmd = "insert into operationlogs (user_ip,user) values ('%s','%s')"%(user_ip, user_name)
            result = db_proxy.write_db(operlog_cmd)
            result,operation_id_db = db_proxy.read_db("select max(operationLogId) from  operationlogs")
            for operation in operation_id_db:
                operation_id = operation[0]
            loginlog_cmd = "insert into dpiuseroperationlogs (operationLogId,oper,oper_result,timestamp) values (%s,'%s','%s','%s')"%(operation_id, user_operate, msg['Result'], nowTimeNyr)
            result = db_proxy.write_db(loginlog_cmd)
            try:
                logger.info('enter send_center_msg of MODULE_OPERATION about log_oper')
                if int(msg['Result']) == 0:
                    res = '成功'
                else:
                    res = '失败'
                content = "{}--{}--{}--{}{}".format(msg['UserName'], msg['ManageStyle'], msg['UserIP'], msg['Operate'], res)
                # logger.info(content)
                args = (1, 2, content)
                send_center_msg(logger, *args)
            except:
                logger.error(traceback.format_exc())
                logger.error("send_log_center error...")
            logger.info("operation log, msg:" + loginlog_cmd)
        except Exception:
            logger.error(traceback.format_exc())
    elif (logtype == MODULE_SYSTEM):
        '''
            Msg = {"Type": IFSTATUS_EVENT, "LogLevel": LOG_WARNING, "Content": "interface bvi123 linkup"}
        '''
        try:
            result,rows = db_proxy.read_db("select count(*) from events")
            for row in rows:
                num_event = row[0]
            if num_event >= SYS_LOG_MAX_NUM:
                result = db_proxy.write_db("delete from events where eventId  in (select eventId from events limit 0,1000)")
            content = msg['Content'].encode('utf-8')
            sql_str="INSERT INTO events (type,timestamp,content,level,status, componetName)VALUES (" \
                    "%d,'%s','%s',%d,0,'%s')"%(msg['Type'], nowTimeNyr, content, msg['LogLevel'], msg['Componet'])
            result = db_proxy.write_db(sql_str)
            try:
                logger.info('enter send_center_msg of SYSTEM_TYPE about log_oper')
                args = (msg['Type'], 1, content)
                send_center_msg(logger, *args)
            except:
                logger.error(traceback.format_exc())
                logger.error("send_log_center error...")
            logger.info("system log, msg:" + sql_str)
        except Exception:
            logger.error(traceback.print_exc())


def get_log_switch():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    try:
        sql_str = "select syslogIp, port, logSwitch from syslog_server"
        # rows = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
        _, rows = db_proxy.read_db(sql_str)
        switch = int(rows[0][2])
    except:
        switch = 0
        logger.error("get log_switch error")
    SYSLOG_UPLOAD["status"] = switch
    return switch


class SendIncident(threading.Thread):
    def __init__(self):
        super(SendIncident, self).__init__()

    @staticmethod
    def send_incident_to_icsp(content):
        try:
            logserver_sock.sendto(content, logserver_addr)
        except:
            logger.error(traceback.format_exc())

    def run(self):
        i = 0
        while True:
            try:
                log = CONTENT_DICT["content_list"].get(timeout=3)
                if log:
                    SendIncident.send_incident_to_icsp(log)
                    i += 1
                    if i >= 200:
                        time.sleep(0.1)
                        i = 0
            except:
                logger.error(traceback.format_exc())
                time.sleep(3)


class StatusSwitch(threading.Thread):
    def __init__(self):
        super(StatusSwitch, self).__init__()
        get_log_switch()
        logger = logging.getLogger('flask_db_socket_log')
        self.logger = logger

    def run(self):
        try:
            if os.path.exists(syslog_incident_ctl_addr):
                os.remove(syslog_incident_ctl_addr)
        except:
            self.logger.error("syslog_incident_ctl_addr file not exist")
        get_log_switch()
        incident_ctl_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        incident_ctl_sock.bind(syslog_incident_ctl_addr)
        while True:
            try:
                self.logger.info("syslog_incident_ctl_addr recieve start...")
                data, addr = incident_ctl_sock.recvfrom(4096)
            except:
                data = None
                self.logger.info("syslog_incident_ctl_addr rcv msg %s" % data)
            if data != None:
                try:
                    str_list = data.split(",", 1)
                    if str_list[0] == "0":
                        SYSLOG_UPLOAD["status"] = False
                    if str_list[0] == "1":
                        SYSLOG_UPLOAD["status"] = True
                except:
                    self.logger.error(traceback.format_exc())
                    self.logger.error("syslog_incident_ctl_addr send incident error.")
            else:
                self.logger.info("syslog_incident_ctl_addr recv data is none.")


class SendTrafficIncident(threading.Thread):
    def __init__(self):
        super(SendTrafficIncident, self).__init__()

    @staticmethod
    def send_incident_to_icsp(content):
        try:
            logserver_sock.sendto(content, logserver_addr)
        except:
            logger.error(traceback.format_exc())

    def run(self):
        i = 0
        while True:
            try:
                log = CONTENT_DICT["content_traffic_list"].get(timeout=3)
                if log:
                    SendTrafficIncident.send_incident_to_icsp(log)
                    i += 1
                    if i >= 200:
                        time.sleep(0.1)
                        i = 0
            except:
                # logger.error(traceback.format_exc())
                time.sleep(3)


class TrafficStatusSwitch(threading.Thread):
    def __init__(self):
        super(TrafficStatusSwitch, self).__init__()
        get_log_switch()

    def run(self):
        try:
            if os.path.exists(syslog_traffic_incident_ctl_addr):
                os.remove(syslog_traffic_incident_ctl_addr)
        except:
            logging.error("syslog_traffic_incident_ctl_addr file not exist")
        incident_ctl_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        incident_ctl_sock.bind(syslog_traffic_incident_ctl_addr)
        while True:
            try:
                data, addr = incident_ctl_sock.recvfrom(4096)
            except:
                data = None
            logger.info("syslog_traffic_incident_ctl_addr rcv msg %s" % data)
            if data != None:
                try:
                    str_list = data.split(",", 1)
                    if str_list[0] == "0":
                        SYSLOG_UPLOAD["status"] = False
                    if str_list[0] == "1":
                        SYSLOG_UPLOAD["status"] = True
                except:
                    logger.error(traceback.format_exc())
                    logger.error("syslog_traffic_incident_ctl_addr send incident error.")
            else:
                logger.info("syslog_traffic_incident_ctl_addr recv data is none.")


def handle_info(sql_str, type_content):
    """
    定义函数处理由dpi发送过来的sql语句,对其进行日志格式化处理并存放到队列中
    :param sql_str: 接收到的关于安全事件的sql语句
    :param type_content: 日志对应的队列
    :return:
    """
    try:
        # logger.info(sql_str)
        index = sql_str.find('values')
        info_str = sql_str[index+6:]
        info_str = info_str.strip().lstrip('(').rstrip(')').replace(' ', '').replace('\n', '')
        # logger.info(info_str)
        tmp_str = shlex.shlex(info_str, posix=True)
        tmp_str.whitespace = ','
        tmp_str.escape = '.'
        tmp_str.whitesapce_split = True
        info_list = list(tmp_str)
        # logger.info(info_list)
        if info_list:
            try:
                sip = info_list[16] if info_list[16] else u'NA'
                dip = info_list[17] if info_list[17] else u'NA'
                if type_content == "content_list":
                    timestamp = info_list[11]
                    s_name = info_list[18]
                    sname = ALARM_SRC_DICT[s_name]
                    try:
                        sport = info_list[21] if int(info_list[21]) else u'NA'
                        dport = info_list[22] if int(info_list[22]) else u'NA'
                    except:
                        sport = u"NA"
                        dport = u"NA"
                elif type_content == "content_traffic_list":
                    timestamp = info_list[0]
                    s_name = info_list[5]
                    sname = ALARM_SRC_DICT[s_name]
                    sport = u"NA"
                    dport = u"NA"
                # if sip and dip and int(sport) and int(dport):
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(timestamp)))
                send_content = "%s %s %s %s %s" % (sname, sip, sport, dip, dport)
                # send2content = LOG_GB31992_STR(LOG_ALERT, str(timestamp), TYPE_MANAGEMENT_LOG, str(send_content))
                send2content = LOG_GB31992_STR.format(LOG_ALERT, str(timestamp), TYPE_SECURITY_LOG, SUBTYPE_SECURITY_ACCESS, str(send_content))
                logger.info(send2content)
                if not CONTENT_DICT[type_content].full():
                    CONTENT_DICT[type_content].put(send2content)
            except:
                logger.error(traceback.format_exc())
                logger.error("handle incdents sql info error.")
    except:
        logger.error(traceback.format_exc())
        logger.error("get incdents sql info error.")


def send_login_success_to_icsp(content):
    nowtime = datetime.datetime.now()
    nowTimeNyr = nowtime.strftime("%Y-%m-%d") + " " + nowtime.strftime("%H:%M:%S")
    log = LOG_GB31992_STR.format(LOG_NOTICE, nowTimeNyr, TYPE_MANAGEMENT_LOG, SUBTYPE_MANAGEMENT_LOGIN_SUCCESS, content)
    try:
        logserver_sock.sendto(log, logserver_addr)
    except:
        logging.error(traceback.print_exc())


def send_logout_to_icsp(content):
    nowtime = datetime.datetime.now()
    nowTimeNyr = nowtime.strftime("%Y-%m-%d") + " " + nowtime.strftime("%H:%M:%S")
    log = LOG_GB31992_STR.format(LOG_NOTICE, nowTimeNyr, TYPE_MANAGEMENT_LOG, SUBTYPE_MANAGEMENT_LOGOUT, content)
    try:
        logserver_sock.sendto(log, logserver_addr)
    except:
        logging.error(traceback.print_exc())


def send_login_failed_to_icsp(content):
    nowtime = datetime.datetime.now()
    nowTimeNyr = nowtime.strftime("%Y-%m-%d") + " " + nowtime.strftime("%H:%M:%S")
    log = LOG_GB31992_STR.format(LOG_WARNING, nowTimeNyr, TYPE_MANAGEMENT_LOG, SUBTYPE_MANAGEMENT_LOGIN_FAILED, content)
    try:
        logserver_sock.sendto(log, logserver_addr)
    except:
        logging.error(traceback.print_exc())


def send_operate_rules_to_icsp(content):
    nowtime = datetime.datetime.now()
    nowTimeNyr = nowtime.strftime("%Y-%m-%d") + " " + nowtime.strftime("%H:%M:%S")
    log = LOG_GB31992_STR.format(LOG_WARNING, nowTimeNyr, TYPE_MANAGEMENT_LOG, SUBTYPE_MANAGEMENT_EDIT_RULE, content)
    try:
        logserver_sock.sendto(log, logserver_addr)
    except:
        logging.error(traceback.print_exc())


def send_cpu_usage_to_icsp(content):
    nowtime = datetime.datetime.now()
    nowTimeNyr = nowtime.strftime("%Y-%m-%d") + " " + nowtime.strftime("%H:%M:%S")
    log = LOG_GB31992_STR.format(LOG_NOTICE, nowTimeNyr, TYPE_SYSTEM_LOG, SUBTYPE_SYSTEM_CPU_USAGE, content)
    try:
        logserver_sock.sendto(log, logserver_addr)
    except:
        logging.error(traceback.print_exc())


def send_mem_usage_to_icsp(content):
    nowtime = datetime.datetime.now()
    nowTimeNyr = nowtime.strftime("%Y-%m-%d") + " " + nowtime.strftime("%H:%M:%S")
    log = LOG_GB31992_STR.format(LOG_NOTICE, nowTimeNyr, TYPE_SYSTEM_LOG, SUBTYPE_SYSTEM_MEM_USAGE, content)
    try:
        logserver_sock.sendto(log, logserver_addr)
    except:
        logging.error(traceback.print_exc())


def send_eth_down_to_icsp(content):
    nowtime = datetime.datetime.now()
    nowTimeNyr = nowtime.strftime("%Y-%m-%d") + " " + nowtime.strftime("%H:%M:%S")
    if 'down' in content:
        log = LOG_GB31992_STR.format(LOG_WARNING, nowTimeNyr, TYPE_SYSTEM_LOG, SUBTYPE_SYSTEM_ETH_LINKDOWN, content)
    else:
        logging.error(content)
        return
    try:
        logserver_sock.sendto(log, logserver_addr)
    except:
        logging.error(traceback.print_exc())


def send_eth_up_to_icsp(content):
    nowtime = datetime.datetime.now()
    nowTimeNyr = nowtime.strftime("%Y-%m-%d") + " " + nowtime.strftime("%H:%M:%S")
    if 'up' in content:
        log = LOG_GB31992_STR.format(LOG_WARNING, nowTimeNyr, TYPE_SYSTEM_LOG, SUBTYPE_SYSTEM_ETH_LINKUP,content)
    else:
        logging.error(content)
        return
    try:
        logserver_sock.sendto(log, logserver_addr)
    except:
        logging.error(traceback.print_exc())
