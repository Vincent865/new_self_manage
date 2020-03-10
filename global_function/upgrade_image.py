__author__ = 'yxs'

import logging
import traceback
import subprocess
import os
import re
#from log_config import *
import time
import commands

#LogConfig('upgrade_image.log')
logger = logging.getLogger('flask_engine_log')


class UpgradeImage():
    def __init__(self):
        self.image_dir = "/app/upgrade/"
        self.image_tmp_dir = "/app/upgrade_tmp/"
        self.package_upgrade_flag = False

    def upgrade_process(self, data):
        result=True
        logger.info("---------start upgrade image...---------")
        
        # check image version
        result,versionerr = self.check_image_version(message.imageVersion)
        if result is False:
            return result

        #check image
        if self.check_image_sign(file) is False:
            return result

        #update image file
        if self.update_image_file(file) is False:
            return result

        return result
        # wait 20s for web display
        time.sleep(20)
        command = "reboot"
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)


    def check_image_version(self,version):
        local_ver=""
        result=True
        error="successful"
        update_ver=version[:23]
        time.sleep(2)
        for line in open("/usr/local/etc/southwest_engine/version.autogen"):
            local_ver=line[:23]
            break
        logger.info("local version is :"+local_ver+" updating version is: "+update_ver)
        if update_ver == local_ver:
            logger.error("Local version equals to upgrading version")
        #check uboot is updated
        result=False
        command="get_eeprom read all"
        handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for line in handle.stdout.readlines():
            if "bootfile" in line:
                result=True
                logger.info("bootfile in uboot, line content is:"+line)
                break
        if result is False:
            error="Please update uboot first"
            logger.error("Please update uboot first")
            return result,error
        result=False
        command="cat /proc/cmdline"
        handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for line in handle.stdout.readlines():
            if "bootdevice" in line:
                result=True
                logger.info("bootdevice in uboot, line content is:"+line)
                break
        if result is False:
            error="Please update uboot first"
            logger.error("Please update uboot first")
            return result,error
        return result,error

    def remount_boot(self):
        mount_output = commands.getoutput('mount -v')
        lines = mount_output.split('\n')
        mount_points = map(lambda line: [line.split()[2], line.split()[0]], lines)
        mount_dict = dict(mount_points)
        mount_command = 'mount ' + mount_dict['/boot'] + ' /boot -o remount'
        logger.info('remount boot command is \"%s\"'%(mount_command))
        os.system(mount_command)

    def prepare_down_image(self):
        '''preparing download image, remount /boot partition and check disk free space'''
        #self.remount_boot()
        command = "df -m"
        handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for line in handle.stdout.readlines():
            if '/app' in line:
                try:
                    v1, v2, v3, v4, v5, v6 = line.split()
                    logger.info("/boot Partition size is " + str(v4))
                    if (int(v4) < 500):
                        logger.error("/boot Partition size is " + str(v4) + ", too small!")
                        return False
                except:
                    logger.error("str format error--" + line)


        return True

    def check_image_md5(self,file):
        os.chdir(self.image_tmp_dir)
        shcmd = "sed -n '1p' %s |awk {print'$1'}"%(file)
        result = os.popen(shcmd).read()
        get_checksum = result.split()[0]
        
        shcmd = "sed -i '1d'  %s "%(file)
        os.system(shcmd)
        
        shcmd = "md5sum %s |awk {print'$1'}"%(file)
        result = os.popen(shcmd).read()
        calc_checksum = result.split()[0]
        
        if get_checksum == calc_checksum:
            shcmd = "mkdir -p  %s"%(self.image_dir)
            os.system(shcmd)
            return True
        else:
            shcmd = "rm -f %s"%(file)
            os.system(shcmd)
            return False

        return True

    def check_image_sign(self,file):
        file_fullpath = "%s%s"%(self.image_tmp_dir,file)
        shcmd = "/usr/bin/check_sig.sh %s "%(file_fullpath)
        result = os.popen(shcmd).read()
        logger.info("check_sig.sh result" + result)
        if "Signature Verified Successfully" in result:
            if "tdhx Package Upgrade" in result:
                self.package_upgrade_flag = True
            shcmd = "mkdir -p  %s"%(self.image_dir)
            os.system(shcmd)
            return True
        else:
            shcmd = "rm -f %s"%(file)
            os.system(shcmd)
            return False

        return True

    def update_image_file(self,file):
        localfile = "package_ramfs.tgz"
        try:
            command = "rm %s*.tgz"%(self.image_dir)
            os.system(command)
            if os.path.exists("%spackage"%(self.image_dir)):
                command = "rm -rf %spackage"%(self.image_dir)
                os.system(command)
            command = "mv %s%s %s%s"%(self.image_tmp_dir,file,self.image_dir, localfile)
            os.system(command)

            os.chdir(self.image_dir)
            command = "tar zxf %s"%localfile
            os.system(command)

            if self.package_upgrade_flag == False:
                if os.path.exists("./package/firewall.gz"):
                    command = "cp -f ./package/firewall.gz /boot/boot/"
                    os.system(command)
                if os.path.exists("./package/ks-kernel64"):
                    command = "cp -f ./package/ks-kernel64 /boot/boot/"
                    os.system(command)
                if os.path.exists("./package/menu.lst"):
                    command = "cp -f ./package/menu.lst /boot/"
                    os.system(command)
                command = "touch /app/upgrade/upgrade.flag"
                os.system(command)
                command = "rm -rf package"
                os.system(command)
                return True

        except:
            logger.error(traceback.format_exc())
            return False

    def package_upgrade(self):
        if self.package_upgrade_flag:
            os.chdir(self.image_dir)  
            if os.path.exists("./package/package_upgrade.sh"):
                    command = "chmod 777 ./package/package_upgrade.sh"
                    os.system(command)
                    command = "./package/package_upgrade.sh"
                    os.system(command)
                    command = "rm -rf package"
                    os.system(command)

