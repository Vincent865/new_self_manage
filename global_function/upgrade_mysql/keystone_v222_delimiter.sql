-- MySQL dump 10.13  Distrib 5.6.31, for linux-glibc2.5 (x86_64)
-- Host: localhost    Database: keystone
-- ------------------------------------------------------
-- Server version	5.6.31

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- increase the statictis, when insert one incident
--

delimiter $
drop EVENT if exists limitinfo1;
CREATE EVENT limitinfo1 ON SCHEDULE EVERY 10 SECOND DO IF (select count(*) from da_31992_data_acquire_1) > 2000000 then delete from da_31992_data_acquire_1 limit 10000;END IF $
delimiter ;

delimiter $
drop EVENT if exists limitinfo2;
CREATE EVENT limitinfo2 ON SCHEDULE EVERY 10 SECOND DO IF (select count(*) from da_31992_data_acquire_2) > 2000000 then delete from da_31992_data_acquire_2 limit 10000;END IF $
delimiter ;

delimiter $
drop EVENT if exists limitinfo3;
CREATE EVENT limitinfo3 ON SCHEDULE EVERY 10 SECOND DO IF (select count(*) from da_31992_data_acquire_3) > 2000000 then delete from da_31992_data_acquire_3 limit 10000;END IF $
delimiter ;

delimiter $
drop EVENT if exists limitinfo4;
CREATE EVENT limitinfo4 ON SCHEDULE EVERY 10 SECOND DO IF (select count(*) from da_31992_data_acquire_4) > 2000000 then delete from da_31992_data_acquire_4 limit 10000;END IF $
delimiter ;

delimiter $
drop EVENT if exists limitinfo5;
CREATE EVENT limitinfo5 ON SCHEDULE EVERY 10 SECOND DO IF (select count(*) from da_31992_data_acquire_5) > 2000000 then delete from da_31992_data_acquire_5 limit 10000;END IF $
delimiter ;

delimiter $
drop EVENT if exists limitinfo6;
CREATE EVENT limitinfo6 ON SCHEDULE EVERY 10 SECOND DO IF (select count(*) from da_31992_data_acquire_6) > 2000000 then delete from da_31992_data_acquire_6 limit 10000;END IF $
delimiter ;

delimiter $
drop EVENT if exists limitinfo7;
CREATE EVENT limitinfo7 ON SCHEDULE EVERY 10 SECOND DO IF (select count(*) from da_31992_data_acquire_7) > 2000000 then delete from da_31992_data_acquire_7 limit 10000;END IF $
delimiter ;

delimiter $
drop EVENT if exists limitinfo8;
CREATE EVENT limitinfo8 ON SCHEDULE EVERY 10 SECOND DO IF (select count(*) from da_31992_data_acquire_8) > 2000000 then delete from da_31992_data_acquire_8 limit 10000;END IF $
delimiter ;

delimiter $
drop EVENT if exists limitinfo9;
CREATE EVENT limitinfo9 ON SCHEDULE EVERY 10 SECOND DO IF (select count(*) from da_31992_data_acquire_9) > 2000000 then delete from da_31992_data_acquire_9 limit 10000;END IF $
delimiter ;

delimiter $
drop EVENT if exists limitinfo10;
CREATE EVENT limitinfo10 ON SCHEDULE EVERY 10 SECOND DO IF (select count(*) from da_31992_data_acquire_10) > 2000000 then delete from da_31992_data_acquire_10 limit 10000;END IF $
delimiter ;

delimiter $
drop EVENT if exists limitinfo11;
CREATE EVENT limitinfo11 ON SCHEDULE EVERY 10 SECOND DO IF (select count(*) from da_31992_data_acquire_11) > 2000000 then delete from da_31992_data_acquire_11 limit 10000;END IF $
delimiter ;

delimiter $
drop EVENT if exists limitinfo12;
CREATE EVENT limitinfo12 ON SCHEDULE EVERY 10 SECOND DO IF (select count(*) from da_31992_data_acquire_12) > 2000000 then delete from da_31992_data_acquire_12 limit 10000;END IF $
delimiter ;

delimiter $
drop EVENT if exists delete_month;
CREATE  EVENT  delete_month
ON  SCHEDULE  EVERY  1  MONTH  STARTS DATE_ADD(DATE_ADD(DATE_SUB(CURDATE(),INTERVAL DAY(CURDATE())-1 DAY), INTERVAL 1 MONTH),INTERVAL 0 HOUR)
ON  COMPLETION  PRESERVE  ENABLE
DO
BEGIN
set @asql = CONCAT("TRUNCATE TABLE da_31992_data_acquire_",MONTH(CURDATE()),"");
prepare stml from @asql;
EXECUTE stml;
END $
delimiter ;


