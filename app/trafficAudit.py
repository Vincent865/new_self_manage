#! /usr/bin/env python
#coding=utf-8
from flask import request
from flask import jsonify
from flask import Blueprint
from flask import current_app
from global_function.log_oper import *
#flask-login
from flask_login.utils import login_required
import traceback

sys.path.append(os.path.abspath(__file__).split('app')[0])

from global_function.global_var import *
from global_function.traffic_audit import ipTraffic


trafficAudit_page = Blueprint('trafficAudit_page', __name__,template_folder='templates')


@trafficAudit_page.route('/getCurTimeTraffic')
@login_required
def getCurTimeTraffic():
    db_proxy = DbProxy()
    res,rows = db_proxy.read_db("select timestamp, sendSpeed from safedevpoint order by timestamp desc limit 180")
    rows = list(rows)
    rows.reverse()
    if len(rows) == 0:
        bytes = []
        timePoints = []
        for i in range(0,180):
            bytes.append(0)
            tmp_time = time.strftime('%H:%M:%S', time.localtime(time.time() - i*20))
            timePoints.append(tmp_time)
            return jsonify({'points': bytes, 'timePoints': timePoints})
    timePoints = [row[0].split(' ')[1] for row in rows]
    bytes = [row[1] for row in rows]
    return jsonify({'points': bytes, 'timePoints': timePoints})


@trafficAudit_page.route('/getCurTimeTrafficLatestPoint')
@login_required
def getCurTimeTrafficLatestPoint():
    db_proxy = DbProxy()
    sql = "select timestamp, sendSpeed from safedevpoint order by id desc limit 1"
    res,rows = db_proxy.read_db(sql)
    if len(rows) == 0:
        tmp_time = time.strftime('%H:%M:%S', time.localtime(time.time()))
        return jsonify({'point': 0, 'timePoint': tmp_time})
    return jsonify({'point':rows[0][1],'timePoint':rows[0][0].split(' ')[1]})


def get_traffic_percent_1h(sorted_rows, ipmatch="", macmatch=""):
    db_proxy = DbProxy()
    # sorted_dev_traffic_1h: id | devid | ip | mac | sendSpeed | recvSpeed | totalBytes | timestamp
    matchrule = " where 1=1"
    selCmd = "select count(*), cast(sum(totalBytes) as UNSIGNED) from sorted_dev_traffic_1h"
    if ipmatch != "":
        matchrule += " and ip like '%%%s%%'"%(ipmatch)
    if macmatch != "":
        matchrule += " and mac like '%%%s%%'"%(macmatch)
    selCmd = selCmd + matchrule
    result, rows = db_proxy.read_db(selCmd)
    if result !=0 or len(rows) == 0:
        return jsonify({'rows': rows,'total':0,'page':1})
    count = rows[0][0]
    totalBytes = rows[0][1]
    values = []
    for row in sorted_rows:
        ip = row[2]
        if ip == "NULL":
            ip = ""
        deviceName = get_devname_by_ipmac(ip, row[3])
        devPer = round(float(row[6]) / totalBytes, 4)
        # 返回值顺序 ip,mac,send,recv,ts,name,per
        row_tmp = [ip, row[3], row[4], row[5], row[7], deviceName, devPer, row[1]]
        values.append(row_tmp)
    return values, count


@trafficAudit_page.route('/getDevTrafficPercent')
@login_required
def getDevTrafficPercent():
    delta = request.args.get('timeDelta', 0, type=int)
    db_proxy = DbProxy()

    if delta == 1:
        selCmd = "select * from sorted_dev_traffic_1h limit 5"
        result, sorted_rows = db_proxy.read_db(selCmd)
        if result != 0 or len(sorted_rows) == 0:
            return jsonify({'rows': []})
        # 返回值顺序 ip,mac,send,recv,ts,name,per,devid
        values, count = get_traffic_percent_1h(sorted_rows)
        current_app.logger.info(str(values))
        rows = []
        five_per = 0
        for val in values:
            rows.append([val[5], val[6]])
            five_per += val[6]
        current_app.logger.info(rows)
    else:
        if delta == 0:
            # | id | devid | ip | mac | sendBytes | recvBytes | totalBytes | timestamp |
            sel_cmd = "select devid, ip, mac, cast(sum(totalBytes) as UNSIGNED) from dev_his_traffic group by devid"
        else:
            nowtime = datetime.datetime.now()
            nowtimeNyr = nowtime.strftime("%Y-%m-%d %H:%M:%S")
            preTime = nowtime + datetime.timedelta(hours=-delta, seconds=-1)
            preTimeNyr = preTime.strftime("%Y-%m-%d %H:%M:%S")
            db_proxy = DbProxy()
            sel_cmd = "select devid, ip, mac, cast(sum(totalBytes) as UNSIGNED) from dev_his_traffic where timestamp" \
                      " > '%s' and timestamp < '%s' group by devid" % (preTimeNyr, nowtimeNyr)
        current_app.logger.info(sel_cmd)
        result, rows = db_proxy.read_db(sel_cmd)
        if result !=0 or len(rows) == 0:
            return jsonify({'rows': []})
        sorted_rows = sorted(rows, key=lambda x : x[3], reverse=True)
        current_app.logger.info(sorted_rows)
        totalBytes = 0
        rows = []
        for row in sorted_rows:
            totalBytes += row[3]
        current_app.logger.info(totalBytes)
        sorted_rows = sorted_rows[0:5]
        five_per = 0
        for row in sorted_rows:
            ip = row[1]
            if ip == "NULL":
                ip = ""
            # deviceName = get_device_name(ip, row[2])
            deviceName = get_devname_by_ipmac(ip, row[2])
            dev_per = round(float(row[3]) / totalBytes, 4)
            five_per += dev_per
            row_tmp = [deviceName, dev_per]
            rows.append(row_tmp)
    otherPer = 1.0 - five_per
    if otherPer > 0.0000999 and len(rows) == 5:
        rows.append([u'其他', otherPer])
    return jsonify({'rows': rows})


