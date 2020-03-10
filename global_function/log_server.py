#!/usr/bin/python
# -*- coding:UTF-8 -*-
__author__ = 'yxs'

from log_oper import *
import sys
import threading
import logging
logger = logging.getLogger('flask_mw_log')

sys.path.append("..")
sys.path.append("/usr/local/share/flask_mw")


class UserCmdLog:
  """
  Attributes:
   - timestamp
   - user
   - cmd
   - result
   - user_ip
  """

  def __init__(self, timestamp=None, user=None, cmd=None, result=None, user_ip=None,):
    self.timestamp = timestamp
    self.user = user
    self.cmd = cmd
    self.result = result
    self.user_ip = user_ip

class UserLoginLog:
  """
  Attributes:
   - timestamp
   - user
   - user_ip
   - result
   - reason
  """

  def __init__(self, timestamp=None, user=None, user_ip=None, result=None, reason=None):
    self.timestamp = timestamp
    self.user = user
    self.user_ip = user_ip
    self.result = result
    self.reason = reason


class LogServer(threading.Thread):
    def __init__(self, test=False):
        threading.Thread.__init__(self)
        self.log_conn = None
        self.ip = "127.0.0.1"
        self.port = 22222

        self.pattern_times        = re.compile('[A-Z][a-z][a-z]\s+\d+\s+(\d+:\d+:\d+)')
        self.pattern_day          = re.compile('\s(\d+)\s')
        self.pattern_time         = re.compile('(\d+:\d+:\d+)')
        self.pattern_login_user   = re.compile('USER=([^ ]+)')
        self.pattern_login_userIp = re.compile('IP=(.*?)\s')
        self.pattern_cli_command  = re.compile('COMMAND=\"(.*)\"')
        self.pattern_cli_result   = re.compile('RESULT=(.*)')
        self.pattern_IP           = re.compile('IP=(.*?)\s')

        self.pattern_mac          = re.compile('MAC=([^ ]+)')
        self.pattern_src_ip       = re.compile('SRC=(\d+.\d+.\d+.\d+)')
        self.pattern_dst_ip       = re.compile('DST=(\d+.\d+.\d+.\d+)')
        self.pattern_src_port     = re.compile('SPT=(\d+)')
        self.pattern_dst_port     = re.compile('DPT=(\d+)')
        self.pattern_protocol     = re.compile('PROTO=([^ ]+)\s')
        self.pattern_packet_len   = re.compile('LEN=(\d+)')
        self.pattern_iptable_reason = re.compile('PKTFILTER_([^ ]+)')
        self.pattern_granted      = re.compile('GRANTED\s(.*)')
        self.pattern_deny         = re.compile('DENIED\s(.*)')
        self.pattern_commonlog    = re.compile('SYSTEM (.*)')
        self.month_dict = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04',
                           'May':'05', 'Jun':'06', 'Jul':'07', 'Aug':'08',
                           'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}
        self.operation_id = 0
        self.login_oper = "用户命令行登录".decode("utf-8")

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.ip, self.port))

        #logger.info("bind socket success ip:" + str(self.ip) + " port:" + str(self.port))

        while True:
            data, addr = sock.recvfrom(4096)
            # logger.info("receive data : --------------" + data)

            if not data:
                continue

            extractdata = None
            message_type = 0
            try:
                if 'LOGIN ' in data and "pam_unix" not in data:
                    #logger.info("----------------LOG----------------")
                    extractdata = self.extract_login_info(data)
                    message_type = 0
                elif 'ssh' in data and "pam_unix" not in data:
                    extractdata = self.extract_login_info_allinone(data)
                    message_type = 2
                elif 'panguOS login' in data and "pam_unix" not in data:
                    extractdata = self.extract_console_login_info(data)
                    message_type = 3
                elif 'login ' in data and "pam_unix" not in data:
                    #logger.info("----------------console login----------------")
                    extractdata = self.extract_console_login_info(data)
                    message_type = 0
                elif 'CLI' in data:
                    #logger.info("----------------CLI----------------")
                    extractdata = self.extract_cli_info(data)
                    message_type = 1
                elif 'Accepted ' in data or 'Failed password ' in data:
                    #logger.info("----------------LOGIN----------------")
                    extractdata = self.extract_login_info_allinone(data)
                    message_type = 0

            except Exception:
                logging.error(traceback.print_exc())

            if extractdata is None:
                continue
            
            if extractdata.user and extractdata.user.find('root')>=0:
                continue         
            try:
                if message_type == 0:
                    #logger.info("timestamp: " + extractdata.timestamp + ", user: " + extractdata.user)
                    msg = {}
                    msg['UserIP'] = extractdata.user_ip
                    msg['UserName'] = extractdata.user
                    msg['Operate'] = extractdata.reason
                    msg['ManageStyle'] = 'WEB'
                    msg['Result'] = extractdata.result
                    send_log_db(MODULE_OPERATION, msg)
                elif message_type == 1:
                    #logger.info("timestamp: " + extractdata.timestamp + ", cmd: " + extractdata.cmd + ", userip: " + extractdata.user_ip)
                    msg = {}
                    msg['UserIP'] = extractdata.user_ip
                    msg['UserName'] = extractdata.user
                    msg['Operate'] = extractdata.cmd.decode('utf-8')
                    msg['ManageStyle'] = 'console'
                    msg['Result'] = extractdata.result
                    if msg['Operate'].find('引擎白名单学习') < 0:
                        send_log_db(MODULE_OPERATION, msg)
                elif message_type == 2:
                    #logger.info("timestamp: " + extractdata.timestamp + ", user: " + extractdata.user)
                    msg = {}
                    msg['UserIP'] = extractdata.user_ip
                    msg['UserName'] = extractdata.user
                    msg['Operate'] = extractdata.reason
                    msg['ManageStyle'] = 'SSH'
                    msg['Result'] = extractdata.result
                    send_log_db(MODULE_OPERATION, msg)
                elif message_type == 3:
                    # logger.info("timestamp: " + extractdata.timestamp + ", user: " + extractdata.user)
                    msg={}
                    msg['UserIP']=extractdata.user_ip
                    msg['UserName']=extractdata.user
                    msg['Operate']=extractdata.reason
                    msg['ManageStyle']='CONSOLE'
                    msg['Result']=extractdata.result
                    send_log_db(MODULE_OPERATION, msg)

                    
            except Exception:
                logging.error(traceback.print_exc())
        sock.close()

    def extract_login_info(self,data):
        logdata = data.strip()

        timestr = self.get_utc_time(logdata)

        userName = None
        userNameList = re.findall(self.pattern_login_user,logdata)
        if userNameList:
            userName = userNameList[0]
            if userName != 'admin' and userName != 'root':
                userName = "not system user"

        userIp = None
        userIpList = re.findall(self.pattern_login_userIp,logdata)
        if userIpList:
            userIp = userIpList[0]

        logreason = None

        if 'GRANTED' in logdata:
            logresult = '0'
            logreasonlist = re.findall(self.pattern_granted,logdata)
            if logreasonlist:
                logreason = logreasonlist[0]

        else:
            logresult = '1'
            logreasonlist = re.findall(self.pattern_deny,logdata)
            if logreasonlist:
                logreason = logreasonlist[0]

        return UserLoginLog(timestamp=timestr,
                                      user=userName,
                                      user_ip=userIp,
                                      result=logresult,
                                      reason=logreason)

    def extract_login_info_allinone(self,data):
        logdata = data.strip()
        timestr = self.get_utc_time(logdata)
        logreason = None
        userName = None
        userIp = None
        data_index = logdata.find("for")+4
        data_tmp = logdata[data_index:]
        if 'Accepted ' in logdata:
            logresult = '0'
            user_str,from_str,ip_str,port_str,portno,ssh_str=data_tmp.strip().split(' ')
            userName = user_str
            userIp = ip_str
            logreason = self.login_oper
        elif 'Failed ' in logdata and 'invalid ' in logdata:
            logresult = '1'
            invalit_str,user_pre,user_str,from_str,ip_str,port_str,portno,ssh_str=data_tmp.strip().split(' ')
            userName = user_str
            userIp = ip_str
            logreason = self.login_oper
        else:
            logresult = '1'
            user_str,from_str,ip_str,port_str,portno,ssh_str=data_tmp.strip().split(' ')
            userName = user_str
            userIp = ip_str
            logreason = self.login_oper
        #filter user: dpi_user login info
        if userName == "dpi_user":
            return None

        return UserLoginLog(timestamp=timestr,
                                      user=userName,
                                      user_ip=userIp,
                                      result=logresult,
                                      reason=logreason)

    def extract_console_login_info(self,data):
        logdata = data.strip()
        timestr = self.get_utc_time(logdata)
        userName = "admin"
        userIp = "CONSOLE"
        logresult = '0'
        logreason = self.login_oper
        return UserLoginLog(timestamp=timestr,
                                      user=userName,
                                      user_ip=userIp,
                                      result=logresult,
                                      reason=logreason)
                                      
    def extract_cli_info(self,data):
        logdata = data.strip()

        timestr = self.get_utc_time(logdata)

        username = None
        userNameList = re.findall(self.pattern_login_user,logdata)
        if userNameList:
            username = userNameList[0]

        userip = None
        useriplist = re.findall(self.pattern_IP,logdata)
        if useriplist:
            userip = useriplist[0]

        command = None
        commandList = re.findall(self.pattern_cli_command,logdata)
        if commandList:
            command = commandList[0]

        logresult = None
        logstr = re.findall(self.pattern_cli_result,logdata)
        if logstr:
            if logstr[0] == 'OK':
                logresult = '0'
            else:
                logresult = '1'

        return UserCmdLog(timestamp=timestr,user=username,cmd=command,result=logresult,
                                    user_ip=userip)
                                    
    def get_utc_time(self,data):

        now = time.time()
        return time.strftime("%Y-%m-%dT%H:%M:%SZ",time.localtime(now))
 
