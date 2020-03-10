#!/usr/bin/python
# -*- coding:utf-8 -*-
import datetime
import psutil
import traceback
from flask import render_template, request
from flask import jsonify
from flask import Blueprint
from flask import current_app
from global_function.global_var import *
# flask-login
from flask_login.utils import login_required
import logging

index_page = Blueprint('index_page', __name__, template_folder='templates')

g_mem_size, g_disk_size = init_device_size_info()


@index_page.route('/getSysTime')
@login_required
def mw_getSysTime():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    user_name = request.args.get("loginuser")
    time_stamp = int(time.time() * 1000)
    try:
        sql_str = "update users set last_update='{}' where name='{}'".format(time_stamp, user_name)
        current_app.logger.info(sql_str)
        db_proxy.write_db(sql_str)
    except:
        current_app.logger.error(traceback.format_exc())
    nowtime = datetime.datetime.now()
    nowTimeNyr = nowtime.strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({'systime': str(nowTimeNyr)})


@index_page.route('/indexRefreshCount')
@login_required
def mw_index_refreshcount():
    sys_info = getCpuMemDiskInfo()
    dictEventNum = getEventNum()
    dictAllPort = getAllPortInfo()
    top_info = get_index_topinfo()
    # dictBypassStat = getBypassStat() for KEC_U2000

    # merge all the dicts
    sys_info.update(dictEventNum)
    sys_info.update(dictAllPort)
    sys_info.update(top_info)
    # sys_info.update(dictBypassStat)
    if g_dpi_plat_type == DEV_PLT_MIPS:
        led_key = ('runState', 'alarmState', 'findState', 'powerState')
        led_val = get_led_status()
        sys_info.update(zip(led_key, led_val))
    current_app.logger.info("get systemInfo success!")
    return jsonify(sys_info=sys_info)


def get_index_topinfo():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    top_info = {}
    sql_str = "select count(if(is_live=1,is_live,NULL)) as val1,count(if(is_live=0,is_live,NULL)) as val2 from topdevice"
    _, rows = db_proxy.read_db(sql_str)
    tmp_top = rows[0][0]
    tmp_untop = rows[0][1]
    # tmp_all = tmp_top + tmp_untop
    top_info['top_num'] = tmp_top + tmp_untop
    top_info['live_per'] = tmp_top
    top_info['unlive_per'] = tmp_untop
    return top_info


def deal_percent(per):
    if per == 0:
        return 1
    elif per > 100:
        return 100
    elif per > 70:
        return per * per / 100
    else:
        return per


def getCpuMemDiskInfo():
    sys_info = {}
    try:
        partitions = psutil.disk_partitions()
        part_sum = 0
        part_used = 0

        cpu_usage = int(psutil.cpu_percent() + 0.5)

        for part in partitions:
            part_sum += psutil.disk_usage(part.mountpoint).total
            part_used += psutil.disk_usage(part.mountpoint).used
        part_usage = int(((float(part_used)) / part_sum) * 100 + 0.5)
        if part_usage == 0:
            part_usage = 1
        mem_usage = int(psutil.virtual_memory().percent + 0.5)

        sys_info['diskState'] = part_usage
        sys_info['memoryState'] = deal_percent(mem_usage)
        sys_info['cpuState'] = deal_percent(cpu_usage)
        sys_info['memorySize'] = g_mem_size
        sys_info['diskSize'] = g_disk_size
        current_app.logger.info("get cpu memDiskInfo success!")
    except:
        current_app.logger.error("get cpu memDiskInfo error!")
        current_app.logger.error(traceback.format_exc())
    return sys_info