def deal_top_device_name(rows):
    db_proxy = DbProxy()
    for i, row in enumerate(rows):
        result, ipmac = db_proxy.read_db("select iCDeviceIp,iCDeviceMac from icdevicetrafficstats where iCDeviceId='%s'"%row[0])
        mac = ipmac[0][1]
        ip = ipmac[0][0]
        if ip == "NULL":
            ip = ""
        rows[i][0] = get_devname_by_ipmac(ip, mac)
    return rows


def get_device_name(ip, mac):
    db_proxy = DbProxy()
    result, dev_name = db_proxy.read_db("select name from topdevice where ip='%s' and mac='%s'"%(ip, mac))
    if len(dev_name) == 0:
        deviceName = get_name_by_mac(mac)
        if deviceName[0:4] == 'dev-' and ip != "":
            deviceName = 'dev-'+ip
    else:
        deviceName = dev_name[0][0]
    return deviceName


@trafficAudit_page.route('/getProtTrafficPercent')
@login_required
def getProtTrafficPercent():
    timeDelta = request.args.get('timeDelta', 0, type=int)
    nowtime = datetime.datetime.now()
    nowtimeNyr = nowtime.strftime("%Y-%m-%d %H:%M:%S")
    preTime = nowtime + datetime.timedelta(hours=-timeDelta)
    preTimeNyr = preTime.strftime("%Y-%m-%d %H:%M:%S")
    selCmd = "select distinct trafficName from icdevicetrafficstats where timestamp >= '%s' and timestamp < '%s'"%(preTimeNyr, nowtimeNyr)
    protDict = {}
    db_proxy = DbProxy()
    try:
        result,allProts = db_proxy.read_db(selCmd)
        selCmd = "select cast(sum(totalBytes) as UNSIGNED)  from icdevicetrafficstats where \
        timestamp >= '%s' and timestamp < '%s'"%(preTimeNyr, nowtimeNyr)
        for prot in allProts:
            sumCmd = selCmd + " and trafficName = '%s'"%(prot[0])
            result,protBytes = db_proxy.read_db(sumCmd)
            protBytes = protBytes[0][0]
            if protBytes == None:
                protBytes = 0
            protDict['%s'%prot[0]] =  protBytes
    except:
        current_app.logger.error(traceback.format_exc())
    if 'unknown' in protDict:
        if 'tradition_pro' in protDict:
            protDict['tradition_pro'] += protDict['unknown']
        else:
            protDict['tradition_pro'] = protDict['unknown']
        del protDict['unknown']
    sortedProtList = sorted(protDict.iteritems(), key=lambda x : x[1], reverse=True)
    allBytes = 0
    for i in range(len(sortedProtList)):
        allBytes += sortedProtList[i][1]
    rows = []
    if allBytes == 0:
        return jsonify({'rows':rows})
    fiveProtPer = 0.0
    for i in range(len(sortedProtList)):
        if i < 5:
            protPerc = round(float(sortedProtList[i][1])/allBytes,4)
            if protPerc > 0.0000999:
                if sortedProtList[i][0] == 'tradition_pro':
                    sortedProtList[i] = list(sortedProtList[i])
                    sortedProtList[i][0] = u"通用网络协议"
                fiveProtPer += protPerc
                rows.append(('%s'%sortedProtList[i][0],protPerc))
        else:
            break
    otherPer = 1.0 - fiveProtPer
    if otherPer > 0.0000999:
        rows.append((u'其他', otherPer))
    return jsonify({'rows': rows})

    
@trafficAudit_page.route('/getDevTrafficTable')
@login_required
def getDevTrafficTable():
    page = request.args.get('page', 0, type=int)
    devname = request.args.get('devName')
    ip = request.args.get('devIp')
    mac = request.args.get('devMac')
    db_proxy = DbProxy()
    options_str = "where 1=1"
    if ip != "":
        options_str += " and ip like '%%%s%%'"%(ip)
    if mac != "":
        options_str += " and mac like '%%%s%%'"%(mac)
    #  id | devid | ip | mac | sendSpeed | recvSpeed | totalBytes | timestamp
    offset = (page-1) * 4
    first = (page-1)*4 + 1
    end = (page-1)*4+4
    indx = 0
    dev_rows = []
    if devname == "":
        selCmd = "select * from sorted_dev_traffic_1h %s limit 4 offset %s" % (options_str,offset)
        result, sorted_rows = db_proxy.read_db(selCmd)
        if result != 0 or len(sorted_rows) == 0:
            return jsonify({'rows': [], 'total': 0, 'page': 1})
        values, count = get_traffic_percent_1h(sorted_rows, ipmatch=ip, macmatch=mac)
        return jsonify({'rows': values, 'total': count, 'page': page})
    else:
        selCmd = "select * from sorted_dev_traffic_1h %s"%(options_str)
        result, sorted_rows = db_proxy.read_db(selCmd)
        if result !=0 or len(sorted_rows) == 0:
            return jsonify({'rows': [],'total':0,'page':1})
        for row in sorted_rows:
            name = get_devname_by_ipmac(row[2], row[3])
            if (name == "") or (len(name) < len(devname)):
                continue
            elif (name.upper().find(devname.upper()) != -1):
                indx += 1
                if (int(indx) >= int(first)) and (int(indx) <= int(end)):
                    dev_rows.append(row)
                # if int(indx) >= int(end):
                #     break
            else:
                continue
        values, count= get_traffic_percent_1h(dev_rows)
        return jsonify({'rows': values, 'total': indx, 'page': page})


