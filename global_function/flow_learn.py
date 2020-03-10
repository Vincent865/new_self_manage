# -*- coding:UTF-8 -*-
'''
flow audit handle msg from dpi
author: HanFei
'''
import math
import threading
import global_var as GlobalVar
import syslog
from log_oper import *
import logging

FLOW_AUFIT_SAVE_DAYS = 90
FLOW_AUDIT_SAVE_DIR = "/data/streambuild"
FLOW_AUDIT_SIZE_RANGE = 18 * 1024 * 1024 * 1024

logger = logging.getLogger('flask_mw_log')

class flow_band_learn_ctl(threading.Thread):
    '''flow band learn ctl thread,link to machinestate process'''
    def __init__(self):
        '''init flow band learn object'''
        threading.Thread.__init__(self)
        self.flow_band_threshold_init()
        logger.info("flow_band_learn_ctl init ok!")

    def run(self):
        '''run flow band learn obj'''
        try:
            if os.path.exists(GlobalVar.dst_machine_learn_ctl_addr):
                os.remove(GlobalVar.dst_machine_learn_ctl_addr)
        except:
            logging.error("g_dst_ml_ctl_sock file not exist")
        ml_ctl_sock = socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
        ml_ctl_sock.bind(GlobalVar.dst_machine_learn_ctl_addr)
        db_proxy = DbProxy(CONFIG_DB_NAME)
        while True:
            try:
                data, addr = ml_ctl_sock.recvfrom(4096)
            except:
                data = None
                logging.error("recive data error from flow audit socket")
                logger.exception("Exception Logged")
            logger.info("flow_band_learn_ctl rcv msg %s" % data)
            if data != None:
                try:
                    str_list = data.split(",",1)
                    #开始学习，设置开始流量采样标记
                    if str_list[0] == "1":
                        logger.info("start learnning")
                        GlobalVar.FLOW_LEARN_FLAG = 0
                        time.sleep(3)
                        if str_list[1] == "1":
                            logger.info("clear flag learnning")
                            #删除之前的阈值记录，包括mysql表项和内存
                            sql_str = "delete from dev_band_threshold"
                            db_proxy.write_db(sql_str)
                            GlobalVar.dev_band_threshold_info = {}
                            GlobalVar.flow_band_sample = band_sample_info()
                        GlobalVar.FLOW_LEARN_FLAG = 1

                    #停止学习
                    elif str_list[0] == "2":
                        GlobalVar.FLOW_LEARN_FLAG = 0
                        time.sleep(3)
                        self.flow_band_range_gen(db_proxy)
                        logger.info("flow_band_range_gen finish")

                        GlobalVar.flow_band_sample = band_sample_info()
                        GlobalVar.FLOW_LEARN_FLAG = 2
                    elif str_list[0] == "3":
                        logger.info("before mod, dev_threshold = %s" % str(GlobalVar.dev_band_threshold_info))
                        GlobalVar.FLOW_LEARN_FLAG = 0
                        time.sleep(3)
                        new_range = eval(str_list[1])
                        GlobalVar.dev_band_threshold_info[new_range[0]][2] = new_range[1]
                        GlobalVar.dev_band_threshold_info[new_range[0]][3] = new_range[2]
                        GlobalVar.dev_band_threshold_info[new_range[0]][4] = 0
                        GlobalVar.dev_band_threshold_info[new_range[0]][5] = 0
                        GlobalVar.dev_band_threshold_info[new_range[0]][6] = 0
                        GlobalVar.FLOW_LEARN_FLAG = 2
                        logger.info("after mod, dev_threshold = %s" % str(GlobalVar.dev_band_threshold_info))
                    elif str_list[0] == "4":
                        logger.info("before add, dev_threshold = %s" % str(GlobalVar.dev_band_threshold_info))
                        GlobalVar.FLOW_LEARN_FLAG = 0
                        time.sleep(3)
                        new_range = eval(str_list[1])
                        GlobalVar.dev_band_threshold_info[new_range[0]] = [new_range[1], new_range[2], new_range[3], new_range[4], 0, 0, 0]
                        GlobalVar.FLOW_LEARN_FLAG = 2
                        logger.info("after add, dev_threshold = %s" % str(GlobalVar.dev_band_threshold_info))
                    elif str_list[0] == "5":
                        logger.info("before del, dev_threshold = %s" % str(GlobalVar.dev_band_threshold_info))
                        GlobalVar.FLOW_LEARN_FLAG = 0
                        time.sleep(3)
                        dev_id = str_list[1]
                        del GlobalVar.dev_band_threshold_info[dev_id]
                        GlobalVar.FLOW_LEARN_FLAG = 2
                        logger.info("after del, dev_threshold = %s" % str(GlobalVar.dev_band_threshold_info))
                    # elif str_list[0] == "6":
                    #     SYSLOG_UPLOAD["status"] = False
                    # elif str_list[0] == "7":
                    #     SYSLOG_UPLOAD["status"] = True
                    else:
                        pass
                except:
                    logger.exception("Exception Logged")

    def flow_band_range_gen(self, db_proxy):
        M_ARG = 8
        dev_list = GlobalVar.flow_band_sample.sample_info.keys()
        for idx in dev_list:
            sample_elem = GlobalVar.flow_band_sample.sample_info[idx]
            devid = idx
            devip = sample_elem[0]
            devmac = sample_elem[1]
            min_band = sample_elem[2]
            max_band = sample_elem[3]
            ave_band = sample_elem[4]
            if max_band == 0:
                continue
            range_val = float(ave_band) / M_ARG
            if min_band <= range_val:
                low_line = 0
            else:
                # low_line = round(min_band - range_val, 1)
                low_line = math.floor(min_band - range_val)

            # high_line = round(max_band + range_val, 1)
            high_line = math.ceil(max_band + range_val)

            #dev_band_threshold_list, elem is [设备ID, IP, MAC, 低阈值，高阈值，上次告警类型， 当前告警的类型， 当前告警命中数]
            if devid not in GlobalVar.dev_band_threshold_info:
                GlobalVar.dev_band_threshold_info[devid] = [devip, devmac, low_line, high_line, 0, 0, 0]
                #插入dev_band_threshold表
                sql_str = "insert into dev_band_threshold (dev_id, dev_ip, dev_mac, low_line, high_line) \
                        values('%s','%s','%s', %d, %d)" % (devid, devip, devmac, low_line, high_line)
                db_proxy.write_db(sql_str)
            else:
                GlobalVar.dev_band_threshold_info[devid] = [devip, devmac, low_line, high_line, 0, 0, 0]
                #更新dev_band_threshold表
                sql_str = "update dev_band_threshold set low_line = %d, high_line = %d where dev_id = '%s'" % (low_line, high_line, devid)
                db_proxy.write_db(sql_str)
        logger.info("flow band range: %s" % str(GlobalVar.dev_band_threshold_info))

    def flow_band_threshold_init(self):
        sql_str = "select count(*) from dev_band_threshold"
        db_proxy = DbProxy(CONFIG_DB_NAME)
        res, sql_res = db_proxy.read_db(sql_str)
        total_num = 0
        if res == 0:
            total_num = sql_res[0][0]
        else:
            return
        logger.info("dev_band_threshold total num = %d" % total_num)

        left_cnt = total_num
        index = 0
        while left_cnt > 0:
            if left_cnt >= 1000:
                get_cnt = 1000
            else:
                get_cnt = left_cnt
            sql_str = '''select dev_id, dev_ip, dev_mac, low_line, high_line from dev_band_threshold \
                      limit %d offset %d''' % (get_cnt, index*1000)
            res, sql_res = db_proxy.read_db(sql_str)
            if res != 0:
                left_cnt -= get_cnt
                index += 1
                logger.info("flow_band_threshold_init read dev_band_threshold failed")
                continue
            for i in range(0, len(sql_res)):
                GlobalVar.dev_band_threshold_info[sql_res[i][0]] = [sql_res[i][1], sql_res[i][2], sql_res[i][3], sql_res[i][4], 0, 0, 0]
            left_cnt -= get_cnt
            index += 1
        logger.info("init dev_band_threshold_info = %s" % str(GlobalVar.dev_band_threshold_info))
        if total_num > 0:
            GlobalVar.FLOW_LEARN_FLAG = 2
        return

