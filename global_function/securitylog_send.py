#!/usr/bin/python
# -*- coding:UTF-8 -*-
import psutil
from log_oper import *
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


logger = logging.getLogger('flask_mw_log')

PROTO_NAME_DICT = {"6": "tcp", "17": "udp", "1": "icmp"}


def deal_percent(per):
    if per == 0:
        return 1
    elif per > 100:
        return 100
    elif per > 20:
        return per*per/100
    else:
        return per


def trans_ip_format(ip):
    tmp_ip = ip.encode('hex')
    ip_start = tmp_ip[-8:]
    ip_res = ""
    ip_res += str(int(ip_start[0:2], 16))
    ip_res += '.'
    ip_res += str(int(ip_start[2:4], 16))
    ip_res += '.'
    ip_res += str(int(ip_start[4:6], 16))
    ip_res += '.'
    ip_res += str(int(ip_start[6:], 16))
    return ip_res


class SecuritylogSend(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            try:
                if get_log_switch():
                    self.send_cpu_usage()
                    self.send_mem_usage()
            except:
                logger.error(traceback.format_exc())
            time.sleep(30)

    def send_cpu_usage(self):
        cpu_usage = int(psutil.cpu_percent() + 0.5)
        cpu_state = deal_percent(cpu_usage)
        send_cpu_usage_to_icsp(str(cpu_state) + '%')

    def send_mem_usage(self):
        mem_usage = int(psutil.virtual_memory().percent + 0.5)
        mem_state = deal_percent(mem_usage)
        send_mem_usage_to_icsp(str(mem_state) + '%')