class UpgradeImage_MIPS():
    def __init__(self):
        self.image_dir = "/boot"

    def upgrade_process(self, data):
        result=True
        logger.info("---------start upgrade image...---------")

        # check image version
        result,versionerr = self.check_image_version(message.imageVersion)
        if result is False:
            return result

        #check image MD5
        if self.check_image_md5(file) is False:
            return result

        #update image file
        if self.update_image_file(file) is False:
            return result

        return result
        # wait 20s for web display
        time.sleep(20)
        command = "reboot"
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)


    def check_image_version(self,version):
        local_ver=""
        result=True
        error="successful"
        update_ver=version[:23]
        time.sleep(2)
        for line in open("/usr/local/etc/southwest_engine/version.autogen"):
            local_ver=line[:23]
            break
        logger.info("local version is :"+local_ver+" updating version is: "+update_ver)
        if update_ver == local_ver:
            logger.error("Local version equals to upgrading version")
        #check uboot is updated
        result=False
        command="get_eeprom read all"
        handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for line in handle.stdout.readlines():
            if "bootfile" in line:
                result=True
                logger.info("bootfile in uboot, line content is:"+line)
                break
        if result is False:
            error="Please update uboot first"
            logger.error("Please update uboot first")
            return result,error
        result=False
        command="cat /proc/cmdline"
        handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for line in handle.stdout.readlines():
            if "bootdevice" in line:
                result=True
                logger.info("bootdevice in uboot, line content is:"+line)
                break
        if result is False:
            error="Please update uboot first"
            logger.error("Please update uboot first")
            return result,error
        return result,error

    def remount_boot(self):
        mount_output = commands.getoutput('mount -v')
        lines = mount_output.split('\n')
        mount_points = map(lambda line: [line.split()[2], line.split()[0]], lines)
        mount_dict = dict(mount_points)
        mount_command = 'mount ' + mount_dict['/boot'] + ' /boot -o remount'
        logger.info('remount boot command is \"%s\"'%(mount_command))
        os.system(mount_command)

    def prepare_down_image(self):
        '''preparing download image, remount /boot partition and check disk free space'''
        self.remount_boot()
        command = "df -m"
        handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for line in handle.stdout.readlines():
            if '/boot' in line:
                try:
                    v1, v2, v3, v4, v5, v6 = line.split()
                    logger.info("/boot Partition size is " + str(v4))
                    if (int(v4) < 500):
                        logger.error("/boot Partition size is " + str(v4) + ", too small!")
                        return False
                except:
                    logger.info("str format error--" + line)


        return True

    def check_image_md5(self,file):

        os.chdir("/boot")

        command = "ShowImage " + file
        handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

        md5Result = False
        for line in handle.stdout.readlines():
            logger.info(line)
            if 'Image is correct' in line:
                md5Result = True
                break

        return md5Result

    def update_image_file(self,file):
        try:
            command = "mv " + file + " vmlinux.tmp"
            handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)


            command = "get_eeprom read all"
            handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

            for line in handle.stdout.readlines():
                if "bootfile" in line:
                    lastbootfile = re.compile("bootfile\s+:\s(.*)").findall(line)
                    if lastbootfile:
                        command = "echo " + lastbootfile[0] + " > /data/log/update_last_bootfile"
                        handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                    break

            command = "touch /data/log/dpi_need_update"
            handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)


            command = "get_eeprom write bootfile vmlinux.tmp"
            handle = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            return True

        except:
            logger.info(traceback.format_exc())
            return False
