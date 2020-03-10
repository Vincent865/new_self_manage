#!/usr/bin/python
# -*- coding: utf-8 -*-

import commands  # commands 模块在py3中被废弃
from flask import current_app
import traceback


def excute_command(cmdStr):
    '''
    执行底层指令，并记录操作日志
    :param cmdStr: 指令字符串
    :return: 成功：True ,失败：False
    '''

    # COMMAND_INCOMPLETE = 1
    # WRONG_IP_ADDRESS_FORMAT = 2
    # MALFORMED_ADDRESS = 3
    # WRONG_INTERFACE_NAME = 4
    # PARAMETER_EXCEED_RANGE = 5
    #
    # e_msg = {
    #     COMMAND_INCOMPLETE: '命令不完整',
    #     WRONG_IP_ADDRESS_FORMAT: '地址格式错误 eg：0.0.0.0、192.168.1.255',
    #     MALFORMED_ADDRESS: '地址格式不正确',
    #     WRONG_INTERFACE_NAME: '接口名称错误',
    #     PARAMETER_EXCEED_RANGE: '参数超过限制'
    # }

    msg = '指令执行成功'
    flag = True
    try:
        res, txt = commands.getstatusoutput(cmdStr)
        if res != 0:
            flag = False
            msg = "下发命令失败"
            current_app.logger.info(
                "command sending faild,iptables commangs:{0},status code:{1},error meesage{2}".format(cmdStr, res,
                                                                                                      txt))
            msg = ("%s ！错误码：%d") % (msg, res)
        else:
            current_app.logger.info(
                "command sending successed,iptables commangs:{0}. status code:{1}".format(cmdStr, res))

    except:
        current_app.logger.error(traceback.format_exc())
    return flag, msg, txt
