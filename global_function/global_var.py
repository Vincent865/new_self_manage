#!/usr/bin/python
#-*- coding:utf-8 -*-
import io
import os
import sys
import time
import sqlite3
import cStringIO
import codecs
import csv
import socket
import json
import logging
import traceback
import subprocess
import re
import MySQLdb
import struct
import commands
import Queue
import fcntl
#flask-login
from flask_login.mixins import UserMixin
from collections import OrderedDict
#add dist_package_path and check
dist_package_path = "/app/local/lib/python2.7/dist-packages"
if dist_package_path not in sys.path:
    sys.path.append(dist_package_path)
from device_info import webdpi
ACTION_LIST = ['pass','alert','drop']

logger = logging.getLogger('flask_mw_log')

g_app_sock=None
g_event_sock=None

DEV_PLT_X86 = 1
DEV_PLT_MIPS = 2

dev_plt_type_dict = {
    "KEC-C400" : DEV_PLT_MIPS,
    "KEA-C200" : DEV_PLT_MIPS,
    "KEA-C400" : DEV_PLT_MIPS,
    "KEA-U1000" : DEV_PLT_X86,
    "IMAP" : DEV_PLT_X86
}

def get_serial_num():
    command = "get_eeprom read all"
    handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    
    serialnum = ''
    for line in handle.stdout.readlines():
        if 'serialnum' in line:
            line = line.strip()
            pattern_serialNum  = re.compile('serialnum\s+:\s(.*)')
            serialnumList      = re.findall(pattern_serialNum,line)
    
            if serialnumList:
                serialnum = serialnumList[0]
                break
    
    return serialnum

def get_dev_type():
    sn_num =  get_serial_num()[0:6]
    product_dict = {"JA0301": "KEA-U1000",
                    #"JA0302": "KEA-U1000E",
                    #"JA0401": "KEA-U2000",
                    "IMAP01": "IMAP",
                    #"SS0101": "KEC-U1000",
                    #"SS0301": "KEC-U2000",
                    "JC0102": "KEA-C200",
                    "SS0202": "KEC-C400",
                    # 以下产品处于逐步淘汰中，因设备有限，便于调试添加
                    "JC0101": "KEA-C200",
                    "JS0201": "KEA-C400",
                    }

    if sn_num in product_dict:
        return product_dict[sn_num]
    else:
        return "UNKOWN"

g_dpi_plat_type = 0
g_dev_type = ''
def init_dpi_type_info():
    global g_dev_type
    global g_dpi_plat_type
    if len(g_dev_type) <= 0:
        g_dev_type = get_dev_type()
    if g_dev_type in dev_plt_type_dict:
        g_dpi_plat_type = dev_plt_type_dict[g_dev_type]
    else:
        g_dpi_plat_type = DEV_PLT_X86
    return


def get_hw_type():
    command = "get_hw_type read all"
    handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    hw_type = handle.stdout.readline().strip()
    logger.info("get_hw_type ==============" + str(hw_type))
    # hw_type = ''
    # for line in handle.stdout.readlines():
    #     if 'serialnum' in line:
    #         line=line.strip()
    #         pattern_serialNum=re.compile('serialnum\s+:\s(.*)')
    #         serialnumList=re.findall(pattern_serialNum, line)
    #
    #         if serialnumList:
    #             serialnum=serialnumList[0]
    #             break
    #
    # return serialnum
    return str(hw_type)


g_hw_type = ""
def init_hw_type_info():
    global g_hw_type
    if len(g_hw_type) <= 0:
        g_hw_type = get_hw_type()
    return


def get_dpi_type_info():
    global g_dev_type
    global g_dpi_plat_type
    return g_dev_type, g_dpi_plat_type

def get_hw_type_info():
    global g_hw_type
    return g_hw_type

def get_oper_ip_info(request_info):
    global g_dev_type
    global g_dpi_plat_type
    if g_dpi_plat_type == DEV_PLT_X86:
        userip = request_info.remote_addr
    else:
        userip = request_info.headers.get('X-Real-Ip', request_info.remote_addr)
    return userip

init_dpi_type_info()
g_dev_type, g_dpi_plat_type = get_dpi_type_info()

init_hw_type_info()
g_hw_type = get_hw_type_info()

if g_dpi_plat_type == DEV_PLT_X86:
    SQLITE_PATH = "/conf/db/devconfig.db"
    MACDICT_PATH = "/conf/db/mac_name.txt"
    APP_PY_PATH = "/app/local/share/new_self_manage/app"
    CROND_PATH = "/app/local/cron/crontabs/root"
    CROND_CONF = "/app/local/cron/crontabs"

    # 达到规格后，一次删除条目数限制
    del_limit = {"incident": 10*10000, "protocol": 10*10000, "traffic": 10*10000}
    # 队列大小限制
    queue_limit = {"whitelistStudy": 10000, "protAudit": 2*10000, "unknownDevice": 500, "ipTraffic": 5000, "devAutoIdentify": 6000}
    if g_dev_type == "IMAP":
        queue_limit.update({"complex_tbl": 10000})
        db_record_limit = {"device": 1000, "whitelist": 10000, "incident": 2000 * 10000, "protocol": 2000 * 10000,
                           "traffic": 2000 * 10000}
    elif g_dev_type == "KEA-U1000":
        queue_limit.update({"complex_tbl": 2*10000})
        db_record_limit = {"device": 3000, "whitelist": 5*10000, "incident": 5000 * 10000, "protocol": 5000 * 10000,
                           "traffic": 5000 * 10000}
