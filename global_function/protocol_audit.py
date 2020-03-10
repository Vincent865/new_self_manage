#! /usr/bin/env python
# coding=utf-8
import chardet
import threading
# from log_config import LogConfig
from global_function.dev_auto_identify import devAutoIdentify
from global_function.global_var import *
import logging

# LogConfig('flask_mw.log')
logger = logging.getLogger('flask_db_socket_log')


class protAudit(threading.Thread):
    '''protAudit thread,link to machinestate process'''

    def __init__(self):
        '''init protAudit object'''
        threading.Thread.__init__(self)

        self.myQueue = Queue.Queue(maxsize=queue_limit["protAudit"])
        self.flowHeadsList = []
        self.flowHeadsNumLimit = 50
        self.flowdataHeadId = 0
        logger.info("Init protAuditProcess ok!")

    def run(self):
        '''run protAudit obj'''
        t1 = threading.Thread(target=self.runDeleteHisData)
        t1.setDaemon(True)
        t1.start()

        t2 = threading.Thread(target=self.runReceiveData)
        t2.setDaemon(True)
        t2.start()

        t3 = threading.Thread(target=self.runWriteIntoQueue)
        t3.setDaemon(True)
        t3.start()
        
        t3.join()
        
    def runReceiveData(self):
        traffic_addr = '/data/sock/protAudit_sock'
        try:
            if os.path.exists(traffic_addr):
                os.remove(traffic_addr)
        except:
            logger.error(traceback.format_exc())

        db_write_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        db_write_sock.bind(traffic_addr)
        num = 0
        while True:
            if num % 500 == 0:
                num = 0
                time.sleep(0.001)
            try:
                data = db_write_sock.recvfrom(5120)
                if len(data) != 0:
                    logger.info(data)
                if self.myQueue.full():
                    time.sleep(0.001)
                    continue
                self.myQueue.put(data[0])
            except:
                data = None
                logger.error(traceback.format_exc())
            num += 1

    def runWriteIntoQueue(self):
        global protocol_columns
        time.sleep(5)
        db_proxy = DbProxy()
        try:
            selCmd = "select max(flowdataHeadId) from flowdataheads"
            # maxFlowHeadId = audit_send_read_cmd(TYPE_PROTREC_SOCKET,selCmd)
            result, maxFlowHeadId = db_proxy.read_db(selCmd)
            if maxFlowHeadId[0][0] != None:
                self.flowdataHeadId = maxFlowHeadId[0][0]
        except:
            logger.error("select max flowdataHeadId error")
        num = 0
        while True:
            if num % 100 == 0:
                num = 0
                # time.sleep(0.001)
            try:
                data = self.myQueue.get()
                flowHead, protVal, others = data.split('----')
                others = None
                flowHead = flowHead.split(',')
            except:
                logger.error(traceback.format_exc())
                continue

            try:
                protID = flowHead[12][1:-1]
                if int(protID) > 500:
                    protSeg = 'proto_id, protocolDetail'
                else:
                    protSeg = protocol_columns[int(protID)]
                    if int(protID) == 5:
                        protSeg += ',allData'
                # logger.info("protID=%d, protVal=%s",int(protID), protVal)
                # logger.info("flowHead=%s",flowHead)
                # logger.info("protSeg=%s",protSeg)
                self.writeDataInDB(flowHead, protSeg, protVal)
            except:
                logger.error(traceback.format_exc())
            num += 1

    def parse(self, pro_val, db, pid):
        result = str(pid) + ",'"
        item_list = pro_val.split(",")
        for item in item_list:
            value = item.split(":")
            value_id = int(value[0].lstrip("'"))
            seg = value[1]
            desc = value[2].rstrip("'")
            cmd_str = "select value_desc from value_map_model where value_map_id={} and audit_value='{}'".format(
                value_id, desc)
            logger.info(cmd_str)
            res, rows = db.read_db(cmd_str)
            if res == 0 and len(rows) > 0:
                result = result + str(seg) + ":" + str(rows[0][0]) + ","
            else:
                result = result + str(seg) + ":" + str(desc) + ","
        result = result.rstrip(",")
        result += "'"
        return result

    def writeDataInDB(self, flowHead, protSeg, protVal):
        db_proxy = DbProxy()
        db_proxy_config = DbProxy(CONFIG_DB_NAME)
        flag = False
        if protVal.find(','):
            protVal_split = protVal.split(',')
            for protVal_c in protVal_split:
                if protVal_c != "''":
                    flag = True
        else:
            if protVal != "''":
                flag = True

        '''write data in db,flowdatahead table & protoco table'''
        global protocol_names
        protID = flowHead[12][1:-1]
        if int(protID) > 500:
            cmd_str = "select proto_name from self_define_proto_config where proto_id = %d" % int(protID)
            # rows=new_send_cmd(TYPE_APP_SOCKET, cmd_str, 1)
            res, rows = db_proxy_config.read_db(cmd_str)
            if len(rows) > 0:
                protName = "cusproto"
                protName_sql_val = "'" + str(protID) + "," + rows[0][0] + "'"
            else:
                protName = "NA"
                protName_sql_val = "'" + protName + "'"
            # protVal = protVal.encode('raw_unicode_escape').decode()
            # encod = chardet.detect(protVal)
            # logger.info("before: =================== " + protVal + "++++" + str(encod))
            if protVal != "''":
                protVal = self.parse(protVal, db_proxy_config, protID)
            logger.info("self_define_proto: =================== " + protVal)
        else:
            protName = protocol_names[int(protID)]
            protName_sql_val = "'" + protName + "'"

        receiveHead = (flowHead[2], flowHead[3], flowHead[5], flowHead[6], flowHead[7], flowHead[8])
        reverseReceiveHead = (flowHead[3], flowHead[2], flowHead[7], flowHead[8], flowHead[5], flowHead[6])
        recordFlag = False
        flowdataHeadId = 0
        date_change = 0
        list_index = 0
        packet_date = flowHead[0].split(" ")[0].replace("'", "")
        '''
        #http contains ','
        if protName == 'http' and protVal[0] == '#':
            protValFormat = "'%s'"%protVal[1:]
        else:
            protVal = protVal.split(',')
            protValFormat = ""
            for i,val in enumerate(protVal):
                protValFormat += "'%s',"%val
            protValFormat = protValFormat[:-1]
        '''
        # ================= check if the cur flowHeads in list =================
        # =====> direction

        for k, val in enumerate(self.flowHeadsList):
            if val[0] == receiveHead:
                flowdataHeadId = val[1]
                recordFlag = True
                if val[2] < packet_date:
                    date_change = 1
                    list_index = k
                break

        # <===== reverse direction
        if recordFlag == False:
            for k, val in enumerate(self.flowHeadsList):
                if val[0] == reverseReceiveHead:
                    flowdataHeadId = val[1]
                    recordFlag = True
                    if val[2] < packet_date:
                        date_change = 1
                        list_index = k
                    break

        flowtime = flowHead[-1]
        flowtime = str(flowtime)
        # logger.info(flowtime)
        # have found in flowHeadsList
        if recordFlag == True:
            if protName_sql_val != "'NA'":
                update_str = "update flowdataheads set flowTimestamp = %s,protocolSourceName = %s where flowdataHeadId = %d" \
                             % (flowHead[0], protName_sql_val, flowdataHeadId)
                db_proxy.write_db(update_str)

            if date_change == 1:
                update_str = "update flowdataheads set flowTimestamp = %s where flowdataHeadId = %d" \
                             % (flowHead[0], flowdataHeadId)
                db_proxy.write_db(update_str)
                self.flowHeadsList[list_index][2] = packet_date

            # update protocol_audit time
            update_str = "update flowdataheads set packetTimestampint = %s where flowdataHeadId = %d" % (
            flowtime, flowdataHeadId)
            db_proxy.write_db(update_str)

            if flag:
                protSqlStr = "insert into %sflowdatas (flowdataHeadId,%s,packetLenth,packetTimestamp,packetTimestampint)\
                values(%s,%s,%s,%s,%s)" % (
                protName, protSeg, flowdataHeadId, protVal, flowHead[11], flowHead[1], flowHead[13])
                # logger.info(protSqlStr)
                # send_write_cmd(TYPE_PROTREC_SOCKET,protSqlStr)
                SqlQueueIn("%sflowdatas" % protName, protSqlStr)
            return
        # =================================== end===============================

        # ================= check if the cur flowHeads in DB ===================
        # =====> direction
        checkCmd = "select flowdataHeadId, flowTimestamp from flowdataheads where sourceMac=%s and destinationMac=%s \
        and sourceIp=%s and sourcePort=%s and destinationIp=%s and destinationPort=%s" % (
        receiveHead[0], receiveHead[1], receiveHead[2], receiveHead[3], receiveHead[4], receiveHead[5])
        # headId = audit_send_read_cmd(TYPE_PROTREC_SOCKET,checkCmd)
        result, headId = db_proxy.read_db(checkCmd)
        if len(headId) == 0:
            # <===== reverse direction
            checkReverseCmd = "select flowdataHeadId, flowTimestamp from flowdataheads where sourceMac=%s and destinationMac=%s \
            and sourceIp=%s and sourcePort=%s and destinationIp=%s and destinationPort=%s" % (
            reverseReceiveHead[0], reverseReceiveHead[1], reverseReceiveHead[2], reverseReceiveHead[3],
            reverseReceiveHead[4], reverseReceiveHead[5])
            # headIdReverse = audit_send_read_cmd(TYPE_PROTREC_SOCKET,checkReverseCmd)
            result, headIdReverse = db_proxy.read_db(checkReverseCmd)
            if len(headIdReverse) == 0:
                recordFlag = False
            else:
                recordFlag = True
                flowdataHeadId = headIdReverse[0][0]
                flowTimestamp = headIdReverse[0][1]
        else:
            recordFlag = True
            flowdataHeadId = headId[0][0]
            flowTimestamp = headId[0][1]

        if recordFlag == True:
            if flowTimestamp.split(" ")[0] < packet_date:
                date_change = 1

            # update protocol_audit time
            update_str = "update flowdataheads set packetTimestampint = %s where flowdataHeadId = %d" % (
            flowtime, flowdataHeadId)
            db_proxy.write_db(update_str)

            if date_change == 1:
                update_str = "update flowdataheads set flowTimestamp = %s where flowdataHeadId = %d" \
                             % (flowHead[0], flowdataHeadId)
                db_proxy.write_db(update_str)

            update_str = "update flowdataheads set flowTimestamp = %s,protocolSourceName = %s  where flowdataHeadId = %d" \
                         % (flowHead[0], protName_sql_val, flowdataHeadId)
            db_proxy.write_db(update_str)
            if flag:
                protSqlStr = "insert into %sflowdatas (flowdataHeadId,%s,packetLenth,packetTimestamp,packetTimestampint)\
                 values(%s,%s,%s,%s,%s)" % (
                protName, protSeg, flowdataHeadId, protVal, flowHead[11], flowHead[1], flowHead[13])
                # send_write_cmd(TYPE_PROTREC_SOCKET,protSqlStr)
                SqlQueueIn("%sflowdatas" % protName, protSqlStr)

            self.flowHeadsList.insert(0, [receiveHead, flowdataHeadId, packet_date])
            # self.flowdataHeadId = flowdataHeadId
            if len(self.flowHeadsList) > self.flowHeadsNumLimit:
                self.flowHeadsList.pop()

            return

        # =================insert new flowdatahead in db========================
        self.flowdataHeadId += 1
        self.flowHeadsList.insert(0, [receiveHead, self.flowdataHeadId, packet_date])
        if len(self.flowHeadsList) > self.flowHeadsNumLimit:
            self.flowHeadsList.pop()
        devAutoIdentify.runDevPutData(flowHead)

        headSqlStr = "insert into flowdataheads (flowdataHeadId,flowTimestamp,packetTimestamp,sourceMac,destinationMac,ipVersion,\
        sourceIp, sourcePort, destinationIp, destinationPort, protocolType, protocolTypeName, packetLenth,protocolSourceName,directions,packetTimestampint) \
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,2,%s)" % (
        self.flowdataHeadId, flowHead[0], flowHead[1], flowHead[2], flowHead[3], flowHead[4], flowHead[5], \
        flowHead[6], flowHead[7], flowHead[8], flowHead[9], flowHead[10], flowHead[11], protName_sql_val, flowHead[13])
        # audit_send_write_cmd(TYPE_PROTREC_SOCKET,headSqlStr)
        result = db_proxy.write_db(headSqlStr)
        if flag:
            protSqlStr = "insert into %sflowdatas (flowdataHeadId,%s,packetLenth,packetTimestamp, packetTimestampint) \
            values(%s,%s,%s,%s,%s)" % (
            protName, protSeg, self.flowdataHeadId, protVal, flowHead[11], flowHead[1], flowHead[13])
            # send_write_cmd(TYPE_PROTREC_SOCKET,protSqlStr)
            SqlQueueIn("%sflowdatas" % protName, protSqlStr)

    def runDeleteHisData(self):
        clean_flowheadid_sock_addr = '/data/sock/db_clean_flowheadid'
        try:
            if os.path.exists(clean_flowheadid_sock_addr):
                os.remove(clean_flowheadid_sock_addr)
        except:
            logger.error(traceback.format_exc())

        db_clean_flowheadid_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        db_clean_flowheadid_sock.bind(clean_flowheadid_sock_addr)

        while True:
            try:
                data = db_clean_flowheadid_sock.recvfrom(2048)
                headId = int(data[0])
                for i, val in enumerate(self.flowHeadsList):
                    if val[1] == headId:
                        del self.flowHeadsList[i]
                        break
                logger.info("delete flowdateheads,headId=%d" % (headId))
            except:
                data = None
                logger.error(traceback.format_exc())


