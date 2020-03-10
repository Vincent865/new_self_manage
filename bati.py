#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import thread
from logging.handlers import RotatingFileHandler
from logging.handlers import SysLogHandler
from global_function.log_config import *
from global_function.aes_cipher import *
import global_function.global_var
from common import common_helper
from common.daemon import Daemon
from app.whitelist import white_list_start_timer
from app.whitelist import white_list_stop_timer
from apscheduler.schedulers.background import BackgroundScheduler
#import affinity
import random
from global_function.switch_info import *
from global_function.protocol_audit import *
from global_function.traffic_audit import *
from global_function.self_white_list import *
from global_function.log_oper import *
from global_function.dev_online import DeviceOnline

logger = logging.getLogger('flask_db_socket_log')

IP_STUDYLIST_PATH = "/conf/db/ip.list"
MAC_STUDYLIST_PATH = "/conf/db/mac.list"
if g_dpi_plat_type == DEV_PLT_MIPS:
    IP_STUDYLIST_PATH = "/data/db/ip.list"
    MAC_STUDYLIST_PATH = "/data/db/mac.list"


def find_insert_table_name(sql_str):
    tmp = sql_str.lower()
    tablename= tmp.split('into')[1].strip().split(' ')[0]
    return tablename

def recv_read_db_oper(read_cmd_list,db_read_sock):
    #affinity.set_process_affinity_mask(os.getpid(), 0xeL)
    while 1:
        data,addr = db_read_sock.recvfrom(8192)
        if not data:
            continue
        info = ClientInfo()
        data_len = len(data)
        fox_s = 'iiL%ds'%(data_len - 16)
        tmp = struct.unpack(fox_s,data)
        msgid = tmp[1]
        sql_str = tmp[3]
        info = ClientInfo()
        if msgid == 1:
            info.sqlstr = sql_str[0:sql_str.find('\0')]
        else:
            info.sqlstr = sql_str

        info.addr = addr
        if read_cmd_list.full():
            continue
        read_cmd_list.put(info)

def recv_write_db_oper(dict_table_list,db_write_sock):
    #affinity.set_process_affinity_mask(os.getpid(), 0xeL)
    while 1:
        data,addr = db_write_sock.recvfrom(8192)
        if not data:
            continue

        data_len = len(data)
        fox_s = 'iiL%ds'%(data_len - 16)
        tmp = struct.unpack(fox_s,data)
        msgid = tmp[1]
        sql_str = tmp[3]
        info = ClientInfo()
        if msgid == 1:
            info.sqlstr = sql_str[0:sql_str.find('\0')]
        else:
            info.sqlstr = sql_str
        info.addr = addr
        tablename = find_insert_table_name(info.sqlstr)
        if tablename in dict_table_list:
            write_cmd_list = dict_table_list[tablename]
        else:
            continue
        # logger.info(info.sqlstr)

        # if syslog switch open and sqlstr incloud incident, syslog will upload
        if SYSLOG_UPLOAD["status"] and "incidents" in info.sqlstr:
            type_log = "content_list"
            handle_info(info.sqlstr, type_log)

        if write_cmd_list.full():
            continue
        try:
            write_cmd_list.put(info)
        except:
            continue


def recv_file_db_oper(file_cmd_list,db_file_sock):
    #affinity.set_process_affinity_mask(os.getpid(), 0xeL)
    while 1:
        sql_str,addr = db_file_sock.recvfrom(2048)
        if not sql_str:
            continue
        info = ClientInfo()
        info.sqlstr = sql_str
        info.addr = addr
        if file_cmd_list.full():
            continue
        file_cmd_list.put(info)

def recv_deploy_db_oper(deploy_cmd_list,db_deploy_sock):
    #affinity.set_process_affinity_mask(os.getpid(), 0xeL)
    while 1:
        sql_str,addr = db_deploy_sock.recvfrom(32768)
        if not sql_str:
            continue
        info = ClientInfo()
        info.sqlstr = sql_str
        info.addr = addr
        if deploy_cmd_list.full():
            continue
        deploy_cmd_list.put(info)