else:
    SQLITE_PATH = "/data/db/devconfig.db"
    MACDICT_PATH = "/data/db/mac_name.txt" 
    APP_PY_PATH = "/usr/local/share/new_self_manage/app"
    CROND_PATH = "/usr/local/etc/cron/crontabs/root"
    CROND_CONF = "/usr/local/etc/cron/crontabs"

    # 达到规格后，一次删除条目数限制
    del_limit = {"incident": 5000, "protocol": 10000, "traffic": 10000}
    # 队列大小限制
    queue_limit = {"whitelistStudy": 5000, "protAudit": 6000, "unknownDevice": 200, "ipTraffic": 1000, "complex_tbl": 2000, "devAutoIdentify": 6000}
    # 数据库各表条目数限制
    db_record_limit = {"device": 200, "whitelist": 5000, "incident": 5 * 10000, "protocol": 10 * 10000, "traffic": 10 * 10000}
# for whitelist study, to support clear out by web command, so pop it as global variable
deviceinfo_list = {}
macfilter_list = []
whitelist_info = []
top_list = []
ipmac_list = []

FLOW_LEARN_FLAG = 0

dev_band_threshold_info = {}

class band_sample_info:
    def __init__(self):
        self.sample_num = 0
        self.sample_detail = []
        self.sample_info = {}

flow_band_sample = band_sample_info()

class ClientInfo:
    def __init__(self):
        self.sqlstr = ''
        self.addr = 10

protocol_names = (
    'dnp3',
    'enipio',
    'eniptcp',
    'enipudp',
    'ftp',
    'goose',
    'http',
    'iec104',
    'mms',
    'modbus',
    'opcda',
    'opcua',
    'pnrtdcp',
    'pop3',
    'profinetio',
    's7',
    'smtp',
    'snmp',
    'sv',
    'telnet',
    'oracle',
    'focas',
    'sip',
    'sqlserver',
    's7plus'
)

AUDIT_SEG_LIST = (
    ['功能码'],
    ['地址类型', '数据类型'],
    ['命令' , '服务码' , '地址类型' , '数据类型'],
    ['命令'],
    ['使用账号', '输入命令'],
    ['数据集', 'GO标识符'],
    ['目标URL'],
    ['Causetx类型', 'Asdu类型'],
    ['PDU类型', '服务请求类型'],
    ['功能码', '起始地址', '结束地址'],
    ['操作接口', '操作码'],
    ['服务码'],
    ['frame标识符', '服务标识符', '服务类型' , '选项' , '子选项'],
    ['源信箱地址', '目的信箱地址','信箱主题'],
    ['功能码', '操作接口', '数据类型'],
    ['PDU类型', '操作类型', '数据类型', '地址', '数值'],
    ['源信箱地址', '目的信箱地址','信箱主题'],
    ['PDU类型', '版本' , '团体名'],
    ['sv编号', '采样同步'],
    ['使用账号', '输入命令'],
    ['sql操作', '用户名称', 'sql语句'],
    ['操作命令', '类型', '功能键', '功能码'],
    ['方法名字', '命令', '类型', '命令类型', '命令模式', '命令字', '命令参数1', '命令参数2', '存储方式', '动作类型', '持续时间'],
    ['操作类型', '执行结果', 'SQL语句', '查询行数', '用户名', '主机名'],
    ['操作码', '功能码']
    )

AUDIT_SEG_DICT = dict(zip(protocol_names,AUDIT_SEG_LIST))

flow_tables = [protocol_names[i]+"flowdatas" for i in range(len(protocol_names))]
flow_tables_1 = [protocol_names[i]+"bhvAduitdatas" for i in range(len(protocol_names))]
tables_name = flow_tables + flow_tables_1 + ['incidents', 'icdevicetraffics', 'cusprotoflowdatas']

protocol_columns = (
    'func',  # dnp3flowdatas
    'addressType,dataType', # enipioflowdatas
    'command,serviceName,addressType,dataType', # eniptcpflowdatas
    'command', # enipudpflowdatas
    'accountName,command',  # ftpflowdatas
    'goId,datSet', # gooseflowdatas
    'url', # httpflowdatas
    'asduType,causetxType', # iec104flowdatas
    'pduType,serviceRequest', # mmsflowdatas
    'func,startAddr,endAddr', # modbusflowdatas
    'opInt,opCode', # opcdaflowdatas
    'serviceId', # opcuaflowdatas
    'frameid,serviceid,servicetype,dcpoption,dcpsuboption', # pnrtdcpflowdatas
    'souceMailAddress,destMailAddress,MailTitle', # pop3flowdatas
    'func,opInt,dataType', # profinetioflowdatas
    'pduType,dataType,opType,area,dataInfo', # s7flowdatas
    'souceMailAddress,destMailAddress,MailTitle', # smtpflowdatas
    'pduType,version,community', # snmpflowdatas
    'svID,smpSynch', # svflowdatas
    'accountName,command', # telnetflowdatas
    'operType,sqlstr,clientuser', # oracleflowdatas
    'cmd,type,function_key,func', # focasflowdatas
    'method,Command,Type,CmdType,CmdMode,CmdId,CmdParam1,CmdParam2,StoreType,ActionType,Duration',  # sipflowdatas
    'operType,operResult,sqlstr,rownums,username,hostname', # sqlserverflowdatas
    'opCode,funcCode' # s7plusflowdatas
)