@trafficAudit_page.route('/getDevDetailTraffic')
@login_required
def getDevDetailTraffic():
    mac = request.args.get('mac')
    nowtime = datetime.datetime.now() + datetime.timedelta(hours=-1)
    nowtimeNyr = nowtime.strftime("%Y-%m-%d %H:%M:%S")
    points = []
    timePoints = []
    db_proxy = DbProxy()
    for i in range(180):
        laterTime = nowtime + datetime.timedelta(seconds=20*(i+1))
        timePoints.append(nowtimeNyr.split(' ')[1])
        laterTimeNyr = laterTime.strftime("%Y-%m-%d %H:%M:%S")
        selCmd = "select cast(sum(sendSpeed) as UNSIGNED),cast(sum(recvSpeed) as UNSIGNED) from icdevicetraffics where iCDeviceMac = '%s' \
        and timestamp >= '%s' and timestamp < '%s' and trafficName = 'equipment'"%(mac,nowtimeNyr,laterTimeNyr)

        nowtimeNyr = laterTimeNyr
        try:
            #avgBytes = audit_send_read_cmd(TYPE_AUDIT_APP_SOCKET,selCmd)
            result,avgBytes = db_proxy.read_db(selCmd)
            avgBytes = avgBytes[0]
            avgBytes = list(avgBytes)
            if avgBytes[0] == None:
                avgBytes[0] = 0
            if avgBytes[1] == None:
                avgBytes[1] = 0
            
            totalBytes = avgBytes[0] + avgBytes[1]
            #totalBytes/4.0/1024.0*8.0
            totalBytes = round((totalBytes/512.0),1)
            points.append(totalBytes)
        except:
            current_app.logger.error(traceback.format_exc())
    return jsonify({'points':points,'timePoints':timePoints})


@trafficAudit_page.route('/getDevDetailTrafficLatestPoint')
@login_required
def getDevDetailTrafficLatestPoint():
    mac = request.args.get('mac')
    nowtime = datetime.datetime.now()
    nowtimeNyr = nowtime.strftime("%Y-%m-%d %H:%M:%S")
    point = 0
    db_proxy = DbProxy()
    preTime = nowtime + datetime.timedelta(seconds=-20)
    preTimeNyr = preTime.strftime("%Y-%m-%d %H:%M:%S")
    timePoint = preTimeNyr.split(' ')[1]
    selCmd = "select cast(sum(sendSpeed) as UNSIGNED),cast(sum(recvSpeed) as UNSIGNED) from icdevicetraffics " \
             "where iCDeviceMac = '%s' and timestamp >= '%s' and timestamp < '%s' " \
             "and trafficName = 'equipment'" % (mac, preTimeNyr, nowtimeNyr)
    try:
        #avgBytes = audit_send_read_cmd(TYPE_AUDIT_APP_SOCKET,selCmd)
        result,avgBytes = db_proxy.read_db(selCmd)
        avgBytes = avgBytes[0]
        if avgBytes[0] == None:
            avgBytes[0] = 0
        if avgBytes[1] == None:
            avgBytes[1] = 0
        totalBytes = avgBytes[0] + avgBytes[1]
        point = round((totalBytes/512.0),1)
    except:
        current_app.logger.error(traceback.format_exc())
    return jsonify({'point': point, 'timePoint': timePoint})


@trafficAudit_page.route('/getDevDetailProtPer')
@login_required
def getDevDetailProtPer():
    timeDelta = request.args.get('timeDelta', 0, type=int)
    deviceId = request.args.get('mac')
    # current_app.logger.info(deviceId)
    nowtime = datetime.datetime.now()
    nowtimeNyr = nowtime.strftime("%Y-%m-%d %H:%M:%S")
    preTime = nowtime + datetime.timedelta(hours=-timeDelta, seconds=-1)
    preTimeNyr = preTime.strftime("%Y-%m-%d %H:%M:%S")
    selCmd = "select distinct trafficName from icdevicetrafficstats where \
    iCDeviceId ='%s' and timestamp > '%s' and timestamp < '%s'"%(deviceId,preTimeNyr, nowtimeNyr)
    protDict = {}
    db_proxy = DbProxy()
    
    try:
        #allProts = conn.execute(selCmd)
        #allProts = audit_send_read_cmd(TYPE_AUDIT_APP_SOCKET,selCmd)
        result,allProts = db_proxy.read_db(selCmd)
        selCmd = "select cast(sum(totalBytes) as UNSIGNED) from icdevicetrafficstats where \
        timestamp > '%s' and timestamp < '%s' and iCDeviceId ='%s'"%(preTimeNyr, nowtimeNyr, deviceId)
        
        for prot in allProts:
            sumCmd = selCmd + " and trafficName = '%s'"%(prot[0])
            #cursor.execute(sumCmd)
            #protBytes = cursor.fetchone()[0]
            #protBytes = audit_send_read_cmd(TYPE_AUDIT_APP_SOCKET,sumCmd)
            result,protBytes = db_proxy.read_db(sumCmd)
            protBytes = protBytes[0][0]
            if protBytes == None:
                protBytes = 0
            protDict['%s'%prot[0]] =  protBytes
    except:
        current_app.logger.error(traceback.format_exc())
    if 'unknown' in protDict:
        if 'tradition_pro' in protDict:
            protDict['tradition_pro'] += protDict['unknown']
        else:
            protDict['tradition_pro'] = protDict['unknown']
        del protDict['unknown']
    sortedProtList = sorted(protDict.iteritems(), key=lambda x : x[1], reverse=True)
    allBytes = 0
    for i in range(len(sortedProtList)):
        allBytes += sortedProtList[i][1]
    rows = []
    if allBytes == 0:
        return jsonify({'rows':rows})
    fiveProtPer = 0.0
    for i in range(len(sortedProtList)):
        if i < 5:
            protPerc = round(float(sortedProtList[i][1])/allBytes,4)
            if protPerc > 0.0000999:
                if sortedProtList[i][0] == 'tradition_pro':
                    sortedProtList[i] = list(sortedProtList[i])
                    sortedProtList[i][0] = u'通用网络协议'
                fiveProtPer += protPerc
                rows.append(('%s'%sortedProtList[i][0], protPerc))
        else:
            break
    otherPer = 1.0 - fiveProtPer
    if otherPer > 0.0000999:
        rows.append((u'其他', otherPer))
    return jsonify({'rows': rows})


