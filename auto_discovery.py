import socket
import traceback
import subprocess
import commands
import os
import logging
import time
from global_function.log_config import *
from common import common_helper
from common.daemon import Daemon



class AutoDiscovery(Daemon):
    host = ""
    client_port = 6067
    server_port = 6068
    dev_sn = ""
    dev_ip = ""
    dev_subnet = ""
    sock_rev = None
    sock_send = None
    addr_send = ('<broadcast>',server_port)
    
    # get ip and submask
    def getIp(self):
        res = commands.getoutput('ifconfig agl0')
        lines = res.split()
        self.dev_ip = lines[6][5:]
        self.dev_subnet = lines[8][5:]
    
    # get sn info    
    def getSn(self):
        res_out = commands.getoutput('vtysh -c "conf t" -c "show version"')
        sn_start = res_out.find('Box S/N')
        sn_start = sn_start+10
        sn_end = res_out.find('\n',sn_start)
        self.dev_sn = res_out[sn_start:sn_end]                                                                               
    
    def setIp(self,ip,mwip,subnet,route):
        subnet_count = subnet.count('255')*8
        setipstr = "vtysh -c 'conf t' -c 'interface agl0' -c 'ip address %s/%d'" %(ip,subnet_count)
        setmwipstr = "vtysh -c 'conf t' -c 'manager-ui ip %s\n'" %mwip
        setroutestr = "vtysh -c 'conf t' -c 'ip route 0.0.0.0/0 %s'" %route
        # writefilestr = "vtysh -c 'write file'"
        #set dev ip
        os.system(setipstr)   
        #set mwip
        os.system(setmwipstr)
        #set routes
        os.system(setroutestr)
        #save configure
        # os.system(writefilestr)
        #restart dpi
        os.system('/etc/stop_app x86')
        time.sleep(8)
        os.system('/etc/start_app')
        time.sleep(5)
        self.getIp()
      
    #socket for receiving data 
    def setRevSocket(self):
        if self.sock_rev != None:
            self.sock_rev.close()
        self.sock_rev =socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_rev.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.sock_rev.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
        self.sock_rev.bind((self.host,self.client_port))
        
    #socket for sending data  
    def setSendSocket(self):                                                              
        #get ip info 
        self.getIp()
        #init socket for sending data
        if self.sock_send != None:
            self.sock_send.close()
        self.sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_send.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.sock_send.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
        self.sock_send.bind((self.dev_ip,self.client_port))
        
    def run(self):   
        logging.info("----start running auto_discovery----")
        try:
            self.setRevSocket()
            self.setSendSocket()
            while 1:                                                                                         
                try:
                    data,addr= self.sock_rev.recvfrom(1024)
                    logging.info("from %s:%s" %(addr,data))
                    msg = data.split(":")
                    if msg[0] == 'tdhx-search-dev':
                        self.getSn()
                        dev_resp = "tdhx-dev-info:%s:%s:%s" %(self.dev_sn,self.dev_ip,self.dev_subnet)
                        self.sock_send.sendto(dev_resp,self.addr_send)
                        logging.info("send broadcat:%s" %dev_resp)
                    if msg[0] == 'tdhx-disc-setip':
                        self.getSn()
                        if msg[1] == self.dev_sn and len(msg) == 6:
                            if msg[2] == self.dev_ip:
                                confirm_msg = "tdhx-disc-setip-duplicated:%s" %self.dev_sn
                                self.sock_send.sendto(confirm_msg,self.addr_send)
                                logging.info("send broadcat:%s" %confirm_msg)
                            else:   
                                confirm_msg = "tdhx-disc-setip-ok:%s" %self.dev_sn
                                self.sock_send.sendto(confirm_msg,self.addr_send)
                                logging.info("send broadcat:%s" %confirm_msg)
                                self.setIp(msg[2],msg[3],msg[4],msg[5])
                                self.setSendSocket()
                except: 
                    logging.info(traceback.format_exc())
                    pass
        except: 
            logging.info(traceback.format_exc())
        finally:
            if self.sock_rev != None:
                self.sock_rev.close()
            if self.sock_send != None:
                self.sock_send.close()
                                                                         
def main(): 
    LogConfig('auto-disc.log')
    app_name = os.path.basename(os.path.realpath(__file__))             
    if common_helper.process_already_running(app_name):                 
        print(app_name+' is already running. Abort!')
        return                                                          
    daemon = AutoDiscovery()                                             
    daemon.start()                                                       
if __name__ == "__main__":                                               
    main()