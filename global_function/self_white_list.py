# coding=utf-8

import base64
import threading
from cmdline_oper import *
from global_function.dev_auto_identify import devAutoIdentify
from global_var import *
import global_function.global_var

action = "pass"
global file_num
status_data = 0
WHITE_LIST_FLOWDATA_PATH = "/data/log/engines/dpi/flow-data.debug.log"
logger = logging.getLogger('flask_db_socket_log')


class topdeviceinfo:
    def __init__(self):
        self.ip = ''
        self.mac = ''
        self.proto = ''


def list_to_str(list_data):
    special_data = ""
    flag = 0
    data = list_data[0].split(":")[1] + ".whitelist:\""
    tmp_proto = list_data[0].split(':')[1]
    for item in list_data[1:]:
        if item.find(":\"{") != -1 or flag == 1:
            if item.find(":\"{") != -1:
                special_data += item.replace("\"", "")
                flag = 1
            else:
                if item.find("}\"") != -1:
                    special_data += "," + item.replace("\"", "")
                    flag = 0
                else:
                    special_data += ","
                    if tmp_proto == 'focas' or tmp_proto == 'iec104' or tmp_proto == 'dnp3':
                        special_data += item
        else:
            data += item.split(":")[0] + ":{" + item.split(":")[1] + "}"
    rule_data = (data + special_data + "\"").replace("}", "}|")
    rule_data = rule_data.replace("|\"", "\"")
    return rule_data


def set_whitelist_study_status(status):
    global status_data
    status_data = status


def is_exist_deviceinfo(device_list, device_info):
    status = 0
    info_key = "%s%s" % (device_info.ip, device_info.mac)
    if info_key in device_list:
        if device_info.proto in device_list[info_key]:
            return 1
        else:
            status = 1
    else:
        device_list[info_key] = []

    if status == 1:
        return 2
    return 0


