#!/usr/bin/python
# -*- coding: UTF-8 -*-
import datetime
import tempfile
from flask import Flask
from flask import render_template
from logging.handlers import RotatingFileHandler
from logging.handlers import SysLogHandler

from common import common_helper
from common.daemon import Daemon
from app.login import login_page
from app.systeminfo import index_page
from app.safeevent import safeevent_page
from app.sysevent import sysevent_page
from app.loginlog import loginlog_page
from app.operlog import operlog_page
from app.ipmac import ipmac_page
from app.customProto import customProto_page
from app.blacklist import blacklist_page
from app.whitelist import whitelist_page
from app.deviceinfo import deviceinfo_page
from app.usermanage import usermanage_page
from app.topdev import topdev_page
from app.trafficAudit import trafficAudit_page
from app.protocolAudit import protAudit_page
from app.userguide import userguide_page
from app.trendaudit import trendaudit_page
from app.proto_switch import protoswitch_page
from app.proto_switch import proto_switch_init
from app.flowaudit import flowaudit_page
from app.dbgcollect import dbgcollect_page
from app.sysconfbackup import sysbackup_page
from app.reportgen import reportgen_page
from app.auditstrategy import auditstrategy_page
from app.down_user_manual import down_user_manual_page
from app.macfilter import macfilter_page
from app.ukeyauth import ukeyauth_page
from app.download_pcap import start_pcap_page
from app.license import license_page
from app.assets_locate import assets_locate_page
from app.logaudit import logaudit_page
from app.static_route_config import static_route_config_page
from global_function.log_config import *

#flask-login
# from flask.ext.cors import CORS
from flask_login import login_manager
import ConfigParser

app = Flask(__name__)
# CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.register_blueprint(down_user_manual_page)
app.register_blueprint(login_page)
app.register_blueprint(index_page)
app.register_blueprint(safeevent_page)
app.register_blueprint(sysevent_page)
app.register_blueprint(loginlog_page)
app.register_blueprint(operlog_page)
app.register_blueprint(ipmac_page)
app.register_blueprint(customProto_page)
app.register_blueprint(blacklist_page)
app.register_blueprint(whitelist_page)
app.register_blueprint(deviceinfo_page)
app.register_blueprint(usermanage_page)
app.register_blueprint(ukeyauth_page)
app.register_blueprint(topdev_page)
app.register_blueprint(trafficAudit_page)
app.register_blueprint(protAudit_page)
#app.register_blueprint(userguide_page)
app.register_blueprint(protoswitch_page)
app.register_blueprint(flowaudit_page)
app.register_blueprint(dbgcollect_page)
app.register_blueprint(sysbackup_page)
app.register_blueprint(reportgen_page)
app.register_blueprint(trendaudit_page)
app.register_blueprint(auditstrategy_page)
app.register_blueprint(macfilter_page)
app.register_blueprint(start_pcap_page)
app.register_blueprint(license_page)
app.register_blueprint(assets_locate_page)
app.register_blueprint(static_route_config_page)
app.register_blueprint(logaudit_page)
app.secret_key = 'A0Zr98j/3yX C~XHH!jmOR]LWN/,?RT'
#flask-login
import os

login_manager_ins = login_manager.LoginManager()
login_manager_ins.session_protection = 'strong'
login_manager_ins.init_app(app)

def load_config():
    config_name = '/app/local/share/new_self_manage/app_config.ini'
    if os.path.exists(config_name) == False:
        return False
    app_config = ConfigParser.ConfigParser()
    try:
        app_config.readfp(open(config_name))
        login_dis = app_config.get("APPCONFIG","LOGIN_DISABLED")
        # login_dis="True"
        if login_dis == "False":
            return False
        return True
    except:
        return False

login_manager_ins._login_disabled = load_config()
login_manager_ins.login_view = "login_page.mw_login"

@login_manager_ins.user_loader
def load_user(id):
    if id is None:
        return render_template('/login.html')
    user = User(id)
    return user


class Manage(Daemon):
    def setup_logger(self):
        output_file = '/data/log/flask_engine.log'
        #logger = logging.getLogger('flask_engine_log')
        app.logger.setLevel(GetLogLevelConf())
        # create a rolling file handler
        try:
            handler = RotatingFileHandler(output_file, mode='a',
                                      maxBytes=1024 * 1024 * 10, backupCount=10)
        except:
            handler = SysLogHandler()
        handler.setLevel(GetLogLevelConf())
        handler.setFormatter(logging.Formatter("[%(asctime)s -%(levelname)5s- %(filename)20s:%(lineno)3s]    %(message)s"))
        app.logger.addHandler(handler)
        
    def run(self):
        # global g_sqlite_file_lock
        self.setup_logger()
        # logger = logging.getLogger('flask_engine_log')

        try:
            os.system('mkdir -p /tmp/sock')
            init_socket(TYPE_APP_SOCKET,pid=os.getpid(), time=datetime.datetime.now().strftime("%M%S%f"))
            init_socket(TYPE_EVENT_SOCKET,pid=os.getpid(), time=datetime.datetime.now().strftime("%M%S%f"))
            create_mac_dict()
            # os.remove('/data/sock/flag_machine')
            # os.system('touch %s' % g_sqlite_file_lock)
            # init_sqlite()
            conf_save_flag_unset()
            # proto_switch_init()
            app.logger.info("Start App_main :listen 0.0.0.0, port 4000")
            os.system('mkdir -p /app/tmp')                                         
            tempfile.tempdir = '/app/tmp'
            # for multi pcap to download
            os.system("echo 0 > /tmp/download_multi_pcap_process_count")
            app.logger.info("product name = %s, platform type = %d" % (g_dev_type, g_dpi_plat_type))
            if g_dpi_plat_type == DEV_PLT_X86:
                # app.run('0.0.0.0',port='443',ssl_context=context)
                pass
            else:
                app.run('0.0.0.0',port='4000')
        except:
            app.logger.error(traceback.format_exc())

def main():
    daemon = Manage()
    if g_dpi_plat_type == DEV_PLT_X86:
        daemon.run()
    else:
        app_name = os.path.basename(os.path.realpath(__file__))
        if common_helper.process_already_running(app_name):
            logging.info(app_name + ' is already running. Abort!')
            return
        daemon.start()

main()