def export_customrules(info, db_proxy):
    file_name = "whitelist-" + time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(time.time())) + ".csv"
    field_list = []
    writer = UnicodeWriter(open("/data/download/" + file_name, "wb"))
    tmp_sql = info.sqlstr.split(';')
    for tmp_str in tmp_sql:
        res, cur = db_proxy.execute(tmp_str)
        if res == 1:
            logger.error("file_db_oper oper db file cmd=%s", info.sqlstr)
        try:
            tmp_res = cur.fetchone()
            while tmp_res:
                if len(tmp_res) > 2:
                    tmp_filter = tmp_res[0] + tmp_res[2]
                else:
                    tmp_filter = tmp_res[0] + "any"
                if tmp_filter not in field_list:
                    oper_list = base64.b64decode(tmp_res[0])
                    if len(tmp_res) > 2:
                        tmp_row = (oper_list, tmp_res[1], tmp_res[2])
                    else:
                        tmp_row = (oper_list, tmp_res[1], "any")
                    writer.writerow(tmp_row)
                    field_list.append(tmp_filter)
                    tmp_res = cur.fetchone()
                else:
                    tmp_res = cur.fetchone()
        except:
            logger.error("db_oper file write error")
    writer.writeclose()

def file_db_oper(file_cmd_list,db_file_sock):
    #affinity.set_process_affinity_mask(os.getpid(), 0xeL)
    logger = logging.getLogger('flask_db_socket_log')
    db_proxy = DbProxy()
    config_db_proxy = DbProxy(CONFIG_DB_NAME)
    log_level = [u"紧急", u"警告", u"严重", u"错误", u"警示", u"通知", u"信息", u"调试"]
    log_type = [u"设备状态", u"接口状态", u"系统状态", u"业务状态", u"bypass状态"]
    log_result = [u"成功", u"失败"]

    while 1:
        info = file_cmd_list.get()
        logger.info(info.addr)
        logger.info(info.sqlstr)
        if info.sqlstr.find("customrules")>0:
            export_customrules(info, config_db_proxy)
        else:
            res, cur = db_proxy.execute(info.sqlstr)
            if res == 1:
                logger.error("file_db_oper execute error")
                continue

            col_list = [elem[0] for elem in cur.description]

            if info.sqlstr.find("incidents")>0:
                file_name = "incidents-" + time.strftime("%Y-%m-%d_%H:%M:%S",time.localtime(time.time()))+".csv"
                file_type = 1
            elif info.sqlstr.find("events")>0:
                file_name = "sysevent-" + time.strftime("%Y-%m-%d_%H:%M:%S",time.localtime(time.time()))+".csv"
                file_type = 2
                col_list = [u'时间', u"日志等级", u"日志类型", u"内容"]
            elif info.sqlstr.find("dpiuseroperationlogs")>0:
                file_name = "operlog-" + time.strftime("%Y-%m-%d_%H:%M:%S",time.localtime(time.time()))+".csv"
                file_type = 3
                col_list = [u'时间', u'用户', u'IP', u'执行操作', u'执行结果']
            else:
                file_name = "incidents-" + time.strftime("%Y-%m-%d_%H:%M:%S",time.localtime(time.time()))+".csv"
                file_type = 4

            try:
                writer = UnicodeWriter(open("/data/download/"+file_name, "wb"))
                writer.writerow(col_list)

                tmp_res = cur.fetchone()
                while tmp_res:
                    if file_type == 2:
                        row = [tmp_res[0].replace("T", " ").replace("Z", ""), log_level[int(tmp_res[1])], log_type[int(tmp_res[2])-1], tmp_res[3].decode("utf8")]
                        writer.writerow(row)
                    else:
                        row = [tmp_res[0].replace("T", " ").replace("Z", ""), tmp_res[1].decode("utf8"), tmp_res[2], tmp_res[3].decode("utf8"), log_result[int(tmp_res[4])]]
                        writer.writerow(row)
                    tmp_res = cur.fetchone()
            except:
                logger.error("db_oper file write error")
                logger.error(traceback.format_exc())
            writer.writeclose()
        try:
            logger.info(info.addr)
            db_file_sock.sendto(file_name,info.addr)
        except:
            logger.error("file_db_oper send filename error!filename=%s",file_name)
        time.sleep(0.001)

def get_ip_study_list(cur):
    ip_study_list = ""
    ip_res = []
    cur.execute("select distinct ip from topdevice where dev_type=0")
    ip_file = open(IP_STUDYLIST_PATH, 'w')
    ip_study_res = cur.fetchall()
    #ip2num = lambda x: sum([256**j*int(i) for j, i in enumerate(x.split('.')[::-1])])
    for ip_study in ip_study_res:
        if len(ip_study[0]) > 0:
            ip_res.append(ip_study[0])
            ip_study_list += "%s," % ip_study[0]
            #ip_int = ip2num(ip_study[0])
            #ip_file.write("%d\n" % ip_int)
    if len(ip_study_list) > 0:
        if ip_study_list[-1] == ',':
            ip_study_list = ip_study_list[0:-1]
    #ip_file.close()
    return ip_study_list

