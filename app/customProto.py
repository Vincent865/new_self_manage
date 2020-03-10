#!/usr/bin/python
# -*- coding: UTF-8 -*-
from flask import render_template, send_from_directory
import traceback
from flask import request
from flask import jsonify
from flask import Blueprint
from flask import Response
from flask import current_app
from werkzeug.utils import secure_filename

from global_function.cmdline_oper import *
from global_function.log_oper import *
#flask-login
from flask_login.utils import login_required

#logger = logging.getLogger('flask_engine_log')

customProto_page = Blueprint('customProto_page', __name__, template_folder='templates')

proto_id_map_dict = {
     6: "TCP",
    17: "UDP"
}

MAX_PROTO_NUM = 50
MAX_CONTENT_NUM = 32
MAX_VALUE_NUM = 16


def get_protoName(id):
    if id in proto_id_map_dict:
        return proto_id_map_dict[id]
    return "Unkown"


def get_map_dict(db_proxy, table):
    if table == "model":
        cmd_str = "select distinct value_map_id, value_model_name from value_map_model"
        res, rows = db_proxy.read_db(cmd_str)
        if res == 0:
            return dict(rows)
        else:
            return {}
    if table == "content":
        cmd_str="select content_id, content_name from content_model"
        res, rows=db_proxy.read_db(cmd_str)
        if res == 0:
            return dict(rows)
        else:
            return {}


def change_traffic_table(db, old_name, new_name='unknown'):
    cmd_str = "update icdevicetraffics set trafficName='{}' where trafficName='{}'".format(new_name, old_name)
    cmd_str1 = "update icdevicetrafficstats set trafficName='{}' where trafficName='{}'".format(new_name, old_name)
    db.write_db(cmd_str)
    db.write_db(cmd_str1)


