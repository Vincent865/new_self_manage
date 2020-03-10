#!/usr/bin/python
# -*- coding:utf-8 -*-

import traceback

from flask import Response,send_from_directory,Blueprint,request,make_response,jsonify,current_app
from flask_login.utils import login_required
from global_function.global_var import get_oper_ip_info
from global_function.log_oper import send_log_db,MODULE_OPERATION

down_user_manual_page=Blueprint('down_user_manual_page',__name__)

@down_user_manual_page.route('/download_user_manual')
@login_required
def down_user_manaual():
    directory='/app/local/share/new_self_manage'
    filename='天地和兴工控安全审计平台使用手册.pdf'
    ret=0 # 成功
    try:
        response = send_from_directory(directory, filename, as_attachment=True)
    except:
        ret=1
        response =make_response('')
        current_app.logger.error(traceback.format_exc())
    msg = {}
    userip = get_oper_ip_info(request)
    loginuser = request.args.get('loginuser', '')
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = u'下载用户使用手册'
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = ret
    send_log_db(MODULE_OPERATION, msg)
    return response


