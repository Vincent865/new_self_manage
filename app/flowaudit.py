'''
Flask UI for flow audit
author: HanFei
'''
import sys
sys.path.append("..")
from flask import request
from flask import jsonify
from flask import send_from_directory
from flask import Blueprint
from global_function.global_var import *
#flask-login
from flask_login.utils import login_required


flowaudit_page = Blueprint('flowaudit_page', __name__, template_folder='templates')

@flowaudit_page.route('/flowAuditRes', methods=['GET', 'POST'])
@login_required
def mw_flowaudit_res():
    '''search for flow audit info'''
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        start_time = request.args.get('starttime', "", type=str)
        stop_time = request.args.get('endtime', "", type=str)
        ip_str = request.args.get('ip', "", type=str)
        proto_str = request.args.get('proto', "", type=str)
        keyword = request.args.get('keyword', "", type=str)
    elif request.method == 'POST':
        post_data = request.get_json()
        start_time = post_data['start_time']
        stop_time = post_data['stop_time']
        ip_str = post_data['ip_str']
        proto_str = post_data['proto_str']
        keyword = post_data['keyword']
    option_str = "where 1=1"
    if len(start_time) > 0:
        option_str += " and timestamp >= '%s'" % start_time
    if len(stop_time) > 0:
        option_str += " and timestamp <= '%s'" % stop_time
    if len(ip_str) > 0:
        option_str += " and (srcip like '%%%s%%' or dstip like '%%%s%%')" % (ip_str, ip_str)
    if len(proto_str) > 0:
        option_str += " and (protoname like '%%%s%%')" % proto_str
    if len(keyword) > 0:
        option_str += ''' and (srcmac like '%%%s%%' or dstmac like '%%%s%%'
                      or srcip like '%%%s%%' or dstip like '%%%s%%' or srcport like '%%%s%%'
                      or dstport like '%%%s%%' or protoname like '%%%s%%')''' \
                      % (keyword, keyword, keyword, keyword, keyword, keyword, keyword)
    limit_str = 'limit 10 offset %d'%((page-1)*10)

    sql_str = "select srcip, dstip, srcmac, dstmac, srcport, dstport, \
              timestamp, protoname, filename, sessionid from \
              nsm_flowaudit %s order by timestamp desc %s" \
              % (option_str, limit_str)
    sum_str = "select count(*) from nsm_flowaudit %s"%(option_str)
    total = 0
    flowAuditInfos = []
    db_proxy = DbProxy(CONFIG_DB_NAME)
    res1, flowAuditInfos = db_proxy.read_db(sql_str)
    res2, rows = db_proxy.read_db(sum_str)
    if res1 == 0 and res2 == 0:
        total = rows[0][0]
        return jsonify({'status': 1, 'rows': flowAuditInfos, 'total':total, 'page':page})
    else:
        return jsonify({'status': 0, 'rows': [], 'total':0, 'page':page})


@flowaudit_page.route('/flowAuditGetFTPFileDetail')
@login_required
def mw_flowaudit_get_ftp_file_detail():
    '''Get FTP file name info'''
    session_id = request.args.get('sessionid', "", type=str)
    page = request.args.get('page', 1, type=int)
    limit_str = 'limit 10 offset %d'%((page-1)*10)
    sql_str = 'select filename from nsm_flowftpinfo where \
               sessionid="%s" %s' % (session_id, limit_str)
    sum_str = "select count(sessionid) from nsm_flowaudit where sessionid = %s" % (session_id)
    fileinfo = []
    total = 0
    db_proxy = DbProxy(CONFIG_DB_NAME)
    res1, rows = db_proxy.read_db(sum_str)
    total = rows[0][0]
    res2, sql_res = db_proxy.read_db(sql_str)
    if res1 == 0 and res2 == 0:
        total = rows[0][0]
        for elem in sql_res:
            realfile = elem[0]
            filebase = os.path.basename(realfile)
            time_val = time.localtime(int(filebase.split("_", 1)[0]))
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time_val)
            filename = filebase.split("_", 1)[1]
            fileinfo.append([timestamp, filename, realfile])
        return jsonify({'status': 1, 'filelist':fileinfo, "total":total})
    else:
        return jsonify({'status': 0, 'filelist':[], "total":0})


@flowaudit_page.route('/flowAuditGetFTPCtlDetail')
@login_required
def mw_flowaudit_get_ftp_ctl_detail():
    '''Get FTP control info'''
    session_id = request.args.get('sessionid', "", type=str)
    sql_str = 'select filename from nsm_flowaudit where sessionid="%s"' % (session_id)
    data = ""
    db_proxy = DbProxy(CONFIG_DB_NAME)
    res, sql_res = db_proxy.read_db(sql_str)
    if res == 0:
        filename = "/data/streambuild/" + sql_res[0][0]
        status, data = commands.getstatusoutput("cat %s" % filename)
        if status != 0:
            return jsonify({'status': 0, 'data':""})
        else:
            return jsonify({'status': 1, 'data':data})
    else:
        return jsonify({'status': 0, 'data':""})


@flowaudit_page.route('/flowAuditFileDownload')
@login_required
def mw_flowaudit_get_file_name():
    '''Download for flow audit file'''
    passwd = request.args.get('passwd', "", type=str)
    file_name = request.args.get('file', "", type=str)
    path_str = "/data/streambuild/" + file_name
    if os.path.exists(path_str) == True:
        curdir = "/data/streambuild"
        real_file = file_name
        zipfile_name = curdir + "/" + real_file + ".zip"
        real_zip_file = real_file + ".zip"
        if os.path.exists(zipfile_name) == True:
            os.system("rm -f %s" % zipfile_name)
        if len(passwd) > 0:
            cmd_str = "cd %s && zip -P %s %s %s" % (curdir, passwd, (real_file + ".zip"), real_file)
        else:
            cmd_str = "cd %s && zip %s %s" % (curdir, (real_file + ".zip"), real_file)
        child = subprocess.Popen(cmd_str, shell=True)
        child.wait()
        if os.path.exists(zipfile_name) == True:
            return jsonify({'status': 1, "filename":real_zip_file})
        else:
            return jsonify({'status': 0, "filename":""})
    else:
        return jsonify({'status': 0, "filename":""})


@flowaudit_page.route('/streamdownload/<file_name>')
@login_required
def streamdownload(file_name):
    '''File download action'''
    curdir = "/data/streambuild"
    return send_from_directory(curdir, file_name, as_attachment=True)


@flowaudit_page.route('/flowAuditDeleteAll')
@login_required
def mw_flowaudit_del_all():
    '''Delete all flow audit info'''
    child = subprocess.Popen("cd %s && rm -f *" % ("/data/streambuild"), shell=True)
    child.wait()
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "delete from nsm_flowftpinfo"
    db_proxy.write_db(sql_str)
    sql_str = "delete from nsm_flowaudit"
    db_proxy.write_db(sql_str)
    sql_str = "update nsm_flowfull set fullflag = 0"
    db_proxy.write_db(sql_str)
    return jsonify({'status': 1})


@flowaudit_page.route('/flowAuditGetFullFlag')
@login_required
def mw_flowaudit_get_full_Flag():
    '''Get flow audit full flag info'''
    db_proxy = DbProxy(CONFIG_DB_NAME)
    sql_str = "select fullflag from nsm_flowfull"
    res, sql_res = db_proxy.read_db(sql_str)
    if res == 0:
        return jsonify({'status': 1, "flag":sql_res[0][0]})
    else:
        return jsonify({'status': 0, "flag":0})


