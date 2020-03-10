#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Report Generation FLASK module
author:HanFei
'''
import ipaddress
import os
import sys
import datetime
import time
from logging.handlers import RotatingFileHandler
from logging.handlers import SysLogHandler
from global_function.log_oper import send_log_db, MODULE_OPERATION

path = os.path.split(os.path.realpath(__file__))[0]
dirs = os.path.dirname(path)
sys.path.append(dirs)
sys.path.append("/app/local/share/new_self_manage/global_function/report_build")
from flask import request
from flask import jsonify
from flask import send_from_directory
from flask import Blueprint
from flask import render_template
from global_function.global_var import *
from report import *
# flask-login
from flask_login.utils import login_required
from flask import current_app
import base64
import zipfile

RISK_LOW = 0
RISK_MID = 1
RISK_HIG = 2
RISK_UNKNOW = 3

SIG_WHITELIST = 1
SIG_BLACKLIST = 2
SIG_IPMAC = 3
SIG_TRAFFIC = 4
SIG_MACFILTER = 5
SIG_ABNORMAL_PACKET= 7

# logger = logging.getLogger('flask_engine_log')
reportgen_page = Blueprint('reportgen_page', __name__, template_folder='templates')


def get_time_section_by_pre_day():
    '''
    get daily report time section
    '''
    now_ticks = int(time.time())
    now = time.localtime(now_ticks)
    year = now.tm_year
    month = now.tm_mon
    day = now.tm_mday

    day1_str = "%4d-%02d-%02d 00:00:00" % (year, month, day)
    day1 = datetime.datetime.strptime(day1_str, '%Y-%m-%d %H:%M:%S')

    delta = datetime.timedelta(days=1, seconds=0)
    day2 = day1 - delta

    day2_str = day2.strftime('%Y-%m-%d %H:%M:%S')
    return day2_str, day1_str


def get_time_section_by_pre_week():
    '''
    get weekly report time section
    '''
    now_ticks = int(time.time())
    now = time.localtime(now_ticks)
    year = now.tm_year
    month = now.tm_mon
    day = now.tm_mday
    weekday = now.tm_wday

    delta_day = 7 - weekday

    day1_str = "%4d-%02d-%02d 00:00:00" % (year, month, day)
    day1 = datetime.datetime.strptime(day1_str, '%Y-%m-%d %H:%M:%S')

    delta = datetime.timedelta(days=delta_day, seconds=0)
    day2 = day1 - delta
    day2_str = day2.strftime('%Y-%m-%d %H:%M:%S')
    return day2_str, day1_str


def get_time_section_by_pre_month():
    '''
    get monthly report time section
    '''
    now_ticks = int(time.time())
    now = time.localtime(now_ticks)
    year = now.tm_year
    month = now.tm_mon

    if month > 1:
        dest_month = month - 1
        dest_year = year
    else:
        dest_month = 12
        dest_year = year - 1

    day2_str = "%4d-%02d-01 00:00:00" % (dest_year, dest_month)
    day1_str = "%4d-%02d-01 00:00:00" % (year, month)
    return day2_str, day1_str


def get_start_end_time(freq_type):
    '''
    get report time section according freq type
    '''
    if freq_type == 1:
        start_time, end_time = get_time_section_by_pre_day()
    elif freq_type == 2:
        start_time, end_time = get_time_section_by_pre_week()
    else:
        start_time, end_time = get_time_section_by_pre_month()
    return start_time, end_time


def get_statics_time_section_by_day(start_date_str, end_date_str):
    '''
    get weekly or weekly report statics time section
    '''
    zero_date = start_date_str.split(" ")[0] + " 00:00:00"
    day1 = datetime.datetime.strptime(zero_date, '%Y-%m-%d %H:%M:%S')

    delta_1 = datetime.timedelta(hours=24)

    date = day1
    date_list = []
    date_str = []

    while 1:
        start_str = date.strftime('%Y-%m-%d %H:%M:%S')
        date_str.append(start_str.split(" ")[0])
        date = date + delta_1
        end_str = date.strftime('%Y-%m-%d %H:%M:%S')
        date_list.append([start_str, end_str])
        if end_str == end_date_str:
            break
    return date_list, date_str


def get_statics_time_section_by_hour(start_date_str, end_date_str):
    '''
    get daily report statics time section
    '''
    zero_date = start_date_str.split(" ")[0] + " 00:00:00"
    day1 = datetime.datetime.strptime(zero_date, '%Y-%m-%d %H:%M:%S')

    delta_1 = datetime.timedelta(hours=1, minutes=0, seconds=0)

    date = day1
    date_list = []

    while 1:
        start_str = date.strftime('%Y-%m-%d %H:%M:%S')
        date = date + delta_1
        end_str = date.strftime('%Y-%m-%d %H:%M:%S')
        date_list.append([start_str, end_str])
        if end_str == end_date_str:
            break

    return date_list


def get_next_month(year, month):
    if month == 12:
        dest_month = 1
        dest_year = year + 1
    else:
        dest_month = month + 1
        dest_year = year
    return dest_year, dest_month


def get_pre_month(year, month):
    if month == 1:
        dest_month = 12
        dest_year = year - 1
    else:
        dest_month = month - 1
        dest_year = year
    return dest_year, dest_month


def get_statics_time_section_by_month_manual(start_date_str, end_date_str):
    start_ticks = int(time.mktime(time.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')))
    start_time = time.localtime(start_ticks)
    start_year = start_time.tm_year
    start_month = start_time.tm_mon
    start_day = start_time.tm_mday
    static_start_year = start_year
    static_start_month = start_month

    end_ticks = int(time.mktime(time.strptime(end_date_str, '%Y-%m-%d %H:%M:%S')))
    end_time = time.localtime(end_ticks)
    end_year = end_time.tm_year
    end_month = end_time.tm_mon
    end_day = end_time.tm_mday
    if end_day > 1:
        static_end_year, static_end_month = get_next_month(end_year, end_month)
    else:
        static_end_year = end_year
        static_end_month = end_month

    tmp_year = static_start_year
    tmp_month = static_start_month

    date_list = []
    time_axis = []

    # 构造date_list，用来进行数据库统计
    for i in range(0, 13):
        next_time_year, next_time_month = get_next_month(tmp_year, tmp_month)
        start_time_str = "%04d-%02d-01 00:00:00" % (tmp_year, tmp_month)
        end_time_str = "%04d-%02d-01 00:00:00" % (next_time_year, next_time_month)
        date_list.append([start_time_str, end_time_str])
        if next_time_year == static_end_year and next_time_month == static_end_month:
            break
        else:
            tmp_year = next_time_year
            tmp_month = next_time_month

    date_list[0][0] = start_date_str
    date_list[-1][1] = end_date_str
    if 0:
        delta_1 = datetime.timedelta(hours=24, minutes=0, seconds=0)
        last_date = datetime.datetime.strptime("%04d-%02d-%02d 00:00:00" % (end_year, end_month, end_day),
                                               '%Y-%m-%d %H:%M:%S')
        print
        last_date
        last_date = last_date + delta_1
        print
        last_date
        date_list[-1][1] = last_date.strftime('%Y-%m-%d %H:%M:%S')

    # 构造time_axis，用来时间轴展示
    for i in range(0, len(date_list)):
        tmp = date_list[i][0].split(" ")[0].split("-")
        time_axis.append("%04d-%02d" % (int(tmp[0]), int(tmp[1])))

    return date_list, time_axis


def get_statics_time_section_by_hour_manual(start_date_str, end_date_str):
    '''
    get daily report statics time section
    '''

    delta_1 = datetime.timedelta(hours=1, minutes=0, seconds=0)
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
    zero_start_hour_str = "%04d-%02d-%02d %02d:00:00" % (
    start_date.year, start_date.month, start_date.day, start_date.hour)
    zero_start_hour_date = datetime.datetime.strptime(zero_start_hour_str, '%Y-%m-%d %H:%M:%S')
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S')
    zero_end_hour_str = "%04d-%02d-%02d %02d:00:00" % (end_date.year, end_date.month, end_date.day, end_date.hour)
    zero_end_hour_date = datetime.datetime.strptime(zero_end_hour_str, '%Y-%m-%d %H:%M:%S')
    if end_date_str.split(" ")[1].split(":", 1)[1] == "00:00":
        new_end_date_str = end_date_str
    else:
        new_end_date_str = (zero_end_hour_date + delta_1).strftime('%Y-%m-%d %H:%M:%S')
    date_list = []
    time_axis = []
    date = zero_start_hour_date

    while 1:
        start_str = date.strftime('%Y-%m-%d %H:%M:%S')
        date = date + delta_1
        end_str = date.strftime('%Y-%m-%d %H:%M:%S')
        date_list.append([start_str, end_str])
        hour = start_str.split(" ")[1].split(":")[0]
        time_axis.append("%02d:00" % int(hour))
        if end_str == new_end_date_str:
            break
    date_list[0][0] = start_date_str
    date_list[-1][-1] = end_date_str
    return date_list, time_axis


def get_statics_time_section_by_day_manual(start_date_str, end_date_str):
    '''
    get weekly or weekly report statics time section
    '''
    zero_start_date_str = start_date_str.split(" ")[0] + " 00:00:00"
    zero_end_date_str = end_date_str.split(" ")[0] + " 00:00:00"
    date = datetime.datetime.strptime(zero_start_date_str, '%Y-%m-%d %H:%M:%S')

    delta_1_day = datetime.timedelta(hours=24)
    zero_end_date = datetime.datetime.strptime(zero_end_date_str, '%Y-%m-%d %H:%M:%S')
    print
    "end_date_str.split = %s" % end_date_str.split(" ")[1]
    if (end_date_str.split(" ")[1] != "00:00:00"):
        new_end_date_str = (zero_end_date + delta_1_day).strftime('%Y-%m-%d %H:%M:%S')
    else:
        new_end_date_str = end_date_str
    print
    "new_end_date_str = ", new_end_date_str

    date_list = []
    date_str = []

    while 1:
        start_str = date.strftime('%Y-%m-%d %H:%M:%S')
        date_str.append(start_str.split(" ")[0])
        date = date + delta_1_day
        end_str = date.strftime('%Y-%m-%d %H:%M:%S')
        date_list.append([start_str, end_str])
        if end_str == new_end_date_str:
            break
    date_list[0][0] = start_date_str
    date_list[-1][1] = end_date_str
    return date_list, date_str


def get_freq_type(start_time, end_time):
    month_delta = datetime.timedelta(hours=24 * 31, minutes=0, seconds=0)
    day_delta = datetime.timedelta(hours=24 * 1, minutes=0, seconds=0)
    start_date = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end_date = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    if end_date > start_date + month_delta:
        freq_type = MONTH_MANUAL_TYPE
    elif end_date > start_date + day_delta:
        freq_type = DAY_MANUAL_TYPE
    else:
        freq_type = HOUR_MANUAL_TYPE

    return freq_type


def check_time_for_manual_report(start_time, end_time):
    year_delta = datetime.timedelta(hours=24 * 365, minutes=0, seconds=0)
    start_date = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end_date = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if end_date > start_date + year_delta:
        return 1
    total_start_month = start_date.year * 12 + start_date.month
    total_end_month = end_date.year * 12 + end_date.month
    if total_end_month - total_start_month >= 0 and total_end_month - total_start_month <= 12:
        return 0
    else:
        return 1


ALARM_TYPE_DICT = {1:"警告".decode("UTF-8"), 2:"阻断".decode("UTF-8"), 3:"通知".decode("UTF-8")}
ALARM_LEVEL_DICT = {1:"低危".decode("UTF-8"), 2:"中危".decode("UTF-8"), 3:"高危".decode("UTF-8")}
ALARM_SRC_DICT = {"1":"白名单".decode("UTF-8"), "2":"黑名单".decode("UTF-8"), "3":"IP/MAC".decode("UTF-8"), "4":"流量告警".decode("UTF-8"), "5":"MAC过滤".decode("UTF-8"), "6":"资产告警".decode("UTF-8"), "7":U"不合规报文告警".encode("utf-8-sig")}

HOUR_DATE_LIST = ["00:00", "01:00", "02:00", "03:00", "04:00",
                  "05:00", "06:00", "07:00", "08:00", "09:00",
                  "10:00", "11:00", "12:00", "13:00", "14:00",
                  "15:00", "16:00", "17:00", "18:00", "19:00",
                  "20:00", "21:00", "22:00", "23:00"]

REPORT_PATH = "/data/report"
REPORT_GEN_ALARM_PATH = "/data/report/alarm"
REPORT_GEN_PROTO_AUDIT_PATH = "/data/report/protocal"
REPORT_GEN_LOG_PATH = "/data/report/log"
REPORT_GEN_ASSETS_PATH = "/data/report/assets"

def report_gen_init():
    '''
    report gen init func
    '''
    os.system("mkdir -p %s" % REPORT_PATH)
    os.system("mkdir -p %s" % REPORT_GEN_ALARM_PATH)
    os.system("mkdir -p %s" % REPORT_GEN_PROTO_AUDIT_PATH)
    os.system("mkdir -p %s" % REPORT_GEN_LOG_PATH)
    os.system("mkdir -p %s" % REPORT_GEN_ASSETS_PATH)
    db_proxy = DbProxy(CONFIG_DB_NAME)

    sql_str = "select * from nsm_rptalarmmode"
    # sql_res = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
    _, sql_res = db_proxy.read_db(sql_str)
    if sql_res is not None and sql_res != []:
        freq = sql_res[0][0]

        os.system("sed -ir '/.*rptalarm_proc.pyc.*/d' %s" % CROND_PATH)
        if freq == 1:
            os.system("echo \"0 0 * * * python %s/rptalarm_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        elif freq == 2:
            os.system("echo \"0 0 * * 1  python %s/rptalarm_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        elif freq == 3:
            os.system("echo \"0 0 1 * *  python %s/rptalarm_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        else:
            pass

    sql_str = "select * from nsm_rptprotomode"
    # sql_res = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
    _, sql_res = db_proxy.read_db(sql_str)
    if sql_res is not None and sql_res != []:
        freq = sql_res[0][0]

        os.system("sed -ir '/.*rptproto_proc.pyc.*/d' %s" % CROND_PATH)
        if freq == 1:
            os.system("echo \"5 0 * * * python %s/rptproto_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        elif freq == 2:
            os.system("echo \"5 0 * * 1  python %s/rptproto_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        elif freq == 3:
            os.system("echo \"5 0 1 * *  python %s/rptproto_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        else:
            pass

    sql_str = "select * from nsm_rptlogmode"
    # sql_res = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
    _, sql_res = db_proxy.read_db(sql_str)
    if sql_res is not None and sql_res != []:
        freq = sql_res[0][0]
        os.system("sed -ir '/.*rptlog_proc.pyc.*/d' %s" % CROND_PATH)
        if freq == 1:
            os.system("echo \"10 0 * * * python %s/rptlog_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        elif freq == 2:
            os.system("echo \"10 0 * * 1  python %s/rptlog_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        elif freq == 3:
            os.system("echo \"10 0 1 * *  python %s/rptlog_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        else:
            pass

    sql_str = "select * from nsm_rptassetsmode"
    _, sql_res = db_proxy.read_db(sql_str)
    if sql_res is not None and sql_res != []:
        freq = sql_res[0][0]
        os.system("sed -ir '/.*rptassets_proc.pyc.*/d' %s" % CROND_PATH)
        if freq == 1:
            os.system("echo \"15 0 * * * python %s/rptassets_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        elif freq == 2:
            os.system("echo \"15 0 * * 1  python %s/rptassets_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        elif freq == 3:
            os.system("echo \"15 0 1 * *  python %s/rptassets_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        else:
            pass
    os.system("crontab -c %s %s" % (CROND_CONF, CROND_PATH))
    return


@reportgen_page.route('/reportGenAlarmTest')
@login_required
def report_alarm_test():
    '''
    test route for alarm report gen
    '''
    freq = request.args.get('freq', 1, type=int)
    alarm_origin_report_gen_handle(freq)
    return jsonify({'status': 1})


DAY_AUTO_TYPE = 1
WEEK_AUTO_TYPE = 2
MONTH_AUTO_TYPE = 3
HOUR_MANUAL_TYPE = 4
DAY_MANUAL_TYPE = 5
MONTH_MANUAL_TYPE = 6


@reportgen_page.route('/reportGenAlarmManual', methods=['GET', 'POST'])
@login_required
def report_alarm_manual():
    '''
    test route for alarm report gen
    '''
    msg = {}
    userip = get_oper_ip_info(request)
    if request.method == "GET":
        start_time = request.args.get('starttime', '')
        end_time = request.args.get('endtime', '')
        srcaddr = request.args.get('srcaddr', '')
        dstaddr = request.args.get('dstaddr', '')
        proto = request.args.get('proto', '')
        signatureName = request.args.get('signatureName', '')
        srcDevName = request.args.get('sourceName', '')
        dstDevName = request.args.get('destinationName', '')
        riskLevel = request.args.get('riskLevel', '')
        loginuser = request.args.get('loginuser', '')
    elif request.method == "POST":
        post_data = request.get_json()
        start_time = post_data.get('starttime', '')
        end_time = post_data.get('endtime', '')
        srcaddr = post_data.get('srcaddr', '')
        dstaddr = post_data.get('dstaddr', '')
        proto = post_data.get('proto', '')
        signatureName = post_data.get('signatureName', '')
        srcDevName = post_data.get('sourceName', '')
        dstDevName = post_data.get('destinationName', '')
        riskLevel = post_data.get('riskLevel', '')
        loginuser = post_data.get('loginuser', '')
    else:
        return jsonify({'status': 0})
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u'手动生成事件报告'
    msg['Result'] = '1'

    if start_time == "" or end_time == "":
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 0})

    freq_type = get_freq_type(start_time, end_time)

    option_str = ""
    if len(srcaddr) > 0:
        option_str += " and dpi like " + "\"%" + srcaddr + "%\""
    if len(dstaddr) > 0:
        option_str += " and dpiName like " + "\"%" + dstaddr + "%\""
    if len(proto) > 0:
        if proto == 'https':
            proto = 'tls'
        option_str += " and appLayerProtocol like " + "\"%" + proto + "%\""

    if len(signatureName) > 0 and signatureName != "0":
        option_str += " and signatureName=" + "\"" + signatureName + "\""
    if len(riskLevel) > 0:
        if int(riskLevel) == RISK_LOW:
            option_str += " and signatureName in ('%s')" % (SIG_TRAFFIC)
        elif int(riskLevel) == RISK_MID:
            option_str += " and signatureName in ('%s','%s','%s', '%s')"%(SIG_WHITELIST,SIG_IPMAC,SIG_MACFILTER, SIG_ABNORMAL_PACKET)
        elif int(riskLevel) == RISK_HIG:
            option_str += " and signatureName in ('%s')" % (SIG_BLACKLIST)
    if len(srcDevName) > 0 and srcDevName != "0":
        tmp_str = ""
        first_flag = 1
        src_ipmac_list = get_ipmac_list_by_devname(srcDevName.encode("UTF-8"))
        for elem in src_ipmac_list:
            if first_flag == 0:
                tmp_str += " or "
            first_flag = 0

            if elem[0] == "any":
                src_ip_str = " sourceIp like \"" + "%%" + "\""
            elif elem[0] == "":
                src_ip_str = " sourceIp = '' "
            else:
                src_ip_str = " sourceIp = \"" + elem[0] + "\""

            if elem[1] == "any":
                src_mac_str = " sourceMac like \"" + "%%" + "\""
            elif elem[1] == "":
                src_mac_str = " sourceMac = '' "
            else:
                src_mac_str = " sourceMac = \"" + elem[1].replace(":", "") + "\""

            tmp_str += "(" + src_ip_str + " and " + src_mac_str + ")"

        if tmp_str != "":
            option_str += " and (" + tmp_str + ")"
    if len(dstDevName) > 0 and dstDevName != "0":
        tmp_str = ""
        first_flag = 1
        dst_ipmac_list = get_ipmac_list_by_devname(dstDevName.encode("UTF-8"))
        for elem in dst_ipmac_list:
            if first_flag == 0:
                tmp_str += " or "
            first_flag = 0

            if elem[0] == "any":
                dst_ip_str = " destinationIp like \"" + "%%" + "\""
            elif elem[0] == "":
                dst_ip_str = " destinationIp = '' "
            else:
                dst_ip_str = " destinationIp = \"" + elem[0] + "\""

            if elem[1] == "any":
                dst_mac_str = " destinationMac like \"" + "%%" + "\""
            elif elem[1] == "":
                dst_mac_str = " destinationMac = '' "
            else:
                dst_mac_str = " destinationMac = \"" + elem[1].replace(":", "") + "\""
            tmp_str += "(" + dst_ip_str + " and " + dst_mac_str + ")"
        if tmp_str != "":
            option_str += " and (" + tmp_str + ")"

    if 1 == check_time_for_manual_report(start_time, end_time):
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 0})

    paragram_dict = {"input_param": {"srcaddr": srcaddr, "dstaddr": dstaddr, "proto": proto,
                                     "start_time": start_time, "end_time": end_time, "srcname": srcDevName,
                                     "dstname": dstDevName, "signaturename": signatureName, "risklevel": riskLevel},
                     "option_str": option_str}
    try:
        res = alarm_origin_report_gen_handle(freq_type, **paragram_dict)
        if res == 1:
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0})
    except:
        send_log_db(MODULE_OPERATION, msg)
        current_app.logger.error(traceback.format_exc())
        return jsonify({'status': 0})
    msg["Result"] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


def set_up_logger():
    output_file = '/data/log/flask_engine.log'
    logger = logging.getLogger('flask_engine_log')
    logger.setLevel(logging.INFO)
    if not logger.handlers:
    # create a rolling file handler
        try:
            handler = RotatingFileHandler(output_file, mode='a',
                                          maxBytes=1024 * 1024 * 10, backupCount=10)
        except:
            handler = SysLogHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(
            logging.Formatter("[%(asctime)s -%(levelname)5s- %(filename)20s:%(lineno)3s] %(message)s", "%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
    return logger


MAX_ALARM_REPORT_ITEM_NUM = 50000


def alarm_origin_report_gen_handle(freq_type, **kwargs):
    '''
    alarm report gen handle
    '''
    logger = set_up_logger()
    if not kwargs:
        kwargs["option_str"] = ""
        kwargs["input_param"] = {}
    try:
        if kwargs["input_param"]["start_time"] == "" or kwargs["input_param"]["end_time"] == "":
            start_time, end_time = get_start_end_time(freq_type)
        else:
            start_time = kwargs["input_param"]["start_time"]
            end_time = kwargs["input_param"]["end_time"]
    except:
        start_time, end_time = get_start_end_time(freq_type)

    if not kwargs["input_param"]:
        kwargs["input_param"]["start_time"] = start_time
        kwargs["input_param"]["end_time"] = end_time

    start_timestamp = int(time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S')))
    end_timestamp = int(time.mktime(time.strptime(end_time, '%Y-%m-%d %H:%M:%S')))

    # 获取总条数
    sql_str = "select count(*) from incidents where timestamp > %d and timestamp <= %d " \
              % (start_timestamp, end_timestamp)
    db_proxy = DbProxy()
    config_db_proxy = DbProxy(CONFIG_DB_NAME)
    res, sql_res = db_proxy.read_db(sql_str + kwargs["option_str"])
    if res == 0:
        total_num = sql_res[0][0]
    else:
        total_num = 0
        # return 1

    # 获取源地址排行top5
    sql_str = "select dpi,count(*) from incidents where timestamp > %d and timestamp <= %d " \
              % (start_timestamp, end_timestamp)
    db_proxy = DbProxy()
    sql_str = sql_str + kwargs["option_str"] + "group by dpi order by count(*) desc limit 5"
    logger.info(sql_str)
    res, sql_res = db_proxy.read_db(sql_str)
    if res == 0:
        kwargs["srcaddr_order"] = sql_res
    else:
        kwargs["srcaddr_order"] = ()
        # return 1

    # 获取目的地址排名前五的数据
    sql_str = "select dpiName,count(*) from incidents where timestamp > %d and timestamp <= %d and dpiName <> 'NULL' and dpiName <> '' " \
              % (start_timestamp, end_timestamp)
    db_proxy = DbProxy()
    sql_str = sql_str + kwargs["option_str"] + "group by dpiName order by count(*) desc limit 5"
    logger.info(sql_str)
    res, sql_res = db_proxy.read_db(sql_str)
    if res == 0:
        kwargs["dstaddr_order"] = sql_res
    else:
        kwargs["dstaddr_order"] = ()
        # return 1

    # 应用层协议分布数据
    sql_str = "select appLayerProtocol,count(*) from incidents where timestamp > %d and timestamp <= %d " \
              % (start_timestamp, end_timestamp)
    db_proxy = DbProxy()
    sql_str = sql_str + kwargs["option_str"] + "group by appLayerProtocol order by count(*) desc"
    logger.info(sql_str)
    res, sql_res = db_proxy.read_db(sql_str)
    if res == 0:
        kwargs["event_proto_fig"] = sql_res
    else:
        kwargs["event_proto_fig"] = ()
        # return 1

    # 安全事件来源分布数据
    sql_str = "select signatureName,count(*) from incidents where timestamp > %d and timestamp <= %d " \
              % (start_timestamp, end_timestamp)
    db_proxy = DbProxy()
    sql_str = sql_str + kwargs["option_str"] + "group by signatureName order by count(*) desc"
    logger.info(sql_str)
    res, sql_res = db_proxy.read_db(sql_str)
    if res == 0:
        kwargs["event_src"] = sql_res
    else:
        kwargs["event_src"] = ()
        # return 1

    left_cnt = MAX_ALARM_REPORT_ITEM_NUM if total_num > MAX_ALARM_REPORT_ITEM_NUM else total_num

    # sql_str = "select dev_ip, dev_mac, dev_name from dev_name_conf"
    sql_str = "select ip, mac, name from topdevice"
    res, sql_res = config_db_proxy.read_db(sql_str)
    # if res != 0:
    # return 1

    dev_name_dict = {}
    for elem in sql_res:
        elem = list(elem)
        elem[1] = elem[1].replace(":", "")
        dev_name_dict[elem[0] + elem[1]] = elem[2]
    dev_name_dict[""] = "NA"

    sql_str = '''select max(id) from nsm_rptalarminfo '''
    # sql_str = '''select count(*) from nsm_rptalarminfo '''
    res, sql_res = config_db_proxy.read_db(sql_str)
    # if res != 0:
    # return 1
    if sql_res[0][0] is None:
        id_str = 1
    else:
        id_str = int(sql_res[0][0] + 1)

    ch_reprot_type = "安全事件_"

    if freq_type == DAY_AUTO_TYPE:
        en_rpt_type_str = "_Daily_Report"
        ch_rpt_type_str = "_每日报表"
        date_str = start_time.split(" ")[0]
    elif freq_type == WEEK_AUTO_TYPE:
        en_rpt_type_str = "_Weekly_Report"
        ch_rpt_type_str = "_每周报表"
        date_str = start_time.split(" ")[0]
    elif freq_type == MONTH_AUTO_TYPE:
        en_rpt_type_str = "_Monthly_Report"
        ch_rpt_type_str = "_每月报表"
        date_str = start_time.split(" ")[0]
    else:
        en_rpt_type_str = "_Manual_Report"
        ch_rpt_type_str = "_自定义报表"
        date_str = start_time.replace(" ", "_") + "_" + end_time.replace(" ", "_")

    if freq_type > MONTH_AUTO_TYPE:
        report_name = base64.b64encode((ch_reprot_type + date_str + ch_rpt_type_str + "_%d" % int(id_str)))
        file_name = ("Incident_" + date_str + en_rpt_type_str + "_%d" % int(id_str) + ".csv")
        statics_file_name = ("Incident_" + date_str + en_rpt_type_str + "_%d" % int(id_str))
    else:
        report_name = base64.b64encode(ch_reprot_type + date_str + ch_rpt_type_str)
        file_name = ("Incident_" + date_str + en_rpt_type_str + ".csv")
        statics_file_name = ("Incident_" + date_str + en_rpt_type_str)

    col_list = [U"时间戳", U"源设备名",  U"目的设备名", U"源IP", U"目的IP", U"源MAC", U"目的MAC", U"事件处理",
    U"协议名", U"规则名", U"协议细节", U"事件来源", U"安全等级"]
    incident_from = [U"白名单", U"黑名单", U"IP/MAC", U"流量告警", U"MAC过滤", U"资产告警", U"不合规报文告警"]
    incident_action = [U"通过", U"警告", U"阻断", U"通知"]
    item_num = [U"符合条件总条数", U"实际显示条数"]

    writer = UnicodeWriter(open(REPORT_GEN_ALARM_PATH + "/" + file_name, "wb"))
    writer.writerow(item_num)
    writer.writerow([str(total_num), str(left_cnt)])
    writer.writerow(col_list)

    # write alarm info into excle file
    index = 0
    while left_cnt > 0:
        if left_cnt >= 1000:
            get_cnt = 1000
        else:
            get_cnt = left_cnt
        sql_str = '''select sourceIp,destinationIp,action,appLayerProtocol,protocolDetail, \
                  matchedKey,timestamp,dpiIp,boxId,memo,signatureName,sourceMac,destinationMac from incidents \
                  where timestamp >= %d and timestamp < %d %s\
                  order by timestamp desc limit %d offset %d''' \
                  % (int(time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S'))),
                     int(time.mktime(time.strptime(end_time, '%Y-%m-%d %H:%M:%S'))), kwargs["option_str"], get_cnt,
                     index * 1000)

        res, sql_res = db_proxy.read_db(sql_str)
        if res != 0:
            left_cnt -= get_cnt
            index += 1
            continue

        for i in range(0, len(sql_res)):
            if int(sql_res[i][10]) == 2:
                incident_risk = 2
            elif int(sql_res[i][10]) == 4:
                incident_risk = 0
            else:
                incident_risk = 1
            tmp_res = get_traffic_event_row(sql_res[i], dev_name_dict, incident_from, incident_action, incident_risk)
            writer.writerow(tmp_res)
        left_cnt -= get_cnt
        index += 1

    date_list = []
    time_axis = []

    if freq_type == WEEK_AUTO_TYPE:
        date_list, time_axis = get_statics_time_section_by_day(start_time, end_time)
    if freq_type == MONTH_AUTO_TYPE:
        date_list, time_axis = get_statics_time_section_by_day(start_time, end_time)
    if freq_type == DAY_AUTO_TYPE:
        date_list = get_statics_time_section_by_hour(start_time, end_time)
        time_axis = HOUR_DATE_LIST
    if freq_type == HOUR_MANUAL_TYPE:
        date_list, time_axis = get_statics_time_section_by_hour_manual(start_time, end_time)
    if freq_type == DAY_MANUAL_TYPE:
        date_list, time_axis = get_statics_time_section_by_day_manual(start_time, end_time)
    if freq_type == MONTH_MANUAL_TYPE:
        date_list, time_axis = get_statics_time_section_by_month_manual(start_time, end_time)

    rows = []
    # logger.info(date_list)
    # logger.info(time_axis)
    for i in range(0, len(date_list)):
        sql_str = "select count(*) from incidents where timestamp > %d \
                   and timestamp <= %d and action = 3" \
                  % (int(time.mktime(time.strptime(date_list[i][0], '%Y-%m-%d %H:%M:%S'))),
                     int(time.mktime(time.strptime(date_list[i][1], '%Y-%m-%d %H:%M:%S'))))
        res, sql_res = db_proxy.read_db(sql_str + kwargs["option_str"])
        if res != 0:
            notice_num = 0
        else:
            notice_num = sql_res[0][0]
        sql_str = "select count(*) from incidents where timestamp > %d \
                   and timestamp <= %d" \
                  % (int(time.mktime(time.strptime(date_list[i][0], '%Y-%m-%d %H:%M:%S'))),
                     int(time.mktime(time.strptime(date_list[i][1], '%Y-%m-%d %H:%M:%S'))))
        res, sql_res = db_proxy.read_db(sql_str + kwargs["option_str"])
        if res != 0:
            alarm_num = 0
        else:
            alarm_num = sql_res[0][0]
        tmp_row = [time_axis[i], alarm_num, notice_num]
        rows.append(tmp_row)
    answer = {'status': 1, "rows": rows}
    # f = open("%s/%s" % (REPORT_GEN_ALARM_PATH, statics_file_name), "w")
    # f.write(str(answer))
    # f.close()
    # 安全事件趋势分布数据
    kwargs["event_time_data"] = answer["rows"]
    # 根据获取到的数据生成报告,并存储到对应的文件中
    # global REPORT_TYPE
    REPORT_TYPE = "event"
    try:
        # logger.info(kwargs)
        proto_report = ReportBuild(REPORT_TYPE, freq_type, **kwargs)
        proto_report.run()
    except:
        logger.error("event_report build error..")
        logger.error(traceback.format_exc())
        return 1

    report_name_ch = base64.b64decode(report_name)
    os.rename('/data/report/alarm/event_report.pdf', '/data/report/alarm/' + report_name_ch + ".pdf")
    os.rename('/data/report/alarm/' + file_name, '/data/report/alarm/' + report_name_ch + ".csv")

    # 将生成的报告相关信息存入数据库中
    ticks = int(time.time())
    gen_date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ticks))
    sql_str = '''insert into nsm_rptalarminfo (id, report_name, report_time, \
              report_start_time, report_stop_time, report_freq, report_raw_file, \
              report_statics_file) values(default, '%s','%s','%s','%s', %d,'%s','%s')''' \
              % (report_name, gen_date_str, start_time, end_time,
                 freq_type, file_name, statics_file_name)
    config_db_proxy.write_db(sql_str)
    return 0


def time_str_tz_proc(timestr):
    '''
    add T and Z for date string
    '''
    date_str = timestr.replace(" ", "T")
    date_str += "Z"
    return date_str


@reportgen_page.route('/reportGenAlarmSetmode', methods=['GET', 'POST'])
@login_required
def mw_report_gen_alarm_setmode():
    '''
    set alarm report gen mode
    '''
    if request.method == 'GET':
        freq = request.args.get('freq', 1, type=int)
    else:
        post_data = request.get_json()
        freq = int(post_data['freq'])
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select * from nsm_rptalarmmode"
    # sql_res = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
    _, sql_res = db_proxy.read_db(sql_str)
    if sql_res is None or sql_res == []:
        return jsonify({'status': 0})
    if sql_res[0][0] != freq:
        os.system("sed -ir '/.*rptalarm_proc.pyc.*/d' %s" % CROND_PATH)
        if freq == 1:
            os.system("echo \"0 0 * * * python %s/rptalarm_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        elif freq == 2:
            os.system("echo \"0 0 * * 1  python %s/rptalarm_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        elif freq == 3:
            os.system("echo \"0 0 1 * *  python %s/rptalarm_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        else:
            pass
        os.system("crontab -c %s %s" % (CROND_CONF, CROND_PATH))
        conf_save_flag_set()
        sql_str = "update nsm_rptalarmmode set flag=%d" % freq
        # new_send_cmd(TYPE_APP_SOCKET, sql_str, 2)
        db_proxy.write_db(sql_str)
    return jsonify({'status': 1})


@reportgen_page.route('/reportGenAlarmGetmode')
@login_required
def mw_report_gen_alarm_getmode():
    '''
    get alarm report gen mode
    '''
    sql_str = "select * from nsm_rptalarmmode"
    db_proxy = DbProxy(CONFIG_DB_NAME)
    # sql_res = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
    _, sql_res = db_proxy.read_db(sql_str)
    if sql_res is None or sql_res == []:
        return jsonify({'status': 0})
    else:
        return jsonify({'status': 1, "freq": sql_res[0][0]})


@reportgen_page.route('/reportGenAlarmStaticsRes')
@login_required
def mw_report_gen_alarm_statics_res():
    '''
    get alarm report statics info
    '''
    id_num = request.args.get('id', 0, type=int)
    sql_str = "select * from nsm_rptalarminfo where id = %d" % (id_num)
    db_proxy = DbProxy(CONFIG_DB_NAME)
    res, sql_res = db_proxy.read_db(sql_str)
    if res != 0:
        return jsonify({'status': 0, "rows": []})

    report_statics_file = sql_res[0][7]
    if os.path.exists("%s/%s" % (REPORT_GEN_ALARM_PATH, report_statics_file)) == True:
        f = open("%s/%s" % (REPORT_GEN_ALARM_PATH, report_statics_file), "r")
        statics_info = eval(f.read())
        f.close()
    else:
        statics_info = {'status': 0, "rows": []}
    return jsonify(statics_info)


@reportgen_page.route('/RptalarmdetailDownload/<report_id>', methods=['POST', 'GET'])
@login_required
def rpt_alarm_detail_download(report_id):
    '''
    download alarm report detail info
    '''
    curdir = REPORT_GEN_ALARM_PATH
    db_proxy = DbProxy(CONFIG_DB_NAME)
    msg = {}
    userip = get_oper_ip_info(request)
    loginuser = request.args.get('loginuser')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u'下载事件报告详情'
    msg['Result'] = '0'
    try:
        sql_str = "select report_name from nsm_rptalarminfo where id=%d" % int(report_id)
        res, rows = db_proxy.read_db(sql_str)
        if res != 0:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({"status": 0})
        file_name = base64.b64decode(rows[0][0]) + '.csv'
        send_log_db(MODULE_OPERATION, msg)
        return send_from_directory(curdir, file_name, as_attachment=True)
    except:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        current_app.logger.error(traceback.format_exc())
        return jsonify({"status": 0})


@reportgen_page.route('/RptalarmDownload/<report_id>', methods=['POST', 'GET'])
@login_required
def rpt_alarm_download(report_id):
    '''
    download alarm report detail info
    '''
    curdir = REPORT_GEN_ALARM_PATH
    db_proxy = DbProxy(CONFIG_DB_NAME)
    msg = {}
    userip = get_oper_ip_info(request)
    loginuser = request.args.get('loginuser')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u'下载事件报告'
    msg['Result'] = '0'
    try:
        sql_str = "select report_name from nsm_rptalarminfo where id=%d" % int(report_id)
        res, rows = db_proxy.read_db(sql_str)
        if res != 0:
            return jsonify({"status": 0})
        file_name = base64.b64decode(rows[0][0]) + '.pdf'
        send_log_db(MODULE_OPERATION, msg)
        return send_from_directory(curdir, file_name, as_attachment=True)
    except:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        current_app.logger.error(traceback.format_exc())
        return jsonify({"status": 0})


@reportgen_page.route('/reportGenAlarmInfo', methods=['GET', 'PUT', 'DELETE'])
@login_required
def mw_sysbackup_res():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    '''
    get alarm report info for UI
    '''
    msg = {}
    userip = get_oper_ip_info(request)
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)

        sql_str = "select * from nsm_rptalarminfo order by id desc limit 10 offset %d" % ((page - 1) * 10)
        res1, rptalarm_info = db_proxy.read_db(sql_str)
        rows = []
        tmp_report_path = "/data/report/alarm/"
        rptalarm_info = list(rptalarm_info)
        for elem in rptalarm_info:
            elem = list(elem)
            elem[1] = base64.b64decode(elem[1])
            if os.path.exists(tmp_report_path + str(elem[1]) + ".pdf"):
                elem.append(1)
            else:
                elem.append(0)
            rows.append(elem)
        sql_str = "select count(*) from nsm_rptalarminfo"
        res2, sql_res = db_proxy.read_db(sql_str)
        if res1 == 0 and res2 == 0:
            num = sql_res[0][0]
            return jsonify({'status': 1, 'rows': rows, 'total': num, 'page': page})
        else:
            return jsonify({'status': 0, 'rows': [], 'total': 0, 'page': page})

    elif request.method == 'PUT':
        json_data = request.get_json()
        report_id = json_data.get('id', '')
        new_name = json_data.get('report_name', '')
        if len(new_name.encode("utf-8")) > 128:
            return jsonify({"status": 0, "msg": "报告名称不能超过128个字节"})
        loginuser = json_data.get('loginuser', '')
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'
        msg['Operate'] = u'编辑事件报告名称'
        msg['Result'] = '1'
        sql_str = "select * from nsm_rptalarminfo where id=%d" % int(report_id)
        res, elem = db_proxy.read_db(sql_str)
        if res != 0:
            current_app.logger.error("res, elem = db_proxy.read_db(sql_str) == 0")
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({"status": 0})
        new_name_base64 = base64.b64encode(new_name)
        if elem[0][1] == new_name_base64:
            return jsonify({"status": 1})
        try:
            update_str = "update nsm_rptalarminfo set report_name=\"%s\" where id=%d" % (
            new_name_base64, int(report_id))
            res = db_proxy.write_db(update_str)
            if res != 0:
                current_app.logger.error("res = db_proxy.write_db(update_str) == 0")
                current_app.logger.error(update_str)
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({"status": 0})
            old_file_name = base64.b64decode(elem[0][1])
            os.rename(('/data/report/alarm/' + old_file_name + '.csv').encode('utf-8'),
                      ('/data/report/alarm/' + new_name + '.csv').encode('utf-8'))
            os.rename(('/data/report/alarm/' + old_file_name + '.pdf').encode('utf-8'),
                      ('/data/report/alarm/' + new_name + '.pdf').encode('utf-8'))
        except:
            current_app.logger.error(traceback.format_exc())
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({"status": 0})
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({"status": 1})

    elif request.method == 'DELETE':
        json_data = request.get_json()
        report_id_list = json_data.get('id_list', "")
        report_id_list = report_id_list.split(",")
        loginuser = json_data.get('loginuser', '')
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'
        msg['Operate'] = u'删除事件报告'
        msg['Result'] = '1'
        for report_id in report_id_list:
            try:
                sql_str = "select report_name from nsm_rptalarminfo where id=%d" % int(report_id)
                res, rows = db_proxy.read_db(sql_str)
                if res == 0:
                    report_name = base64.b64decode(rows[0][0])
                    os.remove("/data/report/alarm/" + report_name + ".csv")
                    pdf_path = "/data/report/alarm/" + report_name + ".pdf"
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)
            except:
                current_app.logger.error("report_file not found")
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({"status": 0})
            del_str = "delete from nsm_rptalarminfo where id=%d" % int(report_id)
            res = db_proxy.write_db(del_str)
            if res != 0:
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({"status": 0})
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({"status": 1})

    else:
        return jsonify({"status": 0})


if g_dpi_plat_type == DEV_PLT_X86:
    PROTO_LIST = ["telnet", "ftp", "http", "modbus", "iec104", "dnp3",
                  "enipio", "eniptcp", "enipudp", "goose", "mms", "opcda",
                  "opcua", "oracle", "pnrtdcp", "pop3", "profinetio", "s7",
                  "smtp", "snmp", "sv", "sip", "sqlserver", "s7plus"]
else:
    PROTO_LIST = ["telnet", "ftp", "http", "modbus", "iec104", "dnp3",
                  "enipio", "eniptcp", "enipudp", "goose", "mms", "opcda",
                  "opcua", "pnrtdcp", "pop3", "profinetio", "s7",
                  "smtp", "snmp", "sv", "sip", "sqlserver"]


@reportgen_page.route('/reportGenProtoTest')
@login_required
def mw_report_gen_proto_test():
    '''
    test route for protocal audit report gen
    '''
    freq = request.args.get('freq', 1, type=int)
    proto_audit_origin_report_gen_handle(freq)
    return jsonify({'status': 1})


# @reportgen_page.route('/reportGenProtoManual',methods=['GET', 'POST'])
# @login_required
# def mw_report_gen_proto_manual():
#     '''
#     route for protocal audit manual report gen
#     '''
#     if request.method == 'GET':
#         srcIp = request.args.get('srcIp')
#         srcPort = request.args.get('srcPort')
#         srcMac = request.args.get('srcMac')
#         destIp = request.args.get('destIp')
#         destPort = request.args.get('destPort')
#         destMac = request.args.get('destMac')
#         protocol = request.args.get('protocol')
#         start_time = request.args.get('starttime')
#         end_time = request.args.get('endtime')
#
#     elif request.method == 'POST':
#         post_data = request.get_json()
#         srcIp = post_data['srcIp']
#         srcPort = post_data['srcPort']
#         srcMac = post_data['srcMac']
#         destIp = post_data['destIp']
#         destPort = post_data['destPort']
#         destMac = post_data['destMac']
#         protocol = post_data['protocol']
#         start_time = post_data['starttime']
#         end_time = post_data['endtime']
#
#     if start_time == "" or end_time == "":
#         return jsonify({'status': 0})
#     freq_type = get_freq_type(start_time, end_time)
#
#     option_str = ""
#     if len(srcIp) > 0:
#         option_str += " and sourceIp like '%%%s%%'" % (srcIp)
#     if len(srcPort) > 0:
#         option_str += " and sourcePort = %s" % (srcPort)
#     if len(srcMac) > 0:
#         option_str += " and sourceMac like '%%%s%%'" % (srcMac)
#     if len(destIp) > 0:
#         option_str += " and destinationIp like '%%%s%%'" % (destIp)
#     if len(destPort) > 0:
#         option_str += " and destinationPort = %s" % (destPort)
#     if len(destMac) > 0:
#         option_str += " and destinationMac like '%%%s%%'" % (destMac)
#     if len(protocol) > 0:
#         option_str += " and protocolSourceName like '%%%s%%'" % (protocol)
#
#     if 1 == check_time_for_manual_report(start_time, end_time):
#         return jsonify({'status': 0})
#     proto_audit_origin_report_gen_handle(freq_type, start_time, end_time, option_str)
#     return jsonify({'status': 1})


