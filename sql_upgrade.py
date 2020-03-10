#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import json
import logging
import threading
import time
import inspect
import importlib
import pkgutil
from global_function import upgrade_mysql
from global_function import upgrade_sql
from global_function.log_oper import *


logger = logging.getLogger("sql_update_log")
ver_list = ["V1.0"]


class UpgradeMysql(threading.Thread):
    """
    执行数据库升级的类
    """
    def __init__(self, run_list):
        super(UpgradeMysql, self).__init__()
        self.run_class_list = run_list
        self.level = [LOG_ALERT, LOG_INFO]

    @staticmethod
    def get_keystone_new_version():
        """
        获取新版本中数据库的版本信息
        :return:
        """
        sqlpath = "/app/share/keystone_new.sql"
        tag = "SQL file version: "
        sqlverion = "V1.0"
        try:
            with open(sqlpath, "r") as f:
                for line in f.readlines():
                    if tag in line:
                        sqlverion = line.split(tag)[1].strip()
            return sqlverion
        except:
            logger.error("get_new_version failed.")
            return sqlverion

    @staticmethod
    def get_new_version():
        """获取新版本信息"""
        if os.path.exists("/app/share/keystone_config.sql"):
            tag = "SQL file version: "
            conf_verion = ""
            with open("/app/share/keystone_config.sql", "r") as f:
                for line in f.readlines():
                    if tag in line:
                        conf_verion = line.split(tag)[1].strip()
                        break
            old_version = UpgradeMysql.get_keystone_new_version()
            if old_version == conf_verion:
                newversion = old_version
            else:
                newversion = ""
        else:
            newversion = UpgradeMysql.get_keystone_new_version()
        logger.info("new_version: " + str(newversion))
        return newversion

    @staticmethod
    def get_old_version():
        """
        获取升级前版本中数据库的版本信息
        由于upgrade_info.json在u盘安装时并不存在,因此在启动过程获取旧版本信息时执行一次判断,若该文件不存在则去创建改文件并存储版本信息.
        :return:
        """
        verpath = "/data/mysql/upgrade_info.json"
        try:
            if os.path.exists(verpath):
                with open(verpath, "r") as f:
                    ver_dict = json.loads(f.readline())
                    oldversion = ver_dict.get("from_ver", "V1.0")
            else:
                # 使用u盘安装或老版本(不支持数据库升级的版本)升级到新版本时会进入该流程,该过程默认去读取keystone_new.sql文件,获取不到数据库版本信息时取为V1.0
                # 不能用这个方法的原因是会发生没有版本文件便会默认获取最新版本文件,因此异常情况默认版本为1.0
                # oldversion = UpgradeMysql.get_new_version()
                oldversion = "V1.0"
        except:
            logger.error("get_old_version failed.")
            oldversion = "V1.0"
        return oldversion

    @staticmethod
    def get_class_list():
        """
        获取所有的用于版本升级的类,并存储到数组中
        :return:
        """
        try:
            parent_path = os.path.dirname(__file__)
            path = os.path.join(parent_path, 'global_function/upgrade_mysql')
            # path = "global_function/upgrade_mysql"
            modules = [name for _, name, _ in pkgutil.iter_modules([path])]
            class_list = []
            for m in modules:
                mod_name = ".".join(['global_function.upgrade_mysql', m])
                module_ = importlib.import_module(mod_name)
                for name, obj in inspect.getmembers(module_):
                    if inspect.isclass(obj):
                        class_ = getattr(module_, name)
                        if issubclass(class_, module_.MysqlDbUpgradeBase):
                            class_list.append(class_)
            return class_list
        except:
            logger.error("get_class_list error.")
            return []

    @staticmethod
    def get_ver_list():
        """
        从V1.0版本起执行递归获取升级版本顺序表
        :return:
        """
        try:
            class_list = UpgradeMysql.get_class_list()
            for _class in class_list:
                if _class.from_ver == ver_list[-1]:
                    version = _class.to_ver
                    ver_list.append(version)
                    logger.info("version_list append a version: "+version)
                    UpgradeMysql.get_ver_list()
            return ver_list
        except:
            logger.error("get_ver_list error.")
            return []

    @staticmethod
    def upgrade_judge():
        """
        判断是否可升级,通过获取version信息判断是否在version列表中
        :return:True/False
        """
        newversion = UpgradeMysql.get_new_version()
        oldversion = UpgradeMysql.get_old_version()
        logger.info("oldversion: " + oldversion)
        logger.info("newversion: " + newversion)
        version_list = UpgradeMysql.get_ver_list()
        logger.info("all version list: "+str(version_list))
        class_list = UpgradeMysql.get_class_list()
        logger.info("all class list: "+str(class_list))
        run_class_list = []
        try:
            if version_list.index(newversion) > version_list.index(oldversion):
                logger.info("current version support upgrade, upgrade will start...")
                from_version_list = version_list[version_list.index(oldversion):version_list.index(newversion)]
                for ver in from_version_list:
                    for cls in class_list:
                        if cls.from_ver == ver:
                            run_class_list.append(cls)
                return run_class_list
            else:
                logger.info("current version not support upgrade.")
                return None
        except:
            logger.info("version info not in version_list,not support upgrade.")
            return None

    @staticmethod
    def upgrade_class_run(run_class_array):
        """
        执行需要执行的类并进行进度管理
        :return:
        """
        logger.info(run_class_array)
        try:
            for cls in run_class_array:
                upgrade_mysql.PROGRESS_DICT["total_num"] += cls.num
            logger.info("upgrade table total_num:" + str(upgrade_mysql.PROGRESS_DICT["total_num"]))
            for cls in run_class_array:
                cls.run()
                # res = cls.run()
                # if not res:
                #     return False
            logger.info("all upgrade class run finished.")
            return True
        except:
            logger.error("upgrade table run error.")
            return False

    def deal_upgrade_log(self, pid):
        """
        判断升级成功还是失败,并写入系统日志
        :return:
        """
        content = [u'数据库升级失败', u'数据库升级成功']
        msg = {'Type': SYSTEM_TYPE, 'LogLevel': self.level[pid], 'Content': content[pid], 'Componet': 'sql'}
        send_log_db(MODULE_SYSTEM, msg)

    def upgrade_handle(self, run_class_array):
        """
        数据库升级的主处理程序
        :return:
        """
        if not os.path.exists("/data/mysql/sql_upgrade_error.flag"):
            os.system("touch /data/mysql/sql_upgrade_error.flag")
        if not os.path.exists("/data/mysql/sql_backup_error.flag"):
            os.system("touch /data/mysql/sql_backup_error.flag")
        upgrade_mysql.MysqlDbUpgradeBase.mysql_dump()
        run_res = UpgradeMysql.upgrade_class_run(run_class_array)
        if not run_res:
            command = "touch /data/mysql/mysql_upgrade_fail"
            os.system(command)
            load_res = upgrade_mysql.MysqlDbUpgradeBase.mysql_load()
            if load_res:
                command = "touch /data/mysql/mysql_upgrade_restore"
                os.system(command)
            self.deal_upgrade_log(0)
        upgrade_mysql.MysqlDbUpgradeBase.mysql_del_copy()
        self.deal_upgrade_log(1)
        rm_command = "rm /data/mysql/sql_upgrade_error.flag"
        os.system(rm_command)

    @staticmethod
    def make_ver_flag():
        """
        获取to_ver数据库版本信息,并存储到upgrade_info.json文件中以备使用
        :return:
        """
        try:
            sqlverion = UpgradeMysql.get_new_version()
            versionpath = "/data/mysql/upgrade_info.json"
            if not os.path.exists(versionpath):
                command = "touch %s" % versionpath
                os.system(command)
            dict = {"from_ver": sqlverion}
            with open(versionpath, "w+") as f:
                f.write(json.dumps(dict))
            logger.info("write mysql from_version success.")
        except:
            logger.error(traceback.format_exc())

    def run(self):
        try:
            if os.path.exists("/data/mysql/sql_upgrade_error.flag"):
                self.deal_upgrade_log(0)
                if os.path.exists("/data/mysql/sql_backup_error.flag"):
                    self.upgrade_handle(self.run_class_list)
                else:
                    upgrade_mysql.MysqlDbUpgradeBase.mysql_load()
                    self.upgrade_handle(self.run_class_list)
            else:
                self.upgrade_handle(self.run_class_list)
            UpgradeMysql.make_ver_flag()
            time.sleep(5)
            command = "touch /app/bin/progress_stop_app.flag"
            os.system(command)
            os._exit(0)
        except:
            logger.error("mysql_db_upgrade run error.")
            command = "touch /app/bin/progress_stop_app.flag"
            os.system(command)


if __name__ == '__main__':
    # t2 = threading.Thread(target=get_process,)
    # t2.run()
    run_class_list = UpgradeMysql.get_class_list()
    # update_sql = UpgradeMysql(run_class_list)
    # update_sql.run()
    print(run_class_list)