def get_mac_study_list(cur):
    mac_study_list = ""
    cur.execute("select distinct mac from topdevice where dev_type=0")
    mac_res = cur.fetchall()
    #mac_file = open(MAC_STUDYLIST_PATH, 'w')
    for mac in mac_res:
        mac_tmp = mac[0].replace(':', '')
        mac_study_list += "%s," % mac_tmp
        #mac_file.write("%s\n" % mac_tmp)
    if len(mac_study_list) > 0:
        mac_study_list = mac_study_list[0:-1]
    #mac_file.close()
    return mac_study_list

def write_black_list_file(cur, sqlstr):
    blacklist_file = open(BLACK_LIST_PATH, "w")
    cur.execute(sqlstr)
    res = cur.fetchall()
    for body in res:
        if RUN_MODE == 'ids':
            rule_str = 'alert'
        else:
            rule_str = ACTION_LIST[body[1]]
        dec_str = get_aes_cipher().decrypt(body[0])
        start_pos = dec_str.find(" ")
        rule_str += dec_str[start_pos:-1]
        rule_str += "\n"
        blacklist_file.write(rule_str.replace("$HTTP_PORTS", "443"))
    blacklist_file.close()

def write_white_list_file(cur):
    logger = logging.getLogger('flask_db_socket_log')
    cur.execute("select body,action from customrules where deleted=1 order by ruleId desc")
    res = cur.fetchall()
    res = list(res)
    cur.execute("select body,action from rules where deleted=1")
    res2 = cur.fetchall()
    for val in res2:
        res.append(val)
    whitelist_file = open(WHITE_LIST_PATH,"w")
    for body in res:
        rule_str = ACTION_LIST[body[1]]
        dec_str = base64.b64decode(body[0])
        start_pos = dec_str.find(" ")
        rule_str += dec_str[start_pos:]
        rule_str += "\n"
        whitelist_file.write(rule_str)
    # default rules just valid for learned rules
    if len(res2) > 0:
        write_default_rules(whitelist_file, "", "", RUN_MODE)
        '''
        ip_study_list = get_ip_study_list(cur)
        mac_study_list = get_mac_study_list(cur)
        cur.execute("select count(distinct ip,mac) from topdevice  where dev_type=0")
        device_num = cur.fetchone()[0]
        logger.info("white list device number: %s, threshold: 50" % device_num)
        if device_num <= 50:
            # using 3 old rules
            write_default_rules(whitelist_file, ip_study_list, mac_study_list, RUN_MODE)
        else:
            # using the default rules: any any -> any any
            write_default_rules(whitelist_file, "", "", RUN_MODE)
        '''
    whitelist_file.close()

def deploy_db_oper(deploy_cmd_list,db_deploy_sock):
    #affinity.set_process_affinity_mask(os.getpid(), 0xeL)
    logger = logging.getLogger('flask_db_socket_log')
    while 1:
        try:
            info = deploy_cmd_list.get()
            conn = MySQLdb.connect(host='localhost',port=3306, user='keystone', passwd='OptValley@4312',db='keystone_config')
            cur = conn.cursor()
            conn.commit()
            if info.sqlstr.find('signatures') >= 0:
                write_black_list_file(cur, info.sqlstr)
            elif info.sqlstr.find('rules') >= 0:
                write_white_list_file(cur)
            else:
                db_deploy_sock.sendto("fail", info.addr)
            # subprocess.Popen(['vtysh', '-c', 'config t', '-c', 'write file'])
            os.system("/app/bin/conf_bakup.sh")
            db_deploy_sock.sendto("ok", info.addr)
            cur.close()
            conn.close()
        except:
            logger.error(traceback.format_exc())

        time.sleep(0.001)

write_addr='/data/sock/db_write_sock'
read_addr='/data/sock/db_read_sock'
file_addr='/data/sock/db_file_sock'
deploy_addr='/data/sock/db_deploy_sock'
client_addr='/data/sock/db_client_sock'
count_opp_addr='/data/sock/db_count_opp_sock'


