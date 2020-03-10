#!/usr/bin/python
# -*- coding:UTF-8 -*-
import traceback

import ipaddress
from global_function.log_oper import *
from global_function.cmdline_oper import *
from global_function.global_var import get_oper_ip_info
from global_function.cmdline_oper import check_ip_valid
from werkzeug import secure_filename
from flask import send_from_directory
from flask import Blueprint, request, jsonify, current_app
from flask_login.utils import login_required
from global_function.global_var import DbProxy, CONFIG_DB_NAME
from global_function.switch_info import trans_mac, autoGetSwitchInfo

assets_locate_page = Blueprint('assets_locate_page', __name__, template_folder='templates')
SWITCH_ALLOWED_EXTENSIONS = set(['csv'])
SWITCH_UPLOAD_FOLDER = '/data/switchinfo/'
SECURITY_LEVEL_DICT = {"": "", "noAuthNoPriv": "不认证不加密", "authNoPriv": "只认证不加密", "authPriv": "既认证又加密"}
SECURITY_LEVEL_MAP = {"": "", "不认证不加密": "noAuthNoPriv", "只认证不加密": "authNoPriv", "既认证又加密": "authPriv"}
SNMP_VERSION_DICT = {"0": "", "1": "V1", "2": "V2C", "3": "V3"}
SNMP_VERSION_MAP = {"": 0, "V1": 1, "V2C": 2, "V3": 3}


def isIP4or6(data):
    ipFlg = False
    if '/' in data:
        ip = data[:data.rfind('/')]
    else:
        ip = data

    try:
        addr = ipaddress.ip_address(unicode(ip))
        ipFlg = True
    except:
        ipFlg = False

    if ipFlg:
        ip_version = addr.version
        return ip_version
    else:
        return False


def switch_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in SWITCH_ALLOWED_EXTENSIONS


