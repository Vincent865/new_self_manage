#!/usr/bin/python
# *-* coding:utf-8 *-*

import logging
import os
import sys
import time
import threading
import traceback

from flask import Flask
from flask.ext.cors import CORS

from global_function.log_config import GetLogLevelConf
from logging.handlers import RotatingFileHandler, SysLogHandler
from app.progress_bar import bp_progress
from sql_upgrade import UpgradeMysql

app = Flask(__name__)
CORS(app)
app.register_blueprint(bp_progress)
logger = logging.getLogger("sql_update_log")


class ProgressShow(object):
    """
    进度展示执行页面,实现程序启动运行
    """
    def setup_logger(self):
        output_file = '/data/log/sql_update.log'
        logger = logging.getLogger('sql_update_log')
        logger.setLevel(GetLogLevelConf())  # Log等级总开关
        # create a rolling file handler
        try:
            handler = RotatingFileHandler(output_file, mode='a',
                                          maxBytes=1024 * 1024 * 10, backupCount=10)
        except:
            handler = SysLogHandler()
        handler.setLevel(GetLogLevelConf())  # 输出到file的log等级的开关
        handler.setFormatter(
            logging.Formatter("[%(asctime)s -%(levelname)5s- %(filename)20s:%(lineno)3s]    %(message)s"))
        logger.addHandler(handler)

    def run(self):
        """
        :return:
        """
        self.setup_logger()
        try:
            class_list = UpgradeMysql.upgrade_judge()
            if class_list:
                logger.info('database upgrade starting...')
                # t = threading.Thread(target=db_upgratde, args=(123,))
                upgrade = UpgradeMysql(class_list)
                upgrade.setDaemon(True)  # 设置线程为后台线程
                upgrade.start()

                app.run('0.0.0.0', ssl_context='adhoc', port=443)
            else:
                UpgradeMysql.make_ver_flag()
                os.system("touch /app/bin/progress_stop_app.flag")
        except:
            logger.error("ProgressShow app run error.")
            os.system("touch /app/bin/progress_stop_app.flag")


if __name__ == '__main__':
    progress = ProgressShow()
    progress.run()
