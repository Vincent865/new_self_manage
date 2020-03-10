import subprocess
import commands
import time
import re
import os

class webdpi():
    def checkip(self,ip_str):
        if len(ip_str)==0:
            return False
        pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        if re.match(pattern, ip_str):
            return True
        else:
            return False

    def checkdpiip(self,ip_str):
        if len(ip_str)==0:
            return False
        #exclude 127(local loop) or 0 in first segment
        pattern_127_0 = r"\b(127|0)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        #exclude 0 or 255 in last segment
        pattern_255_0 = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-4]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[1-9])\b"

        if re.match(pattern_255_0, ip_str):
            if re.match(pattern_127_0, ip_str):
                return False
            else:
                return True
        else:
            return False

    def checkmask(self,mask):
        if self.checkip(mask):
            mask = mask.split(".")
            masknum = [int(num) for num in mask]
            maskbin = ''

            for num in masknum:
                item = bin(num).split('0b')[1]

                if len(item) != 8:
                    zeronum = '0'*(8-len(item))
                    item = zeronum + item
                maskbin += item

            if '01' in maskbin:
                return False
            else:
                return True
        else:
            return False
	
    def deldefaultroute(self):
        child = subprocess.Popen('vtysh',shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        child.stdin.write('show running-config\n')
        child.stdin.write('exit\n')
        route_list = []
        res_out = child.stdout.read()
        route_start = res_out.find('ip route')
        route_end = 0
        while(route_start>=0):
            route_end = res_out.find('\n',route_start)
            route_info = res_out[route_start:route_end]
            route_list.append(route_info)
            route_start = res_out.find('ip route',route_end)
		
        child = subprocess.Popen('vtysh',shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        child.stdin.write('configure terminal\n')
        for info in route_list:
            child.stdin.write('no '+info+'\n')
        child.stdin.write('exit\n')
        child.stdin.write('exit\n')
		

    def setmwip(self,ip):
        ip_str = "vtysh -c 'conf t'  -c 'manager-ui ip %s' -c 'exit'"%(ip)
        commands.getoutput(ip_str)

    # def setdpiip(self,ip,mask,gateway):
    #     #get new ip
    #     if mask.find('.') == -1:
    #         strcount = mask
    #     else:
    #         count_bit = lambda bin_str: len([i for i in bin_str if i=='1'])
    #         mask_splited = mask.split('.')
    #         mask_count = [count_bit(bin(int(i))) for i in mask_splited]
    #         mcount = sum(mask_count)
    #         strcount='%d' %mcount
    #     new_str = 'ip address ' + ip+'/'+strcount+'\n'
    #     new_route = "ip route 0.0.0.0/0 "+gateway+'\n'
    #     print new_route
    #
    #     subprocess.Popen(['vtysh', '-c', 'config t', '-c', 'interface agl0', '-c', new_str])
    #     time.sleep(1)
    #     self.deldefaultroute()
    #     time.sleep(5)
    #     subprocess.Popen(['vtysh', '-c', 'config t','-c',new_route])
    #     os.system("route add default gw "+gateway)
        
    def get_error_dict(self, ip):
        error_dict = {"% Command incomplete.": u"不完整的命令",
                      "% Malformed address": u"地址格式不正确",
                      "ERROR: Interface eth6 is not exist.": u"接口不存在",
                      "% Can't find address": u"删除时没有找到该地址",
                      "Same IP address '{}' with existing interface 'agl0'. ".format(ip): u"管理口存在相同的IP",
                      "IP address '{}' conflict with existing IP address at interface 'agl0'. ".format(
                          ip): u"管理口存在相同网段的IP",
                      "Can not assign IP address or netmask to 0.": u"子网掩码是0",
                      "Invalid IP address netmask '%d'.": u"无效的IP地址掩码",
                      "can not set multicasting or broadcasting  IP address.": u"不能配置组播或广播地址",
                      "% Can't set interface IP address: {}".format(ip): u"设置IP失败"}
        return error_dict

    def setdpiip(self,ip,mask,gateway):
        #get new ip
        if mask.find('.') == -1:
            strcount = mask
        else:
            count_bit = lambda bin_str: len([i for i in bin_str if i=='1'])
            mask_splited = mask.split('.')
            mask_count = [count_bit(bin(int(i))) for i in mask_splited]
            mcount = sum(mask_count)
            strcount='%d' %mcount
        new_str = 'ip address ' + ip+'/'+strcount+'\n'
        eip = ip+'/'+strcount
        # new_route = "ip route 0.0.0.0/0 "+gateway+'\n'
        # print new_route

        # subprocess.Popen(['vtysh', '-c', 'config t', '-c', 'interface agl0', '-c', new_str])
        status = 0
        error_dict = self.get_error_dict(eip)
        cmd_str = "vtysh -c 'conf t' -c 'interface agl0' -c '{}'".format(new_str)
        # current_app.logger.info("++++++++++before commands command str:" + cmd_str)
        res = commands.getoutput(cmd_str)
        # current_app.logger.info("----------after commands command res:" + res if res else "res is null")
        if res:
            if res in error_dict:
                # current_app.logger.info("error dict return entered")
                # return jsonify({"status": status, "msg": error_dict[res]})
                return 0, error_dict[res]

        cmd_str = "/app/bin/update_interfaces 2 {}".format(gateway)
        os.system(cmd_str)
        time.sleep(1)
        # self.deldefaultroute()
        del_str = "ip route delete default dev agl0"
        os.system(del_str)
        time.sleep(5)
        # subprocess.Popen(['vtysh', '-c', 'config t','-c',new_route])
        # os.system("route add default gw "+gateway)
        os.system("ip route add default via {} dev agl0".format(gateway))
        return 1, "success"


    def setdpiflag(self,flag):
        mode_cmd = 'dpi_management mode self'
        if flag == 0:
            mode_cmd = 'dpi_management mode centralize'
        child = subprocess.Popen(['vtysh', '-c', 'config t', '-c', mode_cmd, '-c','write file'])
        child.wait()

    def getdpiinfo(self):
        #get kev-c200 ip
        res = commands.getoutput('ifconfig agl0')
        start_res = res.find('inet addr:')
        stop_res = res.find('Bcast')
        start = start_res+10
        stop = stop_res-2
        dpiip = res[start:stop]

        #get product
        child = subprocess.Popen('vtysh',shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        child.stdin.write('configure terminal\n')
        child.stdin.write('show version\n')
        child.stdin.write('exit\n')
        child.stdin.write('exit\n')
        res_out = child.stdout.read()
        pro_start = res_out.find('Product')
        pro_start = pro_start+10
        pro_end = res_out.find('\n',pro_start)
        pro_info = res_out[pro_start:pro_end]

        #get version
        ver_start = res_out.find('Version')
        ver_start = ver_start+10
        ver_end = res_out.find('\n',ver_start)
        ver_info = res_out[ver_start:ver_end]
        ver_info = "-".join(ver_info.split("-")[:3])

        #get sn info
        sn_start = res_out.find('Box S/N')
        sn_start = sn_start+10
        sn_end = res_out.find('\n',sn_start)
        sn_info = res_out[sn_start:sn_end]

        #get mwip
        child = subprocess.Popen('vtysh',shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        child.stdin.write('configure terminal\n')
        child.stdin.write('show run\n')
        child.stdin.write('exit\n')
        child.stdin.write('exit\n')
        mw_res = child.stdout.read()
        if mw_res.find('manager-ui ip ') != -1:
            mw_start = mw_res.find('manager-ui ip ')
            mw_start = mw_start + len('manager-ui ip ')
        else:
            mw_start = mw_res.find('manager-ui host IstuaryOS ip ')
            mw_start = mw_start + len('manager-ui host IstuaryOS ip ')
        mw_end = mw_res.find('\n',mw_start)
        mw_ip = mw_res[mw_start:mw_end]
        return dpiip,pro_info,ver_info,sn_info,mw_ip