#!/usr/bin/python
# -*- coding:UTF-8 -*-
import socket
import struct

class TopOper(object):
    def __init__(self):
        pass

    @staticmethod
    def get_topo_dict(config_db_proxy, db_proxy, topo_flag):
        res_list = []
        icd_dict = {}
        sql_str = 'select ip,mac,id,name,is_live,dev_type,category_info,dev_desc,is_unknown,dev_mode,auto_flag from topdevice where is_topo=%d' % topo_flag
        _, rows = config_db_proxy.read_db(sql_str)
        tmp_str = "select ip,mac,icd_count,icd_bl_count,icd_wl_count,icd_im_count,icd_flow_count,icd_mf_count,incidentstat_bydev.read,icd_dev_count,icd_pcap_count from incidentstat_bydev"
        _, tmp_rows = db_proxy.read_db(tmp_str)
        for t in tmp_rows:
            tmp_ip = t[0]
            tmp_mac = t[1]
            tmp_icd = t[2]
            tmp_bl = t[3]
            tmp_wl = t[4]
            tmp_im = t[5]
            tmp_flow = t[6]
            tmp_mf = t[7]
            tmp_dev = t[9]
            tmp_pcap = t[10]
            tmp_read = t[8]
            tmp_list = list()
            tmp_list.append(tmp_icd)
            tmp_list.append(tmp_bl)
            tmp_list.append(tmp_wl)
            tmp_list.append(tmp_im)
            tmp_list.append(tmp_flow)
            tmp_list.append(tmp_mf)
            tmp_list.append(tmp_dev)
            tmp_list.append(tmp_read)
            tmp_list.append(tmp_pcap)
            tmp_key = str(tmp_ip) + tmp_mac
            icd_dict[tmp_key] = tmp_list
        for r in rows:
            tmp_dict = {'id': '', 'name': '', 'unread': '', 'alarm_info': {}, 'device_info': {}}
            tmp_ip = r[0]
            tmp_mac = r[1]
            tmp_id = r[2]
            tmp_name = r[3]
            tmp_live = r[4]
            tmp_type = r[5]
            tmp_category = r[6]
            tmp_desc = r[7]
            tmp_unknown = r[8]
            tmp_mode = r[9]
            auto_flag = r[10]
            tmp_dict['id'] = tmp_id
            tmp_dict['name'] = tmp_name
            tmp_dict['device_info']['ip_addr'] = tmp_ip
            tmp_dict['device_info']['mac_addr'] = tmp_mac
            tmp_dict['device_info']['online'] = tmp_live
            tmp_dict['device_info']['dev_type'] = tmp_type
            tmp_dict['device_info']['vender_info'] = tmp_category
            tmp_dict['device_info']['desc'] = tmp_desc
            tmp_dict['device_info']['unknown'] = tmp_unknown
            tmp_dict['device_info']['mode'] = tmp_mode
            tmp_dict['device_info']['auto_flag'] = auto_flag
            tmp_key = tmp_ip + tmp_mac.replace(':', '')
            if tmp_key in icd_dict.keys():
                tmp_value = icd_dict[tmp_key]
                tmp_dict['alarm_info']['evt_count'] = tmp_value[0]
                tmp_dict['alarm_info']['bl_count'] = tmp_value[1]
                tmp_dict['alarm_info']['wl_count'] = tmp_value[2]
                tmp_dict['alarm_info']['im_count'] = tmp_value[3]
                tmp_dict['alarm_info']['flow_count'] = tmp_value[4]
                tmp_dict['alarm_info']['mf_count'] = tmp_value[5]
                tmp_dict['alarm_info']['dev_count'] = tmp_value[6]
                tmp_dict['alarm_info']['pcap_count'] = tmp_value[8]
                tmp_dict['unread'] = tmp_value[0] - tmp_value[7]
                res_list.append(tmp_dict)
            else:
                tmp_dict['alarm_info']['evt_count'] = 0
                tmp_dict['alarm_info']['bl_count'] = 0
                tmp_dict['alarm_info']['wl_count'] = 0
                tmp_dict['alarm_info']['im_count'] = 0
                tmp_dict['alarm_info']['flow_count'] = 0
                tmp_dict['alarm_info']['mf_count'] = 0
                tmp_dict['alarm_info']['dev_count'] = 0
                tmp_dict['unread'] = 0
                res_list.append(tmp_dict)
        return res_list
