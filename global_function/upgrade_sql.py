#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import logging
import time
from .global_var import DbProxy, CONFIG_DB_NAME

logger = logging.getLogger("sql_update_log")
PROGRESS_DICT = {"process": 0, "total_num": 0, "done_num": 0}


class MysqlDbUpgradeBase(object):
    """
    数据库升级的基类,主要用于实现数据库的备份和回复
    """
    from_ver = None
    to_ver = None

    @staticmethod
    def mysql_dump():
        """
        执行数据库备份,数据库备份文件存储在/data/backup路径下
        :return:
        """
        logger.info("start backup mysql_db...")
        if not os.path.exists("/data/backup"):
            os.system("mkdir -p /data/backup")
        try:
            cp_command = "cp -a /data/mysql/keystone/* /data/backup/"
            os.system(cp_command)
            logger.info("backup mysql_db ok.")
            if os.path.exists("/data/mysql/sql_backup_error.flag"):
                os.system("rm -rf /data/mysql/sql_backup_error.flag")
            return True
        except:
            logger.error("backup mysql_db error.")
            return False

    @staticmethod
    def mysql_load():
        """
        数据库恢复操作
        :return:
        """
        try:
            command = "rm -rf /data/mysql/keystone/* | cp -a /data/backup/* /data/mysql/keystone/"
            os.system(command)
            logger.info("recover mysql_db ok.")
            return True
        except:
            logger.error("recover mysql_db error.")
            return False

    @staticmethod
    def mysql_del_copy():
        """
        升级完成后删除备份的数据库
        :return:
        """
        try:
            command = "rm -rf /data/backup/*"
            os.system(command)
            logger.info("delete mysql_db_copy ok.")
            return True
        except:
            logger.error("delete mysql_db_copy error.")
            return False


