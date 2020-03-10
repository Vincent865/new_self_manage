# -*- coding: utf-8 -*-
import random
import sys
from logging.handlers import RotatingFileHandler
from logging.handlers import SysLogHandler
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('/app/local/share/new_self_manage')
sys.path.append('/app/lib/python2.7/site-packages/')
from common.daemon import Daemon
from global_function.log_config import *
from global_function.log_oper import *

LogConfig('flask_db_socket.log')

class DbClean(Daemon):
    
    def clean_incidents(self,period):
        logger = logging.getLogger('db_clean_log')
        result = 0
        db_proxy = DbProxy()
        nowtime = datetime.datetime.now()
        preHours = nowtime + datetime.timedelta(days=-period)
        # preHours = nowtime + datetime.timedelta(days =+ period) # TODO��for test
        last_date_str = preHours.strftime("%Y-%m-%d") + " " + preHours.strftime("%H") + ":00:00"
        preHoursNyr = int(time.mktime(time.strptime(last_date_str, '%Y-%m-%d %H:%M:%S')))

        selCmd = "select count(*) from incidents where timestamp < %d" % (preHoursNyr)
        res, rows = db_proxy.read_db(selCmd)
        if res == 0:
            total = rows[0][0]
            if total > 0 :
            # if total >= 0 : # TODO: for test
                try:
                    msg = {}
                    msg['Type'] = SYSTEM_TYPE
                    msg['LogLevel'] = LOG_ALERT
                    msg['Content'] = '数据库定期删除：删除'.decode("UTF-8") + str(period) + '天之前的安全事件。'.decode("UTF-8")
                    msg['Componet'] = "mysql"
                    send_log_db(MODULE_SYSTEM, msg)
                except:
                    logger.error(traceback.format_exc())

                delCmd = "delete from incidents where timestamp < %d"%(preHoursNyr)
                result = db_proxy.write_db(delCmd)

    def clean_flow(self,period):
        logger = logging.getLogger('db_clean_log')
        result = 0
        db_proxy = DbProxy()
        nowtime = datetime.datetime.now()
        preHours = nowtime + datetime.timedelta(days=-period)
        last_date_str = preHours.strftime("%Y-%m-%d") + " " + preHours.strftime("%H") + ":00:00"
        preHoursNyr = int(time.mktime(time.strptime(last_date_str, '%Y-%m-%d %H:%M:%S')))

        try:
            clean_flowheadid_sock_addr = '/data/sock/db_clean_flowheadid'
            clean_flowheadid_sock_client_addr = '/data/sock/db_clean_flowheadid_client_' + str(os.getpid()) + '_' + str(random.randint(1, 999999))
            db_clean_flowheadid_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            db_clean_flowheadid_sock.bind(clean_flowheadid_sock_client_addr)
        except:
            logger.error(traceback.format_exc())

        # log
        try:
            delete_log = 0
            for prot in flow_tables:
                delete_flag = 0
                sqlstr = "select count(*) from %s where packetTimestamp < %d"%(prot, preHoursNyr)
                res, sqlres = db_proxy.read_db(sqlstr)
                if res != 0:
                    continue

                if sqlres[0][0] > 0:
                    delete_flag = 1
                    delete_log = 1
                if delete_flag == 1:
                    getFlowCmd = "select distinct flowdataHeadId from %s where packetTimestamp < %d"%(prot, preHoursNyr)
                    result,allFlowHeadId = db_proxy.read_db(getFlowCmd)
                    delCmd = "delete from %s where packetTimestamp< %d"%(prot, preHoursNyr)
                    result = db_proxy.write_db(delCmd)
                    for headIdvalue in allFlowHeadId:
                        headId = headIdvalue[0]
                        countCmd = "select count(*) from %s where flowdataHeadId=%d"%(prot,headId)
                        result,num = db_proxy.read_db(countCmd)
                        nums = num[0][0]
                        if nums ==0:
                            delFlowCmd = "delete from flowdataheads where flowdataHeadId=%d"%(headId)
                            result = db_proxy.write_db(delFlowCmd)
                            db_clean_flowheadid_sock.sendto(str(headId),clean_flowheadid_sock_addr)
            if delete_log == 1:
                msg = {}
                msg['Type'] = SYSTEM_TYPE
                msg['LogLevel'] = LOG_ALERT
                msg['Content'] = '数据库定期删除：删除'.decode("UTF-8") + str(period) + '天之前的协议审计记录。'.decode("UTF-8")
                msg['Componet'] = "mysql"
                send_log_db(MODULE_SYSTEM, msg)
        except:
            logger.error(traceback.format_exc())
        try:
            db_clean_flowheadid_sock.close()
            os.remove(clean_flowheadid_sock_client_addr)
        except:
            logger.error(traceback.format_exc())

        
    def clean_traffic(self,period):
        logger = logging.getLogger('db_clean_log')
        result = 0
        db_proxy = DbProxy()
        nowtime = datetime.datetime.now()
        preHours = nowtime + datetime.timedelta(days=-period)
        preHoursNyr = preHours.strftime("%Y-%m-%d %H:%M:%S")

        selCmd = "select count(*) from icdevicetraffics where timestamp<'%s'" % (preHoursNyr)
        res, rows = db_proxy.read_db(selCmd)
        if res == 0:
            total = rows[0][0]
            if total > 0:
            # if total >= 0 : # TODO: for test
                try:
                    msg = {}
                    msg['Type'] = SYSTEM_TYPE
                    msg['LogLevel'] = LOG_ALERT
                    msg['Content'] = '数据库定期删除：删除'.decode("UTF-8") + str(period) + '天之前的流量审计。'.decode("UTF-8")
                    msg['Componet'] = "mysql"
                    send_log_db(MODULE_SYSTEM, msg)
                except:
                    logger.error(traceback.format_exc())

                delCmd = "delete from icdevicetraffics where timestamp<'%s'"%(preHoursNyr)
                result = db_proxy.write_db(delCmd)

        delCmd = "delete from icdevicetrafficstats where timestamp<'%s'"%(preHoursNyr)
        result = db_proxy.write_db(delCmd)

    def setup_logger(self):
        output_file = '/data/log/db_clean.log'
        logger = logging.getLogger('db_clean_log')
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
        db_proxy = DbProxy(CONFIG_DB_NAME)
        # init_sqlite()
        period = 0
        # rows = new_send_cmd(TYPE_APP_SOCKET, "select volumenthreshold, dataperiod from dbcleanconfig where id=1", 1)
        _, rows = db_proxy.read_db("select volumenthreshold, dataperiod from dbcleanconfig where id=1")
        period = rows[0][1]
        if period == 0:
            return
        else:
            self.clean_incidents(period)
            self.clean_flow(period)
            self.clean_traffic(period)
            return
    

def main():
    daemon = DbClean('/dev/null','/dev/null','/data/log/dbclean_error.log')
    if os.path.exists('/data/log/dbclean_error.log') is False:
        os.mknod('/data/log/dbclean_error.log')
    daemon.start()
    
if __name__ == "__main__":
    main()