@reportgen_page.route('/reportGenProtoManual', methods=['GET', 'POST'])
@login_required
def mw_report_gen_proto_manual():
    '''
    route for protocal audit manual report gen
    '''
    if request.method == 'GET':
        srcIp = request.args.get('srcIp')
        srcPort = request.args.get('srcPort')
        srcMac = request.args.get('srcMac')
        destIp = request.args.get('destIp')
        destPort = request.args.get('destPort')
        destMac = request.args.get('destMac')
        protocol = request.args.get('protocol')
        start_time = request.args.get('starttime')
        end_time = request.args.get('endtime')
        loginuser = request.args.get('loginuser')
    else:
        post_data = request.get_json()
        srcIp = post_data['srcIp']
        srcPort = post_data['srcPort']
        srcMac = post_data['srcMac']
        destIp = post_data['destIp']
        destPort = post_data['destPort']
        destMac = post_data['destMac']
        protocol = post_data['protocol']
        start_time = post_data['starttime']
        end_time = post_data['endtime']
        loginuser = post_data['loginuser']
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u'手动生成审计报告'
    msg['Result'] = '1'

    if start_time == "" or end_time == "":
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 0})
    freq_type = get_freq_type(start_time, end_time)

    option_str = ""
    if len(srcIp) > 0:
        option_str += " and sourceIp like '%%%s%%'" % (srcIp)
    if len(srcPort) > 0:
        option_str += " and sourcePort = %s" % (srcPort)
    if len(srcMac) > 0:
        option_str += " and sourceMac like '%%%s%%'" % (srcMac)
    if len(destIp) > 0:
        option_str += " and destinationIp like '%%%s%%'" % (destIp)
    if len(destPort) > 0:
        option_str += " and destinationPort = %s" % (destPort)
    if len(destMac) > 0:
        option_str += " and destinationMac like '%%%s%%'" % (destMac)
    if len(protocol) > 0:
        option_str += " and protocolSourceName like '%%%s%%'" % (protocol)

    if 1 == check_time_for_manual_report(start_time, end_time):
        return jsonify({'status': 0})
    paragram_dict = {"input_param": {"srcIp": srcIp, "srcPort": srcPort, "srcMac": srcMac, "destIp": destIp,
                                     "destPort": destPort, "destMac": destMac, "protocol": protocol,
                                     "start_time": start_time, "end_time": end_time}, "option_str": option_str}
    try:
        # current_app.logger.info(paragram_dict)
        proto_audit_origin_report_gen_handle(freq_type, **paragram_dict)
    except:
        current_app.logger.error(traceback.format_exc())
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