# 验证参数合法性
def verify_params(id, switch_name, ip, type, locate, snmp_version, group_name, security_level, security_name, auth_mode,
                  auth_pwd, priv_mode, priv_pwd, ssh_name, ssh_pwd, flag):
    db_proxy = DbProxy(CONFIG_DB_NAME)
    error_msg = ""
    if len(switch_name.encode("utf-8")) > 32:
        error_msg = u"交换机名称不能超过32个字符"
    if len(switch_name) == 0:
        error_msg = u"交换机名称不能为空"
    if switch_name.find(" ") != -1:
        error_msg = u"交换机名称不能包含空格字符"
    if len(ip) == 0:
        error_msg = u"IP地址信息不能为空"
    if len(locate) == 0:
        error_msg = u"交换机位置不能为空"
    if ip and check_ip_valid(ip) is False:
        error_msg = u'ip格式不合法'
    if len(type.encode("utf-8")) > 64:
        error_msg = u"交换机类型名称不能超过64个字符"
    if len(locate.encode("utf-8")) > 64:
        error_msg = u"位置名称不能超过64个字符"
    if snmp_version == 0 and ssh_name == '':
        error_msg = u"SNMP配置和SSH配置至少配置一条"
    if len(group_name.encode("utf-8")) > 32:
        error_msg = u"团体名不能超过32个字符"

    # 暂不支持ipv6地址的交换机
    res = isIP4or6(ip)
    if res == 6:
        error_msg = u"暂不支持IPv6交换机配置"

    # 查交换机名是否存在
    tmp_name_sql = "select name from switch_info where name = '{}'".format(switch_name)
    if id:  # 编辑时验证
        tmp_name_sql = "select name from switch_info where name = '{}' and id<>{}".format(switch_name, id)
    result, rows = db_proxy.read_db(tmp_name_sql)
    if len(rows) > 0 and not flag:  # 交换机名称重复
        error_msg = u"交换机" + str(switch_name) + u'和已有交换机名称重复，请确认！'

    # 查交换机IP是否存在
    tmp_ip_sql = "select ip from switch_info where ip='%s'" % (ip)
    if id:  # 编辑时验证
        tmp_ip_sql = "select ip from switch_info where ip='%s' and id<>{}".format(ip, id)

    result, rows = db_proxy.read_db(tmp_ip_sql)
    if len(rows) > 0 and not flag:  # 新增编辑是交换机IP重复验证，导入时不验证
        error_msg = u"交换机" + str(switch_name) + u'和已有交换机IP重复，请确认！'

    # 导入文件字段和合法性验证
    if snmp_version not in (0, 1, 2, 3):
        error_msg = u'SNMP版本信息不合法，为空或者"不认证不加密", "只认证不加密","既认证又加密"'
    if security_level not in ("", "authNoPriv", "authPriv", "noAuthNoPriv"):
        error_msg = u'安全等级不合法，为空或者"不认证不加密", "只认证不加密","既认证又加密"'
    if auth_mode not in ("", "MD5", "SHA"):
        error_msg = u'认证方式不合法，为空或者"MD5", "SHA"'
    if priv_mode not in ("", "DES56", "AES128", "3DES"):
        error_msg = u'加密方式不合法，为空或者 "DES56", "AES128", "3DES"'

    # 只配置snmp
    if ssh_name == '' and ssh_pwd == '':
        if snmp_version == 0:
            error_msg = u"SNMP版本不能为空"
        elif snmp_version == 1 and not group_name:
                error_msg = u"团体名不能为空"
        elif snmp_version == 2 and not group_name:
                error_msg = u"团体名不能为空"
        elif snmp_version == 3:
            if not security_name:
                error_msg = u"安全用户名不能为空"
            if len(security_name) > 32:
                error_msg = u"安全用户名不能超过32个字符"
            if len(auth_pwd) > 64:
                error_msg = u'认证密码范围为1-64'
            if len(priv_pwd) > 64:
                error_msg = u'加密密码范围为1-64'
            if security_level == 'authNoPriv':
                if auth_mode == '':
                    error_msg = u"认证方式不能为空"
                if auth_pwd == '':
                    error_msg = u"认证密码不能为空"
            elif security_level == 'authPriv':
                if auth_mode == '':
                    error_msg = u"认证方式不能为空"
                if auth_pwd == '':
                    error_msg = u"认证密码不能为空"
                if priv_mode == '':
                    error_msg = u"认证方式不能为空"
                if priv_pwd == '':
                    error_msg = u"加密密码不能为空！"
    else:  # 只配置ssh或者两个都配置
        if ssh_name == '':
            error_msg = u"SSH配置用户名不能为空"
        if ssh_pwd == '':
            error_msg = u"SSH配置密码不能为空"
        if snmp_version == 3:
            if security_name:
                if len(security_name) > 32:
                    error_msg = u"安全用户名不能超过32个字符"
                if len(auth_pwd) > 64:
                    error_msg = u'认证密码范围为1-64'
                if len(priv_pwd) > 64:
                    error_msg = u'加密密码范围为1-64'
                if security_level == 'authNoPriv':
                    if auth_mode == '':
                        error_msg = u"认证方式不能为空"
                    if auth_pwd == '':
                        error_msg = u"认证密码不能为空"
                elif security_level == 'authPriv':
                    if auth_mode == '':
                        error_msg = u"认证方式不能为空"
                    if auth_pwd == '':
                        error_msg = u"认证密码不能为空"
                    if priv_mode == '':
                        error_msg = u"认证方式不能为空"
                    if priv_pwd == '':
                        error_msg = u"加密密码不能为空！"
    return error_msg


