#!/usr/bin/python
# *-* coding:utf-8 *_*

import os
import sys
import traceback
import time
import logging
from flask import render_template, current_app,Blueprint,jsonify


bp_progress = Blueprint('bp_progress', __name__)
logger = logging.getLogger('sql_update_log')
progress = 0


def make_json_data(status, msg, **kwargs):
    json_data = kwargs or {}
    json_data.update({"status": status, "msg": msg})
    return json_data


@bp_progress.route('/progress')
def progressbar():
    from global_function.upgrade_sql import PROGRESS_DICT
    progress = PROGRESS_DICT.get("process", 0)
    logger.info("get_current_progress: "+str(progress))
    return jsonify(make_json_data(1, '', progress=progress))


@bp_progress.route('/')
def page_progressbar():
    return render_template('/login.html')