MAX_PROTO_REPORT_ITEM_NUM = 50000


def proto_audit_origin_report_gen_handle(freq_type, **kwargs):
    '''
    protocal audit report gen handle
    '''
    logger = set_up_logger()
    if not kwargs:
        kwargs["option_str"] = ""
        kwargs["input_param"] = {}
    try:
        if kwargs["input_param"]["start_time"] == "" or kwargs["input_param"]["end_time"] == "":
            start_time, end_time = get_start_end_time(freq_type)
        else:
            start_time = kwargs["input_param"]["start_time"]
            end_time = kwargs["input_param"]["end_time"]
    except:
        # logger.error("get_start_end_time error.")
        start_time, end_time = get_start_end_time(freq_type)

    if not kwargs["input_param"]:
        kwargs["input_param"]["start_time"] = start_time
        kwargs["input_param"]["end_time"] = end_time

    start_timestamp = int(time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S')))
    end_timestamp = int(time.mktime(time.strptime(end_time, '%Y-%m-%d %H:%M:%S')))

    # flowTimestamp时间格式为2018-10-19 17:12:17, packetTimestamp时间格式为1539940337
    # 获取各个协议对应的流条数,获取饼状图原数据
    sql_str = "select protocolSourceName,count(*) from flowdataheads where (not (packetTimestamp < %d or packetTimestamp >= %d))" \
              % (start_timestamp, end_timestamp)
    db_proxy = DbProxy()
    config_db_proxy = DbProxy(CONFIG_DB_NAME)
    res, sql_res = db_proxy.read_db(sql_str + kwargs["option_str"] + " group by protocolSourceName")
    # logger.info("sql_res:"+str(sql_res))
    proto_fig = {}
    if res == 0:
        total_num = 0
        for i in range(0, len(sql_res)):
            total_num += sql_res[i][1]
            proto_fig[str(sql_res[i][0])] = int(sql_res[i][1])
    else:
        return 1
    logger.info(proto_fig)

    # 获取源地址-目的地址排行前五名
    sql_str = "select sourceIp,destinationIp,count(*) from flowdataheads where (not (packetTimestamp < %d or packetTimestamp >= %d)) and sourceIp!='NULL' and destinationIp!='NULL' " \
              % (start_timestamp, end_timestamp)
    res, sql_res = db_proxy.read_db(
        sql_str + kwargs["option_str"] + " group by sourceIp,destinationIp order by count(*) desc limit 6")
    # logger.info("sql_res:"+str(sql_res))
    if res == 0:
        ip_order = sql_res
    else:
        ip_order = ()
    # logger.info(sql_str)
    sql_str = "select sourceMac,destinationMac,count(*) from flowdataheads where (not (packetTimestamp < %d or packetTimestamp >= %d)) and sourceIp='NULL' and destinationIp='NULL' " \
              % (start_timestamp, end_timestamp)
    res, sql_res = db_proxy.read_db(
        sql_str + kwargs["option_str"] + " group by sourceMac,destinationMac order by count(*) desc limit 5")
    # logger.info("sql_res:"+str(sql_res))
    if res == 0:
        mac_order = sql_res
    else:
        mac_order = ()
    # logger.info(sql_str)
    ip_order_list = list(ip_order)
    mac_order_list = list(mac_order)
    # logger.info(ip_order_list)
    # logger.info(mac_order_list)
    proto_order_list = []
    while len(ip_order_list) > 0 and len(mac_order_list) > 0:
        if ip_order_list[0][2] > mac_order_list[0][2]:
            proto_order_list.append(ip_order_list[0])
            del ip_order_list[0]
        else:
            proto_order_list.append(mac_order_list[0])
            del mac_order_list[0]
    proto_order_list.extend(ip_order_list)
    proto_order_list.extend(mac_order_list)
    logger.info("proto_order_list:" + str(proto_order_list))
    kwargs["proto_order"] = proto_order_list[:5]

    left_cnt = MAX_PROTO_REPORT_ITEM_NUM if total_num > MAX_PROTO_REPORT_ITEM_NUM else total_num

    # sql_str = "select dev_ip, dev_mac, dev_name from dev_name_conf"
    sql_str = "select ip, mac, name from topdevice"
    res, sql_res = config_db_proxy.read_db(sql_str)
    if res != 0:
        return 1

    dev_name_dict = {}
    for elem in sql_res:
        elem = list(elem)
        elem[1] = elem[1].replace(":", "")
        dev_name_dict[elem[0] + elem[1]] = elem[2]
    dev_name_dict[""] = "NA"

    sql_str = '''select max(id) from nsm_rptprotoinfo '''
    # sql_str = '''select count(*) from nsm_rptprotoinfo '''
    res, sql_res = config_db_proxy.read_db(sql_str)
    if res != 0:
        return 1
    if sql_res[0][0] == None:
        id_str = "1"
    else:
        id_str = str(sql_res[0][0] + 1)

    if freq_type == DAY_AUTO_TYPE:
        en_rpt_type_str = "_Daily_Report"
        ch_rpt_type_str = "_每日报表"
        date_str = start_time.split(" ")[0]
    elif freq_type == WEEK_AUTO_TYPE:
        en_rpt_type_str = "_Weekly_Report"
        ch_rpt_type_str = "_每周报表"
        date_str = start_time.split(" ")[0]
    elif freq_type == MONTH_AUTO_TYPE:
        en_rpt_type_str = "_Monthly_Report"
        ch_rpt_type_str = "_每月报表"
        date_str = start_time.split(" ")[0]
    else:
        en_rpt_type_str = "_Manual_Report"
        ch_rpt_type_str = "_自定义报表"
        date_str = start_time.replace(" ", "_") + "_" + end_time.replace(" ", "_")

    if freq_type > MONTH_AUTO_TYPE:
        report_name = base64.b64encode("协议审计_" + date_str + ch_rpt_type_str + "_%s" % id_str)
        file_name = ("ProtocalAudit_" + date_str + en_rpt_type_str + "_%s" % id_str + ".csv")
        statics_file_name = ("ProtocalAudit_" + date_str + en_rpt_type_str + "_%s" % id_str)
    else:
        report_name = base64.b64encode("协议审计_" + date_str + ch_rpt_type_str)
        file_name = ("ProtocalAudit_" + date_str + en_rpt_type_str + ".csv")
        statics_file_name = ("ProtocalAudit_" + date_str + en_rpt_type_str)

    writer = UnicodeWriter(open(REPORT_GEN_PROTO_AUDIT_PATH + "/" + file_name, "wb"))
    item_num = [U"符合条件总条数", U"实际显示条数"]
    writer.writerow(item_num)
    writer.writerow([str(total_num), str(left_cnt)])
    title = [U"创建日期", U"源设备名", U"源IP", U"源MAC", U"源端口",
             U"目的设备名", U"目的IP", U"目的MAC", U"目的端口", U"协议类型"]
    writer.writerow(title)

    index = 0
    while left_cnt > 0:
        if left_cnt >= 1000:
            get_cnt = 1000
        else:
            get_cnt = left_cnt
        sql_str = '''select packetTimestamp, sourceIp, sourceMac, sourcePort, destinationIp, \
                  destinationMac, destinationPort, protocolSourceName from flowdataheads where \
                  (not (packetTimestamp < %d or packetTimestamp >= %d)) %s order by \
                  packetTimestamp desc limit %d offset %d''' \
                  % (start_timestamp, end_timestamp, kwargs["option_str"], get_cnt, index * 1000)
        res, sql_res = db_proxy.read_db(sql_str)
        if res != 0:
            left_cnt -= get_cnt
            index += 1
            continue

        for i in range(0, len(sql_res)):
            src_ip_str = trans_db_ipmac_to_local(sql_res[i][1])
            src_mac_str = trans_db_ipmac_to_local(sql_res[i][2])
            dst_ip_str = trans_db_ipmac_to_local(sql_res[i][4])
            dst_mac_str = trans_db_ipmac_to_local(sql_res[i][5])
            if (src_ip_str + src_mac_str) in dev_name_dict:
                src_dev_name = dev_name_dict[src_ip_str + src_mac_str]
            else:
                src_dev_name = get_default_devname_by_ipmac(src_ip_str, src_mac_str)

            if (dst_ip_str + dst_mac_str) in dev_name_dict:
                dst_dev_name = dev_name_dict[dst_ip_str + dst_mac_str]
            else:
                dst_dev_name = get_default_devname_by_ipmac(dst_ip_str, dst_mac_str)

            proto_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(sql_res[i][0])))
            trans_res = [proto_time, src_dev_name.decode("UTF-8"), get_not_null_name(src_ip_str),
                         get_not_null_name(src_mac_str), str(sql_res[i][3]), dst_dev_name.decode("UTF-8"),
                         get_not_null_name(dst_ip_str), get_not_null_name(dst_mac_str), str(sql_res[i][6]),
                         get_ui_proto_name(sql_res[i][7])]
            writer.writerow(trans_res)
        left_cnt -= get_cnt
        index += 1

    date_list = []
    time_axis = []

    if freq_type == WEEK_AUTO_TYPE:
        date_list, time_axis = get_statics_time_section_by_day(start_time, end_time)
    if freq_type == MONTH_AUTO_TYPE:
        date_list, time_axis = get_statics_time_section_by_day(start_time, end_time)
    if freq_type == DAY_AUTO_TYPE:
        date_list = get_statics_time_section_by_hour(start_time, end_time)
        time_axis = HOUR_DATE_LIST
    if freq_type == HOUR_MANUAL_TYPE:
        date_list, time_axis = get_statics_time_section_by_hour_manual(start_time, end_time)
    if freq_type == DAY_MANUAL_TYPE:
        date_list, time_axis = get_statics_time_section_by_day_manual(start_time, end_time)
    if freq_type == MONTH_MANUAL_TYPE:
        date_list, time_axis = get_statics_time_section_by_month_manual(start_time, end_time)

    global PROTO_LIST
    proto_cmd_str = "select proto_name from self_define_proto_config where proto_id > 500"
    # proto_rows = new_send_cmd(TYPE_APP_SOCKET, proto_cmd_str, 1)
    res, proto_rows = config_db_proxy.read_db(proto_cmd_str)
    if res == 0 and len(proto_rows) > 0:
        for row in proto_rows:
            PROTO_LIST.append(row[0].encode('utf-8'))
    # 增加列表去重，解决生成审计报告时有时无问题
    PROTO_LIST = list(set(PROTO_LIST))
    answer = {}

    for proto in PROTO_LIST:
        answer[proto] = []

    answer["all"] = []
    answer["time_list"] = time_axis
    for i in range(0, len(date_list)):
        total_proto_num = 0
        for proto in PROTO_LIST:
            sql_str = "select count(*) from flowdataheads where (not (packetTimestamp < %d or packetTimestamp >= %d)) and protocolSourceName = '%s' " \
                      % (int(time.mktime(time.strptime(date_list[i][0], '%Y-%m-%d %H:%M:%S'))), int(time.mktime(time.strptime(date_list[i][1], '%Y-%m-%d %H:%M:%S'))), proto)
            res, sql_res = db_proxy.read_db(sql_str + kwargs["option_str"])
            if res != 0:
                proto_num = 0
            else:
                proto_num = sql_res[0][0]
            total_proto_num += proto_num
            answer[proto].append([time_axis[i], proto_num])
        answer["all"].append([time_axis[i], total_proto_num])

    rows = []
    for proto in PROTO_LIST:
        row_info = [get_ui_proto_name(proto), []]
        for elem in answer[proto]:
            row_info[1].append(elem[1])
        rows.append(row_info)

    row_info = ["all", []]
    for elem in answer["all"]:
        row_info[1].append(elem[1])
    rows.append(row_info)
    answer["rows"] = rows

    for proto in PROTO_LIST:
        answer.pop(proto)
    answer.pop("all")

    answer["status"] = 1
    # logger.info(answer)
    # f = open("%s/%s" % (REPORT_GEN_PROTO_AUDIT_PATH, statics_file_name), "w")
    # f.write(str(answer))
    # f.close()

    time_data = {}
    try:
        time_data["time_list"] = answer["time_list"]
        time_data["all"] = answer["rows"][-1][-1]
    except:
        logger.error("get proto time_data error.")
    kwargs["proto_time_data"] = time_data
    kwargs["proto_fig_data"] = proto_fig
    # 根据获取到的数据生成报告,并存储到对应的文件中
    # global REPORT_TYPE
    REPORT_TYPE = "audit"
    try:
        # logger.info(kwargs)
        proto_report = ReportBuild(REPORT_TYPE, freq_type, **kwargs)
        proto_report.run()
    except:
        logger.error("proto_report build error..")
        logger.error(traceback.format_exc())
    report_name_ch = base64.b64decode(report_name)
    os.rename('/data/report/protocal/audit_report.pdf', '/data/report/protocal/' + report_name_ch + ".pdf")
    os.rename('/data/report/protocal/' + file_name, '/data/report/protocal/' + report_name_ch + ".csv")

    # 将生成的报告相关信息存入数据库中
    ticks = int(time.time())
    gen_date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ticks))
    sql_str = '''insert into nsm_rptprotoinfo (id, report_name, report_time, report_start_time, report_stop_time, report_freq, report_raw_file, report_statics_file)
                 values(default, '%s','%s','%s','%s', %d,'%s', '%s')''' % (
    report_name, gen_date_str, start_time, end_time, freq_type, file_name, statics_file_name)
    config_db_proxy.write_db(sql_str)
    return 0


