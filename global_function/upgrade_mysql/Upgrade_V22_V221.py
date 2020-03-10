#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging
from global_function.global_var import DbProxy
from . import MysqlDbUpgradeBase
import traceback

logger = logging.getLogger("sql_update_log")


class MysqlDbUpgradeD(MysqlDbUpgradeBase):
    from_ver = "V2.2"
    to_ver = "V2.2.1"
    num = 2
    def __init__(self):
        super(MysqlDbUpgradeD, self).__init__()

    @staticmethod
    def del_traffictables():
        keystoneconfig_table=('safedevpoint', 'icdevicetrafficstats', 'sorted_dev_traffic_1h', 'dev_his_traffic', 'dev_band_20s', 'icdevicetraffics')
        db_proxy=DbProxy()
        for t in keystoneconfig_table:
            sql_str='DROP TABLE IF EXISTS %s' % t
            db_proxy.write_db(sql_str)

    @staticmethod
    def create_traffic_tables():
        cre_str1="""CREATE TABLE `dev_his_traffic` (
    `id`	int(11) NOT NULL AUTO_INCREMENT,
    `devid`	varchar(128),
    `ip`	varchar(64),
    `mac`	varchar(30),
    `sendBytes` bigint(20),
    `recvBytes` bigint(20),
    `totalBytes` bigint(20),
    `timestamp` varchar(30),
    PRIMARY KEY (`id`)
) ENGINE=MEMORY DEFAULT CHARSET=utf8;"""
        cre_str2="""CREATE TABLE `dev_band_20s` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `devid` varchar(128),
  `devip` varchar(64),
  `devmac` varchar(30),
  `timestamp` varchar(30),
  `band` varchar(30),
  `send` varchar(30),
  `recv` varchar(30),
  primary key(id)
) ENGINE=MEMORY DEFAULT CHARSET=utf8;"""
        cre_str3="""CREATE TABLE `icdevicetraffics` (
  `iCDeviceTrafficId` int(11) DEFAULT NULL,
  `iCDeviceIp` varchar(128),
  `iCDeviceMac` varchar(128),
  `iCDeviceId` varchar(128),
  `trafficType` int(11) DEFAULT NULL,
  `trafficName` varchar(128),
  `sendBytes` int(11) DEFAULT NULL,
  `recvBytes` int(11) DEFAULT NULL,
  `sendSpeed` int(11) DEFAULT NULL,
  `recvSpeed` int(11) DEFAULT NULL,
  `timestamp` varchar(30),
  `createdAt` varchar(128),
  `deviceName` varchar(128),
  index `time_index` (`timestamp`)
) ENGINE=MEMORY DEFAULT CHARSET=utf8;"""
        cre_str4="""CREATE TABLE `sorted_dev_traffic_1h` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `devid` varchar(128),
  `ip` varchar(64),
  `mac` varchar(30),
  `sendSpeed` float,
  `recvSpeed` float,
  `totalBytes` float,
  `timestamp` varchar(30),
  `devPer` float,
  primary key(id)
) ENGINE=MEMORY DEFAULT CHARSET=utf8;"""
        cre_str5="""CREATE TABLE `icdevicetrafficstats` (
  `iCDeviceTrafficStatId` int(11) DEFAULT NULL,
  `iCDeviceIp` varchar(128),
  `iCDeviceMac` varchar(128),
  `iCDeviceId` varchar(128),
  `trafficType` int(11) DEFAULT NULL,
  `trafficName` varchar(128),
  `totalBytes` bigint(20) DEFAULT NULL,
  `timestamp` varchar(30),
  `createdAt` varchar(128),
  `deviceName` varchar(128),
  index `time_index` (`timestamp`)
) ENGINE=MEMORY DEFAULT CHARSET=utf8;"""
        cre_str6="""CREATE TABLE `safedevpoint` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` varchar(128),
  `sendSpeed` varchar(128),
  PRIMARY KEY (`id`)
) ENGINE=MEMORY DEFAULT CHARSET=utf8;"""
        db_proxy=DbProxy()
        try:
            db_proxy.write_db(cre_str1)
            db_proxy.write_db(cre_str2)
            db_proxy.write_db(cre_str3)
            db_proxy.write_db(cre_str4)
            db_proxy.write_db(cre_str5)
            db_proxy.write_db(cre_str6)
        except:
            logger.error(traceback.format_exc())
            logger.error("create traffic tables error.")

    @staticmethod
    def run():
        try:
            MysqlDbUpgradeD.del_traffictables()
            MysqlDbUpgradeD.add_process()
            MysqlDbUpgradeD.create_traffic_tables()
            MysqlDbUpgradeD.add_process()
        except:
            logger.error(traceback.format_exc())
            logger.error("MysqlDbUpgradeD run error.")
