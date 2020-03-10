# -*- coding:UTF-8 -*-
from global_function.get_tcpdump_result import GetTcpdumpResult

__author__ = 'gaofei'

import threading
from logging.handlers import RotatingFileHandler
from logging.handlers import SysLogHandler
from common.daemon import Daemon
from common import common_helper
from global_function.log_server import LogServer
from global_function.system_incident import SystemIncident
from global_function.unknown_device import unknownDevice
from global_function.flow_audit import flowAudit
from global_function.hw_check import hd_raid_check
from global_function.log_config import *
from global_function.flow_learn import flow_band_learn_ctl
from global_function.flow_learn import flow_band_proc
from global_function.flow_learn import flow_alarm_proc
from app.sysconfbackup import sys_backup_init
from app.reportgen import report_gen_init
from app.deviceinfo import accessIp_init
from global_function.log_oper import *
from global_function.securitylog_send import *


class LedProcess(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        logger = logging.getLogger('flask_mw_log')
        logger.info("LedProcess start....")
        db_proxy = DbProxy()
        while 1:
            try:
                safeevent_allSafeEvent = 0
                readNum = 0
                safeevent_noReadSafeEvent = 0

                result, rows = db_proxy.read_db("SELECT count(*) from incidents")
                if result == 0 and rows[0][0]:
                    safeevent_allSafeEvent = rows[0][0]

                result, rows = db_proxy.read_db("select sum(incidentstat.read) from incidentstat")
                if result == 0 and rows[0][0]:
                    readNum = rows[0][0]

                safeevent_noReadSafeEvent = safeevent_allSafeEvent - readNum
                if result == 0:
                    noreadevent = safeevent_noReadSafeEvent
                    res = commands.getoutput('led_display -d /dev/ttyS1 -s 2 "Event :%s"' % (noreadevent))
                    #logger.error('led_display -d /dev/ttyS1 -s 2 "Event :%s"' % (noreadevent))
            except:
                logger.error(traceback.format_exc())
            time.sleep(300)

def get_new_disk_flag():
    logger = logging.getLogger('flask_mw_log')
    if os.path.exists("/preserve/dpi_flag/new_disk.flag"):
        try:
            msg = {}
            msg['Type'] = SYSTEM_TYPE
            msg['LogLevel'] = LOG_INFO
            msg['Content'] = "已成功替换异常磁盘".decode("UTF-8")
            msg['Componet'] = "disk"
            send_log_db(MODULE_SYSTEM, msg)
            logger.info("send syslog for new disk")
            os.system("rm -f /preserve/dpi_flag/new_disk.flag")
        except:
            logger.exception("Exception Logged")

    else:
        logger.info("no new_disk.flag")



remote_ntp_syn_addr = '/data/sock/ntp_syn_sock'
ntp_send_addr = '/data/sock/ntp_send_sock'

class NtpdProcess(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        try:
            if os.path.exists(ntp_send_addr):
                os.remove(ntp_send_addr)
        except:
            pass
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.sock.bind(ntp_send_addr)
        self.sock.settimeout(5)
        
    def run(self):
        # init_sqlite()
        logger = logging.getLogger('flask_mw_log')
        logger.info("ntpd start....")
        db_proxy = DbProxy(CONFIG_DB_NAME)

        while 1:
            try:
                # rows = new_send_cmd(TYPE_APP_SOCKET,"SELECT mode,synDestIp FROM managementmode", 1)
                _, rows = db_proxy.read_db("SELECT mode,synDestIp FROM managementmode")
                values = rows[0]
                if values[0] == 1 and values[1] != "127.0.0.1":
                    self.get_ntp_syn_stat(values[1])
            except:
                logger.error(traceback.print_exc())
            time.sleep(10)

    def get_ntp_syn_stat(self, destIp):
        logger = logging.getLogger('flask_mw_log')
        now = time.time()
        Box_Time = time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(now))
        if g_dpi_plat_type == DEV_PLT_MIPS:
            command = "ntpd -qn -p "+destIp+" ;echo $?"
        else:
            command = "ntpdate -u "+destIp+" ;echo $?"
        logger.info(command)
        handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)    
        ntpSynString = ''
        for line in handle.stdout.readlines():
            ntpSynString += line

        result = 1
        timeOffsetStr = None
        Ntp_Server_Time = Box_Time
        ntpSynString = ntpSynString.strip()

        if ntpSynString == '0':
            if g_dpi_plat_type == DEV_PLT_MIPS:
                os.system('hwclock -w -u')
            timeOffsetStr = "0"
        else:
            if g_dpi_plat_type == DEV_PLT_MIPS:
                syn_state = re.compile('\d{4}-\d+-\d+\s+\d+:\d+:\d+').findall(ntpSynString)
            else:
                syn_state = re.compile('\s+offset\s+').findall(ntpSynString)

            if syn_state:
                #timeArray = time.strptime(synTime[0], "%Y-%m-%d %H:%M:%S")
                #Ntp_Server_Time = time.strftime("%Y-%m-%dT%H:%M:%SZ", timeArray)
                if g_dpi_plat_type == DEV_PLT_MIPS:
                    os.system('hwclock -w -u')
                now = time.time()
                Ntp_Server_Time = time.strftime("%Y/%m/%d %H:%M:%S",time.gmtime(now + 3600*8))

                if g_dpi_plat_type == DEV_PLT_MIPS:
                    timeoffsetRe = re.compile('(\d+.\d+)s').findall(ntpSynString)
                else:
                    timeoffsetRe = re.compile('\d+.\d+\s*sec').findall(ntpSynString)
                try:
                    #timeOffsetStr = timeoffsetRe[0]
                    #start_pos = timeOffsetStr.find(' sec')
                    #tmp_offset = timeOffsetStr[0:start_pos]
                    #if float(tmp_offset) >= 60:     # 误差在60s以上，才更新
                    ntp_res_dict = {'msg_type':1, 'data':Ntp_Server_Time}
                    self.sock.sendto(json.dumps(ntp_res_dict), remote_ntp_syn_addr)
                except:
                    pass
            else:
                result = 0
                timeOffsetStr = "UnKnown"
                logger.info("--------- ntp syn failed-------")
                logger.info(destIp)