# MAX_PROTO_REPORT_ITEM_NUM = 50000
# def proto_audit_origin_report_gen_handle(freq_type, input_start = "", input_end = "", option_str = ""):
#     '''
#     protocal audit report gen handle
#     '''
#     if input_start == "" or input_end == "":
#         start_time, end_time = get_start_end_time(freq_type)
#     else:
#         start_time = input_start
#         end_time = input_end
#
#     start_timestamp = int(time.mktime(time.strptime(start_time,'%Y-%m-%d %H:%M:%S')))
#     end_timestamp = int(time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M:%S')))
#
#     sql_str = "select count(*) from flowdataheads where (not (flowTimestamp < '%s' or packetTimestamp >= %d)) " \
#               % (start_time, end_timestamp)
#     db_proxy = DbProxy()
#     res, sql_res = db_proxy.read_db(sql_str + option_str)
#     if res == 0:
#         total_num = sql_res[0][0]
#     else:
#         return 1
#
#     left_cnt = MAX_PROTO_REPORT_ITEM_NUM if total_num > MAX_PROTO_REPORT_ITEM_NUM else total_num
#
#     sql_str = "select dev_ip, dev_mac, dev_name from dev_name_conf"
#     res, sql_res = db_proxy.read_db(sql_str)
#     if res != 0:
#         return 1
#
#     dev_name_dict = {}
#     for elem in sql_res:
#         dev_name_dict[elem[0] + elem[1]] = elem[2]
#     dev_name_dict[""] = "NA"
#
#     sql_str = '''select max(id) from nsm_rptprotoinfo '''
#     res, sql_res = db_proxy.read_db(sql_str)
#     if res != 0:
#         return 1
#     if sql_res[0][0] == None:
#         id_str = "1"
#     else:
#         id_str = str(sql_res[0][0] + 1)
#
#     if freq_type == DAY_AUTO_TYPE:
#         en_rpt_type_str = "_Daily_Report"
#         ch_rpt_type_str = "_每日报表"
#         date_str = start_time.split(" ")[0]
#     elif freq_type == WEEK_AUTO_TYPE:
#         en_rpt_type_str = "_Weekly_Report"
#         ch_rpt_type_str = "_每周报表"
#         date_str = start_time.split(" ")[0]
#     elif freq_type == MONTH_AUTO_TYPE:
#         en_rpt_type_str = "_Monthly_Report"
#         ch_rpt_type_str = "_每月报表"
#         date_str = start_time.split(" ")[0]
#     else:
#         en_rpt_type_str = "_Manual_Report"
#         ch_rpt_type_str = "_自定义报表"
#         date_str = start_time.replace(" ", "_") + "_" + end_time.replace(" ", "_")
#
#     if freq_type > MONTH_AUTO_TYPE:
#         report_name = base64.b64encode("协议审计_" + date_str + ch_rpt_type_str + "_%s" % id_str)
#         file_name = ("ProtocalAudit_" + date_str + en_rpt_type_str + "_%s" % id_str + ".csv")
#         statics_file_name = ("ProtocalAudit_" + date_str + en_rpt_type_str + "_%s" % id_str + "_statics")
#     else:
#         report_name = base64.b64encode("协议审计_" + date_str + ch_rpt_type_str)
#         file_name = ("ProtocalAudit_" + date_str + en_rpt_type_str +".csv")
#         statics_file_name = ("ProtocalAudit_" + date_str + en_rpt_type_str + "_statics")
#
#     writer = UnicodeWriter(open(REPORT_GEN_PROTO_AUDIT_PATH + "/" + file_name, "wb"))
#     item_num = [U"符合条件总条数", U"实际显示条数"]
#     writer.writerow(item_num)
#     writer.writerow([str(total_num), str(left_cnt)])
#     #title = ["日期".decode("UTF-8"), "源设备名".decode("UTF-8"), "源IP".decode("UTF-8"), "源MAC".decode("UTF-8"),"源端口".decode("UTF-8"),
#     #         "目的设备名".decode("UTF-8"), "目的IP".decode("UTF-8"), "目的MAC".decode("UTF-8"), "目的端口".decode("UTF-8"), "协议类型".decode("UTF-8")]
#     title = [U"创建日期", U"源设备名", U"源IP", U"源MAC",U"源端口",
#              U"目的设备名", U"目的IP", U"目的MAC", U"目的端口", U"协议类型"]
#     writer.writerow(title)
#
#     #write alarm info into excle file
#     index = 0
#     while left_cnt > 0:
#         if left_cnt >= 1000:
#             get_cnt = 1000
#         else:
#             get_cnt = left_cnt
#         sql_str = '''select packetTimestamp, sourceIp, sourceMac, sourcePort, destinationIp, \
#                   destinationMac, destinationPort, protocolSourceName from flowdataheads where \
#                   (not (flowTimestamp < '%s' or packetTimestamp >= %d)) %s order by \
#                   packetTimestamp desc limit %d offset %d''' \
#                   % (start_time, end_timestamp, option_str, get_cnt, index*1000)
#         res, sql_res = db_proxy.read_db(sql_str)
#         if res != 0:
#             left_cnt -= get_cnt
#             index += 1
#             continue
#
#         for i in range(0, len(sql_res)):
#             src_ip_str = trans_db_ipmac_to_local(sql_res[i][1])
#             src_mac_str = trans_db_ipmac_to_local(sql_res[i][2])
#             dst_ip_str = trans_db_ipmac_to_local(sql_res[i][4])
#             dst_mac_str = trans_db_ipmac_to_local(sql_res[i][5])
#             if (src_ip_str + src_mac_str) in dev_name_dict:
#                 src_dev_name = dev_name_dict[src_ip_str + src_mac_str]
#             else:
#                 src_dev_name = get_default_devname_by_ipmac(src_ip_str, src_mac_str)
#
#             if (dst_ip_str + dst_mac_str) in dev_name_dict:
#                 dst_dev_name = dev_name_dict[dst_ip_str + dst_mac_str]
#             else:
#                 dst_dev_name = get_default_devname_by_ipmac(dst_ip_str, dst_mac_str)
#
#             proto_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(sql_res[i][0])))
#             trans_res = [proto_time, src_dev_name.decode("UTF-8"), get_not_null_name(src_ip_str), get_not_null_name(src_mac_str), str(sql_res[i][3]), dst_dev_name.decode("UTF-8"), get_not_null_name(dst_ip_str), get_not_null_name(dst_mac_str), str(sql_res[i][6]), get_ui_proto_name(sql_res[i][7])]
#             writer.writerow(trans_res)
#         left_cnt -= get_cnt
#         index += 1
#
#     date_list = []
#     time_axis = []
#
#     if freq_type == WEEK_AUTO_TYPE:
#         date_list, time_axis = get_statics_time_section_by_day(start_time, end_time)
#     if freq_type == MONTH_AUTO_TYPE:
#         date_list, time_axis = get_statics_time_section_by_day(start_time, end_time)
#     if freq_type == DAY_AUTO_TYPE:
#         date_list = get_statics_time_section_by_hour(start_time, end_time)
#         time_axis = HOUR_DATE_LIST
#     if freq_type == HOUR_MANUAL_TYPE:
#         date_list, time_axis = get_statics_time_section_by_hour_manual(start_time, end_time)
#     if freq_type == DAY_MANUAL_TYPE:
#         date_list, time_axis = get_statics_time_section_by_day_manual(start_time, end_time)
#     if freq_type == MONTH_MANUAL_TYPE:
#         date_list, time_axis = get_statics_time_section_by_month_manual(start_time, end_time)
#
#     answer = {}
#     for proto in PROTO_LIST:
#         answer[proto] = []
#
#     answer["all"] = []
#     answer["time_list"] = time_axis
#     for i in range(0, len(date_list)):
#         total_proto_num = 0
#         for proto in PROTO_LIST:
#             sql_str = "select count(*) from flowdataheads where (not (flowTimestamp < '%s' or packetTimestamp >= %d)) and protocolSourceName = '%s' " \
#                       % (date_list[i][0], int(time.mktime(time.strptime(date_list[i][1],'%Y-%m-%d %H:%M:%S'))), proto)
#             res, sql_res = db_proxy.read_db(sql_str + option_str)
#             if res != 0:
#                 proto_num = 0
#             else:
#                 proto_num = sql_res[0][0]
#             total_proto_num += proto_num
#             answer[proto].append([time_axis[i], proto_num])
#         answer["all"].append([time_axis[i], total_proto_num])
#
#     rows = []
#     for proto in PROTO_LIST:
#         row_info = [get_ui_proto_name(proto), []]
#         for elem in answer[proto]:
#             row_info[1].append(elem[1])
#         rows.append(row_info)
#
#     row_info = ["all", []]
#     for elem in answer["all"]:
#         row_info[1].append(elem[1])
#     rows.append(row_info)
#     answer["rows"] = rows
#
#     for proto in PROTO_LIST:
#         answer.pop(proto)
#     answer.pop("all")
#
#     answer["status"] = 1
#     f = open("%s/%s" % (REPORT_GEN_PROTO_AUDIT_PATH, statics_file_name), "w")
#     f.write(str(answer))
#     f.close()
#
#     ticks = int(time.time())
#     gen_date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ticks))
#     sql_str = '''insert into nsm_rptprotoinfo (id, report_name, report_time, report_start_time, report_stop_time, report_freq, report_raw_file, report_statics_file)
#                  values(default, '%s','%s','%s','%s', %d,'%s', '%s')''' % (report_name, gen_date_str, start_time, end_time, freq_type, file_name, statics_file_name)
#     db_proxy.write_db(sql_str)
#     return 0


