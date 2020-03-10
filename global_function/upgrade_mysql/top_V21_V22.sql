DROP TABLE IF EXISTS `topdevice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `topdevice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name`  varchar(64),
  `ip` varchar(64),
  `mac` varchar(32),
  `proto` longtext DEFAULT NULL,
  `dev_type` int(11) DEFAULT NULL,
  `is_study` int(11) DEFAULT 0,
  `dev_interface` int(11) DEFAULT 0,
  `dev_desc` varchar(64),
  `is_topo` int(11) DEFAULT 0,
  `category_info` varchar(128),
  `is_live` int(11) DEFAULT 1,
  `is_unknown` int(11) DEFAULT 0,
  `dev_mode` varchar(64) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=MYISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `topdevice`
--

LOCK TABLES `topdevice` WRITE;
/*!40000 ALTER TABLE `topdevice` DISABLE KEYS */;
/*!40000 ALTER TABLE `topdevice` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Table structure for table `topshow`
--

DROP TABLE IF EXISTS `topshow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `topshow` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `xml_info`  longtext,
  PRIMARY KEY (`id`)
) ENGINE=MYISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `topshow`
--

LOCK TABLES `topshow` WRITE;
/*!40000 ALTER TABLE `topshow` DISABLE KEYS */;
insert into `topshow` values (1,'');
/*!40000 ALTER TABLE `topshow` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Table structure for table `top_config`
--

DROP TABLE IF EXISTS `top_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `top_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `check_time`  TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=MYISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `top_config`
--

LOCK TABLES `top_config` WRITE;
/*!40000 ALTER TABLE `top_config` DISABLE KEYS */;
insert into `top_config` values (1,1);
/*!40000 ALTER TABLE `top_config` ENABLE KEYS */;
UNLOCK TABLES;


DROP TABLE IF EXISTS `incidentstat_bydev`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `incidentstat_bydev` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `icd_count` int(11) UNSIGNED DEFAULT 0,
  `icd_bl_count` int(11) UNSIGNED DEFAULT 0,
  `icd_wl_count` int(11) UNSIGNED DEFAULT 0,
  `icd_im_count` int(11) UNSIGNED DEFAULT 0,
  `icd_flow_count` int(11) UNSIGNED DEFAULT 0,
  `icd_mf_count` int(11) UNSIGNED DEFAULT 0,
  `icd_dev_count` int(11) UNSIGNED DEFAULT 0,
  `read` int(11) UNSIGNED DEFAULT 0,
  `ip` varchar(64) DEFAULT '',
  `mac` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  index(`ip`)
) ENGINE=MYISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `incidentstat_bydev`
--

LOCK TABLES `incidentstat_bydev` WRITE;
/*!40000 ALTER TABLE `incidentstat_bydev` DISABLE KEYS */;
/*!40000 ALTER TABLE `incidentstat_bydev` ENABLE KEYS */;
UNLOCK TABLES;

--
-- increase the statictis, when insert one incident
--
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
    ElSE
        update incidentstat_bydev set incidentstat_bydev.icd_dev_count = incidentstat_bydev.icd_dev_count +1 where (ip=@sip and mac=@smac);
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
    ElSE
        insert into incidentstat_bydev (icd_count,icd_dev_count,ip,mac) values(1,1,@sip,@smac);
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
    ElSE
        update incidentstat_bydev set incidentstat_bydev.icd_dev_count = incidentstat_bydev.icd_dev_count +1 where (ip=@dip and mac=@dmac);
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
    ElSE
        insert into incidentstat_bydev (icd_count,icd_dev_count,ip,mac) values(1,1,@dip,@dmac);
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
    ElSE
        update incidentstat_bydev set incidentstat_bydev.icd_count = incidentstat_bydev.icd_count - 1,incidentstat_bydev.icd_dev_count = incidentstat_bydev.icd_dev_count - 1,incidentstat_bydev.read = incidentstat_bydev.read - status where (ip=@sip and mac=@smac) or (ip=@dip and mac=@dmac);
END CASE;
end ||
delimiter ;
--
-- increase the statictis of read status, when mark the status of one incident
--
delimiter ||
drop procedure if exists pr_mark_incident_is_read;
create procedure pr_mark_incident_is_read(IN timestamp varchar(30), IN sourceIp longtext, IN destinationIp longtext, IN sourceMac longtext, IN destinationMac longtext, IN old_status int, IN new_status int)
begin
if old_status != new_status and new_status = 1 then
set @dt=timestamp;
update incidentstat set incidentstat.read = incidentstat.read + 1 where incidentstat.timestamp=@dt;  
set @sip=if(LENGTH(sourceIp),sourceIp,'') ;
set @dip=if(LENGTH(destinationIp),destinationIp,'') ;
set @smac=sourceMac ;
set @dmac=destinationMac;
update incidentstat_bydev set incidentstat_bydev.read = incidentstat_bydev.read +1 where (ip=@sip and mac=@smac) or (ip=@dip and mac=@dmac) ; 
end if; 
end ||
delimiter ;

