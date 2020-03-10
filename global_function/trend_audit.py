import threading
import psutil
from global_function.global_var import *
from log_config import LogConfig

ISOTIMEFORMAT='%Y-%m-%d %X'
DAYTOHOURS = 24

INTERFACE_LIST = ['eth0','eth1','eth2','eth3','eth4','eth5']

def get_intf_info():
    tmp_rx_list = []
    tmp_tx_list = []
    res = psutil.net_io_counters(pernic=True)
    for intf in INTERFACE_LIST:
        try:
            tmp_rx_list.append(res[intf][1])
            tmp_tx_list.append(res[intf][0])
        except:
            tmp_rx_list.append(0)
            tmp_tx_list.append(0)
    return tmp_rx_list,tmp_tx_list
    

class trendAudit(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        t4 = threading.Thread(target=self.SaveMachineFlowInfo)
        t4.setDaemon(True)
        t4.start()
        t4.join()
              
    
    def UpdateMachineFlowInfo(self,db_proxy):    
        sql_str = "select id,time from machineflow where flag=1"
        res, rows = db_proxy.read_db(sql_str)
        count_str = "select count(*) from machineflow"
        res, count_rows = db_proxy.read_db(count_str)
        count_num = count_rows[0][0]
        insert_num = 360 - count_num    
        if len(rows) > 0:
            id_num = rows[0][0]
            tmp_sql_str = "update machineflow set flag=0 where id=%d"%id_num
            tmp_count = (int(time.time())-self.getsecondfromtime(rows[0][1]))/10
            if tmp_count<=0:
                tmp_count = 0
            else:
                tmp_count = tmp_count - 1
            if tmp_count>360:
                tmp_count = 360
            if tmp_count>0:
                db_proxy.write_db(tmp_sql_str)
            for i in range(0,tmp_count):
                tmp_flag = 0
                tmp_time = time.strftime(ISOTIMEFORMAT, time.localtime(time.time()-(tmp_count-i+1)*10))
                if i == tmp_count-1:
                    tmp_flag = 1
                if i<insert_num:
                    insert_str = "insert into machineflow (deviceflow_rx,deviceflow_tx,interfaceflow_one_rx,interfaceflow_one_tx,\
                                    interfaceflow_two_rx,interfaceflow_two_tx,interfaceflow_three_rx,interfaceflow_three_tx,\
                                    interfaceflow_four_rx,interfaceflow_four_tx,interfaceflow_five_rx,interfaceflow_five_tx,\
                                    interfaceflow_six_rx,interfaceflow_six_tx,time,flag) values(%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,'%s',%d)"\
                                    %(0,0,0,0,0,0,0,0,0,0,0,0,0,0,tmp_time,tmp_flag)
                    db_proxy.write_db(insert_str)
                    id_num = id_num + 1
                else:
                    update_str = "update machineflow set deviceflow_rx=%d,deviceflow_tx=%d,interfaceflow_one_rx=%d,interfaceflow_one_tx=%d,\
                        interfaceflow_two_rx=%d,interfaceflow_two_tx=%d,interfaceflow_three_rx=%d,interfaceflow_three_tx=%d,\
                        interfaceflow_four_rx=%d,interfaceflow_four_tx=%d,interfaceflow_five_rx=%d,interfaceflow_five_tx=%d,\
                        interfaceflow_six_rx=%d,interfaceflow_six_tx=%d,time='%s',flag=%d where id=%d"\
                        %(0,0,0,0,0,0,0,0,0,0,0,0,0,0,tmp_time,tmp_flag,(id_num%360)+1)
                    db_proxy.write_db(update_str)
                    id_num = id_num + 1          
            
            
    def SaveMachineFlowInfo(self):
        db_proxy = DbProxy()
        try:
            self.UpdateMachineFlowInfo(db_proxy)
        except:
            logging.error(traceback.format_exc())
        rx_per_list = []
        rx_last_list = []
        tx_per_list = []
        tx_last_list = []
        per_session_rx_num = 0
        per_session_tx_num = 0
        last_session_rx_num = 0
        last_session_tx_num = 0
        rx_per_list,tx_per_list = get_intf_info()
        for i in range(0,6):
            per_session_rx_num += rx_per_list[i]
            per_session_tx_num += tx_per_list[i]
        try:
            while True:
                time.sleep(10)
                rx_last_list,tx_last_list = get_intf_info()
                for i in range(0,6):
                    last_session_rx_num += rx_last_list[i]
                    last_session_tx_num += tx_last_list[i]
                now_session_rx_num = (last_session_rx_num - per_session_rx_num)*8/10240
                now_session_tx_num = (last_session_tx_num - per_session_tx_num)*8/10240
                per_session_rx_num = last_session_rx_num
                per_session_tx_num = last_session_tx_num
                last_session_rx_num = 0
                last_session_tx_num = 0
                now_interface_rx_num_list = []
                now_interface_tx_num_list = []
                for i in range(0,6):
                    tmp_rx_num =  (rx_last_list[i] - rx_per_list[i])*8/10240
                    now_interface_rx_num_list.append(tmp_rx_num)
                    tmp_tx_num =  (tx_last_list[i] - tx_per_list[i])*8/10240
                    now_interface_tx_num_list.append(tmp_tx_num)
                sql_str = "select id from machineflow where flag=1"
                res,rows = db_proxy.read_db(sql_str)
                insert_str=""
                tmp_time = time.strftime(ISOTIMEFORMAT, time.localtime())
                rx_per_list = rx_last_list
                tx_per_list = tx_last_list
                if len(rows) == 0:
                    insert_str = "insert into machineflow (deviceflow_rx,deviceflow_tx,interfaceflow_one_rx,interfaceflow_one_tx,\
                                    interfaceflow_two_rx,interfaceflow_two_tx,interfaceflow_three_rx,interfaceflow_three_tx,\
                                    interfaceflow_four_rx,interfaceflow_four_tx,interfaceflow_five_rx,interfaceflow_five_tx,\
                                    interfaceflow_six_rx,interfaceflow_six_tx,time,flag) values(%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,'%s',1)"\
                                    %(now_session_rx_num,now_session_tx_num,now_interface_rx_num_list[0],now_interface_tx_num_list[0],\
                                      now_interface_rx_num_list[1],now_interface_tx_num_list[1],now_interface_rx_num_list[2],now_interface_tx_num_list[2],\
                                      now_interface_rx_num_list[3],now_interface_tx_num_list[3],now_interface_rx_num_list[4],now_interface_tx_num_list[4],\
                                      now_interface_rx_num_list[5],now_interface_tx_num_list[5],tmp_time)
                     
                    db_proxy.write_db(insert_str)
                else:
                    id_num = rows[0][0]
                    count_str = "select count(*) from machineflow"
                    res,count_rows = db_proxy.read_db(count_str)
                    count_num = count_rows[0][0]
                    if count_num<360:
                        insert_str = "insert into machineflow (deviceflow_rx,deviceflow_tx,interfaceflow_one_rx,interfaceflow_one_tx,\
                                    interfaceflow_two_rx,interfaceflow_two_tx,interfaceflow_three_rx,interfaceflow_three_tx,\
                                    interfaceflow_four_rx,interfaceflow_four_tx,interfaceflow_five_rx,interfaceflow_five_tx,\
                                    interfaceflow_six_rx,interfaceflow_six_tx,time,flag) values(%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,'%s',1)"\
                                    %(now_session_rx_num,now_session_tx_num,now_interface_rx_num_list[0],now_interface_tx_num_list[0],\
                                      now_interface_rx_num_list[1],now_interface_tx_num_list[1],now_interface_rx_num_list[2],now_interface_tx_num_list[2],\
                                      now_interface_rx_num_list[3],now_interface_tx_num_list[3],now_interface_rx_num_list[4],now_interface_tx_num_list[4],\
                                      now_interface_rx_num_list[5],now_interface_tx_num_list[5],tmp_time)
                    else:
                        insert_str = "update machineflow set deviceflow_rx=%d,deviceflow_tx=%d,interfaceflow_one_rx=%d,interfaceflow_one_tx=%d,\
                        interfaceflow_two_rx=%d,interfaceflow_two_tx=%d,interfaceflow_three_rx=%d,interfaceflow_three_tx=%d,\
                        interfaceflow_four_rx=%d,interfaceflow_four_tx=%d,interfaceflow_five_rx=%d,interfaceflow_five_tx=%d,\
                        interfaceflow_six_rx=%d,interfaceflow_six_tx=%d,time='%s',flag=1 where id=%d"\
                        %(now_session_rx_num,now_session_tx_num,now_interface_rx_num_list[0],now_interface_tx_num_list[0],\
                          now_interface_rx_num_list[1],now_interface_tx_num_list[1],now_interface_rx_num_list[2],now_interface_tx_num_list[2],\
                          now_interface_rx_num_list[3],now_interface_tx_num_list[3],now_interface_rx_num_list[4],now_interface_tx_num_list[4],\
                          now_interface_rx_num_list[5],now_interface_tx_num_list[5],tmp_time,(id_num%360)+1)
                    db_proxy.write_db(insert_str)
                    tmp_sql_str = "update machineflow set flag=0 where id=%d"%id_num
                    db_proxy.write_db(tmp_sql_str)
        except:
            logging.error(traceback.format_exc())