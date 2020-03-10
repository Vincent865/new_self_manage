#!/usr/bin/python
# -*- coding: utf-8 -*-
import commands
from subprocess import Popen, PIPE
from global_function.log_oper import send_log_db, MODULE_OPERATION


def load_conf_file(filename):
    status = 0
    # send operation log
    msg = {}
    userip = ''
    msg['UserName'] = 'admin'
    msg['UserIP'] = userip
    msg['Operate'] = u"导入配置文件"
    msg['ManageStyle'] = 'WEB'
    with open(filename, 'r+') as f:
        info_str = f.readline()
        start_pos = info_str.find('info:')
        if start_pos < 0:
            status = -1  # 数据库连接错误，执行失败
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            return status
        start_pos += len('info:')
        tmp_info = info_str[start_pos:]
        tmp_pos = tmp_info.find(';')
        tmp_ip = tmp_info[0:tmp_pos]
        tmp_pos += 1
        tmp_name = tmp_info[tmp_pos:]
        msg['UserName'] = tmp_name
        msg['UserIP'] = tmp_ip
        # check device_version
    try:
        process = Popen('/app/local/mysql-5.6.31-linux-glibc2.5-x86_64/bin/mysql -ukeystone -pOptValley@4312',
            stdout=PIPE, stdin=PIPE, shell=True)
        process.stdin.write('use keystone_config\n')
        process.stdin.write('source %s\n' % filename)
        process.stdin.write('exit\n')
        process.wait()
    except:
        status = -4  # 配置文件格式错误，执行失败
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        return status
    status = 1
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return status


def load_confbak_file(filename):
    try:
        process = Popen(
            '/app/local/mysql-5.6.31-linux-glibc2.5-x86_64/bin/mysql -ukeystone -pOptValley@4312',
            stdout=PIPE, stdin=PIPE, shell=True)
        process.stdin.write('use keystone_config\n')
        process.stdin.write(
            'source %s\n' % filename)
        process.stdin.write('exit\n')
        process.wait()
    except:
        status = -4  # 配置文件格式错误，执行失败
        return status
    status = 1
    return status


def main():
    try:
        res = load_conf_file('/data/rules/import_config.sql')
        # load_itf_config()
    except:
        res = 0
    if res != 1:
        load_confbak_file('/data/rules/import_config_bak.sql')
    commands.getoutput('rm -f /data/rules/import_config.sql')
    commands.getoutput('rm -f /data/rules/import_config_bak.sql')


if __name__ == '__main__':
    main()
