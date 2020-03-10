#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
crond task for system backup
author: HanFei
'''
import os
import sys
path = os.path.split(os.path.realpath(__file__))[0]
dirs = os.path.dirname(path)
sys.path.append(dirs)
from global_function.global_var import *
if g_dpi_plat_type == DEV_PLT_X86:
    sys.path.append("/app/lib/python2.7/site-packages")
else:
    sys.path.append("/usr/lib/python2.7/site-packages")
from sysconfbackup import sys_backup_handle

if __name__ == "__main__":
    sys_backup_handle()