def nullprotocol(proto_type, proto_list=[]):
    nowtime = datetime.datetime.now()
    nextgettime = nowtime.strftime("%Y-%m-%d %H:%M:%S")
    time_list = [(nowtime - datetime.timedelta(seconds=i * 20)).strftime("%Y-%m-%d %H:%M:%S") for i in
                 range(1, 181)]
    time_list.reverse()
    if proto_type == "predefine":
        iptraffics = ipTraffic()
        outputinfo = []
        trafficdata = [0] * 180
        for proto in iptraffics.protocolTuple:
            if proto == "equipment":
                continue
            protoname = []
            protomsg = []
            protoname.append(proto)
            protomsg.append(protoname)
            protomsg.append(trafficdata)
            protomsg.append(0)
            if ["FOCAS"] not in protomsg:
                outputinfo.append(protomsg)
        return jsonify({'time': time_list, 'data': outputinfo, 'nexttime': nextgettime})
    elif proto_type == "cusproto":
        outputinfo = []
        trafficdata = [0] * 180
        for proto in proto_list:
            if proto == "equipment":
                continue
            protoname = []
            protomsg = []
            protoname.append(proto)
            protomsg.append(protoname)
            protomsg.append(trafficdata)
            protomsg.append(0)
            outputinfo.append(protomsg)
        return jsonify({'time': time_list, 'data': outputinfo, 'nexttime': nextgettime})


def assemproto(v,timelist,len):
    total = 0
    pdatalist = []
    trafficlist = []
    for i in range(0,len):
        pdatalist.append(0)
        trafficlist.append([20,0])
    starttime = datetime.datetime.strptime(timelist,"%Y-%m-%d %H:%M:%S")
    for data in v:
        thistime = datetime.datetime.strptime(data[3],"%Y-%m-%d %H:%M:%S")
        div = ((thistime - starttime).seconds)//20
        mod = ((thistime - starttime).seconds) % 20
        if div > (len-1):
            continue
        if div == 0:
            total += int(data[1]) + int(data[2])
            trafficlist[0][1] += (int(data[1]) + int(data[2])) * 5
            if mod != 0 and mod < 5:
                trafficlist[0][0] += (5 - mod)
        else:
            total += int(data[1]) + int(data[2])
            trafficlist[div][1] += (int(data[1]) + int(data[2])) * 5
            if mod != 0 and mod < 5:
                trafficlist[div][0] += (5 - mod)
                trafficlist[div-1][0] -= (5 - mod)
    for i in range(0,len):
        pdatalist[i] = round((float(trafficlist[i][1] * 8))/(float(trafficlist[i][0] * 1024)), 2)
    return total, pdatalist


@trafficAudit_page.route('/getProtocolInfoByDev')
@login_required
def getProtocolInfoByDev():
    db_proxy = DbProxy()
    timelist = []
    deviceId = request.args.get('deviceId')
    curTime = datetime.datetime.now()
    nextgettime = curTime.strftime("%Y-%m-%d %H:%M:%S")
    # timelist.append(curTime.strftime("%Y-%m-%d %H:%M:%S"))
    for i in range(1,182):
        timelist.append((curTime-datetime.timedelta(seconds=20 * i)).strftime("%Y-%m-%d %H:%M:%S"))
    timelist.reverse()
    iptraffics = ipTraffic()
    protodist = {}
    for proto in iptraffics.protocolTuple:
        if proto != "equipment" and proto != "unknown":
            protodist[proto] = []
    try:
        selcmd = "select trafficName,sendSpeed,recvSpeed,timestamp from icdevicetraffics " \
                 "where iCDeviceId = '%s' and timestamp > '%s' and timestamp < '%s' " \
                 "order by trafficName,timestamp" % (deviceId, timelist[0], timelist[-1])
        result, allprotocol = db_proxy.read_db(selcmd)
        if result != 0 or len(allprotocol) == 0:
            current_app.logger.info(selcmd)
            return nullprotocol("predefine")
        for pro in allprotocol:
            if protodist.has_key(pro[0]):
                protodist[pro[0]].append(pro)
            elif pro[0] == "unknown":
                protodist['tradition_pro'].append(pro)
        outputinfo = []
        for k,v in protodist.iteritems():
            total = 0
            protoname = []
            trafficdata = []
            protomsg = []
            protoname.append(k)
            if len(v) != 0:
                total,trafficdata = assemproto(v,timelist[0],180)
            else:
                trafficdata = [0] * 180
            protomsg.append(protoname)
            protomsg.append(trafficdata)
            protomsg.append(total)
            if ["FOCAS"] not in protomsg:
                outputinfo.append(protomsg)
        outputinfo = sorted(outputinfo, key=lambda x: x[2], reverse=True)
        return jsonify({'time': timelist[1:181], 'data': outputinfo, 'nexttime': nextgettime})
    except:
        current_app.logger.info(traceback.format_exc())
        return nullprotocol("predefine")


