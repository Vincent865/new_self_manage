#!/usr/bin/python
# -*- coding: UTF-8 -*-
import ctypes
from flask import request
from flask import jsonify
from flask import Blueprint
from flask import current_app
from global_function.log_oper import *
# flask-login
from flask_login.utils import login_required
ukeyauth_page = Blueprint('ukeyauth_page', __name__, template_folder='templates')


@ukeyauth_page.route('/setUserLoginAuthAction', methods=['GET', 'POST'])
def setUserLoginAuthAction():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        result, values = db_proxy.read_db("SELECT auth_switch FROM ukey_auth")
        if result == 0 and len(values) != 0:
            return jsonify({'status': values[0][0]})
        else:
            return jsonify({'status': 0})
    elif request.method == 'POST':
        data = request.get_json()
        action = data['enable']
        loginuser = data['loginuser']
        if int(action) != 0:
            action = 1
        else:
            action = 0
        cmd = "UPDATE ukey_auth set auth_switch='%s'" % (action)
        db_proxy.write_db(cmd)

        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserName'] = loginuser
        msg['UserIP'] = userip
        if action == 1:
            msg['Operate'] = u"开启ukey认证"
        else:
            msg['Operate'] = u"关闭ukey认证"
        msg['ManageStyle'] = 'WEB'
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 1})

UPDATE_PIN_ERRORCODE = ('修改成功', '修改失败', '没有发现ukey', '修改失败', '修改失败', '原PIN码错误')

@ukeyauth_page.route('/changeUkeyAuthPasswd', methods=['POST'])
@login_required
def changeUkeyAuthPasswd():
    if request.method == 'POST':
        data = request.get_json()
        username = data['loginuser']
        old_pw = data['oldpwd']
        new_pw = data['newpwd']

        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserName'] = username
        msg['UserIP'] = userip
        msg['Operate'] = u"修改PIN码"
        msg['ManageStyle'] = 'WEB'

        so = ctypes.CDLL('/lib/x86_64-linux-gnu/libukey.so')
        res = so.sfw_update_ukey_passwd(str(old_pw),8,str(new_pw),8)
        if res == 0:
            msg['Result'] = '0'
        else:
            msg['Result'] = '1'

        tmp_status = 0
        if res == 0:
            tmp_status = 1

        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': tmp_status, 'msg': UPDATE_PIN_ERRORCODE[res]})