@customProto_page.route('/customProtocol',methods=['GET', 'POST', 'DELETE', 'PUT'])
@login_required
def mw_customProtocol_res():
    db = DbProxy()
    db_proxy = DbProxy(CONFIG_DB_NAME)
    oper_msg = {}
    userip = get_oper_ip_info(request)

    if request.method == 'GET':
        page = request.args.get('page', 0, type=int)
        add_str = ' order by proto_id desc limit ' + str((page - 1) * 10) + ',10'
        info = []
        try:
            cmd_str = "select proto_id,proto_port,proto_type,proto_name,status,content_id,client_type,server_type from self_define_proto_config where proto_id > 500 " + add_str
            res, rows = db_proxy.read_db(cmd_str)
            # rows = new_send_cmd(TYPE_APP_SOCKET, cmd_str, 1)
            if res == 0 and len(rows) == 0:
                return jsonify({'data': [], 'status': 1})
            for row in rows:
                item = {}
                row = list(row)
                item["protoId"] = row[0]
                item["port"] = row[1]
                item["protoType"] = get_protoName(row[2])
                item["protoName"] = row[3]
                item["action"] = row[4]
                item["content_id"] = row[5]
                item["client_type"] = row[6]
                item["server_type"] = row[7]
                current_app.logger.error(item)
                info.append(item)
            cmd_str = "select count(*) from self_define_proto_config where proto_id > 500"
            res, rows = db_proxy.read_db(cmd_str)
            # rows = new_send_cmd(TYPE_APP_SOCKET, cmd_str, 1)
            total = rows[0][0]
            return jsonify({'data': info, 'total': total, 'status': 1})
        except:
            current_app.logger.error(traceback.format_exc())
            return jsonify({'data': [], 'total': 0, 'status': 1})

    elif request.method == 'POST':
        data = request.get_json()
        try:
            loginuser = data.get('loginuser')
            name = data.get('name')
            str_type = data.get('type')
            port = int(data.get('port'))
            content_type = data.get('content_id')
            client_type = data.get('client_type')
            server_type = data.get('server_type')
        except:
            return jsonify({'status': 0, 'msg': '参数错误'})

        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        oper_msg['Operate']="添加自定义协议:" + name + "," + str_type + "," + str(port)
        oper_msg['Result']='1'

        if len(name) == 0 or len(name.encode("utf-8")) > 128:
            return jsonify({'status': 0, 'msg': '自定义协议名称长度大于128字节'})
        if str_type != "TCP" and str_type != "UDP":
            return jsonify({'status': 0, 'msg': '自定义协议为TCP或UDP'})
        if port == 0 or port > 65535:
            return jsonify({'status': 0, 'msg': '端口号为1-65535'})
        type = 0
        if str_type == "TCP":
            type = 6
        elif str_type == "UDP":
            type = 17

        try:
            cmd_str = "select count(*) from self_define_proto_config where and proto_name='{}'".format(name)
            # rows = new_send_cmd(TYPE_APP_SOCKET, cmd_str, 1)
            current_app.logger.info(cmd_str)
            res, rows = db_proxy.read_db(cmd_str)
            if res == 0 and rows[0][0] > 0:
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({'status': 0, 'msg': u'协议名称已存在'})

            cmd_str = "select count(*) from self_define_proto_config where proto_id > 500 and proto_port=%d and proto_type='%d'" % (port, type)
            # rows = new_send_cmd(TYPE_APP_SOCKET, cmd_str, 1)
            res, rows = db_proxy.read_db(cmd_str)
            if res == 0 and rows[0][0] > 0:
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({'status': 0, 'msg': u'存在相同自定义协议'})

            cmd_str = "select count(*) from service_info where service_desc='{}'".format(name)
            res, rows = db_proxy.read_db(cmd_str)
            if res == 0 and rows[0][0] > 0:
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({'status': 0, 'msg': u'存在相同的预定义协议名称'})

            cmd_str = "select count(*) from service_info where service_proto='%s' and service_port=%d" % (str_type, port)
            res, rows = db_proxy.read_db(cmd_str)
            if res == 0 and rows[0][0] > 0:
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({'status': 0, 'msg': u'存在相同的预定义协议'})

            cmd_str = "select count(*) from self_define_proto_config where proto_id > 500"
            res, rows = db_proxy.read_db(cmd_str)
            if res == 0 and rows[0][0] > 50:
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({'status': 0, 'msg': u'自定义协议数量超过上限'})

            cmd_str = "insert into self_define_proto_config (proto_port,proto_type,proto_name,status,content_id,client_type,server_type) values({}, {}, '{}', 0,'{}',{},{})".format(port, type, name, content_type,client_type,server_type)
            # new_send_cmd(TYPE_APP_SOCKET, cmd_str, 2)
            db_proxy.write_db(cmd_str)
            cmd_str = "insert into proto_dev_type (proto_type,client_type,server_type) values('{}', {}, {})".format(name, client_type, server_type)
            db_proxy.write_db(cmd_str)
            oper_msg['Result'] = '0'
            send_log_db(MODULE_OPERATION, oper_msg)
            subprocess.call(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', "dpi modify self_def_proto_model"])
            return jsonify({'status': 1, 'msg': u'添加成功'})
        except:
            current_app.logger.error(traceback.format_exc())
            return jsonify({'status': 0, 'msg': u'添加失败'})

    elif request.method == 'PUT':
        data = request.get_json()
        try:
            loginuser = data.get('loginuser')
            id = int(data.get('id'))
            name = data.get('name')
            str_type = data.get('type')
            port = int(data.get('port'))
            content_id = data.get('content_id')
            client_type = data.get('client_type')
            server_type = data.get('server_type')
        except:
            return jsonify({'status': 0, 'msg': '参数错误'})

        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        oper_msg['Result']='1'

        try:
            cmd_str = "select proto_name,proto_port,proto_type from self_define_proto_config where proto_id = {}".format(id)
            # rows = new_send_cmd(TYPE_APP_SOCKET, cmd_str, 1)
            res, rows = db_proxy.read_db(cmd_str)
            if len(rows) == 0:
                return jsonify({'status': 0, 'msg': '修改失败'})
            old_name = rows[0][0]
            old_port = rows[0][1]
            old_type = get_protoName(rows[0][2])

            if len(name) == 0 or len(name.encode("utf-8")) > 128:
                return jsonify({'status': 0, 'msg': '自定义协议名称长度大于128字节'})
            if str_type != "TCP" and str_type != "UDP":
                return jsonify({'status': 0, 'msg': '自定义协议为TCP或UDP'})
            if port == 0 or port > 65535:
                return jsonify({'status': 0, 'msg': '端口号为1-65535'})
            type = 0
            if str_type == "TCP":
                type = 6
            elif str_type == "UDP":
                type = 17

            cmd_str = "select count(*) from self_define_proto_config where proto_name='{}' and proto_id <> {}".format(name, id)
            # rows = new_send_cmd(TYPE_APP_SOCKET, cmd_str, 1)
            res, rows=db_proxy.read_db(cmd_str)
            if res == 0 and rows[0][0] > 0:
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({'status': 0, 'msg': '存在相同名称'})

            cmd_str = "select count(*) from self_define_proto_config where proto_port=%d and proto_type=%d and proto_id <> %d" % (port, type, id)
            # rows = new_send_cmd(TYPE_APP_SOCKET, cmd_str, 1)
            res, rows=db_proxy.read_db(cmd_str)
            if res == 0 and rows[0][0] > 0:
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({'status': 0, 'msg': '存在相同自定义协议'})

            cmd_str = "select count(*) from service_info where service_desc='{}'".format(name)
            result, rows = db_proxy.read_db(cmd_str)
            if res == 0 and rows[0][0] > 0:
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({'status': 0, 'msg': '存在相同的预定义协议名称'})

            cmd_str = "select count(*) from service_info where service_proto='%s' and service_port=%d" % (str_type, port)
            result, rows = db_proxy.read_db(cmd_str)
            if res == 0 and rows[0][0] > 0:
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({'status': 0, 'msg': '存在相同的预定义协议'})

            cmd_str = "update proto_dev_type set proto_type='{}',client_type={},server_type={} where proto_type = '{}'".format(name, client_type, server_type, old_name)
            db_proxy.write_db(cmd_str)
            cmd_str = "update self_define_proto_config set proto_name='{}',proto_port={},proto_type={}, content_id = '{}',client_type={},server_type={} where proto_id = {}".format(name, port, type, content_id, client_type, server_type, id)
            # new_send_cmd(TYPE_APP_SOCKET, cmd_str, 2)
            db_proxy.write_db(cmd_str)

            # 更新流量表的协议名称
            db = DbProxy()
            change_traffic_table(db, old_name, name)

            oper_msg['Operate'] = "编辑自定义协议:" + old_name + "," + old_type + "," + str(old_port) + "-->" + name + "," + str_type + "," + str(port)
            oper_msg['Result'] = '0'
            send_log_db(MODULE_OPERATION, oper_msg)
            subprocess.call(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', "dpi modify self_def_proto_model"])
            return jsonify({'status': 1, 'msg': '编辑成功'})
        except:
            current_app.logger.error(traceback.format_exc())
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({'status': 0, 'msg': '编辑失败'})

    elif request.method == 'DELETE':
        data = request.get_json()
        loginuser = data.get('loginuser', '')
        ids = data.get('id')
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'

        if len(ids) == 0:
            return jsonify({'status': 0, 'msg': '删除失败'})

        try:
            cmd_str = "select proto_name,proto_port,proto_type,status from self_define_proto_config where proto_id in (%s)" % ids
            # rows = new_send_cmd(TYPE_APP_SOCKET, cmd_str, 1)
            res, rows = db_proxy.read_db(cmd_str)
            if res != 0:
                return jsonify({'status': 0, 'msg': '删除失败'})
            namelist = ""
            send_self_proto_on = 0
            send_self_proto_off = 0
            for row in rows:
                if row[3] == 1:
                    return jsonify({'status': 0, 'msg': '无法删除启用的规则'})
                namelist = namelist + row[0] + "," + get_protoName(row[2]) + "," + str(row[1]) + ';'
                if row[3]:
                    send_self_proto_on = 1
                # 更新历史流量表为网络通用流量
                change_traffic_table(db, row[0])
            namelist = namelist[:-1]

            cmd_str = "select count(*) from self_define_proto_config where proto_id > 500 and status = 1"
            # rows = new_send_cmd(TYPE_APP_SOCKET, cmd_str, 1)
            res, rows = db_proxy.read_db(cmd_str)
            if res == 0 and rows[0][0] == 0:
                send_self_proto_off = 1
                send_self_proto_on = 0
            # 删除设备协议设备类型表proto_dev_type中自定义协议
            cmd_str = "select proto_name from self_define_proto_config where proto_id in (%s)" % ids
            res, rows = db_proxy.read_db(cmd_str)
            proto_namelist = []
            if len(rows) > 0:
                for row in rows:
                    proto_namelist.append(row[0])
                for proto_name in proto_namelist:
                    cmd_str = "delete from proto_dev_type where proto_type ='{}'".format(proto_name)
                    db_proxy.write_db(cmd_str)

            cmd_str = "delete from self_define_proto_config where proto_id > 500 and proto_id in (%s)" % ids
            # new_send_cmd(TYPE_APP_SOCKET, cmd_str, 2)
            db_proxy.write_db(cmd_str)
            if send_self_proto_on == 1:
                subprocess.call(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', "dpi self_def_proto on"])
            elif send_self_proto_off == 1:
                subprocess.call(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', "dpi self_def_proto off"])

            # sel_str = "select proto_name from self_define_proto_config where proto_id in ({})".format(ids)
            # current_app.logger.info(sel_str)
            # _, protos = db_proxy.read_db(sel_str)
            # db = DbProxy()
            # for proto in protos:
            #     change_traffic_table(db, proto[0])

            oper_msg['Operate'] = "删除自定义协议:" + namelist
            oper_msg['Result'] = '0'
            send_log_db(MODULE_OPERATION, oper_msg)
            subprocess.call(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', "dpi modify self_def_proto_model"])
            return jsonify({'status': 1, 'msg': '删除成功'})
        except:
            current_app.logger.error(traceback.format_exc())
            return jsonify({'status': 0, 'msg': '删除失败'})


@customProto_page.route('/contentModel',methods=['GET', 'POST', 'DELETE', 'PUT'])
@login_required
def mw_content_model():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    oper_msg = {}
    userip = get_oper_ip_info(request)

    if request.method == 'GET':
        id_str = "select content_id from self_define_proto_config"
        res, rows = db_proxy.read_db(id_str)
        id_set = []
        if res == 0 and len(rows) > 0:
            for row in rows:
                if row[0] not in id_set:
                    id_set.append(row[0])

        page = request.args.get('page', 0, type=int)
        add_str = ' order by content_id desc limit ' + str((page - 1) * 10) + ',10'
        info = []
        cmd_str = "select content_id,content_name,content_desc,start_offset,depth,content,start_offset2,depth2,content2,start_offset3,depth3,content3,offset_1,length_1," \
                  "audit_name_1,value_map_id_1,bit_offset1,offset_2,length_2,audit_name_2,value_map_id_2,bit_offset2,offset_3,length_3," \
                  "audit_name_3,value_map_id_3,bit_offset3,offset_4,length_4,audit_name_4,value_map_id_4,bit_offset4,offset_5,length_5," \
                  "audit_name_5,value_map_id_5,bit_offset5 from content_model" + add_str
        try:
            res, rows = db_proxy.read_db(cmd_str)
            for row in rows:
                item = {}
                item["content_id"] = row[0]
                if str(row[0]) in id_set:
                    item["is_used"] = 1
                else:
                    item["is_used"] = 0
                item["content_name"] = row[1]
                item["content_desc"] = row[2]
                item["start_offset"] = row[3]
                item["depth"] = row[4]
                item["verify_code"] = row[5]
                item["start_offset2"] = row[6]
                item["depth2"] = row[7]
                item["verify_code2"] = row[8]
                item["start_offset3"] = row[9]
                item["depth3"] = row[10]
                item["verify_code3"] = row[11]
                item["audit_sets"] = []
                for i in range(5):
                    audit_dict = {}
                    j = 12+5*i
                    if row[j+2]:
                        audit_dict["offset"] = row[j]
                        audit_dict["length"] = row[j+1]
                        audit_dict["audit_name"] = row[j+2]
                        audit_dict["value_map_id"] = row[j+3]
                        if -1 < row[j+4] < 16:
                            audit_dict["bit_offset"] = row[j+4]
                        else:
                            audit_dict["bit_offset"] =  ""
                        item["audit_sets"].append(audit_dict)
                info.append(item)
            total_str = "select count(*) from content_model"
            res,rows = db_proxy.read_db(total_str)
            if res == 0:
                total_num = rows[0][0]
            else:
                total_num = 0
            return jsonify({'data': info, 'total': total_num, 'status': 1})
        except:
            current_app.logger.error(traceback.format_exc())
            return jsonify({'data': [], 'total': 0, 'status': 1})

    elif request.method == 'POST':
        data = request.get_json()
        try:
            content_name = data.get("content_name")
            content_desc = data.get("content_desc")
            if len(content_name.encode("utf-8")) > 128:
                return jsonify({"status": 0, "msg": u"名称不能超过128字节"})
            if len(content_desc.encode("utf-8")) > 128:
                return jsonify({"status": 0, "msg": u"描述不能超过128字节"})
            start_offset = int(data.get("start_offset")) if data.get("start_offset") else 0
            depth = int(data.get("depth")) if data.get("depth") else 1500
            start_offset2 = int(data.get("start_offset2")) if data.get("start_offset2") else 0
            depth2 = int(data.get("depth2")) if data.get("depth2") else 1500
            start_offset3 = int(data.get("start_offset3")) if data.get("start_offset3") else 0
            depth3 = int(data.get("depth3")) if data.get("depth3") else 1500
            audit_sets = data.get("audit_sets")
            audit_vaule_num = data.get("verify_code")
            audit_vaule_num2 = data.get("verify_code2")
            audit_vaule_num3 = data.get("verify_code3")
            verify_length = len(audit_vaule_num)/2
            verify_length2 = len(audit_vaule_num2)/2
            verify_length3 = len(audit_vaule_num3)/2
            if verify_length > 64 or verify_length2 > 64 or verify_length3 > 64:
                return jsonify({"status": 0, "msg": u"特征码长度不能超过64字节"})
            loginuser = data.get("loginuser")
            audit_count = len(audit_sets)
            if audit_count > 5:
                return jsonify({"status": 0, "msg": u"参数错误"})
        except:
            current_app.logger.error(traceback.format_exc())
            return jsonify({"status": 0, "msg": u"参数错误"})
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        oper_msg['Operate']="添加自定义协议内容:" + content_name
        oper_msg['Result']='1'
        try:
            if verify_length > depth or verify_length2 > depth2 or verify_length3 > depth3:
                return jsonify({"status": 0, "msg": u"特征码长度不能超过匹配深度"})

            if audit_vaule_num and audit_vaule_num2:
                if audit_vaule_num3:
                    if start_offset3 < (len(audit_vaule_num2) / 2 + start_offset2):
                        return jsonify({"status": 0, "msg": u"下一个起始偏移需要大于前一个特征码长度加起始偏移"})
                elif start_offset2 < (len(audit_vaule_num) / 2 + start_offset):
                    return jsonify({"status": 0, "msg": u"下一个起始偏移需要大于前一个特征码长度加起始偏移"})
            head_length = verify_length + start_offset
            head_length2 = verify_length2 + start_offset2
            head_length3 = verify_length3 + start_offset3
            head_length = max(head_length,head_length2,head_length3)
            if head_length > 1500:
                return jsonify({"status": 0, "msg": u"字段长度超过1500限制"})
            content_length_list = [int(j["offset"]) + int(j["length"]) for j in audit_sets]
            # total_length = int(head_length) + max(content_length_list)
            # 解析值改为绝对偏移值
            total_length = max(content_length_list)
            if total_length > 1500:
                return jsonify({"status": 0, "msg": u"字段长度超过1500限制"})

            verify_code_list = [data["audit_name"] for data in audit_sets]
            verify_code_set = set(verify_code_list)
            if len(verify_code_list) > len(verify_code_set):
                return jsonify({"status": 0, "msg": u"存在重复字段名"})

            name_str = "select audit_name_1,audit_name_2,audit_name_3,audit_name_4,audit_name_5 from content_model"
            res, rows = db_proxy.read_db(name_str)
            name_set = []
            if res == 0 and len(rows) > 0:
                for row in rows:
                    for i in row:
                        if i and i not in name_set:
                            name_set.append(i)
            # current_app.logger.info(name_set)
            for code in verify_code_list:
                if code in name_set:
                    return jsonify({"status": 0, "msg": u"当前字段名存在于其他规则"})

            count_str = "select count(*) from content_model"
            res, rows = db_proxy.read_db(count_str)
            if res == 0 and rows[0][0] > 15:
                return jsonify({"status": 0, "msg": u"规则配置已达16条上限"})

            count_str = "select count(*) from content_model where content_name = '{}'".format(content_name)
            res, rows = db_proxy.read_db(count_str)
            if res == 0 and rows[0][0] > 0:
                return jsonify({"status": 0, "msg": u"规则配置名称已存在"})

            if content_desc:
                count_str = "select count(*) from content_model where content_desc = '{}'".format(content_desc)
                res, rows = db_proxy.read_db(count_str)
                if res == 0 and rows[0][0] > 0:
                    return jsonify({"status": 0, "msg": u"规则配置描述已存在"})

            if audit_vaule_num:
                count_str="select count(*) from content_model where content = '{}'".format(audit_vaule_num)
                res, rows=db_proxy.read_db(count_str)
                if res == 0 and rows[0][0] > 0:
                    return jsonify({"status": 0, "msg": u"特征码已存在"})

            add_title = ""
            value_str = ""
            for i, j in enumerate(audit_sets):
                index = str(i+1)
                if j["bit_offset"] or j["bit_offset"] == 0:
                    # current_app.logger.info('int(j["bit_offset"]) + int(j["length"]) ====  ' + str(int(j["bit_offset"]) + int(j["length"])))
                    if (int(j["bit_offset"]) + int(j["length"])) > 16 or int(j["length"]) == 0:
                        return jsonify({"status": 0, "msg": u"位偏移长度或字段长度不合法"})
                    add_title += "offset_{0}, length_{0}, audit_name_{0}, value_map_id_{0}, bit_offset{0},".format(index)
                    value_map_id = j["value_map_id"] if j["value_map_id"] else 0
                    value_str += "{},{},'{}',{},{},".format(j["offset"], j["length"], j["audit_name"], value_map_id, j["bit_offset"])
                else:
                    add_title+="offset_{0}, length_{0}, audit_name_{0}, value_map_id_{0}, bit_offset{0},".format(index)
                    value_map_id=j["value_map_id"] if j["value_map_id"] else 0
                    value_str+="{},{},'{}',{},-1,".format(j["offset"], j["length"], j["audit_name"], value_map_id)
            add_title = add_title.rstrip(",")
            value_str = value_str.rstrip(",")
            cmd_str = "insert into content_model (content_name,content_desc,start_offset,depth,audit_value_num,content,start_offset2,depth2,content2,start_offset3,depth3,content3,{}) values ('{}','{}',{},{},{},'{}',{},{},'{}',{},{},'{}',{})".format(add_title,content_name,content_desc,start_offset,depth,audit_count,audit_vaule_num,start_offset2,depth2,audit_vaule_num2,start_offset3,depth3,audit_vaule_num3,value_str)
            current_app.logger.info(cmd_str)
            res = db_proxy.write_db(cmd_str)
            if res != 0:
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({"status": 0, "msg": u"添加失败"})
            oper_msg['Result']='0'
            send_log_db(MODULE_OPERATION, oper_msg)
            subprocess.call(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', "dpi modify self_def_proto_model"])
            return jsonify({"status": 1, "msg": u"添加成功"})
        except:
            current_app.logger.error(traceback.format_exc())
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": u"添加失败"})

    elif request.method == 'PUT':
        data = request.get_json()
        try:
            content_id = int(data.get("content_id"))
            content_name = data.get("content_name")
            if len(content_name.encode("utf-8")) > 128:
                return jsonify({"status": 0, "msg": u"名称不能超过128字节"})
            content_desc = data.get("content_desc")
            if len(content_desc.encode("utf-8")) > 128:
                return jsonify({"status": 0, "msg": u"描述不能超过128字节"})
            start_offset = int(data.get("start_offset")) if data.get("start_offset") else 0
            depth = int(data.get("depth")) if data.get("depth") else 1500
            start_offset2 = int(data.get("start_offset2")) if data.get("start_offset2") else 0
            depth2 = int(data.get("depth2")) if data.get("depth2") else 1500
            start_offset3 = int(data.get("start_offset3")) if data.get("start_offset3") else 0
            depth3 = int(data.get("depth3")) if data.get("depth3") else 1500
            audit_vaule_num = data.get("verify_code")
            audit_vaule_num2=data.get("verify_code2")
            audit_vaule_num3=data.get("verify_code3")
            verify_length = len(audit_vaule_num)/2
            verify_length2 = len(audit_vaule_num2)/2
            verify_length3 = len(audit_vaule_num3)/2
            if verify_length > 64 or verify_length2 > 64 or verify_length3 > 64:
                return jsonify({"status": 0, "msg": u"特征码长度不能超过128字节"})
            loginuser = data.get("loginuser")
            audit_sets = data.get("audit_sets")
            audit_count = len(audit_sets)
            if audit_count > 5:
                return jsonify({"status": 0, "msg": u"参数错误"})
        except:
            current_app.logger.error(traceback.format_exc())
            return jsonify({"status": 0, "msg": u"参数错误"})
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        try:
            if verify_length > depth or verify_length2 > depth2 or verify_length3 > depth3:
                return jsonify({"status": 0, "msg": u"特征码长度不能超过匹配深度"})

            head_length = verify_length + start_offset
            head_length2 = verify_length2 + start_offset2
            head_length3 = verify_length3 + start_offset3
            head_length = max(head_length,head_length2,head_length3)
            if head_length > 1500:
                return jsonify({"status": 0, "msg": u"字段长度超过1500限制"})
            content_length_list = [int(j["offset"]) + int(j["length"]) for j in audit_sets]
            # total_length = int(head_length) + max(content_length_list)
            total_length = max(content_length_list)
            if total_length > 1500:
                return jsonify({"status": 0, "msg": u"解析字段长度超过1500限制"})

            verify_code_list = [data["audit_name"] for data in audit_sets]
            verify_code_set = set(verify_code_list)
            if len(verify_code_list) > len(verify_code_set):
                return jsonify({"status": 0, "msg": u"存在重复字段名"})

            name_str = "select audit_name_1,audit_name_2,audit_name_3,audit_name_4,audit_name_5 from content_model where content_id <> {}".format(content_id)
            res, rows = db_proxy.read_db(name_str)
            name_set = []
            if res == 0 and len(rows) > 0:
                for row in rows:
                    for i in row:
                        if i and i not in name_set:
                            name_set.append(i)
            # current_app.logger.info(name_set)
            for code in verify_code_list:
                if code in name_set:
                    return jsonify({"status": 0, "msg": u"当前字段名存在于其他规则"})
            
            cmd_str = "select content_name from content_model where content_id={}".format(content_id)
            res, rows = db_proxy.read_db(cmd_str)
            if res != 0:
                return jsonify({"status": 0, "msg": u"不存在的id"})
            old_name = rows[0][0]
            oper_msg['Operate']="编辑自定义协议内容:" + old_name
            oper_msg['Result']='1'

            # 页面已做限制,被引用的content无法编辑
            # cmd_str="select content_id from self_define_proto_config where content_id like '%{}%'".format(content_id)
            # current_app.logger.error(cmd_str)
            # try:
            #     res, rows=db_proxy.read_db(cmd_str)
            #     id_list=[row[0] for row in rows]
            #     id_str=",".join(id_list)
            #     id_set=id_str.split(",")
            #     if content_id in id_set:
            #         return jsonify({"status": 0, "msg": u"规则配置已被引用"})
            # except:
            #     current_app.logger.error(traceback.format_exc())

            count_str="select count(*) from content_model where content_name = '{}' and content_id <> {}".format(content_name, content_id)
            res, rows=db_proxy.read_db(count_str)
            if res == 0 and rows[0][0] > 0:
                return jsonify({"status": 0, "msg": u"规则配置名称已存在"})

            if content_desc:
                count_str="select count(*) from content_model where content_desc = '{}' and content_id <> {}".format(content_desc, content_id)
                res, rows=db_proxy.read_db(count_str)
                if res == 0 and rows[0][0] > 0:
                    return jsonify({"status": 0, "msg": u"规则配置描述已存在"})

            if audit_vaule_num:
                count_str="select count(*) from content_model where audit_vaule_num = '{}' and content_id <> {}".format(audit_vaule_num, content_id)
                res, rows=db_proxy.read_db(count_str)
                if res == 0 and rows[0][0] > 0:
                    return jsonify({"status": 0, "msg": u"特征码已存在"})

            # delete and add
            del_str = "delete from content_model where content_id={}".format(content_id)
            db_proxy.write_db(del_str)

            add_title = ""
            value_str = ""
            for i, j in enumerate(audit_sets):
                index = str(i+1)

                if j["bit_offset"] or j["bit_offset"] == 0:
                    add_title += "offset_{0}, length_{0}, audit_name_{0}, value_map_id_{0}, bit_offset{0},".format(index)
                    value_map_id = j["value_map_id"] if j["value_map_id"] else 0
                    value_str += "{},{},'{}',{},{},".format(j["offset"], j["length"], j["audit_name"], value_map_id, j["bit_offset"])
                else:
                    add_title+="offset_{0}, length_{0}, audit_name_{0}, value_map_id_{0}, bit_offset{0},".format(index)
                    value_map_id=j["value_map_id"] if j["value_map_id"] else 0
                    value_str+="{},{},'{}',{},-1,".format(j["offset"], j["length"], j["audit_name"], value_map_id)

                # add_title += "offset_{0}, length_{0}, audit_name_{0}, value_map_id_{0},bit_offset{0}".format(index)
                # value_map_id = j["value_map_id"] if j["value_map_id"] else 0
                # value_str += "{},{},'{}',{},'{}',".format(j["offset"], j["length"], j["audit_name"], value_map_id, j["bit_offset"])
            add_title = add_title.rstrip(",")
            value_str = value_str.rstrip(",")
            current_app.logger.info(add_title)
            current_app.logger.info(value_str)
            # cmd_str = "insert into content_model (content_id,content_name,content_desc,start_offset,depth,audit_value_num,content,{}) values ({},'{}','{}',{},{},{},'{}',{})".format(add_title,content_id,content_name,content_desc,start_offset,depth,audit_count,audit_vaule_num,value_str)
            cmd_str = "insert into content_model (content_name,content_desc,start_offset,depth,audit_value_num,content,start_offset2,depth2,content2,start_offset3,depth3,content3,{}) values ('{}','{}',{},{},{},'{}',{},{},'{}',{},{},'{}',{})".format(add_title,content_name,content_desc,start_offset,depth,audit_count,audit_vaule_num,start_offset2,depth2,audit_vaule_num2,start_offset3,depth3,audit_vaule_num3,value_str)

            """
            alter_str = ""
            for i, j in enumerate(audit_sets):
                index = str(i+1)
                alter_str += "offset_{0} = {1}, length_{0} = {2}, audit_name_{0} = '{3}', value_map_id_{0} = {4},".format(index, j["offset"],j["length"],j["audit_name"],j["value_map_id"])
            alter_str = alter_str.rstrip(",")
            cmd_str = "update content_model set content_name='{}',content_desc='{}',start_offset={},depth={},audit_count={},audit_vaule_num='{}',{} where content_id={}".format(content_name, content_desc, start_offset,
                            depth,audit_count,audit_vaule_num, alter_str,content_id)
            """
            current_app.logger.info(cmd_str)
            res=db_proxy.write_db(cmd_str)
            if res != 0:
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({"status": 0, "msg": u"编辑失败"})
            oper_msg['Result']='0'
            send_log_db(MODULE_OPERATION, oper_msg)
            subprocess.call(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', "dpi modify self_def_proto_model"])
            return jsonify({"status": 1, "msg": u"编辑成功"})
        except:
            current_app.logger.error(traceback.format_exc())
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": u"编辑失败"})

    elif request.method == "DELETE":
        data = request.get_json()
        loginuser=data.get("loginuser")
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        try:
            content_id = data.get("content_id")
            # 查询是否在协议中被使用
            content_id_list = content_id.split(",")
            for i in content_id_list:
                cmd_str = "select content_id from self_define_proto_config where content_id like '%{}%'".format(i)
                current_app.logger.error(cmd_str)
                try:
                    res, rows = db_proxy.read_db(cmd_str)
                    id_list = [row[0] for row in rows]
                    id_str = ",".join(id_list)
                    id_set = id_str.split(",")
                    if i in id_set:
                        return jsonify({"status": 0, "msg": u"规则已被引用"})
                except:
                    current_app.logger.error(traceback.format_exc())
            cmd_str = "select content_name from content_model where content_id in ({})".format(content_id)
            res, rows = db_proxy.read_db(cmd_str)
            name_list = [row[0] for row in rows]
            content_name_str = ",".join(name_list)
            oper_msg['Operate'] = "删除自定义协议内容:" + content_name_str
            oper_msg['Result']='1'
            del_str = "delete from content_model where content_id in ({})".format(content_id)
            res = db_proxy.write_db(del_str)
            if res != 0:
                send_log_db(MODULE_OPERATION, oper_msg)
                return jsonify({"status": 0, "msg": u"删除失败"})
            oper_msg['Result']='0'
            send_log_db(MODULE_OPERATION, oper_msg)
            subprocess.call(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', "dpi modify self_def_proto_model"])
            return jsonify({"status": 1, "msg": u"删除成功"})
        except:
            current_app.logger.error(traceback.format_exc())
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": u"删除失败"})


@customProto_page.route('/customValue',methods=['GET', 'POST', 'DELETE', 'PUT'])
@login_required
def mw_content_value():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    oper_msg = {}
    userip = get_oper_ip_info(request)
    if request.method == "GET":
        id_str = "select value_map_id_1,value_map_id_2,value_map_id_3,value_map_id_4,value_map_id_5 from content_model"
        res, rows = db_proxy.read_db(id_str)
        ids_set = []
        if res == 0 and len(rows) > 0:
            for row in rows:
                for i in row:
                    if i and i not in ids_set:
                        ids_set.append(i)

        page = request.args.get('page', 0, type=int)
        add_str = ' order by value_map_id desc limit ' + str((page - 1) * 10) + ',10'
        info = []
        total_str = "select count(distinct value_map_id) from value_map_model"
        res, rows = db_proxy.read_db(total_str)
        if res != 0:
            return jsonify({"status": 0, "msg": u"获取失败"})
        else:
            if len(rows) == 0:
                return jsonify({"status": 1, "data": [], "total": 0, "msg": u"获取成功"})
            else:
                total = rows[0][0]

        cmd_str = "select distinct value_map_id from value_map_model" + add_str
        res, rows = db_proxy.read_db(cmd_str)
        if res != 0:
            return jsonify({"status": 0, "msg": u"获取失败"})

        value_map_id_list = [row[0] for row in rows]
        for map_id in value_map_id_list:
            item_list = []
            model_dict = {}
            cmd_str = "select value_model_name,value_model_desc,audit_value, value_desc from value_map_model where value_map_id={}".format(map_id)
            res, rows = db_proxy.read_db(cmd_str)
            for row in rows:
                item={}
                item["audit_value"] = row[2]
                item["value_desc"] = row[3]
                item_list.append(item)
            model_dict["value_map_name"] = rows[0][0]
            model_dict["value_map_desc"] = rows[0][1]
            model_dict["value_list"] = item_list
            model_dict["value_map_id"] = map_id
            if map_id in ids_set:
                model_dict["is_used"] = 1
            else:
                model_dict["is_used"] = 0
            info.append(model_dict)
        return jsonify({"data": info, "total": total, "status": 1, "msg": u"获取成功"})

    elif request.method == "POST":
        data = request.get_json()
        try:
            value_model_name = data.get("value_map_name")
            if len(value_model_name.encode("utf-8")) > 128:
                return jsonify({"status": 0, "msg": u"名称不能超过128字节"})
            value_model_desc = data.get("value_map_desc")
            if len(value_model_desc.encode("utf-8")) > 64:
                return jsonify({"status": 0, "msg": u"描述不能超过64字节"})
            audit_desc_list = data.get("value_list")
            loginuser = data.get("loginuser")
            if len(audit_desc_list) > 32:
                return jsonify({"status": 0, "msg": u"参数错误"})
        except:
            return jsonify({"status": 0, "msg": u"参数错误"})
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        oper_msg['Operate']="添加自定义解析规则:" + value_model_name
        oper_msg['Result']='1'

        verify_code_list = [data["audit_value"] for data in audit_desc_list]
        verify_code_set = set(verify_code_list)
        if len(verify_code_list) > len(verify_code_set):
            return jsonify({"status": 0, "msg": u"存在重复字段值"})

        name_str = "select audit_value from value_map_model"
        res, rows = db_proxy.read_db(name_str)
        name_set = []
        if res == 0 and len(rows) > 0:
            for row in rows:
                for i in row:
                    if i and i not in name_set:
                        name_set.append(i)
        # current_app.logger.info(verify_code_list)
        # current_app.logger.info(name_set)
        for code in verify_code_list:
            if code in name_set:
                return jsonify({"status": 0, "msg": u"当前字段值存在于其他描述配置"})

        count_str = "select count(distinct value_map_id) from value_map_model"
        res, rows = db_proxy.read_db(count_str)
        if res == 0 and rows[0][0] > 15:
            return jsonify({"status": 0, "msg": u"描述配置已达16条上限"})

        count_str = "select count(*) from value_map_model where value_model_name='{}'".format(value_model_name)
        res, rows = db_proxy.read_db(count_str)
        if res == 0 and rows[0][0] > 0:
            return jsonify({"status": 0, "msg": u"当前描述配置名称已存在"})

        if value_model_desc:
            count_str = "select count(*) from value_map_model where value_model_desc='{}'".format(value_model_desc)
            res, rows = db_proxy.read_db(count_str)
            if res == 0 and rows[0][0] > 0:
                return jsonify({"status": 0, "msg": u"当前描述配置描述已存在"})

        cmd_str = "select max(value_map_id) from value_map_model"
        res, rows = db_proxy.read_db(cmd_str)
        try:
            value_map_id = int(rows[0][0]) + 1
        except:
            value_map_id = 1

        value_model_desc = value_model_desc if value_model_desc else ""
        head_str = "insert into value_map_model(value_map_id,value_model_name,value_model_desc,audit_value,value_desc) values"
        for item in audit_desc_list:
            audit_value = item["audit_value"]
            if len(audit_value.encode("utf-8")) > 128:
                return jsonify({"status": 0, "msg": u"字段值长度不能超过128字节"})
            value_desc = item["value_desc"]
            current_app.logger.info(len(value_desc))
            if len(value_desc.encode("utf-8")) > 64:
                return jsonify({"status": 0, "msg": u"字段值描述不能超过64字节"})
            head_str += "({},'{}','{}','{}','{}'),".format(value_map_id,value_model_name,value_model_desc,audit_value,value_desc)
        cmd_str = head_str.rstrip(",")
        current_app.logger.info(cmd_str)
        res = db_proxy.write_db(cmd_str)
        if res != 0:
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": u"添加失败"})
        oper_msg['Result']='0'
        send_log_db(MODULE_OPERATION, oper_msg)
        return jsonify({"status": 1, "msg": u"添加成功"})

    elif request.method == "PUT":
        data = request.get_json()
        try:
            loginuser = data.get("loginuser")
            value_model_name = data.get("value_map_name")
            if len(value_model_name.encode("utf-8")) > 128:
                return jsonify({"status": 0, "msg": u"名称不能超过128字节"})
            value_map_id = int(data.get("value_map_id"))
            value_model_desc = data.get("value_map_desc")
            if len(value_model_desc.encode("utf-8")) > 128:
                return jsonify({"status": 0, "msg": u"描述不能超过128字节"})
            audit_desc_list = data.get("value_list")
            if len(audit_desc_list) > 32:
                return jsonify({"status": 0, "msg": u"参数错误"})
        except:
            return jsonify({"status": 0, "msg": u"参数错误"})
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        oper_msg['Result']='1'

        verify_code_list = [data["audit_value"] for data in audit_desc_list]
        verify_code_set = set(verify_code_list)
        if len(verify_code_list) > len(verify_code_set):
            return jsonify({"status": 0, "msg": u"存在重复字段值"})

        name_str = "select audit_value from value_map_model where value_map_id<>{}".format(value_map_id)
        res, rows = db_proxy.read_db(name_str)
        name_set = []
        if res == 0 and len(rows) > 0:
            for row in rows:
                for i in row:
                    if i and i not in name_set:
                        name_set.append(i)
        # current_app.logger.info(verify_code_list)
        # current_app.logger.info(name_set)
        for code in verify_code_list:
            if code in name_set:
                return jsonify({"status": 0, "msg": u"当前字段值存在于描述配置"})

        for item in audit_desc_list:
            if len(item["audit_value"].encode("utf-8")) > 128:
                return jsonify({"status": 0, "msg": u"字段值长度不能超过128字节"})
            if len(item["value_desc"].encode("utf-8")) > 64:
                return jsonify({"status": 0, "msg": u"字段值描述不能超过64字节"})

        # 获取旧的名称
        try:
            sea_str = "select value_model_name from value_map_model where value_map_id={}".format(value_map_id)
            res, rows = db_proxy.read_db(sea_str)
            old_value_model_name = rows[0][0]
            oper_msg['Operate'] = "编辑自定义描述配置:" + old_value_model_name
        except:
            current_app.logger.error(traceback.format_exc())
            return jsonify({"status": 0, "msg": u"编辑的id不存在"})

        count_str = "select count(*) from content_model where value_map_id_1={0} or value_map_id_2={0} or value_map_id_3={0} or value_map_id_4={0} or value_map_id_5={0}".format(value_map_id)
        res, rows = db_proxy.read_db(count_str)
        if res == 0 and rows[0][0] > 0:
            return jsonify({"status": 0, "msg": u"当前描述配置已被使用"})

        count_str = "select count(*) from value_map_model where value_model_name='{}' and value_map_id <> {}".format(value_model_name, value_map_id)
        res, rows = db_proxy.read_db(count_str)
        if res == 0 and rows[0][0] > 0:
            return jsonify({"status": 0, "msg": u"当前描述配置名称已存在"})

        if value_model_desc:
            count_str = "select count(*) from value_map_model where value_model_desc='{}' and value_map_id <> {}".format(value_model_desc, value_map_id)
            res, rows = db_proxy.read_db(count_str)
            if res == 0 and rows[0][0] > 0:
                return jsonify({"status": 0, "msg": u"当前描述配置描述已存在"})

        # delete and add
        del_str = "delete from value_map_model where value_map_id={}".format(value_map_id)
        res = db_proxy.write_db(del_str)
        if res != 0:
            return jsonify({"status": 0, "msg": u"编辑失败"})

        value_model_desc = value_model_desc if value_model_desc else ""
        head_str = "insert into value_map_model(value_map_id,value_model_name,value_model_desc,audit_value,value_desc) values"
        for item in audit_desc_list:
            audit_value = item["audit_value"]
            value_desc = item["value_desc"]
            head_str += "({}, '{}','{}','{}','{}'),".format(value_map_id,value_model_name,value_model_desc,audit_value,value_desc)
        cmd_str = head_str.rstrip(",")
        current_app.logger.info(cmd_str)
        res = db_proxy.write_db(cmd_str)
        if res != 0:
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": u"编辑失败"})
        oper_msg['Result']='0'
        send_log_db(MODULE_OPERATION, oper_msg)
        return jsonify({"status": 1, "msg": u"编辑成功"})

    elif request.method == "DELETE":
        data = request.get_json()
        value_map_id = data.get("id")
        loginuser = data.get("loginuser")
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        oper_msg['Result']='1'
        try:
            value_map_id_list = [int(i) for i in value_map_id.split(",")]
        except:
            current_app.logger.error(traceback.format_exc())
            return jsonify({"status": 0, "msg": u"删除失败"})
        # 获取名称记录操作日志
        sea_str = "select distinct value_model_name from value_map_model where value_map_id in ({})".format(value_map_id)
        res, rows = db_proxy.read_db(sea_str)
        old_value_model_name = ",".join([row[0] for row in rows])
        oper_msg['Operate'] = "删除字段值描述配置:" + old_value_model_name
        # 判断是否在content中被使用
        for map_id in value_map_id_list:
            count_str = "select count(*) from content_model where value_map_id_1={0} or value_map_id_2={0} or value_map_id_3={0} or value_map_id_4={0} or value_map_id_5={0}".format(map_id)
            res,rows = db_proxy.read_db(count_str)
            if res == 0  and rows[0][0] > 0:
                return jsonify({"status": 0, "msg": u"当前描述信息已被使用"})
        del_str = "delete from value_map_model where value_map_id in ({})".format(value_map_id)
        res = db_proxy.write_db(del_str)
        if res != 0:
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": u"删除失败"})
        oper_msg['Result']='0'
        send_log_db(MODULE_OPERATION, oper_msg)
        return jsonify({"status": 1, "msg": u"删除成功"})


@customProto_page.route('/getContent',methods=['GET'])
@login_required
def mw_content():
    try:
        db_proxy = DbProxy(CONFIG_DB_NAME)
        content_map = get_map_dict(db_proxy, "content")
        return jsonify({"status": 1, "data": content_map, "msg": u"获取成功"})
    except:
        current_app.logger.error(traceback.format_exc())
        return jsonify({"status": 0, "data": [], "msg": u"获取失败"})


@customProto_page.route('/getValue',methods=['GET'])
@login_required
def mw_value():
    try:
        db_proxy = DbProxy(CONFIG_DB_NAME)
        content_map = get_map_dict(db_proxy, "model")
        return jsonify({"status": 1, "data": content_map, "msg": u"获取成功"})
    except:
        current_app.logger.error(traceback.format_exc())
        return jsonify({"status": 0, "data": [], "msg": u"获取失败"})


@customProto_page.route('/deployCustomProto',methods=['GET', 'POST'])
@login_required
def mw_deployCustomProto():
    db_proxy = DbProxy()
    db_proxy_config = DbProxy(CONFIG_DB_NAME)
    oper_msg = {}
    userip = get_oper_ip_info(request)

    if request.method != 'GET':
        sql_str = "select status from whiteliststudy where id=1"
        try:
            result, rows = db_proxy_config.read_db(sql_str)
            if rows[0][0] == 1:
                return jsonify({'status': 0, 'msg': '学习时不能操作自定义协议'})
        except:
            return jsonify({'status': 0, 'msg': '数据库读取错误'})

    try:
        if request.method == 'GET':
            loginuser = request.args.get('loginuser')
            str_id = request.args.get('id')
            str_action = request.args.get('action')
        elif request.method == 'POST':
            data = request.get_json()
            loginuser = data.get('loginuser', '')
            str_id = data.get('id', '').encode('utf-8')
            str_action = data.get('action', '').encode('utf-8')

        if len(str_id) == 0 or len(str_action) == 0:
            return jsonify({'status': 0, 'msg': '参数错误'})
        action = int(str_action)
        if action:
            action = 1
        else:
            action = 0

        id = int(str_id)
        if id == 0:
            if action:
                oper_msg['Operate'] = "部署所有自定义协议"
            else:
                oper_msg['Operate'] = "取消所有自定义协议"
        else:
            cmd_str = "select proto_name,proto_port,proto_type from self_define_proto_config where proto_id in (%s)" % str_id
            # rows = new_send_cmd(TYPE_APP_SOCKET, cmd_str, 1)
            res, rows=db_proxy_config.read_db(cmd_str)
            if len(rows) == 0:
                return jsonify({'status': 0, 'msg': '数据库读取错误'})
            namelist = ""
            for row in rows:
                namelist = namelist + row[0] + "," + get_protoName(row[2]) + "," + str(row[1]) + ';'
            namelist = namelist[:-1]
            if action:
                oper_msg['Operate'] = "部署自定义协议:" + namelist
            else:
                oper_msg['Operate'] = "取消自定义协议:" + namelist

        if id == 0:
            cmd_str = "update self_define_proto_config set status = %d where proto_id > 500" % action
        else:
            cmd_str = "update self_define_proto_config set status = %d where proto_id > 500 and proto_id in (%s)" % (action, str_id)
        # new_send_cmd(TYPE_APP_SOCKET, cmd_str, 2)
        db_proxy_config.write_db(cmd_str)

        cmd_str = "select count(*) from self_define_proto_config where proto_id > 500 and status = 1"
        # rows = new_send_cmd(TYPE_APP_SOCKET, cmd_str, 1)
        res, rows=db_proxy_config.read_db(cmd_str)
        for row in rows:
            num = row[0]
        if num == 0:
            subprocess.call(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', "dpi self_def_proto off"])
        else:
            subprocess.call(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', "dpi self_def_proto on"])

        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        oper_msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, oper_msg)
        return jsonify({'status': 1})
    except:
        current_app.logger.error(traceback.format_exc())
        return jsonify({'status': 0})


@customProto_page.route('/cusProtoExport', methods=['GET', 'POST'])
@login_required
def customProto_export():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    oper_msg = {}
    oper_msg['Operate'] = "导出自定义协议配置"
    userip = get_oper_ip_info(request)
    loginuser = request.args.get("loginuser")
    file_name = "custom_proto_" + time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(time.time())) + ".json"
    filepath = "/data/download/" + file_name
    json_info = {"self_define_proto": [], "content_model": [], "value_desc": []}
    # content_map = get_map_dict(db_proxy, "content")
    proto_str = "select proto_id,proto_name,proto_port,proto_type,content_id,client_type,server_type from self_define_proto_config where proto_id > 500"
    _, rows = db_proxy.read_db(proto_str)
    if len(rows) > 0:
        for row in rows:
            data = {}
            data["proto_id"] = row[0]
            data["proto_name"] = row[1]
            data["proto_port"] = row[2]
            data["proto_type"] = proto_id_map_dict[row[3]]
            data["content_id"] = row[4]
            data["client_type"] = row[5]
            data["server_type"] = row[6]
            json_info["self_define_proto"].append(data)
    content_str = "select content_id,content_name,content_desc,start_offset,depth,audit_value_num,content," \
                      "start_offset2,depth2,content2,start_offset3,depth3,content3,offset_1,length_1,audit_name_1," \
                      "value_map_id_1,bit_offset1,offset_2,length_2,audit_name_2,value_map_id_2,bit_offset2,offset_3," \
                      "length_3,audit_name_3,value_map_id_3,bit_offset3,offset_4,length_4,audit_name_4,value_map_id_4," \
                      "bit_offset4,offset_5,length_5,audit_name_5,value_map_id_5,bit_offset5 from content_model"
    _, rows = db_proxy.read_db(content_str)
    if len(rows) > 0:
        for row in rows:
            data = {}
            data["content_id"]=row[0]
            data["content_name"]=row[1]
            data["content_desc"]=row[2]
            data["start_offset"]=row[3]
            data["depth"]=row[4]
            data["audit_value_num"]=row[5]
            data["content"]=row[6]
            data["start_offset2"]=row[7]
            data["depth2"]=row[8]
            data["content2"]=row[9]
            data["start_offset3"]=row[10]
            data["depth3"]=row[11]
            data["content3"]=row[12]
            data["offset_1"]=row[13]
            data["length_1"]=row[14]
            data["audit_name_1"]=row[15]
            data["value_map_id_1"]=row[16]
            data["bit_offset1"]=row[17]
            data["offset_2"]=row[18]
            data["length_2"]=row[19]
            data["audit_name_2"]=row[20]
            data["value_map_id_2"]=row[21]
            data["bit_offset2"]=row[22]
            data["offset_3"]=row[23]
            data["length_3"]=row[24]
            data["audit_name_3"]=row[25]
            data["value_map_id_3"]=row[26]
            data["bit_offset3"]=row[27]
            data["offset_4"]=row[28]
            data["length_4"]=row[29]
            data["audit_name_4"]=row[30]
            data["value_map_id_4"]=row[31]
            data["bit_offset4"]=row[32]
            data["offset_5"]=row[33]
            data["length_5"]=row[34]
            data["audit_name_5"]=row[35]
            data["value_map_id_5"]=row[36]
            data["bit_offset5"]=row[37]
            json_info["content_model"].append(data)
    value_str = "select value_id,value_map_id,value_model_name,value_model_desc,audit_value,value_desc from value_map_model"
    _, rows = db_proxy.read_db(value_str)
    if len(rows) > 0:
        for row in rows:
            data = {}
            data["value_id"]=row[0]
            data["value_map_id"]=row[1]
            data["value_model_name"]=row[2]
            data["value_model_desc"]=row[3]
            data["audit_value"]=row[4]
            data["value_desc"]=row[5]
            json_info["value_desc"].append(data)
    try:
        with open(filepath, "w+") as f:
            f.write(json.dumps(json_info))
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        oper_msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, oper_msg)
        return send_from_directory("/data/download/", file_name, as_attachment=True)
    except:
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        oper_msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, oper_msg)
        current_app.logger.error('download %s except' % file_name)
        current_app.logger.error(traceback.format_exc())
        return jsonify({"status": 0, "msg": u"导出失败"})


def overlay_import(filename, db):
    os.chdir(UPLOAD_FOLDER)
    # 1.备份数据表
    proto_backup_str = "mysqldump -ukeystone -pOptValley@4312 keystone_config self_define_proto_config > self_proto.sql"
    content_backup_str = "mysqldump -ukeystone -pOptValley@4312 keystone_config content_model > content.sql"
    value_backup_str = "mysqldump -ukeystone -pOptValley@4312 keystone_config value_map_model > value.sql"
    os.system(proto_backup_str)
    os.system(content_backup_str)
    os.system(value_backup_str)
    cmd_str1 = "truncate self_define_proto_config"
    cmd_str2 = "truncate content_model"
    cmd_str3 = "truncate value_map_model"
    # 2.开始进行数据处理,失败时还原备份数据
    # 2.1 刪除表中原有数据
    # 2.2 读取文件内容并写入
    try:
        with open(filename, "r+") as f:
            json_info = json.load(f)
    except:
        return "文件信息读取失败"
    current_app.logger.info(json_info)
    if json_info["self_define_proto"]:
        db.write_db(cmd_str1)
        name_id_map = {"UDP": 17, "TCP": 6}
        insert_head = "insert into self_define_proto_config (proto_id,proto_name,proto_port,proto_type,content_id,status,client_type,server_type) values {}"
        value_str = ""
        for data in json_info["self_define_proto"][: 50]:
            client_type = data["client_type"] if data["client_type"] else "NULL"
            server_type = data["server_type"] if data["server_type"] else "NULL"
            value_str += "({},'{}',{},{},'{}',0,{},{}),".format(data["proto_id"],data["proto_name"],data["proto_port"],name_id_map[data["proto_type"]],data["content_id"],client_type,server_type)
        insert_str = insert_head.format(value_str.rstrip(","))
        current_app.logger.info(insert_str)
        res = db.write_db(insert_str)
        if res != 0:
            # 执行失败,删除已写入数据并将备份还原
            db.write_db(cmd_str1)
            db.write_db("source /data/rules/self_proto.sql")
            return "导入自定义协议信息失败"

    if json_info["content_model"]:
        db.write_db(cmd_str2)
        insert_head = "insert into content_model (content_id,content_name,content_desc,start_offset,depth,audit_value_num,content," \
                      "start_offset2,depth2,content2,start_offset3,depth3,content3,offset_1,length_1,audit_name_1," \
                      "value_map_id_1,bit_offset1,offset_2,length_2,audit_name_2,value_map_id_2,bit_offset2,offset_3," \
                      "length_3,audit_name_3,value_map_id_3,bit_offset3,offset_4,length_4,audit_name_4,value_map_id_4," \
                      "bit_offset4,offset_5,length_5,audit_name_5,value_map_id_5,bit_offset5) values {}"
        value_str = ""
        for data in json_info["content_model"][: 32]:
            content_id = data["content_id"]
            content_name = data["content_name"]
            content_desc = data["content_desc"]
            start_offset = data["start_offset"]
            depth = data["depth"]
            audit_value_num = data["audit_value_num"]
            content = data["content"]
            start_offset2 = data["start_offset2"]
            depth2 = data["depth2"]
            content2 = data["content2"]
            start_offset3 = data["start_offset3"]
            depth3 = data["depth3"]
            content3 = data["content3"]
            offset_1 = data["offset_1"]
            length_1 = data["length_1"]
            audit_name_1 = data["audit_name_1"]
            value_map_id_1 = data["value_map_id_1"]
            bit_offset1 = data["bit_offset1"]
            if not bit_offset1 and bit_offset1 != 0:
                bit_offset1 = "NULL"
            value_str += "({},'{}','{}',{},{},{},'{}',{},{},'{}',{},{},'{}',{},{},'{}',{},{},".format(content_id,content_name,content_desc,start_offset,depth,audit_value_num,content,start_offset2,depth2,content2,start_offset3,depth3,content3,offset_1,length_1,audit_name_1,value_map_id_1,bit_offset1)
            for i in range(2,6):
                offset = "offset_{}".format(i)
                length = "length_{}".format(i)
                audit_name = "audit_name_{}".format(i)
                value_map_id = "value_map_id_{}".format(i)
                bit_offset = "bit_offset{}".format(i)
                if data[audit_name]:
                    if data[bit_offset] or data[bit_offset] == 0:
                        value_str += "{},{},'{}',{},{},".format(data[offset],data[length],data[audit_name],data[value_map_id],data[bit_offset])
                    else:
                        value_str += "{},{},'{}',{},{},".format(data[offset], data[length], data[audit_name],
                                                               data[value_map_id], -1)
                else:
                    value_str += "{},{},{},{},{},".format('NULL','NULL','NULL','NULL',-1)
            value_str = value_str.rstrip(",") + "),"
        insert_str = insert_head.format(value_str.rstrip(","))
        current_app.logger.info(insert_str)
        res = db.write_db(insert_str)
        if res != 0:
            # 执行失败,删除已写入数据并将备份还原
            db.write_db(cmd_str1)
            db.write_db(cmd_str2)
            db.write_db("source /data/rules/self_proto.sql")
            db.write_db("source /data/rules/content.sql")
            return "导入自定义协议规则失败"

    if json_info["value_desc"]:
        db.write_db(cmd_str3)
        insert_head = "insert into value_map_model (value_id,value_map_id,value_model_name,value_model_desc,audit_value,value_desc) values {}"
        value_str = ""
        for data in json_info["value_desc"]:
            total_str = "select count(distinct value_model_name) from value_map_model"
            _, rows = db.read_db(total_str)
            if rows[0][0] > MAX_VALUE_NUM:
                break
            value_str += "({},{},'{}','{}','{}','{}'),".format(data["value_id"],data["value_map_id"],data["value_model_name"],data["value_model_desc"],data["audit_value"],data["value_desc"])
        insert_str = insert_head.format(value_str.rstrip(","))
        current_app.logger.info(insert_str)
        res = db.write_db(insert_str)
        if res != 0:
            # 执行失败,删除已写入数据并将备份还原
            db.write_db(cmd_str1)
            db.write_db(cmd_str2)
            db.write_db(cmd_str3)
            db.write_db("source /data/rules/self_proto.sql")
            db.write_db("source /data/rules/content.sql")
            db.write_db("source /data/rules/value.sql")
            return "导入自定义协议解析失败"

    # 3.成功时删除备份数据
    if os.path.exists("/data/rules/self_proto.sql"):
        os.system("/data/rules/self_proto.sql")
    if os.path.exists("/data/rules/content.sql"):
        os.system("/data/rules/content.sql")
    if os.path.exists("/data/rules/value.sql"):
        os.system("/data/rules/value.sql")
    return False


def increase_import(filename,db,run=1):
    # 1.记录最大id及已存在数据条数,用于控制总数及添加失败删除新增的数据
    res, rows = db.read_db("select max(proto_id) from self_define_proto_config")
    if rows and rows[0]:
        max_proto_id = rows[0][0]
    else:
        max_proto_id = 0
    res, rows = db.read_db("select count(*) from self_define_proto_config")
    proto_num = rows[0][0]

    res, rows = db.read_db("select max(content_id) from content_model")
    if rows and rows[0]:
        max_content_id = rows[0][0]
    else:
        max_content_id = 0
    res, rows = db.read_db("select count(*) from content_model")
    content_num = rows[0][0]

    res, rows = db.read_db("select max(value_map_id) from value_map_model")
    if rows and rows[0]:
        max_value_id = rows[0][0]
    else:
        max_value_id = 0
    cmd_str1 = "delete from self_define_proto_config where proto_id>{}".format(max_proto_id)
    cmd_str2 = "delete from content_model where content_id>{}".format(max_content_id)
    cmd_str3 = "delete from value_map_model where value_map_id>{}".format(max_value_id)
    # 2.新增数据处理,判断数据是否存在,已经存在的则不进行插入
    try:
        with open(filename, "r+") as f:
            json_info = json.load(f)
    except:
        return "文件信息读取失败"
    current_app.logger.info(json_info)
    if json_info["self_define_proto"]:
        name_id_map = {"UDP": 17, "TCP": 6}
        insert_head = "insert into self_define_proto_config (proto_name,proto_port,proto_type,client_type,server_type,status) values {}"
        value_str = ""
        for data in json_info["self_define_proto"]:
            count_str = "select count(*) from self_define_proto_config where proto_name='{}' or (proto_port={} and proto_type={})".format(data["proto_name"], data["proto_port"], name_id_map[data["proto_type"]])
            _, rows = db.read_db(count_str)
            if rows[0][0] == 0:
                client_type = data["client_type"] if data["client_type"] else "NULL"
                server_type = data["server_type"] if data["server_type"] else "NULL"
                value_str += "('{}',{},{},{},{},0),".format(data["proto_name"], data["proto_port"],name_id_map[data["proto_type"]],client_type,server_type)
                # 在此处进行总量的判断
                proto_num += 1
                if proto_num > MAX_PROTO_NUM:
                    break
        if value_str:
            insert_str = insert_head.format(value_str.rstrip(","))
            current_app.logger.info(insert_str)
            res = db.write_db(insert_str)
            if res != 0:
                db.write_db(cmd_str1)
                return "导入自定义协议信息失败"

    if json_info["content_model"]:
        insert_head = "insert into content_model (content_name,content_desc,start_offset,depth,audit_value_num,content," \
                      "start_offset2,depth2,content2,start_offset3,depth3,content3,offset_1,length_1,audit_name_1," \
                      "value_map_id_1,bit_offset1,offset_2,length_2,audit_name_2,value_map_id_2,bit_offset2,offset_3," \
                      "length_3,audit_name_3,value_map_id_3,bit_offset3,offset_4,length_4,audit_name_4,value_map_id_4," \
                      "bit_offset4,offset_5,length_5,audit_name_5,value_map_id_5,bit_offset5) values {}"
        value_str = ""
        for data in json_info["content_model"]:
            count_str = "select count(*) from content_model where content_name='{}'".format(data["content_name"])
            _, rows = db.read_db(count_str)
            if rows[0][0] == 0:
                content_name = data["content_name"]
                content_desc = data["content_desc"]
                start_offset = data["start_offset"]
                depth = data["depth"]
                audit_value_num = data["audit_value_num"]
                content = data["content"]
                start_offset2 = data["start_offset2"]
                depth2 = data["depth2"]
                content2 = data["content2"]
                start_offset3 = data["start_offset3"]
                depth3 = data["depth3"]
                content3 = data["content3"]
                offset_1 = data["offset_1"]
                length_1 = data["length_1"]
                audit_name_1 = data["audit_name_1"]
                value_map_id_1 = 'NULL'
                bit_offset1 = data["bit_offset1"]
                if not bit_offset1 and bit_offset1 != 0:
                    bit_offset1 = "-1"
                value_str += "('{}','{}',{},{},{},'{}',{},{},'{}',{},{},'{}',{},{},'{}',{},{},".format(content_name,content_desc,start_offset,depth,audit_value_num,content,start_offset2,depth2,content2,start_offset3,depth3,content3,offset_1,length_1,audit_name_1,value_map_id_1,bit_offset1)
                for i in range(2,6):
                    offset = "offset_{}".format(i)
                    length = "length_{}".format(i)
                    audit_name = "audit_name_{}".format(i)
                    bit_offset = "bit_offset{}".format(i)
                    if data[audit_name]:
                        if data[bit_offset] or data[bit_offset] == 0:
                            value_str += "{},{},'{}',{},{},".format(data[offset],data[length],data[audit_name],'NULL',data[bit_offset])
                        else:
                            value_str += "{},{},'{}',{},{},".format(data[offset], data[length], data[audit_name], 'NULL', '-1')
                    else:
                        value_str += "{},{},{},{},{},".format('NULL','NULL','NULL','NULL','-1')
                value_str = value_str.rstrip(",") + "),"
                # 在此处进行总量的判断
                content_num += 1
                if content_num >= MAX_CONTENT_NUM:
                    break
        if value_str:
            insert_str = insert_head.format(value_str.rstrip(","))
            current_app.logger.info(insert_str)
            res = db.write_db(insert_str)
            if res != 0:
                db.write_db(cmd_str1)
                db.write_db(cmd_str2)
                return "导入自定义协议规则失败"

    if json_info["value_desc"]:
        insert_head = "insert into value_map_model (value_map_id,value_model_name,value_model_desc,audit_value,value_desc) values {}"
        value_str=""
        max_id = max_value_id if max_value_id else 0
        for data in json_info["value_desc"]:
            total_str = "select count(distinct value_model_name) from value_map_model"
            _, rows = db.read_db(total_str)
            if rows[0][0] > MAX_VALUE_NUM:
                break
            max_id += 1

            count_str = "select count(*) from value_map_model where value_model_name='{}'".format(data["value_model_name"])
            _, rows = db.read_db(count_str)
            if rows[0][0] == 0:
                value_str += "({},'{}','{}','{}','{}'),".format(max_id, data["value_model_name"], data["value_model_desc"], data["audit_value"], data["value_desc"])
        if value_str:
            insert_str = insert_head.format(value_str.rstrip(","))
            current_app.logger.info(insert_str)
            res = db.write_db(insert_str)
            if res != 0:
                db.write_db(cmd_str1)
                db.write_db(cmd_str2)
                db.write_db(cmd_str3)
                return "导入自定义协议解析失败"
            id_name_str = "select min(value_map_id),value_model_name from value_map_model where value_map_id>{} group by value_model_name".format(max_value_id)
            _, rows = db.read_db(id_name_str)
            for row in rows:
                update_str = "update value_map_model set value_map_id={} where value_model_name='{}'".format(row[0], row[1])
                db.write_db(update_str)
    return False


@customProto_page.route('/cusProtoImport', methods=['GET', 'POST'])
@login_required
def customProto_import():
    oper_msg = {}
    oper_msg['Operate'] = "导入自定义协议配置"
    userip = get_oper_ip_info(request)
    loginuser = request.args.get("loginuser")
    oper_msg['UserName'] = loginuser
    oper_msg['UserIP'] = userip
    oper_msg['ManageStyle'] = 'WEB'
    oper_msg['Result'] = '1'
    config_proxy = DbProxy(CONFIG_DB_NAME)
    # 1.获取上传的文件
    file = request.files["file"]
    import_type = request.form["import_type"]
    # current_app.logger.info(import_type)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
    else:
        return jsonify({"status": 0, "msg": u"上传文件不合法"})
    filepath = UPLOAD_FOLDER + filename
    # 增量导入的处理
    if str(import_type) == "2":
        res = increase_import(filepath, config_proxy)
        if res:
            os.system("rm {}".format(filepath))
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": res})
    # 全局导入的处理
    else:
        res = overlay_import(filepath, config_proxy)
        if res:
            os.system("rm {}".format(filepath))
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": res})
    oper_msg['Result']='0'
    os.system("rm {}".format(filepath))
    send_log_db(MODULE_OPERATION, oper_msg)
    return jsonify({"status": 1, "msg": u"导入成功"})


@customProto_page.route('/exportCustomProto', methods=['GET', 'POST'])
@login_required
def export_customProto():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    oper_msg = {}
    oper_msg['Operate']="导出自定义协议规则"
    userip = get_oper_ip_info(request)
    loginuser = request.args.get("loginuser")
    file_name="custom_proto_" + time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(time.time())) + ".csv"
    # file = codecs.open(file_name, "w+", "utf_8_sig")
    # writer = csv.writer(file)
    # writer.writerow(title_row)
    # file.close()
    cmd_str="select * from self_define_proto_config where proto_id > 500"
    # rows=new_send_cmd(TYPE_APP_SOCKET, cmd_str, 1)
    res, rows = db_proxy.read_db(cmd_str)
    if len(rows) == 0:
        return jsonify({'data': [], 'status': 1})
    content_map = get_map_dict(db_proxy, "content")

    def generate_proto_file():
        try:
            title_row=[u"序号".encode("utf-8-sig"), u"端口".encode("utf-8-sig"), u"协议类型".encode("utf-8-sig"),
                       u"协议名称".encode("utf-8-sig"), u"启用状态".encode("utf-8-sig"), u"审计内容".encode("utf-8-sig")]
            yield ','.join(map(str, title_row)) + '\n'
            for row in rows:
                row=list(row)
                row[2]=get_protoName(row[2])
                if row[5]:
                    cid_list = row[5].split(",")
                    row[5] = " ".join([content_map[i] for i in cid_list])
                yield ','.join(map(str, row)) + '\n'

        except:
            current_app.logger.error(traceback.format_exc())

    try:
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        oper_msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, oper_msg)
        return Response(generate_proto_file(), 200, {'Content-Disposition': 'attachment;filename=' + file_name,
                                                    'Content-Type': 'text/csv; charset=utf-8-sig'})
    except:
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        oper_msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, oper_msg)
        current_app.logger.error('download %s except' % file_name)
        current_app.logger.error(traceback.format_exc())
        return jsonify({"status": 0, "msg": u"导出失败"})


@customProto_page.route('/exportContent', methods=['GET', 'POST'])
@login_required
def export_content():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    oper_msg = {}
    oper_msg['Operate']="导出自定义协议详情"
    userip = get_oper_ip_info(request)
    loginuser = request.args.get("loginuser")
    file_name="custom_content_" + time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(time.time())) + ".csv"
    cmd_str="select content_id,content_name,content_desc,start_offset,depth,audit_value_num,offset_1,length_1," \
                  "audit_name_1,value_map_id_1,offset_2,length_2,audit_name_2,value_map_id_2,offset_3,length_3," \
                  "audit_name_3,value_map_id_3,offset_4,length_4,audit_name_4,value_map_id_4,offset_5,length_5," \
                  "audit_name_5,value_map_id_5 from content_model"
    res, rows = db_proxy.read_db(cmd_str)
    if len(rows) == 0:
        return jsonify({'data': [], 'status': 1})
    value_map = get_map_dict(db_proxy, "model")

    def generate_content_file():
        try:
            title_row=[u"序号".encode("utf-8-sig"), u"名称".encode("utf-8-sig"), u"描述".encode("utf-8-sig"),
                       u"起始偏移".encode("utf-8-sig"), u"解析深度".encode("utf-8-sig"), u"特征码".encode("utf-8-sig"),
                       u"偏移1".encode("utf-8-sig"),u"长度1".encode("utf-8-sig"),u"审计字段1".encode("utf-8-sig"),u"解析模板1".encode("utf-8-sig"),
                       u"偏移2".encode("utf-8-sig"), u"长度2".encode("utf-8-sig"), u"审计字段2".encode("utf-8-sig"),u"解析模板2".encode("utf-8-sig"),
                       u"偏移3".encode("utf-8-sig"), u"长度3".encode("utf-8-sig"), u"审计字段3".encode("utf-8-sig"),u"解析模板3".encode("utf-8-sig"),
                       u"偏移4".encode("utf-8-sig"), u"长度4".encode("utf-8-sig"), u"审计字段4".encode("utf-8-sig"),u"解析模板4".encode("utf-8-sig"),
                       u"偏移5".encode("utf-8-sig"), u"长度5".encode("utf-8-sig"), u"审计字段5".encode("utf-8-sig"),u"解析模板5".encode("utf-8-sig"),]
            yield ','.join(map(str, title_row)) + '\n'
            for row in rows:
                row=list(row)
                for i in range(5):
                    j = 9+4*i
                    if row[j]:
                        row[j] = value_map[row[j]]
                yield ','.join(map(str, row)) + '\n'

        except:
            current_app.logger.error(traceback.format_exc())

    try:
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        oper_msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, oper_msg)
        return Response(generate_content_file(), 200, {'Content-Disposition': 'attachment;filename=' + file_name,
                                                    'Content-Type': 'text/csv; charset=utf-8-sig'})
    except:
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        oper_msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, oper_msg)
        current_app.logger.error('download %s except' % file_name)
        current_app.logger.error(traceback.format_exc())
        return jsonify({"status": 0, "msg": u"导出失败"})