def insert_complex_tbl(oper_cmd_list, tablename):
    logger = logging.getLogger('flask_db_socket_log')
    db_proxy = DbProxy()
    sqlstr=''
    num=0
    tabnum=0
    while 1:
        info = None
        try:
            info = oper_cmd_list.get(timeout=3)
        except:
            info = None
        if info is None:
            if num>0:
                sqlstr=sqlstr + ';'
                sqlstr = sqlstr.replace(tablename,tablename+'_%d'%(tabnum))
                db_proxy.write_db(sqlstr)
                num = 0
                tabnum= (tabnum + 1)%10
                # logger.info(sqlstr)
            continue
        else:
            if num==0:
                sqlstr=info.sqlstr
            else:
                #sqlstr=sqlstr + ',' + info.sqlstr.split('values')[1]
                index = info.sqlstr.find('values')
                sqlstr=sqlstr + ',' + info.sqlstr[index+6:]
            num = num + 1
        if num>=100:
            sqlstr=sqlstr + ';'
            sqlstr = sqlstr.replace(tablename,tablename+'_%d'%(tabnum))
            db_proxy.write_db(sqlstr)
            num = 0
            tabnum= (tabnum + 1)%10


def count_opp_complex_tbl(oper_cmd_list, oper_cmd_q_list,result_queue,db_read_sock):
    while 1:
        info = None
        try:
            info = oper_cmd_list.get(timeout=3)
        except:
            info = None
        if info is None:
            continue
        for i in range(0,10):
            oper_cmd_q_list[i].put(info.sqlstr)
        count_num = 0
        total = 0
        restotal=None
        while count_num < 10:
            res = None
            try:
                res = result_queue.get(timeout=3)
            except:
                res = None
            if res is None:
                continue

            total += res[0][0]
            count_num +=1
        else:
            restotal=((total,),)
        data =  json.dumps(restotal)
        try:
            db_read_sock.sendto(data,info.addr)
        except:
            pass


def count_opp_sub_tbl(oper_cmd_list, result_list, num):
    logger = logging.getLogger('flask_db_socket_log')
    db_proxy = DbProxy()
    while 1:
        info = None
        try:
            info = oper_cmd_list.get(timeout=3)
        except:
            info = None
        if info is None:
            continue

        tablename= info.split('from')[1].strip().split(' ')[0]
        sql_str = info.replace(tablename,tablename+'_%d'%(num))
        res,results = db_proxy.read_db(sql_str)
        result_list.put(results)

def clean_incident_record(del_strategy, threshold):
    deletenum = del_limit["incident"]
    db_proxy = DbProxy()
    sql_cmd = "select count(*) from incidents"
    result,rows = db_proxy.read_db(sql_cmd)
    total = rows[0][0]
    if total > threshold:
        sql_str = "delete from incidents order by timestamp limit %d" % (total-threshold+deletenum)
        result = db_proxy.write_db(sql_str)
        if del_strategy == 1:
            content = U'安全事件条数达到上限，删除部分记录。'
        elif del_strategy == 2:
            content = U'数据库存储空间达到上限，删除部分安全事件。'
        msg = {}
        msg['Type'] = SYSTEM_TYPE
        msg['LogLevel'] = LOG_ALERT
        msg['Content'] = content
        msg['Componet'] = "mysql"
        send_log_db(MODULE_SYSTEM, msg)