class flask_mw(Daemon):
    def setup_logger(self):
        output_file = '/data/log/flask_mw.log'
        logger = logging.getLogger('flask_mw_log')
        logger.setLevel(GetLogLevelConf())
        # create a rolling file handler
        try:
            handler = RotatingFileHandler(output_file, mode='a',
                                      maxBytes=1024 * 1024 * 10, backupCount=10)
        except:
            handler = SysLogHandler()
        handler.setLevel(GetLogLevelConf())
        handler.setFormatter(logging.Formatter("[%(asctime)s -%(levelname)5s- %(filename)20s:%(lineno)3s] %(message)s","%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
        
    def run(self):
        self.setup_logger()
        logger = logging.getLogger('flask_mw_log')
        init_dpi_type_info()
        init_hw_type_info()
        get_new_disk_flag()
        # init_sqlite()
        sys_backup_init()
        report_gen_init()
        flag_machine = "/data/sock/flag_machine"
        if os.path.exists(flag_machine):
            os.remove(flag_machine)

        os.system('mkdir -p /tmp/sock')
        create_mac_dict()
        #run_mode = send_read_cmd(TYPE_FLASK_SOCKET,"select mode from managementmode")
        #for judge_mode in run_mode:
        #    mode = judge_mode[0]
        #self.log_conn.close()
        try:
            accessIp_init()

            logger.info("Init SystemIncident!")
            systemIncident = SystemIncident()
            systemIncident.setDaemon(True)
            systemIncident.start()
            logger.info("SystemIncident OK!")

            logger.info("Init NtpdProcess!")
            ntpdprocess = NtpdProcess()
            ntpdprocess.setDaemon(True) 
            ntpdprocess.start()
            logger.info("ntpdprocess OK!")

            logger.info("Init LedProcess!")
            Ledprocess = LedProcess()
            Ledprocess.setDaemon(True)
            Ledprocess.start()
            logger.info("LedProcess OK!")

            logger.info("Init unknownDevice!")
            unknownproc = unknownDevice()
            unknownproc.setDaemon(True)
            unknownproc.start()
            logger.info("unknownDevice OK!")
            
            #logger.info("Init trendAudit!")
            #trendAuditproc = trendAudit()
            #trendAuditproc.setDaemon(True)
            #trendAuditproc.start()
            #logger.info("trendAudit OK!")
            
            logger.info("flow audit!")
            FlowAudit = flowAudit()
            FlowAudit.setDaemon(True)
            FlowAudit.start()
            logger.info("flow audit OK!")

            logger.info("flow learn ctl!")
            FlowLearnCtl = flow_band_learn_ctl()
            FlowLearnCtl.setDaemon(True)
            FlowLearnCtl.start()
            logger.info("flow learn ctl OK!")

            logger.info("flow band proc!")
            FlowBandProc = flow_band_proc()
            FlowBandProc.setDaemon(True)
            FlowBandProc.start()
            logger.info("flow band proc OK!")

            logger.info("Init raid status check!")
            raid_status_thread = hd_raid_check()
            raid_status_thread.setDaemon(True)
            raid_status_thread.start()
            logger.info("raid status check OK!")

            logger.info("Init log server!")
            logServer = LogServer()                    
            logServer.setDaemon(True)                                                  
            logServer.start()
            logger.info("Log server OK!")

            logger.info("Init tcpdump Send!")
            get_tcpdump_result = GetTcpdumpResult()
            get_tcpdump_result.setDaemon(True)
            get_tcpdump_result.start()
            logger.info("tcpdump OK!")

            logger.info("Init SendTrafficIncident Send!")
            tra_incident = SendTrafficIncident()
            tra_incident.setDaemon(True)
            tra_incident.start()
            logger.info("SendTrafficIncident OK!")

            logger.info("Init TrafficStatusSwitch Send!")
            switch = TrafficStatusSwitch()
            switch.setDaemon(True)
            switch.start()
            logger.info("TrafficStatusSwitch OK!")

            logger.info("Init Securitylog Send!")
            slog = SecuritylogSend()
            slog.setDaemon(True)
            slog.start()
            logger.info("SecuritylogSend OK!")

            try:
                os.system("touch %s"%flag_machine)
            except:
                logger.error(traceback.format_exc())
            logServer.join()
        except:
            tb = traceback.format_exc()
            logger.error(tb)
        

def main():
    app_name = os.path.basename(os.path.realpath(__file__))
    if common_helper.process_already_running(app_name):
        print(app_name+' is already running. Abort!')
        return

    daemon = flask_mw('/dev/null','/dev/null','/data/log/owen_error.log')
    if os.path.exists('/data/log/owen_error.log') is False:
        os.mknod('/data/log/owen_error.log')
    daemon.start()


if __name__ == '__main__':
    main()
