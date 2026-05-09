-- MySQL dump 10.13  Distrib 5.7.26, for Win32 (AMD64)
--
-- Host: localhost    Database: school_mis
-- ------------------------------------------------------
-- Server version	5.7.26

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
-- Table structure for table `学籍表`
--

DROP TABLE IF EXISTS `学籍表`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `学籍表` (
  `学号` int(11) NOT NULL,
  `姓名` varchar(50) DEFAULT NULL,
  `性别` varchar(2) DEFAULT NULL,
  `所在班级` varchar(50) DEFAULT NULL,
  `照片` longblob,
  `本学期评语` text,
  `综合评语` text,
  `期中1` int(11) DEFAULT NULL,
  `期中2` int(11) DEFAULT NULL,
  `期中3` int(11) DEFAULT NULL,
  `期中4` int(11) DEFAULT NULL,
  `期中5` int(11) DEFAULT NULL,
  `期中6` int(11) DEFAULT NULL,
  `期中7` int(11) DEFAULT NULL,
  `期中8` int(11) DEFAULT NULL,
  `期中9` int(11) DEFAULT NULL,
  `期中10` int(11) DEFAULT NULL,
  `期末1` int(11) DEFAULT NULL,
  `期末2` int(11) DEFAULT NULL,
  `期末3` int(11) DEFAULT NULL,
  `期末4` int(11) DEFAULT NULL,
  `期末5` int(11) DEFAULT NULL,
  `期末6` int(11) DEFAULT NULL,
  `期末7` int(11) DEFAULT NULL,
  `期末8` int(11) DEFAULT NULL,
  `期末9` int(11) DEFAULT NULL,
  `期末10` int(11) DEFAULT NULL,
  `联系电话` varchar(20) DEFAULT NULL,
  `家庭住址` varchar(200) DEFAULT NULL,
  `户籍` varchar(100) DEFAULT NULL,
  `籍贯` varchar(100) DEFAULT NULL,
  `家长A` varchar(20) DEFAULT NULL,
  `家长A姓名` varchar(50) DEFAULT NULL,
  `家长A单位` varchar(100) DEFAULT NULL,
  `家长A电话` varchar(20) DEFAULT NULL,
  `家长B` varchar(20) DEFAULT NULL,
  `家长B姓名` varchar(50) DEFAULT NULL,
  `家长B单位` varchar(100) DEFAULT NULL,
  `家长B电话` varchar(20) DEFAULT NULL,
  `班内职务` varchar(50) DEFAULT NULL,
  `民族` varchar(20) DEFAULT NULL,
  `出生日期` date DEFAULT NULL,
  `入学日期` date DEFAULT NULL,
  `身份证号` varchar(18) DEFAULT NULL,
  PRIMARY KEY (`学号`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `学籍表`
--

LOCK TABLES `学籍表` WRITE;
/*!40000 ALTER TABLE `学籍表` DISABLE KEYS */;
/*!40000 ALTER TABLE `学籍表` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `教员表`
--

DROP TABLE IF EXISTS `教员表`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `教员表` (
  `编号` int(11) NOT NULL,
  `姓名` varchar(50) DEFAULT NULL,
  `性别` varchar(2) DEFAULT NULL,
  `照片` longblob,
  `个人简历` text,
  `民族` varchar(20) DEFAULT NULL,
  `出生日期` date DEFAULT NULL,
  `学历` varchar(20) DEFAULT NULL,
  `政治面貌` varchar(20) DEFAULT NULL,
  `参加工作时间` date DEFAULT NULL,
  `调入本校时间` date DEFAULT NULL,
  `职称` varchar(30) DEFAULT NULL,
  `职务或岗位` varchar(50) DEFAULT NULL,
  `身份证号` varchar(18) DEFAULT NULL,
  `手机号码` varchar(20) DEFAULT NULL,
  `家庭住址` varchar(200) DEFAULT NULL,
  `住宅电话` varchar(20) DEFAULT NULL,
  `籍贯` varchar(100) DEFAULT NULL,
  `户籍所在地` varchar(100) DEFAULT NULL,
  `其他资料` text,
  PRIMARY KEY (`编号`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `教员表`
--

LOCK TABLES `教员表` WRITE;
/*!40000 ALTER TABLE `教员表` DISABLE KEYS */;
/*!40000 ALTER TABLE `教员表` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `班级表`
--

DROP TABLE IF EXISTS `班级表`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `班级表` (
  `所在班级` varchar(50) NOT NULL,
  `班主任` varchar(50) DEFAULT NULL,
  `科目1` varchar(50) DEFAULT NULL,
  `科目2` varchar(50) DEFAULT NULL,
  `科目3` varchar(50) DEFAULT NULL,
  `科目4` varchar(50) DEFAULT NULL,
  `科目5` varchar(50) DEFAULT NULL,
  `科目6` varchar(50) DEFAULT NULL,
  `科目7` varchar(50) DEFAULT NULL,
  `科目8` varchar(50) DEFAULT NULL,
  `科目9` varchar(50) DEFAULT NULL,
  `科目10` varchar(50) DEFAULT NULL,
  `班级分类` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`所在班级`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `班级表`
--

LOCK TABLES `班级表` WRITE;
/*!40000 ALTER TABLE `班级表` DISABLE KEYS */;
INSERT INTO `班级表` VALUES ('一年级1班','admin','Mathematics','Chinese','English','Politics','History','Geography','Physics','Chemistry','Biology','Sports','通用');
/*!40000 ALTER TABLE `班级表` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `离校人员名单`
--

DROP TABLE IF EXISTS `离校人员名单`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `离校人员名单` (
  `学号` int(11) NOT NULL,
  `姓名` varchar(50) DEFAULT NULL,
  `性别` varchar(2) DEFAULT NULL,
  `民族` varchar(20) DEFAULT NULL,
  `出生日期` date DEFAULT NULL,
  `入学日期` date DEFAULT NULL,
  `所在班级` varchar(50) DEFAULT NULL,
  `班内职务` varchar(50) DEFAULT NULL,
  `家庭住址` varchar(200) DEFAULT NULL,
  `联系电话` varchar(20) DEFAULT NULL,
  `户籍` varchar(100) DEFAULT NULL,
  `籍贯` varchar(100) DEFAULT NULL,
  `家长A` varchar(20) DEFAULT NULL,
  `家长A姓名` varchar(50) DEFAULT NULL,
  `家长A单位` varchar(100) DEFAULT NULL,
  `家长A电话` varchar(20) DEFAULT NULL,
  `家长B` varchar(20) DEFAULT NULL,
  `家长B姓名` varchar(50) DEFAULT NULL,
  `家长B单位` varchar(100) DEFAULT NULL,
  `家长B电话` varchar(20) DEFAULT NULL,
  `照片` longblob,
  `本学期评语` text,
  `综合评语` text,
  `期中1` int(11) DEFAULT NULL,
  `期中2` int(11) DEFAULT NULL,
  `期中3` int(11) DEFAULT NULL,
  `期中4` int(11) DEFAULT NULL,
  `期中5` int(11) DEFAULT NULL,
  `期中6` int(11) DEFAULT NULL,
  `期中7` int(11) DEFAULT NULL,
  `期中8` int(11) DEFAULT NULL,
  `期中9` int(11) DEFAULT NULL,
  `期中10` int(11) DEFAULT NULL,
  `期末1` int(11) DEFAULT NULL,
  `期末2` int(11) DEFAULT NULL,
  `期末3` int(11) DEFAULT NULL,
  `期末4` int(11) DEFAULT NULL,
  `期末5` int(11) DEFAULT NULL,
  `期末6` int(11) DEFAULT NULL,
  `期末7` int(11) DEFAULT NULL,
  `期末8` int(11) DEFAULT NULL,
  `期末9` int(11) DEFAULT NULL,
  `期末10` int(11) DEFAULT NULL,
  `离校时间` date DEFAULT NULL,
  `离校原因` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`学号`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `离校人员名单`
--

LOCK TABLES `离校人员名单` WRITE;
/*!40000 ALTER TABLE `离校人员名单` DISABLE KEYS */;
/*!40000 ALTER TABLE `离校人员名单` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `管理员表`
--

DROP TABLE IF EXISTS `管理员表`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `管理员表` (
  `用户名` varchar(50) NOT NULL,
  `密码` varchar(50) NOT NULL,
  `权限` char(4) NOT NULL DEFAULT '0000',
  PRIMARY KEY (`用户名`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `管理员表`
--

LOCK TABLES `管理员表` WRITE;
/*!40000 ALTER TABLE `管理员表` DISABLE KEYS */;
INSERT INTO `管理员表` VALUES ('admin','123456','1111');
/*!40000 ALTER TABLE `管理员表` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `系统设置表`
--

DROP TABLE IF EXISTS `系统设置表`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `系统设置表` (
  `id` int(11) NOT NULL DEFAULT '1',
  `学校名称` varchar(100) DEFAULT '校务管理系统',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `系统设置表`
--

LOCK TABLES `系统设置表` WRITE;
/*!40000 ALTER TABLE `系统设置表` DISABLE KEYS */;
INSERT INTO `系统设置表` VALUES (1,'校务管理系统');
/*!40000 ALTER TABLE `系统设置表` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wage_config`
--

DROP TABLE IF EXISTS `wage_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wage_config` (
  `table_id` int(11) NOT NULL,
  `标题` varchar(100) NOT NULL,
  `项目1名称` varchar(50) DEFAULT NULL,
  `项目2名称` varchar(50) DEFAULT NULL,
  `项目3名称` varchar(50) DEFAULT NULL,
  `项目4名称` varchar(50) DEFAULT NULL,
  `项目5名称` varchar(50) DEFAULT NULL,
  `项目6名称` varchar(50) DEFAULT NULL,
  `项目7名称` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`table_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wage_config`
--

LOCK TABLES `wage_config` WRITE;
/*!40000 ALTER TABLE `wage_config` DISABLE KEYS */;
INSERT INTO `wage_config` VALUES (1,'教员工资表(表一)','基本工资','岗位津贴','绩效工资','工龄工资','其他补贴','养老保险','实发合计'),(2,'教员工资表(表二)','基本工资','岗位津贴','绩效工资','工龄工资','其他补贴','养老保险','实发合计'),(3,'教员工资表(表三)','基本工资','岗位津贴','绩效工资','工龄工资','其他补贴','养老保险','实发合计'),(4,'教员工资表(表四)','基本工资','岗位津贴','绩效工资','工龄工资','其他补贴','养老保险','实发合计'),(5,'教员工资表(表五)','基本工资','岗位津贴','绩效工资','工龄工资','其他补贴','养老保险','实发合计');
/*!40000 ALTER TABLE `wage_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wage_records`
--

DROP TABLE IF EXISTS `wage_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wage_records` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `table_id` int(11) NOT NULL,
  `姓名` varchar(50) DEFAULT NULL,
  `项目1` decimal(10,2) DEFAULT NULL,
  `项目2` decimal(10,2) DEFAULT NULL,
  `项目3` decimal(10,2) DEFAULT NULL,
  `项目4` decimal(10,2) DEFAULT NULL,
  `项目5` decimal(10,2) DEFAULT NULL,
  `项目6` decimal(10,2) DEFAULT NULL,
  `项目7` decimal(10,2) DEFAULT NULL,
  `合计` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wage_records`
--

LOCK TABLES `wage_records` WRITE;
/*!40000 ALTER TABLE `wage_records` DISABLE KEYS */;
/*!40000 ALTER TABLE `wage_records` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-05 18:44:40