delimiter ||     
drop trigger if exists statement_trigger_delete_status_statictis|| 
create trigger statement_trigger_delete_status_statictis
before delete on incidents
for each row
begin
if @g_has_delete_statistic is null then
	call pr_decrease_incident_stat(old.timestamp,old.sourceIp,old.destinationIp,old.sourceMac,old.destinationMac,old.status,old.signatureName); 
elseif @g_has_delete_statistic = 0 then
	delete from incidentstat;
	delete from incidentstat_bydev;
	set @g_has_delete_statistic=1;
end if;
end ||
delimiter ;

delimiter ||     
drop trigger if exists statement_trigger_update_status_statictis|| 
create trigger statement_trigger_update_status_statictis
before update on incidents
for each row
begin
if @g_has_update_statistic <> 1 then
update incidentstat set incidentstat.read = incidentstat.count;
update incidentstat_bydev set incidentstat_bydev.read = incidentstat_bydev.count;
set @g_has_update_statistic=1;
end if;
end ||
delimiter ;

delimiter ||     
drop trigger if exists tr_increase_incident_stat_0|| 
CREATE TRIGGER `tr_increase_incident_stat_0` AFTER INSERT ON `incidents_0`
FOR EACH ROW begin 
call pr_increase_incident_stat(new.timestamp,new.sourceIp,new.destinationIp,new.sourceMac,new.destinationMac,new.signatureName);
end ||
delimiter ;

delimiter ||     
drop trigger if exists tr_mark_incident_is_read_0||  
CREATE TRIGGER `tr_mark_incident_is_read_0` AFTER UPDATE ON `incidents_0`
FOR EACH ROW 
begin 
call pr_mark_incident_is_read(old.timestamp,old.sourceIp,old.destinationIp,old.sourceMac,old.destinationMac,old.status,new.status); 
end ||
delimiter ;	

delimiter ||     
drop trigger if exists tr_increase_incident_stat_1|| 
CREATE TRIGGER `tr_increase_incident_stat_1` AFTER INSERT ON `incidents_1`
FOR EACH ROW begin 
call pr_increase_incident_stat(new.timestamp,new.sourceIp,new.destinationIp,new.sourceMac,new.destinationMac,new.signatureName);
end ||
delimiter ;

delimiter ||     
drop trigger if exists tr_mark_incident_is_read_1||  
CREATE TRIGGER `tr_mark_incident_is_read_1` AFTER UPDATE ON `incidents_1`
FOR EACH ROW 
begin 
call pr_mark_incident_is_read(old.timestamp,old.sourceIp,old.destinationIp,old.sourceMac,old.destinationMac,old.status,new.status); 
end ||
delimiter ;	


delimiter ||     
drop trigger if exists tr_increase_incident_stat_2|| 
CREATE TRIGGER `tr_increase_incident_stat_2` AFTER INSERT ON `incidents_2`
FOR EACH ROW begin 
call pr_increase_incident_stat(new.timestamp,new.sourceIp,new.destinationIp,new.sourceMac,new.destinationMac,new.signatureName);
end ||
delimiter ;

delimiter ||     
drop trigger if exists tr_mark_incident_is_read_2||  
CREATE TRIGGER `tr_mark_incident_is_read_2` AFTER UPDATE ON `incidents_2`
FOR EACH ROW 
begin 
call pr_mark_incident_is_read(old.timestamp,old.sourceIp,old.destinationIp,old.sourceMac,old.destinationMac,old.status,new.status); 
end ||
delimiter ;	

delimiter ||     
drop trigger if exists tr_increase_incident_stat_3|| 
CREATE TRIGGER `tr_increase_incident_stat_3` AFTER INSERT ON `incidents_3`
FOR EACH ROW begin 
call pr_increase_incident_stat(new.timestamp,new.sourceIp,new.destinationIp,new.sourceMac,new.destinationMac,new.signatureName);
end ||
delimiter ;

delimiter ||     
drop trigger if exists tr_mark_incident_is_read_3||  
CREATE TRIGGER `tr_mark_incident_is_read_3` AFTER UPDATE ON `incidents_3`
FOR EACH ROW 
begin 
call pr_mark_incident_is_read(old.timestamp,old.sourceIp,old.destinationIp,old.sourceMac,old.destinationMac,old.status,new.status); 
end ||
delimiter ;	

