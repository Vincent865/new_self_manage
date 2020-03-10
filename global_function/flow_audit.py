'''
flow audit handle msg from dpi
author: HanFei
'''
import threading
from log_oper import *


FLOW_AUFIT_SAVE_DAYS = 90
FLOW_AUDIT_SAVE_DIR = "/data/streambuild"
FLOW_AUDIT_SIZE_RANGE = 18 * 1024 * 1024 * 1024

logger = logging.getLogger('flask_mw_log')

class flowAudit(threading.Thread):
    '''flow audit thread,link to machinestate process'''
    def __init__(self):
        '''init flow audit object'''
        threading.Thread.__init__(self)
        logger.info("init flow audit ok!")

    def run(self):
        '''run flow audit obj'''
        flow_audit_addr = '/data/sock/flow_audit_sock'
        try:
            os.remove(flow_audit_addr)
        except:
            logging.error("flow audit socket file not exist")
        db_write_sock = socket.socket(socket. AF_UNIX, socket.SOCK_DGRAM)
        db_write_sock.bind(flow_audit_addr)
        db_proxy = DbProxy(CONFIG_DB_NAME)
        while True:
            try:
                data, addr = db_write_sock.recvfrom(4096)
            except:
                data = None
                logging.error("recive data error from flow audit socket")
            if data != None:
                '''
                split by ",", content as below:
                flow_info[1]  --  timestamp
                flow_info[2]  --  src_mac
                flow_info[3]  --  dst_mac
                flow_info[4]  --  src_ip
                flow_info[5]  --  src_port
                flow_info[6]  --  dst_ip
                flow_info[7]  --  dst_port
                flow_info[8]  --  protocal id
                flow_info[9]  --  filename
                flow_info[10]  --  sessionid
                '''
                flow_info = data.split(',')
                msg_type = flow_info[0]
                if msg_type == "1":
                    start_time_str = flow_info[1]
                    srcmac = flow_info[2]
                    dstmac = flow_info[3]
                    srcip = flow_info[4]
                    dstip = flow_info[5]
                    srcport = flow_info[6]
                    dstport = flow_info[7]
                    proto = flow_info[8]
                    filename = flow_info[9]
                    session_id = flow_info[10]
                    sql_str = "select count(sessionid) from nsm_flowaudit where sessionid = '%s'" \
                              % session_id
                    res, sql_res = db_proxy.read_db(sql_str)
                    if res == 0:
                        if sql_res[0][0] > 0:
                            continue
                    sql_str = '''insert into nsm_flowaudit (timestamp,srcmac,dstmac,srcip,dstip,
                              srcport,dstport, protoname, filename, sessionid) values('%s','%s','%s',
                              '%s','%s','%s','%s','%s', '%s', '%s')''' \
                              %(start_time_str, srcmac, dstmac, srcip, dstip, srcport, dstport, \
                                proto, filename, session_id)
                    db_proxy.write_db(sql_str)
                elif msg_type == "2":
                    session_id = flow_info[1]
                    filename = flow_info[2]
                    sql_str = '''insert into nsm_flowftpinfo (sessionid,filename) \
                    values('%s','%s')'''%(session_id, filename)
                    db_proxy.write_db(sql_str)
                elif msg_type == "3":
                    flow_audit_del_spare()
                    full_flag = flow_audit_check_full()
                    sql_str = "select fullflag from nsm_flowfull"
                    res, sql_res = db_proxy.read_db(sql_str)
                    if res == 0:
                        db_full_flag = sql_res[0][0]
                        msg = {}
                        if db_full_flag == 0 and full_flag == 1:
                            logger.error("flow file size is out of range")
                            content = "stream full"
                            db_proxy.write_db(sql_str)
                            sql_str = "update nsm_flowfull set fullflag = %d" % full_flag
                            db_proxy.write_db(sql_str)
                            msg['Type'] = SYSTEM_TYPE
                            msg['LogLevel'] = LOG_INFO
                            msg['Content'] = content
                            send_log_db(MODULE_SYSTEM, msg)
                        if db_full_flag == 1 and full_flag == 0:
                            logger.info("flow file size change normal")
                            content = "stream normal"
                            db_proxy.write_db(sql_str)
                            sql_str = "update nsm_flowfull set fullflag = %d" % full_flag
                            db_proxy.write_db(sql_str)
                            msg['Type'] = SYSTEM_TYPE
                            msg['LogLevel'] = LOG_INFO
                            msg['Content'] = content
                            send_log_db(MODULE_SYSTEM, msg)
                else:
                    continue

def flow_audit_get_start_time():
    '''Calc start time for deleting redundent flow audit info'''
    now_ticks = int(time.time())
    day1_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now_ticks))
    day1 = datetime.datetime.strptime(day1_str, '%Y-%m-%d %H:%M:%S')
    delta = datetime.timedelta(days=FLOW_AUFIT_SAVE_DAYS, seconds=0)
    day2 = day1 - delta
    day2_str = day2.strftime('%Y-%m-%d %H:%M:%S')
    return day2_str

def flow_audit_del_spare():
    '''
    delete flow audit info beyond 3 months
    '''
    db_proxy = DbProxy(CONFIG_DB_NAME)
    start_time = flow_audit_get_start_time()
    sql_str = "select sessionid, protoname, filename from nsm_flowaudit where timestamp < '%s' \
               order by timestamp asc" % start_time
    res, sql_res = db_proxy.read_db(sql_str)
    if res != 0:
        logger.error("flow_audit_del_spare, readdb error")
        return
    for elem in sql_res:
        sessionid = elem[0]
        proto = elem[1]
        ctl_file = elem[2]
        if proto == "ftp":
            sql_str = "select filename from nsm_flowftpinfo where sessionid = '%s'" % sessionid
            res, file_res = db_proxy.read_db(sql_str)
            for subelem in file_res:
                filename = FLOW_AUDIT_SAVE_DIR + "/" + subelem[0]
                zip_filename = FLOW_AUDIT_SAVE_DIR + "/" + subelem[0] + ".zip"
                os.system("rm -f %s" % filename)
                os.system("rm -f %s" % zip_filename)

            sql_str = "delete from nsm_flowftpinfo where sessionid = '%s'" % sessionid
            db_proxy.write_db(sql_str)
        filename = FLOW_AUDIT_SAVE_DIR + "/" + ctl_file
        zip_filename = FLOW_AUDIT_SAVE_DIR + "/" + ctl_file + ".zip"
        os.system("rm -f %s" % filename)
        os.system("rm -f %s" % zip_filename)
    sql_str = "delete from nsm_flowaudit where timestamp < '%s'" % start_time
    db_proxy.write_db(sql_str)
    return

def flow_audit_check_full():
    '''
    get size of flow audit files
    0 -- not full
    1 -- full
    '''


    if os.path.exists(FLOW_AUDIT_SAVE_DIR) == False:
        logger.error("flow file dir does not exists")
        return 0

    handle = subprocess.Popen("du -s /data/streambuild",
                    stdin = subprocess.PIPE,
                    stdout = subprocess.PIPE,
                    stderr = subprocess.PIPE,
                    shell = True)
    handle.wait()
    cap_str = handle.stdout.read()
    cap_val = int(cap_str.split("\t")[0].strip())
    if cap_val * 1024 >= FLOW_AUDIT_SIZE_RANGE:
        return 1
    else:
        return 0