@customProto_page.route('/exportValue', methods=['GET', 'POST'])
@login_required
def export_Value():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    oper_msg = {}
    oper_msg['Operate']="导出解析规则"
    userip = get_oper_ip_info(request)
    loginuser = request.args.get("loginuser")
    file_name="custom_rule_" + time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(time.time())) + ".csv"
    cmd_str="select value_model_name,value_model_desc,audit_value,value_desc from value_map_model"
    res, rows = db_proxy.read_db(cmd_str)
    if len(rows) == 0:
        return jsonify({'data': [], 'status': 1})

    def generate_content_file():
        try:
            title_row = [u"解析规则名称".encode("utf-8-sig"),u"解析规则描述".encode("utf-8-sig"),
                         u"功能码".encode("utf-8-sig"), u"对应功能码解析".encode("utf-8-sig")]
            yield ','.join(map(str, title_row)) + '\n'
            for row in rows:
                row=list(row)
                yield ','.join(map(str, row)) + '\n'

        except:
            current_app.logger.error(traceback.format_exc())

    try:
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        oper_msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, oper_msg)
        return Response(generate_content_file(), 200, {'Content-Disposition': 'attachment;filename=' + file_name,
                                                    'Content-Type': 'text/csv; charset=utf-8-sig'})
    except:
        oper_msg['UserName'] = loginuser
        oper_msg['UserIP'] = userip
        oper_msg['ManageStyle'] = 'WEB'
        oper_msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, oper_msg)
        current_app.logger.error('download %s except' % file_name)
        current_app.logger.error(traceback.format_exc())
        return jsonify({"status": 0, "msg": u"导出失败"})