delimiter ||     
drop trigger if exists tr_increase_incident_stat_4|| 
CREATE TRIGGER `tr_increase_incident_stat_4` AFTER INSERT ON `incidents_4`
FOR EACH ROW begin 
call pr_increase_incident_stat(new.timestamp,new.sourceIp,new.destinationIp,new.sourceMac,new.destinationMac,new.signatureName);
end ||
delimiter ;

delimiter ||     
drop trigger if exists tr_mark_incident_is_read_4||  
CREATE TRIGGER `tr_mark_incident_is_read_4` AFTER UPDATE ON `incidents_4`
FOR EACH ROW 
begin 
call pr_mark_incident_is_read(old.timestamp,old.sourceIp,old.destinationIp,old.sourceMac,old.destinationMac,old.status,new.status); 
end ||
delimiter ;	

delimiter ||     
drop trigger if exists tr_increase_incident_stat_5|| 
CREATE TRIGGER `tr_increase_incident_stat_5` AFTER INSERT ON `incidents_5`
FOR EACH ROW begin 
call pr_increase_incident_stat(new.timestamp,new.sourceIp,new.destinationIp,new.sourceMac,new.destinationMac,new.signatureName);
end ||
delimiter ;

delimiter ||     
drop trigger if exists tr_mark_incident_is_read_5||  
CREATE TRIGGER `tr_mark_incident_is_read_5` AFTER UPDATE ON `incidents_5`
FOR EACH ROW 
begin 
call pr_mark_incident_is_read(old.timestamp,old.sourceIp,old.destinationIp,old.sourceMac,old.destinationMac,old.status,new.status); 
end ||
delimiter ;	

delimiter ||     
drop trigger if exists tr_increase_incident_stat_6|| 
CREATE TRIGGER `tr_increase_incident_stat_6` AFTER INSERT ON `incidents_6`
FOR EACH ROW begin 
call pr_increase_incident_stat(new.timestamp,new.sourceIp,new.destinationIp,new.sourceMac,new.destinationMac,new.signatureName);
end ||
delimiter ;

delimiter ||     
drop trigger if exists tr_mark_incident_is_read_6||  
CREATE TRIGGER `tr_mark_incident_is_read_6` AFTER UPDATE ON `incidents_6`
FOR EACH ROW 
begin 
call pr_mark_incident_is_read(old.timestamp,old.sourceIp,old.destinationIp,old.sourceMac,old.destinationMac,old.status,new.status); 
end ||
delimiter ;	


delimiter ||     
drop trigger if exists tr_increase_incident_stat_7|| 
CREATE TRIGGER `tr_increase_incident_stat_7` AFTER INSERT ON `incidents_7`
FOR EACH ROW begin 
call pr_increase_incident_stat(new.timestamp,new.sourceIp,new.destinationIp,new.sourceMac,new.destinationMac,new.signatureName);
end ||
delimiter ;

delimiter ||     
drop trigger if exists tr_mark_incident_is_read_7||  
CREATE TRIGGER `tr_mark_incident_is_read_7` AFTER UPDATE ON `incidents_7`
FOR EACH ROW 
begin 
call pr_mark_incident_is_read(old.timestamp,old.sourceIp,old.destinationIp,old.sourceMac,old.destinationMac,old.status,new.status); 
end ||
delimiter ;	

delimiter ||     
drop trigger if exists tr_increase_incident_stat_8|| 
CREATE TRIGGER `tr_increase_incident_stat_8` AFTER INSERT ON `incidents_8`
FOR EACH ROW begin 
call pr_increase_incident_stat(new.timestamp,new.sourceIp,new.destinationIp,new.sourceMac,new.destinationMac,new.signatureName);
end ||
delimiter ;

delimiter ||     
drop trigger if exists tr_mark_incident_is_read_8||  
CREATE TRIGGER `tr_mark_incident_is_read_8` AFTER UPDATE ON `incidents_8`
FOR EACH ROW 
begin 
call pr_mark_incident_is_read(old.timestamp,old.sourceIp,old.destinationIp,old.sourceMac,old.destinationMac,old.status,new.status); 
end ||
delimiter ;	


delimiter ||     
drop trigger if exists tr_increase_incident_stat_9|| 
CREATE TRIGGER `tr_increase_incident_stat_9` AFTER INSERT ON `incidents_9`
FOR EACH ROW begin 
call pr_increase_incident_stat(new.timestamp,new.sourceIp,new.destinationIp,new.sourceMac,new.destinationMac,new.signatureName);
end ||
delimiter ;

delimiter ||     
drop trigger if exists tr_mark_incident_is_read_9||  
CREATE TRIGGER `tr_mark_incident_is_read_9` AFTER UPDATE ON `incidents_9`
FOR EACH ROW 
begin 
call pr_mark_incident_is_read(old.timestamp,old.sourceIp,old.destinationIp,old.sourceMac,old.destinationMac,old.status,new.status); 
end ||
delimiter ;	