def getEventNum():
    db_proxy = DbProxy()
    config_db_proxy = DbProxy(CONFIG_DB_NAME)
    sys_info = {}
    allNum = 0
    readNum = 0
    todaySafeNum = 0
    try:
        # get incidents counts
        result, rows = db_proxy.read_db("select sum(count),sum(incidentstat.read) from incidentstat")
        if result == 0 and rows[0][0]:
            allNum = int(rows[0][0])
            readNum = int(rows[0][1])
        sys_info['noReadNum'] = allNum - readNum

        today = datetime.date.today()
        todayTime = str(today) + ' 00:00:00'
        tomorrowTime = str(today) + ' 23:59:59'
        tup_todayTime = time.strptime(todayTime, "%Y-%m-%d %H:%M:%S")
        tmp_todayTime = int(time.mktime(tup_todayTime))
        tup_tomorrowTime = time.strptime(tomorrowTime, "%Y-%m-%d %H:%M:%S")
        tmp_tomorrowTime = int(time.mktime(tup_tomorrowTime))
        sql_today_incidents_cmd = "SELECT sum(count) from incidentstat where timestamp>=" + str(
            tmp_todayTime) + " and timestamp<=" + str(tmp_tomorrowTime)
        result, rows = db_proxy.read_db(sql_today_incidents_cmd)
        if result == 0 and rows[0][0]:
            todaySafeNum = rows[0][0]
        sys_info['todayEventNum'] = todaySafeNum

        sys_info['historyEventNum'] = allNum - int(todaySafeNum)

        # get rule num
        result, self_white = config_db_proxy.read_db("SELECT count(*) from rules where deleted=1")
        result, rows = config_db_proxy.read_db("SELECT count(*) from customrules where deleted=1")
        sys_info['whiteNum'] = rows[0][0] + self_white[0][0]
        result, rows = config_db_proxy.read_db("SELECT count(*) from signatures where deleted=1")
        sys_info['blackNum'] = rows[0][0]
        result, rows = config_db_proxy.read_db("SELECT count(*) from ipmaclist where enabled=1")
        sysNoReadNum = rows[0][0]

        sys_info['ipmacNum'] = sysNoReadNum
        sys_info['rulesNum'] = sys_info['whiteNum'] + sys_info['blackNum'] + sys_info['ipmacNum']
        current_app.logger.info("get eventNum success!")
    except:
        current_app.logger.error("get eventNum error!")
        current_app.logger.error(traceback.format_exc())
    return sys_info

def getAllPortInfo():
    sys_info = {}
    try:
        hwaddr, ip, mask, state, ip6, ip6prefix = GetOnePortInfo('ifconfig agl0')
        sys_info['agl0LinkState'] = state
        sys_info['agl0Info'] = "agl0;%s;%s;%s;%s;%s" % (ip, hwaddr, mask, ip6, ip6prefix)
        hwaddr, ip, mask, state, ip6, ip6prefix = GetOnePortInfo('ifconfig agl1')
        sys_info['extLinkState'] = state
        sys_info['extInfo'] = "ext;%s;%s;%s;%s;%s" % (ip, hwaddr, mask, ip6, ip6prefix)
        current_app.logger.info(g_hw_type)
        if g_hw_type == "0":
            sys_info["hw_type"] = "0"
            for port_info in PORT_MAP_DICT["IMAP"]:
                hwaddr, ip, mask, state, ip6, ip6prefix = GetOnePortInfo('ifconfig %s' % port_info[1])
                sys_info['%sLinkState' % port_info[0]] = state
                sys_info['%sInfo' % port_info[0]] = "%s;%s;%s;%s;%s;%s" % (port_info[0], ip, hwaddr, mask, ip6, ip6prefix)
        elif g_hw_type == "1":
            sys_info["hw_type"]="1"
            for port_info in PORT_MAP_DICT["IMAP02"]:
                hwaddr, ip, mask, state, ip6, ip6prefix = GetOnePortInfo('ifconfig %s' % port_info[1])
                sys_info['%sLinkState' % port_info[0]] = state
                sys_info['%sInfo' % port_info[0]] = "%s;%s;%s;%s;%s;%s" % (port_info[0], ip, hwaddr, mask, ip6, ip6prefix)
        # if g_dev_type in PORT_MAP_DICT:
        #     for port_info in PORT_MAP_DICT[g_dev_type]:
        #         hwaddr, ip, mask, state, ip6, ip6prefix = GetOnePortInfo('ifconfig %s' % port_info[1])
        #         sys_info['%sLinkState' % port_info[0]] = state
        #         sys_info['%sInfo' % port_info[0]] = "%s;%s;%s;%s;%s;%s" % (port_info[0], ip, hwaddr, mask, ip6, ip6prefix)
        current_app.logger.info("get allPortInfo success!")
    except:
        current_app.logger.error("get allPortInfo error!")
        current_app.logger.error(traceback.format_exc())
    return sys_info

