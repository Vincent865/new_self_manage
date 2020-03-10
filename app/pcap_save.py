#!/usr/bin/python
# -*- coding:UTF-8 -*-
import os,sys
path = os.path.split(os.path.realpath(__file__))[0]
dirs = os.path.dirname(path)
sys.path.append(dirs)
from global_function.log_oper import *
import fcntl
import glob
import signal
import commands

'''
author: diaowq
function point:
1. alert the event, when disk free space is not enough, then don't save this pcap file
2. rename p0.0/p0.1 to p0/[interface]_[starttime]_[endtime]_f[1,2,...10000].pcap,
   eg: p0_20161109133616_20161109133624_f1.pcap
3. update pcap info to the table of `pcap_info` at database `keystone`

input:
p0.0 or p0.1, the name of pcap file, which will be handled.

[root@IstuaryOS ~]:/data/pcap_save$ tree
├── cur_file_p0     # the index of the next saved pcap file
├── max_file_p0     # the max index of pcap file. skip to 1, when index reaches to it
├── p0              # the dir to save all the pcap file for interface p0
│   ├── p0_20161109133616_20161109133624_f1.pcap
│   ├── p0_20161109133624_20161109133630_f2.pcap
│   ├── p0_20161109133630_20161109133920_f3.pcap
├── p0.0            # the capture of tcpdump is saving to it.
├── pcap_save_clear.py      # clear out one interface's pcap info at database `keystone`'s table `pcap_info`, called by cli.
└── pcap_save.py            # just this script
'''

def get_ps_result():
    ''' get process status '''
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    ps_result = []
    for pid in pids:
        try:
            ps_result.append(pid + ' ' + \
                open(os.path.join('/proc', pid, 'cmdline'), 'rb').read())
        except IOError: # proc has already terminated
            continue
    return ps_result

def process_already_running(cmdline):
    ''' check process is running! '''
    count = 0
    result = get_ps_result()
    for line in result:
        if line.find(cmdline) != -1:
            #print line
            count += 1
    #print count
    if count > 1:
        return True
    else:
        return False

