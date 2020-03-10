#!/usr/bin/python
# -*- coding: UTF-8 -*-
import traceback
import logging
import json
import MySQLdb
from aes_cipher import AESCipher, AES_KEY, AES_IV

logger = logging.getLogger('flask_mw_log')

def get_aes_cipher():
    return AESCipher(AES_KEY.decode("hex"), AES_IV.decode("hex"))
def InsertRuleDb(path):
    try:
        file = open(path)
    except:
        logger.info("open rule file failed")
    try:
        conn = MySQLdb.connect(host='localhost',port=3306, user='keystone', passwd='OptValley@4312',db='keystone_config')
        cur = conn.cursor()
        while True:
            line = file.readline()
            if not line:
                break
            else:
                sid_num = 0
                sid = (line.split("sid:")[1].split(";"))[0]
                judge_sid =  "select count(*) from signatures where sid =" + str(sid)
                sid_total = cur.execute(judge_sid)
                sid_total=cur.fetchall()
                for sid_rule in sid_total:
                    sid_num = sid_rule[0]
                if sid_num == 0:
                    message = get_aes_cipher().encrypt(line)
                    hash_key = hash(message)
                
                    sql = "INSERT INTO signatures (action,riskLevel,vulnerabilityId,sid,body) VALUES (2,2," + "\"" + str(hash_key)+ "\"," + sid + ",\"" + str(message) + "\")"
                    cur.execute(sql)
     
                    vulner_sql = "update vulnerabilities set vulnerabilityId =" + "\"" + str(hash_key) + "\"where sid =" + str(sid)
                    cur.execute(vulner_sql)
                else:
                     logger.info("signatures tables have already")     
        conn.commit()
    except:
        logger.error("InsertRuleDb error")
        logger.error(traceback.format_exc())

def InsertjsonDataDb(path):
    json_key = 0
    #0 is format correct 1 is error   
    flag = 0 
    try:
        f = file(path)
    except:
        logger.info("open json file failed")
    try:
        json_format = ("sid", "severity", "category", "threatName", "threatNameEng", "description", "descriptionEng", \
                       "vulnerable", "requirement", "caused", "suggest", "reference", "valid", "cve", "defaultAction", "publishDate")
        conn = MySQLdb.connect(host='localhost',port=3306, user='keystone', passwd='OptValley@4312',db='keystone_config')
        cur = conn.cursor()
        json_data = json.load(f)
        for json_node in json_data['vulnerability']:
            element_list = []
            element_data = []
            sql_seq = ["INSERT INTO vulnerabilities("]
            # for use for check json format is correct or error
            for node_key in json_node.keys():
                if node_key not in json_format:
                    json_key = 0
                    break
                else:
                    if node_key == "vulnerable":
                        continue
                    json_key += 1
                    element = '%s'%(node_key)
                    data = '"%s"'%(json_node[node_key])
                    if node_key == "valid":
                        if json_node[node_key] == 'True':
                            data = '1'
                        else:
                            data = '0'
                    element_list.append(element)
                    element_data.append(data)
            if json_key <= 15:
                json_key = 0
                sid = json_node["sid"]
                judge_sid =  "select count(*) from vulnerabilities where sid =" + str(sid)
                sid_total = cur.execute(judge_sid)
                sid_total=  cur.fetchall()
                for sid_rule in sid_total:
                    sid_num = sid_rule[0]
                if sid_num == 0 or sid_total == None:
                    sql = ",".join(element_list)
                    sql_node = ",".join(element_data)
                    sql_seq.append(sql)
                    sql_seq.append(")VALUES(") 
                    sql_seq.append(sql_node)
                    sql_seq.append(")")
                    sql_node = "".join(sql_seq)
                    try:
                        sql_node=sql_node.encode('utf-8')
                        cur.execute(sql_node)
                    except:
                        logger.info("insert into vulnerabilities error"+sql_node)
                        logger.error(traceback.format_exc())
        conn.commit()
        conn.close()
        f.close
    except:
        logger.error("InsertjsonDataDb error")
        logger.error(traceback.format_exc())