@trafficAudit_page.route('/getcusProtocolInfoByDev')
@login_required
def getcusProtocolInfoByDev():
    db_proxy = DbProxy()
    db_proxy_config = DbProxy(CONFIG_DB_NAME)
    timelist = []
    deviceId = request.args.get('deviceId')
    curTime = datetime.datetime.now()
    nextgettime = curTime.strftime("%Y-%m-%d %H:%M:%S")
    # timelist.append(curTime.strftime("%Y-%m-%d %H:%M:%S"))
    for i in range(1,182):
        timelist.append((curTime-datetime.timedelta(seconds=20 * i)).strftime("%Y-%m-%d %H:%M:%S"))
    timelist.reverse()

    cmd_str = "select proto_id, proto_name from self_define_proto_config where proto_id > 500"
    res, rows = db_proxy_config.read_db(cmd_str)

    cusproto_list = []
    cusproto_map = {}
    if res == 0 and len(rows) > 0:
        cusproto_list = [row[1] for row in rows]
        cusproto_map = {row[1]:row[0] for row in rows}
    current_app.logger.info(cusproto_map)
    protodist = {}
    for proto in cusproto_list:
        if proto != "equipment" and proto != "unknown":
            protodist[proto] = []
    # protodist['tradition_pro'] = []
    try:
        selcmd = "select trafficName,sendSpeed,recvSpeed,timestamp from icdevicetraffics " \
                 "where iCDeviceId = '%s' and timestamp > '%s' and timestamp < '%s' " \
                 "order by trafficName,timestamp" % (deviceId, timelist[0], timelist[-1])
        result, allprotocol = db_proxy.read_db(selcmd)
        if result != 0 or len(allprotocol) == 0 or not cusproto_list:
            current_app.logger.info(selcmd)
            return nullprotocol("cusproto", cusproto_list)
        for pro in allprotocol:
            if protodist.has_key(pro[0]):
                protodist[pro[0]].append(pro)
            # elif pro[0] == "unknown":
            #     protodist['tradition_pro'].append(pro)
        outputinfo = []
        for k,v in protodist.iteritems():
            total = 0
            protoname = []
            trafficdata = []
            protomsg = []
            protoname.append(k)
            if len(v) != 0:
                total,trafficdata = assemproto(v,timelist[0],180)
            else:
                trafficdata = [0] * 180
            protomsg.append(protoname)
            protomsg.append(trafficdata)
            protomsg.append(total)
            protomsg.append(cusproto_map[k])
            outputinfo.append(protomsg)
        outputinfo = sorted(outputinfo, key=lambda x: x[2], reverse=True)
        return jsonify({'time': timelist[1:181], 'data': outputinfo, 'nexttime': nextgettime})
    except:
        current_app.logger.info(traceback.format_exc())
        return nullprotocol("cusproto", cusproto_list)


@trafficAudit_page.route('/getcusProtocolInfoRefresh')
@login_required
def getcusProtocolInfoRefresh():
    db_proxy = DbProxy()
    db_proxy_config = DbProxy(CONFIG_DB_NAME)
    nexttime = request.args.get('nexttime')
    deviceId = request.args.get('deviceId')
    idstr = request.args.get('proto_order')
    idlist = idstr.split(',')

    cmd_str = "select proto_id, proto_name from self_define_proto_config where proto_id in ({})".format(idstr)
    res, rows = db_proxy_config.read_db(cmd_str)
    cusproto_list = []
    cusproto_map = {}
    name_id_dict = {}
    if res == 0 and len(rows) > 0:
        cusproto_list = [row[1] for row in rows]
        cusproto_map = {row[0]:row[1] for row in rows}
        name_id_dict = {row[1]:row[0] for row in rows}

    nowtime = datetime.datetime.now()
    nexttimeNpy = datetime.datetime.strptime(nexttime,"%Y-%m-%d %H:%M:%S")
    if nowtime < nexttimeNpy:
        return jsonify({'refersh':1})
    starttime = (nexttimeNpy-datetime.timedelta(seconds=20)).strftime("%Y-%m-%d %H:%M:%S")
    div = ((nowtime - nexttimeNpy).seconds) // 20
    mod = ((nowtime - nexttimeNpy).seconds) % 20
    if mod == 0:
        div = div - 1
    endtime = (nexttimeNpy+datetime.timedelta(seconds=20 * div)).strftime("%Y-%m-%d %H:%M:%S")
    nextgettime = (nexttimeNpy+datetime.timedelta(seconds=20 * (div+1))).strftime("%Y-%m-%d %H:%M:%S")
    if div > 178:
        return jsonify({'refersh': 1})
    timelist = []
    for i in range(0,div+1):
        timelist.append((nexttimeNpy+datetime.timedelta(seconds=20 * i)).strftime("%Y-%m-%d %H:%M:%S"))
    protodist = {}
    for proto in cusproto_list:
        if proto != "equipment" and proto != "unknown":
            protodist[proto] = []
    try:
        selcmd = "select trafficName,sendSpeed,recvSpeed,timestamp from icdevicetraffics where iCDeviceId = '%s' and timestamp >= '%s' and timestamp <= '%s' order by trafficName,timestamp"%(deviceId,starttime,endtime)
        result, allprotocol = db_proxy.read_db(selcmd)
        if result != 0:
            current_app.logger.info(selcmd)
            return jsonify({'refersh': 1})
        for pro in allprotocol:
            if protodist.has_key(pro[0]):
                protodist[pro[0]].append(pro)
        outputinfo = []
        if len(cusproto_list) != 0:
            current_app.logger.info("order_proto is not null :")
            for name in cusproto_list:
                if protodist.has_key(name):
                    protoname = []
                    # trafficdata = []
                    protomsg = []
                    protoname.append(name_id_dict[name])
                    if len(protodist[name]) != 0:
                        total, trafficdata = assemproto(protodist[name], starttime, len(timelist))
                    else:
                        trafficdata = [0] * len(timelist)
                    protomsg.append(protoname)
                    protomsg.append(trafficdata)
                    outputinfo.append(protomsg)
        else:
            current_app.logger.info("order_proto is null :")
            for k,v in protodist.iteritems():
                protoname = []
                protomsg = []
                protoname.append(name_id_dict[k])
                if len(v) != 0:
                    total,trafficdata = assemproto(v,starttime,len(timelist))
                else:
                    trafficdata = [0] * len(timelist)
                protomsg.append(protoname)
                protomsg.append(trafficdata)
                outputinfo.append(protomsg)

        for proto_id in idlist:
            if int(proto_id) not in cusproto_map:
                protomsg = []
                protoname = [int(proto_id)]
                trafficdata = [0] * len(timelist)
                protomsg.append(protoname)
                protomsg.append(trafficdata)
                outputinfo.append(protomsg)
        out_dict = {int(i[0][0]): i for i in outputinfo}
        data_list = []
        for proto_id in idlist:
            if int(proto_id) in out_dict:
                data_list.append(out_dict[int(proto_id)])
        return jsonify({'time': timelist, 'data': data_list, 'nexttime': nextgettime, 'refersh': 0})
    except:
        current_app.logger.info(traceback.format_exc())
        return jsonify({'refersh': 1})