PROTO_NAME_MAPPING = {
    "pnio" : "DCE-RPC-UDP",
    "modbus" : "Modbus-TCP",
    "dnp3" : "DNP3",
    "iec104" : "IEC104",
    "mms" : "MMS",
    "opcua" : "OPCUA-TCP",
    "opcda" : "OPCDA",
    "profinetio" : "PROFINET-IO",
    "eniptcp" : "ENIP-TCP",
    "snmp" : "SNMP",
    "enipudp" : "ENIP-UDP",
    "s7" : "S7",
    "s7plus" : "S7-PLUS",
    "enipio" : "ENIP-IO",
    "hexagon" : "Hexagon",
    "goose" : "GOOSE",
    "sv" : "SV",
    "pnrtdcp" : "PNRT-DCP",
    "focas" : "FOCAS",
    "bacnet" : "BACnet",
    "sqlserver" : "SQL-Server",
    "sip" : "SIP",
    "oracle" : "ORACLE",
    "http" : "HTTP",
    "https" : "HTTPS",
    "ftp" : "FTP",
    "pop3" : "POP3",
    "smtp" : "SMTP",
    "telnet" : "Telnet",
    "opcua_tcp" : "OPCUA-TCP"
}


def get_ui_proto_name(inner_name):
    try:
        name = PROTO_NAME_MAPPING[inner_name]
    except:
        name = inner_name
    return name

def mw_get_interface_map():
    global g_dev_type
    global g_hw_type
    ok = 1
    map = None
    if len(g_dev_type) <= 0:
        g_dev_type = get_dev_type()

    # if g_dev_type == "IMAP":
    if g_hw_type == "0":
        map = OrderedDict([('ETH1', 'eth1'), ('ETH2', 'eth2'), ('ETH3', 'eth3')])
    elif g_hw_type == "1":
        map=OrderedDict([('ETH1', 'eth1'), ('ETH2', 'eth2'), ('ETH3', 'eth3'), ('ETH4', 'eth4'), ('ETH5', 'eth5')])
    elif g_dev_type == "KEA-U1000":
        map = OrderedDict([('p0', 'eth1'), ('p1', 'eth2')])
    elif g_dev_type == "KEA-C200":
        map = OrderedDict([('p0', 'eth0'), ('p1', 'eth1')])
    else:
        ok = 0
    return ok, map
    
def init_device_size_info():
    global DEVICE_DISK_SIZE
    global DEVICE_MEM_SIZE
    sn_num =  get_serial_num()
    if sn_num[0:6] == "JA0301":
        DEVICE_DISK_SIZE = 1000
        DEVICE_MEM_SIZE = 16
    elif sn_num[0:6] == "IMAP01":
        DEVICE_DISK_SIZE = 500
        DEVICE_MEM_SIZE = 8
    elif sn_num[0:6] == "SS0101":
        DEVICE_DISK_SIZE = 1000
        DEVICE_MEM_SIZE = 16
    else:
        DEVICE_DISK_SIZE = 1000
        DEVICE_MEM_SIZE = 16
    return DEVICE_MEM_SIZE,DEVICE_DISK_SIZE

QUEUE_MAX_SIZE = queue_limit["complex_tbl"]

dict_table_list = dict(zip(tables_name, [Queue.Queue(maxsize=QUEUE_MAX_SIZE) for i in range(len(tables_name))]))

def SqlQueueIn(table_name, sql):
    global dict_table_list
    if dict_table_list.has_key(table_name):
        info = ClientInfo()
        info.sqlstr = sql
        write_cmd_list = dict_table_list[table_name]
        if write_cmd_list.full():
            return
        write_cmd_list.put(info)

webDpi=None
UPLOAD_FOLDER = '/data/rules/'
UPDATE_FOLDER= '/app/upgrade_tmp/'
VENDOR_UPLOAD_FOLDER = '/data/vendorinfo/'
app_sock_addr='/tmp/sock/db_app_sock'
event_sock_addr = '/tmp/sock/db_event_sock'
remote_read_addr='/data/sock/db_read_sock'
remote_file_addr='/data/sock/db_file_sock'
remote_deploy_addr='/data/sock/db_deploy_sock'

src_machine_learn_ctl_addr = '/data/sock/src_machine_learn_ctl_addr'
dst_machine_learn_ctl_addr = '/data/sock/dst_machine_learn_ctl_addr'

# 系统日志上报使用的地址和变量
SYSLOG_UPLOAD = {"status": False}
syslog_incident_ctl_addr = '/data/sock/syslog_incident_ctl_addr'
syslog_traffic_incident_ctl_addr = '/data/sock/syslog_traffic_incident_ctl_addr'

if g_dpi_plat_type == DEV_PLT_MIPS:
    app_sock_addr='/data/sock/db_app_sock'
    event_sock_addr = '/data/sock/db_event_sock'
    UPDATE_FOLDER= '/boot/'

macdict={}

TYPE_APP_SOCKET = 1
TYPE_EVENT_SOCKET = 8
CONFIG_DB_NAME = 'keystone_config'


#mw_sock_addr='/data/sock/db_client_sock'
#logger = logging.getLogger('flask_mw_log')
# SQLITECON = None
# def init_sqlite():
#     global SQLITECON
#     SQLITECON = sqlite3.connect(SQLITE_PATH,check_same_thread=False)

