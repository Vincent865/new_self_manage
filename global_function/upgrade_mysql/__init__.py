#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import logging
import time
from global_function.global_var import DbProxy

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

    @staticmethod
    def add_process():
        """
        执行完一个函数调用一次该代码,进度加1
        :return:
        """
        PROGRESS_DICT["done_num"] += 1.0
        process = int((PROGRESS_DICT["done_num"] / PROGRESS_DICT["total_num"]) * 100)
        PROGRESS_DICT["process"] = process