delimiter ||
drop procedure if exists pr_increase_incident_stat;
create procedure pr_increase_incident_stat(IN timestamp varchar(30), IN sourceIp longtext, IN destinationIp longtext, IN sourceMac longtext, IN destinationMac longtext, IN signatureName longtext)
begin
set @dt=timestamp;
update incidentstat set incidentstat.count = incidentstat.count +1 where incidentstat.timestamp=@dt;
if row_count() = 0 then
insert into incidentstat(count,timestamp) values(1,@dt);
end if;
set @sip=if(LENGTH(sourceIp),sourceIp,'') ;
set @dip=if(LENGTH(destinationIp),destinationIp,'') ;
set @smac=sourceMac ;
set @dmac=destinationMac;
update incidentstat_bydev set incidentstat_bydev.icd_count = incidentstat_bydev.icd_count +1 where (ip=@sip and mac=@smac);
set @icd_type=CONVERT(signatureName,UNSIGNED);
CASE @icd_type
    WHEN 1 THEN
        update incidentstat_bydev set incidentstat_bydev.icd_wl_count = incidentstat_bydev.icd_wl_count +1 where (ip=@sip and mac=@smac);
    WHEN 2 THEN
        update incidentstat_bydev set incidentstat_bydev.icd_bl_count = incidentstat_bydev.icd_bl_count +1 where (ip=@sip and mac=@smac);
    WHEN 3 THEN
        update incidentstat_bydev set incidentstat_bydev.icd_im_count = incidentstat_bydev.icd_im_count +1 where (ip=@sip and mac=@smac);
    WHEN 4 THEN
        update incidentstat_bydev set incidentstat_bydev.icd_flow_count = incidentstat_bydev.icd_flow_count +1 where (ip=@sip and mac=@smac);
    WHEN 5 THEN
        update incidentstat_bydev set incidentstat_bydev.icd_mf_count = incidentstat_bydev.icd_mf_count +1 where (ip=@sip and mac=@smac);
    WHEN 6 THEN
        update incidentstat_bydev set incidentstat_bydev.icd_dev_count = incidentstat_bydev.icd_dev_count +1 where (ip=@sip and mac=@smac);
    ElSE
        update incidentstat_bydev set incidentstat_bydev.icd_pcap_count = incidentstat_bydev.icd_pcap_count +1 where (ip=@sip and mac=@smac);
END CASE;
if row_count() = 0 then
CASE @icd_type
    WHEN 1 THEN
        insert into incidentstat_bydev (icd_count,icd_wl_count,ip,mac) values(1,1,@sip,@smac);
    WHEN 2 THEN
        insert into incidentstat_bydev (icd_count,icd_bl_count,ip,mac) values(1,1,@sip,@smac);
    WHEN 3 THEN
        insert into incidentstat_bydev (icd_count,icd_im_count,ip,mac) values(1,1,@sip,@smac);
    WHEN 4 THEN
        insert into incidentstat_bydev (icd_count,icd_flow_count,ip,mac) values(1,1,@sip,@smac);
    WHEN 5 THEN
        insert into incidentstat_bydev (icd_count,icd_mf_count,ip,mac) values(1,1,@sip,@smac);
    WHEN 6 THEN
        insert into incidentstat_bydev (icd_count,icd_dev_count,ip,mac) values(1,1,@sip,@smac);
    ElSE
        insert into incidentstat_bydev (icd_count,icd_pcap_count,ip,mac) values(1,1,@sip,@smac);
END CASE;
end if;
update incidentstat_bydev set incidentstat_bydev.icd_count = incidentstat_bydev.icd_count +1 where (ip=@dip and mac=@dmac) ;
CASE @icd_type
    WHEN 1 THEN
        update incidentstat_bydev set incidentstat_bydev.icd_wl_count = incidentstat_bydev.icd_wl_count +1 where (ip=@dip and mac=@dmac);
    WHEN 2 THEN
        update incidentstat_bydev set incidentstat_bydev.icd_bl_count = incidentstat_bydev.icd_bl_count +1 where (ip=@dip and mac=@dmac);
    WHEN 3 THEN
        update incidentstat_bydev set incidentstat_bydev.icd_im_count = incidentstat_bydev.icd_im_count +1 where (ip=@dip and mac=@dmac);
    WHEN 4 THEN
        update incidentstat_bydev set incidentstat_bydev.icd_flow_count = incidentstat_bydev.icd_flow_count +1 where (ip=@dip and mac=@dmac);
    WHEN 5 THEN
        update incidentstat_bydev set incidentstat_bydev.icd_mf_count = incidentstat_bydev.icd_mf_count +1 where (ip=@dip and mac=@dmac);
    WHEN 6 THEN
        update incidentstat_bydev set incidentstat_bydev.icd_dev_count = incidentstat_bydev.icd_dev_count +1 where (ip=@dip and mac=@dmac);
    ElSE
        update incidentstat_bydev set incidentstat_bydev.icd_pcap_count = incidentstat_bydev.icd_pcap_count +1 where (ip=@dip and mac=@dmac);