class PcapSaveHandler():
    def __init__(self):
        self.db_proxy = DbProxy()
        self.tcpdump_running = 1

    def disk_alarm(self, file_name):
        ''' alert the event, when disk free is not enough, then don't save this pcap file '''
        pcap_save_incident_flag = "/tmp/pcap_save_disk_space_incident"
        data_disk = os.statvfs("/data")
        dd_free = data_disk.f_bsize * data_disk.f_bavail / (1024 * 1024 * 1024)
        ''' TODO: 1G is ok? '''
        if dd_free < 1:
            if not os.path.exists(pcap_save_incident_flag):
                msg = {}
                msg['Type'] = SERVICE_TYPE
                msg['LogLevel'] = LOG_ALERT
                msg['Content'] = u'数据包存储功能告警：磁盘空间紧张'
                msg['Componet'] = 'pcap'
                send_log_db(MODULE_SYSTEM, msg)

                os.unlink(file_name)
                os.mknod(pcap_save_incident_flag)
            return 1
        else:
            if os.path.exists(pcap_save_incident_flag):
                os.unlink(pcap_save_incident_flag)

    def record_pcap_info(self, file_index, interface, new_name, starttime, endtime, file_size):
        ''' update db '''
        try:
            sql_delete = "delete from pcap_info where filename LIKE '" + interface + "%f" + str(file_index) + ".pcap';"
            self.db_proxy.write_db(sql_delete)
            sql_insert = "insert into pcap_info(filename,interface,starttime,endtime,size) values('%s','%s','%s','%s','%d');" % (
            new_name, interface, time.strftime("%Y-%m-%d %H:%M:%S", starttime),
            time.strftime("%Y-%m-%d %H:%M:%S", endtime), file_size)
            self.db_proxy.write_db(sql_insert)
            return 1
        except:
            return 0

    def handle_one_pcap(self, file_name):
        pcap_save_dir = "/data/pcap_save/"
        cur_file_path = pcap_save_dir + "cur_file"
        max_file_path = pcap_save_dir + "max_file"

        if self.disk_alarm(file_name) == 1:
            return

        pcap_orig_name = file_name

        file_size = os.path.getsize(pcap_orig_name)
        if file_size <= 24:
            # too small size, the pcap file is empty
            os.remove(pcap_orig_name)
            return

        if pcap_orig_name.rfind('/') != -1:
            pcap_interface = pcap_orig_name[pcap_orig_name.rfind('/') + 1:pcap_orig_name.find('.')]
        else:
            pcap_interface = pcap_orig_name[:pcap_orig_name.find('.')]
        pcap_save_subif_dir = pcap_save_dir + pcap_interface + "/"

        ''' default value, will be covered by config file if $cur_file_path/$max_file_path is existed '''
        cur_file = 1
        max_file_count = 10000

        ''' make sure the dir to save pcap for interface '''
        if not os.path.exists(pcap_save_subif_dir):
            os.makedirs(pcap_save_subif_dir)

        ''' get the max index of saving pcap file '''
        max_file_path += '_' + pcap_interface
        try:
            with open(max_file_path) as fp:
                max_file_count = int(fp.read())
        except:
            if g_dpi_plat_type == DEV_PLT_X86:
                max_file_count = 10000
            else:
                max_file_count = 100

        ''' get the index of saving pcap file '''
        cur_file_path += '_' + pcap_interface
        if os.path.exists(cur_file_path):
            with open(cur_file_path, 'r+') as fp:
                fcntl.flock(fp.fileno(), fcntl.LOCK_EX)  # locks the file
                cur_file = int(fp.read())
                ''' save the next index of to be saved pcap file '''
                if cur_file >= max_file_count:
                    fp.seek(0)
                    fp.write('1            ')  # the blank is need, the len must be longer than the max_file_count
                else:
                    fp.seek(0)
                    fp.write(str(cur_file + 1))
        else:
            with open(cur_file_path, 'w') as fp:
                fcntl.flock(fp.fileno(), fcntl.LOCK_EX)  # locks the file
                fp.write(str(cur_file) + '\n')

        ''' get the create time and the close time of the pcap file '''
        atime = time.localtime(os.path.getatime(pcap_orig_name))
        ctime = time.localtime(os.path.getctime(pcap_orig_name))

        ''' construct the new name of pcap file '''
        pcap_new_name = pcap_interface \
                        + '_' \
                        + time.strftime("%Y%m%d%H%M%S", atime) \
                        + '_' \
                        + time.strftime("%Y%m%d%H%M%S", ctime) \
                        + '_f' + str(cur_file) \
                        + '.pcap'

        ''' rolling save '''
        for file in glob.glob(pcap_save_subif_dir + "*_f" + str(cur_file) + ".pcap"):
            os.remove(file)
        os.rename(pcap_orig_name, pcap_save_subif_dir + pcap_new_name)

        self.record_pcap_info(cur_file, pcap_interface, pcap_new_name, atime, ctime, file_size)

    def signal_handler(self,signum, frame):
        time.sleep(1)
        if g_dpi_plat_type == DEV_PLT_X86:
            return_code, output = commands.getstatusoutput('ps -aux | grep tcpdump')
        else:
            return_code, output = commands.getstatusoutput('ps | grep tcpdump')
        if output.find("/data/pcap_save/p") != -1:
            self.tcpdump_running = 1
        else:
            self.tcpdump_running = 0

    def run(self):
        PCAP_SAVE_DIR = '/data/pcap_save/'
        PID_FILE = '/tmp/pcap_save/pcap_save_pyc_id'

        app_name = os.path.basename(os.path.realpath(__file__))
        if process_already_running(app_name):
            print('pcap_save.py is already running. Abort!')
            return

        os.system('mkdir -p /tmp/pcap_save/')
        os.system('echo '+ str(os.getpid()) +' > /tmp/pcap_save/pcap_save_pyc_id')

        signal.signal(signal.SIGUSR1, self.signal_handler)
        if g_dpi_plat_type == DEV_PLT_X86:
            pattern = re.compile(r"p\d{1}\.\d{4}")
        else:
            pattern = re.compile(r"p\d{1}\.\d{2}")
        while True:
            fdict = {}
            dir = os.listdir(PCAP_SAVE_DIR)

            for f in dir:
                pattern_search = pattern.search(f)
                if pattern_search != None:
                    file_name = PCAP_SAVE_DIR+f
                    fdict[file_name] = time.strftime("%Y%m%d%H%M%S", time.localtime(os.path.getatime(file_name)))

            # sort by create time
            forder = sorted(fdict.items(), key=lambda e: e[1], reverse=False)

            # user has disable pcap save function, and the last pcap file has been handled
            if len(forder) == 0 and self.tcpdump_running <= 0:
                os.remove('/tmp/pcap_save/pcap_save_pyc_id')
                break

            # walk to handle pcap file, one by one
            for f in forder:
                file_name = f[0]
                if os.path.getsize(file_name) > 10*1000*1000:
                    self.handle_one_pcap(file_name)
                elif self.tcpdump_running <= 0:
                    self.handle_one_pcap(file_name)

            time.sleep(0.1)

def main():
    psh = PcapSaveHandler()
    psh.run()

if __name__ == "__main__":
    main()