def clean_flow_record(del_strategy, threshold):
    try:
        logger = logging.getLogger('flask_db_socket_log')
        deletenum = del_limit["protocol"]
        clean_flowheadid_sock_addr = '/data/sock/db_clean_flowheadid'
        clean_flowheadid_sock_client_addr = '/data/sock/db_clean_flowheadid_client_' + str(os.getpid()) + '_' + str(random.randint(1, 999999))
        db_clean_flowheadid_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        db_clean_flowheadid_sock.bind(clean_flowheadid_sock_client_addr)
        db_proxy = DbProxy()
        global protocol_names
        for proc in protocol_names:
            sql_cmd = "select count(*) from %sflowdatas"%(proc)
            result,rows = db_proxy.read_db(sql_cmd)
            total = rows[0][0]
            if total > threshold:
                result,rows = db_proxy.read_db("select flowdataHeadId,packetTimestampint from %sflowdatas order by packetTimestampint limit %d" % (proc, total-threshold+deletenum))
                ts_list = [ts[1] for ts in rows]
                if len(ts_list) > 0:
                    db_proxy.write_db("delete from %sflowdatas where packetTimestampint>=%d and packetTimestampint<= %d" % (
                        proc, min(ts_list), max(ts_list)))
                allFlowHeadId = set([id[0] for id in rows])
                try:
                    if del_strategy == 1:
                        content = '协议('.decode('utf8') + str(proc) + ')审计条数达到上限，删除部分记录。'.decode('utf8')
                    elif del_strategy == 2:
                        content = '数据库存储空间达到上限，删除部分协议('.decode('utf8') + str(proc) + ')审计记录。'.decode('utf8')
                    msg = {}
                    msg['Type'] = SYSTEM_TYPE
                    msg['LogLevel'] = LOG_ALERT
                    msg['Content'] = content
                    msg['Componet'] = "mysql"
                    send_log_db(MODULE_SYSTEM, msg)
                except:
                    logger.error(traceback.format_exc())

                # 4. 遍历该协议flowdata，若已无数据，删除该head
                for headId in allFlowHeadId:
                    sql_str = "select count(*) from %sflowdatas where flowdataHeadId=%d " % (proc, headId)
                    result,num = db_proxy.read_db(sql_str)
                    if result != 0:
                        continue
                    else:
                        num = num[0][0]
                    if num == 0:
                        sql_str = "delete from flowdataheads where flowdataHeadId=%d" % (headId)
                        result = db_proxy.write_db(sql_str)
                        # 删除缓存中flow，否则此flow不再写入数据库
                        db_clean_flowheadid_sock.sendto(str(headId), clean_flowheadid_sock_addr)
    except:
        logger.exception("Exception Logged")
    finally:
        db_clean_flowheadid_sock.close()
        os.remove(clean_flowheadid_sock_client_addr)

    return


def clean_traffic_record(del_strategy, threshold):
    deletenum = del_limit["traffic"]
    db_proxy = DbProxy()

    # 历史流量数据
    sql_cmd = "select count(*) from icdevicetrafficstats"
    result,rows = db_proxy.read_db(sql_cmd)
    total = rows[0][0]
    if total > threshold:
        del_str = "delete from icdevicetrafficstats order by timestamp limit %d" % (total - threshold + deletenum)
        db_proxy.write_db(del_str)

        # 记录LOG
        if del_strategy == 1:
            content = u'流量审计条数达到上限，删除部分记录。'
        elif del_strategy == 2:
            content = u'数据库存储空间达到上限，删除部分流量审计记录。'
        msg = {}
        msg['Type'] = SYSTEM_TYPE
        msg['LogLevel'] = LOG_ALERT
        msg['Content'] = content
        msg['Componet'] = "mysql"
        send_log_db(MODULE_SYSTEM, msg)


def get_path_size(strPath):
    if not os.path.exists(strPath):
        return 0;

    if os.path.isfile(strPath):
        return os.path.getsize(strPath);

    nTotalSize = 0;
    for strRoot, lsDir, lsFiles in os.walk(strPath):
        #get child directory size
        for strDir in lsDir:
            nTotalSize = nTotalSize + get_path_size(os.path.join(strRoot, strDir));

        #for child file size
        for strFile in lsFiles:
            nTotalSize = nTotalSize + os.path.getsize(os.path.join(strRoot, strFile));

    return nTotalSize;

def db_delete_his_record():
    # TODO: wait for receive thread start
    time.sleep(30)
    dev_type = get_dev_type()
    if dev_type == "IMAP":
        totalsize = 60 * 1024 * 1024 * 1024
        max_incident_num = 200 * 10000
        max_proto_num = 200 * 10000
        max_traffic_num = 200 * 10000
    elif dev_type == "KEA-U1000":
        totalsize = 250 * 1024 * 1024 * 1024
        max_incident_num = 500 * 10000
        max_proto_num = 500 * 10000
        max_traffic_num = 500 * 10000
    else:
        # MIPS默认规格
        totalsize = 3 * 1024 * 1024 * 1024
        max_incident_num = 25000
        max_proto_num = 5 * 10000
        max_traffic_num = 5 * 10000
    check_full_cnt = 0
    check_not_full_cnt = 0
    db_proxy = DbProxy(CONFIG_DB_NAME)
    while 1:
        try:
            # rows = new_send_cmd(TYPE_APP_SOCKET, "select volumenthreshold, dataperiod from dbcleanconfig where id=1", 1)
            _, rows = db_proxy.read_db("select volumenthreshold, dataperiod from dbcleanconfig where id=1")
            threshold = rows[0][0] / 100.0
            threshold_size = totalsize * threshold
            cursize = get_path_size("/data/mysql")
            if cursize > threshold_size:
                clean_incident_record(2, max_incident_num)
                clean_flow_record(2, max_proto_num)
                clean_traffic_record(2, max_traffic_num)
                check_not_full_cnt = 0
                if check_full_cnt < 2:
                    check_full_cnt += 1
                if check_full_cnt == 1:
                    msg = {}
                    msg['Type'] = SYSTEM_TYPE
                    msg['LogLevel'] = LOG_ALERT
                    msg['Content'] = "超过数据库存储空间上限".decode("UTF-8")
                    msg['Componet'] = "mysql"
                    send_log_db(MODULE_SYSTEM, msg)
            else:
                if check_not_full_cnt < 3:
                    check_not_full_cnt += 1
                if check_not_full_cnt == 3:
                    check_full_cnt = 0
                time.sleep(30)
        except:
            logger.error(traceback.format_exc())

