#!/usr/bin/python
# -*- coding: UTF-8 -*-


import traceback
import ipaddress

# 内置模块
from flask import request, jsonify, Blueprint
from flask import current_app

from flask_login.utils import login_required
from global_function.rule_util_oper import *
# 自定义模块
from global_function.global_var import DbProxy, CONFIG_DB_NAME
from global_function import cmdline_oper
from global_function.global_var import get_oper_ip_info
from global_function.log_oper import MODULE_OPERATION, send_log_db
from common.common_static_route import excute_command

static_route_config_page = Blueprint('static_route_config_page', __name__, template_folder='templates')


# status:0:失败 1 成功
# 调用的数据库操作方法返回值：0：成功，1 失败
# 发底层指令：0：成功 其它：失败
# 日志数据库：0：成功 1：失败


# 客户端错误，将错误告诉客户，非客户端错误返回状态码，便于定位错误
# D_IP_MASK_FORMAT_ERROR = 4001  # 目的ip/掩码格式错误
# NEXT_GATEWAY = 4002  # 下一跳格式错误
#
# W_DATABASE = 5001  # 写数据库错误
# R_DATABASE = 5002  # 读数据库错误
# UNKNOWN_ERROR=6001 # 未知错误
# j_msg = {
#     D_IP_MASK_FORMAT_ERROR: '目的ip/掩码格式错误',
#     NEXT_GATEWAY: '下一跳格式错误',
#     W_DATABASE: '写/数据库错误',
#     R_DATABASE: '写/数据库错误'
# }
#
#
# class BaseFlaskErr(Exception):
#     # 默认状态
#     status = 0  # 0 失败
#
#     def __init__(self, return_code, payload=None):
#         super(BaseFlaskErr, self).__init__()
#         self.return_code = return_code
#         self.payload = payload
#
#     # 构建要返回的错误代码和错误信息dict
#     def to_dict(self):
#         rv = dict(self.payload or {})
#         rv['return_code']=self.return_code
#         rv['return_code_msg'] = j_msg[self.return_code]
#
#         # TODO 日志打印
#         return rv
#
#
# @static_route_config_page.app_errorhandler
# def handle_flask_err(error):
#     response = jsonify(error.to_dict())
#     response.status_code = error.status_code
#     return response


