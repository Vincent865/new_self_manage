#!/usr/bin/python
# -*- coding:UTF-8 -*-

import sys
sys.path.append('/app/local/share/new_self_manage/')
from global_function.global_var import *

'''
 clear out one interface's pcap info at database `keystone`'s table `pcap_info`, called by cli.
'''
pcap_interface = sys.argv[1]

'''
 clear all the pcap file of the `interface` from db
'''
db_proxy = DbProxy()
sql_delete = "delete from pcap_info where interface = '"+pcap_interface+"';"
db_proxy.write_db(sql_delete)