def db_clean_his_record():
    # TODO: wait for receive thread start
    time.sleep(30)

    max_incident_num = db_record_limit["incident"]
    max_proto_num = db_record_limit["protocol"]
    max_traffic_num = db_record_limit["traffic"]

    while 1:
        try:
            clean_incident_record(1, max_incident_num)
            clean_flow_record(1, max_proto_num)
            clean_traffic_record(1, max_traffic_num)
        except:
            logger.error(traceback.format_exc())
        time.sleep(30)



class DbSocket(Daemon):
    def setup_logger(self):
        output_file = '/data/log/flask_db_socket.log'
        logger = logging.getLogger('flask_db_socket_log')
        logger.setLevel(GetLogLevelConf())
        # create a rolling file handler
        try:
            handler = RotatingFileHandler(output_file, mode='a',
                                      maxBytes=1024 * 1024 * 10, backupCount=10)
        except:
            handler = SysLogHandler()
        handler.setLevel(GetLogLevelConf())
        handler.setFormatter(logging.Formatter("[%(asctime)s -%(levelname)5s- %(filename)20s:%(lineno)3s]    %(message)s"))
        logger.addHandler(handler)

    def run(self):
        global tables_name
        global RECVSOCKADDR
        global dict_table_list
        flag_corner = "/data/sock/flag_corner"
        self.setup_logger()
        logger = logging.getLogger('flask_db_socket_log')

        app_sock = init_socket(TYPE_APP_SOCKET)
        try:
            if os.path.exists(write_addr):
                os.remove(write_addr)
            if os.path.exists(read_addr):
                os.remove(read_addr)
            if os.path.exists(file_addr):
                os.remove(file_addr)
            if os.path.exists(deploy_addr):
                os.remove(deploy_addr)

            if os.path.exists(flag_corner):
                os.remove(flag_corner)
            if os.path.exists(count_opp_addr):
                os.remove(count_opp_addr)
        except:
            logger.error("mw socket file not exist")
        db_write_sock=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
        db_read_sock=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
        db_file_sock=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
        db_deploy_sock=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
        db_count_opp_sock=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)

        db_write_sock.bind(write_addr)
        db_read_sock.bind(read_addr)
        db_file_sock.bind(file_addr)
        db_deploy_sock.bind(deploy_addr)
        db_count_opp_sock.bind(count_opp_addr)

        file_cmd_list = Queue.Queue(maxsize = 100)
        deploy_cmd_list = Queue.Queue(maxsize = 10)
        count_complex_tbl = Queue.Queue(maxsize = 100)
        oper_cmd_q_list = []
        result_queue=Queue.Queue(maxsize = 10)

        try:
            for tab in tables_name:
                thread.start_new_thread(insert_complex_tbl, (dict_table_list[tab], tab))
            for i in range(0,10):
                oper_cmd_q_list.append(Queue.Queue(maxsize = 10))
                thread.start_new_thread(count_opp_sub_tbl, (oper_cmd_q_list[i],result_queue,i))
            thread.start_new_thread(count_opp_complex_tbl, (count_complex_tbl, oper_cmd_q_list, result_queue, db_count_opp_sock,))
        except:
            logger.error("Error: unable to start thread")

        try:
            thread.start_new_thread(recv_write_db_oper, (dict_table_list, db_write_sock,))
            thread.start_new_thread(recv_read_db_oper, (count_complex_tbl, db_read_sock,))
            thread.start_new_thread(recv_file_db_oper, (file_cmd_list, db_file_sock,))
            thread.start_new_thread(recv_deploy_db_oper, (deploy_cmd_list, db_deploy_sock,))

            thread.start_new_thread(file_db_oper, (file_cmd_list,db_file_sock, ))
            thread.start_new_thread(deploy_db_oper, (deploy_cmd_list,db_deploy_sock, ))
            thread.start_new_thread(db_delete_his_record, ())
            thread.start_new_thread(db_clean_his_record, ())

            logger.info("Init trafficProcess!")
            traffic = ipTraffic()
            traffic.setDaemon(True)
            traffic.start()
            logger.info("ipTraffic OK!")

            logger.info("Init protAuditProcess!")
            ProtAudit = protAudit()
            ProtAudit.setDaemon(True)
            ProtAudit.start()
            logger.info("protAudit OK!")

            logger.info("Init protoBehaviorAuditProcess!")
            protoBehaviorAudit = protoBhvAudit()
            protoBehaviorAudit.setDaemon(True)
            protoBehaviorAudit.start()
            logger.info("protoBehaviorAudit OK!")

            logger.info("Init devAutoIdentifyProcess!")
            DevAutoIdentify = devAutoIdentify()
            DevAutoIdentify.setDaemon(True)
            DevAutoIdentify.start()
            logger.info("devAutoIdentify OK!")

            logger.info("Init autoGetSwitchInfoProcess!")
            switch_info = autoGetSwitchInfo()
            switch_info.setDaemon(True)
            switch_info.start()
            logger.info("autoGetSwitchInfo OK!")

            logger.info("Init whitelistStudy!")
            wls = whitelistStudy()
            wls.setDaemon(True)
            wls.start()
            logger.info("whitelistStudy OK!")

            logger.info("Init sendincident Send!")
            slog = SendIncident()
            slog.setDaemon(True)
            slog.start()
            logger.info("sendincident OK!")

            logger.info("Init StatusSwitch Send!")
            switch = StatusSwitch()
            switch.setDaemon(True)
            switch.start()
            logger.info("StatusSwitch OK!")

            logger.info("Init devonline!")
            dev_online = DeviceOnline()
            dev_online.setDaemon(True)
            dev_online.start()
            logger.info("devonline OK!")

            cmdHander = CommanddHanderThread(app_sock)
            cmdHander.setDaemon(True)
            cmdHander.start()
            os.system("touch %s"%flag_corner)
        except:
            logger.error("Error: unable to start thread")
            logger.error(traceback.format_exc())
        while 1:
            time.sleep(10)