UPLOAD_FOLDER = "/data/rules/"
ALLOWED_EXTENSIONS = {"json"}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def judge_valid(item, db_proxy, type_im):
    if type_im == "proto":
        cont_list = item.split(",")
        port=cont_list[1]
        proto=cont_list[2]
        proto_name=cont_list[3]
        if proto == "TCP":
            proto_int = 6
        elif proto == "UDP":
            proto_int = 17

        if len(proto_name) == 0 or len(proto_name) > 64:
            return False

        port=int(port)
        if port == 0 or port > 65535:
            return False

        cmd_str="select count(*) from self_define_proto_config where proto_id > 500 and proto_name='%s'" % proto_name
        # rows=new_send_cmd(TYPE_APP_SOCKET, cmd_str, 1)
        res, rows=db_proxy.read_db(cmd_str)
        if rows[0][0] > 0:
            return False

        cmd_str="select count(*) from self_define_proto_config where proto_id > 500 and proto_port=%d and proto_type='%d'" % (port, proto_int)
        # rows=new_send_cmd(TYPE_APP_SOCKET, cmd_str, 1)
        res, rows=db_proxy.read_db(cmd_str)
        if rows[0][0] > 0:
            return False

        cmd_str="select count(*) from service_info where service_desc='%s'" % proto_name
        result, rows=db_proxy.read_db(cmd_str)
        if rows[0][0] > 0:
            return False

        cmd_str="select count(*) from service_info where service_proto='%s' and service_port=%d" % (proto, port)
        result, rows=db_proxy.read_db(cmd_str)
        if rows[0][0] > 0:
            return False
        return True
    elif type_im == "content":
        count_str="select count(*) from content_model"
        res, rows=db_proxy.read_db(count_str)
        if res == 0 and rows[0][0] > 15:
            return False
        cont_list = item.split(",")
        content_name=cont_list[1]
        content_desc=cont_list[2]
        start_offset=cont_list[2]
        depth=cont_list[4]
        audit_vaule_num=cont_list[5]
        offset_1=cont_list[6]
        length_1=cont_list[7]
        audit_name_1=cont_list[8]
        value_map_id_1=cont_list[9]
        offset_2=cont_list[10]
        length_2=cont_list[11]
        audit_name_2=cont_list[12]
        value_map_id_2=cont_list[13]
        offset_3=cont_list[14]
        length_3=cont_list[15]
        audit_name_3=cont_list[16]
        value_map_id_3=cont_list[17]
        offset_4=cont_list[18]
        length_4=cont_list[19]
        audit_name_4=cont_list[20]
        value_map_id_4=cont_list[21]
        offset_5=cont_list[22]
        length_5=cont_list[23]
        audit_name_5=cont_list[24]
        value_map_id_5=cont_list[25]
        count_str="select count(*) from content_model where content_name = '{}'".format(content_name)
        res, rows=db_proxy.read_db(count_str)
        if res == 0 and rows[0][0] > 0:
            return False

        count_str="select count(*) from content_model where content_desc = '{}'".format(content_desc)
        res, rows=db_proxy.read_db(count_str)
        if res == 0 and rows[0][0] > 0:
            return False

        if audit_vaule_num:
            count_str="select count(*) from content_model where audit_vaule_num = '{}'".format(audit_vaule_num)
            res, rows=db_proxy.read_db(count_str)
            if res == 0 and rows[0][0] > 0:
                return False
        return True
    elif type_im == "value":
        pass
    else:
        return False


