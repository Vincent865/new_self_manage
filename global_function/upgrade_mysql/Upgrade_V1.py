#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import logging
import time
from global_function.global_var import DbProxy
from . import MysqlDbUpgradeBase, PROGRESS_DICT

logger = logging.getLogger("sql_update_log")


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
        db = DbProxy()
        try:
            sql_str = """INSERT INTO `signatures` VALUES (NULL,'1065387488247104870',0,'LiMJJmW3x/LdsJOZvMYukHIBYQak1nzx102tJGXMNUDgfGNF40EyDl5J9JmxF7NsBpZKr6IFFJHz8r2WAMU1qK3KK4N1pw/dBm6KOLQ0VP6oL67CIipz4x+tCZpIBjy3PW+1GmDfmmVXj0+acxDTRnbAsZlvzCUqv1E1Yvi6B3wEHQktniTKALvPhqQfr5lJNFqzawVpcDvveCUCm23fRYVQzUeN889+TEL/KNvGzdbS6a41UGxVNCiN3x5MRLrzdH64SvAC9AQFNjJ4bKwTb57tskyBfoWGijwSdTIGpdF3U8n6VbahOFKQqT5TH3ZWkpXY5Q9PaGSpHjPJ18jeNdhJmIjertf35pOGSJZ8tylDyyfR37mJF+vNm8M3s2fGl8r3p5UrRJmJcgZOqrfKlQ==',3,101116,'ICS-ATTACK.TRISIS/TRITON READ REQUEST','ICS-ATTACK.TRISIS/TRITON READ REQUEST',NULL,1,NULL,0,2,0,12),(NULL,'2875134312413836186',0,'LiMJJmW3x/LdsJOZvMYukHIBYQak1nzx102tJGXMNUDgfGNF40EyDl5J9JmxF7NsBpZKr6IFFJHz8r2WAMU1qN0zcWz7KbMrk6eYHGF++7B4mp/+lvz35M/1T+Lplr4Q3eEUJBTyq/3+QNQzjTAj7VLsUDLov4bCRzs5zo1L/26jmMooJqW5+BkT1b83U+GbMkqtTuRWexaC8nQG3RsUgNvPWMTh4LTHGoYa5bMP5W9n71GyfB7BziLHcQwOj5PDx4j7QdU2KmASQVDjNR8dzMb6huXPkACFXpt47dU4SGOGRSZU0AWmQC808b6EvzqY9rwttlyS+bkH2IBwT6G9agsotxPm6jTBAP55qLqo2cRA+JsZFvASuJ3VI0ThL04Kzr4MQYCunvHnLASX2+LbLw==',3,101117,'ICS-ATTACK.TRISIS/TRITON WRITE REQUEST','ICS-ATTACK.TRISIS/TRITON WRITE REQUEST',NULL,1,NULL,0,2,0,12),(NULL,'1591739768215462186',0,'LiMJJmW3x/LdsJOZvMYukHIBYQak1nzx102tJGXMNUDgfGNF40EyDl5J9JmxF7NsBpZKr6IFFJHz8r2WAMU1qBsu9Nb5vziRGqv+WMrmHj1uBer3K+Qha5uxkUzawkeEFS0mrcG20QCUE8cvG/FAos8q+QV3JGNbgY5RL27K6QcN95k6W3k3OhIqUgC7moLOqdmtq5TtirkP8PEntwyoc2TzitH7tBz8pfdmWacfKumsPKcS26IjmUTRGt42T+p/vQCPq4TdKExZXCzkeQF7RjTqYiMa2EoocH6AbHvzl3b7tWJ4n/uPGDRm2FvFVASIPijPoeIdrFIiic6a5FfEknuZPIPf0L8wx5+je/mc4jZiomDxYiSdGBeWNJhkG7epaf6xERn23xazC9PZ1yKbXdfSoXa2V6qQhl5N1imfqj/Kwcq+ALnOWgH179m7e07btXbGvc4zzucEza/d2Gr7Nqz0v1l0W8PavzocYmnVlOPfuStHNgB0sQlYtdVTXsD7',3,101118,'ICS-ATTACK.TRISIS/TRITON EXECUTE REQUEST','ICS-ATTACK.TRISIS/TRITON EXECUTE REQUEST',NULL,1,NULL,0,2,0,12);"""
            res = db.write_db(sql_str)
            if res == 0:
                logger.info("add_signatures ok.")
            else:
                logger.error("add_signatures write_db error.")
        except:
            logger.error("add_signatures error.")

    @staticmethod
    def add_vulnerabilities():
        db = DbProxy()
        try:
            sql_str = """INSERT INTO `vulnerabilities`  values ('1591739768215462186',1,'code_execution','ICS-ATTACK.TRISIS/TRITON EXECUTE REQUEST',NULL,'施耐德电气Triconex Tricon MP3008存在漏洞。恶意软件可以在攻陷SIS系统后，对SIS系统逻辑进行重编程，使SIS系统产生意外动作，对正常生产活动造成影响；或是造成SIS系统失效，在发生安全隐患或安全风险时无法及时实行和启动安全保护机制；亦或在攻陷SIS系统后，对DCS系统实施攻击，并通过SIS系统与DCS系统的联合作用，对工业设备、生产活动以及操作人员的人身安全造成巨大威胁。',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2017-12-14',101118,0),('1065387488247104870',1,'code_execution','ICS-ATTACK.TRISIS/TRITON READ REQUEST',NULL,'施耐德电气Triconex Tricon MP3008存在漏洞。恶意软件可以在攻陷SIS系统后，对SIS系统逻辑进行重编程，使SIS系统产生意外动作，对正常生产活动造成影响；或是造成SIS系统失效，在发生安全隐患或安全风险时无法及时实行和启动安全保护机制；亦或在攻陷SIS系统后，对DCS系统实施攻击，并通过SIS系统与DCS系统的联合作用，对工业设备、生产活动以及操作人员的人身安全造成巨大威胁。',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2017-12-14',101116,0),('2875134312413836186',1,'code_execution','ICS-ATTACK.TRISIS/TRITON WRITE REQUEST',NULL,'施耐德电气Triconex Tricon MP3008存在漏洞。恶意软件可以在攻陷SIS系统后，对SIS系统逻辑进行重编程，使SIS系统产生意外动作，对正常生产活动造成影响；或是造成SIS系统失效，在发生安全隐患或安全风险时无法及时实行和启动安全保护机制；亦或在攻陷SIS系统后，对DCS系统实施攻击，并通过SIS系统与DCS系统的联合作用，对工业设备、生产活动以及操作人员的人身安全造成巨大威胁。',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2017-12-14',101117,0);"""
            res = db.write_db(sql_str)
            if res == 0:
                logger.info("add_vulnerabilities ok.")
            else:
                logger.error("add_vulnerabilities write_db error.")
        except:
            logger.error("add_vulnerabilities error.")

    @staticmethod
    def run():
        try:
            MysqlDbUpgradeA.add_signatures()
            MysqlDbUpgradeA.add_process()
            MysqlDbUpgradeA.add_vulnerabilities()
            MysqlDbUpgradeA.add_process()
            logger.info("MysqlDbUpgradeA run finished.")
            return True
        except:
            logger.error("MysqlDbUpgradeA run error.")
            return False