@static_route_config_page.route('/routes', methods=['GET', 'POST', 'DELETE', 'PUT'])
@login_required
def static_route_config_operate():
    db = DbProxy(CONFIG_DB_NAME)
    status = 1
    msg = '查询成功'
    total = 0
    data_list = []
    if request.method == 'GET':
        try:
            # 1 获取请求参数
            page = request.args.get('page', 1, type=int)
            # 2 读取数据库
            limit_str = 'limit 10 offset %d' % ((page - 1) * 10)
            list_str = 'select * from tb_static_route_config order by id asc \
                         %s' % limit_str
            sum_str = 'select count(*) from tb_static_route_config'

            res_sum, rows_sum = db.read_db(sum_str)
            res_list, rows_list = db.read_db(list_str)

            # 数据库操作成功
            if res_list == 0 and res_sum == 0:
                total = rows_sum[0][0]
                for row in rows_list:
                    data = {}
                    data['id'] = row[0]
                    data['d_ip_mask'] = row[1]
                    data['next_gateway'] = row[2]
                    data['ip_type'] = row[3]
                    route_status, msg = check_status(row[1], row[2], row[3])
                    if route_status == 0:
                        status = 0
                        return jsonify({'status': status, 'total': total, 'page': page, 'msg': msg})
                    else:

                        data['is_activate'] = True if route_status == 1 else False
                    data_list.append(data)
            else:
                status = 0
                msg = u'读数据库异常'
                current_app.logger.error('when querying the route,the read database failed')
        except:
            status = 0
            msg = u'查询失败'
            current_app.logger.error(traceback.format_exc())

        return jsonify({'status': status, 'total': total, 'page': page, 'msg': msg, 'data': data_list})
    elif request.method == 'POST':
        status = 1
        try:
            # 1 获取请求参数
            post_data = request.get_json()
            d_ip_mask = post_data.get('d_ip_mask', '').strip().encode('utf8')
            next_gateway = post_data.get('next_gateway', '').strip().encode('utf8')
            ip_type = int(post_data.get('iptype'))
            # 2 请求参数格式检查
            ret = check_d_ip_mask(d_ip_mask, ip_type)
            if ret == 1:
                record_log_to_db(request, "1", '新增路由')
                return jsonify({'status': 0, 'msg': '目的ip/掩码格式错误'})
            elif ret == 2:
                record_log_to_db(request, "1", '新增路由')
                return jsonify({'status': 0, 'msg': '禁止配置默认路由（0.0.0.0）'})

            if not cmdline_oper.check_ip_valid(next_gateway):
                record_log_to_db(request, "1", '新增路由')
                return jsonify({'status': 0, 'msg': '下一跳格式错误'})

            if ip_type == 4 and d_ip_mask.find('/') >= 0:
                d_ip_mask = trans_ip_mask(d_ip_mask)
                if d_ip_mask == '':
                    return jsonify({'status': 0, 'msg': '目的ip/掩码格式错误'})
            # we need to switch ipv6 format
            if ip_type == 6:
                src_net6 = ipaddress.ip_network(unicode(d_ip_mask), False)
                d_ip_mask = str(src_net6)
                gw_ipv6 = ipaddress.ip_network(unicode(next_gateway), False)
                next_gateway = str(gw_ipv6).split('/')[0]
            # 3 检查数据库是否已存在该数据
            sql_equql = 'select count(*) from tb_static_route_config where d_ip_mask="{0}" and next_gateway="{1}"'.format(
                d_ip_mask, next_gateway)

            res_count, rows_count = db.read_db(sql_equql)
            # 读数据库失败
            if res_count:
                current_app.logger.error('reading database failed')
                record_log_to_db(request, "1", '新增路由')
                return jsonify({'status': 0, 'msg': u'读数据库失败'})
            else:
                if rows_count[0][0] != 0:
                    record_log_to_db(request, "1", '新增路由')
                    return jsonify({'status': 0, 'msg': u'路由已存在，请不要重复配置'})

            # 4 发新增命令
            if ip_type == 4:
                cmd_str = "vtysh -c 'conf t' -c 'ip route {} {}'".format(d_ip_mask, next_gateway)
            else:
                cmd_str = "vtysh -c 'conf t' -c 'ipv6 route {} {}'".format(d_ip_mask, next_gateway)

            flag_cmd, msg, txt = excute_command(cmd_str)
            if not flag_cmd:
                record_log_to_db(request, "1", '新增路由')
                return jsonify({'status': 0, 'msg': msg})

            # 5 写数据库
            sql_str = 'insert into tb_static_route_config(d_ip_mask,next_gateway, ip_type) VALUES("%s","%s", "%d")' % (
                d_ip_mask, next_gateway, ip_type)

            if db.write_db(sql_str):
                current_app.logger.error('when adding the route,the write database failed')
                record_log_to_db(request, "1", '新增路由')
                return jsonify({'status': 0, 'msg': u'写数据库失败'})
        except:
            status = 0
            current_app.logger.error(traceback.format_exc())
            record_log_to_db(request, "1", '新增路由')
            return jsonify({'status': status, 'msg': u'新增失败'})
        record_log_to_db(request, "0", '新增路由')
        route_status, msg = check_status(d_ip_mask, next_gateway, ip_type)
        if route_status == 0:
            return jsonify({'status': 0, 'msg': msg})  # 0：失败
        else:
            status_result = True if route_status == 1 else False
        return jsonify({'status': status, 'msg': '新增成功', 'is_activate': status_result})
    elif request.method == 'DELETE':
        status = 1
        try:
            # 1 获取请求参数
            id_list = request.get_json().get('id_list', [])
            # 2 判断参数是否有效
            if not id_list:
                record_log_to_db(request, "1", '删除路由')
                return jsonify({'status': 0, 'msg': '未选择任何路由'})
            # 3 遍历id
            for id in id_list:
                # 4、根据id查询完整信息
                # TODO 可优化查询语句，只进行一次读数据库
                sql_str = 'select d_ip_mask, next_gateway, ip_type from tb_static_route_config where id = {}'.format(id)
                flag, res = db.read_db(sql_str)
                if flag == 0:
                    d_ip_mask = res[0][0]
                    next_gateway = res[0][1]
                    ip_type = res[0][2]
                    # 5、发删除指令
                    if ip_type == 4:
                        cmd_str = "vtysh -c 'conf t' -c 'no ip route {0} {1}'".format(d_ip_mask, next_gateway)
                    else:
                        cmd_str = "vtysh -c 'conf t' -c 'no ipv6 route {0} {1}'".format(d_ip_mask, next_gateway)
                    flag_cmd, msg, txt = excute_command(cmd_str)
                    if not flag_cmd:
                        record_log_to_db(request, "1", '删除路由')
                        return jsonify({'status': 0, 'msg': msg})
                    # 6、删除数据库中数据
                    sql_str_del = 'delete from tb_static_route_config where id={}'.format(id)
                    if db.write_db(sql_str_del):
                        current_app.logger.error('when deleting the route,the write database failed')
                        record_log_to_db(request, "1", '删除路由')
                        return jsonify({'status': 0, 'msg': u'写数据库异常'})
                else:
                    current_app.logger.error('when deleting the route,the reade database failed')
                    record_log_to_db(request, "1", '删除路由')
                    return jsonify({'status': 0, 'msg': u'读数据库异常'})
        except:
            status = 0
            current_app.logger.error(traceback.format_exc())
            record_log_to_db(request, "1", '删除路由')
            return jsonify({'status': status, 'msg': u'删除失败'})
        record_log_to_db(request, "0", '删除路由')
        return jsonify({'status': status, 'msg': u'删除成功'})
    elif request.method == 'PUT':
        status = 1
        try:
            # 1、获取请求参数
            id = request.get_json().get('id')
            d_ip_mask = request.get_json().get('d_ip_mask', '').strip().encode('utf8')
            next_gateway = request.get_json().get('next_gateway', '').strip().encode('utf8')
            ip_type = request.get_json().get('iptype')
            # 2、验证请求参数
            ret = check_d_ip_mask(d_ip_mask, ip_type)
            if ret == 1:
                record_log_to_db(request, "1", '编辑路由')
                return jsonify({'status': 0, 'msg': '目的ip/掩码格式错误'})
            elif ret == 2:
                record_log_to_db(request, "1", '编辑路由')
                return jsonify({'status': 0, 'msg': '禁止配置默认路由（0.0.0.0）'})

            if not cmdline_oper.check_ip_valid(next_gateway):
                record_log_to_db(request, "1", '编辑路由')
                return jsonify({'status': 0, 'msg': '下一跳格式错误'})

            if ip_type == 4 and d_ip_mask.find('/') >= 0:
                d_ip_mask = trans_ip_mask(d_ip_mask)
                if d_ip_mask == '':
                    return jsonify({'status': 0, 'msg': '目的ip/掩码格式错误'})
            # we need to switch ipv6 format
            if ip_type == 6:
                src_net6 = ipaddress.ip_network(unicode(d_ip_mask), False)
                d_ip_mask = str(src_net6)
                gw_ipv6 = ipaddress.ip_network(unicode(next_gateway), False)
                next_gateway = str(gw_ipv6).split('/')[0]
            # 3、根据id获取要更新的原有数据
            sql_str = 'select d_ip_mask, next_gateway from tb_static_route_config where id = {}'.format(id)
            flag, res = db.read_db(sql_str)
            if flag == 0 and len(res) == 1:
                d_ip_mask_old = res[0][0]
                next_gateway_old = res[0][1]
                if d_ip_mask == d_ip_mask_old and next_gateway == next_gateway_old:
                    record_log_to_db(request, "0", '编辑路由')  # 0 ：成功
                    route_status, msg = check_status(d_ip_mask, next_gateway, ip_type)
                    if route_status == 0:
                        return jsonify({'status': 0, 'msg': msg})  # 0：失败
                    else:
                        status_result = True if route_status == 1 else False
                    return jsonify({'status': 1, 'msg': '编辑成功', 'is_activate': status_result})

                # 4 数据库查重，请求参数和原有数据对比
                sql_equql = 'select count(*) from tb_static_route_config where d_ip_mask="{0}" and next_gateway="{1}"'.format(
                    d_ip_mask, next_gateway)

                res_count, rows_count = db.read_db(sql_equql)
                if res_count:
                    current_app.logger.error('reading database failed')
                    record_log_to_db(request, "1", '编辑路由')
                    return jsonify({'status': 0, 'msg': u'读数据库失败'})
                else:
                    if rows_count[0][0] != 0:
                        record_log_to_db(request, "1", '编辑路由')
                        return jsonify({'status': 0, 'msg': u'路由已存在，请不要重复配置'})

                # 5、执行指令 删除 添加
                if ip_type == 4:
                    cmd_str_del = "vtysh -c 'conf t' -c 'no ip route {} {}'".format(d_ip_mask_old, next_gateway_old)
                    cmd_str_add = "vtysh -c 'conf t' -c 'ip route {} {}'".format(d_ip_mask, next_gateway)
                else:
                    cmd_str_del = "vtysh -c 'conf t' -c 'no ipv6 route {} {}'".format(d_ip_mask_old, next_gateway_old)
                    cmd_str_add = "vtysh -c 'conf t' -c 'ipv6 route {} {}'".format(d_ip_mask, next_gateway)
                flag_cmd_del, msg, txt = excute_command(cmd_str_del)
                if not flag_cmd_del:
                    record_log_to_db(request, "1", '编辑路由')
                    return jsonify({'status': 0, 'msg': msg})
                flag_cmd_add, msg, txt = excute_command(cmd_str_add)
                if not flag_cmd_add:
                    record_log_to_db(request, "1", '编辑路由')
                    return jsonify({'status': 0, 'msg': msg})

                # 6、更新数据库
                sql_str_update = 'update tb_static_route_config set d_ip_mask="{0}",next_gateway="{1}"  where id={2}'.format(
                    d_ip_mask,
                    next_gateway, id)
                flag = db.write_db(sql_str_update)
                if flag != 0:
                    record_log_to_db(request, "1", '编辑路由')
                    current_app.logger.error('when updating the route,the write database failed')
                    return jsonify({'status': 0, 'msg': u'写数据库异常'})
            else:
                current_app.logger.error('when adding the route,the reade database failed')
                record_log_to_db(request, "1", '编辑路由')
                return jsonify({'status': 0, 'msg': u'读数据库异常'})
        except:
            status = 0
            msg = '路由更新失败'
            current_app.logger.error(traceback.format_exc())
            record_log_to_db(request, "1", '编辑路由')
            return jsonify({'status': status, 'msg': msg})

        record_log_to_db(request, "0", '编辑路由')
        route_status, msg = check_status(d_ip_mask, next_gateway, ip_type)
        if route_status == 0:
            return jsonify({'status': 0, 'msg': msg})
        else:
            status_result = True if route_status == 1 else False
            return jsonify({'status': status, 'msg': '编辑成功', 'is_activate': status_result})
    else:
        pass