# 交换机列表，增删改查
@assets_locate_page.route('/switch_info', methods=['GET', 'POST', 'DELETE', 'PUT'])
@login_required
def mw_switch_info():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    # 主页面及详情页面获取全部
    if request.method == 'GET':
        ip = request.args.get('ip', '').encode('utf-8')
        locate = request.args.get('locate', '').encode('utf-8')
        name = request.args.get('name', '').encode('utf-8')
        type = request.args.get('type', '').encode('utf-8')
        page = request.args.get('page', 0, type=int)
        sql_str = 'select * from switch_info where 1=1 '
        num_str = 'select count(*) from switch_info where 1=1 '
        if name:
            sql_str += " and name like '%%%s%%'" % name
            num_str += " and name like '%%%s%%'" % name
        if ip:
            sql_str += " and ip like '%%%s%%'" % ip
            num_str += " and ip like '%%%s%%'" % ip
        if type:
            sql_str += " and type like '%%%s%%'" % type
            num_str += " and type like '%%%s%%'" % type
        if locate:
            sql_str += " and locate like '%%%s%%'" % locate
            num_str += " and locate like '%%%s%%'" % locate
        if page:
            limit_str = ' order by id desc limit ' + str((page - 1) * 10) + ',10;'
            sql_str += limit_str
        info = []
        try:
            res, rows = db_proxy.read_db(sql_str)
            for row in rows:
                item = {}
                item["id"] = row[0]
                item["switch_name"] = row[1]
                item["ip"] = row[2]
                item["type"] = row[3]
                item["locate"] = row[4]
                item["snmp_version"] = row[5]
                item["group_name"] = row[6]
                item["security_level"] = row[7]
                item["security_name"] = row[8]
                item["auth_mode"] = row[9]
                item["auth_pwd"] = row[10]
                item["priv_mode"] = row[11]
                item["priv_pwd"] = row[12]
                item["ssh_name"] = row[13]
                item["ssh_pwd"] = row[14]
                info.append(item)

            res, rows = db_proxy.read_db(num_str)
            if res == 0:
                total_num = rows[0][0]
            else:
                total_num = 0
            return jsonify({'data': info, 'num': total_num, 'page': page})
        except:
            current_app.logger.error(traceback.format_exc())
            return jsonify({'data': [], 'num': 0, page: 1})

    # 详情页面新增
    elif request.method == 'POST':
        data = request.get_json()
        oper_msg = {}
        userip = get_oper_ip_info(request)
        loginuser = data.get('loginuser')
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        oper_msg['Result'] = '1'
        try:
            switch_name = data.get("switch_name")
            ip = data.get("ip")
            type = data.get("type").decode("utf-8")
            locate = data.get("locate")
            snmp_version = data.get("snmp_version")
            group_name = data.get("group_name")
            security_level = data.get("security_level")
            security_name = data.get("security_name")
            auth_mode = data.get("auth_mode")
            auth_pwd = data.get("auth_pwd")
            priv_mode = data.get("priv_mode")
            priv_pwd = data.get("priv_pwd")
            ssh_name = data.get("ssh_name")
            ssh_pwd = data.get("ssh_pwd")
            id = 0
            flag = 0  # 字段验证使用
            error_msg = verify_params(id,switch_name, ip, type, locate, snmp_version, group_name, security_level, security_name,
                          auth_mode, auth_pwd, priv_mode, priv_pwd, ssh_name, ssh_pwd,flag)
            if len(error_msg) != 0:
                oper_msg['Result'] = '0'
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({'status': 0, 'msg': error_msg})
        except:
            current_app.logger.error(traceback.format_exc())
            return jsonify({"status": 0, "msg": u"参数错误"})

        try:
            cmd_str = '''insert into switch_info (name,ip,type,locate,snmp_version,group_name,security_level,security_name,auth_mode,auth_pwd,priv_mode,priv_pwd,ssh_name,ssh_pwd) values('{}','{}','{}','{}',{},'{}','{}','{}','{}','{}','{}','{}','{}','{}')'''.format(
                switch_name, ip, type, locate, snmp_version, group_name, security_level, security_name, auth_mode,
                auth_pwd, priv_mode, priv_pwd, ssh_name, ssh_pwd)
            res = db_proxy.write_db(cmd_str)
            if res != 0:
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({"status": 0, "msg": u"添加失败"})

            # 调用计算函数重新计算mac_port表信息，并更新switch_mac_port表交换机名称信息
            sql_str = "select snmp_version,group_name,security_level,security_name,auth_mode,auth_pwd,priv_mode,priv_pwd,ssh_name,ssh_pwd, ip,name from switch_info where name = '{}'".format(
                switch_name)
            res, rows = db_proxy.read_db(sql_str)
            if len(rows) > 0:
                for row in rows:
                    autoGetSwitchInfo.get_one_switch_mac_port(row)

            oper_msg['Result'] = '0'
            oper_msg['Operate'] = "添加交换机:" + switch_name
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 1, "msg": u"添加成功"})
        except:
            current_app.logger.error(traceback.format_exc())
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": u"添加失败"})

    # 详情页面的编辑修改
    elif request.method == 'PUT':
        data = request.get_json()
        try:
            id = data.get("id")
            switch_name = data.get("switch_name")
            ip = data.get("ip")
            type = data.get("type").decode("utf-8")
            locate = data.get("locate")
            snmp_version = data.get("snmp_version")
            group_name = data.get("group_name")
            security_level = data.get("security_level")
            security_name = data.get("security_name")
            auth_mode = data.get("auth_mode")
            auth_pwd = data.get("auth_pwd")
            priv_mode = data.get("priv_mode")
            priv_pwd = data.get("priv_pwd")
            ssh_name = data.get("ssh_name")
            ssh_pwd = data.get("ssh_pwd")
            oper_msg = {}
            userip = get_oper_ip_info(request)
            loginuser = data.get('loginuser')
            oper_msg['UserName'] = loginuser
            oper_msg['UserIP'] = userip
            oper_msg['ManageStyle'] = 'WEB'
            oper_msg['Result'] = '1'
            flag = 0
            error_msg = verify_params(id, switch_name, ip, type, locate, snmp_version, group_name, security_level,security_name,auth_mode, auth_pwd, priv_mode, priv_pwd, ssh_name, ssh_pwd,flag)
            if len(error_msg) != 0:
                oper_msg['Result'] = '0'
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({'status': 0, 'msg': error_msg})
        except:
            current_app.logger.error(traceback.format_exc())
            return jsonify({"status": 0, "msg": u"参数错误"})
        try:
            cmd_str = "select name from switch_info where id={}".format(id)
            res, rows = db_proxy.read_db(cmd_str)
            old_name = rows[0][0]
            if res != 0:
                return jsonify({"status": 0, "msg": u"不存在的id"})

            # delete and add
            del_str = "delete from switch_info where id={}".format(id)
            db_proxy.write_db(del_str)
            cmd_str = '''insert into switch_info (name,ip,type,locate,snmp_version,group_name,security_level,security_name,auth_mode,auth_pwd,priv_mode,priv_pwd,ssh_name,ssh_pwd) values('{}','{}','{}','{}',{},'{}','{}','{}','{}','{}','{}','{}','{}','{}')'''.format(
                switch_name, ip, type, locate, snmp_version, group_name, security_level, security_name, auth_mode,
                auth_pwd, priv_mode, priv_pwd, ssh_name, ssh_pwd)
            res = db_proxy.write_db(cmd_str)
            if res != 0:
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({"status": 0, "msg": u"编辑失败"})

            # 调用计算函数重新计算mac_port表信息，并更新switch_mac_port表交换机名称信息
            sql_str = "select snmp_version,group_name,security_level,security_name,auth_mode,auth_pwd,priv_mode,priv_pwd,ssh_name,ssh_pwd, ip,name from switch_info where name = '{}'".format(
                switch_name)
            res, rows = db_proxy.read_db(sql_str)
            if len(rows) > 0:
                for row in rows:
                    autoGetSwitchInfo.get_one_switch_mac_port(row)
            oper_msg['Operate'] = "编辑交换机内容:" + old_name
            oper_msg['Result'] = '0'
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 1, "msg": u"编辑成功"})
        except:
            current_app.logger.error(traceback.format_exc())
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": u"编辑失败"})

    # 主页面的删除
    elif request.method == "DELETE":
        data = request.get_json()
        userip = get_oper_ip_info(request)
        loginuser = data.get('loginuser')
        oper_msg = {}
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        oper_msg['Result'] = '1'
        try:
            id = data.get("id")
            cmd_str = "select name from switch_info where id in ({})".format(id)
            res, rows = db_proxy.read_db(cmd_str)
            name_list = [row[0] for row in rows]
            content_name_str = ",".join(name_list)
            oper_msg['Operate'] = "删除交换机内容:" + content_name_str
            oper_msg['Result'] = '1'

            # 删除交换机列表mac_port信息表中与之相关的mac_port信息
            del_str = "delete from switch_mac_port where switch_name in (select name from switch_info where id in ({}));".format(id)
            res = db_proxy.write_db(del_str)

            # 删除交换机列表中信息
            del_str = "delete from switch_info where id in ({})".format(id)
            res = db_proxy.write_db(del_str)
            if res != 0:
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({"status": 0, "msg": u"删除失败"})
            oper_msg['Result'] = '0'
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 1, "msg": u"删除成功"})
        except:
            current_app.logger.error(traceback.format_exc())
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": u"删除失败"})