END CASE;
if row_count() = 0 then
CASE @icd_type
    WHEN 1 THEN
        insert into incidentstat_bydev (icd_count,icd_wl_count,ip,mac) values(1,1,@dip,@dmac);
    WHEN 2 THEN
        insert into incidentstat_bydev (icd_count,icd_bl_count,ip,mac) values(1,1,@dip,@dmac);
    WHEN 3 THEN
        insert into incidentstat_bydev (icd_count,icd_im_count,ip,mac) values(1,1,@dip,@dmac);
    WHEN 4 THEN
        insert into incidentstat_bydev (icd_count,icd_flow_count,ip,mac) values(1,1,@dip,@dmac);
    WHEN 5 THEN
        insert into incidentstat_bydev (icd_count,icd_mf_count,ip,mac) values(1,1,@dip,@dmac);
    WHEN 6 THEN
        insert into incidentstat_bydev (icd_count,icd_dev_count,ip,mac) values(1,1,@dip,@dmac);
    ElSE
        insert into incidentstat_bydev (icd_count,icd_pcap_count,ip,mac) values(1,1,@dip,@dmac);
END CASE;
end if;
end ||
delimiter ;
--
-- decrease the statictis, when delete one incident
--
delimiter ||
drop procedure if exists pr_decrease_incident_stat;
create procedure pr_decrease_incident_stat(IN timestamp varchar(30), IN sourceIp longtext, IN destinationIp longtext, IN sourceMac longtext, IN destinationMac longtext, IN status int, IN signatureName longtext)
begin
set @dt=timestamp;
set @icd_type=CONVERT(signatureName,UNSIGNED);
update incidentstat set incidentstat.count = incidentstat.count - 1, incidentstat.read = incidentstat.read - status where incidentstat.timestamp=@dt;
set @sip=if(LENGTH(sourceIp),sourceIp,'');
set @dip=if(LENGTH(destinationIp),destinationIp,'');
set @smac=sourceMac ;
set @dmac=destinationMac;
-- update incidentstat_bydev set incidentstat_bydev.count = incidentstat_bydev.count - 1,incidentstat_bydev.read = incidentstat_bydev.read - status where (ip=@sip and mac=@smac) or (ip=@dip and mac=@dmac) ;
CASE @icd_type
    WHEN 1 THEN
        update incidentstat_bydev set incidentstat_bydev.icd_count = incidentstat_bydev.icd_count - 1,incidentstat_bydev.icd_wl_count = incidentstat_bydev.icd_wl_count - 1,incidentstat_bydev.read = incidentstat_bydev.read - status where (ip=@sip and mac=@smac) or (ip=@dip and mac=@dmac);
    WHEN 2 THEN
        update incidentstat_bydev set incidentstat_bydev.icd_count = incidentstat_bydev.icd_count - 1,incidentstat_bydev.icd_bl_count = incidentstat_bydev.icd_bl_count - 1,incidentstat_bydev.read = incidentstat_bydev.read - status where (ip=@sip and mac=@smac) or (ip=@dip and mac=@dmac);
    WHEN 3 THEN
        update incidentstat_bydev set incidentstat_bydev.icd_count = incidentstat_bydev.icd_count - 1,incidentstat_bydev.icd_im_count = incidentstat_bydev.icd_im_count - 1,incidentstat_bydev.read = incidentstat_bydev.read - status where (ip=@sip and mac=@smac) or (ip=@dip and mac=@dmac);
    WHEN 4 THEN
        update incidentstat_bydev set incidentstat_bydev.icd_count = incidentstat_bydev.icd_count - 1,incidentstat_bydev.icd_flow_count = incidentstat_bydev.icd_flow_count - 1,incidentstat_bydev.read = incidentstat_bydev.read - status where (ip=@sip and mac=@smac) or (ip=@dip and mac=@dmac);
    WHEN 5 THEN
        update incidentstat_bydev set incidentstat_bydev.icd_count = incidentstat_bydev.icd_count - 1,incidentstat_bydev.icd_mf_count = incidentstat_bydev.icd_mf_count - 1,incidentstat_bydev.read = incidentstat_bydev.read - status where (ip=@sip and mac=@smac) or (ip=@dip and mac=@dmac);
    WHEN 6 THEN
        update incidentstat_bydev set incidentstat_bydev.icd_count = incidentstat_bydev.icd_count - 1,incidentstat_bydev.icd_dev_count = incidentstat_bydev.icd_dev_count - 1,incidentstat_bydev.read = incidentstat_bydev.read - status where (ip=@sip and mac=@smac) or (ip=@dip and mac=@dmac);
    ElSE
        update incidentstat_bydev set incidentstat_bydev.icd_count = incidentstat_bydev.icd_count - 1,incidentstat_bydev.icd_pcap_count = incidentstat_bydev.icd_pcap_count - 1,incidentstat_bydev.read = incidentstat_bydev.read - status where (ip=@sip and mac=@smac) or (ip=@dip and mac=@dmac);
END CASE;
end ||
delimiter ;