@reportgen_page.route('/reportGenProtoSetmode', methods=['GET', 'POST'])
@login_required
def mw_report_gen_proto_audit_setmode():
    '''
    set protocal audit report gen mode
    '''
    if request.method == 'GET':
        freq = request.args.get('freq', 1, type=int)
    else:
        post_data = request.get_json()
        freq = int(post_data['freq'])
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select * from nsm_rptprotomode"
    # sql_res = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
    _, sql_res = db_proxy.read_db(sql_str)
    if sql_res is None or sql_res == []:
        return jsonify({'status': 0})
    if sql_res[0][0] != freq:
        os.system("sed -ir '/.*rptproto_proc.pyc.*/d' %s" % CROND_PATH)
        if freq == 1:
            os.system("echo \"5 0 * * * python %s/rptproto_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        elif freq == 2:
            os.system("echo \"5 0 * * 1  python %s/rptproto_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        elif freq == 3:
            os.system("echo \"5 0 1 * *  python %s/rptproto_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        else:
            pass
        os.system("crontab -c %s %s" % (CROND_CONF, CROND_PATH))
        conf_save_flag_set()
        sql_str = "update nsm_rptprotomode set flag = %d" % freq
        # new_send_cmd(TYPE_APP_SOCKET, sql_str, 2)
        db_proxy.write_db(sql_str)
    return jsonify({'status': 1})


@reportgen_page.route('/reportGenProtoStaticsRes')
@login_required
def mw_report_gen_proto_audit_statics_res():
    '''
    get protocal audit report statics info
    '''
    id_num = request.args.get('id', 0, type=int)
    sql_str = "select * from nsm_rptprotoinfo where id = %d" % (id_num)
    db_proxy = DbProxy(CONFIG_DB_NAME)
    res, sql_res = db_proxy.read_db(sql_str)
    if res != 0:
        return jsonify({'status': 0})

    report_statics_file = sql_res[0][7]
    if os.path.exists("%s/%s" % (REPORT_GEN_PROTO_AUDIT_PATH, report_statics_file)) == True:
        f = open("%s/%s" % (REPORT_GEN_PROTO_AUDIT_PATH, report_statics_file), "r")
        val_str = f.read()
        statics_info = eval(val_str)
        f.close()
    else:
        statics_info = {'status': 0}
    return jsonify(statics_info)


@reportgen_page.route('/reportGenProtoInfo', methods=['GET', 'PUT', 'DELETE'])
@login_required
def mw_report_gen_proto_info():
    '''
    get protocal report info for UI
    '''
    msg = {}
    userip = get_oper_ip_info(request)
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        sql_str = "select * from nsm_rptprotoinfo order by id desc limit 10 offset %d" % ((page - 1) * 10)
        res1, rptproto_info = db_proxy.read_db(sql_str)
        if res1 != 0:
            return jsonify({'status': 0, 'rows': [], 'total': 0, 'page': page})
        rptproto_info = list(rptproto_info)
        rows = []
        tmp_report_path = "/data/report/protocal/"
        for elem in rptproto_info:
            elem = list(elem)
            elem[1] = base64.b64decode(elem[1])
            if os.path.exists(tmp_report_path + str(elem[1]) + ".pdf"):
                elem.append(1)
            else:
                elem.append(0)
            rows.append(elem)
        sql_str = "select count(*) from nsm_rptprotoinfo"
        res2, sql_res = db_proxy.read_db(sql_str)
        if res2 != 0:
            return jsonify({'status': 0, 'rows': [], 'total': 0, 'page': page})
        num = sql_res[0][0]
        return jsonify({'status': 1, 'rows': rows, 'total': num, 'page': page})
    elif request.method == 'PUT':
        json_data = request.get_json()
        report_id = json_data.get('id', '')
        new_name = json_data.get('report_name', '')
        if len(new_name.encode("utf-8")) > 128:
            return jsonify({"status": 0, "msg": "报告名称不能超过128个字节"})
        loginuser = json_data.get('loginuser', '')
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'
        msg['Operate'] = u'编辑审计报告名称'
        msg['Result'] = '1'
        sql_str = "select * from nsm_rptprotoinfo where id=%d" % int(report_id)
        res, elem = db_proxy.read_db(sql_str)
        if res != 0:
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({"status": 0})
        new_name_base64 = base64.b64encode(new_name)
        if elem[0][1] == new_name_base64:
            return jsonify({"status": 1})
        try:
            update_str = "update nsm_rptprotoinfo set report_name=\"%s\" where id=%d" % (
            new_name_base64, int(report_id))
            res = db_proxy.write_db(update_str)
            if res != 0:
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({"status": 0})
            old_file_name = base64.b64decode(elem[0][1])
            os.rename(('/data/report/protocal/' + old_file_name + '.csv').encode('utf-8'),
                      ('/data/report/protocal/' + new_name + ".csv").encode('utf-8'))
            os.rename(('/data/report/protocal/' + old_file_name + '.pdf').encode('utf-8'),
                      ('/data/report/protocal/' + new_name + ".pdf").encode('utf-8'))
        except:
            current_app.logger.error(traceback.format_exc())
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({"status": 0})
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({"status": 1})

    elif request.method == 'DELETE':
        json_data = request.get_json()
        report_id_list = json_data.get('id_list', '')
        report_id_list = report_id_list.split(",")
        loginuser = json_data.get('loginuser', '')
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'
        msg['Operate'] = u'删除审计报告'
        msg['Result'] = '1'
        for report_id in report_id_list:
            try:
                sql_str = "select report_name from nsm_rptprotoinfo where id=%d" % int(report_id)
                res, rows = db_proxy.read_db(sql_str)
                if res == 0:
                    report_name = base64.b64decode(rows[0][0])
                    os.remove("/data/report/protocal/" + report_name + ".csv")
                    pdf_path = "/data/report/protocal/" + report_name + ".pdf"
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)
            except:
                current_app.logger.error("report_file not found")
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({"status": 0})
            del_str = "delete from nsm_rptprotoinfo where id=%d" % int(report_id)
            res = db_proxy.write_db(del_str)
            if res != 0:
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({"status": 0})
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({"status": 1})
    else:
        return jsonify({"status": 0})


@reportgen_page.route('/reportGenProtoGetmode')
@login_required
def mw_report_gen_proto_getmode():
    '''
    get protocal audit report gen mode
    '''
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select * from nsm_rptprotomode"
    # sql_res = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
    _, sql_res = db_proxy.read_db(sql_str)
    if sql_res is None or sql_res == []:
        return jsonify({'status': 0})
    else:
        return jsonify({'status': 1, "freq": sql_res[0][0]})


@reportgen_page.route('/RptprotodetailDownload/<report_id>', methods=['POST', 'GET'])
@login_required
def rpt_proto_detail_download(report_id):
    '''
    download protocal audit report detail info
    '''
    curdir = REPORT_GEN_PROTO_AUDIT_PATH
    db_proxy = DbProxy(CONFIG_DB_NAME)
    msg = {}
    userip = get_oper_ip_info(request)
    loginuser = request.args.get('loginuser')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u'下载审计报告详情'
    msg['Result'] = '0'
    try:
        sql_str = "select report_name from nsm_rptprotoinfo where id=%d" % int(report_id)
        res, rows = db_proxy.read_db(sql_str)
        if res != 0:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({"status": 0})
        file_name = base64.b64decode(rows[0][0]) + '.csv'
        send_log_db(MODULE_OPERATION, msg)
        return send_from_directory(curdir, file_name, as_attachment=True)
    except:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        current_app.logger.error(traceback.format_exc())
        return jsonify({"status": 0})


@reportgen_page.route('/RptprotoDownload/<report_id>', methods=['POST', 'GET'])
@login_required
def rpt_proto_download(report_id):
    '''
    download protocal audit report info
    '''
    curdir = REPORT_GEN_PROTO_AUDIT_PATH
    db_proxy = DbProxy(CONFIG_DB_NAME)
    msg = {}
    userip = get_oper_ip_info(request)
    loginuser = request.args.get('loginuser')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u'下载审计报告'
    msg['Result'] = '0'
    try:
        sql_str = "select report_name from nsm_rptprotoinfo where id=%d" % int(report_id)
        res, rows = db_proxy.read_db(sql_str)
        if res != 0:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({"status": 0})
        file_name = base64.b64decode(rows[0][0]) + '.pdf'
        send_log_db(MODULE_OPERATION, msg)
        return send_from_directory(curdir, file_name, as_attachment=True)
    except:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        current_app.logger.error(traceback.format_exc())
        return jsonify({"status": 0})


@reportgen_page.route('/reportGenSyslogTest')
@login_required
def mw_report_gen_syslog_test():
    '''
    test route for sys log report gen
    '''
    freq = request.args.get('freq', 1, type=int)
    res, raw_file, statics_file = sys_log_report_gen_handle(freq)
    return jsonify({'status': 1, "raw_file": raw_file, "statics_file": statics_file})


SYS_LOG_LEVEL_DICT = {6: "信息".decode("UTF-8"), 4: "警告".decode("UTF-8"), 1: "警告".decode("UTF-8")}
SYS_LOG_EN_LEVEL_DICT = {6: "info", 4: "info", 1: "alarm"}
SYS_LOG_TYPE_DICT = {1: "设备状态".decode("UTF-8"),
                     2: "接口状态".decode("UTF-8"),
                     3: "系统状态".decode("UTF-8"),
                     4: "业务状态".decode("UTF-8"),
                     5: "bypass状态".decode("UTF-8")}
SYS_LOG_EN_TYPE_DICT = {1: "device",
                        2: "interface",
                        3: "system",
                        4: "service",
                        5: "bypass"}

MAX_SYS_LOG_REPORT_ITEM_NUM = 50000


def sys_log_report_gen_handle(freq_type, input_start="", input_end=""):
    '''
    sys log report gen handle
    '''
    if input_start == "" or input_end == "":
        start_time, end_time = get_start_end_time(freq_type)
    else:
        start_time = input_start
        end_time = input_end
    sql_str = "select count(*) from events where timestamp < '%s' and timestamp >= '%s' " \
              % (time_str_tz_proc(end_time), time_str_tz_proc(start_time))
    db_proxy = DbProxy()
    res, sql_res = db_proxy.read_db(sql_str)
    if res == 0:
        total_num = sql_res[0][0]
    else:
        return 1, "", ""

    left_cnt = MAX_SYS_LOG_REPORT_ITEM_NUM if total_num > MAX_SYS_LOG_REPORT_ITEM_NUM else total_num

    if freq_type == DAY_AUTO_TYPE:
        en_rpt_type_str = "_Daily_Report"
        ch_rpt_type_str = "_每日报表"
        date_str = start_time.split(" ")[0]
    elif freq_type == WEEK_AUTO_TYPE:
        en_rpt_type_str = "_Weekly_Report"
        ch_rpt_type_str = "_每周报表"
        date_str = start_time.split(" ")[0]
    elif freq_type == MONTH_AUTO_TYPE:
        en_rpt_type_str = "_Monthly_Report"
        ch_rpt_type_str = "_每月报表"
        date_str = start_time.split(" ")[0]
    else:
        en_rpt_type_str = "_Manual_Report"
        ch_rpt_type_str = "_自定义报表"
        date_str = start_time.replace(" ", "_") + "_" + end_time.replace(" ", "_")

    file_name = ("Syslog_" + date_str + en_rpt_type_str + ".csv")
    statics_file_name = ("Syslog_" + date_str + en_rpt_type_str + "_statics")
    title = ["日期".decode("UTF-8"), "日志等级".decode("UTF-8"), "日志类型".decode("UTF-8"), "内容".decode("UTF-8")]
    writer = UnicodeWriter(open(REPORT_GEN_LOG_PATH + "/" + file_name, "wb"))
    writer.writerow(title)

    param_dict = {}
    sql_str = "select type,count(*) from events where timestamp >= '%s' and timestamp < '%s' group by type;" % (
    time_str_tz_proc(start_time), time_str_tz_proc(end_time))
    res, sql_res = db_proxy.read_db(sql_str)
    if res == 0:
        param_dict["sys_log_fig"] = sql_res
    else:
        param_dict["sys_log_fig"] = ()

    index = 0
    while left_cnt > 0:
        if left_cnt >= 1000:
            get_cnt = 1000
        else:
            get_cnt = left_cnt
        sql_str = '''select timestamp, level, type, content from events where timestamp >= '%s' and timestamp < '%s'
                  order by timestamp desc limit %d offset %d''' % (
        time_str_tz_proc(start_time), time_str_tz_proc(end_time), get_cnt, index * 1000)
        res, sql_res = db_proxy.read_db(sql_str)
        if res != 0:
            left_cnt -= get_cnt
            index += 1
            continue

        for i in range(0, len(sql_res)):
            data_list = []
            for j in range(0, 4):
                if j == 1:
                    data_elem = SYS_LOG_LEVEL_DICT[sql_res[i][j]]
                elif j == 2:
                    data_elem = SYS_LOG_TYPE_DICT[sql_res[i][j]]
                elif j == 3:
                    data_elem = sql_res[i][j].decode("UTF-8")
                else:
                    data_elem = sql_res[i][j].replace("T", " ").replace("Z", "")
                data_list.append(data_elem)
            writer.writerow(data_list)
        left_cnt -= get_cnt
        index += 1

    date_list = []
    time_axis = []

    if freq_type == WEEK_AUTO_TYPE:
        date_list, time_axis = get_statics_time_section_by_day(start_time, end_time)
    if freq_type == MONTH_AUTO_TYPE:
        date_list, time_axis = get_statics_time_section_by_day(start_time, end_time)
    if freq_type == DAY_AUTO_TYPE:
        date_list = get_statics_time_section_by_hour(start_time, end_time)
        time_axis = HOUR_DATE_LIST
    if freq_type == HOUR_MANUAL_TYPE:
        date_list, time_axis = get_statics_time_section_by_hour_manual(start_time, end_time)
    if freq_type == DAY_MANUAL_TYPE:
        date_list, time_axis = get_statics_time_section_by_day_manual(start_time, end_time)
    if freq_type == MONTH_MANUAL_TYPE:
        date_list, time_axis = get_statics_time_section_by_month_manual(start_time, end_time)

    answer = {}
    for i in range(1, 6):
        answer[SYS_LOG_EN_TYPE_DICT[i]] = []
    answer["all"] = []
    for i in range(0, len(date_list)):
        total_proto_num = 0
        for log_type in range(1, 6):
            sql_str = "select count(*) from events where type = %d and timestamp >= '%s' and timestamp < '%s'" \
                      % (log_type, time_str_tz_proc(date_list[i][0]), time_str_tz_proc(date_list[i][1]))
            res, sql_res = db_proxy.read_db(sql_str)
            if res != 0:
                log_num = 0
            else:
                log_num = sql_res[0][0]
            total_proto_num += log_num
            answer[SYS_LOG_EN_TYPE_DICT[log_type]].append([time_axis[i], log_num])
        answer["all"].append([time_axis[i], total_proto_num])

    # 获取警告日志随时间分布趋势数据
    answer_dict = {}
    for i in [1, 4, 6]:
        answer_dict[SYS_LOG_EN_LEVEL_DICT[i]] = []
    for i in range(0, len(date_list)):
        total_proto_num = 0
        for log_level in [1, 4, 6]:
            sql_str = "select count(*) from events where level = %d and timestamp >= '%s' and timestamp < '%s'" \
                      % (log_level, time_str_tz_proc(date_list[i][0]), time_str_tz_proc(date_list[i][1]))
            res, sql_res = db_proxy.read_db(sql_str)
            if res != 0:
                log_num = 0
            else:
                log_num = sql_res[0][0]
            total_proto_num += log_num
            answer_dict[SYS_LOG_EN_LEVEL_DICT[log_level]].append([time_axis[i], log_num])

    param_dict["sys_log_time"] = answer["all"]

    param_dict["alarm_log_time"] = answer_dict["alarm"]

    answer["status"] = 1
    # f = open("%s/%s" % (REPORT_GEN_LOG_PATH, statics_file_name), "w")
    # f.write(str(answer))
    # f.close()

    return 0, file_name, statics_file_name, param_dict


OPER_LOG_RESULT_DICT = {"0": "成功", "1": "失败"}


@reportgen_page.route('/reportGenOperlogTest')
@login_required
def mw_report_gen_operlog_test():
    '''
    test route for oper log report gen
    '''
    freq = request.args.get('freq', 1, type=int)
    res, raw_file, statics_file, db_cont = oper_log_report_gen_handle(freq)
    return jsonify({'status': 1, "raw_file": raw_file, "statics_file": statics_file, "db_cont": db_cont})


MAX_OPER_LOG_REPORT_ITEM_NUM = 50000


def oper_log_report_gen_handle(freq_type, input_start="", input_end=""):
    '''
    oper log report gen handle
    '''
    if input_start == "" or input_end == "":
        start_time, end_time = get_start_end_time(freq_type)
    else:
        start_time = input_start
        end_time = input_end

    param = {}
    sql_str = '''SELECT oper,count(*) from dpiuseroperationlogs inner join operationlogs opl
              on opl.operationLogId=dpiuseroperationlogs.operationLogId where dpiuseroperationlogs.timestamp >= "%s"
              and dpiuseroperationlogs.timestamp < "%s" group by oper order by count(*) desc''' % (
    time_str_tz_proc(start_time), time_str_tz_proc(end_time))
    db_proxy = DbProxy()
    config_db_proxy = DbProxy(CONFIG_DB_NAME)
    res, sql_res = db_proxy.read_db(sql_str)
    if res == 0:
        total_num = 0
        param["oper_fig"] = sql_res
        for row in sql_res:
            total_num += int(row[1])
    else:
        param["oper_fig"] = ()
    left_cnt = MAX_OPER_LOG_REPORT_ITEM_NUM if total_num > MAX_OPER_LOG_REPORT_ITEM_NUM else total_num

    if freq_type == DAY_AUTO_TYPE:
        en_rpt_type_str = "_Daily_Report"
        ch_rpt_type_str = "_每日报表"
        date_str = start_time.split(" ")[0]
    elif freq_type == WEEK_AUTO_TYPE:
        en_rpt_type_str = "_Weekly_Report"
        ch_rpt_type_str = "_每周报表"
        date_str = start_time.split(" ")[0]
    elif freq_type == MONTH_AUTO_TYPE:
        en_rpt_type_str = "_Monthly_Report"
        ch_rpt_type_str = "_每月报表"
        date_str = start_time.split(" ")[0]
    else:
        en_rpt_type_str = "_Manual_Report"
        ch_rpt_type_str = "_自定义报表"
        date_str = start_time.replace(" ", "_") + "_" + end_time.replace(" ", "_")

    report_name = base64.b64encode("日志_" + date_str + ch_rpt_type_str)
    if freq_type > MONTH_AUTO_TYPE:
        sql_str = '''select max(id) from nsm_rptloginfo '''
        # sql_str = '''select count(*) from nsm_rptloginfo '''
        res, sql_res = config_db_proxy.read_db(sql_str)
        if res != 0:
            return 1
        if sql_res[0][0] == None:
            id_str = "1"
        else:
            id_str = str(sql_res[0][0] + 1)
        report_name = base64.b64encode("日志_" + date_str + ch_rpt_type_str + "_" + id_str)
    file_name = ("Operlog_" + date_str + en_rpt_type_str + ".csv")
    statics_file_name = ("Operlog_" + date_str + en_rpt_type_str + "_statics")
    title = ["日期".decode("UTF-8"), "用户".decode("UTF-8"), "IP".decode("UTF-8"), "执行操作".decode("UTF-8"),
             "执行结果".decode("UTF-8")]
    writer = UnicodeWriter(open(REPORT_GEN_LOG_PATH + "/" + file_name, "wb"))
    item_num = [U"符合条件总条数", U"实际显示条数"]
    writer.writerow(item_num)
    writer.writerow([str(total_num), str(left_cnt)])
    writer.writerow(title)

    # write alarm info into excle file
    index = 0
    while left_cnt > 0:
        if left_cnt >= 1000:
            get_cnt = 1000
        else:
            get_cnt = left_cnt
        sql_str = '''SELECT dpiuseroperationlogs.timestamp,user,user_ip,oper,oper_result from dpiuseroperationlogs
                  inner join operationlogs opl on opl.operationLogId=dpiuseroperationlogs.operationLogId
                  where dpiuseroperationlogs.timestamp >= '%s' and dpiuseroperationlogs.timestamp < '%s'
                  order by dpiuseroperationlogs.timestamp desc limit %d offset %d ''' \
                  % (time_str_tz_proc(start_time), time_str_tz_proc(end_time), get_cnt, index * 1000)
        res, sql_res = db_proxy.read_db(sql_str)
        if res != 0:
            left_cnt -= get_cnt
            index += 1
            continue
        for i in range(0, len(sql_res)):
            data_list = []
            for j in range(0, 5):
                if j == 4:
                    if sql_res[i][j] in OPER_LOG_RESULT_DICT:
                        data_elem = OPER_LOG_RESULT_DICT[sql_res[i][j]].decode("UTF-8")
                    else:
                        data_elem = U"失败"
                elif j == 0:
                    data_elem = sql_res[i][j].replace("T", " ").replace("Z", "")
                else:
                    data_elem = sql_res[i][j].decode("UTF-8")
                data_list.append(data_elem)
            writer.writerow(data_list)
        left_cnt -= get_cnt
        index += 1

    date_list = []
    time_axis = []

    if freq_type == WEEK_AUTO_TYPE:
        date_list, time_axis = get_statics_time_section_by_day(start_time, end_time)
    if freq_type == MONTH_AUTO_TYPE:
        date_list, time_axis = get_statics_time_section_by_day(start_time, end_time)
    if freq_type == DAY_AUTO_TYPE:
        date_list = get_statics_time_section_by_hour(start_time, end_time)
        time_axis = HOUR_DATE_LIST
    if freq_type == HOUR_MANUAL_TYPE:
        date_list, time_axis = get_statics_time_section_by_hour_manual(start_time, end_time)
    if freq_type == DAY_MANUAL_TYPE:
        date_list, time_axis = get_statics_time_section_by_day_manual(start_time, end_time)
    if freq_type == MONTH_MANUAL_TYPE:
        date_list, time_axis = get_statics_time_section_by_month_manual(start_time, end_time)

    answer = {}
    user_list = []
    sql_str = '''SELECT user, count(*) from dpiuseroperationlogs
              inner join operationlogs opl on opl.operationLogId=dpiuseroperationlogs.operationLogId
              where dpiuseroperationlogs.timestamp >= '%s' and dpiuseroperationlogs.timestamp < '%s'
              group by user''' % (time_str_tz_proc(start_time), time_str_tz_proc(end_time))
    res, sql_res = db_proxy.read_db(sql_str)
    if res != 0:
        pass
    else:
        tmp_list = list(sql_res)
        sorted_list = sorted(tmp_list, key=lambda x: x[1], reverse=True)
        index = 0
        for elem in sorted_list:
            if index > 4:
                break
            user_list.append(elem[0])
            index += 1

    answer["all"] = []
    tmp_statics_dict = {}
    for user in user_list:
        tmp_statics_dict[user] = []
    for i in range(0, len(date_list)):
        for user in user_list:
            sql_str = '''SELECT count(*) from dpiuseroperationlogs
                      inner join operationlogs opl on opl.operationLogId=dpiuseroperationlogs.operationLogId
                      where user = '%s' and dpiuseroperationlogs.timestamp >= '%s' and dpiuseroperationlogs.timestamp < '%s'
                      ''' % (user, time_str_tz_proc(date_list[i][0]), time_str_tz_proc(date_list[i][1]))
            res, sql_res = db_proxy.read_db(sql_str)
            if res != 0:
                log_num = 0
            else:
                log_num = sql_res[0][0]
            tmp_statics_dict[user].append([time_axis[i], log_num])

        sql_str = '''SELECT count(*) from dpiuseroperationlogs
                  inner join operationlogs opl on opl.operationLogId=dpiuseroperationlogs.operationLogId
                  where dpiuseroperationlogs.timestamp >= '%s' and dpiuseroperationlogs.timestamp < '%s'
                  ''' % (time_str_tz_proc(date_list[i][0]), time_str_tz_proc(date_list[i][1]))
        res, sql_res = db_proxy.read_db(sql_str)
        if res != 0:
            total_log_num = 0
        else:
            total_log_num = sql_res[0][0]
        answer["all"].append([time_axis[i], total_log_num])

    # 获取操作用户ip登录排行
    sql_str = '''SELECT user_ip, count(*) from dpiuseroperationlogs
              inner join operationlogs opl on opl.operationLogId=dpiuseroperationlogs.operationLogId
              where dpiuseroperationlogs.timestamp >= '%s' and dpiuseroperationlogs.timestamp < '%s'
              group by user_ip order by count(*) desc limit 5''' % (
    time_str_tz_proc(start_time), time_str_tz_proc(end_time))
    res, sql_res = db_proxy.read_db(sql_str)
    if res != 0:
        param["user_ip_table"] = ()
    else:
        param["user_ip_table"] = sql_res
    # 获取用户操作日志随时间趋势分布
    param["oper_log_time"] = answer["all"]
    # 获取用户登录饼状图数据
    answer["userstatics"] = []
    for user in user_list:
        answer["userstatics"].append([user, tmp_statics_dict[user]])
    # oper_dict = {}
    # for row in answer["userstatics"]:
    #     oper_dict[row[0]] = row[1]
    # param["user_oper_fig"] = oper_dict

    answer["status"] = 1
    # f = open("%s/%s" % (REPORT_GEN_LOG_PATH, statics_file_name), "w")
    # f.write(str(answer))
    # f.close()

    ticks = int(time.time())
    gen_date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ticks))
    db_info = [report_name, gen_date_str, start_time, end_time, freq_type]
    return 0, file_name, statics_file_name, db_info, param


