import threading
from global_var import *

logger = logging.getLogger('flask_db_socket_log')

t1 = None
t2 = None

unknowndevice_addr = '/data/sock/unknown_device_sock'


class unknownDevice(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.device_list = Queue.Queue(maxsize=queue_limit["unknownDevice"])
        self.sock = None
    
    def run(self):
        try:
            if os.path.exists(unknowndevice_addr):
                os.remove(unknowndevice_addr)
        except:
            logger.error("unknownDevice socket not exist")
        self.sock = socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
        self.sock.bind(unknowndevice_addr)
        create_mac_dict()
        t1 = threading.Thread(target=self.recvDeviceInfo)
        t1.setDaemon(True)    
        t1.start()
        
        t2 = threading.Thread(target=self.SaveDeviceInfo)
        t2.setDaemon(True)
        t2.start()

    def recvDeviceInfo(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(2048)
            except:
                data = None
            if data is None:
                time.sleep(0.001)
                continue
            try:
                if self.device_list.full():
                    continue
                self.device_list.put(data, 0)
            except:
                continue
            time.sleep(0.001)
    
    def SaveDeviceInfo(self):
        db_proxy = DbProxy(CONFIG_DB_NAME)
        while True:
            try:
                data = self.device_list.get(timeout=60)
            except:
                data = None
            if data is None:
                time.sleep(0.001)
                continue
            tmp_intf_pos = data.find(',')
            tmp_intf = data[0:tmp_intf_pos]
            data = data[tmp_intf_pos+1:]
            try:
                tmp_device = data.split(',')
                tmp_mac = ':'.join((re.findall(r'.{2}', tmp_device[1])))
                # tmp_mac = tmp_device[1]

                if tmp_device[0] != "" and tmp_device[0].find('.') != -1 and int(tmp_device[0].split('.')[0]) >= 224:
                    continue

                device_str = "select count(*) from ipmaclist where ip='%s'" % tmp_device[0]
            except:
                continue
            result, rows = db_proxy.read_db(device_str)
            try:
                device_num = rows[0][0]
            except:
                device_num = 0
            name = get_default_devname_by_ipmac(tmp_device[0], tmp_mac)
            if device_num == 0:
                num_str = "select count(*) from ipmaclist"
                result, rows = db_proxy.read_db(num_str)
                if rows:
                    ipmac_num = rows[0][0]
                else:
                    ipmac_num = 0
                num_limit = db_record_limit["device"] + 1

                if ipmac_num >= num_limit:
                    continue


                ip_str = "insert into ipmaclist (enabled,is_study,device_name,ip,mac,interface) " \
                         "values(0,0,'%s','%s','%s',%s)" % (name, tmp_device[0], tmp_mac, tmp_intf)
                _ = db_proxy.write_db(ip_str)
            num_str = "select count(*) from topdevice"
            _, rows = db_proxy.read_db(num_str)
            if rows:
                top_num = rows[0][0]
            else:
                top_num = 0
            num_limit = db_record_limit["device"] + 1
            if top_num >= num_limit:
                continue
            topdev_str = "select count(*) from topdevice where ip='%s'" % tmp_device[0]
            _, rows = db_proxy.read_db(topdev_str)
            try:
                top_num = rows[0][0]
            except:
                top_num = 0
            if top_num == 0:
                top_str = "insert into topdevice (dev_type,name,ip,mac,is_study,dev_interface,is_unknown) " \
                          "values(0,'%s','%s','%s',0,%s,1)" % (name, tmp_device[0], tmp_mac, tmp_intf)
                _ = db_proxy.write_db(top_str)
            time.sleep(0.001)
