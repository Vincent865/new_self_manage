#!/usr/bin/python
# -*- coding: UTF-8 -*-
from flask import request
from flask import jsonify
from flask import Blueprint
from flask import current_app
from global_function.cmdline_oper import *
from global_function.signature_black import *
from global_function.log_oper import *
from werkzeug import secure_filename
#flask-login
from flask_login.utils import login_required
import traceback

blacklist_page = Blueprint('blacklist_page', __name__, template_folder='templates')
ALLOWED_EXTENSIONS = set(['zip'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@blacklist_page.route('/black-list-add.html', methods=['GET', 'POST'])
@login_required
def mw_blacklist_add():
    error = None
    status = 0
    if request.method == 'POST':
        try:
            file = request.files['blacklist_fileUpload']
            print file.filename
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                command_str = "unzip -o "+UPLOAD_FOLDER+filename + " -d "+UPLOAD_FOLDER
                commands.getoutput(command_str)
                if os.path.exists(UPLOAD_FOLDER+"threat.json") and os.path.exists(UPLOAD_FOLDER+"signature.rules"):
                    InsertjsonDataDb(UPLOAD_FOLDER+"threat.json")
                    InsertRuleDb(UPLOAD_FOLDER+"signature.rules")
                else:
                    return jsonify({'status': status})
                commands.getoutput("rm -rf "+UPLOAD_FOLDER+"threat.json")
                commands.getoutput("rm -rf "+UPLOAD_FOLDER+"signature.rules")
                commands.getoutput("rm -rf "+UPLOAD_FOLDER+filename)
                current_app.logger.info("add blacklist success!")
                status = 1
                return jsonify({'status': status})
            else:
                current_app.logger.error("blacklist file error!")
                return jsonify({'status': status})
        except:
            current_app.logger.error(traceback.format_exc())
            return jsonify({'status': status})
    else:
        current_app.logger.error("method not allowed")
        return jsonify({'status': status})


@blacklist_page.route('/blacklistSearch', methods=['GET', 'POST'])
@login_required
def mw_blacklist_search():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    data = []
    total = 0
    sql_str = "SELECT threatName,publishDate,signatures.deleted,riskLevel,signatures.sid,action,eventtype \
                FROM signatures,vulnerabilities where signatures.vulnerabilityId = vulnerabilities.vulnerabilityId"
    sum_str = "SELECT count(*) FROM signatures,vulnerabilities where signatures.vulnerabilityId = vulnerabilities.vulnerabilityId"
    num_str = "select count(*) from signatures where signatures.deleted=1"
    if request.method == 'POST':
        post_data = request.get_json()
        page = int(post_data['page'])
        status = post_data['status']
        type = post_data['type']
        name = post_data['name']
    if request.method == 'GET':
        page = request.args.get("page", 0, type=int)
        status = request.args.get("status")
        type = request.args.get("type")
        name = request.args.get("name")
    add_str = ' limit ' + str((page-1)*10)+',10;'
    if status is not None and status != '0' and status != '1':
        status = None
    if status is not None:
        status = status.encode('utf8')
        sql_str += " and signatures.deleted=%s" % (status)
        sum_str += " and signatures.deleted=%s" % (status)
    if type is not None and len(type) > 0:
        type = type.encode('utf8')
        sql_str += ' and eventtype=%s' % (type)
        sum_str += ' and eventtype=%s' % (type)
        #num_str += ' and eventtype=%s' % (type)
    if name is not None and len(name) > 0:
        name = name.encode('utf8')
        sql_str += ' and threatName like "%%%s%%"' % (name)
        sum_str += ' and threatName like "%%%s%%"' % (name)
        #num_str += ' and threatName like "%%%s%%"' % (name)
    sql_str += add_str
    result, rows = db_proxy.read_db(sql_str)
    try:
        for row in rows:
            row = list(row)
            index = row[0].find('<')
            if index != -1:
                row[0] = row[0].replace('<', '~')
            data.append(row)
    except:
        current_app.logger.error(traceback.format_exc())
    result, rows = db_proxy.read_db(sum_str)
    for s in rows:
        total = s[0]
    result, rows = db_proxy.read_db(num_str)
    num = rows[0][0]
    return jsonify({'rows': data, 'total': total, 'page': page, 'num': num})


@blacklist_page.route('/blacklistDetail')
@login_required
def mw_blacklist_detail():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    id = request.args.get('recordid')
    data = []
    sql_str = "SELECT threatName,category,publishDate,severity,action,cve,requirement,caused,description,signame,riskLevel,signatures.sid \
                FROM signatures,vulnerabilities where signatures.vulnerabilityId = vulnerabilities.vulnerabilityId and signatures.sid="+id
    result,rows = db_proxy.read_db(sql_str)
    dev_type = get_dev_type()
    if dev_type.find("KEA") != -1:
        for row in rows:
            row = list(row)
            row[4] = 1
            data.append(row)
    else:
        for row in rows:
            data.append(row)
    return jsonify({'rows': data})


@blacklist_page.route('/blacklistAddRes', methods=['GET', 'POST'])
@login_required
def mw_blacklist_addres():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        page = request.args.get('addPage', 0, type=int)
        tmp_all = request.args.get('isAll', 0, type=int)
    else:
        post_data = request.get_json()
        page = int(post_data['addPage'])
        tmp_all = int(post_data['isAll'])

    if tmp_all == 1:
        sql_str = "update signatures set checked=1"
        result = db_proxy.write_db(sql_str)
    else:
        add_str = ' limit ' + str((page-1)*10)+',10;'
        sql_str = "update signatures set checked=1" + add_str
        result = db_proxy.write_db(sql_str)
    return jsonify({'status': 1})


@blacklist_page.route('/blacklistCheckAddRes', methods=['GET', 'POST'])
@login_required
def mw_blacklist_checkaddres():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        sids = request.args.get('sids')
    else:
        post_data = request.get_json()
        sids = post_data['sids']
    sql_str = "update signatures set checked=1 where sid in ("
    tmp_sids = sids.split(",")
    for sid in tmp_sids:
        sql_str += sid
        sql_str += ','
    sql_str = sql_str[:-1]+")"
    # send_write_cmd(TYPE_APP_SOCKET,sql_str)
    result = db_proxy.write_db(sql_str)
    return jsonify({'status': 1})


@blacklist_page.route('/blacklistSetAll', methods=['GET', 'POST'])
@login_required
def mw_blacklist_setall():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        action = request.args.get('action')
        loginuser = request.args.get('loginuser')
    else:
        post_data = request.get_json()
        action = post_data['action']
        loginuser = post_data['loginuser']
    result = db_proxy.write_db("UPDATE signatures set action=%s" % action)
    mw_blacklist_deploy()
    # send operation log
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = u"设置所有黑名单规则的动作为:" + str(action)
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


def mw_blacklist_deploy():
    time.sleep(3)
    body_str = "select body,action from signatures where deleted=1"
    send_deploy_cmd(TYPE_APP_SOCKET,body_str)
    # reload_ipmac_rules()
    realod_all_rules()


@blacklist_page.route('/blacklistShowDeploy')
@login_required
def mw_blacklist_showdeploy():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    page = request.args.get('page', 0, type=int)
    status = request.args.get('status', 0, type=int)
    data = []
    total = 0
    add_str = ' limit ' + str((page-1)*10)+',10;'
    sql_str = "SELECT threatName,publishDate,signatures.deleted,riskLevel,signatures.sid \
                FROM signatures,vulnerabilities where signatures.vulnerabilityId = vulnerabilities.vulnerabilityId and signatures.deleted="+str(status)+add_str
    result, rows = db_proxy.read_db(sql_str)
    for row in rows:
        data.append(row)
    sum_str = "SELECT count(*) FROM signatures,vulnerabilities \
                where signatures.vulnerabilityId = vulnerabilities.vulnerabilityId and signatures.deleted="+str(status)
    result, rows = db_proxy.read_db(sum_str)
    for s in rows:
        total = s[0]
    return jsonify({'rows': data, 'total': total, 'page': page})


@blacklist_page.route('/blacklistClear', methods=['GET', 'POST'])
@login_required
def mw_blacklist_clear():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "UPDATE signatures set deleted=0"
    result = db_proxy.write_db(sql_str)
    file_handle = open(BLACK_LIST_PATH, "w")
    file_handle.close()
    # reload_ipmac_rules()
    realod_all_rules()
    # send operation log
    msg = {}
    userip = get_oper_ip_info(request)
    if request.method == 'GET':
        loginuser = request.args.get('loginuser')
    else:
        post_data = request.get_json()
        loginuser = post_data['loginuser']
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = u"清空所有黑名单部署规则"
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@blacklist_page.route('/blacklistUpdate', methods=['GET', 'POST'])
@login_required
def mw_blacklist_update():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        action = request.args.get('action', 0, type=int)
        risk = request.args.get('risk', 0, type=int)
        sid = request.args.get('sid')
        loginuser = request.args.get('loginuser')
    else:
        post_data = request.get_json()
        action = int(post_data['action'])
        # risk = int(post_data['risk'])
        sid = post_data['sid']
        loginuser = post_data['loginuser']
    sql_str = "update signatures set action="+str(action)+" where sid="+sid
    result = db_proxy.write_db(sql_str)
    result, rows = db_proxy.read_db("select deleted from signatures where sid = %s" % sid)
    if result == 0:
        if rows[0][0] == 1:
            mw_blacklist_deploy()
    # send operation log
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = u"修改单条黑名单规则: sid=" + sid + ",action=" + str(action)
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@blacklist_page.route('/getblacklistCheckedRes')
@login_required
def mw_blacklist_checked_res():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    page = request.args.get('page', 0, type=int)
    data = []
    add_str = ' limit ' + str((page-1)*10)+',10;'
    sql_str = "SELECT threatName,action,riskLevel,signatures.sid FROM signatures,vulnerabilities \
                where signatures.vulnerabilityId = vulnerabilities.vulnerabilityId and checked=1"
    sql_str+=add_str
    result,rows = db_proxy.read_db(sql_str)
    for row in rows:
        data.append(row)
    sum_str = "SELECT count(*) FROM signatures where checked=1"
    result,rows = db_proxy.read_db(sum_str)
    total = rows[0][0]
    return jsonify({'rows': data, 'total': total, 'page': page})


@blacklist_page.route('/clearAllChecked', methods=['GET', 'POST'])
@login_required
def mw_blacklist_clear_allchecked():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "update signatures set checked=0"
    result = db_proxy.write_db(sql_str)
    return jsonify({'status': 1})


@blacklist_page.route('/clearCheckedRule', methods=['GET', 'POST'])
@login_required
def mw_blacklist_clear_onechecked():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        sid = request.args.get('sid')
    else:
        post_data = request.get_json()
        sid = post_data['sid']
    sql_str = "update signatures set checked=0 where sid=" + sid
    result = db_proxy.write_db(sql_str)
    return jsonify({'status': 1})


@blacklist_page.route('/startAllBlacklist', methods=['GET', 'POST'])
@login_required
def mw_blacklist_startallrules():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "update signatures set deleted=1"
    result = db_proxy.write_db(sql_str)
    mw_blacklist_deploy()
    # send operation log
    msg = {}
    userip = get_oper_ip_info(request)
    if request.method == 'GET':
        loginuser = request.args.get('loginuser')
    else:
        post_data = request.get_json()
        loginuser = post_data['loginuser']
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = u"开启所有黑名单规则"
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@blacklist_page.route('/deleteAllBlacklist', methods=['GET', 'POST'])
@login_required
def mw_blacklist_delteallrules():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "update signatures set deleted=0"
    result = db_proxy.write_db(sql_str)
    file_handle = open(BLACK_LIST_PATH,"w")
    file_handle.close()
    # reload_ipmac_rules()
    realod_all_rules()
    # send operation log
    msg = {}
    userip = get_oper_ip_info(request)
    if request.method == 'GET':
        loginuser = request.args.get('loginuser')
    else:
        post_data = request.get_json()
        loginuser = post_data['loginuser']
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = u"清空所有黑名单部署规则"
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@blacklist_page.route('/getdeployNum')
@login_required
def mw_blacklist_deploynum():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select count(*) from signatures where deleted=1"
    result, rows = db_proxy.read_db(sql_str)
    num = rows[0][0]
    return jsonify({'num': num})


@blacklist_page.route('/startOneBlacklist', methods=['GET', 'POST'])
@login_required
def mw_blacklist_startonerules():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    if request.method == 'GET':
        sid = request.args.get('sid')
        status = request.args.get('status')
        loginuser = request.args.get('loginuser')
    else:
        post_data = request.get_json()
        sid = post_data['sid']
        status = post_data['status']
        loginuser = post_data['loginuser']
    sql_str = "update signatures set deleted="+status+" where sid="+sid
    result = db_proxy.write_db(sql_str)
    mw_blacklist_deploy()
    # send operation log
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    if int(status) == 1:
        msg['Operate'] = u"启用单条黑名单规则: sid=" + sid
    else:
        msg['Operate'] = u"禁用单条黑名单规则: sid=" + sid
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})