@reportgen_page.route('/reportGenloghandleTest')
@login_required
def mw_report_gen_loghandle_test():
    '''
    test route for log report gen
    '''
    freq = request.args.get('freq', 1, type=int)
    res = log_report_gen_handle(freq)
    return jsonify({'status': 1, "res": res})


def log_report_gen_handle(freq_type, input_start="", input_end=""):
    '''
    log report gen handle
    '''
    logger = set_up_logger()
    res1, syslog_detail, syslog_statics, sys_param_dict = sys_log_report_gen_handle(freq_type, input_start, input_end)
    if res1 != 0:
        return 1
    res2, operlog_detail, operlog_statics, db_info, param_dict = oper_log_report_gen_handle(freq_type, input_start,
                                                                                            input_end)
    if res2 != 0:
        os.system("rm -f /data/report/log/%s" % syslog_detail)
        os.system("rm -f /data/report/log/%s" % syslog_statics)
        return 1

    logger.info(param_dict)
    db_proxy = DbProxy()
    config_db_proxy = DbProxy(CONFIG_DB_NAME)
    if freq_type > MONTH_AUTO_TYPE:
        sql_str = '''select max(id) from nsm_rptloginfo '''
        # sql_str = '''select count(*) from nsm_rptloginfo '''
        res, sql_res = config_db_proxy.read_db(sql_str)
        if res != 0:
            return 1
        if sql_res[0][0] is None:
            id_str = "1"
        else:
            id_str = str(sql_res[0][0] + 1)
        str_index = operlog_detail.find(".csv")
        dst_operlog_detail = operlog_detail[0:str_index] + ("_%s" % (id_str)) + operlog_detail[str_index:]
        str_index = operlog_statics.find("_statics")
        dst_operlog_statics = operlog_statics[0:str_index] + ("_%s" % (id_str)) + operlog_statics[str_index:]
        str_index = syslog_detail.find(".csv")
        dst_syslog_detail = syslog_detail[0:str_index] + ("_%s" % (id_str)) + syslog_detail[str_index:]
        str_index = syslog_statics.find("_statics")
        dst_syslog_statics = syslog_statics[0:str_index] + ("_%s" % (id_str)) + syslog_statics[str_index:]
        os.rename("%s/%s" % (REPORT_GEN_LOG_PATH, operlog_detail), "%s/%s" % (REPORT_GEN_LOG_PATH, dst_operlog_detail))
        # os.rename("%s/%s" % (REPORT_GEN_LOG_PATH, operlog_statics), "%s/%s" % (REPORT_GEN_LOG_PATH, dst_operlog_statics))
        os.rename("%s/%s" % (REPORT_GEN_LOG_PATH, syslog_detail), "%s/%s" % (REPORT_GEN_LOG_PATH, dst_syslog_detail))
        # os.rename("%s/%s" % (REPORT_GEN_LOG_PATH, syslog_statics), "%s/%s" % (REPORT_GEN_LOG_PATH, dst_syslog_statics))
    else:
        dst_operlog_detail = operlog_detail
        dst_operlog_statics = operlog_statics
        dst_syslog_detail = syslog_detail
        dst_syslog_statics = syslog_statics

    paragram_dict = sys_param_dict.copy()
    paragram_dict.update(param_dict)
    if input_start or input_end:
        paragram_dict["input_param"] = {"start_time": input_start, "end_time": input_end}
    else:
        start_time, end_time = get_start_end_time(freq_type)
        paragram_dict["input_param"] = {"start_time": start_time, "end_time": end_time}
    # 根据获取到的数据生成报告,并存储到对应的文件中
    # global REPORT_TYPE
    REPORT_TYPE = "log"
    try:
        proto_report = ReportBuild(REPORT_TYPE, freq_type, **paragram_dict)
        proto_report.run()
    except:
        logger.error("log_report build error..")
        logger.error(traceback.format_exc())

    report_name_ch = base64.b64decode(db_info[0])
    os.rename('/data/report/log/log_report.pdf', '/data/report/log/' + report_name_ch + ".pdf")

    # 将操作日志和系统日志详情文件形成一个zip压缩包
    zip_file = report_name_ch + ".zip"
    zip_path_file = "/data/" + zip_file
    try:
        ziphandle = zipfile.ZipFile(zip_path_file, 'w', zipfile.ZIP_DEFLATED)
        dirpath = "/data/report/log/"
        ziphandle.write(os.path.join(dirpath, dst_operlog_detail), dst_operlog_detail)
        ziphandle.write(os.path.join(dirpath, dst_syslog_detail), dst_syslog_detail)
        ziphandle.close()
        cmd = "mv " + zip_path_file + " " + dirpath
        os.system(cmd)
    except:
        logger.error("zip log file error...")
        logger.error(traceback.format_exc())
    zip_file = dst_operlog_statics + '.zip'
    sql_str = '''insert into nsm_rptloginfo (id, report_name, report_time, report_start_time, report_stop_time, report_freq,
              operlog_raw_file, operlog_statics_file, syslog_raw_file, syslog_statics_file ) values(default, '%s','%s','%s','%s', %d,'%s', '%s','%s', '%s')''' \
              % (db_info[0], db_info[1], db_info[2], db_info[3], db_info[4], zip_file, dst_operlog_statics,
                 dst_syslog_detail, dst_syslog_statics)
    config_db_proxy.write_db(sql_str)
    return 0