def insert_sql(item, db_proxy, type_im):
    if type_im == "proto":
        cont_list = item.split(",")
        port=cont_list[1]
        proto=cont_list[2]
        proto_name=cont_list[3]
        status = int(cont_list[4])
        if proto == "TCP":
            proto_int = 6
        elif proto == "UDP":
            proto_int = 17
        cmd_str="insert into self_define_proto_config (port,protoType,proto_name,action) values({}, {}, '{}', {})".format(port, proto_int, proto_name, status)
        current_app.logger.info(cmd_str)
        db_proxy.write_db(cmd_str)
    elif type_im == "content":
        cont_list = item.split(",")
        content_name=cont_list[1]
        content_desc=cont_list[2]
        start_offset=cont_list[2]
        depth=cont_list[4]
        audit_vaule_num=cont_list[5]
        offset_1=cont_list[6]
        length_1=cont_list[7]
        audit_name_1=cont_list[8]
        value_map_id_1=cont_list[9]
        offset_2=cont_list[10]
        length_2=cont_list[11]
        audit_name_2=cont_list[12]
        value_map_id_2=cont_list[13]
        offset_3=cont_list[14]
        length_3=cont_list[15]
        audit_name_3=cont_list[16]
        value_map_id_3=cont_list[17]
        offset_4=cont_list[18]
        length_4=cont_list[19]
        audit_name_4=cont_list[20]
        value_map_id_4=cont_list[21]
        offset_5=cont_list[22]
        length_5=cont_list[23]
        audit_name_5=cont_list[24]
        value_map_id_5=cont_list[25]
        # sql_str = "insert into content_model (content_name,content_desc,start_offset,depth,audit_count,audit_vaule_num,offset_1," \
        #               "length_1,audit_name_1,value_map_id_1,offset_2,length_2,audit_name_2,value_map_id_2,offset_3,length_3," \
        #               "audit_name_3,value_map_id_3,offset_4,length_4,audit_name_4,value_map_id_4,offset_5,length_5," \
        #               "audit_name_5,value_map_id_5) values ('{}','{}',{},{},{},{},{},'{}',{},{},{},'{}',{},{},{},'{}'," \
        #               "{},{},{},'{}',{},{},{},'{}',{},)".format(content_name,content_desc,start_offset,depth,audit_count,audit_vaule_num,
        #                                                         offset_1,length_1,audit_name_1,value_map_id_1,offset_2,
        #                                                         length_2,audit_name_2,value_map_id_2,offset_3,length_3,
        #                                                         audit_name_3,value_map_id_3,offset_4,length_4,audit_name_4,
        #                                                         value_map_id_4,offset_5,length_5,audit_name_5,value_map_id_5)
        # current_app.logger.info(sql_str)
        # db_proxy.write_db(sql_str)
    elif type_im == "value":
        pass