@trafficAudit_page.route('/getProtocolInfoRefresh')
@login_required
def getProtocolInfoRefresh():
    db_proxy = DbProxy()
    nexttime = request.args.get('nexttime')
    deviceId = request.args.get('deviceId')
    orderlist = request.args.get('proto_order')
    orderlist = orderlist.split(',')
    nowtime = datetime.datetime.now()
    nexttimeNpy = datetime.datetime.strptime(nexttime,"%Y-%m-%d %H:%M:%S")
    if nowtime < nexttimeNpy:
        return jsonify({'refersh':1})
    starttime = (nexttimeNpy-datetime.timedelta(seconds=20)).strftime("%Y-%m-%d %H:%M:%S")
    div = ((nowtime - nexttimeNpy).seconds) // 20
    mod = ((nowtime - nexttimeNpy).seconds) % 20
    if mod == 0:
        div = div - 1
    endtime = (nexttimeNpy+datetime.timedelta(seconds=20 * div)).strftime("%Y-%m-%d %H:%M:%S")
    nextgettime = (nexttimeNpy+datetime.timedelta(seconds=20 * (div+1))).strftime("%Y-%m-%d %H:%M:%S")
    if div > 178:
        return jsonify({'refersh': 1})
    timelist = []
    for i in range(0,div+1):
        timelist.append((nexttimeNpy+datetime.timedelta(seconds=20 * i)).strftime("%Y-%m-%d %H:%M:%S"))
    iptraffics = ipTraffic()
    protodist = {}
    for proto in iptraffics.protocolTuple:
        if proto != "equipment" and proto != "unknown":
            protodist[proto] = []
    try:
        selcmd = "select trafficName,sendSpeed,recvSpeed,timestamp from icdevicetraffics where iCDeviceId = '%s' and timestamp >= '%s' and timestamp <= '%s' order by trafficName,timestamp"%(deviceId,starttime,endtime)
        result, allprotocol = db_proxy.read_db(selcmd)
        if result != 0:
            current_app.logger.info(selcmd)
            return jsonify({'refersh': 1})
        for pro in allprotocol:
            if protodist.has_key(pro[0]):
                protodist[pro[0]].append(pro)
            elif pro[0] == "unknown":
                protodist['tradition_pro'].append(pro)
        outputinfo = []
        if len(orderlist) != 0:
            current_app.logger.info("order_proto is not null :")
            for name in orderlist:
                if protodist.has_key(name):
                    protoname = []
                    trafficdata = []
                    protomsg = []
                    protoname.append(name)
                    if len(protodist[name]) != 0:
                        total, trafficdata = assemproto(protodist[name], starttime, len(timelist))
                    else:
                        trafficdata = [0] * len(timelist)
                    protomsg.append(protoname)
                    protomsg.append(trafficdata)
                    if ["FOCAS"] not in protomsg:
                        outputinfo.append(protomsg)
        else:
            current_app.logger.info("order_proto is null :")
            for k,v in protodist.iteritems():
                protoname = []
                trafficdata = []
                protomsg = []
                protoname.append(k)
                if len(v) != 0:
                    total,trafficdata = assemproto(v,starttime,len(timelist))
                else:
                    trafficdata = [0] * len(timelist)
                protomsg.append(protoname)
                protomsg.append(trafficdata)
                if ["FOCAS"] not in protomsg:
                    outputinfo.append(protomsg)

        return jsonify({'time': timelist, 'data': outputinfo, 'nexttime': nextgettime, 'refersh': 0})
    except:
        current_app.logger.info(traceback.format_exc())
        return jsonify({'refersh': 1})


@trafficAudit_page.route('/getDevDetailProtTable')
@login_required
def getDevDetailProtTable():
    page = request.args.get('page', 0, type=int)
    deviceId = request.args.get('deviceId')
    # current_app.logger.info(deviceId)
    nowtime = datetime.datetime.now()
    nowtimeNyr = nowtime.strftime("%Y-%m-%d %H:%M:%S")
    preTime = nowtime + datetime.timedelta(hours=-168, seconds=-1)
    preTimeNyr = preTime.strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    db_proxy = DbProxy()
    selCmd = "select distinct trafficName from icdevicetrafficstats where iCDeviceId ='%s' and timestamp > '%s' " \
             "and timestamp < '%s'"%(deviceId, preTimeNyr, nowtimeNyr)
    getAllBytesCmd = "select cast(sum(totalBytes) as UNSIGNED) from icdevicetrafficstats where iCDeviceId ='%s' and " \
                     "timestamp > '%s' and timestamp < '%s'"%(deviceId, preTimeNyr, nowtimeNyr)
    
    try:
        result,allBytes = db_proxy.read_db(getAllBytesCmd)
        allBytes = allBytes[0][0]
        if allBytes == None:
            return jsonify({'rows': rows,'total':0,'page':1})

        result,allProts = db_proxy.read_db(selCmd)
        tra_id = -1
        un_id = -1
        row_index = 0
        for prot_id, prot in enumerate(allProts):
            selCmd = "select trafficName,cast(sum(totalBytes) as UNSIGNED),max(timestamp) from icdevicetrafficstats \
            where iCDeviceId='%s' and trafficName = '%s' and timestamp > '%s' and timestamp < '%s'"%(deviceId,prot[0],preTimeNyr,nowtimeNyr)
            result,row = db_proxy.read_db(selCmd)
            row = row[0]
            row = list(row)
            protPercent = round(float(row[1])/allBytes,4)
            if protPercent < 0.00009999:
                continue
            if row[0] == 'tradition_pro':
                row[0] = u'通用网络协议'
                tra_id = row_index
            elif row[0] == 'unknown':
                row[0] = u'通用网络协议'
                un_id = row_index
            #row = list(row)
            row[1] = protPercent
            rows.append(row)
            row_index = row_index + 1
    except:
        current_app.logger.error(traceback.format_exc())
        return jsonify({'rows': [],'total':0,'page':1})

    if un_id != -1 and tra_id != -1:
        rows[tra_id][1] += rows[un_id][1]
        del rows[un_id]
    sortedRows = sorted(rows,key=lambda x : x[1],reverse=True)
    return jsonify({'rows': sortedRows[((page-1)*10):(page*10)], 'total':len(rows), 'page':page})