class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)


    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def create_mac_dict():
    global macdict
    file_handle = open(MACDICT_PATH)
    for line in file_handle:
        mac_index = line.find("\t")
        mac = line[0:mac_index]
        name = line[mac_index+1:-1]
        macdict[mac] = name
    file_handle.close()


# 根据mac地址自动识别厂商信息
def get_vendor_by_mac(mac_key):
    mac = mac_key.replace(':', '')
    mac = mac[1:7].upper()
    sql_str = "select vendor from dev_vendor_mac where mac = '%s'" % (mac)
    db_proxy_config = DbProxy(CONFIG_DB_NAME)
    res, rows = db_proxy_config.read_db(sql_str)
    logger.info(sql_str)
    if res == 0 and len(rows) > 0:
        vendor = rows[0][0]
    else:
        vendor = "未知"
    logger.info(vendor)
    return vendor


def get_name_by_mac(mac_key):
    global macdict
    mac = mac_key.replace(':','')
    key_info = mac[0:6].upper()
    # print key_info
    # if macdict.has_key(key_info) is True:
    #     return macdict[key_info]
    return "dev-"+mac

def get_device_name(ip, mac):
    db_proxy = DbProxy(CONFIG_DB_NAME)
    result, dev_name = db_proxy.read_db("select name from topdevice where ip='%s' and mac='%s'"%(ip, mac))
    if len(dev_name) == 0:
        deviceName = get_name_by_mac(mac)
        if deviceName[0:4] == 'dev-' and ip != "":
            deviceName = 'dev-'+ip
    else:
        deviceName = dev_name[0][0]
    return deviceName
   
def get_webdpi_obj():
    global webDpi
    if(webDpi == None):
        webDpi = webdpi()
    return webDpi

# g_sqlite_file_lock='/tmp/sqlite_file_lock'
# def new_send_cmd(socket_type, cmd, messageid):
#     '''
#     new_send_cmd function is send anything conf sql
#     socket_type: socket type
#     cmd: conf sql from web
#     messageid: 0 is read sql(select), 1 is write sql(insert, update, delete)
#     '''
#     global SQLITECON
#     global g_sqlite_file_lock
#     rows = None
#
#     with open(g_sqlite_file_lock,'r') as fp:
#         fcntl.flock(fp.fileno(),fcntl.LOCK_EX)  # locks the file
#         if socket_type == TYPE_APP_SOCKET:
#             cur = SQLITECON.cursor()
#             cmd = cmd.encode('utf-8')
#             try:
#                 cur.execute(cmd)
#                 if messageid == 1:
#                     rows=cur.fetchall()
#                 else:
#                     SQLITECON.commit()
#             except sqlite3.Error as e:
#                 logger.error("new_send_cmd oper db cmd=%s", cmd)
#     if rows == None:
#         rows = []
#     return rows


def send_read_cmd(socket_type,cmd):
    global g_app_sock
    global g_event_sock

    if socket_type == TYPE_APP_SOCKET:
        mw_sock = g_app_sock
    elif socket_type == TYPE_EVENT_SOCKET:
        mw_sock = g_event_sock
    else:
        return

    rows = None

    cmd_len = len(cmd)
    format_msg = 'iiL%ds'%(cmd_len)
    data=struct.pack(format_msg, 0, 2, 0, str(cmd))
    try:
        res = mw_sock.sendto(data,remote_read_addr)
    except socket.error, arg:
        logger.error("mw_socket send_read_cmd send error.")
        return []
    if(res>=0):
        mw_sock.settimeout(10)
        try:
            data,addr = mw_sock.recvfrom(409600)

        except socket.error, arg:
            logger.error("mw_socket send_read_cmd recv error.cmd=%s",cmd)
        mw_sock.settimeout(None)

        try:
            rows=json.loads(data)
        except:
            logger.error("json load error")
    if(rows==None):
        rows=[]
    return rows

def send_file_cmd(socket_type,cmd):
    global g_app_sock
    global g_event_sock

    if socket_type == TYPE_APP_SOCKET:
        mw_sock = g_app_sock
    elif socket_type == TYPE_EVENT_SOCKET:
        mw_sock = g_event_sock
    else:
        return
    try:
        res = mw_sock.sendto(cmd,remote_file_addr)
    except socket.error, arg:
        logger.error("mw_socket send_file_cmd send_write_cmd error.")
    mw_sock.settimeout(30)
    try:
        data,addr = mw_sock.recvfrom(2048)
    except socket.error, arg:
        logger.error("mw_socket send_read_cmd recv error.cmd=%s",cmd)
    mw_sock.settimeout(None)
    return data

def send_deploy_cmd(socket_type,cmd):
    global g_app_sock
    if socket_type == TYPE_APP_SOCKET:
        mw_sock = g_app_sock
    else:
        return
    try:
        res = mw_sock.sendto(cmd,remote_deploy_addr)
    except socket.error, arg:
        logger.error("mw_socket send_deploy_cmd send_write_cmd error.")
    mw_sock.settimeout(10)
    data=''
    try:
        data,addr = mw_sock.recvfrom(2048)
    except socket.error, arg:
        logger.error("mw_socket send_read_cmd recv error.cmd=%s",cmd)
    mw_sock.settimeout(None)
    return data

def conf_save_flag_set():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "update nsm_confsave set save_flag = 0"
    res = db_proxy.write_db(sql_str)
    return res

def conf_save_flag_unset():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "update nsm_confsave set save_flag = 1"
    res = db_proxy.write_db(sql_str)
    return res

