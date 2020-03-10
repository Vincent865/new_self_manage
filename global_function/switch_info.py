#!/usr/bin/python
# -*- coding:UTF-8 -*-
import os
import time
import threading
import logging
import traceback

from global_function.global_var import *
from global_function.global_var import DbProxy, CONFIG_DB_NAME

logger = logging.getLogger('flask_db_socket_log')
SWITCH_UPLOAD_FOLDER = '/data/switchinfo/'


def trans_mac(mac):
    """
    转换十进制mac地址为十六进制
    """
    tmp_list = []
    for i in mac.split('.'):
        if int(i) <= 255:
            tmp = hex(int(i))[2:]
            if len(str(tmp)) < 2:
                tmp = "0"+tmp
            tmp_list.append(tmp)
    trans_mac = "%s:%s:%s:%s:%s:%s" % tuple(tmp_list)
    return trans_mac


class autoGetSwitchInfo(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.db_proxy = DbProxy(CONFIG_DB_NAME)

    # 计算所有交换机的mac_port表
    @staticmethod
    def get_all_switch_mac_port():
        db_proxy = DbProxy(CONFIG_DB_NAME)
        sql_str = "select snmp_version,group_name,security_level,security_name,auth_mode,auth_pwd,priv_mode,priv_pwd,ssh_name,ssh_pwd, ip,name from switch_info"
        res, rows = db_proxy.read_db(sql_str)
        if len(rows) > 0:
            for row in rows:
                autoGetSwitchInfo.get_one_switch_mac_port(row)

    # 计算单个交换机的mac_port表
    @staticmethod
    def get_one_switch_mac_port(row):
        if not os.path.exists(SWITCH_UPLOAD_FOLDER):
            os.system("mkdir -p " + SWITCH_UPLOAD_FOLDER)
        ssh_name = row[8]
        ssh_pwd = row[9]

        # 为优化计算性能，根据配置的信息选择计算方式
        if not ssh_name and not ssh_pwd:  # 只配置了snmp配置
            logger.info("--------------snmp--------")
            res_snmp = autoGetSwitchInfo.get_mac_port_by_snmp(row)
        else:  # 优先使用snmp方式获取mac_port表
            logger.info("--------------snmp------------ssh----------")
            res_snmp = autoGetSwitchInfo.get_mac_port_by_snmp(row)
            if not res_snmp:
                logger.info("========snmp fail=========================")
                # snmp失败，再使用ssh方式获取mac_port表
                autoGetSwitchInfo.get_mac_port_by_ssh(row)

    # 使用snmp方式获取mac_port表
    @staticmethod
    def get_mac_port_by_snmp(row):
        db_proxy = DbProxy(CONFIG_DB_NAME)
        snmp_version = row[0]
        group_name = row[1]
        security_level = row[2]
        security_name = row[3]
        auth_mode = row[4]
        auth_pwd = row[5]
        priv_mode = row[6]
        priv_pwd = row[7]
        ip = row[10]
        switch_name = row[11]

        # port索引port_index_oid port名称port_name_oid
        port_index_oid = ' 1.3.6.1.2.1.17.7.1.2.2.1.2 >'
        port_name_oid = ' 1.3.6.1.2.1.31.1.1.1.1 >'

        if snmp_version == 1:  # v1版本
            tmp_cmd = "snmpwalk -v 1 -c " + group_name + " " + ip
        elif snmp_version == 2:  # v2版本
            tmp_cmd = "snmpwalk -v 2c -c " + group_name + " " + ip
        elif snmp_version == 3:  # v3版本
            # 认证方式需要转换DES56转换成DES
            if priv_mode == 'DES56':
                priv_mode = 'DES'
            # 三个安全级别：noAuthNoPriv|authNoPriv|authPriv
            if security_level == "noAuthNoPriv":
                tmp_cmd = 'snmpwalk -v 3 -u ' + security_name + ' -l ' + security_level + ' ' + ip
            if security_level == "authNoPriv":
                tmp_cmd = 'snmpwalk  -v 3 -u ' + security_name + ' -a ' + auth_mode + ' -A ' + auth_pwd + ' -l ' + security_level + ' ' + ip
            if security_level == "authPriv":
                tmp_cmd = 'snmpwalk  -v 3 -u ' + security_name + ' -a ' + auth_mode + ' -A ' + auth_pwd + ' -x ' + priv_mode + ' -X ' + priv_pwd + ' -l ' + security_level + '  ' + ip
        else:
            return False
        port_index_cmd = tmp_cmd + port_index_oid
        port_name_cmd = tmp_cmd + port_name_oid
        logger.info(port_index_cmd)
        logger.info(port_name_cmd)
        os.system(port_index_cmd + SWITCH_UPLOAD_FOLDER + "snmp_mac_port")
        os.system(port_name_cmd + SWITCH_UPLOAD_FOLDER + "snmp_mac_port_name")
        logger.info(os.path.getsize(SWITCH_UPLOAD_FOLDER + "snmp_mac_port"))
        logger.info(os.path.getsize(SWITCH_UPLOAD_FOLDER + "snmp_mac_port_name"))

        if os.path.getsize(SWITCH_UPLOAD_FOLDER + "snmp_mac_port") > 0:
            # 1、查mac索引，存数据库
            with open(SWITCH_UPLOAD_FOLDER + "snmp_mac_port", 'r+') as f:
                del_str = "delete from switch_mac_port where switch_name='{}'".format(switch_name)
                # logger.info(del_str)
                db_proxy.write_db(del_str)
                for line in f.readlines():
                    # logger.info(line)
                    if line.startswith("iso"):  # iso.3.6.1.2.1.17.7.1.2.2.1.2.1.0.12.41.0.101.250 = INTEGER: 24
                        mac = line.split(" =")[0][31:]
                        # 转换十进制mac地址为十六进制
                        mac = trans_mac(mac)
                        port = line.split("INTEGER: ")[1]
                        insert_sql = "insert into switch_mac_port (switch_name, mac, port) values ('{}','{}',{})".format(
                            switch_name, mac, port)
                        # logger.info(insert_sql)
                        res = db_proxy.write_db(insert_sql)
                    continue
            # 2、根据mac索引查询mac端口名称
            if os.path.getsize(SWITCH_UPLOAD_FOLDER + "snmp_mac_port_name") > 0:
                with open(SWITCH_UPLOAD_FOLDER + "snmp_mac_port_name", 'r+') as f:
                    for line in f.readlines():
                        # logger.info(line)
                        if line.startswith("iso"):
                            port_index = str(line.split(' =')[0][line.rfind('.') + 1:])
                            port_name = line.split('STRING: "')[1][:-2]
                            update_sql = "update switch_mac_port set port = '{}' where port = '{}'".format(port_name,port_index)
                            # logger.info(update_sql)
                            res = db_proxy.write_db(update_sql)

            # 删除数据文件
            os.system("rm -rf " + SWITCH_UPLOAD_FOLDER + "snmp_mac_port")
            os.system("rm -rf " + SWITCH_UPLOAD_FOLDER + "snmp_mac_port_name")
            return True
        else:
            return False

    # 使用ssh方式获取mac_port表
    @staticmethod
    def get_mac_port_by_ssh(row):
        db_proxy = DbProxy(CONFIG_DB_NAME)
        ssh_name = row[8]
        ssh_pwd = row[9]
        ip = row[10]
        switch_name = row[11]

        if os.path.exists(SWITCH_UPLOAD_FOLDER + "get_mac_port_by_ssh.expect"):
            os.system("rm -rf " + SWITCH_UPLOAD_FOLDER + "get_mac_port_by_ssh.expect")
        # 此处要复制文件，否则会失去执行权限
        os.system("cp " + SWITCH_UPLOAD_FOLDER + "ssh_template.expect " + SWITCH_UPLOAD_FOLDER + "get_mac_port_by_ssh.expect")

        # 根据模板生成自动获取mac_port脚本
        new_ssh_name = ssh_name + "@" + str(ip)
        new_ssh_pwd = '{ send "' + ssh_pwd + '\n" }'
        with open(SWITCH_UPLOAD_FOLDER + 'get_mac_port_by_ssh.expect', 'w+') as new_file:
            with open(SWITCH_UPLOAD_FOLDER + 'ssh_template.expect', 'r+') as old_file:
                for line in old_file:
                    if 'admin@127.0.0.1' in line:
                        line = line.replace('admin@127.0.0.1', new_ssh_name)
                    if '{ send "123456\n" }' in line:
                        line = line.replace('{ send "123456\n" }', new_ssh_pwd)
                    new_file.write(line)

        # 执行mac_port脚本获取原始mac_port数据文件
        cmd = "./data/switchinfo/get_mac_port_by_ssh.expect | sed -e 's/^ .*16D//' -e '/^[ \\r<]/d' | sed -n '/MAC/,$p' | awk '{print $1,$4}' >" + SWITCH_UPLOAD_FOLDER + "ssh_mac_port"
        logger.info(cmd)
        os.system(cmd)

        # 清洗数据存数据库
        logger.info(os.path.getsize(SWITCH_UPLOAD_FOLDER + "ssh_mac_port"))
        if os.path.getsize(SWITCH_UPLOAD_FOLDER + "ssh_mac_port") > 0:
            # 读取获得的结果写数据库
            with open(SWITCH_UPLOAD_FOLDER + "ssh_mac_port", 'r+') as f:
                del_str = "delete from switch_mac_port where switch_name='{}'".format(switch_name)
                logger.info(del_str)
                db_proxy.write_db(del_str)
                for line in f.readlines():
                    if not line.startswith("MAC"):  # 去掉标题行
                        # 0050-56c0-0003 GigabitEthernet1/0/24
                        tmp_mac = line[0:14].replace("-", "")
                        mac = re.sub(r"(?<=\w)(?=(?:\w\w)+$)", ":", tmp_mac)
                        port = line.split(" ")[1].strip()
                        insert_sql = "insert into switch_mac_port (switch_name, mac, port) values ('{}','{}','{}')".format(
                            switch_name, mac, port)
                        # logger.info(insert_sql)
                        res = db_proxy.write_db(insert_sql)

        # 删除执行文件
        os.system("rm -rf " + SWITCH_UPLOAD_FOLDER + "get_mac_port_by_ssh.expect")
        os.system("rm -rf " + SWITCH_UPLOAD_FOLDER + "ssh_mac_port")

    def run(self):
        while True:
            try:
                autoGetSwitchInfo.get_all_switch_mac_port()
                time.sleep(60)
            except:
                logger.error(traceback.format_exc())
