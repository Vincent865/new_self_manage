import subprocess
import time
import commands
import socket
import ipaddress
import struct

IPMAC_LIST_PATH = "/data/rules/ipmac-dpi/ipmacbinding.rules"
BLACK_LIST_PATH = "/data/rules/signature-dpi/signature.rules"
WHITE_LIST_PATH = "/data/rules/whitelist-dpi/whitelist.rules"
DPI_YAML = "/data/configuration/southwest_engines/dpi.yaml"
MAC_FILTER_PATH = "/data/rules/ipmac-dpi/macfilter.rules"

PROTOCAL_LIST = (
'dcerpcudp', 'modbus', 'dcerpc', 'dnp3', 'iec104', 'mms', 'opcua_tcp', 'ENIP-TCP', 'snmp', 'ENIP-UDP', 's7', 'ENIP-IO',
'hexagon', 'goose', 'sv', 'pnrtdcp', 'oracle', 'ftp', 'focas', 'sip', 's7plus')


#fixed bug KEYS-274
'''
PROTOCAL_LIST = (
'dcerpcudp', 'modbus', 'dcerpc', 'dnp3', 'iec104', 'mms', 'opcua_tcp', 'ENIP-TCP', 'snmp', 'ENIP-UDP', 's7', 'ENIP-IO',
'hexagon', 'goose', 'sv', 'pnrtdcp', 'telnet', 'ssh', 'https', 'http', 'oracle', 'ftp', 'focas', 'sip', 's7plus')
'''


def get_address_count(addr_list):
    strlen = len(addr_list)
    len_comma = addr_list.count(',')
    if strlen == 0 and len_comma == 0:
        return 0
    elif strlen > 0 and len_comma == 0:
        return 1
    elif strlen > 0 and len_comma > 0:
        return len_comma + 1


def write_default_rules(file_handle, ip_list, mac_list, run_mode):
    if ip_list == "" and mac_list == "":
        write_default_rules_any(file_handle, run_mode)
    else:
        write_default_rules_device(file_handle, ip_list, mac_list, run_mode)


def write_default_rules_any(file_handle, run_mode):
    sid = 1
    mode_action = {'ids': 'alert', 'ips': 'drop'}
    for proto in PROTOCAL_LIST:
        msg = 'alert '
        content = ''
        if proto == 'dcerpcudp':
            msg += 'profinetio'
            content += "profinetio.whitelist"
        elif proto == 'dcerpc':
            msg += 'opcda'
            content += "opcda.whitelist"
        elif proto == 'https':
            proto = 'tls'
            msg += 'tls'
            content += "tls.whitelist"
        elif proto == 'goose' or proto == 'sv' or proto == 'pnrtdcp':
            msg += proto
            content += proto
            content += ".L2whitelist"
        else:
            msg += proto
            content += proto + ".whitelist"
        
        msg += ', match all'
        format1 = "%s %s any any -> any any (msg:\"%s \"; %s:\"\"; policy:1; sid:%s; rev:1;)\n" %\
                  (mode_action[run_mode], proto, msg, content, str(sid))
        file_handle.write(format1)
        sid += 1