def get_dev_points(id):
    db_proxy = DbProxy()
    sel_cmd = "select timestamp, band from dev_band_20s where devid = '%s' order by timestamp desc limit 180" % id
    result, rows = db_proxy.read_db(sel_cmd)
    if result != 0:
        return [], []
    rows = list(rows)
    rows.reverse()
    point_num = len(rows)
    if point_num == 0:
        # 系统重新启动，会清空dev_band_20s，导致rows[0][0]不可用，无法补点，更新事件snapshot的线程报错;产生事件的线程不会进入此分支(产生告警，至少得有一个点)
        return [], []
    elif point_num < 180:
        zero_rows = []
        start_time = datetime.datetime.strptime(rows[0][0], "%Y-%m-%d %H:%M:%S")

        for i in range(180-point_num, 0, -1):
            pre_time = start_time + datetime.timedelta(seconds=-i*20)
            pre_time_nyr = pre_time.strftime("%Y-%m-%d %H:%M:%S")
            zero_rows.append((pre_time_nyr, 0))
        zero_rows.extend(rows)
        rows = zero_rows
    else:
        pass
    timePoints = [row[0] for row in rows]
    bytes = [row[1] for row in rows]
    return timePoints, bytes

class flow_band_proc(threading.Thread):
    '''flow band learn ctl thread,link to machinestate process'''
    def __init__(self):
        '''init flow audit object'''
        threading.Thread.__init__(self)
        self.db_proxy = DbProxy()
        self.table_num = 0
        logger.info("flow_band_proc init ok")

    def run(self):
        try:
            '''run flow audit obj'''
            logger.info("flow_band_proc init start")
            read_index = 0
            now_read_time = "2000-01-01 00:00:00"
            #读取dev_band_20s表中最新的时间戳
            sql_str = '''select timestamp from dev_band_20s order by timestamp desc limit 1'''
            res, sql_res = self.db_proxy.read_db(sql_str)
            if res == 0 and len(sql_res) > 0:
                now_read_time = sql_res[0][0]

            while True:
                sql_str = '''select max(id) from dev_band_20s'''
                res, sql_res = self.db_proxy.read_db(sql_str)
                if res == 0 and len(sql_res) > 0 and sql_res[0][0] != None:
                    read_index = sql_res[0][0]
                    read_index += 1
                    break
                else:
                    time.sleep(5)
                    continue

            logger.info("now_read_time = %s, read_index = %d" % (now_read_time, read_index))
        except:
            logger.exception("Exception Logged")

        while True:
            try:
                #读取dev_band_20s
                sql_str = '''select devid, devip, devmac, timestamp, band from dev_band_20s where id = %d''' % read_index
                #logger.info("need to read band info index: %d" % read_index)
                res, sql_res = self.db_proxy.read_db(sql_str)
                if res == 0 and len(sql_res) > 0:
                    #学习状态，需要采样流量点，形成flow_band_sample
                    if GlobalVar.FLOW_LEARN_FLAG == 1:
                        if sql_res[0][3] > now_read_time:
                            self.handle_sample_detail()
                            GlobalVar.flow_band_sample.sample_detail = []
                            GlobalVar.flow_band_sample.sample_num += 1
                            now_read_time = sql_res[0][3]

                        GlobalVar.flow_band_sample.sample_detail.append(sql_res[0])

                    #检测阶段
                    elif GlobalVar.FLOW_LEARN_FLAG == 2:
                        # 插入数据库，形成前一小时内的point，更新内存中告警类型
                        self.generate_traffic_event(sql_res[0])
                    read_index += 1
                else:
                    time.sleep(1)

            except:
                logger.exception("Exception Logged")
                time.sleep(1)

    def generate_traffic_event(self, cur_dev_traffic):
        '''
        算法：连续3个低点且上次告警不是低阈值告警，此次上报低阈值告警；恢复信息和高阈值告警也是如此。
        数值含义：-1:低，0：恢复，1：高，2：初始值。代码释义：
        if 当前流量 < low:
            if 上次流量类型 == -1:
                类型命中数 += 1
            else:
                上次流量类型 = -1
                类型命中数 = 1
                return

            if 类型命中数 > 2:
                类型命中数 = 0
                if 上次告警类型 == -1：
                    不告警
                else:
                    告警
        '''
        # dev_band_threshold_info dict, key:id values:[IP, MAC, 低阈值，高阈值，上次告警类型， 上次流量类型， 类型命中数]
        dev_id = cur_dev_traffic[0]
        if dev_id in GlobalVar.dev_band_threshold_info:
            #logger.error(GlobalVar.dev_band_threshold_info[dev_id])
            #logger.error(cur_dev_traffic)
            low_threshold = GlobalVar.dev_band_threshold_info[dev_id][2]
            high_threshold = GlobalVar.dev_band_threshold_info[dev_id][3]
            traffic = float(cur_dev_traffic[4])
            if traffic < low_threshold:
                traffic_type = -1
                action = 1 # 0-通过；1-告警；2-阻断；3-通知
            elif traffic > high_threshold:
                traffic_type = 1
                action = 1
            else:
                traffic_type = 0
                action = 3
            if cur_dev_traffic[1] == "NULL":
                dev_ip = ""
            else:
                dev_ip = cur_dev_traffic[1]
            # dev_mac = cur_dev_traffic[2]
            dev_mac=cur_dev_traffic[2].replace(':', '')
            self.refresh_traffic_type_data(traffic_type, dev_id, cur_dev_traffic[3], dev_ip,
                                           low_threshold, high_threshold, traffic, dev_mac, action)

    def refresh_traffic_type_data(self, traffic_type, dev_id, timestamp, ip,
                                  low_threshold, high_threshold, traffic, mac, action):
        if GlobalVar.dev_band_threshold_info[dev_id][5] == traffic_type:
            GlobalVar.dev_band_threshold_info[dev_id][6] += 1
        else:
            GlobalVar.dev_band_threshold_info[dev_id][5] = traffic_type
            GlobalVar.dev_band_threshold_info[dev_id][6] = 1
            return

        if GlobalVar.dev_band_threshold_info[dev_id][6] > 2:
            GlobalVar.dev_band_threshold_info[dev_id][6] = 0
            if GlobalVar.dev_band_threshold_info[dev_id][4] != traffic_type:
                GlobalVar.dev_band_threshold_info[dev_id][4] = traffic_type
                point_time, point_bytes = get_dev_points(dev_id)
                time_int = int(time.mktime(time.strptime(timestamp, '%Y-%m-%d %H:%M:%S')))
                time_bigint="%.6f" % (time.time())
                time_bigint = time_bigint.replace(".","")
                if not ip or ip == "NULL":
                    src_addr = mac
                else:
                    src_addr = ip
                # 字段复用：dpiIp-低阈值，boxId-高阈值，memo-当前流量值
                sql_str = '''insert into incidents_%d (timestamp, sourceIp, destinationIp, appLayerProtocol, action,
                    signatureName, status, protocolDetail, signatureMessage, dpiIp, boxId, memo, deviceId, futureAction, sourceMac, destinationMac, dpi, dpiName, timestampint) values ('%s','%s',
                    '','NA',%d,4,0,"%s","%s",%s,%s,%s,'%s', 0,'%s', '', '%s', '', %s)''' % (self.table_num, time_int, ip, action, point_time, point_bytes,
                                                              low_threshold, high_threshold, traffic, dev_id, mac, src_addr, time_bigint)
                #logger.error(sql_str)
                # 处理sqlstr信息并进行日志上报
                if SYSLOG_UPLOAD["status"]:
                    type_log = "content_traffic_list"
                    handle_info(sql_str, type_log)
                #告警开关  通过表flow_status的值判断开关状态
                db_proxy = DbProxy(CONFIG_DB_NAME)
                sql = 'select flow_status from alarm_switch'
                result, rows = db_proxy.read_db(sql)
                flow_status = rows[0][0]
                if flow_status == 1:
                    self.db_proxy.write_db(sql_str)
                else:
                    pass
                self.table_num = (self.table_num + 1) % 10
                webDpi_obj = get_webdpi_obj()
                dpiip, pro_info, ver_info, sn_info, mw_ip = webDpi_obj.getdpiinfo()
                alert_msg = "流量告警，流量低阈值:%dKbps, 高阈值:%dKbps, 当前流量为:%dKbps" % (low_threshold, high_threshold, traffic)
                log_msg = "%s%s%s||||1|||3|%s" % (sn_info, "|TDHX IMAP_1|", src_addr, alert_msg)
                syslog.syslog(syslog.LOG_NOTICE, log_msg)
                # 获取需要的有效信息,并调用发送函数执行
                if traffic > high_threshold:
                    msg = "1,{}kbps,{}kbps,{}kbps".format(traffic,high_threshold,low_threshold)
                else:
                    msg = "2,{}kbps,{}kbps,{}kbps".format(traffic,high_threshold,low_threshold)
                try:
                    logger.info('enter send_center_msg of traffic incident...')
                    args = (4, msg, ip, mac)
                    send_center_msg(logger, *args)
                except:
                    logger.error(traceback.format_exc())
                    logger.error("send_log_center error...")

    def handle_sample_detail(self):
        #logger.info("sample_detail = %s" % (str(GlobalVar.flow_band_sample.sample_detail)))
        #logger.info("pre sample_info = %s" % (str(GlobalVar.flow_band_sample.sample_info)))
        #logger.info("sample_num = %s" % (str(GlobalVar.flow_band_sample.sample_num)))
        sample_info = GlobalVar.flow_band_sample.sample_info
        sample_num = GlobalVar.flow_band_sample.sample_num

        if 0:
            for sample_elem in GlobalVar.flow_band_sample.sample_detail:
                dev_id = sample_elem[0]
                if sample_info.has_key(dev_id):
                    if sample_info[dev_id][2] > float(sample_elem[4]):
                        sample_info[dev_id][2] = float(sample_elem[4])
                    elif sample_info[dev_id][3] < float(sample_elem[4]):
                        sample_info[dev_id][3] = float(sample_elem[4])
                    else:
                        pass
                    sample_info[dev_id][4] = round((float(sample_info[dev_id][4]) * ( float(sample_num - 1) / (sample_num)) +
                                                   float(sample_elem[4]) / float(sample_num)),1)
                else:
                    sample_info[dev_id] = [sample_elem[1], sample_elem[2], float(sample_elem[4]), float(sample_elem[4]), round(float(sample_elem[4]) / float(sample_num),1)]

        for dev_id in GlobalVar.flow_band_sample.sample_info.keys():
            flag = 0
            for sample_elem in GlobalVar.flow_band_sample.sample_detail:
                if( dev_id == sample_elem[0]):
                    if sample_info[dev_id][2] > float(sample_elem[4]):
                        sample_info[dev_id][2] = float(sample_elem[4])
                    elif sample_info[dev_id][3] < float(sample_elem[4]):
                        sample_info[dev_id][3] = float(sample_elem[4])
                    else:
                        pass
                    sample_info[dev_id][4] = round((float(sample_info[dev_id][4]) * ( float(sample_num - 1) / (sample_num)) +
                                                   float(sample_elem[4]) / float(sample_num)),1)
                    flag = 1
                    break
            if flag == 0:
                sample_info[dev_id][4] = round((float(sample_info[dev_id][4]) * ( float(sample_num - 1) / (sample_num))),1)

        for sample_elem in GlobalVar.flow_band_sample.sample_detail:
            if sample_elem[0] not in GlobalVar.flow_band_sample.sample_info:
                sample_info[sample_elem[0]] = [sample_elem[1], sample_elem[2], float(sample_elem[4]), float(sample_elem[4]), round(float(sample_elem[4]) / float(sample_num),1)]
        #logger.info("calc sample_info = %s" % (str(GlobalVar.flow_band_sample.sample_info)))
        return