# 导入数据，导入交换机配置
@assets_locate_page.route('/import_switch_info', methods=['POST'])
@login_required
def mw_import_switch_info():
    if request.method == 'POST':
        db_proxy = DbProxy(CONFIG_DB_NAME)
        loginuser = request.form.get('loginuser')
        msg = {}
        userip = get_oper_ip_info(request)
        msg['UserIP'] = userip
        msg['UserName'] = loginuser
        msg['ManageStyle'] = 'WEB'
        try:
            if not os.path.exists(SWITCH_UPLOAD_FOLDER):
                os.makedirs(SWITCH_UPLOAD_FOLDER)
            file = request.files['file']
            if not file or not switch_allowed_file(file.filename):
                return jsonify({'status': 0, 'msg': '导入文件格式错误'})
            filename = secure_filename(file.filename)
            file.save(os.path.join(SWITCH_UPLOAD_FOLDER, filename))
            FileName = '%s%s' % (SWITCH_UPLOAD_FOLDER, filename)
            csvfile = open(FileName, 'rb')
            reader = csv.reader(csvfile, dialect='excel')
            rows = [row for row in reader]
            if rows[0] != ['\xef\xbb\xbf交换机名称', 'IP', '类型', '位置', 'SNMP版本', '团体名', '安全等级', '安全用户名', '认证方式', '认证密码', '加密方式', '加密密码', 'ssh用户名', 'ssh密码']:
                msg['Operate'] = u"导入switch_list"
                msg['Result'] = '1'
                send_log_db(MODULE_OPERATION, msg)
                os.system("rm '%s'" % (FileName))
                return jsonify({'status': 0, 'msg': u"导入文件内容错误"})
            # 验证导入的信息是否合法，任意一条数据不合法就return
            for data in rows[1:]:
                name, ip, type, locate, snmp_version, group_name, security_level, security_name, auth_mode, auth_pwd, priv_mode, priv_pwd, ssh_name, ssh_pwd = data
                id = 0
                flag = 1
                try:
                    # 安全等级，SNMP版本信息转换
                    snmp_version = SNMP_VERSION_MAP[snmp_version]
                    security_level = SECURITY_LEVEL_MAP[security_level]

                    error_msg = verify_params(id, name, ip, type, locate, snmp_version, group_name,
                                              security_level, security_name, auth_mode, auth_pwd, priv_mode,
                                              priv_pwd, ssh_name, ssh_pwd,flag)
                    if len(error_msg) != 0:
                        return jsonify({'status': 0, 'msg': error_msg})
                except:
                    current_app.logger.error(traceback.format_exc())
                    continue

            # 验证完成，导入信息
            csvfile = open(FileName, 'rb')
            reader = csv.reader(csvfile, dialect='excel')
            rows = [row for row in reader]
            for data in rows[1:]:
                name, ip, type, locate, snmp_version, group_name, security_level, security_name, auth_mode, auth_pwd, priv_mode, priv_pwd, ssh_name, ssh_pwd = data
                # 安全等级，SNMP版本信息转换
                security_level = SECURITY_LEVEL_MAP[security_level]
                snmp_version = SNMP_VERSION_MAP[snmp_version]

                # 删除原有信息,导入新信息
                del_str = "delete from switch_info where ip = '{}'".format(ip)
                db_proxy.write_db(del_str)

                sql_str = '''insert into switch_info (name,ip,type,locate,snmp_version,group_name,security_level,security_name,auth_mode,auth_pwd,priv_mode,priv_pwd,ssh_name,ssh_pwd) values('{}','{}','{}','{}',{},'{}','{}','{}','{}','{}','{}','{}','{}','{}')'''.format(
                    name, ip, type, locate, snmp_version, group_name, security_level, security_name, auth_mode,
                    auth_pwd, priv_mode, priv_pwd, ssh_name, ssh_pwd)
                db_proxy.write_db(sql_str)
                # 导入完成后重新计算所有的mac_port信息 导入速度太慢，导入时先导入列表，不计算
                # autoGetSwitchInfo.get_all_switch_mac_port()
            os.system("rm '%s'" % (FileName))
            msg['Operate'] = u"导入switch_list"
            msg['Result'] = '0'
            send_log_db(MODULE_OPERATION, msg)
            status = 1
            return jsonify({'status': status, "msg": "导入成功"})
        except:
            current_app.logger.error(traceback.format_exc())
            msg['Operate'] = u"导入switch_list"
            msg['Result'] = '1'
            send_log_db(MODULE_OPERATION, msg)
            status = 0
            return jsonify({'status': status})