@reportgen_page.route('/reportGenLogManual', methods=['GET', 'POST'])
@login_required
def report_log_manual():
    '''
    test route for alarm report gen
    '''
    if request.method == "GET":
        start_time = request.args.get('starttime')
        end_time = request.args.get('endtime')
        loginuser = request.args.get('loginuser')

    if request.method == "POST":
        post_data = request.get_json()
        start_time = post_data['starttime']
        end_time = post_data['endtime']
        loginuser = post_data['loginuser']
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u'手动生成日志报告'
    msg['Result'] = '1'

    if start_time == "" or end_time == "":
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 0})
    freq_type = get_freq_type(start_time, end_time)
    if 1 == check_time_for_manual_report(start_time, end_time):
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 0})
    res = log_report_gen_handle(freq_type, start_time, end_time)
    if res != 0:
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 0})
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@reportgen_page.route('/reportGenLogSetmode', methods=['GET', 'POST'])
@login_required
def mw_report_gen_log_setmode():
    '''
    set log report gen mode
    '''
    if request.method == 'GET':
        freq = request.args.get('freq', 1, type=int)
    else:
        post_data = request.get_json()
        freq = int(post_data['freq'])
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select * from nsm_rptlogmode"
    # sql_res = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
    _, sql_res = db_proxy.read_db(sql_str)
    if sql_res is None or sql_res == []:
        return jsonify({'status': 0})
    if sql_res[0][0] != freq:
        os.system("sed -ir '/.*rptlog_proc.pyc.*/d' %s" % CROND_PATH)
        if freq == 1:
            os.system("echo \"10 0 * * * python %s/rptlog_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        elif freq == 2:
            os.system("echo \"10 0 * * 1  python %s/rptlog_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        elif freq == 3:
            os.system("echo \"10 0 1 * *  python %s/rptlog_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        else:
            pass
        os.system("crontab -c %s %s" % (CROND_CONF, CROND_PATH))
        conf_save_flag_set()
        sql_str = "update nsm_rptlogmode set flag = %d" % freq
        # new_send_cmd(TYPE_APP_SOCKET, sql_str, 2)
        db_proxy.write_db(sql_str)
    return jsonify({'status': 1})


@reportgen_page.route('/reportGenLogInfo', methods=['GET', 'PUT', 'DELETE'])
@login_required
def mw_report_gen_log_info():
    '''
    get log report info for UI
    '''
    msg = {}
    userip = get_oper_ip_info(request)
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        sql_str = "select * from nsm_rptloginfo order by id desc limit 10 offset %d" % ((page - 1) * 10)
        res1, rptlog_info = db_proxy.read_db(sql_str)
        if res1 != 0:
            return jsonify({'status': 0, 'rows': [], 'total': 0, 'page': page})
        rptlog_info = list(rptlog_info)
        rows = []
        tmp_report_path = "/data/report/log/"
        for elem in rptlog_info:
            elem = list(elem)
            elem[1] = base64.b64decode(elem[1])
            if os.path.exists(tmp_report_path + str(elem[1]) + ".pdf"):
                elem.append(1)
            else:
                elem.append(0)
            rows.append(elem)
        sql_str = "select count(*) from nsm_rptloginfo"
        res2, sql_res = db_proxy.read_db(sql_str)
        if res2 != 0:
            return jsonify({'status': 0, 'rows': [], 'total': 0, 'page': page})
        num = sql_res[0][0]
        return jsonify({'status': 1, 'rows': rows, 'total': num, 'page': page})

    elif request.method == 'PUT':
        json_data = request.get_json()
        report_id = json_data.get('id', '')
        new_name = json_data.get('report_name', '')
        if len(new_name.encode("utf-8")) > 128:
            return jsonify({"status": 0, "msg": "报告名称不能超过128个字节"})
        loginuser = json_data.get('loginuser', '')
        sql_str = "select * from nsm_rptloginfo where id=%d" % int(report_id)
        res, elem = db_proxy.read_db(sql_str)
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'
        msg['Operate'] = u'编辑日志报告名称'
        msg['Result'] = '1'
        if res != 0:
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({"status": 0})
        new_name_base64 = base64.b64encode(new_name)
        if elem[0][1] == new_name_base64:
            return jsonify({"status": 1})
        try:
            update_str = "update nsm_rptloginfo set report_name=\"%s\" where id=%d" % (new_name_base64, int(report_id))
            res = db_proxy.write_db(update_str)
            if res != 0:
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({"status": 0})
            old_file_name = base64.b64decode(elem[0][1])
            os.rename(('/data/report/log/' + old_file_name + '.zip').encode('utf-8'),
                      ('/data/report/log/' + new_name + ".zip").encode('utf-8'))
            os.rename(('/data/report/log/' + old_file_name + '.pdf').encode('utf-8'),
                      ('/data/report/log/' + new_name + ".pdf").encode('utf-8'))
        except:
            current_app.logger.error(traceback.format_exc())
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({"status": 0})
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({"status": 1})

    elif request.method == 'DELETE':
        json_data = request.get_json()
        report_id_list = json_data.get('id_list', '')
        report_id_list = report_id_list.split(",")
        loginuser = json_data.get('loginuser', '')
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'
        msg['Operate'] = u'删除日志报告'
        msg['Result'] = '1'
        for report_id in report_id_list:
            try:
                sql_str = "select report_name from nsm_rptloginfo where id=%d" % int(report_id)
                res, rows = db_proxy.read_db(sql_str)
                if res == 0:
                    report_name = base64.b64decode(rows[0][0])
                    zip_path = "/data/report/log/" + report_name + ".zip"
                    if os.path.exists(zip_path):
                        os.remove(zip_path)
                    pdf_path = "/data/report/log/" + report_name + ".pdf"
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)
            except:
                current_app.logger.error("report_file not found")
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({"status": 0})
            del_str = "delete from nsm_rptloginfo where id=%d" % int(report_id)
            res = db_proxy.write_db(del_str)
            if res != 0:
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({"status": 0})
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({"status": 1})
    else:
        return jsonify({"status": 0})


@reportgen_page.route('/reportGenSyslogStaticsRes')
@login_required
def mw_report_gen_syslog_statics_res():
    '''
    get sys log report statics info
    '''
    id_num = request.args.get('id', 0, type=int)
    sql_str = "select * from nsm_rptloginfo where id = %d" % (id_num)
    db_proxy = DbProxy(CONFIG_DB_NAME)
    res, sql_res = db_proxy.read_db(sql_str)
    if res != 0:
        return jsonify({'status': 0})

    report_statics_file = sql_res[0][9]
    if os.path.exists("%s/%s" % (REPORT_GEN_LOG_PATH, report_statics_file)) == True:
        syslog_fd = open("%s/%s" % (REPORT_GEN_LOG_PATH, report_statics_file), "r")
        val_str = syslog_fd.read()
        statics_info = eval(val_str)
        syslog_fd.close()
    else:
        statics_info = {'status': 0}
    return jsonify(statics_info)


@reportgen_page.route('/reportGenOperlogStaticsRes')
@login_required
def mw_report_gen_operlog_statics_res():
    '''
    get oper log report statics info
    '''
    id_num = request.args.get('id', 0, type=int)
    sql_str = "select * from nsm_rptloginfo where id = %d" % (id_num)
    db_proxy = DbProxy(CONFIG_DB_NAME)
    res, sql_res = db_proxy.read_db(sql_str)
    if res != 0:
        return jsonify({'status': 0})
    report_statics_file = sql_res[0][7]
    if os.path.exists("%s/%s" % (REPORT_GEN_LOG_PATH, report_statics_file)) == True:
        operlog_fd = open("%s/%s" % (REPORT_GEN_LOG_PATH, report_statics_file), "r")
        val_str = operlog_fd.read()
        statics_info = eval(val_str)
        operlog_fd.close()
    else:
        statics_info = {'status': 0}
    return jsonify(statics_info)


@reportgen_page.route('/reportGenLogGetmode')
@login_required
def mw_report_gen_log_getmode():
    '''
    get log report gen mode
    '''
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select * from nsm_rptlogmode"
    # sql_res = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
    _, sql_res = db_proxy.read_db(sql_str)
    if sql_res is None or sql_res == []:
        return jsonify({'status': 0})
    else:
        return jsonify({'status': 1, "freq": sql_res[0][0]})


@reportgen_page.route('/RptlogdetailDownload/<report_id>', methods=['POST', 'GET'])
@login_required
def rpt_log_detail_download(report_id):
    '''
    download log report detail info
    '''
    curdir = REPORT_GEN_LOG_PATH
    db_proxy = DbProxy(CONFIG_DB_NAME)
    msg = {}
    userip = get_oper_ip_info(request)
    loginuser = request.args.get('loginuser')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u'下载日志报告详情'
    msg['Result'] = '0'
    try:
        sql_str = "select report_name from nsm_rptloginfo where id=%d" % int(report_id)
        res, rows = db_proxy.read_db(sql_str)
        if res != 0:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({"status": 0})
        file_name = base64.b64decode(rows[0][0]) + '.zip'
        send_log_db(MODULE_OPERATION, msg)
        return send_from_directory(curdir, file_name, as_attachment=True)
    except:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        current_app.logger.error(traceback.format_exc())
        return jsonify({"status": 0})


@reportgen_page.route('/RptlogDownload/<report_id>', methods=['POST', 'GET'])
@login_required
def rpt_log_download(report_id):
    '''
    download log report detail info
    '''
    curdir = REPORT_GEN_LOG_PATH
    db_proxy = DbProxy(CONFIG_DB_NAME)
    msg = {}
    userip = get_oper_ip_info(request)
    loginuser = request.args.get('loginuser')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u'下载日志报告'
    msg['Result'] = '0'
    try:
        sql_str = "select report_name from nsm_rptloginfo where id=%d" % int(report_id)
        res, rows = db_proxy.read_db(sql_str)
        if res != 0:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({"status": 0})
        file_name = base64.b64decode(rows[0][0]) + '.pdf'
        send_log_db(MODULE_OPERATION, msg)
        return send_from_directory(curdir, file_name, as_attachment=True)
    except:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        current_app.logger.error(traceback.format_exc())
        return jsonify({"status": 0})


def assset_setRestrictInIptables(ipinfo, ip_type):
    ip_list = ipinfo.split(',')
    for ip in ip_list:
        # 判断获取输入的ip类型(单个ip，范围，掩码)
        type = assets_getiptype(ip)
        if type == 0:  # ip地址
            ret = assets_check_ip(ip, ip_type)
            if ret == 4 or ret == 6:
                return ret
        elif type == 1:  # ip地址范围
            ip_temp = ip.split('-')
            for i in range(2):
                ret = assets_check_ip(ip_temp[i], ip_type)
                if ret == 4 or ret == 6:
                    return ret
        else:  # ip地址掩码
            ret = assets_check_ip(ip.split('/')[0], ip_type)
            if ret == 4 or ret == 6:
                return ret


# 判断输入的是不是合法的ip,不合法返回
def assets_check_ip(ip, ip_type):
    if ip_type == 4:
        try:
            ipaddress.IPv4Address(unicode(ip))
        except:
            return 4
    if ip_type == 6:
        try:
            ipaddress.IPv6Address(unicode(ip))
        except:
            return 6


# 获取输入的ip类型
def assets_getiptype(ip):
    # 输入的是一个范围
    if ip.find('-') >= 0:
        return 1
    # 输入的是ip地址掩码
    elif ip.find('/') >= 0:
        return 2
    # 输入的是ip地址
    return 0


# 获取符合输入条件的ipv4和ipv6的ip列表
def search_assets_data(ipinput,accessIpvx,sql_tmp_res):
    if ipinput == 'Ipv6':
        if accessIpvx:
            ipv6_list = []
            ipv6_temp_num = 0
            # 数据库中is_live的ip
            for rows in sql_tmp_res:
                ip_live = rows[0]
                if ip_live.find(":") >= 0 and ip_live != "":  # ipv6的地址
                    for ipv6 in accessIpvx.split(","):
                        # 输入的ip类型（范围，IP段，单个ip地址）
                        ip_result = assets_getiptype(ipv6)
                        # 输入的是ip范围且在范围内
                        if ip_result == 1 and int(ipaddress.IPv6Address(unicode(ipv6.split("-")[0]))) <= int(
                                ipaddress.IPv6Address(unicode(ip_live))) <= int(ipaddress.IPv6Address(unicode(ipv6.split("-")[1]))):
                            ipv6_list.append(ip_live)
                            ipv6_temp_num += 1
                            break
                        # 输入的是ip段192.168.81.0/16且在范围内
                        elif ip_result == 2 and ipaddress.IPv6Address(unicode(ip_live)) in ipaddress.IPv6Network(ipv6):
                            ipv6_list.append(ip_live)
                            ipv6_temp_num += 1
                            break
                        # 输入的是单个IP地址
                        elif ip_result == 0 and ip_live == ipv6:
                            ipv6_list.append(ip_live)
                            ipv6_temp_num += 1
                            break
            return ipv6_list
        else:
            ipv6_list = []
            # 数据库中is_live的ip
            for rows in sql_tmp_res:
                ip_live = rows[0]
                if ip_live.find(":") >= 0:
                    ipv6_list.append(ip_live)
            return ipv6_list
    elif ipinput == 'Ipv4':
        if accessIpvx:
            ipv4_list = []
            # 数据库中is_live的ip
            for rows in sql_tmp_res:
                ip_live = rows[0]
                if ip_live.find(":") == -1 and ip_live != "":  # ipv4的地址
                    for ipv4 in accessIpvx.split(","):
                        # 输入的ip类型（范围，IP段，单个ip地址）
                        ip_result = assets_getiptype(ipv4)
                        # 输入的是ip范围且在范围内
                        if ip_result == 1 and int(ipaddress.IPv4Address(unicode(ipv4.split("-")[0]))) <= int(
                                ipaddress.IPv4Address(unicode(ip_live))) <= int(
                                ipaddress.IPv4Address(unicode(ipv4.split("-")[1]))):
                            ipv4_list.append(ip_live)
                            break
                        # 输入的是ip段192.168.81.0/16且在范围内
                        elif ip_result == 2 and ipaddress.IPv4Address(unicode(ip_live)) in ipaddress.IPv4Network(ipv4):
                            ipv4_list.append(ip_live)
                            break
                        # 输入的是单个IP地址
                        elif ip_result == 0 and ip_live == ipv4:
                            ipv4_list.append(ip_live)
                            break
            return ipv4_list
        else:
            ipv4_list = []
            # 数据库中is_live的ip
            for rows in sql_tmp_res:
                ip_live = rows[0]
                if ip_live.find(":") == -1:
                    ipv4_list.append(ip_live)
            return ipv4_list


# 获取资产报告生成频率
@reportgen_page.route('/reportGenAssetsGetmode')
@login_required
def mw_report_gen_assets_getmode():
    '''
    get assets report gen mode
    '''
    sql_str = "select * from nsm_rptassetsmode"
    db_proxy = DbProxy(CONFIG_DB_NAME)
    _, sql_res = db_proxy.read_db(sql_str)
    if sql_res is None or sql_res == []:
        return jsonify({'status': 0})
    else:
        return jsonify({'status': 1, "freq": sql_res[0][0]})


# 自动定期生成资产报告
@reportgen_page.route('/reportGenAssetsSetmode', methods=['GET', 'POST'])
@login_required
def mw_report_gen_assets_setmode():
    '''
    set assets report gen mode
    '''
    if request.method == 'POST':
        post_data = request.get_json()
        freq = int(post_data['freq'])
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select * from nsm_rptassetsmode"
    _, sql_res = db_proxy.read_db(sql_str)
    if sql_res is None or sql_res == []:
        return jsonify({'status': 0})

    if sql_res[0][0] != freq:
        os.system("sed -ir '/.*rptassets_proc.pyc.*/d' %s" % CROND_PATH)
        if freq == 1:  # 按天执行
            os.system("echo \"15 0 * * * python %s/rptassets_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        elif freq == 2:  # 按周执行
            os.system("echo \"15 0 * * 1 python %s/rptassets_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        elif freq == 3:  # 按月执行
            os.system("echo \"15 0 1 * *  python %s/rptassets_proc.pyc %d\" \
                      >> %s" % (APP_PY_PATH, freq, CROND_PATH))
        else:
            pass
        os.system("crontab -c %s %s" % (CROND_CONF, CROND_PATH))
        conf_save_flag_set()
        sql_str = "update nsm_rptassetsmode set flag=%d" % freq
        db_proxy.write_db(sql_str)
    return jsonify({'status': 1})


# 自定义生成资产报告
@reportgen_page.route('/reportGenAssetsManual', methods=['GET', 'POST'])
@login_required
def mw_report_gen_assets_manual():
    '''
    route for assets manual report gen
    '''
    if request.method == 'POST':
        post_data = request.get_json()
        accessIpv4 = post_data["ipv4"]
        accessIpv6 = post_data["ipv6"]
        report_level = int(post_data["report_level"])
        loginuser = post_data["loginuser"]
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u'手动生成资产报告'
    msg['Result'] = '1'

    # 同时输入ipv4和ipv6
    if accessIpv4 and accessIpv6:
        status = assset_setRestrictInIptables(accessIpv4, 4)
        if status == 4:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0, 'msg': u'请输入正确的IPV4地址'})
        status = assset_setRestrictInIptables(accessIpv6, 6)
        if status == 6:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0, 'msg': u'请输入正确的IPV6地址'})
    elif accessIpv4:
        status = assset_setRestrictInIptables(accessIpv4, 4)
        if status == 4:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0, 'msg': u'请输入正确的IPV4地址'})
    elif accessIpv6:
        status = assset_setRestrictInIptables(accessIpv6, 6)
        if status == 6:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0, 'msg': u'请输入正确的IPV6地址'})
    if report_level == 1:  # 包含二层设备(设备ip可为空)
        sql_level = ""
    else:  # 不包含二层设备（设备ip不可为空）
        sql_level = " and ip !='' "
    paragram_dict = {
                     "input_param": {"dev_ip4": accessIpv4, "dev_ip6": accessIpv6},
                     "sql_level": sql_level,"report_level":report_level
                     }
    # 设置手动生成报告情况下默认freq_type = 4
    freq_type = 4
    try:
        assets_origin_report_gen_handle(freq_type, **paragram_dict)
    except:
        current_app.logger.error(traceback.format_exc())
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


