#!/usr/bin/python
# -*- coding:UTF-8 -*-
import os
import time
import threading
import logging
import traceback
import commands

from global_function.global_var import DbProxy, CONFIG_DB_NAME

logger = logging.getLogger('flask_mw_log')


def pcap_cur_status(name):
    try:
        file_name = '/data/tcpdumpdata/' + name
        p = os.path.getsize(file_name)
        cur_size = p / 1024
        return cur_size
    except:
        logger.error(traceback.format_exc())


class GetTcpdumpResult(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.db_proxy = DbProxy(CONFIG_DB_NAME)
        # 异常情况下，读取数据存到存储表pcap_down_data中
        sql_str1 = 'select * from pcap_down_status;'
        res, rows = self.db_proxy.read_db(sql_str1)
        pcap_name = rows[0][2]
        pcap_cur_size = rows[0][5]
        pcap_cur_time = rows[0][6]
        pcap_path = '/data/tcpdumpdata/' + pcap_name
        finish_time = int(time.time())
        if pcap_name != "":
            # 存数据到pcap_down_data表中
            sql_str = "insert into pcap_down_data(finish_time,pcap_cur_size,pcap_cur_time,pcap_name,pcap_path) values ('%s','%s','%s', '%s','%s')" % (
                finish_time, pcap_cur_size, pcap_cur_time, pcap_name, pcap_path)
            self.db_proxy.write_db(sql_str)
            # 初始化pcap_down_status表
            sql_update = "update pcap_down_status set flag=0,pcap_name='',pcap_cur_time=0,pcap_cur_size=0,pcap_orig_size=0,pcap_orig_time=0,pcap_start_time=0"
            db_proxy = DbProxy(CONFIG_DB_NAME)
            db_proxy.write_db(sql_update)
        else:
            pass

    def run(self):
        os.system('mkdir -p /data/tcpdumpdata')
        p_status = 0  # 是否需要抓包状态初始化
        while True:
            try:
                sql_str = "select * from pcap_down_status;"
                res, rows = self.db_proxy.read_db(sql_str)
                flag = rows[0][1]
                pcap_name = rows[0][2]
                # 开始启动抓包
                if p_status == 0 and flag == 1:
                    cmd1 = 'tcpdump -i ethbond0 -s 0 -U -w /data/tcpdumpdata/' + pcap_name + ' &'
                    os.system(cmd1)
                    return_code, output = commands.getstatusoutput('ps -ef |grep tcpdump')
                    pcap_save_dir = "/data/tcpdumpdata/" + pcap_name
                    if output.find(pcap_save_dir) != -1:
                        p_status = 1
                        logger.info("tcpdump启动成功")
                    else:
                        # 启动失败，初始化状态表
                        sql_update = "update pcap_down_status set flag=0,pcap_name='',pcap_cur_time=0,pcap_cur_size=0,pcap_orig_size=0,pcap_orig_time=0,pcap_start_time=0"
                        db_proxy = DbProxy(CONFIG_DB_NAME)
                        db_proxy.write_db(sql_update)
                        os.system('kill -9 $(pidof tcpdump)')
                        logger.info("tcpdump启动失败")
                # 抓包启动后，继续抓包状态
                elif p_status == 1 and flag == 1:
                    try:
                        sql_search = "select * from pcap_down_status"
                        result, rows = self.db_proxy.read_db(sql_search)
                        pcap_name = rows[0][2]
                        pcap_orig_size = int(rows[0][3])
                        pcap_orig_time = int(rows[0][4])
                        pcap_start_time = int(rows[0][7])
                        pcap_cur_size = pcap_cur_status(pcap_name)
                        now_time = int(time.time())
                        run_time = now_time - pcap_start_time
                        if pcap_cur_size > pcap_orig_size * 1024 or run_time > pcap_orig_time or pcap_cur_size > 500 * 1024:
                            os.system('kill -9 $(pidof tcpdump)')
                            finish_time = int(time.time())
                            pcap_path = '/data/tcpdumpdata/' + pcap_name

                            # 防止出现不断加数据到数据库的情况
                            sql_count = "select count(*) from pcap_down_data "
                            res, count_rows = self.db_proxy.read_db(sql_count)
                            total = count_rows[0][0]
                            if int(total) < 10 and pcap_name != "":
                                sql_str = "insert into pcap_down_data(finish_time,pcap_cur_size,pcap_cur_time,pcap_name,pcap_path) values ('%s','%s','%s', '%s','%s')" % (
                                    finish_time, pcap_cur_size, run_time, pcap_name, pcap_path)
                                self.db_proxy.write_db(sql_str)
                                sql_update = "update pcap_down_status set flag=0,pcap_name='',pcap_cur_time=0,pcap_cur_size=0,pcap_orig_size=0,pcap_orig_time=0,pcap_start_time=0"
                                db_proxy = DbProxy(CONFIG_DB_NAME)
                                db_proxy.write_db(sql_update)
                                p_status = 0
                        else:
                            sql_update = "update pcap_down_status set flag=1,pcap_cur_time='%s',pcap_cur_size='%s';" % (
                                run_time, pcap_cur_size)
                            self.db_proxy.write_db(sql_update)
                            p_status = 1
                    except:
                        logger.error(traceback.format_exc())
                # 抓包状态转到停止抓包状态
                elif p_status == 1 and flag == 0:
                    p_status = 0
                # 无需抓包
                else:
                    pass
            except:
                logger.error(traceback.format_exc())
            time.sleep(2)
