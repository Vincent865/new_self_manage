#!/usr/bin/python
# -*- coding: UTF-8 -*-
from flask import render_template
from flask import request
from flask import jsonify
from flask import Blueprint
from flask import current_app
from global_function.log_oper import *
#flask-login
from flask_login.utils import login_required

protoswitch_page = Blueprint('protoswitch_page', __name__,template_folder='templates')

PROTO_SWITCH_TUPLE = (
                "modbus",
                "opcda",
                "iec104",
                "dnp3",
                "mms",
                "s7",
                "profinetio",
                "goose",
                "sv",
                "enip",
                "opcua",
                "pnrtdcp",
                "snmp",
                "focas",
                "sip",
                "ftp",
                "telnet",
                "http",
                "pop3",
                "smtp",
                "oracle",
                "sqlserver",
                "s7plus"
)


def proto_switch_init():
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select proto_bit_map from nsm_protoswitch"
    # sql_res = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
    _, sql_res = db_proxy.read_db(sql_str)
    if sql_res is None or sql_res == []:
        vtysh_str = "dpi industry_protocol 4194303"
    else:
        vtysh_str = "dpi industry_protocol %d" % sql_res[0][0]
    return


@protoswitch_page.route('/protoSwitchSet', methods=["GET", "POST"])
@login_required
def mw_protoSwitch_set():
    global PROTO_SWITCH_TUPLE
    switch_states = []
    if request.method == 'GET':
        modbus_states = request.args.get('modbus', 0, type=int)
        opcda_states = request.args.get('opcda', 0, type=int)
        iec104_states = request.args.get('iec104', 0, type=int)
        dnp3_states = request.args.get('dnp3', 0, type=int)
        mms_states = request.args.get('mms', 0, type=int)
        s7_states = request.args.get('s7', 0, type=int)
        profnetio_states = request.args.get('profinetio', 0, type=int)
        goose_states = request.args.get('goose', 0, type=int)
        sv_states = request.args.get('sv', 0, type=int)
        enip_states = request.args.get('enip', 0, type=int)
        opcua_states = request.args.get('opcua', 0, type=int)
        pnrtdcp_states = request.args.get('pnrtdcp', 0, type=int)
        snmp_states = request.args.get('snmp', 0, type=int)
        focas_states = request.args.get('focas', 0, type=int)
        oracle_states = request.args.get('oracle', 0, type=int)
        ftp_states = request.args.get('ftp', 0, type=int)
        telnet_states = request.args.get('telnet', 0, type=int)
        http_states = request.args.get('http', 0, type=int)
        pop3_states = request.args.get('pop3', 0, type=int)
        smtp_states = request.args.get('smtp', 0, type=int)
        sip_states = request.args.get('sip', 0, type=int)
        sqlserver_states = request.args.get('sqlserver', 0, type=int)
        s7plus_states = request.args.get('s7plus', 0, type=int)
        loginuser = request.args.get('loginuser')
    else:
        post_data = request.get_json()
        modbus_states = int(post_data['modbus'])
        opcda_states = int(post_data['opcda'])
        iec104_states = int(post_data['iec104'])
        dnp3_states = int(post_data['dnp3'])
        mms_states = int(post_data['mms'])
        s7_states = int(post_data['s7'])
        profnetio_states = int(post_data['profinetio'])
        goose_states = int(post_data['goose'])
        sv_states = int(post_data['sv'])
        enip_states = int(post_data['enip'])
        opcua_states = int(post_data['opcua'])
        pnrtdcp_states = int(post_data['pnrtdcp'])
        snmp_states = int(post_data['snmp'])
        focas_states = int(post_data['focas'])
        oracle_states = int(post_data['oracle'])
        ftp_states = int(post_data['ftp'])
        telnet_states = int(post_data['telnet'])
        http_states = int(post_data['http'])
        pop3_states = int(post_data['pop3'])
        smtp_states = int(post_data['smtp'])
        sip_states = int(post_data['sip'])
        sqlserver_states = int(post_data['sqlserver'])
        s7plus_states = int(post_data['s7plus'])
        loginuser = post_data['loginuser']

    db_proxy = DbProxy(CONFIG_DB_NAME)
    #fix bug KEYS-388
    if g_dpi_plat_type == DEV_PLT_MIPS:
        oracle_states = 0
        focas_states = 0
    
    switch_states.append(modbus_states)
    switch_states.append(opcda_states)
    switch_states.append(iec104_states)
    switch_states.append(dnp3_states)
    switch_states.append(mms_states)
    switch_states.append(s7_states)
    switch_states.append(profnetio_states)
    switch_states.append(goose_states)
    switch_states.append(sv_states)
    switch_states.append(enip_states)
    switch_states.append(opcua_states)
    switch_states.append(pnrtdcp_states)
    switch_states.append(snmp_states)
    switch_states.append(focas_states)
    switch_states.append(sip_states)
    switch_states.append(ftp_states)
    switch_states.append(telnet_states)
    switch_states.append(http_states)
    switch_states.append(pop3_states)
    switch_states.append(smtp_states)
    switch_states.append(oracle_states)
    switch_states.append(sqlserver_states)
    switch_states.append(s7plus_states)
    #send operation log
    msg={}
    userip = get_oper_ip_info(request)
    
    msg['UserName'] = loginuser
    msg['UserIP'] = userip
    msg['Operate'] = "协议审计开关保存操作".decode("utf8")
    msg['ManageStyle'] = 'WEB'
    

    if( len(switch_states) == 0  or len(switch_states) != len(PROTO_SWITCH_TUPLE)):
        msg['Result'] = '1'
        send_log_db(MODULE_OPERATION, msg)
        jsonify({'status': 0})

    proto_switch_bitmap = 0x007FFFFF
    for i in range(0,len(switch_states)):
        if( switch_states[i] == 0 ):
            tmp_bitmap = 0xFFFFFFFF & (~(1 << i))
            proto_switch_bitmap = proto_switch_bitmap & tmp_bitmap
    vtysh_str = "dpi industry_protocol %d" % proto_switch_bitmap
    process = subprocess.Popen(['vtysh', '-c', 'config t', '-c', 'dpi', '-c', vtysh_str])
    process.wait()
    sql_str = "update nsm_protoswitch set proto_bit_map = %d" % proto_switch_bitmap
    # new_send_cmd(TYPE_APP_SOCKET, sql_str, 2)
    db_proxy.write_db(sql_str)
    conf_save_flag_set()
    msg['Result'] = '0'
    send_log_db(MODULE_OPERATION, msg)
    return jsonify({'status': 1})


@protoswitch_page.route('/protoSwitchRes', methods=["GET", "POST"])
@login_required
def mw_protoSwitch_res():
    global PROTO_SWITCH_TUPLE
    sql_str = "select proto_bit_map from nsm_protoswitch"
    proto_bitmap = 0
    db_proxy = DbProxy(CONFIG_DB_NAME)
    try:
        # sql_res = new_send_cmd(TYPE_APP_SOCKET, sql_str, 1)
        _, sql_res = db_proxy.read_db(sql_str)
        proto_bitmap = sql_res[0][0]
    except:
        current_app.logger.error(traceback.format_exc())
        return jsonify({'status': 0, "switch":{}})
    protoswitch = {}
    for i in range(0, len(PROTO_SWITCH_TUPLE)):
        if g_dpi_plat_type == DEV_PLT_MIPS and (PROTO_SWITCH_TUPLE[i] == "focas" or PROTO_SWITCH_TUPLE[i] == "oracle"):
            continue
        else:
            if( (proto_bitmap & (1<<i)) != 0 ):
                protoswitch[PROTO_SWITCH_TUPLE[i]] = 1
            else:
                protoswitch[PROTO_SWITCH_TUPLE[i]] = 0
    return jsonify({'status': 1, "switch":protoswitch})