def conf_save_flag_get():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select save_flag from nsm_confsave"
    res, sql_res = db_proxy.read_db(sql_str)
    if( res != 0 ):
        return 1
    else:
        return sql_res[0][0]

def init_socket(socket_type, pid = None, tid = None, time = None):
    global g_app_sock
    global g_event_sock

    global app_sock_addr
    global event_sock_addr

    sock = None
    addr = None

    if socket_type == TYPE_APP_SOCKET:
        addr = app_sock_addr
    elif socket_type == TYPE_EVENT_SOCKET:
        addr = event_sock_addr

    else:
        logger.error("mw socket type init error!")

    if pid != None:
        addr += '_'
        addr += str(pid)
    if tid != None:
        addr += '_'
        addr += str(tid)
    if time != None:
        addr += '_'
        addr += str(time)
    try:
        if os.path.exists(addr):
            os.remove(addr)
    except:
        logger.error("%s file not exist" % addr)
    try:
        if socket_type == TYPE_APP_SOCKET:
            g_app_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            g_app_sock.bind(addr)
            sock = g_app_sock
        elif socket_type == TYPE_EVENT_SOCKET:
            g_event_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            g_event_sock.bind(addr)
            sock = g_event_sock

        logger.info("socket for %s ok" % addr)
    except:
        logger.error(traceback.format_exc())
    return sock

def web_send_msg_to_commandhander(msg):
    global g_app_sock
    sock = g_app_sock
    res = None
    data = []

    try:
        res = sock.sendto(json.dumps(msg),app_sock_addr)
    except socket.error, arg:
        print traceback.format_exc()
        logger.error(traceback.format_exc())
        return json.loads(data)

    if (res >= 0):
        sock.settimeout(10)
        try:
            data, addr = sock.recvfrom(409600)
        except:
            logger.error(traceback.format_exc())
        sock.settimeout(None)
    return json.loads(data)

if g_dpi_plat_type == DEV_PLT_X86:
    DB_FLAG_PATH = "/app/db_flag"
else:
    DB_FLAG_PATH = "/data/mysql"

class DbProxy(object):
    def __init__(self, db_name='keystone'):
        self.connect_status = 1
        self.reconnect_times = 0
        self.cur = None
        self.db_name = db_name
        try:
            self.conn=MySQLdb.connect(host='localhost', port=3306, user='keystone',
                                      passwd='OptValley@4312', db=self.db_name)
        except:
            logger.error('connet mysql error')
            logger.error(traceback.format_exc())
            self.connect_status = 0
            return
        self.cur = self.conn.cursor()

    def __del__(self):
        self.cur.close()
        self.conn.close()
        return

    def check_db_errno(self,errno):
        if errno == 29 or errno == 1146 or errno == 1194 or errno == 1030 or errno == 1102 or errno == 1712:
            return True
        return False

    def write_db(self,sqlstr):
        try:
            self.cur.execute(sqlstr)
        except MySQLdb.Error as e:
            try:
                errno  = e.args[0]
                errinfo = e.args[1]
                if self.check_db_errno(errno):
                    logger.error("make mysql_check_error.flag error")
                    os.system("mkdir -p %s" % DB_FLAG_PATH)
                    os.system("touch -f %s/mysql_check_error.flag" % DB_FLAG_PATH)
                    error_str = "write_db error, cmd=%s,errno=[%d],errinfo=%s" % (sqlstr, errno, errinfo)
                    os.system('echo "%s" >> %s/mysql_check_error.flag' % (error_str, DB_FLAG_PATH))
                logger.error("write_db error, cmd=%s,errno=[%d],errinfo=%s", sqlstr, errno, errinfo)
            except IndexError:
                logger.error('write_db error')
                logger.error(traceback.format_exc())
            
            
            if self.reconnect_times < 5:
                self.reconnect_times += 1
                res = self.reconnect()
                # res = self.write_db(sqlstr)
                if res == 0:
                    self.reconnect_times = 0
                else:
                    time.sleep(0.2)
                return res
            else:
                self.reconnect_times = 0
                return 1
        try:
            self.conn.commit()
        except:
            logger.error("conn commit fail!!")
            logger.error(traceback.format_exc())
        return 0
    def read_db(self,sqlstr):
        try:
            self.cur.execute(sqlstr)
            rows=self.cur.fetchall()
        except MySQLdb.Error as e:
            try:
                errno  = e.args[0]
                errinfo = e.args[1]
                if self.check_db_errno(errno):
                    logger.error("make mysql_check_error.flag")
                    os.system("mkdir -p %s" % DB_FLAG_PATH)
                    os.system("touch -f %s/mysql_check_error.flag" % DB_FLAG_PATH)
                    error_str = "write_db error, cmd=%s,errno=[%d],errinfo=%s" % (sqlstr, errno, errinfo)
                    os.system('echo "%s" >> %s/mysql_check_error.flag' % (error_str, DB_FLAG_PATH))
                logger.error("read_db error: cmd=%s,errno=[%d],errinfo=%s",sqlstr,errno, errinfo)
            except IndexError:
                logger.error('read_db error')
                logger.error(traceback.format_exc())

            if self.reconnect_times < 5:
                self.reconnect_times += 1
                self.reconnect()
                res, rows = self.read_db(sqlstr)
                if res == 0:
                    self.reconnect_times = 0
                else:
                    time.sleep(0.2)
                return res,rows
            else:
                self.reconnect_times = 0
                rows = []
                return 1,rows
        return 0,rows

    def execute(self, sqlstr):
        try:
            self.cur.execute(sqlstr)
        except MySQLdb.Error as e:
            try:
                errno  = e.args[0]
                errinfo = e.args[1]
                if self.check_db_errno(errno):
                    logger.error("make mysql_check_error.flag")
                    os.system("mkdir -p %s" % DB_FLAG_PATH)
                    os.system("touch -f %s/mysql_check_error.flag" % DB_FLAG_PATH)
                    error_str = "write_db error, cmd=%s,errno=[%d],errinfo=%s" % (sqlstr, errno, errinfo)
                    os.system('echo "%s" >> %s/mysql_check_error.flag' % (error_str, DB_FLAG_PATH))
                logger.error("execute error: cmd=%s,errno=[%d],errinfo=%s",sqlstr,errno, errinfo)
            except IndexError:
                logger.error("execute error, cmd=%s",sqlstr)
                logger.error(traceback.format_exc())

            if self.reconnect_times < 5:
                self.reconnect_times += 1
                self.reconnect()
                res, self.cur = self.execute(sqlstr)
                if res == 0:
                    self.reconnect_times = 0
                return res,self.cur
            else:
                self.reconnect_times = 0
                return 1,self.cur
        return 0,self.cur

    def get_connect_status(self):
        return self.connect_status

    def reconnect(self):
        try:
            self.cur.close()
            self.conn.close()
        except:
            logger.error(traceback.format_exc())
        try:
            self.conn=MySQLdb.connect(host='localhost', port=3306, user='keystone',
                                      passwd='OptValley@4312', db=self.db_name)
        except:
            logger.error('connet mysql error')
            logger.error(traceback.format_exc())
            self.connect_status = 0
            return
        self.cur = self.conn.cursor()
        self.connect_status = 1
        logger.info("DbProxy reconnect ok")


