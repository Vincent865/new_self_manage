'''
Hardware status check
author: HanFei
'''
import threading
from global_var import *

logger = logging.getLogger('flask_mw_log')


class hd_raid_check(threading.Thread):
    '''raid status check thread,link to machinestate process'''

    def __init__(self):
        '''init flow audit object'''
        threading.Thread.__init__(self)
        logger.info("init hd_raid_check ok!")

    def run(self):

        '''run raid status check obj'''
        while True:
            db_proxy = DbProxy(CONFIG_DB_NAME)
            handle = subprocess.Popen("/bin/bash /usr/bin/statusraid.sh",
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      shell=True)
            handle.wait()
            res = handle.stdout.read().strip()
            sts_list = res.split(",")
            if( len(sts_list) != 6 ):
                time.sleep(15)
                continue

            if( sts_list[0] == '3' or sts_list[3] == '3' ):
                hd_1_offline = 0
                hd_2_offline = 0
                dst_res = [0,0,"",0,0,""]
                handle = subprocess.Popen("cat /proc/scsi/scsi",
                                    stdin = subprocess.PIPE,
                                    stdout = subprocess.PIPE,
                                    stderr = subprocess.PIPE,
                                    shell = True)
                handle.wait()
                scsi_res = handle.stdout.read()
                if( "scsi1" not in scsi_res ):
                    hd_1_offline = 1
                if( "scsi4" not in scsi_res):
                    hd_2_offline = 1

                if(sts_list[0] == '3' and sts_list[3] != '3'):
                    mod_index = 1
                elif(sts_list[0] != '3' and sts_list[3] == '3'):
                    mod_index = 2
                else:
                    mod_index = 3

                if( hd_1_offline == 1 and hd_2_offline == 0 ):
                    if(mod_index == 2):
                        dst_res[0] = 0
                        dst_res[1] = 0
                        dst_res[2] = ""
                        dst_res[3] = sts_list[0]
                        dst_res[4] = sts_list[1]
                        dst_res[5] = sts_list[2]
                    else:
                        dst_res[0] = 0
                        dst_res[1] = 0
                        dst_res[2] = ""
                        dst_res[3] = sts_list[3]
                        dst_res[4] = sts_list[4]
                        dst_res[5] = sts_list[5]

                elif( hd_1_offline == 0 and hd_2_offline == 1 ):
                    if(mod_index == 1):
                        dst_res[0] = sts_list[3]
                        dst_res[1] = sts_list[4]
                        dst_res[2] = sts_list[5]
                        dst_res[3] = 0
                        dst_res[4] = 0
                        dst_res[5] = ""
                    else:
                        dst_res[0] = sts_list[0]
                        dst_res[1] = sts_list[1]
                        dst_res[2] = sts_list[2]
                        dst_res[3] = 0
                        dst_res[4] = 0
                        dst_res[5] = ""
                elif( hd_1_offline == 1 and hd_2_offline == 1 ):
                    dst_res[0] = 0
                    dst_res[1] = 0
                    dst_res[2] = ""
                    dst_res[3] = 0
                    dst_res[4] = 0
                    dst_res[5] = ""
                else:
                    dst_res = sts_list
            else:
                dst_res = sts_list

            sql_str = "update nsm_raidstatus set disk_1_status = %d, rebuild_prog_1 = %02.1f, disk_1_sn = '%s', disk_2_status = %d, rebuild_prog_2 = %02.1f, disk_2_sn = '%s'" \
                      % (int(dst_res[0]), float(dst_res[1]),str(dst_res[2]),int(dst_res[3]), float(dst_res[4]),str(dst_res[5]))
            db_proxy.write_db(sql_str)
            time.sleep(30)

