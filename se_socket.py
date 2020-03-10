# -*- coding:UTF-8 -*-
import os, sys
import logging
from flask import Flask
from flask_socketio import SocketIO, emit
from common.daemon import Daemon
from common import common_helper
from eventlet.green import threading
from global_function.global_var import DbProxy
from global_function.log_config import GetLogLevelConf
from logging.handlers import RotatingFileHandler
from logging.handlers import SysLogHandler
import json
import socket

# 可设置为eventlet或gevent,默认使用的是eventlet
async_mode = 'eventlet'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
ntp_syn_addr = '/data/sock/ntp_syn_sock'
thread = None
thread1 = None


def safeevent_refresh():
    """Example of how to send server generated events to clients."""
    db = DbProxy()
    while True:
        try:
            sql_str = "select count(*) from incidents"
            res, rows = db.read_db(sql_str)
            if rows:
                total = rows[0][0]
                app.logger.info("old total: " + str(total))
                socketio.sleep(5)
                sql_str = "select count(*) from incidents"
                res, rows = db.read_db(sql_str)
                if rows:
                    total1 = rows[0][0]
                    app.logger.info("sql total: " + str(total1))
                    if int(total) != int(total1):
                        if int(total1) != 0:
                            # diff = int(total1) - int(total)
                            # msg = u"安全事件有更新, 数量" + str(diff) + u"条"
                            msg = {'msg_type': 1, 'data': "new_safeevent"}
                            socketio.emit('data_refresh', msg)
            else:
                app.logger.error("read select count(*) from incidents error.")
        except:
            app.logger.error("safeevent socket error.")


def ntp_sync():
    try:
        if os.path.exists(ntp_syn_addr):
            os.remove(ntp_syn_addr)
    except:
        pass
    ntp_syn_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    ntp_syn_sock.bind(ntp_syn_addr)
    ntp_syn_sock.setblocking(0)
    while True:
        try:
            data, addr = ntp_syn_sock.recvfrom(128)
        except:
            data = None
        if data is not None:
            recv_info = json.loads(data)
            tmp_type = recv_info.get('msg_type', 0)
            if tmp_type == 1:   # ntp同步消息
                with app.app_context():
                    socketio.emit('data_update', recv_info)
        socketio.sleep(5)


@socketio.on('connect')
def test_connect():
    global thread
    global thread1
    if thread is None:
        app.logger.info("socketio safeevent connected!")
        thread = socketio.start_background_task(target=safeevent_refresh)
    if thread1 is None:
        app.logger.info("socketio ntp connected!")
        thread1 = socketio.start_background_task(target=ntp_sync)
    emit('my_response', {'data': 'Connected', 'count': 0})


class webSocketThread(Daemon):
    def setup_logger(self):
        output_file = '/data/log/socketio.log'
        app.logger.setLevel(GetLogLevelConf())
        try:
            handler = RotatingFileHandler(output_file, mode='a',
                                      maxBytes=1024 * 1024 * 10, backupCount=10)
        except:
            handler = SysLogHandler()
        handler.setLevel(GetLogLevelConf())
        handler.setFormatter(logging.Formatter("[%(asctime)s -%(levelname)5s- %(filename)20s:%(lineno)3s]    %(message)s"))
        app.logger.addHandler(handler)

    def run(self):
        try:
            self.setup_logger()
            # t = threading.Thread(target=data_worker, name='dataworker')
            # t.setDaemon(True)
            # t.start()
            app.logger.info('before se_socket start')
            socketio.run(app, host='0.0.0.0', port=9002)
            app.logger.info('se_socket start success!')
        except:
            app.logger.error('se_socket start error!')
            sys.exit()


if __name__ == '__main__':
    daemon = webSocketThread()
    app_name = os.path.basename(os.path.realpath(__file__))
    if common_helper.process_already_running(app_name):
        print(app_name + ' is already running. Abort!')
    else:
        daemon.start()