def trans_db_ipmac_to_local(elem):
    if not elem or elem == "NA" or elem == "NULL":
        return ""
    elif len(elem) < 18:
        return elem.replace(":", "")
    else:
        return elem


def get_default_devname_by_ipmac(ip, mac):
    mac = mac.replace(":", "")
    trans_ip = trans_db_ipmac_to_local(ip)
    trans_mac = trans_db_ipmac_to_local(mac)

    if trans_ip != "":
        dev_name = "dev-" + trans_ip
    else:
        if trans_mac != "":
            dev_name = "dev-" + trans_mac
        else:
            dev_name = "NA"
    return dev_name


def get_devname_by_ipmac(ip, mac):
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if ":" not in mac:
        mac = ':'.join(mac[i:i + 2] for i in range(0, len(mac), 2))
    # sql_str = "select dev_name from dev_name_conf where dev_ip = '%s' and dev_mac = '%s'" % (ip, mac)
    sql_str = "select name from topdevice where ip = '%s' and mac = '%s'" % (ip, mac)
    res, sql_res = db_proxy.read_db(sql_str)
    if res == 0 and len(sql_res) > 0:
        dev_name = sql_res[0][0]
    else:
        dev_name = ip or mac if (ip or mac) else 'NA'
        dev_name = "未知(" + dev_name + ")"
    return dev_name


def get_ipmac_list_by_devname(devname):
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select ip, mac from topdevice where name like " + "\"%" + devname + "%\""
    res, sql_res = db_proxy.read_db(sql_str)
    if res == 0 and len(sql_res) > 0:
        ipmac_list = sql_res
    else:
        ipmac_list = ["any", "any"]
    return ipmac_list


def get_ipmac_list_devname(devname):
    db_proxy = DbProxy()
    sql_str = "select dev_ip, dev_mac from dev_name_conf where dev_name like " + "\"%" + devname + "%\""
    res, sql_res = db_proxy.read_db(sql_str)
    if res == 0 and len(sql_res) > 0:
        ipmac_list = sql_res
    else:
        ipmac = get_ipmac_by_default_devname(devname)
        ipmac_list = [ipmac]
    return ipmac_list


def get_ipmac_by_default_devname(dev_name):
    ipmac = []
    if "dev-" in dev_name:
        left_str = dev_name.split("-", 1)[1]
        if "." in left_str:
            ipmac = [left_str, "any"]
        else:
            ipmac = ["", left_str]
    else:
        ipmac = ["", ""]
    return ipmac


def get_devname_ipmac(ip, mac):
    db_proxy = DbProxy(CONFIG_DB_NAME)
    mac = mac.replace(":", "")
    sql_str = "select dev_name from dev_name_conf where dev_ip = '%s' and dev_mac = '%s'" % (ip, mac)
    res, sql_res = db_proxy.read_db(sql_str)
    if res == 0 and len(sql_res) > 0:
        dev_name = sql_res[0][0]
    else:
        dev_name = get_default_devname_by_ipmac(ip, mac)
    return dev_name