class whitelistStudy(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # self.db_proxy = DbProxy(CONFIG_DB_NAME)
        self.whitelist_queue = Queue.Queue(maxsize=queue_limit["whitelistStudy"])
        self.ipmaclist_queue = Queue.Queue(maxsize=queue_limit["whitelistStudy"])
        self.macfilter_queue = Queue.Queue(maxsize=queue_limit["whitelistStudy"])
        logger.info("Init whitelistStudy ok!")

    def make_rules_from_flowdata(self, flowdata_path):
        white_addr = '/data/sock/whitelist_sock'
        try:
            if os.path.exists(white_addr):
                os.remove(white_addr)
        except:
            logger.error("whitelistStudy socket file not exist")
            logger.error(traceback.format_exc())
        db_write_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        db_write_sock.bind(white_addr)

        while True:
            try:
                data, addr = db_write_sock.recvfrom(512)
                # logging.error("whitelist get flowdata data")
            except:
                # logger.error("whitelistStudy:recive data error from dpi")
                logger.error("whitelistStudy:recive data error from dpi")
                logger.error(traceback.format_exc())
            if not data:
                continue
            if self.whitelist_queue.full():
                time.sleep(0.001)
                continue
            try:
                self.whitelist_queue.put(data)
            except:
                continue

    def make_macfilter_from_flowdata(self):
        macfilter_addr = '/data/sock/maclearn_sock'
        try:
            if os.path.exists(macfilter_addr):
                os.remove(macfilter_addr)
        except:
            logger.error("macfilterStudy socket file not exist")
        db_macfilter_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        db_macfilter_sock.bind(macfilter_addr)
        while True:
            data = None
            try:
                # logger.info('start to receive macfilter flowdata')
                # data 是字节串 '\x02\x33\x88' 可转换成16进制
                data, addr = db_macfilter_sock.recvfrom(512)
                # logger.info(data.encode('hex'))
            except:
                logger.error("macfilterStudy:recive data error from dpi")
            if not data:
                continue
            if self.macfilter_queue.full():
                time.sleep(0.001)
                continue
            try:
                self.macfilter_queue.put(data)
            except:
                continue

    def make_macfilter_flowdata(self):
        num_limit = db_record_limit["device"]
        # logger.info("start to parse macfilter flowdata")
        db_proxy = DbProxy(CONFIG_DB_NAME)
        while True:
            data = None
            try:
                data = self.macfilter_queue.get()
                self.generate_macfilter(data, num_limit, db_proxy)
            except:
                if data:
                    logger.error("generate_macfilter failed !! receive data: %s" % str(data))
                logger.error(traceback.format_exc())

    def generate_macfilter(self, data, num_limit, db_proxy):
        try:
            if len(global_function.global_var.macfilter_list) >= num_limit:
                return False
            # logger.debug(data)
            tmp_list = self.unpack_macfilter_data(data)
            # logger.debug(tmp_list)
            for mac in tmp_list:
                if mac:
                    mac_info = "{}".format(mac['mac'])
                    if mac_info not in global_function.global_var.macfilter_list:
                        top_str = "insert into mac_filter (mac,enable) values('%s',0)" % mac['mac']
                        db_proxy.write_db(top_str)
                        global_function.global_var.macfilter_list.append(mac_info)
        except ParameterIllegalException:
            logger.error(traceback.format_exc())
            return False
        except Exception:
            logger.error(traceback.format_exc())
            return False
        return True

    @staticmethod
    def unpack_macfilter_data(data):
        '''
        解析ipmac数据，c数据结构：
        typedef struct {
                uint16_t count; /*value is 1 or 2*/
                uint8_t mac1[6];
                uint8_t mac2[6];
                int port_num;
                } __attribute__((packed)) macfilter_study
        :param data:二进制数据 (str类型)
        :return:
        '''
        # 数据解析格式 按照网络字节序解析，需要源主机将数据按网络字节序进行发送
        tmp_list = []
        try:
            count = struct.unpack_from("!H", data)
            # 至少有一个IP 一个mac
            # 十六进制mac 080302... 字节串按字节截取
            mac1_str = data[2:8].encode('hex')
            mac1 = ':'.join([mac1_str[i:i + 2] for i in range(0, len(mac1_str), 2)])

            tmp_macfilter = dict()
            tmp_macfilter['mac'] = mac1
            tmp_list.append(tmp_macfilter)

            if count[0] == 1:
                pass
            elif count[0] == 2:
                tmp_macfilter = dict()
                mac2_str = data[8:14].encode('hex')
                mac2 = ':'.join([mac2_str[i:i + 2] for i in range(0, len(mac2_str), 2)])
                tmp_macfilter['mac'] = mac2
                tmp_list.append(tmp_macfilter)
            else:
                raise ParameterIllegalException("mac_count", count)
        except ParameterIllegalException, pie:
            raise pie
        except Exception, e:
            raise e
        return tmp_list

    def make_ipmac_from_flowdata(self):
        # 通过bati进程启动该线程，无法使用全局变量logger
        # logger.info('test')
        ipmac_addr = '/data/sock/ipmaclist_sock'
        try:
            if os.path.exists(ipmac_addr):
                os.remove(ipmac_addr)
        except:
            logger.error("ipmaclistStudy socket file not exist")
        db_ipmac_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        db_ipmac_sock.bind(ipmac_addr)

        while True:
            try:
                # logger.info('start to receive ipmaclist flowdata')
                # data 是字节串 '\x02\x33\x88' 可转换成16进制
                data, addr = db_ipmac_sock.recvfrom(512)
                # logger.info(data.encode('hex'))
                # logging.error("whitelist get flowdata data")
            except:
                logger.error("ipmaclistStudy:recive data error from dpi")
            if not data:
                continue
            if self.ipmaclist_queue.full():
                time.sleep(0.001)
                continue
            try:
                self.ipmaclist_queue.put(data)
            except:
                continue

    def make_ipmaclist_flowdata(self):
        num_limit = db_record_limit["device"]
        logger.info("start to parse ipmaclist flowdata")
        db_proxy = DbProxy(CONFIG_DB_NAME)
        while True:
            try:
                data = self.ipmaclist_queue.get()
                self.generate_ipmac(data, num_limit, db_proxy)
            except:
                logger.error("generate_ipmac failed !! receive data: %s" % str(data))
                logger.error(traceback.format_exc())

    def generate_ipmac(self, data, num_limit, db_proxy):
        try:
            tmp_ipmac_list = self.unpack_data(data)
            for ipmac in tmp_ipmac_list:
                if ipmac:
                    ip_info = "{}".format(ipmac['ip'])
                    # 处理拓扑
                    if ip_info not in global_function.global_var.top_list:
                        if ipmac['ip'] != "" and ipmac['ip'].find('.') != -1 and int(
                                ipmac['ip'].split('.')[0]) >= 224:
                            continue
                        if len(global_function.global_var.top_list) >= num_limit:
                            return False
                        tmp_name = get_default_devname_by_ipmac(ipmac['ip'], ipmac['mac'])

                        # 计算设备类型，型号，厂商记录到topdevice表
                        mac = "'"+ipmac['mac']+"'"
                        dev_pro_list = []
                        vendor, dev_type, dev_model, custom_default_flag = devAutoIdentify.calculate_dev_info(mac,dev_pro_list,logger)
                        top_str = """insert into topdevice (name,ip,mac,dev_type,is_study,category_info,dev_mode,proto_info,custom_default_flag) values('%s','%s','%s','%s',1,'%s','%s',"%s",'%s')""" % (tmp_name, ipmac['ip'], ipmac['mac'],dev_type,vendor,dev_model,dev_pro_list,custom_default_flag)
                        res = db_proxy.write_db(top_str)
                        global_function.global_var.top_list.append(ip_info)
                    # 处理ipmac
                    if ip_info not in global_function.global_var.ipmac_list:
                        if ipmac['ip'] != "" and ipmac['ip'].find('.') != -1 and int(
                                ipmac['ip'].split('.')[0]) >= 224:
                            continue
                        if len(global_function.global_var.ipmac_list) >= num_limit:
                            return False
                        tmp_name = get_default_devname_by_ipmac(ipmac['ip'], ipmac['mac'])
                        ipmac_str = "insert into ipmaclist (ip,mac,device_name,enabled,is_study) " \
                                    "values('%s','%s','%s',0,1)" % (ipmac['ip'], ipmac['mac'], tmp_name)
                        db_proxy.write_db(ipmac_str)
                        global_function.global_var.ipmac_list.append(ip_info)
        except ParameterIllegalException:
            logger.error(traceback.format_exc())
            return False
        except Exception:
            logger.error(traceback.format_exc())
            return False
        return True

    def unpack_data(self, data):
        '''
        解析ipmac数据，c数据结构：
        typedef struct {
            unsigned short  count; /*value is 1 or 2*/      ip mac 对数
            unsigned short ip_type; /*4 is ipv4, 6 is ipv6*/
            unsigned char[6] mac1;
            unsigned int[4] ip1; /*ip1[0] 为ipv4地址，整个ip1值为ipv6地址, ip为主机序*/
            unsigned char[6] mac2;
            unsigned int[4] ip2;
            int port_num;
            }
        :param data:二进制数据 (str类型)
        :return:
        '''

        # 数据解析格式 按照网络字节序解析，需要源主机将数据按网络字节序进行发送

        ipmac_list = []

        try:
            count = struct.unpack_from("!H", data)
            ip_type = struct.unpack_from("!H", data, 2)

            # 至少有一个IP 一个mac
            # 十六进制mac 080302... 字节串按字节截取
            mac1_str = data[4:10].encode('hex')
            mac1 = ':'.join([mac1_str[i:i + 2] for i in range(0, len(mac1_str), 2)])
            # mac1_tuple = struct.unpack_from("!6B", data, 4)
            # mac1 = ':'.join([hex(v)[2:] for v in mac1_tuple])

            ipmac = dict()
            ipmac['mac'] = mac1
            if ip_type[0] == 4:
                ip1_tuple = struct.unpack_from("!I", data, 10)
                ip1 = self.__int_to_ip(ip1_tuple[0], 4)
            elif ip_type[0] == 6:
                ip1_tuple = struct.unpack_from("!4I", data, 10)
                ip1 = self.__int_to_ip(ip1_tuple, 6)
                ip1 = ipaddress.ip_network(unicode(ip1)).exploded.split('/')[0]
            else:
                raise ParameterIllegalException("ip_type", ip_type[0])
            ipmac['ip'] = ip1
            ipmac_list.append(ipmac)
            if count[0] == 1:
                pass
            elif count[0] == 2:
                ipmac = dict()
                mac2_str = data[26:32].encode('hex')
                mac2 = ':'.join([mac2_str[i:i + 2] for i in range(0, len(mac2_str), 2)])
                # mac2_tuple = struct.unpack_from("!6B", data, 26)
                # mac2 = ':'.join([hex(v)[2:] for v in mac2_tuple])
                if ip_type[0] == 4:
                    ip2_tuple = struct.unpack_from("!I", data, 32)
                    ip2 = self.__int_to_ip(ip2_tuple[0], 4)
                elif ip_type[0] == 6:
                    ip2_tuple = struct.unpack_from("!4I", data, 32)
                    ip2 = self.__int_to_ip(ip2_tuple, 6)
                    ip2 = ipaddress.ip_network(unicode(ip2)).exploded.split('/')[0]
                else:
                    raise ParameterIllegalException("ip_type", ip_type[0])
                ipmac['ip'] = ip2
                ipmac['mac'] = mac2
                ipmac_list.append(ipmac)
            else:
                raise ParameterIllegalException("ip_type", ip_type[0])
        except ParameterIllegalException, pie:
            raise pie
        except Exception, e:
            raise e
        return ipmac_list

    def __int_to_ip(self, value, ip_type):
        '''
        整数转IP
        :param value:整数，网络序
        :param ip_type: 4 or 6
        :return: ip点分十进制
        '''
        ip = ""
        if ip_type == 4:
            try:
                return socket.inet_ntoa(struct.pack('!I', value))
            except Exception:
                raise Exception("整数转换IP错误")
        elif ip_type == 6:
            try:
                ipv6 = struct.pack('!4I', value[0],  value[1],  value[2],  value[3])
                return socket.inet_ntop(socket.AF_INET6, ipv6)
            except Exception:
                logger.error(traceback.format_exc())
        else:
            raise ParameterIllegalException("ip_type", ip_type)

    def make_whitelist_flowdata(self, sid):
        num_limit = db_record_limit["device"]
        logger.info("start to receive whitelist flowdata")
        db_proxy = DbProxy(CONFIG_DB_NAME)
        while True:
            try:
                data = self.whitelist_queue.get()
                flag = self.generate_rules(data, sid, num_limit, db_proxy)
                if flag:
                    sid += 1
            except:
                logger.error("generate_rules failed !! receive data: %s" % str(data))
                logger.error(traceback.format_exc())

    def generate_rules(self, data, sid, num_limit, db_proxy):
        global status_data
        tmp_intf_pos = data.find(';')
        tmp_intf = data[0:tmp_intf_pos]
        data = data[tmp_intf_pos + 1:]
        cheack_flow_data = base64.b64encode(data)
        if len(global_function.global_var.whitelist_info) >= db_record_limit["whitelist"]:
            return False
        if cheack_flow_data in global_function.global_var.whitelist_info:
            return False

        global_function.global_var.whitelist_info.append(cheack_flow_data)
        flow_data_start = data.find('{')
        flow_data_end = data.rfind('}')
        flow_data_db = data[flow_data_start + 1:flow_data_end]
        data_rule = list_to_str(data.split(";")[4][1: data.split(";")[4].rfind('}')].split(','))
        protocol = data_rule.split(".")[0]
        now = time.time()
        timestamp = time.strftime("-%Y-%m-%d-%H:%M:%S", time.localtime(now))
        rule_name = str(protocol) + str(timestamp)
        srcinfo = topdeviceinfo()
        dstinfo = topdeviceinfo()
        if protocol == "goose" or protocol == "sv" or protocol == 'pnrtdcp':
            sip = data.split(";")[2]
            dip = data.split(";")[3]
            ipmac_flag = 1
            data_rule = data_rule.replace("whitelist", "L2whitelist")
            srcinfo.mac = sip
            dstinfo.mac = dip
        else:
            sip = data.split(";")[0]
            dip = data.split(";")[1]
            smac = data.split(";")[2]
            dmac = data.split(";")[3]
            ipmac_flag = 1
            srcinfo.ip = sip
            srcinfo.mac = smac
            dstinfo.ip = dip
            dstinfo.mac = dmac
        if ipmac_flag == 0:
            return False
        if protocol == "opcda":
            protocol = "dcerpc"
        elif protocol == "profinetio":
            protocol = "dcerpcudp"

        if protocol == "tls":
            protocol = "https"
            data_str = "%s %s %s any -> %s any (%s; policy:1; sid:%d; rev:1;)" % (
                action, "tls", sip, dip, data_rule, sid)
        else:
            data_str = "%s %s %s any -> %s any (%s; policy:1; sid:%d; rev:1;)" % (
                action, protocol, sip, dip, data_rule, sid)
        data_str = base64.b64encode(data_str)
        srcinfo.proto = protocol
        dstinfo.proto = protocol
        tmp_proto = 0
        srcdevice_str = ""
        dstdevice_str = ""
        try:
            tmp_proto = PROTOCAL_LIST.index(srcinfo.proto) + 1
        except:
            logger.info("whitelist get proto type error")
        # 自动识别厂商字段，已去重，学习时默认为自动识别厂商
        auto_flag = 1
        # 源地址进行top处理
        tmp_srcmac = ':'.join((re.findall(r'.{2}', srcinfo.mac)))
        if srcinfo.ip:
            tmp_src_info = "{}".format(srcinfo.ip)
        else:
            tmp_src_info = "{}".format(tmp_srcmac)
        if not srcinfo.ip and tmp_src_info not in global_function.global_var.top_list:
            tmp_name = get_device_name(srcinfo.ip, srcinfo.mac)
            srcdevice_str = "insert into topdevice (name,ip,mac,dev_type,is_study,dev_interface,category_info,auto_flag) " \
                            "values ('%s','%s','%s',0,1,%s,'%s','%d')" % (tmp_name, srcinfo.ip, tmp_srcmac,
                                                                     tmp_intf, get_vendor_by_mac(tmp_srcmac), auto_flag)
            global_function.global_var.top_list.append(tmp_src_info)
        # 目的地址进行top处理
        tmp_dstmac = ':'.join((re.findall(r'.{2}', dstinfo.mac)))
        if dstinfo.ip:
            tmp_dst_info = "{}".format(dstinfo.ip)
        else:
            tmp_dst_info = "{}".format(tmp_dstmac)
        if not dstinfo.ip and tmp_dst_info not in global_function.global_var.top_list:
            tmp_name = get_device_name(dstinfo.ip, dstinfo.mac)
            dstdevice_str = "insert into topdevice (name,ip,mac,dev_type,is_study,dev_interface,category_info,auto_flag) " \
                            "values ('%s','%s','%s',0,1,%s,'%s','%d')" % (tmp_name, dstinfo.ip, tmp_dstmac,
                                                                     tmp_intf, get_vendor_by_mac(tmp_dstmac), auto_flag)
            global_function.global_var.top_list.append(tmp_dst_info)
        insert_sql = "INSERT INTO rules (action,id,fields,body,filterfields," \
                     "riskLevel,ruleName,srcIp,dstIp,srcMac,dstMac,proto) " \
                     "VALUES (0,%d,'%s','%s','%s',1,'%s','%s','%s','%s','%s',%d)" % (sid, flow_data_db, data_str,
                                                                                     cheack_flow_data, rule_name,
                                                                                     srcinfo.ip, dstinfo.ip,
                                                                                     tmp_srcmac, tmp_dstmac, tmp_proto)
        _ = db_proxy.write_db(insert_sql)
        if len(srcdevice_str) > 0:
            _ = db_proxy.write_db(srcdevice_str)
        if len(dstdevice_str) > 0:
            _ = db_proxy.write_db(dstdevice_str)
        return True

    def GetDbSid(self):
        db_proxy = DbProxy(CONFIG_DB_NAME)
        result, rule_id = db_proxy.read_db("select max(id) from rules")
        sid = 200100
        for sid_db in rule_id:
            if sid_db[0] is None:
                break
            else:
                sid = sid_db[0] + 1
        return sid

    def run(self):
        sid = self.GetDbSid()
        t1 = threading.Thread(target=self.make_whitelist_flowdata, args=(sid,))
        t1.setDaemon(True)
        t1.start()

        t2 = threading.Thread(target=self.make_rules_from_flowdata, args=(WHITE_LIST_FLOWDATA_PATH,))
        t2.setDaemon(True)
        t2.start()

        t3 = threading.Thread(target=self.make_ipmaclist_flowdata)
        t3.setDaemon(True)
        t3.start()

        t4 = threading.Thread(target=self.make_ipmac_from_flowdata)
        t4.setDaemon(True)
        t4.start()

        t5 = threading.Thread(target=self.make_macfilter_from_flowdata)
        t5.setDaemon(True)
        t5.start()

        t6 = threading.Thread(target=self.make_macfilter_flowdata)
        t6.setDaemon(True)
        t6.start()

        t6.join()


class ParameterIllegalException(Exception):
    '''
    主要用于通过socket接收的数据的合法性验证，比如ip_table，定义只能是4 6，如果接收到其它数据，应该在相关方法最底层抛出该异常，上层捕捉并处理异常
    '''
    def __init__(self, parameter_name, para_value, desc=""):
        '''
        :param parameter_name:参数名
        :param para_value: 值
        :param desc: 自定义描述（可选）
        '''
        err_msg = 'socket received the data {0}={1} is illegal；{2}'.format(parameter_name, para_value, desc)
        Exception.__init__(self, err_msg)
        self.parameter_name = parameter_name
        self.para_value = para_value