class flow_alarm_proc(threading.Thread):
    '''flow band learn ctl thread,link to machinestate process'''
    def __init__(self):
        '''init flow audit object'''
        threading.Thread.__init__(self)
        self.db_proxy = DbProxy()
        logger.info("flow_alarm_proc init ok")

    def run(self):
        while True:
            time.sleep(60)

            try:
                now_timestamp = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(time.time())))
                now_day = datetime.datetime.strptime(now_timestamp, '%Y-%m-%d %H:%M:%S')
                delta_1 = datetime.timedelta(minutes=55)
                cmp_time_str = (now_day - delta_1).strftime("%Y-%m-%d %H:%M:%S")
                cmp_time_str_TZ = cmp_time_str.replace(" ", "T") + "Z"
                now_timestamp_TZ = now_timestamp.replace(" ", "T") + "Z"
                for i in range(0, 10):
                    sql_str = "select count(*) from incidents_%d where signatureName = 4 and futureAction = 0 and timestamp <= '%s' order by timestamp desc " % (i, now_timestamp_TZ)
                    res, sql_res = self.db_proxy.read_db(sql_str)
                    if res == 0:
                        total_num = sql_res[0][0]
                    else:
                        continue
                    left_cnt = total_num
                    index = 0
                    while left_cnt > 0:
                        if left_cnt >= 1000:
                            get_cnt = 1000
                        else:
                            get_cnt = left_cnt

                        sql_str = "select timestamp, deviceId, futureAction, incidentId, protocolDetail, signatureMessage from incidents_%d where signatureName = 4 and futureAction = 0 and timestamp <= '%s' \
                                   order by timestamp desc limit %d offset %d" % (i, now_timestamp_TZ, get_cnt, index*1000)
                        res, sql_res = self.db_proxy.read_db(sql_str)
                        if res != 0:
                            left_cnt -= get_cnt
                            index += 1
                            continue

                        for j in range(0, len(sql_res)):
                            act_flag = 0
                            if sql_res[j][2] != 1:
                                if cmp(cmp_time_str_TZ, sql_res[j][0]) >= 0:
                                    act_flag = 1
                                now_point_time, now_point_bytes = get_dev_points(sql_res[j][1])
                                point_time, point_bytes = self.point_compensation(eval(sql_res[j][4]), eval(sql_res[j][5]), now_point_time, now_point_bytes)
                                if point_time == [] and point_bytes == []:
                                    continue
                                sql_str = '''update incidents_%d set protocolDetail = "%s", signatureMessage = "%s", futureAction = %d where incidentId=%d''' % (i, point_time, point_bytes, act_flag, sql_res[j][3])
                                self.db_proxy.write_db(sql_str)
                            else:
                                continue

                        left_cnt -= get_cnt
                        index += 1
            except:
                logger.exception("Exception Logged")

    def point_compensation(self, alarm_time_list, alarm_point_list, now_time_list, now_point_list):
        if now_time_list == []:
            return alarm_time_list, alarm_point_list
        cmp_res_1 = cmp(alarm_time_list[-1], now_time_list[0])
        if cmp_res_1 < 0:
            return alarm_time_list, alarm_point_list

            #alarm_lateste_time = time.mktime(time.strptime(alarm_time_list[-1], "%Y-%m-%d %H:%M:%S"))
            #now_early_time = time.mktime(time.strptime(now_time_list[0], "%Y-%m-%d %H:%M:%S"))
            #comp_num = (now_early_time - alarm_lateste_time) / 20 - 1
            #if comp_num > 0:
            #    for i in range(0, comp_num):
            #        alarm_point_list.append(0)
            #        alarm_time_list.append(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(alarm_lateste_time + 20 * (i + 1))))
            #alarm_point_list.extend(now_point_list)
            #alarm_time_list.extend(now_time_list)

        else:
            index = 0
            for elem in now_time_list:
                if cmp(alarm_time_list[-1], elem) < 0:
                    break
                index += 1
            if index < len(now_time_list) - 1:
                alarm_time_list = alarm_time_list[(len(now_time_list) - index) : ]
                alarm_point_list = alarm_point_list[(len(now_point_list) - index) : ]
                alarm_time_list.extend(now_time_list[index:])
                alarm_point_list.extend(now_point_list[index:])

            return alarm_time_list, alarm_point_list