def get_dev_mapdict():
    db = DbProxy(CONFIG_DB_NAME)
    cmd_str = "select type_id,device_name from dev_type"
    _, rows = db.read_db(cmd_str)
    dev_map_dict = {}
    if len(rows) > 0:
        dev_map_dict = dict(rows)
    dev_map_dict.update({0:"未知"})
    return dev_map_dict


# 处理原始数据并生成资产报告最终数据
def assets_origin_report_gen_handle(freq_type, **kwargs):
    '''
    assets report gen handle
    '''
    logger = set_up_logger()
    if not kwargs:
        # 定期生成报告的参数
        accessIpv4 = ""
        accessIpv6 = ""
        sql_level = ""
    else:
        # 自定义生成报告的参数
        accessIpv4 = kwargs["input_param"]["dev_ip4"]
        accessIpv6 = kwargs["input_param"]["dev_ip6"]
        sql_level = kwargs["sql_level"]
    # 是否包含二层设备
    second_floor = str(kwargs["report_level"])
    # 获取所有符合条件的ip列表
    sql_str = "select ip from topdevice"
    db_proxy = DbProxy(CONFIG_DB_NAME)
    res, sql_res = db_proxy.read_db(sql_str)
    dev_ipv4_list = search_assets_data("Ipv4", accessIpv4, sql_res)
    dev_ipv6_list = search_assets_data("Ipv6", accessIpv6, sql_res)
    cur_ip_list = dev_ipv4_list + dev_ipv6_list
    cur_ip_list.append('')
    ip_list = str(cur_ip_list).replace("[", "(").replace("]", ")").strip()
    dev_live_sql = "select is_live, count(*) from topdevice where ip in %s" % ip_list + str(
        sql_level) + " group by is_live "
    dev_type_sql = "select dev_type, count(*) from topdevice where ip in %s" % ip_list + str(
        sql_level) + " group by dev_type "
    dev_status_sql = "select is_unknown, count(*) from topdevice where ip in %s" % ip_list + str(
        sql_level) + " group by is_unknown "
    mode_live_res, sql_live_res = db_proxy.read_db(dev_live_sql)
    mode_type_res, sql_type_res = db_proxy.read_db(dev_type_sql)
    mode_status_res, sql_status_res = db_proxy.read_db(dev_status_sql)
    dev_live_data = {}  # 设备在线数据
    dev_status_data = {}  # 设备身份数据
    dev_type_data = {}  # 设备类型数据

    if mode_live_res == 0:
        is_live_list = []
        for row in sql_live_res:
            detail_live = {}
            detail_live[str(row[0])] = (str(row[1]))
            is_live_list.append(detail_live)
        for i in is_live_list:
            dev_live_data.update(i)
    else:
        return jsonify({'status': 0})

    if mode_status_res == 0:
        dev_status_list = []
        for row in sql_status_res:
            detail_status = {}
            detail_status[str(row[0])] = (str(row[1]))
            dev_status_list.append(detail_status)
        for i in dev_status_list:
            dev_status_data.update(i)
    else:
        return jsonify({'status': 0})

    map_dict = get_dev_mapdict()
    logger.info(map_dict)

    if mode_type_res == 0:
        for row in sql_type_res:
            detail_type = {}
            type_key = base64.b64encode(map_dict[row[0]])
            detail_type[type_key] = (str(row[1]))
            dev_type_data.update(detail_type)
    else:
        return jsonify({'status': 0})

    if freq_type == DAY_AUTO_TYPE:
        en_rpt_type_str = "_Daily_Report"
        ch_rpt_type_str = "_每日报表_"
    elif freq_type == WEEK_AUTO_TYPE:
        en_rpt_type_str = "_Weekly_Report"
        ch_rpt_type_str = "_每周报表_"
    elif freq_type == MONTH_AUTO_TYPE:
        en_rpt_type_str = "_Monthly_Report"
        ch_rpt_type_str = "_每月报表_"
    else:
        en_rpt_type_str = "_Manual_Report"
        ch_rpt_type_str = "_自定义报表_"
    # 显示名称
    sql_str = "select max(id) from nsm_rptassetsinfo"
    res, sql_res = db_proxy.read_db(sql_str)
    if res != 0:
        return 0
    if sql_res[0][0] == None:
        id_str = "1"
    else:
        id_str = str(sql_res[0][0] + 1)

    ticks = time.time()
    cur_time = str(time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(ticks)))
    if freq_type > MONTH_AUTO_TYPE:
        report_name = base64.b64encode("资产报告" + ch_rpt_type_str + cur_time + "_%s" % id_str)
        file_name = ("Assets" + en_rpt_type_str + cur_time + "_%s" % id_str + ".csv")
        statics_file_name = ("Assets" + en_rpt_type_str + cur_time + "_%s" % id_str)
    else:
        report_name = base64.b64encode("资产报告" + ch_rpt_type_str + cur_time)
        file_name = ("Assets" + en_rpt_type_str + cur_time + ".csv")
        statics_file_name = ("Assets" + en_rpt_type_str + cur_time)

    writer = UnicodeWriter(open(REPORT_GEN_ASSETS_PATH + "/" + file_name, "wb"))
    title = [U"设备名", U"设备IP", U"设备MAC", U"设备类型", U"在线状态", U"设备身份"]
    writer.writerow(title)

    # 生成详细信息写入csv表中
    ip_csv_list = dev_ipv4_list + dev_ipv6_list
    sql_str = "select name,ip,mac,dev_type,is_live,is_unknown from topdevice where 1=1"
    sql_str = sql_str + " and ip in %s" % ip_list + str(sql_level)
    res, sql_res = db_proxy.read_db(sql_str)

    for i in range(0, len(sql_res)):
        src_dev_name = sql_res[i][0]
        src_ip_str = trans_db_ipmac_to_local(sql_res[i][1])
        src_mac_str = trans_db_ipmac_to_local(sql_res[i][2])
        src_dev_type = sql_res[i][3]
        src_is_live = sql_res[i][4]
        src_is_unknown = sql_res[i][5]

        # 转换显示名到cvs中
        src_dev_type = map_dict[src_dev_type]
        # if src_dev_type == 0:
        #     src_dev_type = u"未知"
        # elif src_dev_type == 1:
        #     src_dev_type = u"PC"
        # elif src_dev_type == 2:
        #     src_dev_type = u"工程师站PC"
        # elif src_dev_type == 3:
        #     src_dev_type = u"操作员PC"
        # elif src_dev_type == 4:
        #     src_dev_type = u"PLC"
        # elif src_dev_type == 5:
        #     src_dev_type = u"RTU"
        # elif src_dev_type == 6:
        #     src_dev_type = u"HMI"
        # elif src_dev_type == 7:
        #     src_dev_type = u"网络设备"
        if src_is_live == 0:
            src_is_live = u"离线"
        elif src_is_live == 1:
            src_is_live = u"在线"
        if src_is_unknown == 0:
            src_is_unknown = u"正常接入"
        elif src_is_unknown == 1:
            src_is_unknown = u"非法接入"

        trans_res = [src_dev_name.decode("UTF-8"), get_not_null_name(src_ip_str),
                     get_not_null_name(src_mac_str), src_dev_type, src_is_live, src_is_unknown]
        writer.writerow(trans_res)

    # 根据获取到的数据生成报告,并存储到对应的文件中
    REPORT_TYPE = "assets"
    try:
        kwargs["dev_live_info"] = dev_live_data
        kwargs["dev_type_info"] = dev_type_data
        logger.info(dev_type_data)
        kwargs["dev_status_info"] = dev_status_data
        kwargs["input_param"] = {"dev_ip4": accessIpv4, "dev_ip6": accessIpv6, "second_floor": second_floor}
        proto_report = ReportBuild(REPORT_TYPE, freq_type, **kwargs)
        proto_report.run()
    except:
        logger.error("assets_report build error..")
        logger.error(traceback.format_exc())
    report_name_ch = base64.b64decode(report_name)
    os.rename('/data/report/assets/assets_report.pdf', '/data/report/assets/' + report_name_ch + ".pdf")
    os.rename('/data/report/assets/' + file_name, '/data/report/assets/' + report_name_ch + ".csv")

    # 将生成的报告相关信息存入数据库中
    ticks = int(time.time())
    gen_date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ticks))
    sql_str = '''insert into nsm_rptassetsinfo (id, report_name, report_time, report_freq, report_raw_file, report_statics_file)
                 values(default, '%s','%s', %d,'%s', '%s')''' % (
        report_name, gen_date_str, freq_type, file_name, statics_file_name)
    db_proxy = DbProxy(CONFIG_DB_NAME)
    db_proxy.write_db(sql_str)
    return jsonify({'status': 1})


# 下载资产报告详细信息
@reportgen_page.route('/RptassetsdetailDownload/<report_id>', methods=['POST', 'GET'])
@login_required
def rpt_assets_detail_download(report_id):
    '''
    download assets report detail info
    '''
    curdir = REPORT_GEN_ASSETS_PATH
    db_proxy = DbProxy(CONFIG_DB_NAME)
    msg = {}
    userip = get_oper_ip_info(request)
    loginuser = request.args.get('loginuser')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u'下载资产报告详情'
    msg['Result'] = '0'
    try:
        sql_str = "select report_name from nsm_rptassetsinfo where id=%d" % int(report_id)
        res, rows = db_proxy.read_db(sql_str)
        if res != 0:
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({"status": 0})
        file_name = base64.b64decode(rows[0][0]) + '.csv'
        send_log_db(MODULE_OPERATION, msg)
        return send_from_directory(curdir, file_name, as_attachment=True)
    except:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        current_app.logger.error(traceback.format_exc())
        return jsonify({"status": 1})


# 下载资产报告
@reportgen_page.route('/RptassetsDownload/<report_id>', methods=['POST', 'GET'])
@login_required
def rpt_assets_download(report_id):
    '''
    download assets report detail info
    '''
    curdir = REPORT_GEN_ASSETS_PATH
    db_proxy = DbProxy(CONFIG_DB_NAME)
    msg = {}
    userip = get_oper_ip_info(request)
    loginuser = request.args.get('loginuser')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u'下载资产报告'
    msg['Result'] = '0'
    try:
        sql_str = "select report_name from nsm_rptassetsinfo where id=%d" % int(report_id)
        res, rows = db_proxy.read_db(sql_str)
        if res != 0:
            return jsonify({"status": 0})
        file_name = base64.b64decode(rows[0][0]) + '.pdf'
        send_log_db(MODULE_OPERATION, msg)
        return send_from_directory(curdir, file_name, as_attachment=True)
    except:
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        current_app.logger.error(traceback.format_exc())
        return jsonify({"status": 0})


# 修改资产报告名称，删除资产报告
@reportgen_page.route('/reportGenAssetsInfo', methods=['GET', 'PUT', 'DELETE'])
@login_required
def mw_assetsinfo_res():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    msg = {}
    userip = get_oper_ip_info(request)
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)

        sql_str = "select * from nsm_rptassetsinfo order by id desc limit 10 offset %d" % ((page - 1) * 10)
        res1, rptassets_info = db_proxy.read_db(sql_str)
        rows = []
        tmp_report_path = "/data/report/assets/"
        rptassets_info = list(rptassets_info)
        for elem in rptassets_info:
            elem = list(elem)
            elem[1] = base64.b64decode(elem[1])
            if os.path.exists(tmp_report_path + str(elem[1]) + ".pdf"):
                elem.append(1)
            else:
                elem.append(0)
            rows.append(elem)
        sql_str = "select count(*) from nsm_rptassetsinfo"
        res2, sql_res = db_proxy.read_db(sql_str)
        if res1 == 0 and res2 == 0:
            num = sql_res[0][0]
            return jsonify({'status': 1, 'rows': rows, 'total': num, 'page': page})
        else:
            return jsonify({'status': 0, 'rows': [], 'total': 0, 'page': page})

    elif request.method == 'PUT':
        json_data = request.get_json()
        report_id = json_data.get('id', '')
        new_name = json_data.get('assetsname', '')
        if len(new_name.encode("utf-8")) > 128:
            return jsonify({"status": 0, "msg": "报告名称不能超过128个字节"})
        loginuser = json_data.get('loginuser', '')
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'
        msg['Operate'] = u'编辑资产报告名称'
        msg['Result'] = '1'
        sql_str = "select * from nsm_rptassetsinfo where id=%d" % int(report_id)
        res, elem = db_proxy.read_db(sql_str)
        if res != 0:
            current_app.logger.error("res, elem = db_proxy.read_db(sql_str) == 0")
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({"status": 0})
        new_name_base64 = base64.b64encode(new_name)
        if elem[0][1] == new_name_base64:
            return jsonify({"status": 1})
        try:
            update_str = "update nsm_rptassetsinfo set report_name=\"%s\" where id=%d" % (
                new_name_base64, int(report_id))
            res = db_proxy.write_db(update_str)
            if res != 0:
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({"status": 0})
            old_file_name = base64.b64decode(elem[0][1])
            os.rename(('/data/report/assets/' + old_file_name + '.csv').encode('utf-8'),
                      ('/data/report/assets/' + new_name + '.csv').encode('utf-8'))
            os.rename(('/data/report/assets/' + old_file_name + '.pdf').encode('utf-8'),
                      ('/data/report/assets/' + new_name + '.pdf').encode('utf-8'))
        except:
            current_app.logger.error(traceback.format_exc())
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({"status": 0})
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({"status": 1})

    elif request.method == 'DELETE':
        json_data = request.get_json()
        report_id_list = json_data.get('id', "")
        report_id_list = report_id_list.split(",")
        loginuser = json_data.get('loginuser', '')
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        msg['ManageStyle'] = 'WEB'
        msg['Operate'] = u'删除资产报告'
        msg['Result'] = '1'
        for report_id in report_id_list:
            try:
                sql_str = "select report_name from nsm_rptassetsinfo where id=%d" % int(report_id)
                res, rows = db_proxy.read_db(sql_str)
                if res == 0:
                    # 删除文件信息
                    report_name = base64.b64decode(rows[0][0])
                    os.remove("/data/report/assets/" + report_name + ".csv")
                    pdf_path = "/data/report/assets/" + report_name + ".pdf"
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)
            except:
                current_app.logger.error("report_file not found")
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({"status": 0})
            # 删除数据库记录信息
            del_str = "delete from nsm_rptassetsinfo where id=%d" % int(report_id)
            res = db_proxy.write_db(del_str)
            if res != 0:
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({"status": 0})
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({"status": 1})

    else:
        return jsonify({"status": 0})
