#!/usr/bin/python
# -*- coding:UTF-8 -*-
from flask import render_template
from flask import Blueprint
# flask-login
from flask_login.utils import login_required

userguide_page = Blueprint('userguide_page', __name__, template_folder='templates')


@userguide_page.route('/utility/guide/start.html')
@login_required
def userguide_start():
    return render_template('/utility/guide/start.html')


@userguide_page.route('/utility/guide/end.html')
@login_required
def userguide_end():
    return render_template('/utility/guide/end.html')


@userguide_page.route('/utility/guide/step1.html')
@login_required
def userguide_step_one():
    return render_template('/utility/guide/step1.html')


@userguide_page.route('/utility/guide/step2.html')
@login_required
def userguide_step_two():
    return render_template('/utility/guide/step2.html')


@userguide_page.route('/utility/guide/step3.html')
@login_required
def userguide_step_three():
    return render_template('/utility/guide/step3.html')


@userguide_page.route('/utility/guide/step4.html')
@login_required
def userguide_step_four():
    return render_template('/utility/guide/step4.html')


@userguide_page.route('/utility/guide/step5.html')
@login_required
def userguide_step_five():
    return render_template('/utility/guide/step5.html')


@userguide_page.route('/utility/guide/step6.html')
@login_required
def userguide_step_six():
    return render_template('/utility/guide/step6.html')


@userguide_page.route('/utility/guide/step7.html')
@login_required
def userguide_step_seven():
    return render_template('/utility/guide/step7.html')