def GetOnePortInfo(cmd):
    try:
        res = commands.getoutput(cmd)

        # HWaddr
        hwaddr_start = res.find('HWaddr')
        hwaddr_start = hwaddr_start + 7
        hwaddr_end = res.find('\n', hwaddr_start)
        hwaddr = res[hwaddr_start:hwaddr_end]

        # IP
        ip_start = res.find('inet addr:')
        if ip_start != -1:
            ip_end = res.find('Bcast')
            ip_start = ip_start + 10
            ip_end = ip_end - 2
            ip = res[ip_start:ip_end]
        else:
            ip = '0.0.0.0'
        ip6, prefix = getip6_prefix_from_interfaces()
        # addr_type = ""
        # if res.find('Scope:Site') != -1:
        #     addr_type = "Scope:Site"
        # elif res.find('Scope:Global') != -1:
        #     addr_type = "Scope:Global"
        # else:
        #     pass
        #
        # if addr_type == "":
        #     ip6 = ""
        #     prefix = ""
        # else:
        #     stop_ip6_link = res.find('Scope:Link') - 4
        #     stop_ip6 = res.find(addr_type) - 4
        #     if stop_ip6_link > stop_ip6:
        #         start_ip6 = res.find('inet6 addr:') + 11
        #     else:
        #         start_ip6 = res.find('inet6 addr:', stop_ip6_link) + 11
        #     ip6 = res[start_ip6:stop_ip6]
        #     prefix = res[start_ip6:stop_ip6+3].split('/')[1]

        # MASK
        mask_start = res.find('Mask')
        if mask_start != -1:
            mask_start = mask_start + 5
            mask_end = res.find('\n', mask_start)
            mask = res[mask_start:mask_end]
        else:
            mask = '0.0.0.0'

        # STATE
        if res.find('RUNNING') != -1:
            state = 1
        else:
            state = 0
        # current_app.logger.info("get OnePortInfo success!")
        return hwaddr, ip, mask, state, ip6, prefix
    except:
        # current_app.logger.error("GetOnePortInfo error!")
        current_app.logger.error(traceback.format_exc())
        return

def getip6_prefix_from_interfaces():
    try:
        interfaces_file_path = r'/app/etc/network/interfaces'
        file_handler = open(interfaces_file_path, "r")
        network_content = file_handler.read()
        file_handler.close()

        index_ip6addr = network_content.find('ipv6addr')
        if index_ip6addr == -1:
            return '', ''
        else:
            index_ip6addr_end = network_content.find('\n', index_ip6addr)
            index_ip6addr_start = index_ip6addr

            index_prefix_start = network_content.find('prefix')
            index_prefix_end = network_content.find('\n', index_prefix_start)
            return (network_content[index_ip6addr_start:index_ip6addr_end].strip().split(' ')[1],
                    network_content[index_prefix_start:index_prefix_end].strip().split(' ')[1])
    except Exception, e:
        raise e


def get_led_status():
    """
        alarm status:
        off              -led alarm off
        red_on               -led alarm red on
        green_on -led alarm green on
        red_blink -led alarm red flashing
        green_blink      -led alarm green flashing
    """
    try:
        # alarm status
        alarm_dict = {'off': 0, 'red on': 1, 'green on': 2, 'red blink': 3, 'green blink': 4}
        res = os.popen("tdhxtester --led_alarm read")
        result = res.readline()
        # result: res led alarm status :off
        alarm_key = result.split(':')[1][0:-1]
        alarm_val = alarm_dict[alarm_key]

        res = os.popen("tdhxtester --led_run read")
        result = res.readline()
        # result: res led run status :off
        run_key = result.split(':')[1][0:-1]
        run_val = alarm_dict[run_key]

        # power status  1-red on, 2-green on, same to alarm dict
        power_val = 1
        power_dict = {'0x01': 1, '0x02': 1, '0x03': 2}
        res = os.popen('oct-linux-memory -w 1 0x1bb00000')
        result = res.readline()
        # result: Address 0x000000001bb00000 = 0x69
        cpld_ver = result.split('=')[1][1:-1]
        if cpld_ver == '0x69':
            res = os.popen('oct-linux-memory -w 1 0x1bb00002')
            result = res.readline()
            # result: Address 0x000000001bb00002 = 0x01
            power_key = result.split('=')[1][1:-1]
            power_val = power_dict[power_key]

        # bypass status, 0-disable gray, 2-enable green, same to alarm dict
        bypass_dict = {'disable': 0, 'enable': 2}
        bypass_val = 0
        res = os.popen("tdhxtester --bypass0 read")
        result = res.readline()
        # result bypass0 status :disable
        bypass_key0 = result.split(':')[1][0:-1]
        bypass_val0 = 0
        if bypass_key0.find('enable') >= 0:
            bypass_val0 = 2
        if bypass_val0 == 0:
            res = os.popen("tdhxtester --bypass1 read")
            result = res.readline()
            # result bypass1 status :disable
            bypass_key1 = result.split(':')[1][0:-1]
            # bypass_val1 = bypass_dict[bypass_key1]
            bypass_val1 = 0
            if bypass_key1.find('enable') >= 0:
                bypass_val1 = 2
            bypass_val = bypass_val1
        else:
            bypass_val = 2
        current_app.logger.info("get_led_status success!")
        return alarm_val, power_val, bypass_val, run_val
    except:
        current_app.logger.error("get_led_status error!")
        current_app.logger.error(traceback.format_exc())
        return