def check_d_ip_mask(ip, ip_type):
    '''
    验证ip/掩码格式是否正确
    :param ip:
    :return: 0：成功 1：失败 2 默认路由 禁止配置
    '''
    # 0:成功 1：失败 2：默认路由 禁止配置
    # 目的ip/掩码必须含有"/"
    if ip.find('/') <= 0:
        return 1
    else:
        # 掩码[0,32]
        # 不能配置默认路由 0.0.0.0
        mask_str = ip.split('/')[1]
        ip_str = ip.split('/')[0]
        if ip_str == '0.0.0.0':
            return 2
        try:
            mask = int(mask_str)
        except ValueError as e:
            return 1
        else:
            if cmdline_oper.check_ip_valid(ip) == True:
                return 0
            else:
                return 1

def record_log_to_db(request, status, info):
    post_data = request.get_json()
    loginuser = post_data['loginuser']
    msg = {}
    userip = get_oper_ip_info(request)
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = info
    msg['ManageStyle'] = 'WEB'
    msg['Result'] = status
    send_log_db(MODULE_OPERATION, msg)


def check_status(d_ip_mask, next_gateway, ip_type):
    # TODO 如果发route命令失败 是否应该尝试再次发

    '''
    检查配置的路由是否处于激活状态。路由模式禁止配置默认路由，所以将忽略default
    :param d_ip_mask:
    :param next_gateway:
    :return: 0:失败，1：有效 2：无效
    '''

    sign = 0
    # 计算网络标志
    try:
        ip_face = ipaddress.ip_network(unicode(str(d_ip_mask), 'utf-8'), False)

        if ip_type == 4:
            cmd_str = "route"
            ip_mask = ip_face.exploded.split('/')
        else:
            ip_mask = str(ip_face)
            cmd_str = "route -A inet6"
        flag, msg, txt = excute_command(cmd_str)
        if not flag:
            return sign, '查询路由失败'
        # 解析路由
        t_list = map(lambda x: filter(lambda y: bool(y), x.split(' ')), txt.split('\n'))
        for t in t_list[2:]:
            if ip_type == 4 and t[0] == ip_mask[0] and t[1] == next_gateway and t[2] == str(ip_face.netmask):
                sign = 1
                break
            elif ip_type == 6 and t[0] == ip_mask and t[1] == next_gateway:
                sign = 1
                break
            else:
                sign = 2
    except:
        current_app.logger.error(traceback.format_exc())
        sign = 0
        return sign, "检查路由状态出错"

    return sign, ''
