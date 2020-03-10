# -*- coding:UTF-8 -*-


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


"""
create_table_sql

table associate_rules:
CREATE TABLE `associate_rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rule_name` varchar(64) DEFAULT NULL,
  `src_addr` varchar(64) DEFAULT NULL,
  `src_port` int(11) DEFAULT NULL,
  `dst_addr` varchar(64) DEFAULT NULL,
  `dst_port` varchar(64) DEFAULT NULL,
  `src_addr` varchar(64) DEFAULT NULL,
  `src_addr` varchar(64) DEFAULT NULL,
  `src_addr` varchar(64) DEFAULT NULL,
  `src_addr` varchar(64) DEFAULT NULL,
  `src_addr` varchar(64) DEFAULT NULL,
  `src_addr` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyIsam DEFAULT CHARSET=utf8;



"""


class AssociEventProcess(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        logger = logging.getLogger('flask_incident_log')
        logger.info("AssociEventProcess start....")
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
                    # logger.error('led_display -d /dev/ttyS1 -s 2 "Event :%s"' % (noreadevent))
            except:
                logger.error(traceback.format_exc())
            time.sleep(5)


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
        Box_Time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
        if g_dpi_plat_type == DEV_PLT_MIPS:
            command = "ntpd -qn -p " + destIp + " ;echo $?"
        else:
            command = "ntpdate -u " + destIp + " ;echo $?"
        logger.info(command)
        handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
                # timeArray = time.strptime(synTime[0], "%Y-%m-%d %H:%M:%S")
                # Ntp_Server_Time = time.strftime("%Y-%m-%dT%H:%M:%SZ", timeArray)
                if g_dpi_plat_type == DEV_PLT_MIPS:
                    os.system('hwclock -w -u')
                now = time.time()
                Ntp_Server_Time = time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(now + 3600 * 8))

                if g_dpi_plat_type == DEV_PLT_MIPS:
                    timeoffsetRe = re.compile('(\d+.\d+)s').findall(ntpSynString)
                else:
                    timeoffsetRe = re.compile('\d+.\d+\s*sec').findall(ntpSynString)
                try:
                    # timeOffsetStr = timeoffsetRe[0]
                    # start_pos = timeOffsetStr.find(' sec')
                    # tmp_offset = timeOffsetStr[0:start_pos]
                    # if float(tmp_offset) >= 60:     # 误差在60s以上，才更新
                    ntp_res_dict = {'msg_type': 1, 'data': Ntp_Server_Time}
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
        output_file = '/data/log/incident_analysis.log'
        logger = logging.getLogger('flask_incident_log')
        logger.setLevel(GetLogLevelConf())
        try:
            handler = RotatingFileHandler(output_file, mode='a',
                                          maxBytes=1024 * 1024 * 10, backupCount=10)
        except:
            handler = SysLogHandler()
        handler.setLevel(GetLogLevelConf())
        handler.setFormatter(logging.Formatter("[%(asctime)s -%(levelname)5s- %(filename)20s:%(lineno)3s] %(message)s",
                                               "%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)

    def run(self):
        self.setup_logger()
        logger = logging.getLogger('flask_incident_log')
        os.system('mkdir -p /tmp/sock')
        create_mac_dict()
        try:
            accessIp_init()

            logger.info("Init SystemIncident!")
            systemIncident = SystemIncident()
            systemIncident.setDaemon(True)
            systemIncident.start()
            logger.info("SystemIncident OK!")

            logger.info("flow audit!")
            FlowAudit = flowAudit()
            FlowAudit.setDaemon(True)
            FlowAudit.start()
            logger.info("flow audit OK!")

            logger.info("Init log server!")
            logServer = LogServer()
            logServer.setDaemon(True)
            logServer.start()
            logger.info("Log server OK!")

            try:
                os.system("touch %s" % flag_machine)
            except:
                logger.error(traceback.format_exc())
            logServer.join()
        except:
            tb = traceback.format_exc()
            logger.error(tb)


def main():
    app_name = os.path.basename(os.path.realpath(__file__))
    if common_helper.process_already_running(app_name):
        print(app_name + ' is already running. Abort!')
        return

    daemon = flask_mw('/dev/null', '/dev/null', '/data/log/owen_error.log')
    if os.path.exists('/data/log/owen_error.log') is False:
        os.mknod('/data/log/owen_error.log')
    daemon.start()


if __name__ == '__main__':
    main()
