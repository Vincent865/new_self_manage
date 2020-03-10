#!/usr/bin/python
# -*- coding:UTF-8 -*-
import socket
import ipaddress
import struct
# from global_function.cmdline_oper import *
# from global_function.rule_util_oper import *

def ip6_str_to_num(ip_str):
    return struct.unpack("4I", socket.inet_pton(socket.AF_INET6, ip_str))

def address_ipv6_gt(a, b):
    for i in range(4) :
        if b[i] < a[i]:
            return False
    return True

def check_ip_valid(ip, ip_type=4):
    try:
        ip = unicode(ip, 'utf8')
    except:
        pass
    ret = True
    if ip.find(':') >= 0:
        ip_type = 6
    if ip.find('-') >= 0:
        tmp_list = ip.split('-')
        try:
            ipaddress.ip_address(tmp_list[0])
            ipaddress.ip_address(tmp_list[1])
            if ip_type == 4:
                tmp_ip1 = socket.ntohl(struct.unpack("I", socket.inet_aton(str(tmp_list[0])))[0])
                tmp_ip2 = socket.ntohl(struct.unpack("I", socket.inet_aton(str(tmp_list[1])))[0])
                if tmp_ip1 >= tmp_ip2:
                    return False
            else:
                tmp_ip1 = ip6_str_to_num(tmp_list[0])
                tmp_ip2 = ip6_str_to_num(tmp_list[1])
                return address_ipv6_gt(tmp_ip1, tmp_ip2)
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

#only use in check have mask ip and check ip_mask
def trans_ip_mask(ip):
    tmp_ip = unicode(ip, 'utf8')
    try:
        ip_mask = ipaddress.ip_network(tmp_ip, False)
        return str(ip_mask)
    except:
        return ''

def switch_ipv6_unified_format(ipv6_addr):
    if not ipv6_addr:
        return ipv6_addr
    if ipv6_addr.find('/') >= 0:
        ipv6_addr = str(trans_ip_mask(ipv6_addr))
    elif ipv6_addr.find('-') >= 0:
        tmp_list = ipv6_addr.split('-')
        src_net6 = ipaddress.ip_network(unicode(tmp_list[0]), False)
        info_start = str(src_net6).split('/')[0]
        src_net6 = ipaddress.ip_network(unicode(tmp_list[1]), False)
        info_end = str(src_net6).split('/')[0]
        ipv6_addr = "%s-%s" % (info_start, info_end)
    else:
        src_net6 = ipaddress.ip_network(unicode(ipv6_addr), False)
        ipv6_addr = str(src_net6).split('/')[0]
    return ipv6_addr

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


def get_ip_from_name(db_proxy, name):
    ip_info = []
    sql_str = "select list_info from addr_list_manage where list_name='%s'" % name
    res, rows = db_proxy.read_db(sql_str)
    if len(rows) == 0:
        sql_str = "select group_member from addr_group_manage where group_name='%s'" % name
        res, rows = db_proxy.read_db(sql_str)
        tmp_str = "select list_info from addr_list_manage where id in("
        for r in rows:
            tmp_str += r[0]
        if len(rows) == 0:
            tmp_str += '0'
        tmp_str += ")"
        res, rows = db_proxy.read_db(tmp_str)
        for r in rows:
            ip_info.append(r[0])
    else:
        for r in rows:
            ip_info.append(r[0])
    if len(ip_info) == 0:
        if check_ip_valid(name) is True:
            ip_info.append(name)
    return ip_info


def get_service_from_name(db_proxy, name):
    sql_str = "select content from service_info where service_name='%s'" % name
    res, rows = db_proxy.read_db(sql_str)
    service_info = []
    if len(rows) == 0:
        sql_str = "select group_member from service_group_manage where group_name='%s'" % name
        res, rows = db_proxy.read_db(sql_str)
        tmp_str = "select content from service_info where id in("
        for r in rows:
            tmp_str += r[0]
        if len(rows) == 0:
            tmp_str += '0'
        tmp_str += ")"
        res, rows = db_proxy.read_db(tmp_str)
        for r in rows:
            service_info.append(r[0])
    else:
        for r in rows:
            service_info.append(r[0])
    return service_info


def l2_get_mac_from_name(db_proxy, name):
    mac_info = []
    sql_str = "select list_info from l2_addr_list_manage where list_name='%s'" % name
    res, rows = db_proxy.read_db(sql_str)
    if len(rows) == 0:
        sql_str = "select group_member from l2_addr_group_manage where group_name='%s'" % name
        res, rows = db_proxy.read_db(sql_str)
        tmp_str = "select list_info from l2_addr_list_manage where id in("
        for r in rows:
            tmp_str += r[0]
        if len(rows) == 0:
            tmp_str += '0'
        tmp_str += ")"
        res, rows = db_proxy.read_db(tmp_str)
        for r in rows:
            mac_info.append(r[0])
    else:
        for r in rows:
            mac_info.append(r[0])
    if len(mac_info) == 0:
        if check_mac_valid(name) is True:
            mac_info.append(name)
    return mac_info


def l2_get_service_from_name(db_proxy, name):
    sql_str = "select content from l2_service_info where service_name='%s'" % name
    res, rows = db_proxy.read_db(sql_str)
    service_info = []
    if len(rows) == 0:
        sql_str = "select group_member from l2_service_group_manage where group_name='%s'" % name
        res, rows = db_proxy.read_db(sql_str)
        tmp_str = "select content from l2_service_info where id in("
        for r in rows:
            tmp_str += r[0]
        if len(rows) == 0:
            tmp_str += '0'
        tmp_str += ")"
        res, rows = db_proxy.read_db(tmp_str)
        for r in rows:
            service_info.append(r[0])
    else:
        for r in rows:
            service_info.append(r[0])
    return service_info