def write_default_rules_device(file_handle, ip_list, mac_list, run_mode):
    sid = 400000
    mode_action = {'ids': 'alert', 'ips': 'drop'}
    for proto in PROTOCAL_LIST:
        msg = 'alert '
        content = ''
        if proto == 'dcerpcudp':
            msg += 'profinetio'
            content += "profinetio.whitelist"
        elif proto == 'dcerpc':
            msg += 'opcda'
            content += "opcda.whitelist"
        elif proto == 'https':
            proto = 'tls'
            msg += 'tls'
            content += "tls.whitelist"
        elif proto == 'goose' or proto == 'sv' or proto == 'pnrtdcp':
            msg += proto
            content += proto
            content += ".L2whitelist"
        else:
            msg += proto
            content += proto + ".whitelist"
        msg += ', match all'
        format1 = "alert %s [%s] any -> [%s] any (msg:\"%s \"; %s:\"\"; policy:1; sid:%s; rev:1;)\n"
        if proto == 'goose' or proto == 'sv' or proto == 'pnrtdcp':
            value1 = (proto, mac_list, mac_list, msg, content, str(sid))
            address_count = get_address_count(mac_list)
        else:
            value1 = (proto, ip_list, ip_list, msg, content, str(sid))
            address_count = get_address_count(ip_list)
        if address_count > 1:
            rule1 = format1 % value1
            file_handle.write(rule1)
            sid += 1

        format2 = "%s %s [%s] any -> any any (msg:\"%s \"; %s:\"\"; policy:1; sid:%s; rev:1;)\n"
        if proto == 'goose' or proto == 'sv' or proto == 'pnrtdcp':
            value2 = (mode_action[run_mode], proto, mac_list, msg, content, str(sid))
        else:
            value2 = (mode_action[run_mode], proto, ip_list, msg, content, str(sid))
        if address_count > 0:
            sid += 1
            rule2 = format2 % value2
            file_handle.write(rule2)

        format3 = "%s %s any any -> [%s] any (msg:\"%s \"; %s:\"\"; policy:1; sid:%s; rev:1;)\n"
        if proto == 'goose' or proto == 'sv' or proto == 'pnrtdcp':
            value3 = (mode_action[run_mode], proto, mac_list, msg, content, str(sid))
        else:
            value3 = (mode_action[run_mode], proto, ip_list, msg, content, str(sid))
        if address_count > 0:
            rule3 = format3 % value3
            file_handle.write(rule3)
            sid += 1


def switch_ipmac_extraip(status):
    if status == 1:
        child = subprocess.Popen(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', 'dpi ipmac extra-area-ip enable'])
        child.wait()
        child = subprocess.Popen(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', 'dpi ipmac extra-area-ip action alert'])
        child.wait()
        child = subprocess.Popen(['vtysh', '-c', 'config t', '-c', 'write file'])
        child.wait()
    else:
        child = subprocess.Popen(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', 'dpi ipmac extra-area-ip disable', \
                                    '-c', 'exit', '-c', 'write file'])
        child.wait()


def reload_ipmac_rules():
    child = subprocess.Popen(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', 'dpi reload-rules ip_mac'])
    child.wait()


def realod_all_rules():
    child = subprocess.Popen(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', 'dpi reload-rules'])
    child.wait()


def reload_macfilter_rules(db_proxy):
    sql_str = 'select mac from mac_filter where enable = 1'
    res, rows = db_proxy.read_db(sql_str)
    with open(MAC_FILTER_PATH, 'w') as f:
        for r in rows:
            tmp_r = r[0].replace(':', '')
            f.write(tmp_r + '\n')
    child = subprocess.Popen(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', 'dpi reload-rules mac_filter'])
    child.wait()


def switch_whitelist_status(status):
    if status == 1:
        child = subprocess.Popen(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', 'dpi flowdata-switch on'])
        child.wait()
    else:
        child = subprocess.Popen(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', 'dpi flowdata-switch off'])
        child.wait()


def check_ip_valid(ip):
    try:
        ip = unicode(ip, 'utf8')
    except:
        pass
    ret = True
    if ip.find('-') >= 0:
        tmp_list = ip.split('-')
        try:
            ipaddress.ip_address(tmp_list[0])
            ipaddress.ip_address(tmp_list[1])
            tmp_ip1 = socket.ntohl(struct.unpack("I", socket.inet_aton(str(tmp_list[0])))[0])
            tmp_ip2 = socket.ntohl(struct.unpack("I", socket.inet_aton(str(tmp_list[1])))[0])
            if tmp_ip1 >= tmp_ip2:
                return False
        except:
            return False
        return True
    ip_sub = ip.split('/')
    if len(ip_sub) == 1:
        try:
            ipaddress.ip_address(ip)
            return True
        except:
            return False
    elif len(ip_sub) == 2:
        try:
            ipaddress.ip_network(ip, False)
        except:
            ret = False
        return ret
    return False


def check_mac_valid(mac):
    if mac is None:
        return False
    tmp_list = mac.split(',')
    for m in tmp_list:
        try:
            tmp_list = m.split(':')
            if len(tmp_list) != 6:
                return False
            for t in tmp_list:
                if len(t) != 2:
                    return False
                tmp_num = int(t, 16)
                if tmp_num < 0 or tmp_num > 255:
                    return False
        except:
            return False
    return True