def import_handle(filename, im_type):
    db_proxy = DbProxy(CONFIG_DB_NAME)
    path = UPLOAD_FOLDER + filename
    with open(path, "r+") as f:
        cont = f.readlines()[1:]
        cont_length = len(cont)
        if im_type == "proto":
            count_str = "select count(*) from self_define_proto_config"
            res, rows = db_proxy.read_db(count_str)
            if res == 0 and rows[0][0]+cont_length>50:
                return False
        if im_type == "content":
            count_str = "select count(*) from content_model"
            res, rows = db_proxy.read_db(count_str)
            if res == 0 and rows[0][0]+cont_length>16:
                return False
        if im_type == "value":
            count_str = "select count(distinct value_model_name) from value_map_model"
            res, rows = db_proxy.read_db(count_str)
            if res == 0 and rows[0][0]+cont_length>32:
                return False
        for item in cont:
            item = item.strip("\r\n").rstrip(",")
            current_app.logger.info(item)
            res = judge_valid(item, db_proxy, im_type)
            if res:
                try:
                    insert_sql(item, db_proxy, im_type)
                except:
                    return False
            else:
                return False
    subprocess.call(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', "dpi self_def_proto on"])
    return True


@customProto_page.route('/importCustomProto', methods=['GET', 'POST'])
@login_required
def import_customProto():
    oper_msg = {}
    oper_msg['Operate']="导入自定义协议信息"
    userip = get_oper_ip_info(request)
    loginuser=request.args.get("loginuser")
    oper_msg['UserName']=loginuser
    oper_msg['UserIP']=userip
    oper_msg['ManageStyle']='WEB'
    oper_msg['Result']='1'
    try:
        file = request.files["proto_file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
        else:
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": u"上传文件不合法"})
        if not import_handle(filename, "proto"):
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": u"导入失败"})
        oper_msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, oper_msg)
        return jsonify({"status": 1, "msg": u"导入成功"})
    except:
        send_log_db(MODULE_OPERATION, oper_msg)
        current_app.logger.error(traceback.format_exc())
        return jsonify({"status": 0, "msg": u"导入失败"})


@customProto_page.route('/importContent', methods=['GET', 'POST'])
@login_required
def import_content():
    oper_msg = {}
    oper_msg['Operate']="导入自定义协议内容"
    userip = get_oper_ip_info(request)
    loginuser=request.args.get("loginuser")
    oper_msg['UserName']=loginuser
    oper_msg['UserIP']=userip
    oper_msg['ManageStyle']='WEB'
    oper_msg['Result']='1'
    try:
        file = request.files["content_file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
        else:
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": u"上传文件不合法"})
        if not import_handle(filename, "content"):
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": u"导入失败"})
        oper_msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, oper_msg)
        return jsonify({"status": 1, "msg": u"导入成功"})
    except:
        send_log_db(MODULE_OPERATION, oper_msg)
        current_app.logger.error(traceback.format_exc())
        return jsonify({"status": 0, "msg": u"导入失败"})


@customProto_page.route('/importValue', methods=['GET', 'POST'])
@login_required
def import_Value():
    oper_msg = {}
    oper_msg['Operate']="导入自定义解析规则"
    userip = get_oper_ip_info(request)
    loginuser=request.args.get("loginuser")
    oper_msg['UserName']=loginuser
    oper_msg['UserIP']=userip
    oper_msg['ManageStyle']='WEB'
    oper_msg['Result']='1'
    try:
        file = request.files["value_file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
        else:
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": u"上传文件不合法"})
        if not import_handle(filename, "value"):
            send_log_db(MODULE_OPERATION, oper_msg)
            return jsonify({"status": 0, "msg": u"导入失败"})
        oper_msg['Result'] = '0'
        send_log_db(MODULE_OPERATION, oper_msg)
        return jsonify({"status": 1, "msg": u"导入成功"})
    except:
        send_log_db(MODULE_OPERATION, oper_msg)
        current_app.logger.error(traceback.format_exc())
        return jsonify({"status": 0, "msg": u"导入失败"})