@trafficAudit_page.route('/getDevDetailTrafficNew')
def getDevListDetailTrafficNew():
    try:
        now_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dev = request.args.get('dev')
        db_proxy = DbProxy()
        config_db_proxy = DbProxy(CONFIG_DB_NAME)
        sql_str = '''select distinct cast(unix_timestamp(timestamp) as signed) as time from dev_band_20s 
                                    where timestamp<'%s'order by timestamp desc limit 181''' % now_timestamp
        res, sql_res = db_proxy.read_db(sql_str)
        if res != 0:
            return jsonify({'points': [], "max_val": 0, 'timePoints': [],
                            'low_line': -1, 'high_line': -1, 'next_time': ""})

        # 时间戳补点
        origin_time_list = []
        now_time = int(time.time())
        max_flow_time = sql_res[0][0]
        tmp_dur_time = now_time - max_flow_time
        tmp_dur_count = tmp_dur_time / 20
        if tmp_dur_count > 180:
            tmp_dur_count = 180
        origin_time_list.append(max_flow_time)
        for i in range(1, tmp_dur_count):
            origin_time_list.append(max_flow_time + 20 * i)
        origin_time_list.reverse()

        res_len = len(sql_res)
        for t in range(1, res_len):
            tmp_dur = int(sql_res[t-1][0]) - int(sql_res[t][0])
            # print tmp_dur
            tmp_count = tmp_dur / 20
            tmp_mod = tmp_dur % 20
            if tmp_count > 1 and tmp_mod > 5:
                tmp_count += 1
            for i in range(1, tmp_count):
                tmp_i = int(sql_res[t - 1][0]) - 20 * i
                origin_time_list.append(tmp_i)
            origin_time_list.append(sql_res[t][0])
        tmp_len = 180 - len(origin_time_list)
        if tmp_len > 0:
            min_t = int(origin_time_list[-1])
            for i in range(tmp_len):
                origin_time_list.append(min_t - i * 20)
        else:
            origin_time_list = origin_time_list[:180]

        origin_time_list.pop(179)
        origin_time_list.insert(0, origin_time_list[0] - 20)

        points = []
        timePoints = []
        sql_str = "select cast(unix_timestamp(timestamp) as signed) as time, band from dev_band_20s " \
                  "where timestamp <= '%s' and devid = '%s' order by timestamp asc" % (now_timestamp, dev)
        res, sql_res = db_proxy.read_db(sql_str)
        if res != 0:
            return jsonify({'points': [], "max_val": 0, 'timePoints': [],
                            'low_line': -1, 'high_line': -1, 'next_time': ""})
        for time_elem in origin_time_list:
            flag = 0
            for elem in sql_res:
                if time_elem == elem[0]:
                    timePoints.append(elem[0])
                    points.append(float(elem[1]))
                    flag = 1
                    break
            if flag == 0:
                timePoints.append(time_elem)
                points.append(0)
        timePoints.reverse()
        points.reverse()

        time_axis_list = []
        for elem in timePoints:
            tmp_elem = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(elem))
            time_axis_list.append(tmp_elem.split(" ")[1])
        low_line = -1
        high_line = -1

        sql_str = "select * from dev_band_threshold where dev_id = '%s'" % dev
        res, sql_res = config_db_proxy.read_db(sql_str)
        if res == 0 and len(sql_res) > 0:
            low_line = sql_res[0][3]
            high_line = sql_res[0][4]
        return jsonify({'points': points, "max_val": max(points), 'timePoints': time_axis_list,
                        'low_line': low_line, 'high_line': high_line, 'next_time': timePoints[-1]})
    except:
        current_app.logger.error(traceback.format_exc())
        return jsonify({'status': 0})


@trafficAudit_page.route('/getDevDetailTrafficLatestPointNew')
def getDevDetailTrafficLatestPointNew():
    dev = request.args.get('dev')
    tmp_time = request.args.get('time')
    tmp_stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(tmp_time)))
    # now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') # request.args.get('time')
    db_proxy = DbProxy()
    sql_str = "select cast(unix_timestamp(timestamp) as signed) as time from dev_band_20s " \
              "where timestamp > '%s' order by timestamp asc" % tmp_stamp
    res, sql_res = db_proxy.read_db(sql_str)
    if res != 0 or len(sql_res) == 0:
        # next_time = now_time
        res_time = int(tmp_time) + 20
    else:
        res_time = sql_res[0][0]
    next_time = res_time
    res_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(res_time))
    sql_str = "select band from dev_band_20s where timestamp = '%s' and devid = '%s'" % (res_time, dev)
    res, sql_res = db_proxy.read_db(sql_str)
    current_app.logger.error(sql_str)
    if res != 0 or len(sql_res) == 0:
        return jsonify({'status': 1, 'point': 0, 'timePoint': res_time, 'next_time': next_time})
    return jsonify({'status': 1, 'point': sql_res[0][0], 'timePoint': res_time, 'next_time': next_time})


