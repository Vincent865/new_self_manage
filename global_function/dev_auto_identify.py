#! /usr/bin/env python
# coding=utf-8
import chardet
import threading
# from log_config import LogConfig
from global_function.global_var import *
import logging

# LogConfig('flask_mw.log')
logger = logging.getLogger('flask_db_socket_log')


class devAutoIdentify(threading.Thread):
    devautoQueue = Queue.Queue(maxsize=queue_limit["devAutoIdentify"])

    def __init__(self):
        '''init devAutoIdentify object'''
        threading.Thread.__init__(self)

    def run(self):
        self.runDevGetData()
        '''run devAutoIdentify obj'''

    @staticmethod
    def runDevPutData(dev_data):
        try:
            if devAutoIdentify.devautoQueue.full():
                time.sleep(0.001)
            devAutoIdentify.devautoQueue.put(dev_data)
        except:
            logger.error(traceback.format_exc())

    # 接收数据
    def runDevGetData(self):
        num = 0
        while True:
            try:
                flowinfo = self.devautoQueue.get()
                # logger.info(flowinfo)
            except:
                logger.error(traceback.format_exc())
                continue

            try:
                self.writeDevDataInDB(flowinfo)
            except:
                logger.error(traceback.format_exc())
            num += 1

    # 根据mac识别厂商
    @staticmethod
    def get_vendor_by_mac(mac,logger):
        mac = mac.replace(':', '')
        mac = mac[1:7].upper()
        sql_str = "select vendor from dev_vendor_mac where mac = '%s'" % (mac)
        db_proxy_config = DbProxy(CONFIG_DB_NAME)
        res, rows = db_proxy_config.read_db(sql_str)
        if res == 0 and len(rows) > 0:
            vendor = rows[0][0]
        else:
            vendor = "未知"
        return vendor

    # 封装proto_info
    @staticmethod
    def pack_data(name, port, flag):
        if flag == 1:
            packed_info = "[" + name + ",'',1]"  # 协议--1
        else:
            packed_info = "[" + name + ",'" + str(port) + "',2]"  # 协议-端口-2
        packed_info = eval(packed_info)
        return packed_info

    # 解包proto_info
    @staticmethod
    def unpack_data(data):
        # dev_proto_info = ['sv','6005',1]
        name = data[0]
        port = data[1]
        attr = data[2]
        return name, port, attr

    # 计算mac地址是否匹配指纹
    @staticmethod
    def cmp_dev_fig_mac_list(dev_mac_list, fig_mac_list, logger):
        """
        :param mac_list: ['00:50:56', '00:50:56:2a', '00:50:56:2a:ce', '00:50:56:2a:ce:ee']
        :param finger_mac: ['f0:76:1c:6d:ad:5d','00:50:56:2a:ce:ee']
        """
        # logger.info("待匹配mac_list："+str(dev_mac_list))
        # logger.info("指纹库中mac："+str(fig_mac_list))
        for mac in dev_mac_list:
            if mac in fig_mac_list:
                # logger.info("++++++++mac匹配成功+++++++++++")
                return True
        return False

    # 计算proto_info是否匹配指纹
    @staticmethod
    def cmp_dev_fig_pro_list(dev_pro_list, fig_pro_list,logger):
        """
        :param dev_pro_list: [['opcda','3072',2],['s7','102',2],['http','',1]]  ------当前：['http','',1]
        :param fig_pro_list: [['opcda','',0],['sv','205',0]]
        """
        # logger.info("指纹库中指纹："+str(fig_pro_list))
        # logger.info("待匹配dev_proto_info："+str(dev_pro_list))
        if not fig_pro_list:
            return True

        for fig_pro in fig_pro_list:
            for dev_pro in dev_pro_list:
                result = devAutoIdentify.cmp_dev_fig_pro_elm(dev_pro, fig_pro)
                if result:
                    # logger.info("+++++++++++proto_info匹配成功++++++++++++++++")
                    return True
        return False

    # 比较单个元素
    @staticmethod
    def cmp_dev_fig_pro_elm(dev_pro, fig_pro):
        """
        :param dev_pro: ['opcda', '', 0]
        :param fig_pro: ['opcda', '3072', 2]
        """
        for i in range(3):
            if fig_pro[i] == "" or fig_pro[i] == 0:
                continue
            else:
                if dev_pro[i] == fig_pro[i]:
                    continue
                else:
                    return False
        return True

    # 1、更新资产表中proto_info
    @staticmethod
    def add_proto_info(ip, mac, proto_info_list):
        db_proxy_config = DbProxy(CONFIG_DB_NAME)
        sql_str = '''update topdevice set proto_info = "%s" where ip = %s and mac = %s''' % (
            proto_info_list, ip, mac)
        # logger.info(sql_str)
        db_proxy_config.write_db(sql_str)

    # 2、计算设备信息（1、指纹，2、预定义）
    @staticmethod
    def calculate_dev_info(mac, dev_pro_list, logger=logger):
        try:
            # 自定义计算
            result = devAutoIdentify.custom_calculate_dev_info(mac, dev_pro_list,logger)
            res = result["cmp_result"]
            if res:
                vendor = result["vendor"]
                dev_type = result["dev_type"]
                dev_model = result["dev_model"]
                custom_default_flag = result["custom_default_flag"]
                # logger.info("=================指纹识别成功=================")
            else:
                # 正常识别，自定义计算失败，预定义计算
                # logger.info("++++++++++指纹识别失败++++++++++预定义识别开始+++++++++++")
                vendor, dev_type, dev_model, custom_default_flag = devAutoIdentify.default_calculate_dev_info(mac, dev_pro_list,logger)
            return vendor, dev_type, dev_model, custom_default_flag
        except:
            logger.error(traceback.format_exc())
            return "未知", 0, "未知", "1"

    # 2-1、根据指纹计算设备信息
    @staticmethod
    def custom_calculate_dev_info(mac, dev_pro_list,logger):
        try:
            db_proxy_config = DbProxy(CONFIG_DB_NAME)
            custom_default_flag = "0"  # 指纹匹配标记为0
            dev_info = {"cmp_result": 0, "vendor": "", "dev_type": 0, "dev_model": "", "custom_default_flag": ""}
            # 待匹配mac_list（一个mac分四个['00:50:56', '00:50:56:2a', '00:50:56:2a:ce', '00:50:56:2a:ce:ee']
            # 待匹配的dev_pro_list
            dev_mac_list = []
            for i in range(9, 21, 3):
                dev_mac_list.append(mac[1:i] + (":") * ((17 - len(mac[1:i])) / 3))
            # 指纹库中的fig_mac_list['00:50:56:::']和fig_pro_list
            sql_str = "select mac, proto_port_attr, vendor, dev_type,dev_model from self_define_fingerprint order by update_time desc"
            res, rows = db_proxy_config.read_db(sql_str)
            for row in rows:
                fig_mac_list = eval(row[0])
                fig_pro_list = eval(row[1])
                vendor = row[2]
                dev_type = row[3]
                dev_model = row[4]

                # 1、计算MAC地址是否匹配
                mac_res = devAutoIdentify.cmp_dev_fig_mac_list(dev_mac_list, fig_mac_list,logger)
                if not mac_res:
                    continue

                # 2、计算协议端口是否匹配（['opcda', '3072', 2]）
                proto_res = devAutoIdentify.cmp_dev_fig_pro_list(dev_pro_list, fig_pro_list,logger)
                if not proto_res:
                    continue
                # logger.info("mac识别结果："+str(mac_res))
                # logger.info("协议识别结果："+str(proto_res))
                if mac_res and proto_res:
                    # 数据格式更改
                    dev_info["cmp_result"] = 1
                    dev_info["vendor"] = vendor
                    dev_info["dev_type"] = dev_type
                    dev_info["dev_model"] = dev_model
                    dev_info["custom_default_flag"] = custom_default_flag
                    return dev_info
            return dev_info
        except:
            logger.error(traceback.format_exc())
            return {"cmp_result": 0, "vendor": "未知", "dev_type": 0, "dev_model": "未知", "custom_default_flag": "1"}
    # 2-2、预定义计算设备信息
    @staticmethod
    def default_calculate_dev_info(mac, dev_pro_list,logger):
        try:
            db_proxy_config = DbProxy(CONFIG_DB_NAME)
            vendor = devAutoIdentify.get_vendor_by_mac(mac,logger)
            dev_model = "未知"
            custom_default_flag = "1"  # 预定义计算出标记为1

            if not dev_pro_list:  # 去除特殊情况[]
                dev_type = 0
                return vendor, dev_type, dev_model, custom_default_flag

            # 循环此设备的dev_pro_list  [[xxx],[yyy]]
            for proto_info in dev_pro_list:
                proto_name, _, dev_flag = devAutoIdentify.unpack_data(proto_info)
                if dev_flag == 1:  # 客户端
                    sql_str = "select client_type from proto_dev_type where proto_type = '%s'" % (proto_name)
                else:  # 服务器
                    sql_str = "select server_type from proto_dev_type where proto_type = '%s'" % (proto_name)
                res, rows = db_proxy_config.read_db(sql_str)
                dev_type = rows[0][0]
                if dev_type != 0:  # 识别出“未知”，继续往后识别，直到识别出类型；如果最终未识别出，最终就是“未知”
                    return vendor, dev_type, dev_model, custom_default_flag
                return vendor, dev_type, dev_model, custom_default_flag
        except:
            logger.error(traceback.format_exc())
            return "未知", 0, "未知", "1"

    # 识别主入口
    def writeDevDataInDB(self, flowinfo):
        '''
        flowinfo = ["'2019-11-18 14:20:32'", '1574058032', "'00:50:56:2a:ce:ee'", "'f0:76:1c:6d:ad:5d'", '4',
                    "'192.168.1.21'", '49155', "'192.168.1.15'", '34964', '0', "''", '0', "'14'", '1574058032732611']
        '''
        db_proxy_config = DbProxy(CONFIG_DB_NAME)
        global protocol_names
        protID = flowinfo[12][1:-1]
        if int(protID) > 500:
            cmd_str = "select proto_name from self_define_proto_config where proto_id = %d" % int(protID)
            res, rows = db_proxy_config.read_db(cmd_str)
            if len(rows) > 0:
                proto_name = "'" + rows[0][0] + "'"
            else:
                proto_name = "'NA'"
        else:
            proto_name = "'" + protocol_names[int(protID)] + "'"
        logger.info(flowinfo)
        logger.info(proto_name)

        cli_ip = flowinfo[5]
        cli_mac = flowinfo[2]
        cli_port = flowinfo[6]
        cli_attr = 1
        ser_ip = flowinfo[7]
        ser_mac = flowinfo[3]
        ser_port = flowinfo[8]
        ser_attr = 2
        # flag = 1  # 标记此条设备信息是流上报
        devAutoIdentify.dev_auto_identify(cli_ip, cli_mac, proto_name, cli_port, cli_attr)
        devAutoIdentify.dev_auto_identify(ser_ip, ser_mac, proto_name, ser_port, ser_attr)

    @staticmethod
    def dev_auto_identify(ip, mac, proto_name, port, attr):
        # 查询此设备是否存在
        db_proxy_config = DbProxy(CONFIG_DB_NAME)
        sql_str = "select count(*) from topdevice where ip = %s and mac = %s" % (ip, mac)
        res, rows = db_proxy_config.read_db(sql_str)
        if len(rows) > 0:
            exit_flag = 1
        else:
            exit_flag = 0

        # 查询此设备是否设置是自动识别
        sql_str = "select auto_flag from topdevice where ip = %s and mac = %s" % (ip, mac)
        res, rows = db_proxy_config.read_db(sql_str)
        auto_flag = 0
        if len(rows) > 0:
            for row in rows:
                auto_flag = row[0]

        # 设备存在并且为自动识别，更新proto_info,计算设备信息
        if exit_flag and auto_flag:
            sql_str = "select proto_info from topdevice where ip = %s and mac = %s" % (ip, mac)
            res, rows = db_proxy_config.read_db(sql_str)
            dev_pro_list = eval(rows[0][0])

            # 封装 此条设备proto_info信息['opcda','3072',0]
            tmp_proto_info = devAutoIdentify.pack_data(proto_name, port, attr)

            # 去重，更新 此条设备的proto_info_list
            if tmp_proto_info not in dev_pro_list:
                dev_pro_list.append(tmp_proto_info)

            # 1、记录proto_info到数据库['opcda','3072',0]
            devAutoIdentify.add_proto_info(ip, mac, dev_pro_list)

            # 2、计算厂商，类型，型号 flag是标记计算单个还是计算多个的标志  flag
            vendor, dev_type, dev_model, custom_default_flag = devAutoIdentify.calculate_dev_info(mac, dev_pro_list,logger)

            # 3、记录厂商，类型，型号
            update_str = '''update topdevice set category_info = "%s", dev_mode = "%s",dev_type = %d, custom_default_flag = "%s" where ip = %s and mac = %s''' % (
                vendor, dev_model, dev_type, custom_default_flag, ip, mac)
            db_proxy_config.write_db(str(update_str))
            # logger.info(update_str)

