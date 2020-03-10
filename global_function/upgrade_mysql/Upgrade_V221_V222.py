#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging
from global_function.global_var import DbProxy
from . import MysqlDbUpgradeBase
import traceback
from subprocess import Popen, PIPE

logger = logging.getLogger("sql_update_log")
db = DbProxy()


class MysqlDbUpgradeE(MysqlDbUpgradeBase):
    """
    新增自定义协议表
    """
    from_ver = "V2.2.1"
    to_ver = "V2.2.2"
    num = 18
    def __init__(self):
        super(MysqlDbUpgradeE, self).__init__()

    @staticmethod
    def add_service_info():
        """
        自定义协议: 增加预定义协议表
        :return:
        """
        cre_str = """CREATE TABLE `service_info` (
  `id` int not null primary key auto_increment,
  `service_name` varchar(64),
  `service_desc` varchar(64),
  `service_proto` varchar(16),
  `service_port` int,
  `service_type` int
) ENGINE=MYISAM DEFAULT CHARSET=utf8;
        """
        add_str = "insert into service_info(service_name,service_desc,service_proto,service_port,service_type) values('Modbus-TCP','Modbus-TCP','TCP',502,0),('IEC104','IEC104','TCP',2404,0),('ENIP-TCP','ENIP','TCP',44818,0),('ENIP-UDP','ENIP','UDP',44818,0),('ENIP-IO','ENIP','UDP',2222,0),('DNP3','DNP3','any',0,0),('OPCDA','OPCDA','any',0,0),('S7','S7','any',0,0),('MMS','MMS','any',0,0),('PROFINET-IO','PROFINET-IO','any',0,0),('OPCUA-TCP','OPCUA-TCP','TCP',4840,0),('ORACLE','ORACLE','any',0,0),('SQL-Server','SQL-Server','TCP',1433,0),('HTTP','HTTP','TCP',80,0),('FTP','FTP','TCP',21,0),('FTP-DATA','FTP','TCP',20,0),('SNMP','SNMP','UDP',161,0),('SNMPTRAP','SNMP','UDP',162,0),('TELNET','TELNET','TCP',23,0),('POP3','POP3','TCP',110,0),('SMTP','SMTP','any',0,0),('GOOSE','GOOSE','any',0,0),('SV','SV','any',0,0),('PNRT-DCP','PNRT-DCP','any',0,0),('SIP','SIP','UDP',5060,0),('SIP1','SIP','UDP',5061,0)"
        db_config=DbProxy("keystone_config")
        try:
            db_config.write_db(cre_str)
            db_config.write_db(add_str)
            logger.info("add_service_info ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("add_service_info error.")

    @staticmethod
    def add_self_define_proto_config():
        """
        自定义协议配置表
        """
        add_str = """CREATE TABLE `self_define_proto_config` (
  `proto_id` int(11) NOT NULL AUTO_INCREMENT,
  `proto_port` int(11) DEFAULT NULL,
  `proto_type` int(11) DEFAULT NULL,
  `proto_name` varchar(128) DEFAULT NULL,
  `status` int(11) DEFAULT 1,
  `content_id` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`proto_id`)
) ENGINE=MyISAM AUTO_INCREMENT=501 DEFAULT CHARSET=utf8;"""
        db_config=DbProxy("keystone_config")
        try:
            db_config.write_db(add_str)
            logger.info("create add_self_define_proto_config tables ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("create add_self_define_proto_config tables error.")

    @staticmethod
    def add_content_model():
        """
        自定义协议content解析规则表
        :return:
        """
        cre_str1="""CREATE TABLE `content_model` (
  `content_id` int(11) NOT NULL AUTO_INCREMENT,
  `content_name` varchar(128) DEFAULT NULL,
  `content_desc` varchar(128) DEFAULT NULL,
  `start_offset` int(11) DEFAULT NULL,
  `depth` int(11) DEFAULT NULL,
  `content` varchar(64) DEFAULT NULL,
  `audit_value_num` int(11) DEFAULT NULL,
  `offset_1` int(11) DEFAULT NULL,
  `length_1` int(11) DEFAULT NULL,
  `audit_name_1` varchar(64) DEFAULT NULL,
  `value_map_id_1` int(11) DEFAULT NULL,
  `offset_2` int(11) DEFAULT NULL,
  `length_2` int(11) DEFAULT NULL,
  `audit_name_2` varchar(64) DEFAULT NULL,
  `value_map_id_2` int(11) DEFAULT NULL,
  `offset_3` int(11) DEFAULT NULL,
  `length_3` int(11) DEFAULT NULL,
  `audit_name_3` varchar(64) DEFAULT NULL,
  `value_map_id_3` int(11) DEFAULT NULL,
  `offset_4` int(11) DEFAULT NULL,
  `length_4` int(11) DEFAULT NULL,
  `audit_name_4` varchar(64) DEFAULT NULL,
  `value_map_id_4` int(11) DEFAULT NULL,
  `offset_5` int(11) DEFAULT NULL,
  `length_5` int(11) DEFAULT NULL,
  `audit_name_5` varchar(64) DEFAULT NULL,
  `value_map_id_5` int(11) DEFAULT NULL,
  PRIMARY KEY (`content_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8"""
        db_config = DbProxy("keystone_config")
        try:
            db_config.write_db(cre_str1)
            logger.error("create add_content_model tables ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("create add_content_model tables error.")

    @staticmethod
    def add_value_map_model():
        """
        自定义协议:特征值翻译表
        :return:
        """
        add_str="""CREATE TABLE `value_map_model` (
  `value_id` int(11) NOT NULL AUTO_INCREMENT,
  `value_map_id` int(11) DEFAULT NULL,
  `value_model_name` varchar(128) DEFAULT NULL,
  `value_model_desc` varchar(128) DEFAULT NULL,
  `audit_value` varchar(128) DEFAULT NULL,
  `value_desc` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`value_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;"""
        db_config = DbProxy("keystone_config")
        try:
            db_config.write_db(add_str)
            logger.info("create add_value_map_model tables ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("create add_value_map_model tables error.")

    @staticmethod
    def create_pcap_tables():
        """
        在线抓包功能:状态表
        :return:
        """
        cre_str1 = """CREATE TABLE `pcap_down_status` (
   `id` INT UNSIGNED AUTO_INCREMENT,
   `flag` int NOT NULL,
   `pcap_name` VARCHAR(40) NOT NULL,
   `pcap_orig_size` VARCHAR(40) NOT NULL,
   `pcap_orig_time` VARCHAR(40) NOT NULL,
   `pcap_cur_size` VARCHAR(40) NOT NULL,
   `pcap_cur_time` VARCHAR(40) NOT NULL,
   `pcap_start_time` VARCHAR(40) NOT NULL,
   PRIMARY KEY (`id`)
)ENGINE=MYISAM DEFAULT CHARSET=utf8;"""
        cre_str2 = """CREATE TABLE `pcap_down_data` (
   `id` INT UNSIGNED AUTO_INCREMENT,
   `finish_time` VARCHAR(40) NOT NULL,
   `pcap_name` VARCHAR(40) NOT NULL,
   `pcap_cur_size` VARCHAR(40) NOT NULL,
   `pcap_cur_time` VARCHAR(40) NOT NULL,
   `pcap_path` VARCHAR(64) NOT NULL,
   PRIMARY KEY (`id`)
)ENGINE=MYISAM DEFAULT CHARSET=utf8;"""
        add_str = "insert into pcap_down_status(flag,pcap_orig_size,pcap_orig_time,pcap_cur_size,pcap_cur_time,pcap_name,pcap_start_time) values (0, 0, 0,0,0,'',0)"
        db_config = DbProxy("keystone_config")
        try:
            db_config.write_db(cre_str1)
            db_config.write_db(cre_str2)
            db_config.write_db(add_str)
            logger.error("create pcap tables ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("create pcap tables error.")

    @staticmethod
    def add_asset_report_tables():
        """
        资产报告:资产报告表
        :return:
        """
        cre_str = """CREATE TABLE `nsm_rptassetsinfo` (
  `id` int not null primary key auto_increment,
  `report_name` longtext,
  `report_time` longtext,
  `report_freq` int,
  `report_raw_file` longtext,
  `report_statics_file` longtext
) ENGINE=MYISAM DEFAULT CHARSET=utf8"""
        cre_str1 = """CREATE TABLE `nsm_rptassetsmode` (
	`flag`	int(11) NOT NULL
)ENGINE=MYISAM DEFAULT CHARSET=utf8"""
        add_str = "INSERT INTO `nsm_rptassetsmode` VALUES (2)"
        db_config = DbProxy("keystone_config")
        try:
            db_config.write_db(cre_str)
            db_config.write_db(cre_str1)
            db_config.write_db(add_str)
            logger.info("add_asset_report_tables ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("add_asset_report_tables error.")

    @staticmethod
    def add_license_info_tables():
        """
        license功能:license信息表
        :return:
        """
        cre_str = """CREATE TABLE `license_info` (
  `id` int not null primary key auto_increment,
  `license_legal` longtext,
  `license_time` longtext,
  `license_func` longtext,
  `license_key` longtext
) ENGINE=MYISAM DEFAULT CHARSET=utf8"""
        add_str = "INSERT INTO license_info (license_legal,license_time, license_func,license_key) VALUES('1','0','0','')"
        db_config = DbProxy("keystone_config")
        try:
            db_config.write_db(cre_str)
            db_config.write_db(add_str)
            logger.info("add_license_info_tables ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("add_license_info_tables error.")

    @staticmethod
    def create_alarm_tables():
        """
        告警开关设置表
        :return:
        """
        cre_sql = """CREATE TABLE `alarm_switch`(
    `flow_status` INT(11)
)ENGINE=MYISAM DEFAULT CHARSET=utf8;"""
        insert_sql = "INSERT INTO `alarm_switch`(flow_status)VALUES(0);"
        db_config = DbProxy("keystone_config")
        try:
            db_config.write_db(cre_sql)
            db_config.write_db(insert_sql)
            logger.info("create alarm tables ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("create alarm tables error.")

    @staticmethod
    def create_table_devtype():
        """
        资产优化功能:增加设备类型表
        :return:
        """
        cre_sql = """CREATE TABLE `dev_type` (
  `type_id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(64) DEFAULT NULL,
  `pre_define` varchar(64) DEFAULT "0",
  `res_1` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`type_id`)
)ENGINE=MYISAM DEFAULT CHARSET=utf8;"""
        insert_sql = """insert into dev_type (device_name,pre_define) values ("PC", "1"),("工程师站", "1"),("操作员站", "1"),("PLC", "1"),("RTU", "1"),("HMI", "1"),("网络设备", "1"),("服务器", "1"),("OPC服务器", "1"),("DCS", "1"),("安全设备", "1"),("IED", "1");"""
        db_config = DbProxy("keystone_config")
        try:
            db_config.write_db(cre_sql)
            db_config.write_db(insert_sql)
            logger.info("create_table_devtype ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("create_table_devtype error.")

    @staticmethod
    def alter_table_users():
        """
        单机登陆功能:用户表增加更新时间
        :return:
        """
        alter_sql = "alter table users add column last_update varchar(64) default null after editAt"
        db_config = DbProxy("keystone_config")
        try:
            db_config.write_db(alter_sql)
            logger.info("alter_table_users ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("alter_table_users error.")

    @staticmethod
    def alter_table_top_config():
        """
        升级后默认资产告警周期为五分钟
        :return:
        """
        alter_sql = "update top_config set check_time=5 where check_time=1"
        db_config = DbProxy("keystone_config")
        try:
            db_config.write_db(alter_sql)
            logger.info("alter_table_top_config ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("alter_table_top_config error.")

    @staticmethod
    def add_log_audit_tables():
        """
        日志审计:添加日志审计表
        :return:
        """
        cre_str = """CREATE TABLE `comm_param` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `seq` INT NOT NULL default 1,
  `serverdev_dcport` INT NOT NULL default 8800,
  `protectdev_dcport` INT NOT NULL default 514,
  `netdev_trapport` INT NOT NULL default 162,
  `agentport` INT NOT NULL default 8801,
  `mgmt_ip1` BLOB,
  `event_port1` INT NOT NULL default 8800,
  `ip1_permission` INT NOT NULL default 0,
  `reserver1` INT NOT NULL default 0,
  `mgmt_ip2` BLOB,
  `event_port2` INT NOT NULL default 8800,
  `ip2_permission` INT NOT NULL default 0,
  `reserver2` INT NOT NULL default 0,
  `mgmt_ip3` BLOB,
  `event_port3` INT NOT NULL default 8800,
  `ip3_permission` INT NOT NULL default 0,
  `reserver3` INT NOT NULL default 0,
  `mgmt_ip4` BLOB,
  `event_port4` INT NOT NULL default 8800,
  `ip4_permission` INT NOT NULL default 0,
  `reserver4` INT NOT NULL default 0,
  PRIMARY KEY (`id`))
ENGINE = MyISAM"""
        add_str = "INSERT INTO comm_param ( serverdev_dcport, protectdev_dcport) VALUES (8800, 514)"
        cre_str1 = """CREATE TABLE `tb_static_route_config` (
          `id` int not null primary key auto_increment,
          `d_ip_mask` varchar(64),
          `next_gateway` varchar(64),
          `ip_type` int
        ) ENGINE=MYISAM DEFAULT CHARSET=utf8"""
        db_config = DbProxy("keystone_config")
        try:
            db_config.write_db(cre_str)
            db_config.write_db(add_str)
            db_config.write_db(cre_str1)
            logger.info("add_log_audit_tables ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("add_log_audit_tables error")

    @staticmethod
    def add_cusproto_tables():
        """
        自定义协议:自定义协议审计详情表
        :return:
        """
        for table_id in range(0, 10):
            add_str = """CREATE TABLE `cusprotoflowdatas_%d` (
      `cusprotoFlowdataId` int(11) NOT NULL AUTO_INCREMENT,
      `flowdataHeadId` int(11) DEFAULT NULL,
      `proto_id` int(11) DEFAULT NULL,
      `protocolDetail` longtext,
      `packetLenth` int(11) DEFAULT NULL,
      `packetTimestamp` int(11),
      `createdAt` longtext,
      `flowTimestamp` varchar(30),
      `tableNum` int(5) DEFAULT 4,
      `direction` int(11) DEFAULT NULL,
      `packetTimestampint` bigint DEFAULT NULL,
      PRIMARY KEY (`cusprotoFlowdataId`),
      index `time_index` (`flowTimestamp`),
      index `head_index` (`flowdataHeadId`),
      index `packet_time_index` (`packetTimestamp`),
      index `packet_time_int_index` (`packetTimestampint`)
    ) ENGINE=MYISAM DEFAULT CHARSET=utf8;""" % (table_id)
            try:
                db.write_db(add_str)
                logger.info("create add_value_map_model tables_%d ok." % table_id)
            except:
                logger.error(traceback.format_exc())
                logger.error("create add_value_map_model tables_%d error."%table_id)
        add_str = """CREATE TABLE `cusprotoflowdatas` (
      `cusprotoFlowdataId` int(11) NOT NULL AUTO_INCREMENT,
      `flowdataHeadId` int(11) DEFAULT NULL,
      `proto_id` int(11) DEFAULT NULL,
      `protocolDetail` longtext,
      `packetLenth` int(11) DEFAULT NULL,
      `packetTimestamp` int(11),
      `createdAt` longtext,
      `flowTimestamp` varchar(30),
      `tableNum` int(5) DEFAULT NULL,
      `direction` int(11) DEFAULT NULL,
      `packetTimestampint` bigint DEFAULT NULL,
      PRIMARY KEY (`cusprotoFlowdataId`),
      index `time_index` (`flowTimestamp`),
      index `head_index` (`flowdataHeadId`),
      index `packet_time_index` (`packetTimestamp`),
      index `packet_time_int_index` (`packetTimestampint`)
    ) ENGINE=MERGE UNION=(cusprotoflowdatas_0,cusprotoflowdatas_1,cusprotoflowdatas_2,cusprotoflowdatas_3,cusprotoflowdatas_4,cusprotoflowdatas_5,cusprotoflowdatas_6,cusprotoflowdatas_7,cusprotoflowdatas_8,cusprotoflowdatas_9)  INSERT_METHOD=NO AUTO_INCREMENT=1  DEFAULT CHARSET=utf8;"""
        try:
            db.write_db(add_str)
            logger.info("create add_value_map_model tables ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("create add_value_map_model tables error.")

    @staticmethod
    def add_da_31992_data_acquire():
        """
        日志审计表:增加日志审计存储表
        :return:
        """
        for table_id in range(1, 13):
            add_str = """CREATE TABLE IF NOT EXISTS `da_31992_data_acquire_%d` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `timestamp` INT NOT NULL,
  `utimestamp` BIGINT(20) NOT NULL,
  `infotime` INT NULL,
  `devtype` INT NULL,
  `level` INT NULL,
  `ip` INT UNSIGNED NULL,
  `hostname` VARCHAR(256) NULL,
  `reserve1` INT NULL,
  `reserve2` INT NULL,
  `detailinfo` LONGTEXT NULL,
  `table_id` INT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  INDEX `index_time` (`utimestamp` ASC),
  INDEX `index_table` (`table_id` ASC),
  INDEX `index_info` (`infotime` ASC),
  INDEX `index_ip` (`ip` ASC),
  INDEX `index_type` (`devtype` ASC),
  INDEX `index_level` (`level` ASC))
ENGINE = MyISAM""" % table_id
            try:
                db.write_db(add_str)
                logger.info("add_da_31992_data_acquire_%d ok." % table_id)
            except:
                logger.error(traceback.format_exc())
                logger.error("add_da_31992_data_acquire_%d error." % table_id)
        cre_str = """CREATE TABLE IF NOT EXISTS `da_31992_data_acquire` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `timestamp` INT NOT NULL,
  `utimestamp` BIGINT(20) NOT NULL,
  `infotime` INT NULL,
  `devtype` INT NULL,
  `level` INT NULL,
  `ip` INT UNSIGNED NULL,
  `hostname` VARCHAR(256) NULL,
  `reserve1` INT NULL,
  `reserve2` INT NULL,
  `detailinfo` LONGTEXT NULL,
  `table_id` INT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  INDEX `index_time` (`utimestamp` ASC),
  INDEX `index_table` (`table_id` ASC),
  INDEX `index_info` (`infotime` ASC),
  INDEX `index_ip` (`ip` ASC),
  INDEX `index_type` (`devtype` ASC),
  INDEX `index_level` (`level` ASC))
ENGINE = MRG_MyISAM
UNION = (da_31992_data_acquire_1,da_31992_data_acquire_2,da_31992_data_acquire_3,da_31992_data_acquire_4,da_31992_data_acquire_5,da_31992_data_acquire_6,da_31992_data_acquire_7,da_31992_data_acquire_8,da_31992_data_acquire_9,da_31992_data_acquire_10,da_31992_data_acquire_11,da_31992_data_acquire_12)"""
        try:
            db.write_db(cre_str)
            logger.info("add_da_31992_data_acquire ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("add_da_31992_data_acquire error.")

    @staticmethod
    def empty_vtysh_conf():
        with open('/data/vtysh-dpi/dpi-all.conf', "r+") as f:
            f.seek(0)
            f.truncate()
        with open('/data/vtysh-dpi/dpi.conf', "r+") as f:
            f.seek(0)
            f.truncate()

    @staticmethod
    def alter_table_incidentstat_bydev():
        """
        安全事件状态表更新
        :return:
        """
        alter_sql = "alter table incidentstat_bydev add column icd_pcap_count int(11) UNSIGNED DEFAULT 0 after icd_dev_count"
        try:
            db.write_db(alter_sql)
            logger.info("alter_table_incidentstat_bydev ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("alter_table_incidentstat_bydev error.")

    @staticmethod
    def alter_incidentstat_bydev_delimeter():
        """
        触发器函数更新
        :return:
        """
        process = Popen(
            '/app/local/mysql-5.6.31-linux-glibc2.5-x86_64/bin/mysql -ukeystone -pOptValley@4312',
            stdout=PIPE, stdin=PIPE, shell=True)
        try:
            process.stdin.write('use keystone\n')
            process.stdin.write(
                'source /app/local/share/new_self_manage/global_function/upgrade_mysql/keystone_v222_delimiter.sql\n')
            process.stdin.write('exit\n')
            process.wait()
            logger.info("source keystone_v222_delimiter.sql ok")
        except:
            logger.error('source keystone_v222_delimiter.sql error')
            logger.error(traceback.format_exc())

    @staticmethod
    def alter_incidents():
        # conn=MySQLdb.connect(host='localhost', port=3306, user='keystone', passwd='OptValley@4312', db='keystone')
        # cur=conn.cursor()
        drop_str="drop table if exists incidents"
        db.write_db(drop_str)

        for i in range(0, 10):
            sql_str1="alter table incidents_{} modify column dpi varchar(128) default null".format(i)
            sql_str2="alter table incidents_{} modify column dpiName varchar(128) default null".format(i)
            sql_str3="alter table incidents_{} modify column appLayerProtocol varchar(64) default null".format(i)
            sql_str4="alter table incidents_{} modify column signatureName int(11) default 0".format(i)

            index_str0="alter table incidents_{} add index signature_index(signatureName)".format(i)
            index_str1="alter table incidents_{} add index dpi_index(dpi)".format(i)
            index_str2="alter table incidents_{} add index dpiname_index(dpiName)".format(i)
            index_str3="alter table incidents_{} add index proto_index(appLayerProtocol)".format(i)
            try:
                db.write_db(sql_str1)
                db.write_db(sql_str2)
                db.write_db(sql_str3)
                db.write_db(sql_str4)
                db.write_db(index_str0)
                db.write_db(index_str1)
                db.write_db(index_str2)
                db.write_db(index_str3)
                logger.info('alter_incidents_{} ok'.format(i))
            except:
                logger.error('alter_incidents_{} error'.format(i))
                logger.error(traceback.format_exc())

        cre_str="""CREATE TABLE `incidents` (
      `incidentId` int(11) NOT NULL AUTO_INCREMENT,
      `tableNum` int(5) DEFAULT NULL,
      `sourceName` longtext,
      `destinationName` longtext,
      `sourceIp` longtext,
      `destinationIp` longtext,
      `sourceMac` longtext,
      `destinationMac` longtext,
      `ipVersion` int(11) DEFAULT NULL,
      `sourcePort` int(11) DEFAULT NULL,
      `destinationPort` int(11) DEFAULT NULL,
      `action` int(11) DEFAULT NULL,
      `protocol` longtext,
      `appLayerProtocol` varchar(64) DEFAULT NULL,
      `packetLength` int(11) DEFAULT NULL,
      `packet` longtext,
      `signatureMessage` longtext,
      `signatureId` int(11) DEFAULT NULL,
      `matchedKey` longtext,
      `protocolDetail` longtext,
      `payloadLength` int(11) DEFAULT NULL,
      `payload` longblob,
      `signatureName` int(11) DEFAULT 0,
      `timestamp` varchar(30) DEFAULT NULL,
      `occurredDate` date DEFAULT NULL,
      `occurredTime` time DEFAULT NULL,
      `dpi` varchar(128) DEFAULT NULL,
      `dpiName` varchar(128) DEFAULT NULL,
      `level` int(11) DEFAULT NULL,
      `status` int(11) DEFAULT NULL,
      `deployed` int(11) DEFAULT NULL,
      `alertType` int(11) DEFAULT NULL,
      `alertId` int(11) DEFAULT NULL,
      `createdAt` datetime DEFAULT NULL,
      `updatedAt` datetime DEFAULT NULL,
      `zoneName` longtext,
      `memo` longtext,
      `dpiIp` longtext,
      `boxId` longtext,
      `deviceId` longtext,
      `futureAction` int(11) DEFAULT NULL,
      `deleted` int(11) DEFAULT NULL,
      `topologyId` longtext,
      `deviceName` longtext,
      `statisticDetail` longtext,
      `riskLevel` int(11) DEFAULT NULL,
      `timestampint` bigint(20) DEFAULT NULL,
      PRIMARY KEY (`incidentId`),
      KEY `time_index` (`timestamp`),
      KEY `time_int_index` (`timestampint`),
      KEY `signature_index` (`signatureName`),
      KEY `dpi_index` (`dpi`),
      KEY `dpiname_index` (`dpiName`),
      KEY `proto_index` (`appLayerProtocol`)
    ) ENGINE=MRG_MyISAM DEFAULT CHARSET=utf8 UNION=(`incidents_0`,`incidents_1`,`incidents_2`,`incidents_3`,`incidents_4`,`incidents_5`,`incidents_6`,`incidents_7`,`incidents_8`,`incidents_9`)"""
        try:
            db.write_db(cre_str)
            logger.info('add_incidents ok')
        except:
            logger.error('add_incidents error')
            logger.error(traceback.format_exc())
        # cur.close()
        # conn.close()

    @staticmethod
    def run():
        try:
            MysqlDbUpgradeE.add_service_info()
            MysqlDbUpgradeE.add_process()
            MysqlDbUpgradeE.add_self_define_proto_config()
            MysqlDbUpgradeE.add_process()
            MysqlDbUpgradeE.add_content_model()
            MysqlDbUpgradeE.add_process()
            MysqlDbUpgradeE.add_value_map_model()
            MysqlDbUpgradeE.add_process()
            MysqlDbUpgradeE.create_pcap_tables()
            MysqlDbUpgradeE.add_process()
            MysqlDbUpgradeE.add_asset_report_tables()
            MysqlDbUpgradeE.add_process()
            MysqlDbUpgradeE.add_license_info_tables()
            MysqlDbUpgradeE.add_process()
            MysqlDbUpgradeE.create_alarm_tables()
            MysqlDbUpgradeE.add_process()
            MysqlDbUpgradeE.create_table_devtype()
            MysqlDbUpgradeE.add_process()
            MysqlDbUpgradeE.alter_table_users()
            MysqlDbUpgradeE.add_process()
            MysqlDbUpgradeE.alter_table_top_config()
            MysqlDbUpgradeE.add_process()
            MysqlDbUpgradeE.add_log_audit_tables()
            MysqlDbUpgradeE.add_process()
            MysqlDbUpgradeE.add_cusproto_tables()
            MysqlDbUpgradeE.add_process()
            MysqlDbUpgradeE.add_da_31992_data_acquire()
            MysqlDbUpgradeE.add_process()
            MysqlDbUpgradeE.empty_vtysh_conf()
            MysqlDbUpgradeE.add_process()
            MysqlDbUpgradeE.alter_table_incidentstat_bydev()
            MysqlDbUpgradeE.add_process()
            MysqlDbUpgradeE.alter_incidentstat_bydev_delimeter()
            MysqlDbUpgradeE.add_process()
            MysqlDbUpgradeE.alter_incidents()
            MysqlDbUpgradeE.add_process()
        except:
            logger.error(traceback.format_exc())
            logger.error("MysqlDbUpgradeE run error.")
