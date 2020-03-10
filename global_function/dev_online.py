#!/usr/bin/python
# -*- coding:UTF-8 -*-
import threading
import random
from global_var import *
import time

logger = logging.getLogger('flask_db_socket_log')


class DeviceOnline(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        db_proxy = DbProxy()
        config_db_proxy = DbProxy(CONFIG_DB_NAME)
        old_live_dev = []
        old_unlive_dev = []
        sql = 'select check_time from top_config where id=1'
        _, rows = config_db_proxy.read_db(sql)
        pre_conf = rows[0][0] * 60
        pre_reporttime = time.time()
        while True:
            time.sleep(2)
            conf_str = 'select check_time from top_config where id=1'
            _, conf_rows = config_db_proxy.read_db(conf_str)
            if conf_rows:
                conf_time = conf_rows[0][0] * 60
            else:
                conf_time = 5*60
            if conf_time == pre_conf:#如果配置没有发生改变
                pass
            else:#如果配置改变
                pre_reporttime = time.time()
                pre_conf = conf_time
            now = time.time()
            if now - pre_reporttime >= conf_time:
                tmp_live_dev = []
                tmp_unlive_dev = []
                all_str = 'select ip,mac from topdevice'
                _, all_rows = config_db_proxy.read_db(all_str)
                sql_str = "select devip,devmac from dev_band_20s where unix_timestamp(timestamp)>=unix_timestamp(CURRENT_TIMESTAMP())-{} group by devip,devmac HAVING sum(band)>=0.01".format(conf_time+2)
                logger.info(sql_str)
                _, rows = db_proxy.read_db(sql_str)
                tmp_rows = []
                for r in rows:
                    tmp_r = list(r)
                    if r[0] == 'NULL':
                        tmp_r[0] = ''
                    tmp_rows.append(tuple(tmp_r))
                tmp_rows = tuple(tmp_rows)
                tmp_res_rows = tuple(set(all_rows) & set(tmp_rows))
                update_str = "update topdevice set is_live= case when (ip,mac) in(('',''),"
                for r in tmp_res_rows:
                    tmp_ip = r[0]
                    tmp_mac = r[1]
                    if tmp_ip == 'NULL':
                        tmp_ip = ''
                    tmp_str = "('%s','%s')," % (tmp_ip, tmp_mac)
                    update_str += tmp_str
                update_str = update_str[:-1]
                update_str += ') Then 1 else 0 end'
                logger.error(update_str)
                _ = config_db_proxy.write_db(update_str)
                not_rows = tuple(set(all_rows) - set(tmp_res_rows))
                rand_num = random.randint(0, 9)
                data_str = "insert into incidents_%d(timestamp,sourceName,sourceIp,sourceMac,destinationName," \
                        "destinationIp,destinationMac,appLayerProtocol,signatureName,action,timestampint,status,dpi,tableNum,matchedKey) values" % rand_num
                tmp_time = int(round(time.time() * 1000 * 1000))
                tmp_i = 0
                for r in tmp_res_rows:
                    tmp_ip = r[0]
                    tmp_mac = r[1]
                    if tmp_ip == 'NULL':
                        tmp_ip = ''
                    tmp_info = tmp_ip + tmp_mac
                    tmp_name = get_default_devname_by_ipmac(tmp_ip, tmp_mac)
                    tmp_val = ''
                    if tmp_info not in old_live_dev:  # 在线且上次不在线
                        tmp_mac = tmp_mac.replace(':', '')
                        if tmp_ip:
                            tmp_dpi = tmp_ip
                        else:
                            tmp_dpi = tmp_mac
                        tmp_val = "(unix_timestamp(now()),'%s','%s','%s','NA','NA','NA','NA','6',3,%d,0,'%s',%d,'设备上线')" \
                                % (tmp_name, tmp_ip, tmp_mac, tmp_time + tmp_i, tmp_dpi, rand_num)
                        # 每次资产告警消息单独处理并发送到安管平台
                        try:
                            tmp_mac = tmp_mac.replace(":", "")
                            logger.info('enter send_center_msg of incidents about dev_alert')
                            args = (6, 3, tmp_ip, tmp_mac)
                            send_center_msg(logger, *args)
                        except:
                            logger.error(traceback.format_exc())
                            logger.error("send_log_center error...")
                    tmp_live_dev.append(tmp_info)
                    tmp_i += 1
                    if tmp_val:
                        data_str += tmp_val
                        data_str += ","
                for r in not_rows:
                    tmp_ip = r[0]
                    tmp_mac = r[1]
                    if tmp_ip == 'NULL':
                        tmp_ip = ''
                    tmp_info = tmp_ip + tmp_mac
                    tmp_name = get_default_devname_by_ipmac(tmp_ip, tmp_mac)
                    tmp_val = ''
                    if tmp_info not in old_unlive_dev:  # 不在线且上次在线
                        tmp_mac=tmp_mac.replace(':', '')
                        if tmp_ip:
                            tmp_dpi = tmp_ip
                        else:
                            tmp_dpi = tmp_mac
                        tmp_val = "(unix_timestamp(now()),'%s','%s','%s','NA','NA','NA','NA','6',1,%d,0,'%s',%d,'设备离线')" \
                                % (tmp_name, tmp_ip, tmp_mac, tmp_time + tmp_i, tmp_dpi, rand_num)
                        # 每次资产告警消息单独处理并发送到安管平台
                        try:
                            tmp_mac=tmp_mac.replace(":", "")
                            logger.info('enter send_center_msg of incidents about dev_alert')
                            args = (6, 1, tmp_ip, tmp_mac)
                            send_center_msg(logger, *args)
                        except:
                            logger.error(traceback.format_exc())
                            logger.error("send_log_center error...")
                    tmp_unlive_dev.append(tmp_info)
                    tmp_i += 1
                    if tmp_val:
                        data_str += tmp_val
                        data_str += ","
                data_str = data_str[:-1]
                logger.info(data_str)
                db_proxy.write_db(data_str)
                old_live_dev = tmp_live_dev[:]
                old_unlive_dev = tmp_unlive_dev[:]
                pre_reporttime = time.time()
                           