class CommanddHanderThread(threading.Thread):
    def __init__(self,sock):
        threading.Thread.__init__(self)
        self.scheduler = BackgroundScheduler()
        self.server_socket = sock

    def deal_global_buffer(self):
        # global_function.global_var.deviceinfo_list.clear()
        global_function.global_var.whitelist_info = []
        global_function.global_var.top_list = []
        global_function.global_var.macfilter_list = []
        global_function.global_var.ipmac_list = []

        db_proxy = DbProxy(CONFIG_DB_NAME)
        result, rows = db_proxy.read_db("select ip,mac,proto from topdevice")
        for info in rows:
            tmpinfo = topdeviceinfo()
            tmpinfo.ip = info[0]
            tmpinfo.mac = info[1]
            tmpinfo.proto = info[2]
            if tmpinfo.ip:
                topinfo = "%s" % info[0]
            else:
                topinfo = "%s" % info[1]
            global_function.global_var.top_list.append(topinfo)

        result, rows = db_proxy.read_db("select ip from ipmaclist where ipmac_id>1")
        for info in rows:
            ipinfo = "%s" % info[0]
            global_function.global_var.ipmac_list.append(ipinfo)

        result, rows = db_proxy.read_db("select filterfields from rules")
        for info in rows:
            global_function.global_var.whitelist_info.append(info[0])

        result, rows = db_proxy.read_db("select mac from mac_filter")
        for m in rows:
            global_function.global_var.macfilter_list.append(m[0])

    def scheduler_hander(self, msg):
        logger = logging.getLogger('flask_db_socket_log')
        ret = {}
        try:
            if msg['cmd'] == 'start_whitelist_study':
                '''
                if msg['clear'] == 1:
                    deviceinfo_list.clear()
                    whitelist_info[:] = []
                '''
                self.deal_global_buffer()
                start_time = datetime.datetime.strptime(msg['starttime'],'%Y-%m-%d %X')
                stop_time = start_time + datetime.timedelta(seconds=int(msg['duration'])*60)
                if start_time <= datetime.datetime.now():
                    white_list_start_timer(msg['clear'])
                else:
                    self.scheduler.add_job(id='id_start_whitelist_study', func=white_list_start_timer, next_run_time=start_time, args=[msg['clear']])
                self.scheduler.add_job(id='id_stop_whitelist_study', func=white_list_stop_timer, next_run_time=stop_time)
            elif msg['cmd'] == 'stop_whitelist_study':
                switch_whitelist_status(0)
                if self.scheduler.get_job('id_start_whitelist_study') != None:
                    self.scheduler.remove_job('id_start_whitelist_study')
                if self.scheduler.get_job('id_stop_whitelist_study') != None:
                    self.scheduler.remove_job('id_stop_whitelist_study')
                sock = socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
                sock.sendto("2", dst_machine_learn_ctl_addr)
        except:
            logger.error(traceback.format_exc())
            ret['status'] = 0
            return ret
        ret['status'] = 1
        return ret

    def whitelist_study_check(self):
        logger = logging.getLogger('flask_db_socket_log')
        startTime = ''
        dur_time = 0
        status = 0
        clear = 0 # whether clear the old white list record

        db_proxy = DbProxy(CONFIG_DB_NAME)
        sql_str = "select startTime,durTime,status from whiteliststudy where id=1"
        result, rows = db_proxy.read_db(sql_str)
        logger.info("%s, get whiteliststudy status, rows:%s" % (sys._getframe().f_code.co_name, rows))
        if result == 0:
            startTime = rows[0][0]
            dur_time = rows[0][1]
            status = rows[0][2]
            logger.info("%s, starttime:%s, dur:%d, status:%d" % (sys._getframe().f_code.co_name, startTime, dur_time, status))

            if status == None or status == 0:
                logger.info("%s, whitelist study is disable status" % (sys._getframe().f_code.co_name))
                return

            start_time = datetime.datetime.strptime(startTime, '%Y-%m-%d %X')
            stop_time = start_time + datetime.timedelta(seconds=dur_time * 60)
            now = datetime.datetime.now()
            logger.info("%s, now:%s, start_time:%s, stop_time:%s" % (sys._getframe().f_code.co_name, now, start_time, stop_time))
            if now <= start_time:
                logger.info("%s, add 2 scheduler job for start/stop timer" % (sys._getframe().f_code.co_name))
                self.deal_global_buffer()
                self.scheduler.add_job(id='id_start_whitelist_study', func=white_list_start_timer, next_run_time=start_time+datetime.timedelta(seconds=2), args=[clear])
                self.scheduler.add_job(id='id_stop_whitelist_study', func=white_list_stop_timer, next_run_time=stop_time)
            elif start_time < now and now < stop_time:
                logger.info("%s, excute starttimer's handler, add 1 scheduler job for stop timer" % (sys._getframe().f_code.co_name))
                self.deal_global_buffer()
                try:
                    white_list_start_timer(clear)
                except:
                    logger.error(traceback.format_exc())
                self.scheduler.add_job(id='id_stop_whitelist_study', func=white_list_stop_timer, next_run_time=stop_time+datetime.timedelta(seconds=2))
            elif now >= stop_time:
                logger.info("%s, excute stoptimer's handler" % (sys._getframe().f_code.co_name))
                try:
                    white_list_stop_timer()
                except:
                    logger.error(traceback.format_exc())

    def run(self):
        logger = logging.getLogger('flask_db_socket_log')
        sock = self.server_socket
        addr = None
        data = None
        self.scheduler.start()
        self.whitelist_study_check()
        while True:
            try:
                data, addr = sock.recvfrom(512)
            except:
                logger.error(traceback.format_exc())
            if not data:
                continue
            msg = json.loads(data.lower())
            if msg['type'] == 'scheduler':
                ret = self.scheduler_hander(msg)

            try:
                sock.sendto(json.dumps(ret), addr)
            except:
                logger.error(traceback.format_exc())
def main():
    # global g_sqlite_file_lock
    app_name = os.path.basename(os.path.realpath(__file__))
    if common_helper.process_already_running(app_name):
        print(app_name+' is already running. Abort!')
        return
    #affinity.set_process_affinity_mask(os.getpid(), 0xeL)
    os.system('mkdir -p /tmp/sock')
    create_mac_dict()
    # os.system('touch %s' % g_sqlite_file_lock)
    # init_sqlite()
    daemon = DbSocket('/dev/null', '/dev/null', '/data/log/bati_error.log')
    if os.path.exists('/data/log/bati_error.log') is False:
        os.mknod('/data/log/bati_error.log')
    daemon.start()

if __name__ == "__main__":
    main()
