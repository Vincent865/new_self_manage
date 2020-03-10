#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import logging
import traceback
import time
from global_function.global_var import DbProxy
from . import MysqlDbUpgradeBase, PROGRESS_DICT

logger = logging.getLogger("sql_update_log")


class MysqlDbUpgradeF(MysqlDbUpgradeBase):
    """
    实现指定版本到指定版本升级的功能
    """
    from_ver = "V2.2.2"
    to_ver = "V2.3"
    num = 8

    def __init__(self):
        super(MysqlDbUpgradeF, self).__init__()

    @staticmethod
    def alter_content_model():
        db = DbProxy("keystone_config")
        try:
            alter_str = """alter table content_model add column start_offset2 int(11) DEFAULT NULL after content,add column depth2 int(11) DEFAULT NULL after start_offset2,add column content2 varchar(128) DEFAULT NULL after depth2, add column start_offset3 int(11) DEFAULT NULL after content2,add column depth3 int(11) DEFAULT NULL after start_offset3,add column content3 varchar(128) DEFAULT NULL after depth3,add column bit_offset1 int(11) DEFAULT NULL after value_map_id_1,add column bit_offset2 int(11) DEFAULT NULL after value_map_id_2,add column bit_offset3 int(11) DEFAULT NULL after value_map_id_3,add column bit_offset4 int(11) DEFAULT NULL after value_map_id_4,add column bit_offset5 int(11) DEFAULT NULL after value_map_id_5"""
            res = db.write_db(alter_str)
            if res == 0:
                logger.info("alter_content_model ok.")
            else:
                logger.error("alter_content_model write_db error.")
        except:
            logger.error("alter_content_model error.")

    @staticmethod
    def alter_table_topdevice():
        """
        设备类型，厂商自动识别功能:设备表增加自动识别字段
        :return:
        """
        alter_sql1 = "ALTER TABLE topdevice ADD COLUMN proto_info VARCHAR(1024) DEFAULT '[]' AFTER dev_mode"
        alter_sql2 = "ALTER TABLE topdevice ADD COLUMN auto_flag int DEFAULT 1 AFTER dev_mode"
        alter_sql3 = "ALTER TABLE topdevice ADD COLUMN custom_default_flag VARCHAR(32) DEFAULT NULL AFTER dev_mode"
        db_config = DbProxy("keystone_config")
        try:
            db_config.write_db(alter_sql1)
            db_config.write_db(alter_sql2)
            db_config.write_db(alter_sql3)
            logger.info("alter_table_topdevice ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("alter_table_topdevice error.")

    @staticmethod
    def alter_table_self_define_proto_config():
        """
        设备类型，厂商自动识别功能:自定义协议表增加客户端（client_type），服务端类型（server_type）字段
        :return:
        """
        alter_sql1 = "ALTER TABLE self_define_proto_config ADD COLUMN client_type int DEFAULT NULL AFTER content_id"
        alter_sql2 = "ALTER TABLE self_define_proto_config ADD COLUMN server_type int DEFAULT NULL AFTER content_id"
        db_config = DbProxy("keystone_config")
        try:
            db_config.write_db(alter_sql1)
            db_config.write_db(alter_sql2)
            logger.info("alter_table_self_define_proto_config ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("alter_table_self_define_proto_config error.")

    @staticmethod
    def create_proto_dev_type_tables():
        """
        厂商，设备类型自动识别功能：增加协议设备类型映射表
        """
        cre_sql = """CREATE TABLE `proto_dev_type` (
                  `id` int not null primary key auto_increment,
                  `proto_type` varchar(1024),
                  `client_type` int,
                  `server_type` int
                ) ENGINE=MYISAM DEFAULT CHARSET=utf8;"""
        insert_sql = '''insert into proto_dev_type (proto_type,client_type,server_type) values ("Modbus", "3", "4"),("OPCDA", "3", "9"),("PROFINETIO", "3", "4"),("ENIP", "3", "4"),("DNP3", "3", "4"),("S7", "3", "4"),("OPCUATCP", "3", "9"),("SIP", "0", "8"),("S7PLUS", "3", "4"),("IEC104", "0", "12"),("MMS", "0", "12"),("GOOSE", "0", "12"),("SV", "0", "12"),("FTP", "0", "8"),("HTTP", "0", "8"),("SMTP", "0", "8"),("SNMP", "0", "8"),("ORACLE", "0", "8"),("Telnet", "0", "8"),("POP3", "0", "8"),("SQLServer", "0", "8");'''
        db_config = DbProxy("keystone_config")
        try:
            db_config.write_db(cre_sql)
            db_config.write_db(insert_sql)
            logger.info("create proto_dev_type tables ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("create proto_dev_type tables error.")

    @staticmethod
    def create_self_define_fingerprint_tables():
        """
        厂商，设备类型自动识别功能：增加自定义指纹表
        """
        cre_sql = """CREATE TABLE `self_define_fingerprint` (
                  `id` int not null primary key auto_increment,
                  `update_time` int,
                  `mac` varchar(1024),
                  `rule_name` varchar(1024),
                  `vendor` varchar(1024),
                  `dev_type` int,
                  `dev_model` varchar(1024),
                  `proto_port_attr` varchar(1024)
                ) ENGINE=MYISAM DEFAULT CHARSET=utf8;"""
        db_config = DbProxy("keystone_config")
        try:
            db_config.write_db(cre_sql)
            logger.info("create self_define_fingerprint tables ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("create self_define_fingerprint tables error.")

    @staticmethod
    def create_dev_vendor_mac_tables():
        """
        厂商，设备类型自动识别功能：增加厂商，mac映射表
        """
        cre_sql = """CREATE TABLE `dev_vendor_mac` (
                  `id` int not null primary key auto_increment,
                  `vendor` varchar(1024),
                  `mac` varchar(1024)
                ) ENGINE=MYISAM DEFAULT CHARSET=utf8;"""
        insert_sql = """INSERT INTO `dev_vendor_mac` VALUES (1,'SIGMATEK','0050F4'),(2,'IDEC','00037B'),(3,'Westinghouse','180C77'),(4,'Westinghouse','509772'),(5,'Honeywell','004084'),(6,'Honeywell','00203D'),(7,'Honeywell','144146'),(8,'Honeywell','001F55'),(9,'Honeywell','0080A7'),(10,'Honeywell','0C2369'),(11,'Honeywell','DCB3B4'),(12,'Honeywell','94CA0F'),(13,'Honeywell','00226A'),(14,'Honeywell','F05494'),(15,'Honeywell','D806D1'),(16,'Honeywell','001112'),(17,'Honeywell','0030AF'),(18,'Honeywell','AC7713'),(19,'Honeywell','001E1E'),(20,'Honeywell','000A13'),(21,'Honeywell','00064A'),(22,'Toshiba','0015B7'),(23,'Toshiba','E89D87'),(24,'Toshiba','78D6B2'),(25,'Toshiba','F4645D'),(26,'Toshiba','00080D'),(27,'Toshiba','000E7B'),(28,'Toshiba','E8E0B7'),(29,'Toshiba','887384'),(30,'Toshiba','20B780'),(31,'Toshiba','242FFA'),(32,'Toshiba','FC0012'),(33,'Toshiba','C0F945'),(34,'Toshiba','002318'),(35,'Toshiba','B86B23'),(36,'Toshiba','001C7E'),(37,'Toshiba','28FFB2'),(38,'Toshiba','8CE38E'),(39,'Toshiba','EC21E5'),(40,'Toshiba','E83A97'),(41,'Toshiba','000600'),(42,'Toshiba','6845F1'),(43,'Toshiba','000039'),(44,'Bosch','8834FE'),(45,'Bosch','64DAA0'),(46,'Bosch','70C6AC'),(47,'Bosch','BC903A'),(48,'Bosch','000131'),(49,'Bosch','A00363'),(50,'Bosch','D0B498'),(51,'Bosch','001B86'),(52,'Bosch','000463'),(53,'Bosch','641331'),(54,'Bosch','001017'),(55,'Bosch','FCD6BD'),(56,'Bosch','A41115'),(57,'Bosch','7CACB2'),(58,'Bosch','000B0F'),(59,'Bosch','001C44'),(60,'Hollysys','001C47'),(61,'Invensys','FCFEC2'),(62,'Invensys','703811'),(63,'Invensys','002096'),(64,'Saia-Burgess','7C160D'),(65,'GENERAL','00E0AF'),(66,'GENERAL','00400C'),(67,'GENERAL','0000A6'),(68,'GENERAL','080019'),(69,'GENERAL','002066'),(70,'GENERAL','90837A'),(71,'GENERAL','D491AF'),(72,'GENERAL','C4B512'),(73,'GENERAL','002689'),(74,'GENERAL','001B41'),(75,'GENERAL','001219'),(76,'GENERAL','000BD9'),(77,'GENERAL','000715'),(78,'GENERAL','0002DC'),(79,'GENERAL','0001B1'),(80,'GENERAL','000065'),(81,'GENERAL','0013A5'),(82,'GENERAL','D89341'),(83,'GENERAL','902083'),(84,'GENERAL','0025D4'),(85,'GENERAL','001E5C'),(86,'GENERAL','00148C'),(87,'GENERAL','0C2AE7'),(88,'GENERAL','68FB95'),(89,'GENERAL','0026BC'),(90,'GENERAL','002152'),(91,'GENERAL','001B96'),(92,'GENERAL','00021D'),(93,'GENERAL','00A021'),(94,'GENERAL','00C064'),(95,'GENERAL','0014B4'),(96,'GENERAL','00163B'),(97,'GENERAL','000B4E'),(98,'GENERAL','080062'),(99,'GENERAL','D828C9'),(100,'GENERAL','00144C'),(101,'Fuji','00401A'),(102,'Siemens','500084'),(103,'Siemens','E0DCA0'),(104,'Siemens','001106'),(105,'Siemens','009040'),(106,'Siemens','00A003'),(107,'Siemens','004043'),(108,'Siemens','000E8C'),(109,'Siemens','286336'),(110,'Siemens','0013A3'),(111,'Siemens','B4B15A'),(112,'Siemens','B87AC9'),(113,'Siemens','789F87'),(114,'Siemens','18AEBB'),(115,'Siemens','681FD8'),(116,'Siemens','001FF8'),(117,'Siemens','001865'),(118,'Siemens','000D41'),(119,'Siemens','003005'),(120,'Siemens','AC6417'),(121,'Siemens','883F99'),(122,'Siemens','4486C1'),(123,'Siemens','20E791'),(124,'Siemens','001C06'),(125,'Siemens','000FBB'),(126,'Siemens','301389'),(127,'Siemens','001133'),(128,'Siemens','000B23'),(129,'Siemens','40ECF8'),(130,'Siemens','0018D1'),(131,'Siemens','000519'),(132,'Siemens','10DFFC'),(133,'Siemens','000BA3'),(134,'Siemens','884B39'),(135,'Siemens','001B1B'),(136,'Siemens','001928'),(137,'Siemens','0001E3'),(138,'KOYO','00D07C'),(139,'Foxboro','000D04'),(140,'Mitsubishi','38E08E'),(141,'Mitsubishi','0000BD'),(142,'Mitsubishi','104B46'),(143,'Mitsubishi','58528A'),(144,'Mitsubishi','001ED9'),(145,'Mitsubishi','080070'),(146,'Mitsubishi','28E98E'),(147,'Mitsubishi','002692'),(148,'OMRON','002209'),(149,'OMRON','B0495F'),(150,'OMRON','00000A'),(151,'ABB','60391F'),(152,'ABB','001B45'),(153,'ABB','001386'),(154,'ABB','5031AD'),(155,'ABB','54F876'),(156,'ABB','002459'),(157,'ABB','00904F'),(158,'ABB','803B2A'),(159,'ABB','B89BE4'),(160,'ABB','807A7F'),(161,'ABB','9803A0'),(162,'ABB','0021C1'),(163,'ABB','001C01'),(164,'ABB','000D97'),(165,'ABB','000C02'),(166,'ABB','0002A3'),(167,'ABB','00022C'),(168,'ABB','000023'),(169,'ABB','78AB60'),(170,'ABB','ACD364'),(171,'ABB','E002A5'),(172,'ABB','00032C'),(173,'Festo','000EF0'),(174,'Schneider','74F661'),(175,'Schneider','20443A'),(176,'Schneider','001100'),(177,'Schneider','000C81'),(178,'Schneider','000054'),(179,'Schneider','001324'),(180,'Schneider','942E17'),(181,'Schneider','000123'),(182,'Schneider','282986'),(183,'Emerson','00243D'),(184,'Emerson','0009F5'),(185,'Emerson','0003AD'),(186,'Emerson','00E086'),(187,'Emerson','50206B'),(188,'Emerson','000AF6'),(189,'Emerson','00120A'),(190,'Emerson','004003'),(191,'Eaton','00054B'),(192,'Eaton','002085'),(193,'Eaton','001D05'),(194,'Eaton','001864'),(195,'Eaton','001345'),(196,'Eaton','000CC1'),(197,'Eaton','008099'),(198,'VIPA','0020D5'),(199,'Yokogawa','000064'),(200,'Yokogawa','D00AAB'),(201,'Yokogawa','006041'),(202,'PHOENIX','A8741D'),(203,'PHOENIX','00D08D'),(204,'PHOENIX','00A045'),(205,'PHOENIX','001B1D'),(206,'PHOENIX','001AA5'),(207,'PHOENIX','9C86DA'),(208,'PHOENIX','D4000D'),(209,'PHOENIX','001840'),(210,'PHOENIX','00132B'),(211,'Yamatake','002004'),(212,'Rockwell','086195'),(213,'Rockwell','0000BC'),(214,'Rockwell','5C8816'),(215,'Rockwell','34C0F9'),(216,'Rockwell','F45433'),(217,'Rockwell','184C08'),(218,'Rockwell','E49069'),(219,'Rockwell','001D9C'),(220,'上海新华','3CC2E1'),(221,'Hitachi','A497BB'),(222,'Hitachi','000E66'),(223,'Hitachi','000346'),(224,'Hitachi','000185'),(225,'Hitachi','3CB792'),(226,'Hitachi','FC790B'),(227,'Hitachi','FCFE77'),(228,'Hitachi','2C8BF2'),(229,'Hitachi','18CC88'),(230,'Hitachi','001FC7'),(231,'Hitachi','000C09'),(232,'Hitachi','0006FB'),(233,'Hitachi','D05FCE'),(234,'Hitachi','001F67'),(235,'Hitachi','0004D5'),(236,'Hitachi','60058A'),(237,'Hitachi','F84897'),(238,'Hitachi','0008F7'),(239,'Hitachi','000205'),(240,'Hitachi','000087'),(241,'Hitachi','0080BC'),(242,'Hitachi','000A56'),(243,'Hitachi','00102D'),(244,'Hitachi','0060E8'),(245,'Hitachi','0060CB'),(246,'DELTA','00211F'),(247,'DELTA','0030AB'),(248,'DELTA','00D0AB'),(249,'DELTA','001A25'),(250,'DELTA','0050A0'),(251,'DELTA','0040AE'),(252,'DELTA','0030B8'),(253,'DELTA','20F85E'),(254,'DELTA','6CB9C5'),(255,'DELTA','F4E142'),(256,'DELTA','00231D'),(257,'DELTA','000F5B'),(258,'DELTA','00066E'),(259,'DELTA','20780B'),(260,'DELTA','58E747'),(261,'DELTA','001249'),(262,'DELTA','E405F8'),(263,'DELTA','88B168'),(264,'DELTA','300B9C'),(265,'DELTA','001A26'),(266,'DELTA','18BE92'),(267,'DELTA','001823'),(268,'Panasonic','BCC342'),(269,'Panasonic','001BD3'),(270,'Panasonic','CC7EE7'),(271,'Panasonic','20C6EB'),(272,'Panasonic','001987'),(273,'Panasonic','54CD10'),(274,'Panasonic','080023'),(275,'Panasonic','4C364E'),(276,'Panasonic','34F6D2'),(277,'Panasonic','D8AFF1'),(278,'Panasonic','001267'),(279,'Panasonic','005040'),(280,'Panasonic','EC65CC'),(281,'Panasonic','80C755'),(282,'Panasonic','3432E6'),(283,'Panasonic','00D060'),(284,'Panasonic','74D7CA'),(285,'Panasonic','304C7E'),(286,'Panasonic','0080F0'),(287,'Panasonic','B46C47'),(288,'Panasonic','949D57'),(289,'Panasonic','705812'),(290,'Panasonic','04209A'),(291,'Panasonic','D8B12A'),(292,'Panasonic','A81374'),(293,'Panasonic','000F12'),(294,'Panasonic','4C218C'),(295,'Panasonic','00C08F'),(296,'Panasonic','8CC121'),(297,'Panasonic','3C6FEA'),(298,'Panasonic','24A87D'),(299,'Panasonic','E0EE1B');"""
        db_config = DbProxy("keystone_config")
        try:
            db_config.write_db(cre_sql)
            db_config.write_db(insert_sql)
            logger.info("create dev_vendor_mac tables ok.")
        except:
            logger.error(traceback.format_exc())
            logger.error("create dev_vendor_mac tables error.")

        @staticmethod
        def create_switch_info_tables():
            """
            资产定位功能：增加交换机列表信息表
            """
            cre_sql = """CREATE TABLE `switch_info` (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `name` longtext,
              `ip` varchar(64) DEFAULT NULL,
              `type` longtext,
              `locate` longtext,
              `snmp_version` int,
              `group_name` varchar(64) DEFAULT NULL,
              `security_level` varchar(64) DEFAULT NULL,
              `security_name` varchar(64) DEFAULT NULL,
              `auth_mode` varchar(64) DEFAULT NULL,
              `auth_pwd` varchar(64) DEFAULT NULL,
              `priv_mode` varchar(64) DEFAULT NULL,
              `priv_pwd` varchar(64) DEFAULT NULL,
              `ssh_name` varchar(64) DEFAULT NULL,
              `ssh_pwd` varchar(64) DEFAULT NULL,
              PRIMARY KEY (`id`)
            )ENGINE=MYISAM DEFAULT CHARSET=utf8;"""
            db_config = DbProxy("keystone_config")
            try:
                db_config.write_db(cre_sql)
                logger.info("create switch_info tables ok.")
            except:
                logger.error(traceback.format_exc())
                logger.error("create switch_info tables error.")

        @staticmethod
        def create_switch_mac_port_tables():
            """
            资产定位功能：增加交换机列表mac_port信息表
            """
            cre_sql = """CREATE TABLE `switch_mac_port` (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `switch_name` longtext,
              `mac` varchar(32) DEFAULT NULL,
              `port` varchar(32) DEFAULT NULL,
              PRIMARY KEY (`id`)
            )ENGINE=MYISAM DEFAULT CHARSET=utf8;"""
            db_config = DbProxy("keystone_config")
            try:
                db_config.write_db(cre_sql)
                logger.info("create switch_mac_port tables ok.")
            except:
                logger.error(traceback.format_exc())
                logger.error("create switch_mac_port tables error.")

    @staticmethod
    def run():
        try:
            MysqlDbUpgradeF.alter_content_model()
            MysqlDbUpgradeF.add_process()
            MysqlDbUpgradeF.alter_table_topdevice()
            MysqlDbUpgradeF.add_process()
            MysqlDbUpgradeF.alter_table_self_define_proto_config()
            MysqlDbUpgradeF.add_process()
            MysqlDbUpgradeF.create_proto_dev_type_tables()
            MysqlDbUpgradeF.add_process()
            MysqlDbUpgradeF.create_self_define_fingerprint_tables()
            MysqlDbUpgradeF.add_process()
            MysqlDbUpgradeF.create_dev_vendor_mac_tables()
            MysqlDbUpgradeF.add_process()
            MysqlDbUpgradeF.create_switch_info_tables()
            MysqlDbUpgradeF.add_process()
            MysqlDbUpgradeF.create_switch_mac_port_tables()
            MysqlDbUpgradeF.add_process()
            logger.info("MysqlDbUpgradeF run finished.")
            return True
        except:
            logger.error("MysqlDbUpgradeF run error.")
            return False