class protoBhvAudit(threading.Thread):
    '''protAudit thread,link to machinestate process'''

    def __init__(self):
        '''init protAudit object'''
        threading.Thread.__init__(self)

        self.myQueue = Queue.Queue(maxsize=queue_limit["protAudit"])
        self.flowHeadsList = []
        self.flowHeadsNumLimit = 50
        self.flowdataHeadId = 0
        logger.info("Init protBhvAuditProcess ok!")

    def run(self):
        '''run protAudit obj'''
        t1 = threading.Thread(target=self.runDeleteHisData)
        t1.setDaemon(True)
        t1.start()

        t2 = threading.Thread(target=self.runReceiveData)
        t2.setDaemon(True)
        t2.start()

        t3 = threading.Thread(target=self.runWriteIntoQueue)
        t3.setDaemon(True)
        t3.start()

        t3.join()

    def runReceiveData(self):
        traffic_addr = '/data/sock/BehaviorAduit_sock'
        # logger.info("runReceiveData is running...")
        try:
            if os.path.exists(traffic_addr):
                os.remove(traffic_addr)
        except:
            logger.error(traceback.format_exc())

        db_write_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        db_write_sock.bind(traffic_addr)
        num = 0
        while True:
            if num % 500 == 0:
                num = 0
                time.sleep(0.001)
            try:
                data = db_write_sock.recvfrom(5120)
                # logger.info(str(data))
                if self.myQueue.full():
                    time.sleep(0.001)
                    continue
                logger.info(data[0])
                self.myQueue.put(data[0])
            except:
                data = None
                logger.error(traceback.format_exc())
            num += 1

    def runWriteIntoQueue(self):
        # logger.info("runWriteIntoQueue is running...")
        global protocol_columns
        time.sleep(5)
        db_proxy = DbProxy()
        try:
            selCmd = "select max(flowdataHeadId) from bhvflowdataheads"
            # maxFlowHeadId = audit_send_read_cmd(TYPE_PROTREC_SOCKET,selCmd)
            result, maxFlowHeadId = db_proxy.read_db(selCmd)
            if maxFlowHeadId[0][0] != None:
                self.flowdataHeadId = maxFlowHeadId[0][0]
        except:
            logger.error("select max flowdataHeadId error")
        num = 0
        while True:
            if num % 100 == 0:
                num = 0
                # time.sleep(0.001)
            try:
                data = self.myQueue.get()
                flowHead, protVal, others = data.split('----')
                others = None
                flowHead = flowHead.split(',')
            except:
                logger.error(traceback.format_exc())
                continue

            try:
                protID = flowHead[12][1:-1]
                protSeg = protocol_columns[int(protID)]
                if int(protID) == 15:
                    protSeg = 'type,content'
                else:
                    pass
                # logger.info("protID=%d, protVal=%s",int(protID), protVal)
                # logger.info("flowHead=%s",flowHead)
                # logger.info("protSeg=%s",protSeg)
                self.writeDataInDB(flowHead, protSeg, protVal)
            except:
                logger.error(traceback.format_exc())
            num += 1

    def writeDataInDB(self, flowHead, protSeg, protVal):
        '''write data in db,flowdatahead table & protoco table'''
        global protocol_names
        protID = flowHead[12][1:-1]
        protName = protocol_names[int(protID)]
        protName_sql_val = "'" + protName + "'"
        receiveHead = (flowHead[2], flowHead[3], flowHead[5], flowHead[6], flowHead[7], flowHead[8], protName_sql_val)
        reverseReceiveHead = (
            flowHead[3], flowHead[2], flowHead[7], flowHead[8], flowHead[5], flowHead[6], protName_sql_val)
        recordFlag = False
        flowdataHeadId = 0
        date_change = 0
        list_index = 0
        packet_date = flowHead[0].split(" ")[0].replace("'", "")
        db_proxy = DbProxy()
        '''
        #http contains ','
        if protName == 'http' and protVal[0] == '#':
            protValFormat = "'%s'"%protVal[1:]
        else:
            protVal = protVal.split(',')
            protValFormat = ""
            for i,val in enumerate(protVal):
                protValFormat += "'%s',"%val
            protValFormat = protValFormat[:-1]
        '''
        # ================= check if the cur flowHeads in list =================
        # =====> direction

        for k, val in enumerate(self.flowHeadsList):
            if val[0] == receiveHead:
                flowdataHeadId = val[1]
                recordFlag = True
                if val[2] < packet_date:
                    date_change = 1
                    list_index = k
                break

        # <===== reverse direction
        if recordFlag == False:
            for k, val in enumerate(self.flowHeadsList):
                if val[0] == reverseReceiveHead:
                    flowdataHeadId = val[1]
                    recordFlag = True
                    if val[2] < packet_date:
                        date_change = 1
                        list_index = k
                    break
        flowtime = flowHead[-1]
        flowtime = str(flowtime)
        logger.info(flowtime)
        # have found in flowHeadsList
        if recordFlag == True:
            # if date_change == 1:
            #     update_str="update bhvflowdataheads set flowTimestamp = %s where flowdataHeadId = %d" \
            #                % (flowHead[0], flowdataHeadId)
            #     db_proxy.write_db(update_str)
            #     self.flowHeadsList[list_index][2]=packet_date
            update_str = "update bhvflowdataheads set packetTimestampint = %s where flowdataHeadId = %d" % (
            flowtime, flowdataHeadId)
            db_proxy.write_db(update_str)
            self.flowHeadsList[list_index][2] = packet_date
            protSqlStr = "insert into %sbhvAduitdatas (flowdataHeadId,%s,packetLenth,packetTimestamp,packetTimestampint)\
            values(%s,%s,%s,%s,%s)" % (
            protName, protSeg, flowdataHeadId, protVal, flowHead[11], flowHead[1], flowHead[13])
            # send_write_cmd(TYPE_PROTREC_SOCKET,protSqlStr)
            logger.info(protSqlStr)
            SqlQueueIn("%sbhvAduitdatas" % protName, protSqlStr)
            return
        # =================================== end===============================

        # ================= check if the cur flowHeads in DB ===================
        # =====> direction
        checkCmd = "select flowdataHeadId, flowTimestamp from bhvflowdataheads where sourceMac=%s and destinationMac=%s \
        and sourceIp=%s and sourcePort=%s and destinationIp=%s and destinationPort=%s and \
        protocolSourceName=%s" % (
            receiveHead[0], receiveHead[1], receiveHead[2], receiveHead[3], receiveHead[4], receiveHead[5],
            receiveHead[6])
        # headId = audit_send_read_cmd(TYPE_PROTREC_SOCKET,checkCmd)
        result, headId = db_proxy.read_db(checkCmd)
        if len(headId) == 0:
            # <===== reverse direction
            checkReverseCmd = "select flowdataHeadId, flowTimestamp from bhvflowdataheads where sourceMac=%s and destinationMac=%s \
            and sourceIp=%s and sourcePort=%s and destinationIp=%s and destinationPort=%s and \
            protocolSourceName=%s" % (
                reverseReceiveHead[0], reverseReceiveHead[1], reverseReceiveHead[2], reverseReceiveHead[3],
                reverseReceiveHead[4], reverseReceiveHead[5], reverseReceiveHead[6])
            # headIdReverse = audit_send_read_cmd(TYPE_PROTREC_SOCKET,checkReverseCmd)
            result, headIdReverse = db_proxy.read_db(checkReverseCmd)
            if len(headIdReverse) == 0:
                recordFlag = False
            else:
                recordFlag = True
                flowdataHeadId = headIdReverse[0][0]
                flowTimestamp = headIdReverse[0][1]
        else:
            recordFlag = True
            flowdataHeadId = headId[0][0]
            flowTimestamp = headId[0][1]

        if recordFlag == True:
            if flowTimestamp.split(" ")[0] < packet_date:
                date_change = 1
            # if date_change == 1:
            #     update_str="update bhvflowdataheads set flowTimestamp = %s where flowdataHeadId = %d" \
            #                % (flowHead[0], flowdataHeadId)
            #     db_proxy.write_db(update_str)
            update_str = "update bhvflowdataheads set packetTimestampint = %s where flowdataHeadId = %d" % (
            flowtime, flowdataHeadId)
            db_proxy.write_db(update_str)
            protSqlStr = "insert into %sbhvAduitdatas (flowdataHeadId,%s,packetLenth,packetTimestamp,packetTimestampint)\
             values(%s,%s,%s,%s,%s)" % (
                protName, protSeg, flowdataHeadId, protVal, flowHead[11], flowHead[1], flowHead[13])
            # send_write_cmd(TYPE_PROTREC_SOCKET,protSqlStr)
            SqlQueueIn("%sbhvAduitdatas" % protName, protSqlStr)

            self.flowHeadsList.insert(0, [receiveHead, flowdataHeadId, packet_date])
            # self.flowdataHeadId = flowdataHeadId
            if len(self.flowHeadsList) > self.flowHeadsNumLimit:
                self.flowHeadsList.pop()

            return

        # =================insert new flowdatahead in db========================
        self.flowdataHeadId += 1
        self.flowHeadsList.insert(0, [receiveHead, self.flowdataHeadId, packet_date])
        if len(self.flowHeadsList) > self.flowHeadsNumLimit:
            self.flowHeadsList.pop()

        headSqlStr = "insert into bhvflowdataheads (flowdataHeadId,flowTimestamp,packetTimestamp,sourceMac,destinationMac,ipVersion,\
        sourceIp, sourcePort, destinationIp, destinationPort, protocolType, protocolTypeName, packetLenth,protocolSourceName,directions,packetTimestampint) \
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,2,%s)" % (
            self.flowdataHeadId, flowHead[0], flowHead[1], flowHead[2], flowHead[3], flowHead[4], flowHead[5], \
            flowHead[6], flowHead[7], flowHead[8], flowHead[9], flowHead[10], flowHead[11], protName_sql_val,
            flowHead[13])
        # audit_send_write_cmd(TYPE_PROTREC_SOCKET,headSqlStr)
        result = db_proxy.write_db(headSqlStr)

        protSqlStr = "insert into %sbhvAduitdatas (flowdataHeadId,%s,packetLenth,packetTimestamp, packetTimestampint) \
        values(%s,%s,%s,%s,%s)" % (
            protName, protSeg, self.flowdataHeadId, protVal, flowHead[11], flowHead[1], flowHead[13])
        # send_write_cmd(TYPE_PROTREC_SOCKET,protSqlStr)
        SqlQueueIn("%sbhvAduitdatas" % protName, protSqlStr)
        logger.info(protSqlStr)

    def runDeleteHisData(self):
        clean_flowheadid_sock_addr = '/data/sock/db_clean_flowheadid'
        try:
            if os.path.exists(clean_flowheadid_sock_addr):
                os.remove(clean_flowheadid_sock_addr)
        except:
            logger.error(traceback.format_exc())

        db_clean_flowheadid_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        db_clean_flowheadid_sock.bind(clean_flowheadid_sock_addr)

        while True:
            try:
                data = db_clean_flowheadid_sock.recvfrom(2048)
                headId = int(data[0])
                for i, val in enumerate(self.flowHeadsList):
                    if val[1] == headId:
                        del self.flowHeadsList[i]
                        break
                logger.info("delete flowdateheads,headId=%d" % (headId))
            except:
                data = None
                logger.error(traceback.format_exc())