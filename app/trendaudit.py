#! /usr/bin/env python
# coding=utf-8
from flask import jsonify
from flask import Blueprint
from flask import current_app
from global_function.global_var import *
# flask-login
from flask_login.utils import login_required

trendaudit_page = Blueprint('trendaudit_page', __name__, template_folder='templates')

ISOTIMEFORMAT = '%Y-%m-%d %X'

@trendaudit_page.route('/getallsessionnum')
@login_required
def mw_get_all_sessionnum():
    res_list = []
    status = 1
    db_proxy = DbProxy()
    now_time = int(time.time() - 3780)
    sql_str = "select sessioncount from machinesession where time>%d order by time desc" % (now_time)
    res, rows = db_proxy.read_db(sql_str)
    tmp_start = time.time()
    data_len = len(rows)
    for i in range(0, 720):
        tmp_value = 0
        if i < data_len:
            tmp_value = rows[i][0]
        tmp_time = time.strftime("%H:%M:%S", time.localtime(tmp_start - i * 5))
        tmp_point = (tmp_time, tmp_value)
        res_list.append(tmp_point)
    return jsonify({'status': status, 'rows': res_list})


@trendaudit_page.route('/getonesessionnum')
@login_required
def mw_get_one_sessionnum():
    sql_str = "select sessioncount from machinesession where flag = 1"
    status = 1
    db_proxy = DbProxy()
    res, rows = db_proxy.read_db(sql_str)
    tmp_point = None
    try:
        tmp_value = rows[0][0]
        tmp_time = time.strftime("%H:%M:%S", time.localtime(time.time()))
        tmp_point = (tmp_time, tmp_value)
    except:
        status = 0
        current_app.logger.error("trend audit get one session num error!")
    return jsonify({'status': status, 'rows': tmp_point})