def set_devname_by_ipmac(ip, mac, dev_name):
    db_proxy = DbProxy(CONFIG_DB_NAME)
    mac = mac.replace(":", "")
    sql_str = "select dev_name from dev_name_conf where dev_ip = '%s' and dev_mac = '%s'" % (ip, mac)
    logger.info("set_devname_by_ipmac sql_str: %s" % sql_str)
    res, sql_res = db_proxy.read_db(sql_str)
    if res == 0:
        if len(sql_res) > 0:
            sql_str = "update dev_name_conf set dev_name = '%s' where dev_ip = '%s' and dev_mac = '%s'" % (dev_name, ip, mac)
            logger.info("set_devname_by_ipmac sql_str: %s" % sql_str)
            db_proxy.write_db(sql_str)
            return 0
        else:
            sql_str = "select count(*), min(id) from dev_name_conf "
            logger.info("set_devname_by_ipmac sql_str: %s" % sql_str)
            res, sql_res = db_proxy.read_db(sql_str)
            if res == 0 and len(sql_res) > 0:
                if( sql_res[0][0] >= 1000):
                    sql_str = "delete from dev_name_conf where id = %d" % sql_res[0][1]
                    logger.info("set_devname_by_ipmac sql_str: %s" % sql_str)
                    db_proxy.write_db(sql_str)
                sql_str = "insert into dev_name_conf values(default, '%s', '%s', '%s')" % (ip, mac, dev_name)
                logger.info("set_devname_by_ipmac sql_str: %s" % sql_str)
                db_proxy.write_db(sql_str)
                return 0
            else:
                return 1
    else:
        return 1


def get_run_mode():
    res = commands.getoutput("vtysh -c 'show run'")
    pos_start = res.find('dpi mode') + 9
    pos_end = res.find('\n', pos_start)
    mode = res[pos_start: pos_end]
    return mode

RUN_MODE = get_run_mode()

def getBypassStat():
    sys_info = {"bp0": 0, "bp1": 0}
    bypassDict = {'n': 0, "b": 1}
    if RUN_MODE == "ips":
        try:
            res = commands.getoutput("cat /sys/class/bypass/g3bp0/bypass")
            sys_info["bp0"] = bypassDict[res]
            res = commands.getoutput("cat /sys/class/bypass/g3bp1/bypass")
            sys_info["bp1"] = bypassDict[res]
        except:
            logger.error(traceback.format_exc())
    return sys_info

#flask-login imp


class User(UserMixin):
    def __init__(self, user_id=None):
        self.user_id = user_id
        
    def get_id(self):
        return self.user_id


class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([unicode(s).encode("utf-8-sig") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8-sig")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writeclose(self):
        self.stream.close()

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def get_not_null_name(origin_name):
    if not origin_name or origin_name == "NULL":
        return "NA"
    else:
        return origin_name


def get_dev_dict():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select dev_ip, dev_mac, dev_name from dev_name_conf"
    res, sql_res = db_proxy.read_db(sql_str)
    dev_name_dict = {}
    if res == 0:
        for elem in sql_res:
            dev_name_dict[elem[0] + elem[1]] = elem[2]
    return dev_name_dict

def get_traffic_event_row(tmp_res, dev_name_dict, incident_from, incident_action, incident_risk):
    tmp = list(tmp_res)
    if tmp_res[10] == "4":
        tmp[4] = ("低阈值 = %skbps 高阈值 = %skbps 带宽= %skbps" % (str(tmp[7]), str(tmp[8]), str(tmp[9]))).decode("UTF-8")

    src_ip_str = trans_db_ipmac_to_local(tmp[0])
    src_mac_str = trans_db_ipmac_to_local(tmp[11])
    dst_ip_str = trans_db_ipmac_to_local(tmp[1])
    dst_mac_str = trans_db_ipmac_to_local(tmp[12])

    if (src_ip_str + src_mac_str) in dev_name_dict:
        src_dev_name = dev_name_dict[src_ip_str + src_mac_str]
    else:
        # src_dev_name = get_default_devname_by_ipmac(src_ip_str, src_mac_str)
        src_dev_name = "NA"

    if (dst_ip_str + dst_mac_str) in dev_name_dict:
        dst_dev_name = dev_name_dict[dst_ip_str + dst_mac_str]
    else:
        # dst_dev_name = get_default_devname_by_ipmac(dst_ip_str, dst_mac_str)
        dst_dev_name = "NA"

    if tmp[4] is None:
        tmp[4] = "NA"
    else:
        tmp[4] = tmp[4].replace(",", " ")
    if tmp[5] is None:
        tmp[5] = "NA"
    else:
        tmp[5] = tmp[5].replace(",", " ")

    tmp[0] = get_not_null_name(tmp[0])
    tmp[1] = get_not_null_name(tmp[1])
    tmp[11] = get_not_null_name(tmp[11])
    tmp[12] = get_not_null_name(tmp[12])
    alarm_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(tmp[6])))

    if incident_risk == 0:
        risk_level = u"低危"
    elif incident_risk == 1:
        risk_level = u"中危"
    elif incident_risk == 2:
        risk_level = u"高危"
    else:
        risk_level = u""
    row_format = [alarm_time, src_dev_name.decode("UTF-8"),  dst_dev_name.decode("UTF-8"), tmp[0],  tmp[1], tmp[11], tmp[12], incident_action[int(tmp[2])], get_ui_proto_name(tmp[3]), tmp[5], tmp[4], incident_from[int(tmp[10])-1], risk_level]
    return row_format


#设备端口映射图
PORT_MAP_DICT = {"KEA-C200": [["p0", "eth0"], ["p1", "eth1"]],
                 "KEA-C400": [["p0", "eth0"], ["p1", "eth1"], ["p2", "eth2"], ["p3", "eth3"]],
                 "KEC-C400": [["p0", "eth0"], ["p1", "eth1"], ["p2", "eth2"], ["p3", "eth3"]],
                 "KEA-U1000": [["p0", "eth1"], ["p1", "eth2"]],
                 "IMAP": [["p1", "eth1"], ["p2", "eth2"], ["p3", "eth3"]],
                 "IMAP02": [["p1", "eth1"], ["p2", "eth2"], ["p3", "eth3"],["p4", "eth4"],["p5", "eth5"]]
                 }


