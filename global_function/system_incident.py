#!/usr/bin/python
# -*- coding:UTF-8 -*-
import threading
import syslog
from log_oper import *

logger = logging.getLogger('flask_mw_log')


class SystemIncident(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.equipment_content = ''
        self.port_content = {}
        self.bypass_content = {}
        self.dpi_yaml = "/data/configuration/southwest_engines/dpi.yaml"
        self.service_port_num = 0
        self.level = [LOG_ALERT, LOG_INFO]
        self.log_head = "|TDHX IMAP_2|"
        logger.info("Init SystemIncident ok!")

    def run(self):
        try:
            self.init_class_variable()
        except:
            logger.error(traceback.format_exc())

        while True:
            try:
                self.deal_southwest_status()
                self.deal_sevice_port_link_status()
                #self.deal_bypass_status()
            except:
                logger.error(traceback.format_exc())
            time.sleep(3)

    def init_class_variable(self):
        db_proxy = DbProxy()

        # southwest engine previous status
        resut, rows = db_proxy.read_db("select max(eventId) from events where componetName='engine'")
        event_id = rows[0][0]
        if event_id is not None:
            resut, rows = db_proxy.read_db("select content from events where eventId=%d" % event_id)
            self.equipment_content = rows[0][0].decode('utf8')

        # P0-Pn previous status
        ok, portmap = mw_get_interface_map()
        if ok == 0:
            key_array = []
            value_array = []
            phy_interfaces = os.popen("cat /proc/net/dev | awk -F: '/eth[0-9]/{print $1}'").read().strip('\n')
            key_array = phy_interfaces.replace('\n', ',').replace(' ', '').split(',')
            value_array = phy_interfaces.replace('\n', ',').replace(' ', '').replace('eth', 'p').split(',')
            portmap = dict(zip(key_array, value_array))

        #res = commands.getoutput("mii-tool")
        self.service_port_map = portmap
        for key, value in portmap.items():
            self.port_content[key] = ''
            result, rows = db_proxy.read_db("select max(eventId) from events where componetName='%s'" % key)
            event_id = rows[0][0]
            if event_id is not None:
                resut, rows = db_proxy.read_db("select content from events where eventId=%d" % event_id)
                self.port_content[key] = rows[0][0].decode('utf8')

        # bypass previous status
        for i in range(2):
            self.bypass_content['bp%d' % i] = ''
            result, rows = db_proxy.read_db("select max(eventId) from events where componetName='bp%d'" % i)
            event_id = rows[0][0]
            if event_id is not None:
                resut, rows = db_proxy.read_db("select content from events where eventId=%d" % event_id)
                self.bypass_content['bp%d' % i] = rows[0][0].decode('utf8')

    def get_ps_result(self):
        pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
        ps_result = []
        for pid in pids:
            try:
                ps_result.append(pid + ' ' + open(os.path.join('/proc', pid, 'cmdline'), 'rb').read())
            except IOError:  # proc has already terminated
                continue
        return ps_result

    def get_port_state(self, cmd):
        res = commands.getoutput(cmd)
        if res.find('RUNNING') != -1:
            state = 1
        else:
            state = 0
        return state

    def deal_southwest_status(self):
        pid = 0
        try:
            result = self.get_ps_result()
            for line in result:
                if line.find(self.dpi_yaml) != -1:
                    pid = 1
                    break
        except:
            pid = 0
        # type 0 is equipment connect status; status default is 0(no read)
        content = [u'数据包引擎停止', u'数据包引擎启动']
        if content[pid] != self.equipment_content:
            self.equipment_content = content[pid]
            msg = {'Type': SYSTEM_TYPE, 'LogLevel': self.level[pid], 'Content': content[pid], 'Componet': 'engine'}
            send_log_db(MODULE_SYSTEM, msg)
            if self.level[pid] == LOG_ALERT:
                webDpi_obj = get_webdpi_obj()
                dpiip, pro_info, ver_info, sn_info, mw_ip = webDpi_obj.getdpiinfo()
                log_msg = "%s%s%d|%s"%(sn_info, self.log_head, SYSTEM_TYPE, content[0].encode('utf-8'))
                syslog.syslog(syslog.LOG_NOTICE, log_msg)


    # def deal_sevice_port_link_status(self):
    #     content_list = [u"未连接", u"连接"]
    #     for key, value in self.service_port_map.items():
    #         stat = self.get_port_state('ifconfig %s' % value)
    #         level = self.level[stat]
    #         cur_content = key + content_list[stat]
    #         if cur_content != self.port_content[key]:
    #             self.port_content[key] = cur_content
    #             msg = {'Type': IFSTATUS_TYPE, 'LogLevel': level, 'Content': cur_content, 'Componet': key}
    #             send_log_db(MODULE_SYSTEM, msg)
    #             if level == LOG_ALERT:
    #                 webDpi_obj = get_webdpi_obj()
    #                 dpiip, pro_info, ver_info, sn_info, mw_ip = webDpi_obj.getdpiinfo()
    #                 log_msg = "%s%s%d|%s" % (sn_info, self.log_head, IFSTATUS_TYPE, cur_content.encode('utf-8'))
    #                 syslog.syslog(syslog.LOG_NOTICE, log_msg)

    def deal_sevice_port_link_status(self):
        content_list = [u"未连接", u"连接"]
        content_list1 = [u"Link down", u"Link up"]
        for key, value in self.service_port_map.items():
            stat = self.get_port_state('ifconfig %s' % value)
            ''' link up down is not alert'''
            level = self.level[1]
            cur_content = value.upper() + content_list[stat]
            cur_content1 = value.upper() + ' ' + content_list1[stat]
            if cur_content != self.port_content[key]:
                self.port_content[key] = cur_content
                msg = {'Type': IFSTATUS_TYPE, 'LogLevel': level, 'Content': cur_content, 'Componet': key}
                send_log_db(MODULE_SYSTEM, msg)

                ''' send log to management platform'''
                webDpi_obj = get_webdpi_obj()
                dpiip, pro_info, ver_info, sn_info, mw_ip = webDpi_obj.getdpiinfo()
                log_msg = "%s%s%d|%s" % (sn_info, self.log_head, IFSTATUS_TYPE, cur_content.encode('utf-8'))
                syslog.syslog(syslog.LOG_NOTICE, log_msg)
                if get_log_switch():
                    if 'down' in cur_content1:
                        send_eth_down_to_icsp(cur_content1)
                    else:
                        send_eth_up_to_icsp(cur_content1)

    def deal_bypass_status(self):
        if RUN_MODE == "ids":
            return
        level_list = [LOG_INFO, LOG_ALERT]
        bypass_info = getBypassStat()
        bp0_list = [u'bp0关', u'bp0开']
        if bp0_list[bypass_info["bp0"]] != self.bypass_content['bp0']:
            self.bypass_content['bp0'] = bp0_list[bypass_info["bp0"]]
            level = level_list[bypass_info['bp0']]
            msg = {'Type': BYPASSSTATUS_TYPE, 'LogLevel': level, 'Content': bp0_list[bypass_info["bp0"]], 'Componet': 'bp0'}
            send_log_db(MODULE_SYSTEM, msg)

        bp1_list = [u'bp1关', u'bp1开']
        if bp1_list[bypass_info["bp1"]] != self.bypass_content['bp1']:
            self.bypass_content['bp1'] = bp1_list[bypass_info["bp1"]]
            level = level_list[bypass_info['bp1']]
            msg = {'Type': BYPASSSTATUS_TYPE, 'LogLevel': level, 'Content': bp1_list[bypass_info["bp1"]], 'Componet': 'bp1'}
            send_log_db(MODULE_SYSTEM, msg)