# 导出全部信息，导出交换机配置
@assets_locate_page.route('/export_switch_info')
@login_required
def mw_export_switch_info():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    loginuser = request.args.get('loginuser')
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserIP'] = userip
    msg['UserName'] = loginuser
    msg['ManageStyle'] = 'WEB'
    try:
        # 防止初次导出时无文件报错
        if not os.path.exists(SWITCH_UPLOAD_FOLDER):
            os.makedirs(SWITCH_UPLOAD_FOLDER)
        os.system('rm /data/switchinfo/switch_list.csv')
        csvfile = open('/data/switchinfo/switch_list.csv', 'wb')
        csvfile.write(codecs.BOM_UTF8)
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(['交换机名称', 'IP', '类型', '位置', 'SNMP版本', '团体名', '安全等级' , '安全用户名', '认证方式', '认证密码',
                           '加密方式', '加密密码', 'ssh用户名', 'ssh密码'])
        sql_str = "select name,ip, type, locate,snmp_version,group_name,security_level,security_name,auth_mode,auth_pwd,priv_mode,priv_pwd,ssh_name,ssh_pwd from switch_info order by id desc"
        result, rows = db_proxy.read_db(sql_str)
        for row in rows:
            row = list(row)
            row[6] = SECURITY_LEVEL_DICT[str(row[6])]
            row[4] = SNMP_VERSION_DICT[str(row[4])]
            # 导出时去掉v3版本字段默认信息
            if not row[7]:
                row[4] = ""
                row[6] = ""
                row[8] = ""
                row[10] = ""
            writer.writerow(row)
        csvfile.close()
        msg['Operate'] = u"导出switch_list"
        msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, msg)
        return send_from_directory(SWITCH_UPLOAD_FOLDER, "switch_list.csv", as_attachment=True)
    except:
        current_app.logger.error(traceback.format_exc())
        msg['Operate'] = u"导出switch_list"
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        status = 0
        return jsonify({'status': status})