center_ser_addr = '/data/sock/icspd_event_msg_sock'
center_ser_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)


def inet_pton(family, addr):
    if family == socket.AF_INET:
        return socket.inet_aton(addr)

    elif family == socket.AF_INET6:
        if '.' in addr:  # a v4 addr
            v4addr=addr[addr.rindex(':') + 1:]
            v4addr=socket.inet_aton(v4addr)
            v4addr=map(lambda x: ('%02X' % ord(x)), v4addr)
            v4addr.insert(2, ':')
            newaddr=addr[:addr.rindex(':') + 1] + ''.join(v4addr)
            return inet_pton(family, newaddr)
        dbyts=[0] * 8  # 8 groups
        grps=addr.split(':')

        for i, v in enumerate(grps):
            if v:
                dbyts[i]=int(v, 16)
            else:
                for j, w in enumerate(grps[::-1]):
                    if w:
                        dbyts[7 - j]=int(w, 16)
                    else:
                        break
                break
        return ''.join((chr(i // 256) + chr(i % 256)) for i in dbyts)
    else:
        return ''


def send_center_msg(logger, *info):
    '''执行消息的发送功能,通过判断flag文件是否存在执行发送与否的操作'''
    if os.path.exists('/data/send_icspd.flag'):
        # 通用消息头
        version=1
        platform=1
        msg_type=1
        padding=0
        timestamp=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # clientid = os.system("/app/bin/get_eeprom read all | grep 'serialnum' | awk '{print $3}'")
        clientid = commands.getoutput("/app/bin/get_eeprom read all | grep 'serialnum' | awk '{print $3}'")
        clientid = str(clientid)
        logger.info(clientid)
        struct_str = ""
        try:
            if len(info) > 3:
                src_mac = info[3] if info[3].strip() else "000000000000"
                smac=src_mac.decode('hex')
                dmac="000000000000".decode('hex')
                sip=info[2] if info[2].strip() else ''
                if ':' in sip:
                    af_family=6
                    sip=inet_pton(socket.AF_INET6, sip)
                elif '.' in sip:
                    af_family=4
                    sip=inet_pton(socket.AF_INET, sip)
                else:
                    af_family=0
                    sip=''
                dip=''
                sport=0
                dport=0
                action=1
                protocol=0
                app=''
                if info[0] == 4:
                    message = '流量告警'
                    risklevel = 1
                    event_type = 24
                    info_list = info[1].split(",")
                    # incident_pack_str = '!HHHH20s20s6s6sI16s16sHHBB21sB{}s'.format(len(bytes(message)))
                    incident_pack_str = '!HHHH20s20s6s6sI16s16sHHBB21sBHB16s16s16s'
                    struct_str = struct.pack(incident_pack_str, version, platform, msg_type, padding, timestamp, clientid,
                                           smac, dmac, af_family, sip, dip, sport, dport, action, protocol, app,
                                           risklevel, event_type, int(info_list[0]), info_list[1], info_list[2],info_list[3])
                elif info[0] == 6:
                    message = '设备上线'
                    if info[1] == 1:
                        message = '设备离线'
                    risklevel = 2
                    event_type = 26
                    incident_pack_str = '!HHHH20s20s6s6sI16s16sHHBB21sBH{}s'.format(len(bytes(message)))
                    struct_str = struct.pack(incident_pack_str, version, platform, msg_type, padding, timestamp, clientid,
                                           smac, dmac, af_family, sip, dip, sport, dport, action, protocol, app,
                                           risklevel,event_type,message)
            elif info[1] == 1:
                msg_type = 2
                e_type = int(info[0])
                msg = str(info[2])
                logger.info(e_type)
                logger.info(msg)
                # event_pack_str='!HHHH20s20sB' + str(len(bytes(msg))) + 's'
                event_pack_str='!HHHH20s20sB{}s'.format(len(bytes(msg)))
                struct_str=struct.pack(event_pack_str, version, platform, msg_type, padding, timestamp, clientid, e_type, msg)
            elif info[1] == 2:
                msg_type = 6
                info_list = info[2].split("--")
                # af_family = 6
                # sip = inet_pton(socket.AF_INET6, "1::3")
                sip = info_list[2] if info_list[2].strip() else ''
                if sip == "CONSOLE":
                    af_family = 0
                    sip = ''
                elif ':' in sip:
                    af_family = 6
                    sip = inet_pton(socket.AF_INET6, sip)
                else:
                    af_family = 4
                    sip = inet_pton(socket.AF_INET, sip)
                # logger.info(str(af_family) + "==================" + sip)
                event_pack_str = '!HHHH20s20s20s20sI16s128s'
                struct_str = struct.pack(event_pack_str, version, platform, msg_type, padding, timestamp, clientid, info_list[0], info_list[1], af_family, sip, info_list[3])

        except:
            logger.error(traceback.format_exc())
        try:
            logger.info(struct_str)
            center_ser_sock.sendto(struct_str, center_ser_addr)
        except:
            logger.error(traceback.format_exc())
            logger.error('center_ser_sock send error...')
    else:
        pass
