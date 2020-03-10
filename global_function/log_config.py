#!/usr/bin/python
# -*- coding:UTF-8 -*-
import logging
# from logging.handlers import RotatingFileHandler
from global_function.global_var import *


LOGCONFIG_PATH = "/data/db/log_config.conf"
if g_dpi_plat_type == DEV_PLT_X86:
    LOGCONFIG_PATH = "/conf/db/log_config.conf"


def GetLogLevelConf():
    with open(LOGCONFIG_PATH, 'r') as f:
        file_data = f.readline()
        log_level = 'logging.' + file_data.split('SET LOGLEVEL:')[1].split('\n')[0]
    if log_level == "logging.DEBUG":
        return logging.DEBUG
    if log_level == "logging.INFO":
        return logging.INFO
    if log_level == "logging.WARNING":
        return logging.WARNING
    if log_level == "logging.ERROR":
        return logging.ERROR
    if log_level == "logging.CRITICAL":
        return logging.CRITICAL


def LogConfig(log_level, log_name="flask_engine.log"):
    if log_level == "logging.DEBUG":
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename='/data/log/' + log_name,
                            filemode='a')
    if log_level == "logging.INFO":
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename='/data/log/' + log_name,
                            filemode='a')
    if log_level == "logging.WARNING":
        logging.basicConfig(level=logging.WARNING,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename='/data/log/' + log_name,
                            filemode='a')
    if log_level == "logging.ERROR":
        logging.basicConfig(level=logging.ERROR,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename='/data/log/' + log_name,
                            filemode='a')
    if log_level == "logging.CRITICAL":
        logging.basicConfig(level=logging.CRITICAL,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename='/data/log/' + log_name,
                            filemode='a')


def SetLogLevel():
    with open(LOGCONFIG_PATH, 'r') as f:
        file_data = f.readline()
        log_level = 'logging.' + file_data.split('SET LOGLEVEL:')[1].split('\n')[0]
    if not log_level:
        log_level = "logging.INFO"
    LogConfig(log_level)