# 交换机信息，根据mac查交换机信息
@assets_locate_page.route('/get_switch_info_by_mac', methods=['POST'])
@login_required
def mw_get_switch_info():
    if request.method == 'POST':
        db_proxy = DbProxy(CONFIG_DB_NAME)
        post_data = request.get_json()
        page = post_data.get('page', 0)
        mac = post_data.get('mac', '').encode('utf-8')
        sql_str = "select a.name,a.locate, b.port, b.mac from switch_info as a inner join switch_mac_port as b where a.name in (select b.switch_name from switch_mac_port"
        num_str = "select count(*) from switch_info as a inner join switch_mac_port as b where a.name in (select b.switch_name from switch_mac_port"

        if mac:
            sql_str += " where b.mac like '%%%s%%'" % mac
            num_str += " where b.mac like '%%%s%%'" % mac
        sql_str += ")"
        num_str += ")"
        if page:
            limit_str = ' order by a.id desc limit ' + str((page - 1) * 10) + ',10;'
            sql_str += limit_str
        res, rows = db_proxy.read_db(sql_str)

        row_list = []
        # 构造结果
        if len(rows) > 0:
            for row in rows:
                row_list.append(row)

        # 总条数
        res, count = db_proxy.read_db(num_str)
        total = count[0][0]
        return jsonify({'rows': row_list, 'num': total, 'page': page})


# 查看详情,刷新，获取单个交换机的mac_port信息表
@assets_locate_page.route('/switch_mac_port_list', methods=['POST'])
@login_required
def mw_get_switch_info_by_mac():
    if request.method == 'POST':
        db_proxy = DbProxy(CONFIG_DB_NAME)
        post_data = request.get_json()
        switch_name = post_data.get('name')
        flag = post_data.get('flag')  # 刷新flag=1，查看详情flag=0
        if flag:
            # 刷新信息
            sql_str = "select snmp_version,group_name,security_level,security_name,auth_mode,auth_pwd,priv_mode,priv_pwd,ssh_name,ssh_pwd, ip,name from switch_info where name = '{}'".format(
                switch_name)
            res, rows = db_proxy.read_db(sql_str)
            if len(rows) > 0:
                for row in rows:
                    autoGetSwitchInfo.get_one_switch_mac_port(row)

        # 查询出此交换机最新的mac_port详细信息(无需翻页)
        sql_str = "select mac,port from switch_mac_port where switch_name = '{}'".format(switch_name)
        res, rows = db_proxy.read_db(sql_str)
        row_list = []
        if len(rows) > 0:
            for row in rows:
                row_list.append(row)
        return jsonify({'rows': row_list})