@trafficAudit_page.route('/setDevTrafficBandRange', methods=["GET", "POST"])
def setDevTrafficBandRange():
    try:
        if request.method == "GET":
            dev = request.args.get('dev')
            ip = request.args.get('ip')
            mac = request.args.get('mac')
            high_line = float(request.args.get('high'))
            low_line = float(request.args.get('low'))
            flag = int(request.args.get('flag'))
            loginuser = request.args.get('loginuser')
        else:
            data = request.get_json()
            dev = data['dev']
            ip = data['ip']
            mac = data['mac']
            high_line = float(data['high'])
            low_line = float(data['low'])
            flag = int(data['flag'])
            loginuser = data['loginuser']
        config_db_proxy = DbProxy(CONFIG_DB_NAME)
        if( ip == "NULL" or ":" in ip):
            ip = ""
        dev_name = get_devname_by_ipmac(ip, mac)
        dev_name = dev_name.encode("utf8")
        if flag == 1:
            sql_str = "update dev_band_threshold set high_line = %.1f, low_line = %.1f where dev_id = '%s'" % (high_line, low_line, dev)
            res = config_db_proxy.write_db(sql_str)
            if( res != 0 ):
                msg={}
                userip = get_oper_ip_info(request)
                msg['UserName'] = loginuser
                msg['UserIP'] = userip
                msg['Operate'] = u"修改设备%s流量阈值，低阈值：%skbps, 高阈值：%skbps" % (dev_name, str(low_line), str(high_line))
                msg['ManageStyle'] = 'WEB'
                msg['Result'] = '1'
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({'status': 0})
            else:
                sock = socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
                sock.sendto("3,%s"% str([dev, low_line, high_line]), dst_machine_learn_ctl_addr)
                msg={}
                userip = get_oper_ip_info(request)
                msg['UserName'] = loginuser
                msg['UserIP'] = userip
                msg['Operate'] = "修改设备%s流量阈值，低阈值：%skbps, 高阈值：%skbps" % (dev_name, str(low_line), str(high_line))
                msg['Operate'] = msg['Operate'].decode("utf8")
                msg['ManageStyle'] = 'WEB'
                msg['Result'] = '0'
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({'status': 1})
        elif flag == 2:
            if ":" in ip:
                ip = "NULL"
            sql_str = "insert into dev_band_threshold values ('%s', '%s', '%s', %.1f, %.1f)" % (dev, ip, mac, low_line, high_line)
            res = config_db_proxy.write_db(sql_str)
            if( res != 0 ):
                msg={}
                userip = get_oper_ip_info(request)
                msg['UserName'] = loginuser
                msg['UserIP'] = userip
                msg['Operate'] = u"增加设备%s流量阈值，低阈值：%skbps, 高阈值：%skbps" % (dev_name, str(low_line), str(high_line))
                msg['ManageStyle'] = 'WEB'
                msg['Result'] = '1'
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({'status': 0})
            else:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
                sock.sendto("4,%s"% str([dev, ip, mac, low_line, high_line]), dst_machine_learn_ctl_addr)
                msg={}
                userip = get_oper_ip_info(request)
                msg['UserName'] = loginuser
                msg['UserIP'] = userip
                msg['Operate'] = "增加设备%s流量阈值，低阈值：%skbps, 高阈值：%skbps" % (dev_name, str(low_line), str(high_line))
                msg['Operate'] = msg['Operate'].decode("utf8")
                msg['ManageStyle'] = 'WEB'
                msg['Result'] = '0'
                send_log_db(MODULE_OPERATION, msg)
                return jsonify({'status': 1})
        else:
            return jsonify({'status': 0})
    except:
        current_app.logger.exception("Exception Logged")
        return jsonify({'status': 0})


@trafficAudit_page.route('/delDevTrafficBandRange', methods=["GET", "POST"])
def delDevTrafficBandRange():
    try:
        if request.method == "GET":
            dev = request.args.get('dev')
            loginuser = request.args.get('loginuser')
        else:
            data = request.get_json()
            dev = data['dev']
            loginuser = data['loginuser']
        db_proxy = DbProxy(CONFIG_DB_NAME)
        sql_str = "select dev_ip, dev_mac from dev_band_threshold where dev_id = '%s' limit 1" % dev
        res, sql_res = db_proxy.read_db(sql_str)
        if res != 0 or len(sql_res) == 0:
            return jsonify({'status': 0})
        ip = sql_res[0][0]
        mac = sql_res[0][1]
        if sql_res[0][0] == "NULL" or ":" in sql_res[0][0]:
            ip = ""
        dev_name = get_devname_by_ipmac(ip, mac)
        dev_name = dev_name.encode("utf8")
        sql_str = "delete from dev_band_threshold where dev_id = '%s'" % dev
        res = db_proxy.write_db(sql_str)
        if res != 0 :
            msg = {}
            userip = get_oper_ip_info(request)
            msg['UserName'] = loginuser
            msg['UserIP'] = userip
            msg['Operate'] = u"删除设备%s流量阈值" % dev_name
            msg['ManageStyle'] = 'WEB'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 0})
        else:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            sock.sendto("5,%s" % dev, dst_machine_learn_ctl_addr)
            msg = {}
            userip = get_oper_ip_info(request)
            msg['UserName'] = loginuser
            msg['UserIP'] = userip
            msg['Operate'] = "删除设备%s流量阈值" % dev_name
            msg['Operate'] = msg['Operate'].decode("utf8")
            msg['ManageStyle'] = 'WEB'
            msg['Result'] = '0'
            send_log_db(MODULE_OPERATION, msg)
            return jsonify({'status': 1})

    except:
        current_app.logger.exception("Exception Logged")
        return jsonify({'status': 0})
