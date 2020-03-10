#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import sys
path = os.path.split(os.path.realpath(__file__))[0]
dirs = os.path.dirname(path)
sys.path.append(dirs)
sys.path.append("/app/lib/python2.7/site-packages")
from global_function.global_var import *
from reportgen import log_report_gen_handle

if __name__ == "__main__":
    if( len(sys.argv) != 2 ):
        exit(1)
    freq = int(sys.argv[1])
    if( freq != 1 and freq != 2 and freq != 3 ):
        exit(1)
    log_report_gen_handle(freq)
