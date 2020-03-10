# -*- coding:UTF-8 -*-
import threading
import syslog
import logging
from log_oper import *
from global_function.cmdline_oper import *
from global_function.log_oper import *

logger = logging.getLogger('flask_db_socket_log')

class ipTraffic(threading.Thread):
    '''ip traffic thread,link to machinestate process'''
    def __init__(self):
        '''init ipTraffic object'''
        threading.Thread.__init__(self)
        self.dev_list = []
        self.dev_num_limit = 0
        self.dev_exceed_limit = False
        self.db_proxy = DbProxy(CONFIG_DB_NAME)
        self.time_queue = Queue.Queue(maxsize=queue_limit["ipTraffic"])
        self.protocolTuple = (
            'equipment',
            'Modbus-TCP',
            'OPCDA',
            'IEC104',
            'DNP3',
            'MMS',
            'S7',
            'PROFINET-IO',
            'GOOSE',
            'SV',
            'ENIP',
            'tradition_pro',
            'OPCUA-TCP',
            'PNRT-DCP',
            'FOCAS',
            'SIP',
            'ORACLE',
            'SQL-Server',
            'S7PLUS',
            'HTTP',
            'FTP',
            'SNMP',
            'TELNET',
            'POP3',
            'SMTP',
            'unknown'
        )

    def getProtoNameByID(self, id):
        if id < len(self.protocolTuple):
            return self.protocolTuple[id]
        elif id > 500:
            cmd_str = "select proto_name from self_define_proto_config where proto_id = %d" % id
            # rows = new_send_cmd(TYPE_APP_SOCKET, cmd_str, 1)
            res, rows = self.db_proxy.read_db(cmd_str)
            if len(rows) == 0:
                return "unknown"
            data = "unknown"
            for row in rows:
                row = list(row)
                data = row[0]
            data = data.encode('utf-8')
            return data
        else:
            return "unknown"

    def run(self):
        '''run ipTraffic obj'''
        self.classInit()

        # summary one hour data and delete one week ago data
        t1 = threading.Thread(target=self.runGetTrafficData)
        t1.setDaemon(True)
        t1.start()

        t2 = threading.Thread(target=self.runTrafficDataSummary)
        t2.setDaemon(True)
        t2.start()

        t3 = threading.Thread(target=self.generate_industry_device_data)
        t3.setDaemon(True)
        t3.start()

        t3.join()

    def classInit(self):
        db_proxy = DbProxy()
        # db_proxy.write_db("delete from dev_band_20s")
        # db_proxy.write_db("delete from icdevicetraffics")
        # db_proxy.write_db("delete from sorted_dev_traffic_1h")
        # db_proxy.write_db("delete from icdevicetrafficstats")
        # db_proxy.write_db("delete from dev_his_traffic")
        # db_proxy.write_db("delete from safedevpoint")
        db_proxy.write_db("update machinesession set sessioncount = 0")

        dpiinfo = get_webdpi_obj()
        dpiip,pro_info,ver_info,sn_info,mw_ip = dpiinfo.getdpiinfo()
        if pro_info.find("U1000") != -1:
            self.dev_num_limit = 3000
        elif pro_info.find("IMAP") != -1:
            self.dev_num_limit = 1000
        else:
            self.dev_num_limit = 200
        logger.info("pro_info:%s dev_num_limit:%s" % (pro_info, self.dev_num_limit))

    def runGetTrafficData(self):
        try:
            db_proxy = DbProxy()
            self.init_safedevpoint(db_proxy)
        except:
            logger.error(traceback.format_exc())
        self.getTrafficData(db_proxy)


    def getTrafficData(self, db_proxy):
        '''get ip traffic data from c program'''
        traffic_addr = '/data/sock/traffic_sock'
        try:
            if os.path.exists(traffic_addr):
                os.remove(traffic_addr)
        except:
            logger.error(traceback.format_exc())
        db_write_sock = socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
        db_write_sock.bind(traffic_addr)
        # safe device report traffic every 5s even if receive bytes is 0
        time_5s_count = 0
        safe_dev_20s_bytes = 0
        while True:
            try:
                data, addr = db_write_sock.recvfrom(256)
                logger.error(data)
                data = data.split('----')[0].split(';')
                # data[0] 1 network device£ 0 security device
                device_type = data[0]
                del data[0]
                #data[0]-protocol id; data[1]-timestamp; data[2]-ip; data[3]-mac; data[4]-sendBytes; data[5]-receiveBytes; data[6]-deviceid
                sendSpeed = int(round(int(data[4])/5.0))
                recvSpeed = int(round(int(data[5])/5.0))

                if device_type == '0':
                    if data[0] == '0':
                        # icdevicetraffics 中5s一条默认数据
                        default_str = '''insert into icdevicetraffics (iCDeviceIp,iCDeviceMac,iCDeviceId, trafficType,
                        trafficName,sendSpeed,recvSpeed,timestamp) values('default','default','default',-1,'default',0,0,'%s')'''%data[1]
                        # SqlQueueIn('icdevicetraffics', default_str)
                        db_proxy.write_db(default_str)

                        time_5s_count += 1
                        safe_dev_20s_bytes += sendSpeed
                        if time_5s_count == 4:
                            sendSpeed = int(round(safe_dev_20s_bytes/512.0))  # Kbps bytes/4/1024*8
                            time_5s_count = 0
                            safe_dev_20s_bytes = 0
                            sql_str = "insert into safedevpoint (timestamp, sendSpeed) values('%s', %d)"%(data[1], sendSpeed)
                            db_proxy.write_db(sql_str)
                            if self.time_queue.full():
                                continue
                            self.time_queue.put(data[1])
                else:
                    if self.is_useful_data(data[6], db_proxy):
                        sql_str = '''insert into icdevicetraffics (iCDeviceIp,iCDeviceMac,iCDeviceId, trafficType,\
                        trafficName,sendSpeed,recvSpeed,timestamp) values('%s','%s','%s',%s,'%s',%d,%d,'%s'
                        )'''%(data[2],data[3],str(data[6]),data[0],self.getProtoNameByID(int(data[0])),sendSpeed,recvSpeed,data[1])
                        db_proxy.write_db(sql_str)
                        # )'''%(data[2],data[3],str(data[6]),data[0],self.protocolTuple[int(data[0])],sendSpeed,recvSpeed,data[1])
                        # SqlQueueIn('icdevicetraffics',sql_str)
            except:
                logger.error("receive data error!! data:%s" % str(data))
                logger.error("protocolTuple:%s" % str(self.protocolTuple))
                logger.exception("Exception Logged")


    def is_useful_data(self, devid, db_proxy):
        # U1000: 3000台设备 ;IMAP：1000台设备; C200：200台设备
        if devid in self.dev_list:
            flag = True
        else:
            if len(self.dev_list) >= self.dev_num_limit:
                flag = False
                if self.dev_exceed_limit is False:
                    logger.info("device num: %s, stop receive new data!!" % len(self.dev_list))
                    now = time.time()
                    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ",time.localtime(now))
                    content = "流量审计设备数已达上限%s台" % str(self.dev_num_limit)
                    level = LOG_ALERT
                    sql_str = "INSERT INTO events (type,timestamp,content,level,status)VALUES (%d,'%s','%s',%d,0)"%(SYSTEM_TYPE,timestamp, content, level)
                    db_proxy.write_db(sql_str)
                    try:
                        logger.info('enter send_center_msg of SYSTEM_TYPE...')
                        args = (SYSTEM_TYPE, content)
                        send_center_msg(logger, *args)
                    except:
                        logger.error(traceback.format_exc())
                        logger.error("send_log_center error...")
                    self.dev_exceed_limit = True
                    webDpi_obj = get_webdpi_obj()
                    # dpiip, pro_info, ver_info, sn_info, mw_ip = webDpi_obj.getdpiinfo()
                    # log_msg = "%s%s%d|%s" % (sn_info, "|TDHX IMAP_2|", SYSTEM_TYPE, content)
                    # syslog.syslog(syslog.LOG_NOTICE, log_msg)
            else:
                flag = True
                self.dev_list.append(devid)
        return flag

    def runTrafficDataSummary(self):
        traCount = 0
        db_proxy = DbProxy()
        while 1:
            try:
                #table: icdevicetraffics
                self.realTrafficDataDelete(db_proxy)
                #table: icdevicetrafficstats
                traCount += 1
                if traCount == 12:  # 60s
                    traCount = 0
                    self.hisPointDelete(db_proxy)
                    self.get_sorted_dev_traffic(db_proxy)
                    self.trafficDataSummary(db_proxy)
                    #self.hisTrafficDataDelete()
            except:
                logger.error(traceback.format_exc())

            time.sleep(5)

    def trafficDataSummary(self, db_proxy):
        '''summary traffic data per hour'''
        timestamp = datetime.datetime.now()
        timestamp = timestamp.replace(minute=0, second=0, microsecond=0)
        timestampNyr = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        delCmd = "delete from icdevicetrafficstats where timestamp='%s'"%(timestampNyr)
        result = db_proxy.write_db(delCmd)
        delCmd = "delete from dev_his_traffic where timestamp='%s'"%(timestampNyr)
        result = db_proxy.write_db(delCmd)
        # self.dev_list = []
        self.temp_dev_list=[]

        # 防止同IP，不同MAC产生
        device_dict = {}
        devCmd = "select distinct iCDeviceIp, iCDeviceMac, iCDeviceId from icdevicetraffics"
        result, all_device = db_proxy.read_db(devCmd)
        if result != 0:
            logger.error("read mysql error")
            return
        for row in all_device:
            device_dict[row[2]] = (row[0], row[1])

        selCmd = "select iCDeviceIp, iCDeviceMac, iCDeviceId, trafficType, cast(sum(sendSpeed) as UNSIGNED)," \
                 "cast(sum(recvSpeed) as UNSIGNED) from icdevicetraffics group by iCDeviceId, trafficType"
        result, rows = db_proxy.read_db(selCmd)
        if result != 0:
            logger.error("read mysql error")
            return
        eqp_data_list = []
        pro_data_list = []
        for row in rows:
            totalBytes = row[4] + row[5]
            if row[3] == 0:
                # equipment
                row_tmp = str((row[0], row[1], row[2], int(row[4]), int(row[5]), int(totalBytes), timestampNyr))
                eqp_data_list.append(row_tmp)
                if row[2] not in self.temp_dev_list:
                    self.temp_dev_list.append(row[2])
            elif row[3] == -1:
                pass
            else:
                # protocol
                row_tmp = str((row[0], row[1], row[2], int(row[3]), self.getProtoNameByID(int(row[3])), int(totalBytes), timestampNyr))
                pro_data_list.append(row_tmp)
        if len(eqp_data_list) > 0:
            #logger.info(str(eqp_data_list))
            sql_str = "insert into dev_his_traffic (ip,mac,devid,sendBytes,recvBytes,totalBytes,timeStamp)" \
                      " values %s" % ', '.join(eqp_data_list)
            # logger.info(sql_str)
            result = db_proxy.write_db(sql_str)
            # self.dev_list.append(row[2])
        self.dev_list=self.temp_dev_list[:1000]

        if len(pro_data_list) > 0:
            #logger.info(str(pro_data_list))
            sql_str = "insert into icdevicetrafficstats (iCDeviceIp,iCDeviceMac,iCDeviceId, trafficType,trafficName," \
                      "totalBytes,timeStamp) values %s" % ', '.join(pro_data_list)
            # logger.info(len(sql_str))
            result = db_proxy.write_db(sql_str)

    def get_sorted_dev_traffic(self, db_proxy):
        selCmd = "select devid, devip, devmac, sum(send), sum(recv), sum(band), max(timestamp) from dev_band_20s group by devid"
        result, rows = db_proxy.read_db(selCmd)
        sort_rows = sorted(rows,key=lambda x:x[5], reverse=True)
        values = []
        for row in sort_rows:
            send_avg = round(float(row[3])/180, 1)
            recv_avg = round(float(row[4])/180, 1)
            # 小流量，不显示
            if send_avg < 0.1 and recv_avg < 0.1:
                continue
            total_bytes_1h = round(float(row[5]) * 20, 1)
            row_tmp = str((row[0], row[1], row[2], send_avg, recv_avg, total_bytes_1h, row[6]))
            values.append(row_tmp)
        result = db_proxy.write_db("delete from sorted_dev_traffic_1h")
        if len(values) > 0:
            sql_str = "insert into sorted_dev_traffic_1h (devid,ip,mac,sendSpeed,recvSpeed," \
                      "totalBytes,timestamp) values %s" % ', '.join(values)
            # logger.info(sql_str)
            result = db_proxy.write_db(sql_str)

    def realTrafficDataDelete(self, db_proxy):
        curTime = datetime.datetime.now()
        desTime = curTime + datetime.timedelta(hours=-1)
        desTimeNyr = desTime.strftime("%Y-%m-%d %H:%M:%S")
        delCmd = "delete from icdevicetraffics where timestamp<'%s'"%(desTimeNyr)
        #audit_send_write_cmd(TYPE_TARFFICSUM_SOCKET,delCmd)
        result = db_proxy.write_db(delCmd)

    def hisTrafficDataDelete(self, db_proxy):
        #delete history(one week ago ) data from db
        curTime = datetime.datetime.now()
        oneWeekAgo = curTime + datetime.timedelta(weeks=-1)
        oneWeekAgoNyr = oneWeekAgo.strftime("%Y-%m-%d %H:%M:%S")
        delCmd = "delete from icdevicetrafficstats where timestamp<'%s'"%(oneWeekAgoNyr)
        #audit_send_write_cmd(TYPE_TARFFICSUM_SOCKET,delCmd)
        result = db_proxy.write_db(delCmd)

    def hisPointDelete(self, db_proxy):
        curTime = datetime.datetime.now()
        desTime = curTime + datetime.timedelta(hours=-1, minutes=-2)
        desTimeNyr = desTime.strftime("%Y-%m-%d %H:%M:%S")
        # safe device 20s points
        delCmd = "delete from safedevpoint where timestamp<'%s'"%(desTimeNyr)
        result = db_proxy.write_db(delCmd)
        # industry device 20s points
        delCmd = "delete from dev_band_20s where timestamp<'%s'"%(desTimeNyr)
        result = db_proxy.write_db(delCmd)

    def init_safedevpoint(self, db_proxy):
        result1, rows = db_proxy.read_db("select max(timestamp) from safedevpoint")
        result2, rows_min = db_proxy.read_db("select min(timestamp) from safedevpoint")
        if result1 | result2 != 0:
            logger.error("read mysql error")
            return
        all_points = []
        logger.info(rows)
        logger.info(rows_min)
        cur_time = datetime.datetime.now()
        one_hour_ago = cur_time + datetime.timedelta(hours=-1)
        nowtimeNyr = one_hour_ago.strftime("%Y-%m-%d %H:%M:%S")

        if len(rows) == 0 or rows[0][0] is None:
            for i in range(180):
                laterTime = one_hour_ago + datetime.timedelta(seconds=20 * i)
                all_points.append("('%s',0)" % laterTime.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            if nowtimeNyr > rows[0][0]:
                for i in range(180):
                    laterTime = one_hour_ago + datetime.timedelta(seconds=20 * i)
                    all_points.append("('%s',0)" % laterTime.strftime("%Y-%m-%d %H:%M:%S"))
            elif nowtimeNyr > rows_min[0][0]:
                all_points = self.generate_zero_point(cur_time, rows[0][0])
            else:
                all_points = self.generate_zero_point(cur_time, rows[0][0])
                min_point_time = datetime.datetime.strptime(rows_min[0][0], "%Y-%m-%d %H:%M:%S")
                for i in range(180):
                    delta = 20 * (i+1)
                    preTime = min_point_time + datetime.timedelta(seconds=-delta)
                    if preTime < one_hour_ago:
                        break
                    preTimeNyr = preTime.strftime("%Y-%m-%d %H:%M:%S")
                    all_points.append("('%s',0)" % preTimeNyr)
        if len(all_points) > 0:
            sql_str = "insert into safedevpoint (timestamp, sendSpeed) values %s" % ','.join(all_points)
            #logger.info(sql_str)
            db_proxy.write_db(sql_str)


    def generate_zero_point(self, cur_time, max_time):
        all_points = []
        max_point_time = datetime.datetime.strptime(max_time, "%Y-%m-%d %H:%M:%S")
        for i in range(180):
            delta = 20 * (i+1)
            laterTime = max_point_time + datetime.timedelta(seconds=delta)
            if laterTime > cur_time:
                break
            laterTimeNyr = laterTime.strftime("%Y-%m-%d %H:%M:%S")
            all_points.append("('%s',0)" % laterTimeNyr)
        return all_points

    def generate_industry_device_points(self, pre_time_nyr, lastest_time_nyr, db_proxy):
        device_dict = {}
        devCmd = "select distinct iCDeviceIp, iCDeviceMac, iCDeviceId from icdevicetraffics"
        result, all_device = db_proxy.read_db(devCmd)
        if result != 0 or len(all_device) == 0:
            return
        for row in all_device:
            if len(row) < 3:
                logger.error("generate_industry_device_points error!! row=%s" % str(row))
                continue
            device_dict[row[2]] = (row[0], row[1])
        sel_cmd="select iCDeviceId,cast(sum(sendSpeed) as UNSIGNED),cast(sum(recvSpeed) as UNSIGNED) " \
                "from icdevicetraffics where timestamp > '%s' and timestamp <= '%s' and trafficName = 'equipment' " \
                "and iCDeviceId in " % (pre_time_nyr, lastest_time_nyr)
        id_str=",".join(map(lambda x: "'%s'" % x, device_dict.keys()))
        sel_cmd+="(%s) group by iCDeviceId" % id_str
        result, rows=db_proxy.read_db(sel_cmd)
        # logger.error(sel_cmd)
        if result != 0 or len(rows) == 0:
            return
        insertCmd="insert into dev_band_20s (devid, devip, devmac, timestamp, band, send, recv) values "
        for avgBytes in rows:
            avgBytes=list(avgBytes)
            tmp_id=avgBytes[0]
            avgBytes[1]=avgBytes[1] or 0
            avgBytes[2]=avgBytes[2] or 0
            avgBytes[1]=round((avgBytes[1] / 512.0), 1)
            avgBytes[2]=round((avgBytes[2] / 512.0), 1)
            totalBytes=avgBytes[1] + avgBytes[2]  # totalBytes/4.0/1024.0*8.0
            data_cmd="('%s', '%s', '%s', '%s', %s, '%s', '%s')," % (
                tmp_id, device_dict[tmp_id][0], device_dict[tmp_id][1],
                lastest_time_nyr, totalBytes, avgBytes[1], avgBytes[2])
            insertCmd+=data_cmd
        insertCmd=insertCmd[:-1]
        db_proxy.write_db(insertCmd)
        # logger.error(insertCmd)

    def generate_industry_device_data(self):
        db_proxy = DbProxy()
        while True:
            try:
                lastest_time_nyr = self.time_queue.get()
                lastest_time = datetime.datetime.strptime(lastest_time_nyr, "%Y-%m-%d %H:%M:%S")
                lastest_time = lastest_time + datetime.timedelta(seconds=-20)
                lastest_time_nyr = lastest_time.strftime("%Y-%m-%d %H:%M:%S")

                pre_time = lastest_time + datetime.timedelta(seconds=-20)
                pre_time_nyr = pre_time.strftime("%Y-%m-%d %H:%M:%S")

                self.generate_industry_device_points(pre_time_nyr, lastest_time_nyr, db_proxy)
            except:
                logger.error(traceback.format_exc())
            time.sleep(10)
