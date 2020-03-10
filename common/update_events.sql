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