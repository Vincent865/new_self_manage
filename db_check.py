import os
import time
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from logging.handlers import  SysLogHandler
from common.daemon import Daemon


class DbCheck(Daemon):
    def setup_logger(self):
        output_file = '/data/log/db_check.log'
        logger = logging.getLogger('db_check_log')
        logger.setLevel(logging.ERROR)
        # create a rolling file handler
        try:
            handler = RotatingFileHandler(output_file, mode='a',
                                      maxBytes=1024 * 1024 * 10, backupCount=10)
        except:
            handler = SysLogHandler()
        handler.setLevel(logging.ERROR)
        handler.setFormatter(logging.Formatter("[%(asctime)s -%(levelname)5s- %(filename)20s:%(lineno)3s] %(message)s","%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
    def check_db(self):
        command = "/app/local/mysql/bin/mysqlcheck  -c keystone "
        handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        while 1:                                                                                         
            if handle.poll() is not None:                                                                
                break
        sss = handle.stdout.read()
        err_tab  = []
        #-------------------------------
        with open("/data/log/mysqlcheck_result.txt", 'w') as f:
            f.write(sss)
        #--------------------------------
        #find error
        if sss.find("error")>0:
            for line in sss.split("keystone."):
                if line.find("error")>0:
                    err_tab.append(line.split()[0])
        else:
            #run mysql_check_keystone 
            return 0,err_tab
        return 1,err_tab     
    def repair_db(self,err_tab):
        if len(err_tab) < 1:
            return

        db_stop_cmd = "/app/local/mysql/support-files/mysql.server stop "
        os.system(db_stop_cmd)
        #command = "/app/local/mysql/bin/myisamchk -r  "
        #file_path = "/data/mysql/keystone"
        #for tab in err_tab:
        #    file_name = os.path.join(file_path,"%s.MYI"%(tab))
        #    command = command + " " + file_name
        #
        #handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        #while 1:                                                                                         
        #    if handle.poll() is not None:                                                                
        #        break
        command = 'cp -rf /data/mysql_bak/keystone /data/mysql'
        os.system(command)
        db_start_cmd = "/app/local/mysql/support-files/mysql.server start "
        os.system(db_start_cmd)
        return
        
        
    def recheck_db(self):
        command = "/app/local/mysql/bin/mysqlcheck  -c keystone "
        handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        while 1:                                                                                         
            if handle.poll() is not None:                                                                
                break
        sss = handle.stdout.read()
        err_tab  = []
        #-------------------------------
        with open("/data/log/mysqlcheck_result1.txt", 'w') as f:
            f.write(sss)
        #--------------------------------
        #find error
        if sss.find("error")>0:
            for line in sss.split("keystone."):
                if line.find("error")>0:
                    err_tab.append(line.split()[0])
        else:
            #run mysql_check_keystone 
            return 0,err_tab
        return 1,err_tab
    def recover_db(self,err_tab):
        if len(err_tab) < 1:
            return
        db_stop_cmd = "/app/local/mysql/support-files/mysql.server stop "
        os.system(db_stop_cmd)
        #0: ok, 1: fail
        res = 0
        if os.path.exists("/data/mysql_bak/keystone"):
            #clear all /data/mysql
            command = "rm -f /data/mysql/keystone/*"
            os.system(command)
            command = "cp -rpH /data/mysql_bak/keystone/* /data/mysql/keystone/"
            os.system(command)
        else:
            res = 1
        db_start_cmd = "/app/local/mysql/support-files/mysql.server start "
        os.system(db_start_cmd)
        #recover fail
        if res == 1:
            command = "/app/bin/db_rebuild.sh"
            os.system(command)
            db_restart_cmd = "/app/local/mysql/support-files/mysql.server restart "
            os.system(db_restart_cmd)
            
        return 
        
    def run(self):
        return
        self.setup_logger()
        logger = logging.getLogger('db_check_log')
        if os.path.exists("/app/db_flag/need_check.flag"):
            while not os.path.exists("/tmp/mysql.sock"):
                time.sleep(2)
            res,err_tab = self.check_db()
            if res == 1:
                #self.repair_db(err_tab)
                #res, re_err_tab = self.recheck_db(err_tab)
                #if res != 0:
                logger.error("recover_db")
                self.recover_db(err_tab)
                res,err_tab = self.recheck_db()
            if res == 0:
                logger.error("db_check ok")
                os.system("rm -f /app/db_flag/mysql_check_error.flag")
            else:
                logger.error("db_check fail")
                os.system("mkdir -p /app/db_flag")
                os.system("touch  /app/db_flag/mysql_check_error.flag")       
        os.system("mkdir -p /app/db_flag")
        os.system("touch  /app/db_flag/need_check.flag")
        return

def main():
    daemon = DbCheck('/dev/null','/dev/null','/data/log/dbcheck_error.log')
    if os.path.exists('/data/log/dbcheck_error.log') is False:
        os.mknod('/data/log/dbcheck_error.log')
    daemon.run()
    
if __name__ == "__main__":
    main()
