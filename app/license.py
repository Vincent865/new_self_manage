#!/usr/bin/python
# -*- coding:UTF-8 -*-
import os
import traceback

from flask import Blueprint, jsonify, request, current_app
from flask_login.utils import login_required

from global_function.global_var import DbProxy, CONFIG_DB_NAME, get_oper_ip_info
from global_function.log_oper import send_log_db, MODULE_OPERATION

license_page = Blueprint('license_page', __name__, template_folder='templates')

LICENSE_UPLOAD_FOLDER = '/data/licensetmpfolder'
LICENSE_RECOVER_ADDR = '/data/licsystemreset/system_reset.lic'


def license_status_verify():
    license_res = str(os.popen('lic_verify /data/licensetmpfolder/licensefile.lic').read())
    license_legal = int(license_res.split("-")[0])
    license_time = license_res.split("-")[1]
    license_func = license_res.split("-")[2]

    # 上传文件合法
    if license_legal == 1:
        update_str = "update license_info set license_legal = '%s',license_time = '%s',license_func = '%s'" % (
            license_legal, license_time, license_func)
        db_proxy = DbProxy(CONFIG_DB_NAME)
        res = db_proxy.write_db(update_str)
        return license_legal, license_time, license_func
    else:
        return 0, 0, 0


@license_page.route('/license_cur_status')
@login_required
def search_license_status():
    """
    查询license是否授权
    """
    # 恢复出厂设置后更新授权状态为True
    if os.path.exists(LICENSE_RECOVER_ADDR):
        update_str = "update license_info set license_legal = 1,license_time = '0',license_func = '0'"
        db_proxy = DbProxy(CONFIG_DB_NAME)
        db_proxy.write_db(update_str)
        os.system('rm -rf /data/licsystemreset')

    search_str = "select license_legal, license_time, license_func from license_info"
    db_proxy = DbProxy(CONFIG_DB_NAME)
    res, rows = db_proxy.read_db(search_str)
    try:
        license_legal = int(rows[0][0])
        license_time = rows[0][1]
        license_func = rows[0][2]
    except:
        return jsonify({'status': 0, "msg": "获取license授权状态错误！"})

    if license_legal == 1:
        # 删除授权文件
        os.system('rm -rf /data/licensetmpfolder/licensefile.lic')
        return jsonify({'status': 1, "license_time": license_time, "license_func": license_func})
    else:
        return jsonify({'status': 0, "msg": "license未授权!"})


@license_page.route('/license_machine_code')
@login_required
def license_info():
    """
    返回机器码
    """
    msg = {}
    userip = get_oper_ip_info(request)
    loginuser = request.args.get('loginuser')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u'license授权，获取机器码'
    msg['Result'] = '1'

    # 从底层获取机器码
    try:
        license_key = os.popen('mc_gen').read()
        update_str = "update license_info set license_key = '%s'" % str(license_key)
        db_proxy = DbProxy(CONFIG_DB_NAME)
        res = db_proxy.write_db(update_str)
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 1, "license_key": license_key})
    except:
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 0, "msg": "获取机器码出错! "})


@license_page.route('/license_file_upload', methods=['POST'])
@login_required
def license_file_info():
    """
    验证上传的license是否合法并返回结果
    """
    loginuser = request.form.get('loginuser')
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['ManageStyle'] = 'WEB'
    msg['Operate'] = u'上传license授权文件'
    msg['Result'] = '1'

    if not os.path.exists(LICENSE_UPLOAD_FOLDER):
        os.makedirs(LICENSE_UPLOAD_FOLDER)
    f = request.files['license_filename']
    if f:
        # 如果路径下有文件则先删除所有文件
        delList = os.listdir(LICENSE_UPLOAD_FOLDER)
        for i in delList:
            filePath = os.path.join(LICENSE_UPLOAD_FOLDER, i)
            if os.path.isfile(filePath):
                os.remove(filePath)
        # 将新文件保存到路径下(所有上传文件重新命名为licensefile.lic)
        new_fname = 'licensefile.lic'
        f.save(os.path.join(LICENSE_UPLOAD_FOLDER, new_fname))
        license_legal, license_time, license_func = license_status_verify()
        if license_legal == 1:
            msg['Result'] = '0'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 1, "license_time": license_time, "license_func": license_func})
        else:
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0, "msg": "无效的license文件，请确认!"})
    else:
        send_log_db(MODULE_OPERATION, msg)
        return jsonify({'status': 0, "msg": "license上传错误!"})