class MysqlDbUpgradeA(MysqlDbUpgradeBase):
    """
    实现指定版本到指定版本升级的功能
    """
    from_ver = "V1.0"
    to_ver = "V2.1"
    num = 2

    def __init__(self):
        super(MysqlDbUpgradeA, self).__init__()

    @staticmethod
    def add_signatures():
        time.sleep(10)
        db = DbProxy(CONFIG_DB_NAME)
        try:
            sql_str = """INSERT INTO `signatures` VALUES (NULL,'1065387488247104870',0,'LiMJJmW3x/LdsJOZvMYukHIBYQak1nzx102tJGXMNUDgfGNF40EyDl5J9JmxF7NsBpZKr6IFFJHz8r2WAMU1qK3KK4N1pw/dBm6KOLQ0VP6oL67CIipz4x+tCZpIBjy3PW+1GmDfmmVXj0+acxDTRnbAsZlvzCUqv1E1Yvi6B3wEHQktniTKALvPhqQfr5lJNFqzawVpcDvveCUCm23fRYVQzUeN889+TEL/KNvGzdbS6a41UGxVNCiN3x5MRLrzdH64SvAC9AQFNjJ4bKwTb57tskyBfoWGijwSdTIGpdF3U8n6VbahOFKQqT5TH3ZWkpXY5Q9PaGSpHjPJ18jeNdhJmIjertf35pOGSJZ8tylDyyfR37mJF+vNm8M3s2fGl8r3p5UrRJmJcgZOqrfKlQ==',3,101116,'ICS-ATTACK.TRISIS/TRITON READ REQUEST','ICS-ATTACK.TRISIS/TRITON READ REQUEST',NULL,1,NULL,0,2,0,12),(NULL,'2875134312413836186',0,'LiMJJmW3x/LdsJOZvMYukHIBYQak1nzx102tJGXMNUDgfGNF40EyDl5J9JmxF7NsBpZKr6IFFJHz8r2WAMU1qN0zcWz7KbMrk6eYHGF++7B4mp/+lvz35M/1T+Lplr4Q3eEUJBTyq/3+QNQzjTAj7VLsUDLov4bCRzs5zo1L/26jmMooJqW5+BkT1b83U+GbMkqtTuRWexaC8nQG3RsUgNvPWMTh4LTHGoYa5bMP5W9n71GyfB7BziLHcQwOj5PDx4j7QdU2KmASQVDjNR8dzMb6huXPkACFXpt47dU4SGOGRSZU0AWmQC808b6EvzqY9rwttlyS+bkH2IBwT6G9agsotxPm6jTBAP55qLqo2cRA+JsZFvASuJ3VI0ThL04Kzr4MQYCunvHnLASX2+LbLw==',3,101117,'ICS-ATTACK.TRISIS/TRITON WRITE REQUEST','ICS-ATTACK.TRISIS/TRITON WRITE REQUEST',NULL,1,NULL,0,2,0,12),(NULL,'1591739768215462186',0,'LiMJJmW3x/LdsJOZvMYukHIBYQak1nzx102tJGXMNUDgfGNF40EyDl5J9JmxF7NsBpZKr6IFFJHz8r2WAMU1qBsu9Nb5vziRGqv+WMrmHj1uBer3K+Qha5uxkUzawkeEFS0mrcG20QCUE8cvG/FAos8q+QV3JGNbgY5RL27K6QcN95k6W3k3OhIqUgC7moLOqdmtq5TtirkP8PEntwyoc2TzitH7tBz8pfdmWacfKumsPKcS26IjmUTRGt42T+p/vQCPq4TdKExZXCzkeQF7RjTqYiMa2EoocH6AbHvzl3b7tWJ4n/uPGDRm2FvFVASIPijPoeIdrFIiic6a5FfEknuZPIPf0L8wx5+je/mc4jZiomDxYiSdGBeWNJhkG7epaf6xERn23xazC9PZ1yKbXdfSoXa2V6qQhl5N1imfqj/Kwcq+ALnOWgH179m7e07btXbGvc4zzucEza/d2Gr7Nqz0v1l0W8PavzocYmnVlOPfuStHNgB0sQlYtdVTXsD7',3,101118,'ICS-ATTACK.TRISIS/TRITON EXECUTE REQUEST','ICS-ATTACK.TRISIS/TRITON EXECUTE REQUEST',NULL,1,NULL,0,2,0,12);"""
            res = db.write_db(sql_str)
            if res == 0:
                PROGRESS_DICT["done_num"] += 1.0
                process = int((PROGRESS_DICT["done_num"] / PROGRESS_DICT["total_num"]) * 100)
                PROGRESS_DICT["process"] = process
                logger.info("add_signatures ok.process=" + str(PROGRESS_DICT["process"]))
            else:
                PROGRESS_DICT["done_num"] += 1.0
                process = int((PROGRESS_DICT["done_num"] / PROGRESS_DICT["total_num"]) * 100)
                PROGRESS_DICT["process"] = process
                logger.error("add_signatures write_db error.")
        except:
            logger.error("add_signatures error.")

    @staticmethod
    def add_vulnerabilities():
        time.sleep(10)
        db = DbProxy(CONFIG_DB_NAME)
        try:
            sql_str = """INSERT INTO `vulnerabilities`  values ('1591739768215462186',1,'code_execution','ICS-ATTACK.TRISIS/TRITON EXECUTE REQUEST',NULL,'施耐德电气Triconex Tricon MP3008存在漏洞。恶意软件可以在攻陷SIS系统后，对SIS系统逻辑进行重编程，使SIS系统产生意外动作，对正常生产活动造成影响；或是造成SIS系统失效，在发生安全隐患或安全风险时无法及时实行和启动安全保护机制；亦或在攻陷SIS系统后，对DCS系统实施攻击，并通过SIS系统与DCS系统的联合作用，对工业设备、生产活动以及操作人员的人身安全造成巨大威胁。',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2017-12-14',101118,0),('1065387488247104870',1,'code_execution','ICS-ATTACK.TRISIS/TRITON READ REQUEST',NULL,'施耐德电气Triconex Tricon MP3008存在漏洞。恶意软件可以在攻陷SIS系统后，对SIS系统逻辑进行重编程，使SIS系统产生意外动作，对正常生产活动造成影响；或是造成SIS系统失效，在发生安全隐患或安全风险时无法及时实行和启动安全保护机制；亦或在攻陷SIS系统后，对DCS系统实施攻击，并通过SIS系统与DCS系统的联合作用，对工业设备、生产活动以及操作人员的人身安全造成巨大威胁。',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2017-12-14',101116,0),('2875134312413836186',1,'code_execution','ICS-ATTACK.TRISIS/TRITON WRITE REQUEST',NULL,'施耐德电气Triconex Tricon MP3008存在漏洞。恶意软件可以在攻陷SIS系统后，对SIS系统逻辑进行重编程，使SIS系统产生意外动作，对正常生产活动造成影响；或是造成SIS系统失效，在发生安全隐患或安全风险时无法及时实行和启动安全保护机制；亦或在攻陷SIS系统后，对DCS系统实施攻击，并通过SIS系统与DCS系统的联合作用，对工业设备、生产活动以及操作人员的人身安全造成巨大威胁。',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2017-12-14',101117,0);"""
            res = db.write_db(sql_str)
            if res == 0:
                PROGRESS_DICT["done_num"] += 1.0
                process = int((PROGRESS_DICT["done_num"] / PROGRESS_DICT["total_num"]) * 100)
                PROGRESS_DICT["process"] = process
                logger.info("add_vulnerabilities ok.process=" + str(PROGRESS_DICT["process"]))
            else:
                PROGRESS_DICT["done_num"] += 1.0
                process = int((PROGRESS_DICT["done_num"] / PROGRESS_DICT["total_num"]) * 100)
                PROGRESS_DICT["process"] = process
                logger.error("add_vulnerabilities write_db error.")
        except:
            logger.error("add_vulnerabilities error.")

    @staticmethod
    def run():
        try:
            MysqlDbUpgradeA.add_signatures()
            MysqlDbUpgradeA.add_vulnerabilities()
            logger.info("MysqlDbUpgradeA run finished.")
            return True
        except:
            logger.error("MysqlDbUpgradeA run error.")
            return False
