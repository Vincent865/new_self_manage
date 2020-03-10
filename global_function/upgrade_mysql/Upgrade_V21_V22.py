#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import logging
import time
import sqlite3
from global_function.global_var import DbProxy
from . import MysqlDbUpgradeBase
import subprocess
import MySQLdb
from subprocess import Popen, PIPE
import traceback

logger = logging.getLogger("sql_update_log")
SQLITE_PATH = "/conf/db/devconfig.db"
SQLITECON = sqlite3.connect(SQLITE_PATH,check_same_thread=False)


# nsm_rptloginfo


class MysqlDbUpgradeC(MysqlDbUpgradeBase):
    """
    实现指定版本到指定版本升级的功能,
    from和to分别对应审计前和升级后版本信息,
    num为run函数下执行的方法个数,用于页面上进度处理及展示
    """
    from_ver = "V2.1"
    to_ver = "V2.2"
    num = 19

    def __init__(self):
        super(MysqlDbUpgradeC, self).__init__()

    @staticmethod
    def addcolumn_users_tables():
        try:
            sql_str = '''alter table users add column editAt varchar(64);'''
            cur = SQLITECON.cursor()
            cmd = sql_str.encode('utf-8')
            cur.execute(cmd)
            SQLITECON.commit()
            logger.info("addcolumn_users_tables success.")
        except:
            logger.error("addcolumn_users_tables error.")

    @staticmethod
    def truncate_traffic_tables():
        db=DbProxy()
        sql_str="truncate sorted_dev_traffic_1h;"
        sql_str1="truncate dev_his_traffic;"
        sql_str2="truncate dev_band_20s;"
        db.write_db(sql_str)
        db.write_db(sql_str1)
        db.write_db(sql_str2)

    @staticmethod
    def alter_sorted_dev_traffic_1h():
        db=DbProxy()
        try:
            MysqlDbUpgradeC.truncate_traffic_tables()
            sql_str="alter table sorted_dev_traffic_1h modify ip varchar(64);"
            db.write_db(sql_str)
        except:
            logger.error("alter table sorted_dev_traffic_1h modify ip error.")

    @staticmethod
    def alter_dev_his_traffic():
        db=DbProxy()
        try:
            sql_str="alter table dev_his_traffic modify ip varchar(64);"
            db.write_db(sql_str)
        except:
            logger.error("alter table dev_his_traffic modify ip error.")

    @staticmethod
    def alter_dev_band_20s():
        db=DbProxy()
        try:
            sql_str="alter table dev_band_20s modify devip varchar(64);"
            db.write_db(sql_str)
        except:
            logger.error("alter table dev_band_20s modify devip error.")

    @staticmethod
    def dropsmtpflowdatas_tables():
        db = DbProxy()
        try:
            sql_str = "DROP TABLE IF EXISTS `smtpflowdatas`"
            db.write_db(sql_str)
        except:
            logger.error("drop table smtpflowdatas error.")

    @staticmethod
    def creat_smtpflowdatas_tables():
        db=DbProxy()
        try:
            sql_str="""CREATE TABLE `smtpflowdatas` (
      `smtpFlowdataId` int(11) NOT NULL AUTO_INCREMENT,
      `flowdataHeadId` int(11) DEFAULT NULL,
      `souceMailAddress` longtext,
      `destMailAddress` longtext,
      `MailTitle` longtext,
      `protocolDetail` int(11) DEFAULT NULL,
      `packetLenth` longtext,
      `packetTimestamp` int(11),
      `createdAt` longtext,
      `flowTimestamp` varchar(30),
      `tableNum` int(5) DEFAULT NULL,
      `direction` int(11) DEFAULT NULL,
      `packetTimestampint` bigint DEFAULT NULL,
      PRIMARY KEY (`smtpFlowdataId`),
      index `time_index` (`flowTimestamp`),
      index `head_index` (`flowdataHeadId`),
      index `packet_time_index` (`packetTimestamp`),
      index `packet_time_int_index` (`packetTimestampint`)
    ) ENGINE=MERGE UNION=(smtpflowdatas_0,smtpflowdatas_1,smtpflowdatas_2,smtpflowdatas_3,smtpflowdatas_4,smtpflowdatas_5,smtpflowdatas_6,smtpflowdatas_7,smtpflowdatas_8,smtpflowdatas_9)  INSERT_METHOD=NO AUTO_INCREMENT=1  DEFAULT CHARSET=utf8;"""
            db.write_db(sql_str)
            logger.info("creat table smtpflowdatas success.")
        except:
            logger.error("creat table smtpflowdatas error.")

    @staticmethod
    def add_smtp_mail_title():
        db=DbProxy()
        try:
            MysqlDbUpgradeC.dropsmtpflowdatas_tables()
            for table_id in range(0, 10):
                sql_str="alter table smtpflowdatas_%d add column MailTitle longtext null default null after destMailAddress;" % table_id
                db.write_db(sql_str)
            logger.info("add_smtp_mail_title write_db success.")
            MysqlDbUpgradeC.creat_smtpflowdatas_tables()
        except:
            logger.error("add_smtp_mail_title error.")

    @staticmethod
    def droppop3flowdatas_tables():
        db = DbProxy()
        try:
            sql_str = "DROP TABLE IF EXISTS `pop3flowdatas`"
            db.write_db(sql_str)
        except:
            logger.error("drop table pop3flowdatas error.")

    @staticmethod
    def creat_pop3flowdatas_tables():
        db=DbProxy()
        try:
            sql_str="""CREATE TABLE `pop3flowdatas` (
    `pop3FlowdataId` int(11) NOT NULL AUTO_INCREMENT,
    `flowdataHeadId` int(11) DEFAULT NULL,
    `souceMailAddress` longtext,
    `destMailAddress` longtext,
    `MailTitle` longtext,
    `protocolDetail` longtext,
    `packetLenth` int(11) DEFAULT NULL,
    `packetTimestamp` int(11),
    `createdAt` longtext,
    `flowTimestamp` varchar(30),
    `tableNum` int(5) DEFAULT NULL,
    `direction` int(11) DEFAULT NULL,
    `packetTimestampint` bigint DEFAULT NULL,
    PRIMARY KEY (`pop3FlowdataId`),
    index `time_index` (`flowTimestamp`),
    index `head_index` (`flowdataHeadId`),
    index `packet_time_index` (`packetTimestamp`),
    index `packet_time_int_index` (`packetTimestampint`)
    ) ENGINE=MERGE UNION=(pop3flowdatas_0,pop3flowdatas_1,pop3flowdatas_2,pop3flowdatas_3,pop3flowdatas_4,pop3flowdatas_5,pop3flowdatas_6,pop3flowdatas_7,pop3flowdatas_8,pop3flowdatas_9)  INSERT_METHOD=NO AUTO_INCREMENT=1  DEFAULT CHARSET=utf8;"""
            db.write_db(sql_str)
            logger.info("add table pop3flowdatas success.")
        except:
            logger.error("add table pop3flowdatas error.")

    @staticmethod
    def add_pop3_mail_title():
        db=DbProxy()
        try:
            MysqlDbUpgradeC.droppop3flowdatas_tables()
            for table_id in range(0, 10):
                sql_str="alter table pop3flowdatas_%d add column MailTitle longtext null default null after destMailAddress;" % table_id
                db.write_db(sql_str)
            logger.info("add_smtp_mail_title write_db success.")
            MysqlDbUpgradeC.creat_pop3flowdatas_tables()
        except:
            logger.error("add_pop3_mail_title error.")

    @staticmethod
    def drop_gooseflowdatas_tables():
        db = DbProxy()
        try:
            sql_str = "DROP TABLE IF EXISTS `gooseflowdatas`"
            db.write_db(sql_str)
        except:
            logger.error("drop_gooseflowdatas_tables error.")

    @staticmethod
    def creat_gooseflowdatas_tables():
        db = DbProxy()
        try:
            sql_str = """CREATE TABLE `gooseflowdatas` (
    `gooseFlowdataId` int(11) NOT NULL AUTO_INCREMENT,
    `flowdataHeadId` int(11) DEFAULT NULL,
    `datSet` longtext,
    `goID` longtext,
    `allData` longtext,
    `packetLenth` int(11) DEFAULT NULL,
    `packetTimestamp` int(11),
    `createdAt` longtext,
    `flowTimestamp` varchar(30),
    `tableNum` int(5) DEFAULT NULL,
    `direction` int(11) DEFAULT NULL,
    `packetTimestampint` bigint DEFAULT NULL,
    PRIMARY KEY (`gooseFlowdataId`),
    index `time_index` (`flowTimestamp`),
    index `head_index` (`flowdataHeadId`),
    index `packet_time_index` (`packetTimestamp`),
    index `packet_time_int_index` (`packetTimestampint`)
    ) ENGINE=MERGE UNION=(gooseflowdatas_0,gooseflowdatas_1,gooseflowdatas_2,gooseflowdatas_3,gooseflowdatas_4,gooseflowdatas_5,gooseflowdatas_6,gooseflowdatas_7,gooseflowdatas_8,gooseflowdatas_9)  INSERT_METHOD=NO AUTO_INCREMENT=1  DEFAULT CHARSET=utf8;"""
            db.write_db(sql_str)
            logger.info("add_gooseflowdatas_tables success.")
        except:
            logger.error("add_gooseflowdatas_tables error.")

    @staticmethod
    def add_goose_alldata_column():
        db = DbProxy()
        try:
            MysqlDbUpgradeC.drop_gooseflowdatas_tables()
            for table_id in range(0, 10):
                sql_str = "alter table gooseflowdatas_%d add column allData longtext null default null after goID;" % table_id
                db.write_db(sql_str)
            logger.info("add_goose_alldata_column write_db success.")
            MysqlDbUpgradeC.creat_gooseflowdatas_tables()
        except:
            logger.error("add_goose_alldata_column error.")

    @staticmethod
    def drop_s7plusflowdatas_tables():
        db = DbProxy()
        try:
            sql_str = "DROP TABLE IF EXISTS `s7plusflowdatas`"
            db.write_db(sql_str)
        except:
            logger.error("drop_s7plusflowdatas_tables error.")

    @staticmethod
    def create_s7plusflowdatas_tables():
        db = DbProxy()
        try:
            sql_str = """CREATE TABLE `s7plusflowdatas` (
    `s7plusFlowdataId` int(11) NOT NULL AUTO_INCREMENT,
    `flowdataHeadId` int(11) DEFAULT NULL,
    `opcode` longtext,
    `funcCode` longtext,
    `reserved1` longtext,
    `reserved2` longtext,
    `reserved3` longtext,
    `reserved4` longtext,
    `reserved5` longtext,
    `reserved6` longtext,
    `packetLenth` int(11) DEFAULT NULL,
    `packetTimestamp` int(11),
    `createdAt` longtext,
    `flowTimestamp` varchar(30),
    `tableNum` int(5) DEFAULT NULL,
    `direction` int(11) DEFAULT NULL,
    `packetTimestampint` bigint DEFAULT NULL,
    PRIMARY KEY (`s7plusFlowdataId`),
    index `time_index` (`flowTimestamp`),
    index `packet_time_index` (`packetTimestamp`)
    ) ENGINE=MERGE UNION=(s7plusflowdatas_0,s7plusflowdatas_1,s7plusflowdatas_2,s7plusflowdatas_3,s7plusflowdatas_4,s7plusflowdatas_5,s7plusflowdatas_6,s7plusflowdatas_7,s7plusflowdatas_8,s7plusflowdatas_9)  INSERT_METHOD=NO AUTO_INCREMENT=1  DEFAULT CHARSET=utf8;"""
            db.write_db(sql_str)
            logger.info("add table s7plusflowdatas success.")
        except:
            logger.error("add table s7plusflowdatas error.")

    @staticmethod
    def add_s7plusflowdatas_tables():
        db=DbProxy()
        try:
            for table_id in range(0, 10):
                sql_str="""CREATE TABLE `s7plusflowdatas_%d` (
      `s7plusFlowdataId` int(11) NOT NULL AUTO_INCREMENT,
      `flowdataHeadId` int(11) DEFAULT NULL,
      `opcode` longtext,
      `funcCode` longtext,
      `reserved1` longtext,
      `reserved2` longtext,
      `reserved3` longtext,
      `reserved4` longtext,
      `reserved5` longtext,
      `reserved6` longtext,
      `packetLenth` int(11) DEFAULT NULL,
      `packetTimestamp` int(11),
      `createdAt` longtext,
      `flowTimestamp` varchar(30),
      `tableNum` int(5) DEFAULT 0,
      `direction` int(11) DEFAULT NULL,
      `packetTimestampint` bigint DEFAULT NULL,
      PRIMARY KEY (`s7plusFlowdataId`),
      index `time_index` (`flowTimestamp`),
      index `packet_time_index` (`packetTimestamp`)
    ) ENGINE=MYISAM DEFAULT CHARSET=utf8;""" % (table_id)
                db.write_db(sql_str)
            MysqlDbUpgradeC.create_s7plusflowdatas_tables()
            logger.info("add_s7plusflowdatas_tables success.")
        except:
            logger.error("add_s7plusflowdatas_tables error.")

    @staticmethod
    def add_macfilter_table():
        db = DbProxy()
        try:
            sql_str = """CREATE TABLE `mac_filter` (
                    `id` int not null primary key auto_increment,
                    `mac` varchar(32),
                    `enable` int(6) DEFAULT 0
                    ) ENGINE=MYISAM DEFAULT CHARSET=utf8;"""
            db.write_db(sql_str)
            logger.info("add table macfilter success.")
        except:
            logger.error("add table macfilter error.")

    @staticmethod
    def add_topdev_table():
        try:
            process = subprocess.Popen(
                '/app/local/mysql-5.6.31-linux-glibc2.5-x86_64/bin/mysql -ukeystone -pOptValley@4312',
                stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            process.stdin.write('use keystone\n')
            process.stdin.write('source /app/local/share/new_self_manage/global_function/upgrade_mysql/top_V21_V22.sql\n')
            process.stdin.write('exit\n')
            process.wait()
            logger.info("add table topdev success.")
        except:
            logger.error("add table topdev error.")

    @staticmethod
    def drop_pwdaging_table():
        db = DbProxy()
        try:
            sql_str = "DROP TABLE IF EXISTS `pwd_aging`"
            db.write_db(sql_str)
        except:
            logger.error("drop_pwdaging_table error.")

    @staticmethod
    def add_pwdaging_table():
        db = DbProxy()
        try:
            MysqlDbUpgradeC.drop_pwdaging_table()
            sql_str = "create table `pwd_aging` (`valid_type` int(11) default 0)"
            db.write_db(sql_str)
            insert_str = "INSERT INTO `pwd_aging` VALUES (0)"
            db.write_db(insert_str)
            logger.info("add_pwdaging_table success.")
        except:
            logger.error("add_pwdaging_table error.")

    @staticmethod
    def add_bhvflowdataheads():
        db = DbProxy()
        try:
            drop_str = "DROP TABLE IF EXISTS `bhvflowdataheads`"
            db.write_db(drop_str)
            sql_str="""CREATE TABLE `bhvflowdataheads` (
              `flowdataHeadId` int(11) DEFAULT NULL,
              `flowTimestamp` varchar(30),
              `packetTimestamp` int(11),
              `sourceMac` longtext,
              `destinationMac` longtext,
              `ipVersion` int(11) DEFAULT NULL,
              `sourceIp` longtext,
              `sourcePort` int(11) DEFAULT NULL,
              `destinationIp` longtext,
              `destinationPort` int(11) DEFAULT NULL,
              `protocolType` int(11) DEFAULT NULL,
              `protocolTypeName` longtext,
              `packetLenth` int(11) DEFAULT NULL,
              `protocolSourceName` longtext,
              `directions` int(11) DEFAULT NULL,
              `packetTimestampint` bigint DEFAULT NULL,
              index `time_index` (`flowTimestamp`),
              index `id_index` (`flowdataHeadId`),
              index `packet_time_index` (`packetTimestamp`),
              index `packet_time_int_index` (`packetTimestampint`)
            ) ENGINE=MYISAM DEFAULT CHARSET=utf8;"""
            db.write_db(sql_str)
            logger.info("add_bhvflowdataheads run success.")
            return True
        except:
            logger.error("add_bhvflowdataheads run error.")
            return False

    @staticmethod
    def add_s7bhvAduitdatas():
        db = DbProxy()
        try:
            drop_str = "DROP TABLE IF EXISTS `s7bhvAduitdatas`"
            db.write_db(drop_str)
            for table_id in range(0, 10):
                sql_str = """CREATE TABLE `s7bhvAduitdatas_%d` (
                  `s7FlowdataId` int(11) NOT NULL AUTO_INCREMENT,
                  `flowdataHeadId` int(11) DEFAULT NULL,
                  `type` longtext,
                  `content` longtext,
                  `packetLenth` int(11) DEFAULT NULL,
                  `packetTimestamp` int(11),
                  `createdAt` longtext,
                  `flowTimestamp` varchar(30),
                  `tableNum` int(5) DEFAULT 0,
                  `direction` int(11) DEFAULT NULL,
                  `packetTimestampint` bigint DEFAULT NULL,
                  PRIMARY KEY (`s7FlowdataId`),
                  index `time_index` (`flowTimestamp`),
                  index `head_index` (`flowdataHeadId`),
                  index `packet_time_index` (`packetTimestamp`),
                  index `packet_time_int_index` (`packetTimestampint`)
                ) ENGINE=MYISAM DEFAULT CHARSET=utf8;"""%table_id
                db.write_db(sql_str)
            sql_str = """CREATE TABLE `s7bhvAduitdatas` (
              `s7FlowdataId` int(11) NOT NULL AUTO_INCREMENT,
              `flowdataHeadId` int(11) DEFAULT NULL,
              `type` longtext,
              `content` longtext,
              `packetLenth` int(11) DEFAULT NULL,
              `packetTimestamp` int(11),
              `createdAt` longtext,
              `flowTimestamp` varchar(30),
              `tableNum` int(5) DEFAULT NULL,
              `direction` int(11) DEFAULT NULL,
              `packetTimestampint` bigint DEFAULT NULL,
              PRIMARY KEY (`s7FlowdataId`),
              index `time_index` (`flowTimestamp`),
              index `head_index` (`flowdataHeadId`),
              index `packet_time_index` (`packetTimestamp`),
              index `packet_time_int_index` (`packetTimestampint`)
            ) ENGINE=MERGE UNION=(s7bhvAduitdatas_0,s7bhvAduitdatas_1,s7bhvAduitdatas_2,s7bhvAduitdatas_3,s7bhvAduitdatas_4,s7bhvAduitdatas_5,s7bhvAduitdatas_6,s7bhvAduitdatas_7,s7bhvAduitdatas_8,s7bhvAduitdatas_9)  INSERT_METHOD=NO AUTO_INCREMENT=1  DEFAULT CHARSET=utf8;"""
            db.write_db(sql_str)
            logger.info("add_s7bhvAduitdatas run success.")
            return True
        except:
            logger.error("add_s7bhvAduitdatas run error.")
            return False

    @staticmethod
    def create_keystoneconfig():
        conn = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='')
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE keystone_config CHARACTER SET utf8 COLLATE utf8_general_ci;")
        cursor.execute("GRANT ALL PRIVILEGES ON keystone_config.* TO 'keystone'@'localhost' WITH GRANT OPTION;")
        conn.commit()
        cursor.close()
        conn.close()
        process = Popen(
            '/app/local/mysql-5.6.31-linux-glibc2.5-x86_64/bin/mysql -ukeystone -pOptValley@4312',
            stdout=PIPE, stdin=PIPE, shell=True)
        try:
            process.stdin.write('use keystone_config\n')
            process.stdin.write(
                'source /app/local/share/new_self_manage/global_function/upgrade_mysql/keystone_config_v2.2.sql\n')
            process.stdin.write('exit\n')
            process.wait()
            logger.info("source keystone_config_v2.2.sql ok")
        except:
            logger.error('source keystone_config_v2.2.sql error')
            logger.error(traceback.format_exc())

    @staticmethod
    def add_devconfig():
        db_proxy = DbProxy("keystone_config")
        devconfig_table = ('users', 'dbcleanconfig', 'managementmode',
                           'ipaccessrestrict', 'dpi_mode',
                           'nsm_sysbackupmode', 'nsm_protoswitch', 'nsm_rptalarmmode',
                           'nsm_rptprotomode', 'nsm_rptlogmode')
        conn = sqlite3.connect('/conf/db/devconfig.db')
        cur = conn.cursor()
        for t in devconfig_table:
            tmp_sql = 'select * from %s' % t
            cur.execute(tmp_sql)
            rows = cur.fetchall()
            tmp_sql = 'TRUNCATE TABLE %s' % t
            db_proxy.write_db(tmp_sql)
            tmp_start = 'insert into %s values(' % t
            for row in rows:
                tmp_ins = tmp_start
                for r in row:
                    if r is not None:
                        if isinstance(r, str) or isinstance(r, unicode):
                            tmp_ins += "'"
                            tmp_ins += r
                            tmp_ins += "'"
                        else:
                            tmp_ins += str(r)
                    else:
                        tmp_ins += "NULL"
                    tmp_ins += ','
                tmp_ins = tmp_ins[:-1]
                tmp_ins += ')'
                db_proxy.write_db(tmp_ins)

    @staticmethod
    def update_protoswitch():
        db_proxy=DbProxy("keystone_config")
        sql_str = "select proto_bit_map from nsm_protoswitch"
        _, rows = db_proxy.read_db(sql_str)
        proto_bitmap = rows[0][0]
        proto_list=[]
        for i in range(22):
            if ((proto_bitmap & (1 << i)) != 0):
                proto_list.append(1)
            else:
                proto_list.append(0)
        proto_list.append(1)
        proto_switch_bitmap=0x007FFFFF
        for i in range(len(proto_list)):
            if (proto_list[i] == 0):
                tmp_bitmap=0xFFFFFFFF & (~(1 << i))
                proto_switch_bitmap=proto_switch_bitmap & tmp_bitmap
        update_str = "update nsm_protoswitch set proto_bit_map = %d" % proto_switch_bitmap
        db_proxy.write_db(update_str)

    @staticmethod
    def set_users_editat():
        db_proxy = DbProxy("keystone_config")
        tmp_str = "update users set editAt='946656000'"
        db_proxy.write_db(tmp_str)

    @staticmethod
    def add_keystoneconfig():
        tmp_name = 'tmp.sql'
        content_list = []
        keystoneconfig_table = ('customrules', 'definedprotocol', 'dev_band_threshold', 'ipmaclist', 'rules',
                                'signatures', 'vulnerabilities', 'whiteliststudy', 'nsm_flowfull',
                                'nsm_flowaudit', 'nsm_flowftpinfo', 'nsm_dbgcollect', 'nsm_sysbackupinfo',
                                'nsm_confsave', 'auditstrategy', 'nsm_raidstatus', 'dev_name_conf')
        dump_str = "mysqldump -t -c keystone "
        for t in keystoneconfig_table:
            dump_str += t
            dump_str += ' '
        dump_str += "-ukeystone -pOptValley@4312 > %s" % tmp_name
        child = Popen(dump_str, stdout=PIPE, stdin=PIPE, shell=True)
        child.wait()
        with open(tmp_name, 'r+') as f:
            for line in f:
                for name in keystoneconfig_table:
                    find_str = "LOCK TABLES `%s` WRITE;" % name
                    pos = line.find(find_str)
                    if pos >= 0:
                        append_str = "TRUNCATE TABLE %s;\n" % name
                        content_list.append(append_str)
                content_list.append(line)
        with open(tmp_name, 'w+') as f:
            f.writelines(content_list)
        process = Popen(
            '/app/local/mysql-5.6.31-linux-glibc2.5-x86_64/bin/mysql -ukeystone -pOptValley@4312',
            stdout=PIPE, stdin=PIPE, shell=True)
        process.stdin.write('use keystone_config\n')
        process.stdin.write('source %s\n' % tmp_name)
        process.stdin.write('exit\n')
        process.wait()

    @staticmethod
    def del_keystonetable():
        keystoneconfig_table = ('customrules', 'definedprotocol', 'dev_band_threshold', 'ipmaclist', 'rules',
                                'signatures', 'vulnerabilities', 'whiteliststudy', 'nsm_flowfull',
                                'nsm_flowaudit', 'nsm_flowftpinfo', 'nsm_dbgcollect', 'nsm_sysbackupinfo',
                                'nsm_confsave', 'nsm_rptalarminfo', 'nsm_rptprotoinfo', 'nsm_rptloginfo',
                                'auditstrategy', 'nsm_raidstatus', 'dev_name_conf')
        db_proxy = DbProxy()
        for t in keystoneconfig_table:
            sql_str = 'DROP TABLE IF EXISTS %s' % t
            db_proxy.write_db(sql_str)

    @staticmethod
    def run():
        try:
            MysqlDbUpgradeC.addcolumn_users_tables()
            MysqlDbUpgradeC.add_process()
            MysqlDbUpgradeC.add_smtp_mail_title()
            MysqlDbUpgradeC.add_process()
            MysqlDbUpgradeC.add_pop3_mail_title()
            MysqlDbUpgradeC.add_process()
            MysqlDbUpgradeC.add_goose_alldata_column()
            MysqlDbUpgradeC.add_process()
            MysqlDbUpgradeC.add_s7plusflowdatas_tables()
            MysqlDbUpgradeC.add_process()
            MysqlDbUpgradeC.add_macfilter_table()
            MysqlDbUpgradeC.add_process()
            MysqlDbUpgradeC.add_topdev_table()
            MysqlDbUpgradeC.add_process()
            MysqlDbUpgradeC.add_pwdaging_table()
            MysqlDbUpgradeC.add_process()
            MysqlDbUpgradeC.add_bhvflowdataheads()
            MysqlDbUpgradeC.add_process()
            MysqlDbUpgradeC.add_s7bhvAduitdatas()
            MysqlDbUpgradeC.add_process()
            MysqlDbUpgradeC.create_keystoneconfig()
            MysqlDbUpgradeC.add_process()
            MysqlDbUpgradeC.add_devconfig()
            MysqlDbUpgradeC.add_process()
            MysqlDbUpgradeC.update_protoswitch()
            MysqlDbUpgradeC.add_process()
            MysqlDbUpgradeC.set_users_editat()
            MysqlDbUpgradeC.add_process()
            MysqlDbUpgradeC.add_keystoneconfig()
            MysqlDbUpgradeC.add_process()
            MysqlDbUpgradeC.del_keystonetable()
            MysqlDbUpgradeC.add_process()
            MysqlDbUpgradeC.alter_dev_band_20s()
            MysqlDbUpgradeC.add_process()
            MysqlDbUpgradeC.alter_dev_his_traffic()
            MysqlDbUpgradeC.add_process()
            MysqlDbUpgradeC.alter_sorted_dev_traffic_1h()
            MysqlDbUpgradeC.add_process()
            logger.info("MysqlDbUpgrade_2.1_2.2 run finished.")
            return True
        except:
            logger.error("MysqlDbUpgrade_2.1_2.2 run error.")
            logger.error(traceback.format_exc())
            return False


if __name__ == '__main__':
    MysqlDbUpgradeC.run()
