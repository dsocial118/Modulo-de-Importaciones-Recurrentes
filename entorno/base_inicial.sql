-- MySQL dump 10.13  Distrib 8.4.11, for Linux (x86_64)
--
-- Host: localhost    Database: runac
-- ------------------------------------------------------
-- Server version	8.4.11

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `runac`
--

/*!40000 DROP DATABASE IF EXISTS `runac`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `runac` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `runac`;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
INSERT INTO `auth_group` VALUES (4,'administrador_nacional'),(5,'jurisdiccion:Chaco'),(6,'jurisdiccion:Chubut'),(1,'operador_provincial'),(2,'responsable_provincial'),(3,'revisor_nacional');
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$1000000$WCaK0wycxTKr1BJnBPRkC5$QEPK+vSfLwaLtA0phsTp+xz4pDO5Sultoqs1OFTf9nY=','2026-09-16 20:42:25.411356',0,'operador','Operador provincial','','',0,1,'2026-09-08 01:22:55.505424'),(2,'pbkdf2_sha256$1000000$qZGw9R4iBq5lZJGFA4ZZD0$8m8zSIp1U4l38qMPy0v46YRoiB6GqXbltuQNsmf+5hs=','2026-09-15 12:46:27.146096',0,'responsable','Responsable provincial','','',0,1,'2026-09-08 01:22:55.892049'),(3,'pbkdf2_sha256$1000000$aGhtuTJHDfVQDl0IO522Lc$s+08aEc1mz+G0aKfb9eP7jZTgrnLycNdbWRUw9hKUe0=','2026-09-15 12:46:27.419490',0,'revisor','Revisor técnico nacional','','',0,1,'2026-09-08 01:22:56.250835'),(4,'pbkdf2_sha256$1000000$EMQQM4q0dsfdg8IvPwx7Ct$VKcoxmUSighU8DyPD7nMg6MF9abOCkG2t6sx9CPTD2Q=','2026-09-16 16:50:34.930473',1,'admin','Administrador nacional','','',1,1,'2026-09-08 01:22:56.572629');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
INSERT INTO `auth_user_groups` VALUES (7,1,1),(8,1,6),(9,2,2),(10,2,6),(11,3,3),(12,4,4);
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-09-08 01:22:49.593382'),(2,'auth','0001_initial','2026-09-08 01:22:51.881582'),(3,'admin','0001_initial','2026-09-08 01:22:52.420547'),(4,'admin','0002_logentry_remove_auto_add','2026-09-08 01:22:52.434499'),(5,'admin','0003_logentry_add_action_flag_choices','2026-09-08 01:22:52.447543'),(6,'contenttypes','0002_remove_content_type_name','2026-09-08 01:22:52.797726'),(7,'auth','0002_alter_permission_name_max_length','2026-09-08 01:22:53.012077'),(8,'auth','0003_alter_user_email_max_length','2026-09-08 01:22:53.060189'),(9,'auth','0004_alter_user_username_opts','2026-09-08 01:22:53.078907'),(10,'auth','0005_alter_user_last_login_null','2026-09-08 01:22:53.235547'),(11,'auth','0006_require_contenttypes_0002','2026-09-08 01:22:53.258122'),(12,'auth','0007_alter_validators_add_error_messages','2026-09-08 01:22:53.274468'),(13,'auth','0008_alter_user_username_max_length','2026-09-08 01:22:53.472358'),(14,'auth','0009_alter_user_last_name_max_length','2026-09-08 01:22:53.703461'),(15,'auth','0010_alter_group_name_max_length','2026-09-08 01:22:53.745754'),(16,'auth','0011_update_proxy_permissions','2026-09-08 01:22:53.761558'),(17,'auth','0012_alter_user_first_name_max_length','2026-09-08 01:22:53.938613'),(18,'sessions','0001_initial','2026-09-08 01:22:54.044106');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c1_archivo`
--

DROP TABLE IF EXISTS `runac_c1_archivo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c1_archivo` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `codigo` varchar(30) NOT NULL COMMENT 'Código estable que identifica el tipo de archivo, por ejemplo MPI, MPE o MPJ_DAE. No cambia nunca.',
  `descripcion` text COMMENT 'Descripción funcional de la información contenida en el archivo.',
  `activo` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Indica si el archivo sigue formando parte de los que se solicitan.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='La identidad del archivo. Todo lo que puede cambiar entre períodos vive en la versión.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c1_archivo`
--

LOCK TABLES `runac_c1_archivo` WRITE;
/*!40000 ALTER TABLE `runac_c1_archivo` DISABLE KEYS */;
INSERT INTO `runac_c1_archivo` VALUES (1,'DISP_PENAL','Listado de dispositivos penales',1),(2,'DISP_SCP','Listado de dispositivos de cuidado residencial',1),(3,'MPI','Nómina de medidas de protección integral',1),(4,'MPE','Nómina de medidas de protección excepcional',1),(5,'MPJ_DAE','Nómina de medidas penales juveniles',1),(9,'LEGAJO_NYA','Legajo de niñas, niños y adolescentes',1);
/*!40000 ALTER TABLE `runac_c1_archivo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c1_archivo_version`
--

DROP TABLE IF EXISTS `runac_c1_archivo_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c1_archivo_version` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `archivo_id` bigint NOT NULL COMMENT 'Archivo cuya estructura describe esta versión.',
  `numero` int NOT NULL COMMENT 'Número de versión, correlativo dentro del archivo.',
  `estado` enum('BORRADOR','VIGENTE','HISTORICA') NOT NULL DEFAULT 'BORRADOR' COMMENT 'BORRADOR: se está editando. VIGENTE: rige para el período abierto. HISTORICA: fue usada por un período anterior y no se modifica.',
  `nombre_esperado` varchar(255) NOT NULL COMMENT 'Nombre que debe tener el archivo. Puede cambiar entre versiones.',
  `titulo` varchar(255) DEFAULT NULL COMMENT 'Título que encabeza la planilla, tal como aparece en la primera fila del Excel.',
  `subtitulo` varchar(255) DEFAULT NULL COMMENT 'Subtítulo o segunda línea del encabezado, cuando la planilla lo tiene.',
  `orden_importacion` int NOT NULL COMMENT 'Orden en que debe procesarse respecto de los demás archivos de la misma versión de período.',
  `obligatorio` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Indica si la ausencia del archivo impide continuar con la importación.',
  `creada_el` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento en que se creó la versión.',
  `creada_por` varchar(150) DEFAULT NULL COMMENT 'Usuario que la creó.',
  `copiada_de` bigint DEFAULT NULL COMMENT 'Versión anterior a partir de la cual se copió para su edición.',
  `nota` text COMMENT 'Qué cambió respecto de la versión anterior.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c1_archivo_version_unica` (`archivo_id`,`numero`),
  KEY `runac_c1_archivo_version_estado` (`archivo_id`,`estado`),
  KEY `copiada_de` (`copiada_de`),
  CONSTRAINT `runac_c1_archivo_version_ibfk_1` FOREIGN KEY (`archivo_id`) REFERENCES `runac_c1_archivo` (`id`),
  CONSTRAINT `runac_c1_archivo_version_ibfk_2` FOREIGN KEY (`copiada_de`) REFERENCES `runac_c1_archivo_version` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Cada versión de la estructura de un archivo. Hojas, dimensiones, campos y reglas cuelgan de la versión, no del archivo.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c1_archivo_version`
--

LOCK TABLES `runac_c1_archivo_version` WRITE;
/*!40000 ALTER TABLE `runac_c1_archivo_version` DISABLE KEYS */;
INSERT INTO `runac_c1_archivo_version` VALUES (1,1,1,'VIGENTE','Base dispositivos PENAL modelo 20260827 desproteg.xlsx','Listado de los dispositivos penales Centros de Régimen Cerrado. MODELO PARA COMPLETAR Y ADJUNTAR',NULL,1,1,'2026-09-07 23:42:51',NULL,NULL,'Generada automáticamente a partir del Excel relevado.'),(2,2,1,'VIGENTE','Base dispositivos SCP modelo 20260827 desproteg.xlsx','Listado de dispositivos de modalidad de cuidado residencial. MODELO PARA COMPLETAR Y ADJUNTAR',NULL,2,1,'2026-09-07 23:42:52',NULL,NULL,'Generada automáticamente a partir del Excel relevado.'),(3,3,1,'VIGENTE','MPI 20260828 desproteg.xlsx','Registro NyA con Medida de Protección Integral',NULL,3,1,'2026-09-07 23:42:53',NULL,NULL,'Generada automáticamente a partir del Excel relevado.'),(4,4,1,'VIGENTE','MPE 20260901 desproteg.xlsx','Registro NyA con Medida de Protección Excepcional',NULL,4,1,'2026-09-07 23:42:53',NULL,NULL,'Generada automáticamente a partir del Excel relevado.'),(5,5,1,'VIGENTE','MPJ DAE 20260827 desproteg.xlsx','Relevamiento Dispositivos Penales Juveniles',NULL,5,1,'2026-09-07 23:42:54',NULL,NULL,'Generada automáticamente a partir del Excel relevado.'),(7,9,1,'BORRADOR','Legajo NyA 2026 09 10.xlsx',NULL,NULL,3,1,'2026-09-12 11:01:37',NULL,NULL,'Generada automáticamente a partir del Excel relevado.'),(8,4,2,'BORRADOR','MPE para SISOC 2026 09 11 Monitoreo.xlsx',NULL,NULL,5,1,'2026-09-12 11:01:39',NULL,NULL,'Generada automáticamente a partir del Excel relevado.');
/*!40000 ALTER TABLE `runac_c1_archivo_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c1_campo`
--

DROP TABLE IF EXISTS `runac_c1_campo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c1_campo` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `hoja_id` bigint NOT NULL COMMENT 'Hoja a la que pertenece el campo.',
  `dimension_id` bigint DEFAULT NULL COMMENT 'Dimensión que agrupa el campo. Puede quedar vacío cuando el campo no pertenece a una dimensión.',
  `catalogo_id` bigint DEFAULT NULL COMMENT 'Catálogo que contiene los valores permitidos para el campo. Puede quedar vacío cuando el campo no utiliza una lista cerrada.',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre técnico y estable del campo, escrito en snake_case y sin tildes ni caracteres especiales.',
  `titulo_esperado` varchar(255) NOT NULL COMMENT 'Título exacto que debe aparecer en la columna del archivo Excel.',
  `orden` int NOT NULL COMMENT 'Posición esperada de la columna dentro de la hoja.',
  `tipo_dato` enum('TEXTO','ENTERO','DECIMAL','FECHA','HORA') NOT NULL,
  `longitud_maxima` int DEFAULT NULL COMMENT 'Cantidad máxima de caracteres admitidos para campos de tipo TEXTO. Si queda vacío, la columna receptora se creará como TEXT.',
  `normalizacion` enum('SIN_NORMALIZAR','UNIVERSO','POR_ENTIDAD') NOT NULL DEFAULT 'SIN_NORMALIZAR' COMMENT 'Si los valores de este campo se unifican contra un diccionario, y con qué alcance. No afecta la importacion: es una declaracion para la normalizacion posterior.',
  `obligatorio` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Indica si el campo debe contener un valor. Las obligatoriedades condicionales se definen mediante reglas.',
  `ayuda` text COMMENT 'Texto explicativo para la confección o validación del campo.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c1_campo_index_3` (`hoja_id`,`nombre`),
  UNIQUE KEY `runac_c1_campo_index_4` (`hoja_id`,`orden`),
  KEY `dimension_id` (`dimension_id`),
  KEY `catalogo_id` (`catalogo_id`),
  CONSTRAINT `runac_c1_campo_ibfk_1` FOREIGN KEY (`hoja_id`) REFERENCES `runac_c1_hoja` (`id`),
  CONSTRAINT `runac_c1_campo_ibfk_2` FOREIGN KEY (`dimension_id`) REFERENCES `runac_c1_dimension` (`id`),
  CONSTRAINT `runac_c1_campo_ibfk_3` FOREIGN KEY (`catalogo_id`) REFERENCES `runac_c1_catalogo` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=625 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Define los campos o columnas esperados dentro de cada hoja.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c1_campo`
--

LOCK TABLES `runac_c1_campo` WRITE;
/*!40000 ALTER TABLE `runac_c1_campo` DISABLE KEYS */;
INSERT INTO `runac_c1_campo` VALUES (122,7,1,NULL,'nombre_del_dispositvo','Nombre del dispositvo',1,'TEXTO',120,'SIN_NORMALIZAR',1,NULL),(123,7,1,NULL,'dependencia_institucional','Dependencia institucional',2,'TEXTO',255,'SIN_NORMALIZAR',0,'Organismo, ministerio, secretaría, dirección o área estatal de la cual depende orgánica y formalmente el dispositivo de cuidado.'),(124,7,1,13,'tipo_de_gestion','Tipo de gestión',3,'TEXTO',20,'SIN_NORMALIZAR',0,'Carácter público o privado/asociativo de la administración de la institución de cuidado alternativo.'),(125,7,1,1,'tiene_convenio_con_el_opn_solo_para_los_de_gestion_no_gub_ce242a','¿Tiene convenio con el OPN? (Solo para los de gestión no gubernamental y gestión mixta)',4,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(126,7,1,NULL,'localidad','Localidad',5,'TEXTO',120,'SIN_NORMALIZAR',0,'Ciudad, municipio, comuna o localidad geográfica donde se encuentra el dispositivo físicamente.'),(127,7,1,NULL,'direccion','Dirección',6,'TEXTO',255,'SIN_NORMALIZAR',0,'Domicilio real (calle, número, piso/departamento, entre calles) donde se encuentra ubicada la residencia.'),(128,7,1,NULL,'codigo_postal','Código postal',7,'TEXTO',10,'SIN_NORMALIZAR',0,'Código Postal Argentino de la localidad correspondiente.'),(129,7,1,NULL,'telefono','Teléfono',8,'TEXTO',50,'SIN_NORMALIZAR',0,'Número de contacto telefónico institucional o celular de guardia de la residencia.'),(130,7,NULL,1,'el_dispositivo_registra_las_intervenciones_en_el_sistema_c4fc90','El dispositivo, ¿registra las intervenciones en el Sistema Nominal digital del OPN provincial?',9,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(131,7,2,19,'proyecto_institucional','... Proyecto institucional?',10,'TEXTO',31,'SIN_NORMALIZAR',0,NULL),(132,7,2,19,'reglamento_de_convivencia','…reglamento de convivencia?',11,'TEXTO',31,'SIN_NORMALIZAR',0,NULL),(133,7,2,15,'habilitacion_municipal','... habilitación municipal?',12,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(134,7,2,28,'con_rampas_o_condiciones_para_el_acceso_y_circulacion_de_ecfaaf','... con rampas o condiciones para el acceso y circulación de personas con discapacidad',13,'TEXTO',38,'SIN_NORMALIZAR',0,NULL),(135,7,2,16,'tablets_o_computadoras_para_los_nya_alojados_en_el_dispositivo','... tablets o computadoras para los NyA alojados en el dispositivo',14,'TEXTO',48,'SIN_NORMALIZAR',0,NULL),(136,7,2,1,'wifi_en_el_dispositivo','... WIFI en el dispositivo',15,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(137,7,3,1,'para_el_ingreso_del_nya_al_dispositivo','... para el ingreso del NyA al dispositivo',16,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(138,7,3,1,'para_el_abordaje_de_conflictos_o_violencia_entre_nya','…para el abordaje de conflictos o violencia entre NyA',17,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(139,7,3,1,'para_el_abordaje_de_crisis_y_urgencias_en_salud_mental','... para el abordaje de crisis y urgencias en salud mental',18,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(140,7,4,NULL,'capacidad_de_alojamiento_plazas','Capacidad de alojamiento (Plazas)',19,'ENTERO',NULL,'SIN_NORMALIZAR',0,'Cantidad máxima total de plazas (camas) habilitadas formalmente por el dispositivo para el alojamiento de NyA.'),(141,7,4,NULL,'cantidad_de_nya_alojados_en_el_dispositivo_al_momento_de_4d0f88','Cantidad de NyA alojados en el dispositivo (al momento de la carga de la información)',20,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(142,7,4,31,'cantidad_de_nya_que_es_posible_alojar_por_dormitorio','Cantidad de NyA que es posible alojar por dormitorio',21,'TEXTO',26,'SIN_NORMALIZAR',0,'Distribución edilicia por habitación. Indicar cuántas camas hay en promedio por dormitorio.'),(143,7,5,32,'genero_admitido','Género admitido',22,'TEXTO',39,'SIN_NORMALIZAR',0,'Perfil de género de la población de NyA que tiene autorización de ingreso al dispositivo.'),(144,7,5,1,'grupos_de_hermanos','grupos de hermanos?',23,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(145,7,5,1,'nya_dolescentes_con_discapacidad','NyA dolescentes con discapacidad',24,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(146,7,5,1,'nya_con_padecimiento_de_salud_mental','NyA con padecimiento de salud mental',25,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(147,7,5,1,'nya_con_uso_o_abuso_de_sustancias','NyA con uso o abuso de sustancias',26,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(148,7,5,1,'adolescentes_con_hijos','Adolescentes con hijos',27,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(149,7,5,1,'aloja_ninos_de_0_a_5_anos','Aloja niños de 0 a 5 años',28,'TEXTO',20,'SIN_NORMALIZAR',0,'Indica si el dispositivo admite y aloja a niños en la primera infancia (0 a 5 años inclusive).'),(150,7,5,1,'aloja_ninos_de_6_a_12_anos','Aloja niños de 6 a 12 años',29,'TEXTO',20,'SIN_NORMALIZAR',0,'Indica si el dispositivo admite y aloja a niños en edad escolar primaria (6 a 12 años inclusive).'),(151,7,5,1,'aloja_poblacion_de_13_a_17_anos','Aloja población de 13 a 17 años',30,'TEXTO',20,'SIN_NORMALIZAR',0,'Indica si el dispositivo admite y aloja a adolescentes de 13 a 17 años inclusive.'),(152,7,5,1,'aloja_poblacion_de_18_anos_y_mas','Aloja población de 18 años y más',31,'TEXTO',20,'SIN_NORMALIZAR',0,'Indica si excepcionalmente aloja a jóvenes de 18 años o más que continúan en tránsito de egreso o bajo prórroga legal de protección.'),(153,7,6,11,'que_conforman_el_equipo_tecnico','… que conforman el equipo técnico',32,'TEXTO',28,'SIN_NORMALIZAR',0,NULL),(154,7,6,34,'destinadas_al_cuidado_del_nya','... destinadas al cuidado del NyA',33,'TEXTO',32,'SIN_NORMALIZAR',0,NULL),(155,7,6,35,'destinadas_a_tareas_de_apoyo_administrativo_mantenimiento_1e125d','... destinadas a tareas de apoyo (administrativo, mantenimiento, cocina, etc)',34,'TEXTO',31,'SIN_NORMALIZAR',0,NULL),(156,7,6,17,'del_equipo_de_conduccion','… del equipo de conducción',35,'TEXTO',36,'SIN_NORMALIZAR',0,NULL),(157,7,7,1,'recibio_capacitacion_en_promocion_de_cuidados','Recibió capacitación en PROMOCION DE CUIDADOS',36,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(158,7,7,1,'recibio_capacitacion_en_alimentacion_saludable','Recibió capacitación en ALIMENTACION SALUDABLE',37,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(159,7,7,1,'recibio_capacitacion_en_reanimacion_cardiopulmonar','Recibió capacitación en REANIMACION CARDIOPULMONAR',38,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(160,7,7,1,'recibio_capacitacion_en_primeros_auxilios','Recibió capacitación en PRIMEROS AUXILIOS',39,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(161,7,7,1,'recibio_capacitacion_en_abuso_sexual_infantil_juvenil','Recibió capacitación en ABUSO SEXUAL INFANTIL /JUVENIL',40,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(162,7,7,1,'recibio_capacitacion_en_paradigma_de_proteccion_integral','Recibió capacitación en PARADIGMA DE PROTECCION INTEGRAL',41,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(163,7,7,1,'recibio_capacitacion_en_autonomia_progresiva','Recibió capacitación en AUTONOMIA PROGRESIVA',42,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(164,7,7,1,'recibio_capacitacion_en_abordaje_en_salud_mental','Recibió capacitación en ABORDAJE EN SALUD MENTAL',43,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(165,7,7,1,'recibio_capacitacion_en_consumos_problematicos','Recibió capacitación en CONSUMOS PROBLEMATICOS',44,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(166,7,7,1,'recibio_capacitacion_en_cultura_digital','Recibió capacitación en CULTURA DIGITAL',45,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(167,7,7,1,'recibio_capacitacion_en_discapacidad','Recibió capacitación en DISCAPACIDAD',46,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(168,7,7,1,'recibio_capacitacion_en_administracion_financiera','Recibió capacitación en ADMINISTRACION FINANCIERA',47,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(169,7,7,1,'recibio_capacitacion_en_otras_tematicas','Recibió capacitación en OTRAS TEMÁTICAS',48,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(170,7,7,NULL,'otras_tematicas_especifique','Otras temáticas. Especifique',49,'TEXTO',255,'SIN_NORMALIZAR',0,'Si se marcó \'Sí\' en la columna de capacitación en \'OTRAS TEMÁTICAS\', especificar aquí cuáles fueron los temas abordados de forma sintética.'),(171,7,8,37,'el_dipositivo_participa_en_la_formulacion_del_proyecto_de_f26a26','El dipositivo participa en la formulación del proyecto de restitución de derechos',50,'TEXTO',34,'SIN_NORMALIZAR',0,NULL),(172,7,8,21,'participa_el_nya_en_el_proyecto_de_restitucion_de_derechos_per','Participa el NyA en el proyecto de restitución de derechos (PER)',51,'TEXTO',32,'SIN_NORMALIZAR',0,NULL),(173,7,8,21,'existe_articulacion_entre_el_per_y_el_plan_de_estadia','Existe articulación entre el PER y el plan de estadía?',52,'TEXTO',32,'SIN_NORMALIZAR',0,'¿Las actividades cotidianas del NyA en el dispositivo están alineadas y coordinadas con el proyecto de restitución trazado por la autoridad de aplicación?'),(174,7,9,1,'promueve_el_contacto_con_la_familia_y_o_referentes_afecti_f4339a','¿Promueve el contacto con la familia y/o referentes afectivos a través de redes, mails, cartas?',53,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(175,7,9,1,'promueve_el_contacto_con_la_familia_y_o_referentes_afecti_c9002f','¿Promueve el contacto con la familia y/o referentes afectivos a través de encuentros fuera del dispositivo?',54,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(176,7,9,1,'promueve_el_contacto_con_la_familia_y_o_referentes_afecti_e14bff','¿Promueve el contacto con la familia y/o referentes afectivos a través de visitas presenciales?',55,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(177,7,9,1,'promueve_el_contacto_con_la_familia_y_o_referentes_afecti_5370e5','¿Promueve el contacto con la familia y/o referentes afectivos a través de llamadas y videollamadas?',56,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(178,7,9,9,'con_que_frecuencia_los_nya_alojados_en_el_dispositivo_rea_254ee2','¿Con que frecuencia los NyA alojados en el dispositivo realizan actividades fuera del dispositivo?',57,'TEXTO',26,'SIN_NORMALIZAR',0,NULL),(179,7,9,9,'con_que_frecuencia_los_nya_alojados_en_el_dispositivo_rea_0a47aa','¿Con que frecuencia los NyA alojados en el dispositivo realizan Actividades ARTISTICAS?',58,'TEXTO',26,'SIN_NORMALIZAR',0,NULL),(180,7,9,9,'con_que_frecuencia_los_nya_alojados_en_el_dispositivo_rea_0516fc','¿Con que frecuencia los NyA alojados en el dispositivo realizan Actividades DEPORTIVAS?',59,'TEXTO',26,'SIN_NORMALIZAR',0,NULL),(181,7,9,9,'con_que_frecuencia_los_nya_alojados_en_el_dispositivo_rea_0010d4','¿Con que frecuencia los NyA alojados en el dispositivo realizan Actividades RECREATIVAS?',60,'TEXTO',26,'SIN_NORMALIZAR',0,NULL),(182,7,9,9,'con_que_frecuencia_los_nya_alojados_en_el_dispositivo_rea_b4d710','¿Con que frecuencia los NyA alojados en el dispositivo realizan OTRAS Actividades?',61,'TEXTO',26,'SIN_NORMALIZAR',0,NULL),(183,8,NULL,NULL,'fecha_del_relevamiento','Fecha del relevamiento',1,'FECHA',NULL,'SIN_NORMALIZAR',1,'Consignar la fecha en que se rrealiza el registro o actuliza la informacion.'),(184,8,10,40,'provincia','Provincia',2,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(185,8,10,NULL,'nombre_del_programa_dispositivo','Nombre del programa/dispositivo',3,'TEXTO',120,'SIN_NORMALIZAR',1,'Indicar el nombre del dispositivo, hogar, residencia, centro o programa donde se realiza la intervención.'),(186,8,10,NULL,'dependencia_institucional','Dependencia institucional',4,'TEXTO',255,'SIN_NORMALIZAR',0,'Registrar la denominación oficial completa de la institución responsable, evitando siglas sin aclaración y nombres abreviados. Si el programa depende de más de un organismo, consignar la dependencia principal.'),(187,8,10,NULL,'localidad','Localidad',5,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(188,8,10,NULL,'domicilio','Domicilio',6,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(189,8,10,NULL,'equipo_interviniente_dispositivo_espacio','Equipo interviniente',7,'TEXTO',255,'SIN_NORMALIZAR',0,'Nombre del equipo o área interviniente. Profesionales que participan de la intervención (si corresponde). Disciplina o función de los integrantes cuando sea relevante.'),(190,8,10,NULL,'responsable_del_programa','Responsable del programa',8,'TEXTO',255,'SIN_NORMALIZAR',0,'Nombre y apellido completos. Cargo o función (si corresponde). Persona formalmente designada como responsable del dispositivo o programa'),(191,8,10,NULL,'telefono_de_contacto','Teléfono de contacto',9,'TEXTO',50,'SIN_NORMALIZAR',0,NULL),(192,8,10,NULL,'mail_de_contacto','Mail de contacto',10,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(193,8,11,NULL,'apellido_s','Apellido/s',11,'TEXTO',120,'SIN_NORMALIZAR',1,'Registrar el o los apellidos completos del niño, niña o adolescente, de acuerdo con la documentación vigente o, en su defecto, según la información proporcionada por la persona responsable o fuente institucional confiable'),(194,8,11,NULL,'nombre_s','Nombre/s',12,'TEXTO',120,'SIN_NORMALIZAR',1,'Registrar el o los nombres completos del niño, niña o adolescente, de acuerdo con la documentación vigente o, en su defecto, según la información proporcionada por la persona responsable o fuente institucional confiable'),(195,8,11,44,'situacion_de_documentacion','Situación de documentación',13,'TEXTO',24,'SIN_NORMALIZAR',0,NULL),(196,8,11,NULL,'n_dni','Nº DNI',14,'TEXTO',15,'SIN_NORMALIZAR',0,NULL),(197,8,11,NULL,'n_de_cuil','Nº de CUIL',15,'TEXTO',13,'SIN_NORMALIZAR',1,NULL),(198,8,11,46,'genero','Género',16,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(199,8,11,41,'pais_de_nacimiento','País de nacimiento',17,'TEXTO',44,'SIN_NORMALIZAR',0,NULL),(200,8,11,NULL,'fecha_de_nacimiento','Fecha de nacimiento',18,'FECHA',NULL,'SIN_NORMALIZAR',1,NULL),(201,8,11,NULL,'edad','Edad',19,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(202,8,11,48,'asistencia_escolar','Asistencia escolar',20,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(203,8,11,39,'maximo_nivel_educativo_alcanzado','Máximo nivel educativo alcanzado',21,'TEXTO',23,'SIN_NORMALIZAR',0,NULL),(204,8,11,NULL,'domicilio_actual','Domicilio actual',22,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(205,8,11,40,'provincia_nya','Provincia (NyA)',23,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(206,8,11,NULL,'localidad_nya','Localidad (NyA)',24,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(207,8,11,NULL,'partido','Partido',25,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(208,8,11,NULL,'codigo_postal','Código postal',26,'TEXTO',10,'SIN_NORMALIZAR',0,NULL),(209,8,11,57,'destinatario','Destinatario',27,'TEXTO',20,'SIN_NORMALIZAR',0,'Consignar la persona, grupo poblacional o sujeto de derecho al que se dirige la intervención, prestación, acción de acompañamiento o medida de protección.'),(210,8,11,49,'linea_de_accion','Línea de acción',28,'TEXTO',24,'SIN_NORMALIZAR',0,'Consignar la estrategia, componente programático, modalidad de intervención o eje de trabajo mediante el cual se implementa la acción de protección, promoción, restitución o fortalecimiento de derechos de NyA.'),(211,8,11,NULL,'enfermedad_cronica','Enfermedad crónica',29,'TEXTO',255,'SIN_NORMALIZAR',0,'Registrar únicamente enfermedades crónicas diagnosticadas o informadas por fuentes confiables'),(212,8,11,50,'problematica_de_salud','Problemática de salud',30,'TEXTO',20,'SIN_NORMALIZAR',0,'Registrar cualquier situación, condición o dificultad vinculada a la salud física, mental o integral del Ny/Oa que requiera atención, seguimiento, tratamiento o articulación con servicios de salud, independientemente de que constituya o no una enfermedad crónica'),(213,8,11,NULL,'consumo_problematico_de_sustancias','Consumo problemático de sustancias',31,'TEXTO',255,'SIN_NORMALIZAR',0,'Registrar únicamente información conocida, relevada o informada por fuentes confiables. Cuando exista una situación de consumo, describirla de manera breve y objetiva'),(214,8,11,43,'presenta_alguna_discapacidad','¿Presenta alguna discapacidad?',32,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(215,8,11,59,'tipo_de_discapacidad','Tipo de discapacidad',33,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(216,8,11,61,'posee_cud','¿Posee CUD?',34,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(217,8,11,51,'cobertura_salud','Cobertura salud',35,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(218,8,11,NULL,'seguridad_social','Seguridad social',36,'TEXTO',255,'SIN_NORMALIZAR',0,'Registrar todos los beneficios vigentes. Ej:Asignación Universal por Hijo (AUH). Asignación Familiar. Pensión por discapacidad. Pensión no contributiva. Programa de acompañamiento social. Otro beneficio social'),(219,8,11,1,'se_identifica_con_algun_pueblo_originario','¿Se identifica con algún pueblo originario?',37,'TEXTO',20,'SIN_NORMALIZAR',0,'Identificar la pertenencia a pueblos originarios para contribuir a la producción de información con enfoque de derechos, diversidad cultural e interculturalidad'),(220,8,11,NULL,'pueblo_originario_especificar','Pueblo originario (especificar)',38,'TEXTO',NULL,'SIN_NORMALIZAR',0,NULL),(221,8,11,43,'tiene_hijos_as','¿Tiene hijos/as?',39,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(222,8,12,53,'relacion_vincular_del_referente','Relación vincular del referente',40,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(223,8,12,NULL,'apellido_s_del_referente','Apellido/s del referente',41,'TEXTO',120,'SIN_NORMALIZAR',1,NULL),(224,8,12,NULL,'nombre_s_del_referente','Nombre/s del referente',42,'TEXTO',120,'SIN_NORMALIZAR',1,NULL),(225,8,12,NULL,'dni_del_referente','DNI del referente',43,'TEXTO',15,'SIN_NORMALIZAR',1,NULL),(226,8,12,46,'genero_del_referente','Género del referente',44,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(227,8,12,NULL,'fecha_de_nacimiento_del_referente','Fecha de nacimiento del referente',45,'FECHA',NULL,'SIN_NORMALIZAR',1,NULL),(228,8,12,41,'nacionalidad_del_referente','Nacionalidad del referente',46,'TEXTO',44,'SIN_NORMALIZAR',0,NULL),(229,8,12,NULL,'domicilio_actual_del_referente','Domicilio actual del referente',47,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(230,8,12,NULL,'codigo_postal_del_referente','Código postal del referente',48,'TEXTO',10,'SIN_NORMALIZAR',0,NULL),(231,8,12,NULL,'localidad_del_referente','Localidad del referente',49,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(232,8,12,NULL,'partido_del_referente','Partido del referente',50,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(233,8,12,40,'provincia_del_referente','Provincia del referente',51,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(234,8,12,NULL,'telefono_y_mail_del_referente','Teléfono y mail del referente',52,'TEXTO',50,'SIN_NORMALIZAR',0,NULL),(235,8,12,42,'nivel_escolar_del_referente','Nivel escolar del referente',53,'TEXTO',24,'SIN_NORMALIZAR',0,NULL),(236,8,12,63,'situacion_laboral_del_referente','Situación laboral del referente',54,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(237,8,12,NULL,'seguridad_social_del_referente','Seguridad social del referente',55,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(238,8,12,1,'el_referente_se_identifica_con_algun_pueblo_originario','¿El referente se identifica con algún pueblo originario?',56,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(239,8,12,NULL,'pueblo_originario_del_refrente','Pueblo originario del refrente',57,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(240,8,13,NULL,'equipo_interviniente_medida','Equipo Interviniente',58,'TEXTO',255,'SIN_NORMALIZAR',0,'Debe identificarse prioritariamente el equipo, área o servicio de pertenencia. Si intervienen varios equipos, consignar el que tenga la responsabilidad principal de la medida o coordinación del caso.'),(241,8,13,66,'origen_de_la_demanda','Origen de la demanda',59,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(242,8,13,NULL,'causas_de_las_medidas','Causas de las medidas',60,'TEXTO',255,'SIN_NORMALIZAR',0,'Mencionar la causa principal que motivó la implementación de la medida. Cuando existan múltiples situaciones de vulneración, registrar aquella que resulte predominante o que haya dado origen a la intervención.'),(243,8,13,NULL,'fecha_de_la_medida_mpi','Fecha de la medida MPI',61,'FECHA',NULL,'SIN_NORMALIZAR',0,'Registrar la fecha en que se dictó, dispuso o formalizó la Medida de Protección Integral (MPI) por parte de la autoridad administrativa competente. Esta fecha marca el inicio formal de la intervención en el marco de la medida'),(244,8,13,NULL,'plazos_en_la_intervencion','Plazos en la intervención',62,'TEXTO',255,'SIN_NORMALIZAR',0,'Consignar el período previsto o establecido para la implementación, seguimiento y evaluación de la Medida de Protección Integral (MPI), de acuerdo con la planificación realizada por el organismo o equipo interviniente.'),(245,8,13,NULL,'causas_del_cese_de_la_mpi','Causas del cese de la MPI',63,'TEXTO',255,'SIN_NORMALIZAR',0,'Identificar los motivos de finalización de las Medidas de Protección Integral y contribuir al monitoreo de los resultados alcanzados en los procesos de restitución y garantía de derechos'),(246,8,NULL,NULL,'observaciones','Observaciones',64,'TEXTO',NULL,'SIN_NORMALIZAR',0,'Registrar información complementaria relevante que contribuya a una mejor comprensión de la situación del niño, niña o adolescente, de su contexto familiar o de la intervención realizada, y que no haya sido consignada en otros campos del formulario.'),(247,9,NULL,NULL,'fecha_del_relevamiento','Fecha del relevamiento',1,'FECHA',NULL,'SIN_NORMALIZAR',1,'Fecha de captura o actualización de la información nominal del NyA.'),(248,9,14,40,'provincia','Provincia',2,'TEXTO',20,'SIN_NORMALIZAR',0,'Jurisdicción político-territorial que dicta y ejecuta la medida excepcional.'),(249,9,14,83,'modalidad_de_cuidado','Modalidad de cuidado',3,'TEXTO',22,'SIN_NORMALIZAR',0,'Entorno o tipo de acogimiento alternativo formal en el cual se encuentra inserto el NyA.'),(250,9,15,NULL,'nombre_de_la_residencia_hogar','Nombre de la residencia/hogar',4,'TEXTO',120,'SIN_NORMALIZAR',0,'Nombre del dispositivo residencial específico de alojamiento. Debe coincidir con el registro oficial del archivo SCP.'),(251,9,15,NULL,'dependencia_institucional','Dependencia institucional',5,'TEXTO',255,'SIN_NORMALIZAR',0,'Organismo público o privado del cual depende legalmente el hogar (ej. OPN, Obispado, Asociación Civil X).'),(252,9,15,NULL,'localidad','Localidad',6,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(253,9,16,NULL,'id_del_nino_nina_o_adolescente','ID del Niño, niña o Adolescente',7,'TEXTO',255,'SIN_NORMALIZAR',0,'Identificador alfanumérico nominal único provincial asignado al NyA para seguimiento resguardando su identidad. En caso de existir.'),(254,9,16,NULL,'apellido_s','Apellido/s',8,'TEXTO',120,'SIN_NORMALIZAR',1,'Apellidos completos del niño, niña o adolescente según partida de nacimiento o DNI.'),(255,9,16,NULL,'nombre_s','Nombre/s',9,'TEXTO',120,'SIN_NORMALIZAR',1,'Nombres completos del niño, niña o adolescente.'),(256,9,16,NULL,'situacion_de_documentacion','Situación de documentación',10,'TEXTO',255,'SIN_NORMALIZAR',0,'Estado legal del trámite y posesión del documento del NyA.'),(257,9,16,NULL,'n_dni','Nº DNI',11,'TEXTO',15,'SIN_NORMALIZAR',0,'Número de Documento Nacional de Identidad del NyA.'),(258,9,16,NULL,'n_de_cuil','Nº de CUIL',12,'TEXTO',13,'SIN_NORMALIZAR',1,'Código Único de Identificación Laboral.'),(259,9,16,46,'genero','Género',13,'TEXTO',20,'SIN_NORMALIZAR',0,'Identidad de género autopercibida por el NyA.'),(260,9,16,41,'pais_de_nacimiento','País de nacimiento',14,'TEXTO',44,'SIN_NORMALIZAR',0,NULL),(261,9,16,NULL,'fecha_de_nacimiento','Fecha de nacimiento',15,'FECHA',NULL,'SIN_NORMALIZAR',1,'Fecha de nacimiento oficial del NyA.'),(262,9,16,NULL,'edad','Edad',16,'ENTERO',NULL,'SIN_NORMALIZAR',0,'Edad del NyA cumplida al momento del relevamiento (puede automatizarse mediante fórmula).'),(263,9,16,86,'asiste_a_institucion_educativa','¿Asiste a institución educativa?',17,'TEXTO',20,'SIN_NORMALIZAR',0,'Indica si asiste de forma activa e inscrita a algún establecimiento oficial de educación inicial, primaria, secundaria o educación especial.'),(264,9,16,NULL,'maximo_nivel_educativo_alcanzado','Máximo nivel educativo alcanzado',18,'TEXTO',255,'SIN_NORMALIZAR',0,'Último nivel educativo completado por el NyA.'),(265,9,16,43,'enfermedad_cronica','Enfermedad crónica',19,'TEXTO',20,'SIN_NORMALIZAR',0,'Indica si el NyA padece alguna condición médica crónica que requiera tratamiento continuo certificado (ej. asma, diabetes, VIH).'),(266,9,16,43,'consumo_problematico_de_sustancias','Consumo problemático de sustancias',20,'TEXTO',20,'SIN_NORMALIZAR',0,'Indica si presenta consumo recurrente u problemático de sustancias adictivas diagnosticado o en abordaje.'),(267,9,16,43,'presenta_alguna_discapacidad','¿Presenta alguna discapacidad?',21,'TEXTO',20,'SIN_NORMALIZAR',0,'Indica si el NyA tiene una discapacidad física, intelectual, auditiva, visual, etc.'),(268,9,16,59,'tipo_de_discapacidad','Tipo de discapacidad',22,'TEXTO',20,'SIN_NORMALIZAR',0,'Categoría de la discapacidad predominante del NyA.'),(269,9,16,61,'posee_cud','¿Posee CUD?',23,'TEXTO',20,'SIN_NORMALIZAR',0,'Indica si el NyA cuenta con el Certificado Único de Discapacidad oficial nacional vigente.'),(270,9,16,51,'cobertura_salud','Cobertura salud',24,'TEXTO',20,'SIN_NORMALIZAR',0,'Tipo de cobertura médica de la que goza el NyA.'),(271,9,16,1,'pertenece_a_pueblo_originario','¿Pertenece a pueblo originario?',25,'TEXTO',20,'SIN_NORMALIZAR',0,'Indica si el NyA se autoreconoce o pertenece a una comunidad de pueblos originarios de Argentina.'),(272,9,16,NULL,'pueblo_originario_especificar','Pueblo originario (especificar)',26,'TEXTO',NULL,'SIN_NORMALIZAR',0,'Nombre de la comunidad étnica correspondiente.'),(273,9,16,1,'tiene_hijos_as','¿Tiene hijos/as?',27,'TEXTO',20,'SIN_NORMALIZAR',0,'Indica si el NyA es padre o madre.'),(274,9,17,NULL,'id_familia','ID familia',28,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(275,9,17,NULL,'familia','Familia',29,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(276,9,18,NULL,'id_familia_ampliada','ID familia ampliada',30,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(277,9,18,NULL,'familia_ampliada','Familia Ampliada',31,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(278,9,19,NULL,'fecha_de_inicio_mpe','Fecha de inicio MPE',32,'FECHA',NULL,'SIN_NORMALIZAR',0,'Fecha de emisión/disposición formal en la que se decretó administrativamente la separación excepcional de su núcleo de origen.'),(279,9,19,NULL,'dias_de_permanencia','Días de permanencia',33,'ENTERO',NULL,'SIN_NORMALIZAR',0,'Cantidad de días que el NyA lleva bajo protección excepcional (se calcula como Fecha Relevamiento - Fecha Inicio de la MPE).'),(280,9,19,76,'origen_de_la_demanda','Origen de la demanda',34,'TEXTO',20,'SIN_NORMALIZAR',0,'Canal que alertó de la vulneración de derechos inicial que dio origen a la MPE.'),(281,9,19,NULL,'motivo_de_intervencion','Motivo de intervención',35,'TEXTO',255,'SIN_NORMALIZAR',0,'Causa primordial legal que justificó la medida de protección excepcional de separación.'),(282,9,19,NULL,'submotivo_de_intervencion','Submotivo de intervención',36,'TEXTO',255,'SIN_NORMALIZAR',0,'Detalle pormenorizado del motivo principal.'),(283,9,19,77,'tipo_de_proyecto_de_restitucion','Tipo de proyecto de restitución',37,'TEXTO',20,'SIN_NORMALIZAR',0,'Línea de acción priorizada del Plan Especial de Restitución (PER) vigente para el NyA.'),(284,9,19,43,'elevacion_dictamen_mpe_a_juzgado','Elevación dictamen MPE a juzgado',38,'TEXTO',20,'SIN_NORMALIZAR',0,'Indica si el dictamen de control de legalidad de la MPE fue elevado al Juzgado de Familia.'),(285,9,19,43,'decreto_judicial_de_adoptabilidad','Decreto judicial de adoptabilidad',39,'TEXTO',20,'SIN_NORMALIZAR',0,'Indica si existe sentencia judicial firme decretando el estado de adoptabilidad del NyA'),(286,9,19,43,'solicitud_inclusion_proy_autonomia','Solicitud inclusión proy. autonomía',40,'TEXTO',20,'SIN_NORMALIZAR',0,'Indica si se ha gestionado e incorporado al NyA al Programa de Acompañamiento para el Egreso (PAE) o iniciativa provincial de autonomía.'),(287,9,NULL,NULL,'observaciones','Observaciones',41,'TEXTO',NULL,'SIN_NORMALIZAR',0,'Comentarios adicionales o novedades relevantes del caso.'),(369,12,NULL,NULL,'nombre_del_dispositvo','Nombre del dispositvo',1,'TEXTO',120,'SIN_NORMALIZAR',1,NULL),(370,12,NULL,NULL,'dependencia_institucional','Dependencia institucional',2,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(371,12,NULL,NULL,'localidad','Localidad',3,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(372,12,NULL,NULL,'direccion','Dirección',4,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(373,12,NULL,NULL,'telefono','Teléfono',5,'TEXTO',50,'SIN_NORMALIZAR',0,NULL),(374,12,NULL,NULL,'capacidad_de_alojamiento_mujeres_plazas_disponibles','Capacidad de alojamiento mujeres (plazas disponibles)',6,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(375,12,NULL,NULL,'capacidad_de_alojamiento_varones_plazas_disponibles','Capacidad de alojamiento varones (plazas disponibles)',7,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(376,12,NULL,4,'cuenta_con_proyecto_institucional','¿Cuenta con Proyecto Institucional?',8,'TEXTO',38,'SIN_NORMALIZAR',0,NULL),(377,12,NULL,6,'cuenta_con_normativa_convivencial','¿Cuenta con Normativa Convivencial?',9,'TEXTO',38,'SIN_NORMALIZAR',0,NULL),(378,12,NULL,NULL,'cantidad_de_agentes_equipo_tecnico_y_profesional_incluye_efd962','Cantidad de agentes: equipo técnico y profesional (incluye cuidadores)',10,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(379,12,NULL,NULL,'cantidad_agentes_de_salud','Cantidad agentes de salud',11,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(380,12,NULL,NULL,'cantidad_de_personal_administrativo_limpieza_cocina_y_man_7d034d','Cantidad de personal: administrativo, limpieza, cocina y mantenimiento',12,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(381,12,NULL,NULL,'cantidad_de_personal_seguridad','Cantidad de personal seguridad',13,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(382,12,NULL,1,'cuenta_con_protocolos_de_ingreso','Cuenta con protocolos de ingreso',14,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(383,12,NULL,1,'cuenta_con_protocolo_de_requisa','Cuenta con protocolo de requisa',15,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(384,12,NULL,1,'cuenta_con_protocolo_de_denuncias_por_malos_tratos','Cuenta con protocolo de denuncias por malos tratos',16,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(385,12,NULL,1,'cuenta_con_protocolos_de_actuacion_ante_conflictos_entre_pares','Cuenta con protocolos de actuación ante conflictos entre pares',17,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(386,12,NULL,1,'protocolo_de_abordaje_del_suicidio','Protocolo de abordaje del suicidio',18,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(387,12,NULL,1,'cuenta_con_protocolo_de_sanciones','Cuenta con protocolo de sanciones',19,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(388,12,NULL,NULL,'cantidad_de_horas_semanales_destinadas_al_contacto_presen_510115','Cantidad de horas semanales destinadas al contacto presencial, afectivo/familiar',20,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(389,12,NULL,1,'cuenta_con_espacios_para_visitas_socioafectivas','Cuenta con espacios para visitas socioafectivas',21,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(390,12,NULL,5,'cumple_con_los_niveles_de_obligatoriedad_de_educacion_primaria','Cumple con los niveles de obligatoriedad de educación primaria',22,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(391,12,NULL,NULL,'cantidad_de_horas_semanales_dedicadas_a_la_educacion_primaria','Cantidad de horas semanales dedicadas a la educación primaria',23,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(392,12,NULL,5,'cumple_con_los_niveles_de_obligatoriedad_de_educacion_secundaria','Cumple con los niveles de obligatoriedad de educación secundaria',24,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(393,12,NULL,NULL,'cantidad_de_horas_semanales_dedicadas_a_la_educacion_secundaria','Cantidad de horas semanales dedicadas a la educación secundaria',25,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(394,12,NULL,1,'tiene_aulas_destinadas_a_la_educacion_obligatoria','Tiene aulas destinadas a la educación obligatoria',26,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(395,12,NULL,NULL,'cantidad_de_horas_semanales_dedicadas_a_la_formacion_profesional','Cantidad de horas semanales dedicadas a la formación profesional',27,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(396,12,NULL,NULL,'cantidad_de_horas_semanales_dedicadas_a_talleres_deportiv_bedd8e','Cantidad de horas semanales dedicadas a talleres deportivos y culturales',28,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(397,12,NULL,1,'cuenta_con_espacio_para_talleres','Cuenta con espacio para talleres',29,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(398,12,NULL,1,'cuenta_con_asesoramiento_tecnico_juridico','Cuenta con asesoramiento técnico jurídico',30,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(399,12,NULL,1,'cuenta_con_patio_abierto','Cuenta con patio abierto',31,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(400,12,NULL,1,'cuenta_con_patio_techado','Cuenta con patio techado',32,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(401,12,NULL,1,'cuenta_con_celdas_secas','Cuenta con celdas secas',33,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(402,12,NULL,1,'cuenta_con_celdas_humedas','Cuenta con celdas humedas',34,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(403,12,NULL,1,'cuenta_con_mobiliario_en_las_celdas','Cuenta con mobiliario en las celdas',35,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(404,12,NULL,1,'cuenta_con_colchones_ignifugos','Cuenta con colchones ignífugos',36,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(405,13,NULL,NULL,'nombre_del_dispositvo','Nombre del dispositvo',1,'TEXTO',120,'SIN_NORMALIZAR',1,NULL),(406,13,NULL,NULL,'dependencia_institucional','Dependencia institucional',2,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(407,13,NULL,NULL,'localidad','Localidad',3,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(408,13,NULL,NULL,'direccion','Dirección',4,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(409,13,NULL,NULL,'telefono','Teléfono',5,'TEXTO',50,'SIN_NORMALIZAR',0,NULL),(410,13,NULL,4,'cuenta_con_proyecto_institucional','Cuenta con Proyecto Institucional',6,'TEXTO',38,'SIN_NORMALIZAR',0,NULL),(411,13,NULL,6,'cuenta_con_normativa_convivencial','Cuenta con Normativa Convivencial',7,'TEXTO',38,'SIN_NORMALIZAR',0,NULL),(412,13,NULL,1,'cuenta_con_protocolos_de_ingreso','Cuenta con protocolos de ingreso',8,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(413,13,NULL,1,'cuenta_con_protocolo_de_requisa','Cuenta con protocolo de requisa',9,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(414,13,NULL,1,'cuenta_con_protocolo_de_denuncias_por_malos_tratos','Cuenta con protocolo de denuncias por malos tratos',10,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(415,13,NULL,1,'cuenta_con_protocolos_de_actuacion_ante_conflictos_entre_pares','Cuenta con protocolos de actuación ante conflictos entre pares',11,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(416,13,NULL,1,'protocolo_de_abordaje_del_suicidio','Protocolo de abordaje del suicidio',12,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(417,13,NULL,1,'cuenta_con_protocolo_de_sanciones','Cuenta con protocolo de sanciones',13,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(418,13,NULL,NULL,'capacidad_de_alojamiento_mujeres_plazas_disponibles','Capacidad de alojamiento mujeres (plazas disponibles)',14,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(419,13,NULL,NULL,'capacidad_de_alojamiento_varones_plazas_disponibles','Capacidad de alojamiento varones (plazas disponibles)',15,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(420,13,NULL,NULL,'cantidad_de_agentes_equipo_tecnico_y_profesional_incluye_efd962','Cantidad de agentes: equipo técnico y profesional (incluye cuidadores)',16,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(421,13,NULL,NULL,'cantidad_agentes_de_salud','Cantidad agentes de salud',17,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(422,13,NULL,NULL,'cantidad_de_personal_administrativo_limpieza_cocina_y_man_7d034d','Cantidad de personal: administrativo, limpieza, cocina y mantenimiento',18,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(423,13,NULL,NULL,'cantidad_de_personal_seguridad','Cantidad de personal seguridad',19,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(424,13,NULL,NULL,'cantidad_de_horas_semanales_destinadas_al_contacto_presen_510115','Cantidad de horas semanales destinadas al contacto presencial, afectivo/familiar',20,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(425,13,NULL,1,'cuenta_con_espacios_para_visitas_socioafectivas','Cuenta con espacios para visitas socioafectivas',21,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(426,13,NULL,5,'cumple_con_los_niveles_de_obligatoriedad_de_educacion_primaria','Cumple con los niveles de obligatoriedad de educación primaria',22,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(427,13,NULL,NULL,'cantidad_de_horas_semanales_dedicadas_a_la_educacion_primaria','Cantidad de horas semanales dedicadas a la educación primaria',23,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(428,13,NULL,5,'cumple_con_los_niveles_de_obligatoriedad_de_educacion_secundaria','Cumple con los niveles de obligatoriedad de educación secundaria',24,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(429,13,NULL,NULL,'cantidad_de_horas_semanales_dedicadas_a_la_educacion_secundaria','Cantidad de horas semanales dedicadas a la educación secundaria',25,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(430,13,NULL,1,'tiene_aulas_destinadas_a_la_educacion_obligatoria','Tiene aulas destinadas a la educación obligatoria',26,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(431,13,NULL,NULL,'cantidad_de_horas_semanales_dedicadas_a_la_formacion_profesional','Cantidad de horas semanales dedicadas a la formación profesional',27,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(432,13,NULL,NULL,'cantidad_de_horas_semanales_dedicadas_a_talleres_deportiv_bedd8e','Cantidad de horas semanales dedicadas a talleres deportivos y culturales',28,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(433,13,NULL,1,'cuenta_con_espacio_para_talleres','Cuenta con espacio para talleres',29,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(434,13,NULL,1,'cuenta_con_asesoramiento_tecnico_juridico','Cuenta con asesoramiento técnico jurídico',30,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(435,13,NULL,1,'cuenta_con_patio_abierto','Cuenta con patio abierto',31,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(436,13,NULL,1,'cuenta_con_patio_techado','Cuenta con patio techado',32,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(437,13,NULL,1,'cuenta_con_celdas_secas','Cuenta con celdas secas',33,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(438,13,NULL,1,'cuenta_con_celdas_humedas','Cuenta con celdas humedas',34,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(439,13,NULL,1,'cuenta_con_mobiliario_en_las_celdas','Cuenta con mobiliario en las celdas',35,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(440,13,NULL,1,'cuenta_con_colchones_ignifugos','Cuenta con colchones ignífugos',36,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(441,14,NULL,NULL,'nombre_del_dispositvo','Nombre del dispositvo',1,'TEXTO',120,'SIN_NORMALIZAR',1,NULL),(442,14,NULL,NULL,'dependencia_institucional','Dependencia institucional',2,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(443,14,NULL,NULL,'localidad','Localidad',3,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(444,14,NULL,NULL,'direccion','Dirección',4,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(445,14,NULL,NULL,'telefono','Teléfono',5,'TEXTO',50,'SIN_NORMALIZAR',0,NULL),(446,14,NULL,4,'cuenta_con_proyecto_institucional','Cuenta con Proyecto Institucional',6,'TEXTO',38,'SIN_NORMALIZAR',0,NULL),(447,14,NULL,1,'cuenta_con_espacio_de_grupalidad','Cuenta con espacio de grupalidad',7,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(448,14,NULL,NULL,'cantidad_de_agentes_equipo_tecnico_y_profesional_incluye_efd962','Cantidad de agentes: equipo técnico y profesional (incluye cuidadores)',8,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(449,14,NULL,1,'cuenta_con_asesoramiento_tecnico_juridico','Cuenta con asesoramiento técnico jurídico',9,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(450,14,NULL,NULL,'jurisdicciones_dentro_de_la_provincia_en_las_que_el_dispo_a48f6b','Jurisdicciones dentro de la provincia en las que el dispositivo tiene alcance',10,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(451,15,NULL,NULL,'nombre_del_dispositvo','Nombre del dispositvo',1,'TEXTO',120,'SIN_NORMALIZAR',1,NULL),(452,15,NULL,NULL,'dependencia_institucional','Dependencia institucional',2,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(453,15,NULL,NULL,'localidad','Localidad',3,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(454,15,NULL,NULL,'direccion','Dirección',4,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(455,15,NULL,NULL,'telefono','Teléfono',5,'TEXTO',50,'SIN_NORMALIZAR',0,NULL),(456,15,NULL,4,'cuenta_con_proyecto_institucional','Cuenta con Proyecto Institucional',6,'TEXTO',38,'SIN_NORMALIZAR',0,NULL),(457,15,NULL,1,'cuenta_con_resolucion_de_creacion','Cuenta con resolución de creación',7,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(458,15,NULL,6,'cuenta_con_normativa_convivencial','Cuenta con Normativa Convivencial',8,'TEXTO',38,'SIN_NORMALIZAR',0,NULL),(459,15,NULL,7,'cuenta_con_protocolos_de_articulacion_interministerial_co_5e1a90','Cuenta con protocolos de articulación interministerial. Con qué áreas',9,'TEXTO',34,'SIN_NORMALIZAR',0,NULL),(460,15,NULL,1,'cuenta_con_protocolos_de_ingreso','Cuenta con protocolos de ingreso',10,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(461,15,NULL,1,'cuenta_con_protocolo_de_requisa','Cuenta con protocolo de requisa',11,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(462,15,NULL,1,'cuenta_con_protocolo_de_denuncias_por_malos_tratos','Cuenta con protocolo de denuncias por malos tratos',12,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(463,15,NULL,1,'cuenta_con_protocolos_de_actuacion_ante_conflictos_entre_pares','Cuenta con protocolos de actuación ante conflictos entre pares',13,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(464,15,NULL,1,'cuenta_con_protocolo_de_abordaje_del_suicidio','Cuenta con protocolo de abordaje del suicidio',14,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(465,15,NULL,1,'cuenta_con_protocolo_de_sanciones','Cuenta con protocolo de sanciones',15,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(466,15,NULL,NULL,'capacidad_de_alojamiento_mujeres_plazas_disponibles','Capacidad de alojamiento mujeres (plazas disponibles)',16,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(467,15,NULL,NULL,'capacidad_de_alojamiento_varones_plazas_disponibles','Capacidad de alojamiento varones (plazas disponibles)',17,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(468,15,NULL,NULL,'cantidad_de_agentes_equipo_tecnico_y_profesional_incluye_efd962','Cantidad de agentes: equipo técnico y profesional (incluye cuidadores)',18,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(469,15,NULL,NULL,'cantidad_agentes_de_salud','Cantidad agentes de salud',19,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(470,15,NULL,NULL,'cantidad_de_personal_administrativo_limpieza_cocina_y_man_7d034d','Cantidad de personal: administrativo, limpieza, cocina y mantenimiento',20,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(471,15,NULL,NULL,'cantidad_de_personal_seguridad','Cantidad de personal seguridad',21,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(472,15,NULL,1,'cuenta_con_celdas_secas','Cuenta con celdas secas',22,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(473,15,NULL,1,'cuenta_con_celdas_humedas','Cuenta con celdas humedas',23,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(474,15,NULL,1,'cuenta_con_mobiliario_en_las_celdas','Cuenta con mobiliario en las celdas',24,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(475,15,NULL,1,'cuenta_con_colchones_ignifugos','Cuenta con colchones ignífugos',25,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(476,15,NULL,NULL,'jurisdicciones_dentro_de_la_provincia_en_las_que_tiene_al_d231ec','Jurisdicciones dentro de la provincia en las que tiene alcancce territorial el dispositivo',26,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(477,15,NULL,NULL,'tiempo_maximo_de_permanencia_dentro_del_dispositivo_en_horas','Tiempo máximo de permanencia dentro del dispositivo (en horas)',27,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(478,16,NULL,NULL,'nombre_del_dispositvo','Nombre del dispositvo',1,'TEXTO',120,'SIN_NORMALIZAR',1,NULL),(479,16,NULL,NULL,'dependencia_institucional','Dependencia institucional',2,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(480,16,NULL,NULL,'telefono','Teléfono',3,'TEXTO',50,'SIN_NORMALIZAR',0,NULL),(481,16,NULL,1,'cuenta_con_resolucion_de_creacion','Cuenta con resolución de creación',4,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(482,16,NULL,7,'cuenta_con_protocolos_de_articulacion_interministerial_co_5e1a90','Cuenta con protocolos de articulación interministerial. Con qué áreas',5,'TEXTO',34,'SIN_NORMALIZAR',0,NULL),(483,16,NULL,1,'cuenta_con_protocolo_de_denuncias_por_malos_tratos','Cuenta con protocolo de denuncias por malos tratos',6,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(484,16,NULL,NULL,'cantidad_de_agentes_equipo_tecnico_y_profesional_incluye_efd962','Cantidad de agentes: equipo técnico y profesional (incluye cuidadores)',7,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(485,16,NULL,NULL,'jurisdicciones_dentro_de_la_provincia_en_las_que_tiene_al_d231ec','Jurisdicciones dentro de la provincia en las que tiene alcancce territorial el dispositivo',8,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(486,16,NULL,NULL,'tiempo_maximo_de_permanencia_dentro_del_dispositivo_en_horas','Tiempo máximo de permanencia dentro del dispositivo (en horas)',9,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(490,18,NULL,NULL,'apellido_s','Apellido/s',1,'TEXTO',120,'SIN_NORMALIZAR',1,NULL),(491,18,NULL,NULL,'nombre_s','Nombre/s',2,'TEXTO',120,'SIN_NORMALIZAR',1,NULL),(492,18,NULL,182,'tipo_de_documento_de_identidad','Tipo de documento de identidad',3,'TEXTO',26,'SIN_NORMALIZAR',0,NULL),(493,18,NULL,NULL,'n_dni','Nº DNI',4,'TEXTO',15,'SIN_NORMALIZAR',1,NULL),(494,18,NULL,NULL,'n_de_cuil','Nº de CUIL',5,'TEXTO',13,'SIN_NORMALIZAR',1,NULL),(495,18,NULL,NULL,'otro_nuero_de_documentacion_de_identidad_si_no_cuenta_con_dni','Otro núero de documentación de identidad (si no cuenta con DNI)',6,'TEXTO',15,'SIN_NORMALIZAR',1,NULL),(496,18,NULL,46,'genero','Género',7,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(497,18,NULL,190,'pais_de_nacimiento','País de nacimiento',8,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(498,18,NULL,NULL,'fecha_de_nacimiento','Fecha de nacimiento',9,'FECHA',NULL,'SIN_NORMALIZAR',1,NULL),(499,18,NULL,NULL,'domicilio_actual','Domicilio actual',10,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(500,18,NULL,NULL,'provincia','Provincia',11,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(501,18,NULL,NULL,'departamento','Departamento',12,'FECHA',NULL,'SIN_NORMALIZAR',0,NULL),(502,18,NULL,NULL,'localidad','Localidad',13,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(503,18,NULL,43,'pertenece_a_pueblo_originario_o_se_identifica_con_algun_p_003571','¿Pertenece a pueblo originario? (o se identifica con algún pueblo originario?)',14,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(504,18,NULL,NULL,'pueblo_originario_especificar','Pueblo originario (especificar)',15,'TEXTO',NULL,'SIN_NORMALIZAR',0,NULL),(505,18,NULL,59,'presenta_algun_tipo_de_discapacidad','¿Presenta algún tipo de discapacidad?',16,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(506,18,NULL,192,'posee_cud','¿Posee CUD?',17,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(507,18,NULL,51,'cobertura_salud','Cobertura salud',18,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(508,18,NULL,43,'tiene_hijos_as','¿Tiene hijos/as?',19,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(509,18,NULL,NULL,'fecha_de_actualizacion','Fecha de actualización',20,'FECHA',NULL,'SIN_NORMALIZAR',0,NULL),(510,19,NULL,NULL,'provincia','PROVINCIA',1,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(511,19,NULL,NULL,'depto','DEPTO',2,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(512,19,NULL,NULL,'localidad','LOCALIDAD',3,'TEXTO',120,'SIN_NORMALIZAR',0,NULL),(513,20,26,NULL,'id_del_nino_nina_o_adolescente','ID del Niño, niña o Adolescente',1,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(514,20,26,45,'apellido_s','Apellido/s',2,'TEXTO',20,'SIN_NORMALIZAR',1,NULL),(515,20,26,NULL,'nombre_s','Nombre/s',3,'TEXTO',120,'SIN_NORMALIZAR',1,NULL),(516,20,26,NULL,'cuil_o_documento_de_identidad','Cuil o documento de identidad',4,'TEXTO',13,'SIN_NORMALIZAR',1,NULL),(517,20,27,76,'origen_de_la_demanda','Origen de la demanda',5,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(518,20,27,260,'organismo_que_toma_la_mpe','Organismo que toma la MPE',6,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(519,20,27,NULL,'fecha_de_inicio_mpe','Fecha de inicio MPE',7,'FECHA',NULL,'SIN_NORMALIZAR',0,NULL),(520,20,27,76,'ultima_fecha_de_renovacion','Última fecha de renovación',8,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(521,20,27,NULL,'motivo_de_toma_de_mpe','Motivo de toma de MPE',9,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(522,20,27,NULL,'submotivo_de_toma_de_mpe','Submotivo de toma de MPE',10,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(523,20,27,43,'elevacion_dictamen_mpe_a_juzgado','Elevación dictamen MPE a juzgado',11,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(524,20,27,43,'control_de_legalidad_por_autoridad_judicial','Control de legalidad por autoridad judicial',12,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(525,20,27,83,'modalidad_de_cuidado','Modalidad de cuidado',13,'TEXTO',22,'SIN_NORMALIZAR',0,NULL),(526,20,28,NULL,'id_dispositivo_residencial','ID dispositivo residencial',14,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(527,20,28,NULL,'nombre_de_la_residencia_hogar','Nombre de la residencia/hogar',15,'TEXTO',120,'SIN_NORMALIZAR',1,NULL),(528,20,29,NULL,'id_familia','ID familia',16,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(529,20,29,NULL,'familia','Familia',17,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(530,20,29,NULL,'departamento_de_residencia_de_la_familia_dispositivo_fami_597d04','Departamento de residencia de la familia (dispositivo familiar)',18,'FECHA',NULL,'SIN_NORMALIZAR',0,NULL),(531,20,30,NULL,'id_familia_ampliada','ID familia ampliada',19,'FECHA',NULL,'SIN_NORMALIZAR',0,NULL),(532,20,30,NULL,'familia_ampliada','Familia Ampliada',20,'FECHA',NULL,'SIN_NORMALIZAR',0,NULL),(533,20,30,NULL,'vinculo_con_el_nya','Vínculo con el NyA',21,'FECHA',NULL,'SIN_NORMALIZAR',0,NULL),(534,20,30,NULL,'departamento_de_residencia_de_la_familia_dispositivo_fami_e8c08b','Departamento de residencia de la familia (dispositivo familiar)',22,'FECHA',NULL,'SIN_NORMALIZAR',0,NULL),(535,20,31,77,'tipo_de_proyecto_de_restitucion','Tipo de proyecto de restitución',23,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(536,20,31,43,'decreto_judicial_de_adoptabilidad','Decreto judicial de adoptabilidad',24,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(537,20,31,43,'solicitud_inclusion_proy_autonomia','Solicitud inclusión proy. autonomía',25,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(538,20,32,43,'asiste_actualmente_a_una_institucion_educativa','¿Asiste actualmente a una institución educativa?',26,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(539,20,32,42,'maximo_nivel_educativo_alcanzado','Máximo nivel educativo alcanzado',27,'TEXTO',24,'SIN_NORMALIZAR',0,NULL),(540,20,32,43,'consumo_problematico_de_sustancias','Consumo problemático de sustancias',28,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(541,20,33,NULL,'fecha_de_cese','Fecha de cese',29,'FECHA',NULL,'SIN_NORMALIZAR',0,NULL),(542,20,33,263,'motivo_de_cese','Motivo de cese',30,'TEXTO',56,'SIN_NORMALIZAR',0,NULL),(543,20,NULL,NULL,'observaciones','Observaciones',31,'TEXTO',NULL,'SIN_NORMALIZAR',0,NULL),(544,21,NULL,NULL,'fecha_del_relevamiento','Fecha del relevamiento',1,'FECHA',NULL,'SIN_NORMALIZAR',1,NULL),(545,21,34,45,'provincia','Provincia',2,'TEXTO',20,'SIN_NORMALIZAR',0,'Identificar la provincia o jurisdicción correspondiente'),(546,21,34,NULL,'nombre_del_dispositivo','Nombre del dispositivo',3,'TEXTO',120,'SIN_NORMALIZAR',1,'Consignar el nombre completo del dispositivo (Establecimiento o Programa) en el cual se encuentran los jóvenes incluidos en el presente listado.'),(547,21,34,105,'tipo_de_dispositivo','Tipo de dispositivo',4,'TEXTO',42,'SIN_NORMALIZAR',0,'Seleccionar el tipo de dispositivo correspondiente de la lista desplegable: Medida Penal en Territorio, Establecimiento de Restricción de Libertad, Establecimiento de Privación de Libertad o Prisión Domiciliaria.'),(548,21,34,NULL,'dependencia_institucional','Dependencia institucional',5,'TEXTO',255,'SIN_NORMALIZAR',0,'Indicar el organismo del cual depende el dispositivo con el siguiente orden: Ministerio, Secretaría, Dirección (según corresponda).'),(549,21,34,NULL,'localidad','Localidad',6,'TEXTO',120,'SIN_NORMALIZAR',0,'Consignar localidad en la cual se encuentra ubicado el dispositivo.'),(550,21,35,NULL,'id_del_nino_nina_o_adolescente','ID del Niño, niña o Adolescente',7,'ENTERO',NULL,'SIN_NORMALIZAR',0,'Identificador alfanumérico nominal único provincial asignado al NyA para seguimiento resguardando su identidad. En caso de existir.'),(551,21,35,NULL,'apellido_s','Apellido/s',8,'TEXTO',120,'SIN_NORMALIZAR',1,'Consignar el/los apellido/s del adolescente, tal como figura/n en su documentación.'),(552,21,35,NULL,'nombre_s','Nombre/s',9,'TEXTO',120,'SIN_NORMALIZAR',1,'Consignar el/los nombre/s del adolescente, tal como figura/n en su documentación.'),(553,21,35,44,'situacion_de_documentacion','Situación de documentación',10,'TEXTO',24,'SIN_NORMALIZAR',0,'Consignar la situación de cada adolescente en relación a la documentación de acuerdo a las siguientes categorías que se encuentran en la lista desplegable: Posee N° DNI, No posee N° DNI, DNI en trámite, Posee N° documento extranjero o Sin datos. Cabe destacar que las opciones Posee N° DNI y No posee N° DNI hacen referencia al hecho de que se haya realizado o no el trámite para la obtención del Documento Nacional de Identidad. En este sentido, es importante mencionar que la indagación aquí realizada no permite identificar otro tipo de situaciones problemáticas vinculadas con la documentación, tales como la falta de renovación, o casos de extravío o deterioro de los mismos, entre otras.'),(554,21,35,NULL,'n_dni','Nº DNI',11,'TEXTO',15,'SIN_NORMALIZAR',0,'Informar el número de DNI del adolescente, sin puntos ni espacios.'),(555,21,35,47,'genero','Género',12,'TEXTO',20,'SIN_NORMALIZAR',0,'Utilizar las categorías: Maculino, Femenino, Otros, Sin datos que se encuentran en la lista desplegable.'),(556,21,35,41,'pais_de_nacimiento','País de nacimiento',13,'TEXTO',44,'SIN_NORMALIZAR',0,'Indicar el país de origen de cada adolescente según el desplegable incluido.'),(557,21,35,NULL,'fecha_de_nacimiento','Fecha de nacimiento',14,'FECHA',NULL,'SIN_NORMALIZAR',1,'Especificar la fecha de nacimiento del adolescente utilizando el siguiente formato: DD/MM/AAAA. Por ejemplo: 01/03/2001.'),(558,21,35,NULL,'edad','Edad',15,'ENTERO',NULL,'SIN_NORMALIZAR',0,'Consignar la edad del adolescente a la fecha del presente relevamiento.'),(559,21,35,94,'asiste_a_institucion_educativa','¿Asiste a institución educativa?',16,'TEXTO',22,'SIN_NORMALIZAR',0,'Seleccionar de la lista desplegable.'),(560,21,35,42,'maximo_nivel_educativo_alcanzado','Máximo nivel educativo alcanzado',17,'TEXTO',24,'SIN_NORMALIZAR',0,'Seleccionar en el menú desplegable, el nivel educativo alcanzado a la fecha del relevamiento.'),(561,21,35,43,'enfermedad_cronica','Enfermedad crónica',18,'TEXTO',20,'SIN_NORMALIZAR',0,'Indicar si el adolescente presenta alguna enfermedad crónica.'),(562,21,35,43,'consumo_problematico_de_sustancias','Consumo problemático de sustancias',19,'TEXTO',20,'SIN_NORMALIZAR',0,'Indicar si el adolescente presenta consumo problemático de sustancias.'),(563,21,35,43,'presenta_alguna_discapacidad','¿Presenta alguna discapacidad?',20,'TEXTO',20,'SIN_NORMALIZAR',0,'Indicar si el adolescente presenta alguna discapacidad. En caso de responder positivamente, en la columna siguiente deberá especificar el tipo de discapacidad.'),(564,21,35,59,'tipo_de_discapacidad','Tipo de discapacidad',21,'TEXTO',20,'SIN_NORMALIZAR',0,'Seleccionar el tipo de discapacidad según las opciones proporcionadas en el desplegable: visual, auditiva, mental, visceral, motora, otros (especificar en observaciones), sin datos.'),(565,21,35,61,'posee_cud','¿Posee CUD?',22,'TEXTO',20,'SIN_NORMALIZAR',0,'Responder según opciones del desplegable: Sí, No, En trámite, Sin datos. El Certificado Único de Discapacidad (CUD) es un documento que certifica la discapacidad de la persona y le permite acceder a derechos y prestaciones que brinda el Estado. El CUD es un documento público válido en todo el país que permite ejercer los derechos y acceder a las prestaciones previstas en las leyes nacionales 22.431 y 24.901.'),(566,21,35,97,'cobertura_salud','Cobertura salud',23,'TEXTO',22,'SIN_NORMALIZAR',0,'Responder según opciones del desplegable: PAMI, IOMA, Obra social provincial, Obra social privada, Prepaga, Sin cobertura, Sin datos'),(567,21,35,43,'se_identifica_con_algun_pueblo_originario','¿Se identifica con algún pueblo originario?',24,'TEXTO',20,'SIN_NORMALIZAR',0,'Consignar si el joven pertenece a un pueblo originario, utilizando las categorías Sí, No o Sin datos del desplegable. En caso de que la respuesta sea Sí , deberá especificarse en la columna siguiente el pueblo originario con el cual el adolescente se identifica, en caso de que la respuesta sea No, consignar en la columna siguiente No corresponde.'),(568,21,35,NULL,'pueblo_originario_especificar','Pueblo originario (especificar)',25,'TEXTO',NULL,'SIN_NORMALIZAR',0,'Pregunta abierta.'),(569,21,35,102,'asignacion_universal_por_hijo','Asignación Universal por Hijo',26,'TEXTO',27,'SIN_NORMALIZAR',0,'Indicar si el joven percibe o no la Asignación Universal por Hijo de acuerdo a los ítems de respuesta desplegables. Debe tenerse en cuenta que aunque el/la adolescente sea titular de la percepción del beneficio no implica que sea la persona que recibe el dinero de la asignación. La percepción refiere sólo a la titularidad.'),(570,21,35,43,'tiene_hijos_as','¿Tiene hijos/as?',27,'TEXTO',20,'SIN_NORMALIZAR',0,'Completarse por Sí, No o Sin datos. Es indistinto si los/as hijos/as se encuentran en el dispositivo junto a sus progenitores/as.'),(571,21,36,NULL,'descripcion_causa_penal_contravencion','Descripción causa penal/contravención',28,'TEXTO',NULL,'SIN_NORMALIZAR',0,'Identificar la causa penal o contravención por la cual el/la adolescente se encuentra en el dispositivo. En caso de que exista más de una causa, por favor consignar todas.'),(572,21,36,NULL,'fecha_de_ingreso_al_dispositivo','Fecha de ingreso al dispositivo',29,'FECHA',NULL,'SIN_NORMALIZAR',0,'Especificar el día de ingreso del adolescente al dispositivo utilizando el siguiente formato DD/MD/AAAA. Ej.: 01/02/2021'),(573,21,36,103,'procedencia_inmediata','Procedencia inmediata',30,'TEXTO',42,'SIN_NORMALIZAR',0,'Consignar la procedencia inmediatamente anterior al ingreso al dispositivo, de acuerdo con las siguientes opciones: Policía provincial, Gendarmería, Prefectura, Infantería, CAD, Comisaría, Juzgado (sin intervención de otro dispositivo penal juvenil), Establecimiento de privación de libertad, Establecimiento de restricción de libertad, Medida penal en territorio, Defensoría de menores, Otros o Sin datos.'),(574,21,36,NULL,'especificar_procedencia','Especificar procedencia',31,'TEXTO',NULL,'SIN_NORMALIZAR',0,'En caso de ser derivado por una comisaría, especificar el número de comisaría. Si se trata de un CAD, Establecimiento de privación de libertad, Establecimiento de restricción de libertad, Medida penal en territorio, indicar el nombre del dispositivo y localización geográfica.'),(575,21,36,NULL,'dependencia_judicial','Dependencia judicial',32,'TEXTO',255,'SIN_NORMALIZAR',0,'Consignar la dependencia Judicial.'),(576,21,36,104,'situacion_procesal','Situación procesal',33,'TEXTO',30,'SIN_NORMALIZAR',0,'Consignar la situación procesal de el/la adolescente utilizando las categorías del desplegable: Investigación penal, Elevación a juicio, Declaración de responsabilidad, Ejecución penal, Sentencia a revisión, Otros, Sin datos. En caso de encontrarse en etapa de Ejecución Penal, especificar el monto de la pena en la columna siguiente.'),(577,21,36,NULL,'monto_de_la_pena','Monto de la pena',34,'DECIMAL',NULL,'SIN_NORMALIZAR',0,'Pregunta abierta. Entrada numérica según cada caso individual.'),(578,21,36,NULL,'fecha_de_egreso_del_dispositivo','Fecha de egreso del dispositivo',35,'FECHA',NULL,'SIN_NORMALIZAR',0,'Especificar el día de egreso del adolescente al dispositivo utilizando el siguiente formato DD/MD/AAAA. Ej.: 01/02/2021'),(579,21,36,98,'destino_al_egreso','Destino al egreso',36,'TEXTO',35,'SIN_NORMALIZAR',0,'Responder utilizando las categorías del desplegable.'),(580,21,36,NULL,'especificar_destino_al_egreso','Especificar destino al egreso',37,'TEXTO',255,'SIN_NORMALIZAR',0,'En caso de que en la columna anterior se haya elegido egreso a un dispositivo penal, consignar el nombre del mismo.'),(581,21,NULL,NULL,'observaciones','Observaciones',38,'TEXTO',NULL,'SIN_NORMALIZAR',0,NULL),(582,22,NULL,NULL,'fecha_del_relevamiento','Fecha del relevamiento',1,'FECHA',NULL,'SIN_NORMALIZAR',1,NULL),(583,22,37,45,'provincia','Provincia',2,'TEXTO',20,'SIN_NORMALIZAR',0,'Identificar la provincia o jurisdicción correspondiente'),(584,22,37,NULL,'nombre_del_dispositivo','Nombre del dispositivo',3,'TEXTO',120,'SIN_NORMALIZAR',1,'Consignar el nombre completo del dispositivo (Establecimiento o Programa) en el cual se encuentran los jóvenes incluidos en el presente listado.'),(585,22,37,107,'tipo_de_dispositivo','Tipo de dispositivo',4,'TEXTO',31,'SIN_NORMALIZAR',0,'Seleccionar el tipo de dispositivo correspondiente de la lista desplegable: Medida Penal en Territorio, Establecimiento de Restricción de Libertad, Establecimiento de Privación de Libertad o Prisión Domiciliaria.'),(586,22,37,NULL,'dependencia_institucional','Dependencia institucional',5,'TEXTO',255,'SIN_NORMALIZAR',0,'Indicar el organismo del cual depende el dispositivo con el siguiente orden: Ministerio, Secretaría, Dirección (según corresponda).'),(587,22,37,NULL,'localidad','Localidad',6,'TEXTO',120,'SIN_NORMALIZAR',0,'Consignar localidad en la cual se encuentra ubicado el dispositivo.'),(588,22,38,NULL,'id_del_nino_nina_o_adolescente','ID del Niño, niña o Adolescente',7,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(589,22,38,NULL,'apellido_s','Apellido/s',8,'TEXTO',120,'SIN_NORMALIZAR',1,NULL),(590,22,38,NULL,'nombre_s','Nombre/s',9,'TEXTO',120,'SIN_NORMALIZAR',1,NULL),(591,22,38,44,'situacion_de_documentacion','Situación de documentación',10,'TEXTO',24,'SIN_NORMALIZAR',0,NULL),(592,22,38,NULL,'n_dni','Nº DNI',11,'TEXTO',15,'SIN_NORMALIZAR',0,NULL),(593,22,38,47,'genero','Género',12,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(594,22,38,41,'pais_de_nacimiento','País de nacimiento',13,'TEXTO',44,'SIN_NORMALIZAR',0,NULL),(595,22,38,NULL,'fecha_de_nacimiento','Fecha de nacimiento',14,'FECHA',NULL,'SIN_NORMALIZAR',1,NULL),(596,22,38,NULL,'edad','Edad',15,'ENTERO',NULL,'SIN_NORMALIZAR',0,NULL),(597,22,38,94,'asiste_a_institucion_educativa','¿Asiste a institución educativa?',16,'TEXTO',22,'SIN_NORMALIZAR',0,NULL),(598,22,38,42,'maximo_nivel_educativo_alcanzado','Máximo nivel educativo alcanzado',17,'TEXTO',24,'SIN_NORMALIZAR',0,NULL),(599,22,38,43,'enfermedad_cronica','Enfermedad crónica',18,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(600,22,38,43,'consumo_problematico_de_sustancias','Consumo problemático de sustancias',19,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(601,22,38,43,'presenta_alguna_discapacidad','¿Presenta alguna discapacidad?',20,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(602,22,38,59,'tipo_de_discapacidad','Tipo de discapacidad',21,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(603,22,38,61,'posee_cud','¿Posee CUD?',22,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(604,22,38,97,'cobertura_salud','Cobertura salud',23,'TEXTO',22,'SIN_NORMALIZAR',0,NULL),(605,22,38,43,'se_identifica_con_algun_pueblo_originario','¿Se identifica con algún pueblo originario?',24,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(606,22,38,NULL,'pueblo_originario_especificar','Pueblo originario (especificar)',25,'TEXTO',NULL,'SIN_NORMALIZAR',0,NULL),(607,22,38,43,'tiene_hijos_as','¿Tiene hijos/as?',26,'TEXTO',20,'SIN_NORMALIZAR',0,NULL),(608,22,39,108,'motivo_de_la_aprehension','Motivo de la aprehensión',27,'TEXTO',28,'SIN_NORMALIZAR',0,NULL),(609,22,39,NULL,'descripcion_causa_contravencion','Descripción causa/contravención',28,'TEXTO',NULL,'SIN_NORMALIZAR',0,'Identificar la causa penal o contravención por la cual el/la adolescente se encuentra en el dispositivo. En caso de que exista más de una causa, por favor consignar todas.'),(610,22,39,NULL,'fecha_de_ingreso_al_dispositivo','Fecha de ingreso al dispositivo',29,'FECHA',NULL,'SIN_NORMALIZAR',0,NULL),(611,22,39,NULL,'hora_de_ingreso_al_dispositivo','Hora de ingreso al dispositivo',30,'HORA',NULL,'SIN_NORMALIZAR',0,'Consignar la hora de ingreso al establecimiento utilizando el siguiente formato HH:MM, en formato 24 hs. Ej.: 22:30. Recuerde utilizar los dos puntos para separar hora de minutos.'),(612,22,39,109,'fuerza_de_seguridad','Fuerza de seguridad',31,'TEXTO',20,'SIN_NORMALIZAR',0,'Identificar la fuerza de seguridad que ha efectuado la aprehensión de acuerdo con las opciones que aparecen en el desplegable: Policía Municipal, Policía Provincial, Policía Federal, Gendarmería, Prefectura, Infantería, Otros, Sin datos.'),(613,22,39,NULL,'n_comisaria_o_dependencia','N° comisaría o dependencia',32,'TEXTO',255,'SIN_NORMALIZAR',0,'Detallar la dependencia a la que pertenece la fuerza que ha efectuado la aprehensión, de acuerdo con las siguientes opciones: Comisaría N° XX, Alcaldía N° XX, u otro/s.'),(614,22,39,NULL,'departamento_de_la_dependencia','Departamento de la dependencia',33,'TEXTO',255,'SIN_NORMALIZAR',0,'Especificar el departamento en el cual se ubica la dependencia policial de procedencia que efectuó la aprehensión.'),(615,22,39,43,'paso_por_comisaria_previo_ingreso','¿Pasó por comisaría previo ingreso?',34,'TEXTO',20,'SIN_NORMALIZAR',0,'Consignar si el adolescente pasó o no por una comisaría (tanto por trámites policiales y/o permanencia) previamente a su ingreso al establecimiento especializado de aprehensión según desplegable.'),(616,22,39,110,'tiempo_en_comisaria','Tiempo en comisaría',35,'TEXTO',20,'SIN_NORMALIZAR',0,'Especificar el tiempo de permanencia en la comisaría, de acuerdo con las opciones que ofrece el listado desplegable: Hasta 12 hs., Entre 12 y 24 hs., etc. Seleccionar del listado desplegable. En caso que el NNyA no haya pasado previamente por una dependencia policial, seleccionar No corresponde.'),(617,22,39,NULL,'fecha_de_egreso_del_dispositivo','Fecha de egreso del dispositivo',36,'FECHA',NULL,'SIN_NORMALIZAR',0,NULL),(618,22,39,NULL,'hora_de_egreso_del_dispositivo','Hora de egreso del dispositivo',37,'HORA',NULL,'SIN_NORMALIZAR',0,'Consignar la hora de egreso del dispositivo utilizando el siguiente formato HH:MM, en formato 24 hs. Ej.: 22:30. Recuerde utilizar los dos puntos para separar hora de minutos.'),(619,22,39,98,'destino_al_egreso','Destino al egreso',38,'TEXTO',35,'SIN_NORMALIZAR',0,NULL),(620,22,39,NULL,'especificar_destino_al_egreso','Especificar destino al egreso',39,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(621,22,39,43,'denuncia_por_apremios_ilegales','Denuncia por apremios ilegales',40,'TEXTO',20,'SIN_NORMALIZAR',0,'Registrar si la institución realizó denuncia por apremios ilegales en el proceso de detención por parte de las fuerzas de seguridad, siempre que el niño, niña o adolescente lo haya manifestado o el equipo técnico lo haya detectado (Ley 26.061 Ley de protección integral de niños, niñas y adolescente: \"El deber de informar\"/Decreto 41/99 Código de ética de la función pública Art. 31 Obligación de denunciar/Códigos penales procesales de cada jurisdicción). Seleccionar Sí o No en el desplegable.'),(622,22,39,NULL,'dependencia_judicial','Dependencia judicial',41,'TEXTO',255,'SIN_NORMALIZAR',0,NULL),(623,22,39,NULL,'edad_al_ingreso','Edad al ingreso',42,'ENTERO',NULL,'SIN_NORMALIZAR',0,'Consignar la edad del adolescente a la fecha del ingreso al dispositivo.'),(624,22,NULL,NULL,'observaciones','Observaciones',43,'TEXTO',NULL,'SIN_NORMALIZAR',0,NULL);
/*!40000 ALTER TABLE `runac_c1_campo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c1_campo_regla`
--

DROP TABLE IF EXISTS `runac_c1_campo_regla`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c1_campo_regla` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `campo_id` bigint NOT NULL COMMENT 'Campo sobre el que se aplica la regla.',
  `regla_id` bigint NOT NULL COMMENT 'Regla que debe aplicarse.',
  `severidad` enum('BLOQUEANTE','ADVERTENCIA') NOT NULL COMMENT 'Atributo de la regla APLICADA, no del tipo: un mismo tipo puede ser bloqueante en un campo y advertencia en otro.',
  `mensaje` text COMMENT 'Mensaje al usuario, en lenguaje claro. Vive en la definición y no en el código, de modo que pueda mejorarse sin desarrollo.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c1_campo_regla_index_10` (`campo_id`,`regla_id`),
  KEY `regla_id` (`regla_id`),
  CONSTRAINT `runac_c1_campo_regla_ibfk_1` FOREIGN KEY (`campo_id`) REFERENCES `runac_c1_campo` (`id`),
  CONSTRAINT `runac_c1_campo_regla_ibfk_2` FOREIGN KEY (`regla_id`) REFERENCES `runac_c1_regla` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=246 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Relaciona los campos con las reglas que deben aplicarse, con su severidad y su mensaje.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c1_campo_regla`
--

LOCK TABLES `runac_c1_campo_regla` WRITE;
/*!40000 ALTER TABLE `runac_c1_campo_regla` DISABLE KEYS */;
INSERT INTO `runac_c1_campo_regla` VALUES (1,183,1,'ADVERTENCIA',NULL),(2,192,2,'ADVERTENCIA',NULL),(3,196,3,'BLOQUEANTE',NULL),(4,196,4,'BLOQUEANTE',NULL),(5,197,5,'BLOQUEANTE',NULL),(6,197,6,'ADVERTENCIA',NULL),(7,200,7,'ADVERTENCIA',NULL),(8,201,8,'ADVERTENCIA',NULL),(9,215,9,'ADVERTENCIA',NULL),(10,216,10,'ADVERTENCIA',NULL),(11,220,11,'ADVERTENCIA',NULL),(12,227,12,'ADVERTENCIA',NULL),(13,234,13,'ADVERTENCIA',NULL),(14,243,14,'ADVERTENCIA',NULL),(15,247,15,'ADVERTENCIA',NULL),(16,257,16,'BLOQUEANTE',NULL),(17,257,17,'BLOQUEANTE',NULL),(18,258,18,'BLOQUEANTE',NULL),(19,258,19,'ADVERTENCIA',NULL),(20,261,20,'ADVERTENCIA',NULL),(21,262,21,'ADVERTENCIA',NULL),(22,268,22,'ADVERTENCIA',NULL),(23,269,23,'ADVERTENCIA',NULL),(24,272,24,'ADVERTENCIA',NULL),(28,278,28,'ADVERTENCIA',NULL),(63,196,63,'BLOQUEANTE','La situación de documentación dice que no hay número de DNI, y sin embargo el campo trae uno. Hay que corregir una de las dos cosas en el Excel.'),(64,257,64,'BLOQUEANTE','La situación de documentación dice que no hay número de DNI, y sin embargo el campo trae uno. Hay que corregir una de las dos cosas en el Excel.'),(69,196,69,'BLOQUEANTE','La situación de documentación dice que la persona tiene número de DNI, y el campo está vacío.'),(70,257,70,'BLOQUEANTE','La situación de documentación dice que la persona tiene número de DNI, y el campo está vacío.'),(77,493,77,'BLOQUEANTE',NULL),(78,494,78,'BLOQUEANTE',NULL),(79,494,79,'ADVERTENCIA',NULL),(80,495,80,'BLOQUEANTE',NULL),(81,498,81,'ADVERTENCIA',NULL),(82,501,82,'ADVERTENCIA',NULL),(83,504,83,'ADVERTENCIA',NULL),(84,509,84,'ADVERTENCIA',NULL),(85,516,85,'BLOQUEANTE',NULL),(86,516,86,'ADVERTENCIA',NULL),(87,519,28,'ADVERTENCIA',NULL),(88,530,88,'ADVERTENCIA',NULL),(91,533,91,'ADVERTENCIA',NULL),(92,534,92,'ADVERTENCIA',NULL),(93,541,93,'ADVERTENCIA',NULL),(94,541,94,'BLOQUEANTE',NULL),(95,544,29,'ADVERTENCIA',NULL),(96,554,30,'BLOQUEANTE',NULL),(97,554,31,'BLOQUEANTE',NULL),(98,557,32,'ADVERTENCIA',NULL),(99,558,33,'ADVERTENCIA',NULL),(100,564,34,'ADVERTENCIA',NULL),(101,565,35,'ADVERTENCIA',NULL),(102,568,36,'ADVERTENCIA',NULL),(103,572,37,'ADVERTENCIA',NULL),(104,574,38,'ADVERTENCIA',NULL),(105,578,39,'ADVERTENCIA',NULL),(106,578,40,'BLOQUEANTE',NULL),(109,580,43,'ADVERTENCIA',NULL),(110,582,29,'ADVERTENCIA',NULL),(111,592,30,'BLOQUEANTE',NULL),(112,592,31,'BLOQUEANTE',NULL),(113,595,32,'ADVERTENCIA',NULL),(114,596,33,'ADVERTENCIA',NULL),(115,602,34,'ADVERTENCIA',NULL),(116,603,35,'ADVERTENCIA',NULL),(117,606,36,'ADVERTENCIA',NULL),(118,610,37,'ADVERTENCIA',NULL),(120,617,39,'ADVERTENCIA',NULL),(121,617,40,'BLOQUEANTE',NULL),(126,620,43,'ADVERTENCIA',NULL),(127,623,61,'ADVERTENCIA',NULL),(129,592,72,'BLOQUEANTE','La situación de documentación dice que la persona tiene número de DNI, y el campo está vacío.'),(130,592,66,'BLOQUEANTE','La situación de documentación dice que no hay número de DNI, y sin embargo el campo trae uno. Hay que corregir una de las dos cosas en el Excel.'),(131,554,71,'BLOQUEANTE','La situación de documentación dice que la persona tiene número de DNI, y el campo está vacío.'),(132,554,65,'BLOQUEANTE','La situación de documentación dice que no hay número de DNI, y sin embargo el campo trae uno. Hay que corregir una de las dos cosas en el Excel.'),(136,584,68,'ADVERTENCIA','El dispositivo no figura en el archivo de dispositivos penales de este período. Puede ser un nombre escrito distinto o un dispositivo que falta declarar.'),(137,546,67,'ADVERTENCIA','El dispositivo no figura en el archivo de dispositivos penales de este período. Puede ser un nombre escrito distinto o un dispositivo que falta declarar.'),(143,250,136,'ADVERTENCIA','La residencia no figura en el archivo de dispositivos de cuidado de este período. Puede ser un nombre escrito distinto o un dispositivo que falta declarar.'),(144,527,136,'ADVERTENCIA','La residencia no figura en el archivo de dispositivos de cuidado de este período. Puede ser un nombre escrito distinto o un dispositivo que falta declarar.'),(146,141,139,'ADVERTENCIA','Es una cantidad de chicas y chicos inusualmente alta. Conviene revisar el dato.'),(147,274,142,'ADVERTENCIA','Un identificador empieza en uno.'),(148,279,140,'ADVERTENCIA','Son más de diez años de permanencia. Conviene revisar el dato.'),(149,378,138,'ADVERTENCIA','Es una cantidad de personal inusualmente alta. Conviene revisar el dato.'),(150,379,138,'ADVERTENCIA','Es una cantidad de personal inusualmente alta. Conviene revisar el dato.'),(151,380,138,'ADVERTENCIA','Es una cantidad de personal inusualmente alta. Conviene revisar el dato.'),(152,381,138,'ADVERTENCIA','Es una cantidad de personal inusualmente alta. Conviene revisar el dato.'),(153,388,137,'BLOQUEANTE','Son más horas de las que tiene una semana: el dato no puede ser correcto.'),(154,391,137,'BLOQUEANTE','Son más horas de las que tiene una semana: el dato no puede ser correcto.'),(155,393,137,'BLOQUEANTE','Son más horas de las que tiene una semana: el dato no puede ser correcto.'),(156,395,137,'BLOQUEANTE','Son más horas de las que tiene una semana: el dato no puede ser correcto.'),(157,396,137,'BLOQUEANTE','Son más horas de las que tiene una semana: el dato no puede ser correcto.'),(158,420,138,'ADVERTENCIA','Es una cantidad de personal inusualmente alta. Conviene revisar el dato.'),(159,421,138,'ADVERTENCIA','Es una cantidad de personal inusualmente alta. Conviene revisar el dato.'),(160,422,138,'ADVERTENCIA','Es una cantidad de personal inusualmente alta. Conviene revisar el dato.'),(161,423,138,'ADVERTENCIA','Es una cantidad de personal inusualmente alta. Conviene revisar el dato.'),(162,424,137,'BLOQUEANTE','Son más horas de las que tiene una semana: el dato no puede ser correcto.'),(163,427,137,'BLOQUEANTE','Son más horas de las que tiene una semana: el dato no puede ser correcto.'),(164,429,137,'BLOQUEANTE','Son más horas de las que tiene una semana: el dato no puede ser correcto.'),(165,431,137,'BLOQUEANTE','Son más horas de las que tiene una semana: el dato no puede ser correcto.'),(166,432,137,'BLOQUEANTE','Son más horas de las que tiene una semana: el dato no puede ser correcto.'),(167,448,138,'ADVERTENCIA','Es una cantidad de personal inusualmente alta. Conviene revisar el dato.'),(168,468,138,'ADVERTENCIA','Es una cantidad de personal inusualmente alta. Conviene revisar el dato.'),(169,469,138,'ADVERTENCIA','Es una cantidad de personal inusualmente alta. Conviene revisar el dato.'),(170,470,138,'ADVERTENCIA','Es una cantidad de personal inusualmente alta. Conviene revisar el dato.'),(171,471,138,'ADVERTENCIA','Es una cantidad de personal inusualmente alta. Conviene revisar el dato.'),(172,484,138,'ADVERTENCIA','Es una cantidad de personal inusualmente alta. Conviene revisar el dato.'),(173,528,142,'ADVERTENCIA','Un identificador empieza en uno.'),(174,550,142,'ADVERTENCIA','Un identificador empieza en uno.'),(175,577,141,'ADVERTENCIA','El monto de la pena no puede ser negativo.'),(177,141,145,'BLOQUEANTE','Ese número de chicas y chicos no puede ser. Hay que corregirlo en el Excel.'),(178,201,147,'BLOQUEANTE','Esa edad no puede ser. Hay que corregirla en el Excel.'),(179,262,147,'BLOQUEANTE','Esa edad no puede ser. Hay que corregirla en el Excel.'),(180,274,149,'BLOQUEANTE','Ese identificador no puede ser. Hay que corregirlo en el Excel.'),(181,279,146,'BLOQUEANTE','Esa cantidad de días no puede ser. Hay que corregirla en el Excel.'),(182,378,144,'BLOQUEANTE','Ese número de personas no puede ser. Hay que corregirlo en el Excel.'),(183,379,144,'BLOQUEANTE','Ese número de personas no puede ser. Hay que corregirlo en el Excel.'),(184,380,144,'BLOQUEANTE','Ese número de personas no puede ser. Hay que corregirlo en el Excel.'),(185,381,144,'BLOQUEANTE','Ese número de personas no puede ser. Hay que corregirlo en el Excel.'),(186,420,144,'BLOQUEANTE','Ese número de personas no puede ser. Hay que corregirlo en el Excel.'),(187,421,144,'BLOQUEANTE','Ese número de personas no puede ser. Hay que corregirlo en el Excel.'),(188,422,144,'BLOQUEANTE','Ese número de personas no puede ser. Hay que corregirlo en el Excel.'),(189,423,144,'BLOQUEANTE','Ese número de personas no puede ser. Hay que corregirlo en el Excel.'),(190,448,144,'BLOQUEANTE','Ese número de personas no puede ser. Hay que corregirlo en el Excel.'),(191,468,144,'BLOQUEANTE','Ese número de personas no puede ser. Hay que corregirlo en el Excel.'),(192,469,144,'BLOQUEANTE','Ese número de personas no puede ser. Hay que corregirlo en el Excel.'),(193,470,144,'BLOQUEANTE','Ese número de personas no puede ser. Hay que corregirlo en el Excel.'),(194,471,144,'BLOQUEANTE','Ese número de personas no puede ser. Hay que corregirlo en el Excel.'),(195,484,144,'BLOQUEANTE','Ese número de personas no puede ser. Hay que corregirlo en el Excel.'),(196,528,149,'BLOQUEANTE','Ese identificador no puede ser. Hay que corregirlo en el Excel.'),(197,550,149,'BLOQUEANTE','Ese identificador no puede ser. Hay que corregirlo en el Excel.'),(198,558,147,'BLOQUEANTE','Esa edad no puede ser. Hay que corregirla en el Excel.'),(199,577,148,'BLOQUEANTE','Ese monto no puede ser. Hay que corregirlo en el Excel.'),(200,596,147,'BLOQUEANTE','Esa edad no puede ser. Hay que corregirla en el Excel.'),(208,374,139,'ADVERTENCIA',NULL),(209,375,139,'ADVERTENCIA',NULL),(210,418,139,'ADVERTENCIA',NULL),(211,419,139,'ADVERTENCIA',NULL),(212,466,139,'ADVERTENCIA',NULL),(213,467,139,'ADVERTENCIA',NULL),(214,140,139,'ADVERTENCIA',NULL),(215,374,145,'BLOQUEANTE',NULL),(216,375,145,'BLOQUEANTE',NULL),(217,418,145,'BLOQUEANTE',NULL),(218,419,145,'BLOQUEANTE',NULL),(219,466,145,'BLOQUEANTE',NULL),(220,467,145,'BLOQUEANTE',NULL),(221,140,145,'BLOQUEANTE',NULL),(222,477,151,'ADVERTENCIA',NULL),(223,486,151,'ADVERTENCIA',NULL),(225,477,152,'BLOQUEANTE',NULL),(226,486,152,'BLOQUEANTE',NULL),(228,623,147,'BLOQUEANTE',NULL),(239,250,153,'BLOQUEANTE',NULL),(241,250,154,'BLOQUEANTE',NULL),(242,276,142,'ADVERTENCIA',NULL),(243,276,149,'BLOQUEANTE',NULL);
/*!40000 ALTER TABLE `runac_c1_campo_regla` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c1_catalogo`
--

DROP TABLE IF EXISTS `runac_c1_catalogo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c1_catalogo` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `codigo` varchar(100) NOT NULL COMMENT 'Código técnico y estable del catálogo, escrito en snake_case.',
  `nombre` varchar(255) NOT NULL COMMENT 'Nombre descriptivo del catálogo.',
  `descripcion` text COMMENT 'Explicación funcional de los valores contenidos en el catálogo.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=287 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Define un conjunto cerrado de valores admitidos para uno o más campos. Una lista que reaparece en varios archivos se define una sola vez.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c1_catalogo`
--

LOCK TABLES `runac_c1_catalogo` WRITE;
/*!40000 ALTER TABLE `runac_c1_catalogo` DISABLE KEYS */;
INSERT INTO `runac_c1_catalogo` VALUES (1,'si_no','Sí / No / Sin datos','Huella 8e8482541b27. Aparece como: Cuenta con protocolo de requisa / Cuenta con protocolo de denuncias por malos tratos / Cuenta con protocolos de actuación ante conflictos entre pares / Cuenta con protocolo de sanciones / Cuenta con espacios para visitas socioafectivas / Tiene aulas destinadas a la educación obligatoria / Cuenta con espacio para talleres / Cuenta con asesoramiento técnico jurídico / Cuenta con patio abierto / Cuenta con patio techado / Cuenta con celdas secas / Cuenta con celdas humedas / Cuenta con mobiliario en las celdas / Cuenta con colchones ignífugos / Cuenta con espacio de grupalidad / Cuenta con resolución de creación / Cuenta con protocolos de ingreso / Protocolo de abordaje del suicidio / Cuenta con protocolo de abordaje del suicidio / ¿Tiene convenio con el OPN? (Solo para los de gestión no gubernamental y gestión mixta) / El dispositivo, ¿registra las intervenciones en el Sistema Nominal digital del OPN provincial? / ... WIFI en el dispositivo / ... para el ingreso del NyA al dispositivo / …para el abordaje de conflictos o violencia entre NyA / ... para el abordaje de crisis y urgencias en salud mental / grupos de hermanos? / NyA dolescentes con discapacidad / NyA con padecimiento de salud mental / NyA con uso o abuso de sustancias / Adolescentes con hijos / Aloja niños de 0 a 5 años / Aloja niños de 6 a 12 años / Aloja población de 13 a 17 años / Aloja población de 18 años y más / Recibió capacitación en PROMOCION DE CUIDADOS / Recibió capacitación en ALIMENTACION SALUDABLE / Recibió capacitación en REANIMACION CARDIOPULMONAR / Recibió capacitación en PRIMEROS AUXILIOS / Recibió capacitación en ABUSO SEXUAL INFANTIL /JUVENIL / Recibió capacitación en PARADIGMA DE PROTECCION INTEGRAL / Recibió capacitación en AUTONOMIA PROGRESIVA / Recibió capacitación en ABORDAJE EN SALUD MENTAL / Recibió capacitación en CONSUMOS PROBLEMATICOS / Recibió capacitación en CULTURA DIGITAL / Recibió capacitación en DISCAPACIDAD / Recibió capacitación en ADMINISTRACION FINANCIERA / Recibió capacitación en OTRAS TEMÁTICAS / ¿Promueve el contacto con la familia y/o referentes afectivos a través de redes, mails, cartas? / ¿Promueve el contacto con la familia y/o referentes afectivos a través de encuentros fuera del dispositivo? / ¿Promueve el contacto con la familia y/o referentes afectivos a través de visitas presenciales? / ¿Promueve el contacto con la familia y/o referentes afectivos a través de llamadas y videollamadas? / ¿Se identifica con algún pueblo originario? / ¿El referente se identifica con algún pueblo originario? / ¿Pertenece a pueblo originario? / ¿Tiene hijos/as? / ¿Pertenece a pueblo originario? (o se identifica con algún pueblo originario?).'),(2,'capacidad_de_alojamiento_mujeres_plazas_disponibles','Capacidad de alojamiento mujeres (plazas disponibles)','Huella 53b2ed9fb588. Aparece como: Capacidad de alojamiento mujeres (plazas disponibles) / Capacidad de alojamiento varones (plazas disponibles) / Cantidad de agentes: equipo técnico y profesional (incluye cuidadores) / Cantidad agentes de salud / Cantidad de personal: administrativo, limpieza, cocina y mantenimiento / Cantidad de personal seguridad / Cantidad de horas semanales destinadas al contacto presencial, afectivo/familiar / Cantidad de horas semanales dedicadas a la educación primaria / Cantidad de horas semanales dedicadas a la educación secundaria / Cantidad de horas semanales dedicadas a la formación profesional / Cantidad de horas semanales dedicadas a talleres deportivos y culturales / Jurisdicciones dentro de la provincia en las que el dispositivo tiene alcance / Jurisdicciones dentro de la provincia en las que tiene alcancce territorial el dispositivo / Tiempo máximo de permanencia dentro del dispositivo (en horas).'),(3,'nombre_del_dispositvo','Nombre del dispositvo','Huella ea631551f556. Aparece como: Nombre del dispositvo / Dependencia institucional / Localidad / Dirección / Teléfono.'),(4,'cuenta_con_proyecto_institucional','Cuenta con Proyecto Institucional','Huella 931f29dcace4. Aparece como: Cuenta con Proyecto Institucional / ¿Cuenta con Proyecto Institucional?.'),(5,'cumple_con_los_niveles_de_obligatoriedad_de_educacion_primaria','Cumple con los niveles de obligatoriedad de educación primaria','Huella 6d21b1b363a6. Aparece como: Cumple con los niveles de obligatoriedad de educación primaria / Cumple con los niveles de obligatoriedad de educación secundaria.'),(6,'cuenta_con_normativa_convivencial','Cuenta con Normativa Convivencial','Huella 51426e6015f7. Aparece como: Cuenta con Normativa Convivencial / ¿Cuenta con Normativa Convivencial?.'),(7,'cuenta_con_protocolos_de_articulacion_interministerial_con_que_areas','Cuenta con protocolos de articulación interministerial. Con qué áreas','Huella f33a281ae191. Aparece como: Cuenta con protocolos de articulación interministerial. Con qué áreas.'),(9,'con_que_frecuencia_los_nya_alojados_en_el_dispositivo_realizan_actividades_fuera_del_dispositivo','¿Con que frecuencia los NyA alojados en el dispositivo realizan actividades fuera del dispositivo?','Huella 587a06b164df. Aparece como: ¿Con que frecuencia los NyA alojados en el dispositivo realizan actividades fuera del dispositivo? / ¿Con que frecuencia los NyA alojados en el dispositivo realizan Actividades ARTISTICAS? / ¿Con que frecuencia los NyA alojados en el dispositivo realizan Actividades DEPORTIVAS? / ¿Con que frecuencia los NyA alojados en el dispositivo realizan Actividades RECREATIVAS? / ¿Con que frecuencia los NyA alojados en el dispositivo realizan OTRAS Actividades?.'),(10,'con_que_frecuencia_los_nya_alojados_en_el_dispositivo_realizan_actividades_fuera_del_dispositivo_2','¿Con que frecuencia los NyA alojados en el dispositivo realizan actividades fuera del dispositivo?','Huella 4d2be3aec8e7. Aparece como: ¿Con que frecuencia los NyA alojados en el dispositivo realizan actividades fuera del dispositivo? / ¿Con que frecuencia los NyA alojados en el dispositivo realizan Actividades ARTISTICAS? / ¿Con que frecuencia los NyA alojados en el dispositivo realizan Actividades DEPORTIVAS? / ¿Con que frecuencia los NyA alojados en el dispositivo realizan Actividades RECREATIVAS? / ¿Con que frecuencia los NyA alojados en el dispositivo realizan OTRAS Actividades?.'),(11,'que_conforman_el_equipo_tecnico','… que conforman el equipo técnico','Huella 0de108996953. Aparece como: … que conforman el equipo técnico / destinadas al cuidado del NyA / destinadas a tareas de apoyo (administrativo, mantenimiento, cocina, etc).'),(12,'que_conforman_el_equipo_tecnico_2','… que conforman el equipo técnico','Huella a6033fb83b7b. Aparece como: … que conforman el equipo técnico / ... destinadas al cuidado del NyA / ... destinadas a tareas de apoyo (administrativo, mantenimiento, cocina, etc).'),(13,'tipo_de_gestion','Tipo de gestión','Huella d1ec715a3dc3. Aparece como: Tipo de gestión.'),(14,'proyecto_institucional','¿Proyecto institucional?','Huella b9a6d2b833b4. Aparece como: ¿Proyecto institucional? / Reglamento de convivencia?.'),(15,'habilitacion_municipal','habilitación municipal?','Huella 50de325975e7. Aparece como: habilitación municipal? / ... habilitación municipal?.'),(16,'tablets_o_computadoras_para_los_nya_alojados_en_el_dispositivo','. tablets o computadoras para los NyA alojados en el dispositivo','Huella b5cfd2a3625e. Aparece como: . tablets o computadoras para los NyA alojados en el dispositivo / ... tablets o computadoras para los NyA alojados en el dispositivo.'),(17,'del_equipo_de_conduccion','del equipo de conducción','Huella 78bbeef4ab34. Aparece como: del equipo de conducción / … del equipo de conducción.'),(18,'participa_el_nya_en_el_proyecto_de_restitucion_de_derechos_per','Participa el NyA en el proyecto de restitución de derechos (PER)','Huella b2113a5761de. Aparece como: Participa el NyA en el proyecto de restitución de derechos (PER) / Existe articulación entre el PER y el plan de estadía?.'),(19,'proyecto_institucional_2','... Proyecto institucional?','Huella a404a156d6dc. Aparece como: ... Proyecto institucional? / …reglamento de convivencia?.'),(20,'proyecto_institucional_3','... Proyecto institucional?','Huella 6c925d618483. Aparece como: ... Proyecto institucional? / …reglamento de convivencia?.'),(21,'participa_el_nya_en_el_proyecto_de_restitucion_de_derechos_per_2','Participa el NyA en el proyecto de restitución de derechos (PER)','Huella 767a7b80cc28. Aparece como: Participa el NyA en el proyecto de restitución de derechos (PER) / Existe articulación entre el PER y el plan de estadía?.'),(22,'participa_el_nya_en_el_proyecto_de_restitucion_de_derechos_per_3','Participa el NyA en el proyecto de restitución de derechos (PER)','Huella 4baa97840f74. Aparece como: Participa el NyA en el proyecto de restitución de derechos (PER) / Existe articulación entre el PER y el plan de estadía?.'),(23,'con_rampas_o_condiciones_para_el_acceso_y_circulacion_de_personas_con_discapacidad','. con rampas o condiciones para el acceso y circulación de personas con discapacidad','Huella d708d29956dd. Aparece como: . con rampas o condiciones para el acceso y circulación de personas con discapacidad.'),(24,'genero_admitido','Género admitido','Huella ecfa45ab4bf7. Aparece como: Género admitido.'),(25,'el_dipositivo_participa_en_la_formulacion_del_proyecto_de_restitucion_de_derechos','El dipositivo participa en la formulación del proyecto de restitución de derechos','Huella 4120f031ec87. Aparece como: El dipositivo participa en la formulación del proyecto de restitución de derechos.'),(26,'tipo_de_gestion_2','Tipo de gestión','Huella 2b1741fff60f. Aparece como: Tipo de gestión.'),(27,'habilitacion_municipal_2','... habilitación municipal?','Huella 2b998845f0e9. Aparece como: ... habilitación municipal?.'),(28,'con_rampas_o_condiciones_para_el_acceso_y_circulacion_de_personas_con_discapacidad_2','... con rampas o condiciones para el acceso y circulación de personas con discapacidad','Huella c642320d5b75. Aparece como: ... con rampas o condiciones para el acceso y circulación de personas con discapacidad.'),(29,'con_rampas_o_condiciones_para_el_acceso_y_circulacion_de_personas_con_discapacidad_3','... con rampas o condiciones para el acceso y circulación de personas con discapacidad','Huella 9fdf6f8a27de. Aparece como: ... con rampas o condiciones para el acceso y circulación de personas con discapacidad.'),(30,'tablets_o_computadoras_para_los_nya_alojados_en_el_dispositivo_2','... tablets o computadoras para los NyA alojados en el dispositivo','Huella 4aa88c41bf06. Aparece como: ... tablets o computadoras para los NyA alojados en el dispositivo.'),(31,'cantidad_de_nya_que_es_posible_alojar_por_dormitorio','Cantidad de NyA que es posible alojar por dormitorio','Huella f6f5c4fec58d. Aparece como: Cantidad de NyA que es posible alojar por dormitorio.'),(32,'genero_admitido_2','Género admitido','Huella 40c2eebf00bf. Aparece como: Género admitido.'),(33,'genero_admitido_3','Género admitido','Huella 83edce9e71d0. Aparece como: Género admitido.'),(34,'destinadas_al_cuidado_del_nya','... destinadas al cuidado del NyA','Huella ea52d0da0c99. Aparece como: ... destinadas al cuidado del NyA.'),(35,'destinadas_a_tareas_de_apoyo_administrativo_mantenimiento_cocina_etc','... destinadas a tareas de apoyo (administrativo, mantenimiento, cocina, etc)','Huella 486d23ea17dc. Aparece como: ... destinadas a tareas de apoyo (administrativo, mantenimiento, cocina, etc).'),(36,'del_equipo_de_conduccion_2','… del equipo de conducción','Huella b0d8e58f4976. Aparece como: … del equipo de conducción.'),(37,'el_dipositivo_participa_en_la_formulacion_del_proyecto_de_restitucion_de_derechos_2','El dipositivo participa en la formulación del proyecto de restitución de derechos','Huella 6749eef5c950. Aparece como: El dipositivo participa en la formulación del proyecto de restitución de derechos.'),(38,'el_dipositivo_participa_en_la_formulacion_del_proyecto_de_restitucion_de_derechos_3','El dipositivo participa en la formulación del proyecto de restitución de derechos','Huella 71f6a455a98c. Aparece como: El dipositivo participa en la formulación del proyecto de restitución de derechos.'),(39,'maximo_nivel_educativo_alcanzado','Máximo nivel educativo alcanzado','Huella cbcde2178f28. Aparece como: Máximo nivel educativo alcanzado.'),(40,'provincia','Provincia','Huella e5688bcc1f76. Aparece como: Provincia / Provincia (NyA) / Provincia del referente / Modalidad de cuidado.'),(41,'pais_de_nacimiento','País de nacimiento','Huella f89ae9bcdd51. Aparece como: País de nacimiento / Nacionalidad del referente.'),(42,'maximo_nivel_educativo_alcanzado_2','Máximo nivel educativo alcanzado','Huella 191c74d6b37c. Aparece como: Máximo nivel educativo alcanzado / Nivel escolar del referente.'),(43,'presenta_alguna_discapacidad','¿Presenta alguna discapacidad?','Huella 99f950a1164a. Aparece como: ¿Presenta alguna discapacidad? / ¿Tiene hijos/as? / Enfermedad crónica / Consumo problemático de sustancias / ¿Pertenece a pueblo originario? / Elevación dictamen MPE a juzgado / Decreto judicial de adoptabilidad / Solicitud inclusión proy. autonomía / ¿Se identifica con algún pueblo originario? / ¿Pasó por comisaría previo ingreso? / Denuncia por apremios ilegales / ¿Pertenece a pueblo originario? (o se identifica con algún pueblo originario?) / Control de legalidad por autoridad judicial / ¿Asiste actualmente a una institución educativa?.'),(44,'situacion_de_documentacion','Situación de documentación','Huella 5e122558d7ca. Aparece como: Situación de documentación.'),(45,'provincias','Provincias','Huella edfba740a9cd. Aparece como: Provincias / Provincia / Modalidad de cuidado / Apellido/s.'),(46,'genero','Género','Huella d41d829e2813. Aparece como: Género / Género del referente.'),(47,'genero_2','Género','Huella 6237de4648ea. Aparece como: Género / Género del referente.'),(48,'asistencia_escolar','Asistencia escolar','Huella 60c9ecfa0f16. Aparece como: Asistencia escolar / ¿Asiste a institución educativa?.'),(49,'linea_de_accion','Línea de acción','Huella a0875824e3d0. Aparece como: Línea de acción.'),(50,'problematica_de_salud','Problemática de salud','Huella 5711b84d2c7c. Aparece como: Problemática de salud.'),(51,'cobertura_salud','Cobertura salud','Huella 521f0a1fc722. Aparece como: Cobertura salud.'),(53,'relacion_vincular_del_referente','Relación vincular del referente','Huella 49dfbaa1b5a1. Aparece como: Relación vincular del referente.'),(54,'maximo_nivel_educativo_alcanzado_3','Máximo nivel educativo alcanzado','Huella e6c78f009f73. Aparece como: Máximo nivel educativo alcanzado.'),(55,'causas_de_las_medidas_mpi','Causas de las medidas (MPI)','Huella 058ee674dd34. Aparece como: Causas de las medidas (MPI).'),(56,'motivos_de_intervencion_aplican_tanto_para_mpe_y_mpi_acordadas_en_2019_con_las_24_jurisdicciones','Motivos de Intervención* (aplican tanto para MPE y MPI) Acordadas en 2019 con las 24 jurisdicciones','Huella 54bcc2ad5371. Aparece como: Motivos de Intervención* (aplican tanto para MPE y MPI) Acordadas en 2019 con las 24 jurisdicciones.'),(57,'destinatario','Destinatario','Huella cf780f537a33. Aparece como: Destinatario.'),(58,'destinatario_2','Destinatario','Huella 956b41b83c22. Aparece como: Destinatario.'),(59,'tipo_de_discapacidad','Tipo de discapacidad','Huella 466147faa3ae. Aparece como: Tipo de discapacidad / ¿Presenta algún tipo de discapacidad?.'),(60,'tipo_de_discapacidad_2','Tipo de discapacidad','Huella 3c11d5f99d20. Aparece como: Tipo de discapacidad.'),(61,'posee_cud','¿Posee CUD?','Huella d4a2539e2083. Aparece como: ¿Posee CUD?.'),(62,'posee_cud_2','¿Posee CUD?','Huella 0ee08ce1dd48. Aparece como: ¿Posee CUD?.'),(63,'situacion_laboral_del_referente','Situación laboral del referente','Huella dd2e08d381a5. Aparece como: Situación laboral del referente.'),(64,'situacion_laboral_del_referente_2','Situación laboral del referente','Huella de7875978b0e. Aparece como: Situación laboral del referente.'),(65,'situacion_laboral_del_referente_3','Situación laboral del referente','Huella efdb6f44dc57. Aparece como: Situación laboral del referente.'),(66,'origen_de_la_demanda','Origen de la demanda','Huella f5f1f936b027. Aparece como: Origen de la demanda.'),(67,'origen_de_la_demanda_2','Origen de la demanda','Huella 6df34b574540. Aparece como: Origen de la demanda.'),(76,'origen_de_la_demanda_3','Origen de la demanda','Huella a4ab36d167be. Aparece como: Origen de la demanda / Última fecha de renovación.'),(77,'tipo_de_proyecto_de_restitucion','Tipo de proyecto de restitución','Huella a52e37ad9871. Aparece como: Tipo de proyecto de restitución.'),(83,'modalidad_de_cuidado','Modalidad de cuidado','Huella ba0bf7f40e78. Aparece como: Modalidad de cuidado.'),(86,'asiste_a_institucion_educativa','¿Asiste a institución educativa?','Huella c1d1a025636c. Aparece como: ¿Asiste a institución educativa?.'),(94,'asiste_a_institucion_educativa_2','¿Asiste a institución educativa?','Huella 641913efc23e. Aparece como: ¿Asiste a institución educativa?.'),(97,'cobertura_salud_2','Cobertura salud','Huella 3ea0f052f9e1. Aparece como: Cobertura salud.'),(98,'destino_al_egreso','Destino al egreso','Huella 629fabcda9eb. Aparece como: Destino al egreso.'),(102,'asignacion_universal_por_hijo','Asignación Universal por Hijo','Huella 1311b32718ff. Aparece como: Asignación Universal por Hijo.'),(103,'procedencia_inmediata','Procedencia inmediata','Huella eefe8009d0e1. Aparece como: Procedencia inmediata.'),(104,'situacion_procesal','Situación procesal','Huella 84209525edcb. Aparece como: Situación procesal.'),(105,'tipo_de_dispositivo','Tipo de dispositivo','Huella ea9e8494e3a0. Aparece como: Tipo de dispositivo.'),(106,'tipo_de_dispositivo_2','Tipo de dispositivo','Huella 9e35c6da1e8f. Aparece como: Tipo de dispositivo.'),(107,'tipo_de_dispositivo_3','Tipo de dispositivo','Huella 39467b07bdb3. Aparece como: Tipo de dispositivo.'),(108,'motivo_de_la_aprehension','Motivo de la aprehensión','Huella 752f8a25aeed. Aparece como: Motivo de la aprehensión.'),(109,'fuerza_de_seguridad','Fuerza de seguridad','Huella 57a838f6d23b. Aparece como: Fuerza de seguridad.'),(110,'tiempo_en_comisaria','Tiempo en comisaría','Huella d792ba04d6de. Aparece como: Tiempo en comisaría.'),(182,'tipo_de_documento_de_identidad','Tipo de documento de identidad','Huella fb8664a5a0f9. Aparece como: Tipo de documento de identidad.'),(183,'pais_de_nacimiento_2','País de nacimiento','Huella 0f8a9895bb40. Aparece como: País de nacimiento.'),(184,'presenta_algun_tipo_de_discapacidad','¿Presenta algún tipo de discapacidad?','Huella c548ad639863. Aparece como: ¿Presenta algún tipo de discapacidad?.'),(185,'cobertura_salud_3','Cobertura salud','Huella 7dbdae952a5f. Aparece como: Cobertura salud.'),(186,'genero_3','Género','Huella 6189f1ff18f5. Aparece como: Género.'),(190,'pais_de_nacimiento_3','País de nacimiento','Huella e0919c9221af. Aparece como: País de nacimiento.'),(192,'posee_cud_3','¿Posee CUD?','Huella 385024af8a7b. Aparece como: ¿Posee CUD?.'),(257,'organismo_que_toma_la_mpe','Organismo que toma la MPE','Huella 451b70b28410. Aparece como: Organismo que toma la MPE.'),(258,'causas_de_las_medidas_mpi_2','Causas de las medidas (MPI)','Huella e396f3f7d43d. Aparece como: Causas de las medidas (MPI).'),(260,'organismo_que_toma_la_mpe_2','Organismo que toma la MPE','Huella 8b35a31178cc. Aparece como: Organismo que toma la MPE.'),(261,'modalidad_de_cuidado_2','Modalidad de cuidado','Huella 26de026f475b. Aparece como: Modalidad de cuidado.'),(263,'motivo_de_cese','Motivo de cese','Huella 10b64109fd82. Aparece como: Motivo de cese.');
/*!40000 ALTER TABLE `runac_c1_catalogo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c1_catalogo_opcion`
--

DROP TABLE IF EXISTS `runac_c1_catalogo_opcion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c1_catalogo_opcion` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `catalogo_id` bigint NOT NULL COMMENT 'Catálogo al que pertenece la opción.',
  `codigo` varchar(100) NOT NULL COMMENT 'Código técnico y estable de la opción. NO cambia aunque cambie el texto: es lo que permite comparar series históricas.',
  `valor_esperado` varchar(255) NOT NULL COMMENT 'Texto que debe encontrarse en el archivo Excel. Puede cambiar sin que cambie el código.',
  `descripcion` text COMMENT 'Explicación funcional de la opción.',
  `orden` int NOT NULL COMMENT 'Orden de presentación de la opción dentro del catálogo.',
  `activo` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Baja lógica. Una opción inactiva no se admite en nuevas importaciones, pero el registro se conserva para que los datos anteriores sigan siendo legibles.',
  `vigente_desde_periodo` varchar(30) DEFAULT NULL COMMENT 'Código del primer período en que la opción se admite. Vacío significa que rige desde el inicio. Se guarda el código y no el id para que la Capa 1 no dependa de la Capa 2.',
  `vigente_hasta_periodo` varchar(30) DEFAULT NULL COMMENT 'Código del último período en que la opción se admite. Vacío significa que sigue vigente.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c1_catalogo_opcion_index_5` (`catalogo_id`,`codigo`),
  UNIQUE KEY `runac_c1_catalogo_opcion_index_6` (`catalogo_id`,`valor_esperado`),
  UNIQUE KEY `runac_c1_catalogo_opcion_index_7` (`catalogo_id`,`orden`),
  CONSTRAINT `runac_c1_catalogo_opcion_ibfk_1` FOREIGN KEY (`catalogo_id`) REFERENCES `runac_c1_catalogo` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3373 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Cada valor permitido dentro de un catálogo, con su vigencia. Permite validar cada archivo contra las opciones que regían en su período.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c1_catalogo_opcion`
--

LOCK TABLES `runac_c1_catalogo_opcion` WRITE;
/*!40000 ALTER TABLE `runac_c1_catalogo_opcion` DISABLE KEYS */;
INSERT INTO `runac_c1_catalogo_opcion` VALUES (1,1,'si','Sí',NULL,1,1,NULL,NULL),(2,1,'no','No',NULL,2,1,NULL,NULL),(3,2,'numero','Número',NULL,1,1,NULL,NULL),(4,3,'texto','texto',NULL,1,1,NULL,NULL),(5,4,'si_es_una_herramienta_de_gestion','Sí, es una herramienta de gestión',NULL,1,1,NULL,NULL),(6,4,'si_esta_actualizado_pero_no_se_aplica','Sí, está actualizado pero no se aplica',NULL,2,1,NULL,NULL),(7,4,'si_pero_esta_desactualizado','Sí, pero está desactualizado',NULL,3,1,NULL,NULL),(8,4,'no_pero_se_encuentra_en_diseno','No, pero se encuentra en diseño',NULL,4,1,NULL,NULL),(9,4,'no','No',NULL,5,1,NULL,NULL),(10,5,'si_con_convenio_me','Sí, con convenio ME',NULL,1,1,NULL,NULL),(11,5,'si_sin_convenio_me','Sí, sin convenio ME',NULL,2,1,NULL,NULL),(12,5,'no','No',NULL,3,1,NULL,NULL),(13,6,'si_es_una_herramienta_de_gestion','Sí, es una herramienta de gestión',NULL,1,1,NULL,NULL),(14,6,'si_esta_actualizada_pero_no_se_aplica','Sí, está actualizada pero no se aplica',NULL,2,1,NULL,NULL),(15,6,'si_pero_esta_desactualizada','Sí, pero está desactualizada',NULL,3,1,NULL,NULL),(16,6,'no_pero_se_encuentra_en_diseno','No, pero se encuentra en diseño',NULL,4,1,NULL,NULL),(17,6,'no','No',NULL,5,1,NULL,NULL),(18,7,'si_con_areas_de_salud_y_seguridad','Sí, con áreas de salud y seguridad',NULL,1,1,NULL,NULL),(19,7,'si_con_areas_de_seguridad','Sí, con áreas de seguridad',NULL,2,1,NULL,NULL),(20,7,'si_con_areas_de_salud','Sí, con áreas de salud',NULL,3,1,NULL,NULL),(21,7,'no','No',NULL,4,1,NULL,NULL),(24,9,'1_vez_por_semana_o_mas','1 vez por semana o más',NULL,1,1,NULL,NULL),(25,9,'entre_1_y_3_veces_por_mes','Entre 1 y 3 veces por mes',NULL,2,1,NULL,NULL),(26,9,'menos_de_1_vez_en_el_mes','Menos de 1 vez en el mes',NULL,3,1,NULL,NULL),(27,9,'no_realizan_esta_actividad','No realizan esta actividad',NULL,4,1,NULL,NULL),(28,10,'entre_1_y_3_veces_por_mes','Entre 1 y 3 veces por mes',NULL,1,1,NULL,NULL),(29,10,'menos_de_1_vez_en_el_mes','Menos de 1 vez en el mes',NULL,2,1,NULL,NULL),(30,10,'no_realizan_esta_actividad','No realizan esta actividad',NULL,3,1,NULL,NULL),(31,11,'1','1',NULL,1,1,NULL,NULL),(32,11,'2','2',NULL,2,1,NULL,NULL),(33,11,'3','3',NULL,3,1,NULL,NULL),(34,11,'4','4',NULL,4,1,NULL,NULL),(35,11,'5','5',NULL,5,1,NULL,NULL),(36,11,'6_o_mas_personas','6 o más personas',NULL,6,1,NULL,NULL),(37,11,'no_cuenta_con_equipo_tecnico','No cuenta con equipo técnico',NULL,7,1,NULL,NULL),(38,12,'2','2',NULL,1,1,NULL,NULL),(39,12,'3','3',NULL,2,1,NULL,NULL),(40,12,'4','4',NULL,3,1,NULL,NULL),(41,12,'5','5',NULL,4,1,NULL,NULL),(42,12,'6_o_mas_personas','6 o más personas',NULL,5,1,NULL,NULL),(43,12,'no_cuenta_con_equipo_tecnico','No cuenta con equipo técnico',NULL,6,1,NULL,NULL),(44,13,'gubernamental','Gubernamental',NULL,1,1,NULL,NULL),(45,13,'no_gubernamental','No gubernamental',NULL,2,1,NULL,NULL),(46,13,'mixta','Mixta',NULL,3,1,NULL,NULL),(47,14,'si_esta_actualizado_y_se_aplica','Sí, está actualizado y se aplica',NULL,1,1,NULL,NULL),(48,14,'si_esta_actualizado_y_no_se_aplica','Sí, está actualizado y no se aplica',NULL,2,1,NULL,NULL),(49,14,'si_pero_esta_desactualizado','Sí, pero esta desactualizado',NULL,3,1,NULL,NULL),(50,14,'no','No',NULL,4,1,NULL,NULL),(51,14,'no_pero_esta_en_diseno','No, pero esta en diseño',NULL,5,1,NULL,NULL),(52,15,'si','Si',NULL,1,1,NULL,NULL),(53,15,'no','No',NULL,2,1,NULL,NULL),(54,15,'en_tramite','En trámite',NULL,3,1,NULL,NULL),(55,16,'1_tablet_o_computadora_por_nya','1 tablet o computadora por NyA',NULL,1,1,NULL,NULL),(56,16,'1_tablet_o_computadora_por_cada_2_a_4_nya','1 tablet o computadora por cada 2 a 4 NyA',NULL,2,1,NULL,NULL),(57,16,'1_tablet_o_computadora_por_cada_5_nya_o_mas','1 tablet o computadora por cada 5 NyA o más',NULL,3,1,NULL,NULL),(58,16,'no_cuentan_con_tablet_o_computadora_para_los_nya','No cuentan con tablet o computadora para los NyA',NULL,4,1,NULL,NULL),(59,17,'1','1',NULL,1,1,NULL,NULL),(60,17,'2','2',NULL,2,1,NULL,NULL),(61,17,'3_o_mas_personas','3 o más personas',NULL,3,1,NULL,NULL),(62,17,'no_cuenta_con_personal_de_conduccion','No cuenta con personal de conducción',NULL,4,1,NULL,NULL),(63,18,'si_en_todas_las_situaciones','Sí, en todas las situaciones',NULL,1,1,NULL,NULL),(64,18,'si_en_la_mayoria_de_las_situaciones','Sí, en la mayoría de las situaciones',NULL,2,1,NULL,NULL),(65,18,'si_en_algunas_situaciones','Sí, en algunas situaciones',NULL,3,1,NULL,NULL),(66,18,'no_en_ninguna_situacion','No, en ninguna situación',NULL,4,1,NULL,NULL),(67,19,'si','Si',NULL,5,1,NULL,NULL),(68,19,'esta_actualizado_y_se_aplica','esta actualizado y se aplica',NULL,2,1,NULL,NULL),(70,19,'esta_actualizado_y_no_se_aplica','esta actualizado y no se aplica',NULL,4,1,NULL,NULL),(72,19,'pero_esta_desactualizado','pero esta desactualizado',NULL,6,1,NULL,NULL),(73,19,'no','No',NULL,8,1,NULL,NULL),(75,19,'pero_esta_en_diseno','pero esta en diseño',NULL,9,1,NULL,NULL),(76,20,'si_esta_actualizado_y_no_se_aplica','Sí, está actualizado y no se aplica',NULL,1,1,NULL,NULL),(77,20,'si_pero_esta_desactualizado','Sí, pero esta desactualizado',NULL,2,1,NULL,NULL),(78,20,'no','No',NULL,3,1,NULL,NULL),(79,20,'no_pero_esta_en_diseno','No, pero esta en diseño',NULL,4,1,NULL,NULL),(80,21,'si','Sí',NULL,5,1,NULL,NULL),(81,21,'en_todas_las_situaciones','en todas las situaciones',NULL,2,1,NULL,NULL),(83,21,'en_la_mayoria_de_las_situaciones','en la mayoría de las situaciones',NULL,4,1,NULL,NULL),(85,21,'en_algunas_situaciones','en algunas situaciones',NULL,6,1,NULL,NULL),(86,21,'no_en_ninguna_situacion','No en ninguna situación',NULL,7,1,NULL,NULL),(87,22,'si_en_la_mayoria_de_las_situaciones','Sí, en la mayoría de las situaciones',NULL,1,1,NULL,NULL),(88,22,'si_en_algunas_situaciones','Sí, en algunas situaciones',NULL,2,1,NULL,NULL),(89,22,'no_en_ninguna_situacion','No, en ninguna situación',NULL,3,1,NULL,NULL),(90,23,'si_en_todos_los_espacios_requeridos','Sí, en todos los espacios requeridos',NULL,1,1,NULL,NULL),(91,23,'si_en_la_mayoria_de_los_espacios','Sí, en la mayoría de los espacios',NULL,2,1,NULL,NULL),(92,23,'si_para_algunos_pocos_espacios','Sí, para algunos pocos espacios',NULL,3,1,NULL,NULL),(93,23,'no_aunque_se_puede_adaptar_si_lo_requiere','No, aunque se puede adaptar si lo requiere',NULL,4,1,NULL,NULL),(94,23,'no_y_no_es_posible_adaptarlos','No y no es posible adaptarlos',NULL,5,1,NULL,NULL),(95,24,'aloja_solo_ninas_y_adolescentes_mujeres','Aloja solo niñas y adolescentes mujeres',NULL,1,1,NULL,NULL),(96,24,'aloja_solo_ninos_y_adolescentes_varones','Aloja solo niños y adolescentes varones',NULL,2,1,NULL,NULL),(97,24,'aloja_ninos_ninas_y_adolescentes','Aloja niños, niñas y adolescentes',NULL,3,1,NULL,NULL),(98,25,'si_en_todas_las_situaciones','Sí, en todas las situaciones',NULL,1,1,NULL,NULL),(99,25,'si_en_la_mayoria_de_las_situaciones','Sí, en la mayoría de las situaciones',NULL,2,1,NULL,NULL),(100,25,'si_en_algunas_situaciones','Sí, en algunas situaciones',NULL,3,1,NULL,NULL),(101,25,'no_se_realiza_desde_el_dispositivo','No, se realiza desde el dispositivo',NULL,4,1,NULL,NULL),(102,26,'no_gubernamental','No gubernamental',NULL,1,1,NULL,NULL),(103,26,'mixta','Mixta',NULL,2,1,NULL,NULL),(104,27,'no','No',NULL,1,1,NULL,NULL),(105,27,'en_tramite','En trámite',NULL,2,1,NULL,NULL),(106,28,'si_en_todos_los_espacios_requeridos','Sí en todos los espacios requeridos',NULL,1,1,NULL,NULL),(107,28,'si_en_la_mayoria_de_los_espacios','Sí en la mayoría de los espacios',NULL,2,1,NULL,NULL),(108,28,'si','Sí',NULL,3,1,NULL,NULL),(109,28,'para_algunos_pocos_espcios','para algunos pocos espcios',NULL,4,1,NULL,NULL),(110,28,'no','No',NULL,7,1,NULL,NULL),(111,28,'aunque_se_puede_adaptar_si_lo_requiere','aunque se puede adaptar si lo requiere',NULL,6,1,NULL,NULL),(113,28,'y_no_es_posible_adaptarlos','y no es posible adaptarlos',NULL,8,1,NULL,NULL),(114,29,'si_en_la_mayoria_de_los_espacios','Sí, en la mayoría de los espacios',NULL,1,1,NULL,NULL),(115,29,'si_para_algunos_pocos_espacios','Sí, para algunos pocos espacios',NULL,2,1,NULL,NULL),(116,29,'no_aunque_se_puede_adaptar_si_lo_requiere','No, aunque se puede adaptar si lo requiere',NULL,3,1,NULL,NULL),(117,29,'no_y_no_es_posible_adaptarlos','No y no es posible adaptarlos',NULL,4,1,NULL,NULL),(118,30,'1_tablet_o_computadora_por_cada_2_a_4_nya','1 tablet o computadora por cada 2 a 4 NyA',NULL,1,1,NULL,NULL),(119,30,'1_tablet_o_computadora_por_cada_5_nya_o_mas','1 tablet o computadora por cada 5 NyA o más',NULL,2,1,NULL,NULL),(120,30,'no_cuentan_con_tablet_o_computadora_para_los_nya','No cuentan con tablet o computadora para los NyA',NULL,3,1,NULL,NULL),(121,31,'hasta_4_nya_por_dormitorio','Hasta 4 NyA por dormitorio',NULL,1,1,NULL,NULL),(122,31,'entre_5_y_8_por_dormitorio','Entre 5 y 8 por dormitorio',NULL,2,1,NULL,NULL),(123,31,'9_y_mas','9 y más',NULL,3,1,NULL,NULL),(124,32,'aloja_solo_ninas_y_adolescentes_mujeres','Aloja solo niñas y adolescentes mujeres',NULL,1,1,NULL,NULL),(125,32,'aloja_solo_ninos_y_adolescente_varones','Aloja solo niños y adolescente varones',NULL,2,1,NULL,NULL),(126,32,'aloja_ninos_ninas_y_adolescentes','Aloja niños niñas y adolescentes',NULL,3,1,NULL,NULL),(127,33,'aloja_solo_ninos_y_adolescentes_varones','Aloja solo niños y adolescentes varones',NULL,1,1,NULL,NULL),(128,33,'aloja_ninos_ninas_y_adolescentes','Aloja niños, niñas y adolescentes',NULL,2,1,NULL,NULL),(129,34,'1','1',NULL,1,1,NULL,NULL),(130,34,'2','2',NULL,2,1,NULL,NULL),(131,34,'3','3',NULL,3,1,NULL,NULL),(132,34,'4','4',NULL,4,1,NULL,NULL),(133,34,'5','5',NULL,5,1,NULL,NULL),(134,34,'6','6',NULL,6,1,NULL,NULL),(135,34,'7','7',NULL,7,1,NULL,NULL),(136,34,'8_o_mas_perosnas','8 o más perosnas',NULL,8,1,NULL,NULL),(137,34,'no_cuena_con_personal_de_cuidado','No cuena con personal de cuidado',NULL,9,1,NULL,NULL),(138,35,'1','1',NULL,1,1,NULL,NULL),(139,35,'2','2',NULL,2,1,NULL,NULL),(140,35,'3','3',NULL,3,1,NULL,NULL),(141,35,'4','4',NULL,4,1,NULL,NULL),(142,35,'5','5',NULL,5,1,NULL,NULL),(143,35,'6','6',NULL,6,1,NULL,NULL),(144,35,'7','7',NULL,7,1,NULL,NULL),(145,35,'8_o_mas_personas','8 o más personas',NULL,8,1,NULL,NULL),(146,35,'no_cuenta_con_personal_de_apoyo','No cuenta con personal de apoyo',NULL,9,1,NULL,NULL),(147,36,'2','2',NULL,1,1,NULL,NULL),(148,36,'3_o_mas_personas','3 o más personas',NULL,2,1,NULL,NULL),(149,36,'no_cuenta_con_personal_de_conduccion','No cuenta con personal de conducción',NULL,3,1,NULL,NULL),(150,37,'si','Sí',NULL,5,1,NULL,NULL),(151,37,'en_todas_las_situaciones','en todas las situaciones',NULL,2,1,NULL,NULL),(153,37,'en_la_mayoria_de_las_situaciones','en la mayoría de las situaciones',NULL,4,1,NULL,NULL),(155,37,'en_algunas_situaciones','en algunas situaciones',NULL,6,1,NULL,NULL),(156,37,'no_se_realiza_desde_el_dispositivo','No se realiza desde el dispositivo',NULL,7,1,NULL,NULL),(157,38,'si_en_la_mayoria_de_las_situaciones','Sí, en la mayoría de las situaciones',NULL,1,1,NULL,NULL),(158,38,'si_en_algunas_situaciones','Sí, en algunas situaciones',NULL,2,1,NULL,NULL),(159,38,'no_se_realiza_desde_el_dispositivo','No, se realiza desde el dispositivo',NULL,3,1,NULL,NULL),(160,39,'nunca_asistio','Nunca asistió',NULL,1,1,NULL,NULL),(161,39,'primaria_incompleta','Primaria incompleta',NULL,2,1,NULL,NULL),(162,39,'primaria_completa','Primaria completa',NULL,3,1,NULL,NULL),(163,39,'secundaria_incompleta','Secundaria incompleta',NULL,4,1,NULL,NULL),(164,39,'secundaria_completa','Secundaria completa',NULL,5,1,NULL,NULL),(165,39,'terciario_universitario','Terciario/Universitario',NULL,6,1,NULL,NULL),(166,39,'sin_datos','Sin datos',NULL,7,1,NULL,NULL),(167,40,'buenos_aires','Buenos Aires',NULL,1,1,NULL,NULL),(168,40,'caba','CABA',NULL,2,1,NULL,NULL),(169,40,'catamarca','Catamarca',NULL,3,1,NULL,NULL),(170,40,'chaco','Chaco',NULL,4,1,NULL,NULL),(171,40,'chubut','Chubut',NULL,5,1,NULL,NULL),(172,40,'cordoba','Córdoba',NULL,6,1,NULL,NULL),(173,40,'corrientes','Corrientes',NULL,7,1,NULL,NULL),(174,40,'entre_rios','Entre Ríos',NULL,8,1,NULL,NULL),(175,40,'formosa','Formosa',NULL,9,1,NULL,NULL),(176,40,'jujuy','Jujuy',NULL,10,1,NULL,NULL),(177,40,'la_pampa','La Pampa',NULL,11,1,NULL,NULL),(178,40,'la_rioja','La Rioja',NULL,12,1,NULL,NULL),(179,40,'mendoza','Mendoza',NULL,13,1,NULL,NULL),(180,40,'misiones','Misiones',NULL,14,1,NULL,NULL),(181,40,'neuquen','Neuquén',NULL,15,1,NULL,NULL),(182,40,'rio_negro','Río Negro',NULL,16,1,NULL,NULL),(183,40,'salta','Salta',NULL,17,1,NULL,NULL),(184,40,'san_juan','San Juan',NULL,18,1,NULL,NULL),(185,40,'san_luis','San Luis',NULL,19,1,NULL,NULL),(186,40,'santa_cruz','Santa Cruz',NULL,20,1,NULL,NULL),(187,40,'santa_fe','Santa Fe',NULL,21,1,NULL,NULL),(188,40,'santiago_del_estero','Santiago del Estero',NULL,22,1,NULL,NULL),(189,40,'tierra_del_fuego','Tierra del Fuego',NULL,23,1,NULL,NULL),(190,40,'tucuman','Tucumán',NULL,24,1,NULL,NULL),(191,40,'sin_datos','Sin datos',NULL,25,1,NULL,NULL),(192,41,'sin_datos','Sin datos',NULL,1,1,NULL,NULL),(193,41,'afganistan','Afganistán',NULL,2,1,NULL,NULL),(194,41,'albania','Albania',NULL,3,1,NULL,NULL),(195,41,'alemania','Alemania',NULL,4,1,NULL,NULL),(196,41,'algeria','Algeria',NULL,5,1,NULL,NULL),(197,41,'andorra','Andorra',NULL,6,1,NULL,NULL),(198,41,'angola','Angola',NULL,7,1,NULL,NULL),(199,41,'anguila','Anguila',NULL,8,1,NULL,NULL),(200,41,'antartida','Antártida',NULL,9,1,NULL,NULL),(201,41,'antigua_y_barbuda','Antigua y Barbuda',NULL,10,1,NULL,NULL),(202,41,'antillas_neerlandesas','Antillas Neerlandesas',NULL,11,1,NULL,NULL),(203,41,'arabia_saudita','Arabia Saudita',NULL,12,1,NULL,NULL),(204,41,'argentina','Argentina',NULL,13,1,NULL,NULL),(205,41,'armenia','Armenia',NULL,14,1,NULL,NULL),(206,41,'aruba','Aruba',NULL,15,1,NULL,NULL),(207,41,'australia','Australia',NULL,16,1,NULL,NULL),(208,41,'austria','Austria',NULL,17,1,NULL,NULL),(209,41,'azerbayan','Azerbayán',NULL,18,1,NULL,NULL),(210,41,'belgica','Bélgica',NULL,19,1,NULL,NULL),(211,41,'bahamas','Bahamas',NULL,20,1,NULL,NULL),(212,41,'bahrein','Bahrein',NULL,21,1,NULL,NULL),(213,41,'bangladesh','Bangladesh',NULL,22,1,NULL,NULL),(214,41,'barbados','Barbados',NULL,23,1,NULL,NULL),(215,41,'belice','Belice',NULL,24,1,NULL,NULL),(216,41,'benin','Benín',NULL,25,1,NULL,NULL),(217,41,'bhutan','Bhután',NULL,26,1,NULL,NULL),(218,41,'bielorrusia','Bielorrusia',NULL,27,1,NULL,NULL),(219,41,'birmania','Birmania',NULL,28,1,NULL,NULL),(220,41,'bolivia','Bolivia',NULL,29,1,NULL,NULL),(221,41,'bosnia_y_herzegovina','Bosnia y Herzegovina',NULL,30,1,NULL,NULL),(222,41,'botsuana','Botsuana',NULL,31,1,NULL,NULL),(223,41,'brasil','Brasil',NULL,32,1,NULL,NULL),(224,41,'brunei','Brunéi',NULL,33,1,NULL,NULL),(225,41,'bulgaria','Bulgaria',NULL,34,1,NULL,NULL),(226,41,'burkina_faso','Burkina Faso',NULL,35,1,NULL,NULL),(227,41,'burundi','Burundi',NULL,36,1,NULL,NULL),(228,41,'cabo_verde','Cabo Verde',NULL,37,1,NULL,NULL),(229,41,'camboya','Camboya',NULL,38,1,NULL,NULL),(230,41,'camerun','Camerún',NULL,39,1,NULL,NULL),(231,41,'canada','Canadá',NULL,40,1,NULL,NULL),(232,41,'chad','Chad',NULL,41,1,NULL,NULL),(233,41,'chile','Chile',NULL,42,1,NULL,NULL),(234,41,'china','China',NULL,43,1,NULL,NULL),(235,41,'chipre','Chipre',NULL,44,1,NULL,NULL),(236,41,'ciudad_del_vaticano','Ciudad del Vaticano',NULL,45,1,NULL,NULL),(237,41,'colombia','Colombia',NULL,46,1,NULL,NULL),(238,41,'comoras','Comoras',NULL,47,1,NULL,NULL),(239,41,'congo','Congo',NULL,49,1,NULL,NULL),(241,41,'corea_del_norte','Corea del Norte',NULL,50,1,NULL,NULL),(242,41,'corea_del_sur','Corea del Sur',NULL,51,1,NULL,NULL),(243,41,'costa_de_marfil','Costa de Marfil',NULL,52,1,NULL,NULL),(244,41,'costa_rica','Costa Rica',NULL,53,1,NULL,NULL),(245,41,'croacia','Croacia',NULL,54,1,NULL,NULL),(246,41,'cuba','Cuba',NULL,55,1,NULL,NULL),(247,41,'dinamarca','Dinamarca',NULL,56,1,NULL,NULL),(248,41,'dominica','Dominica',NULL,57,1,NULL,NULL),(249,41,'ecuador','Ecuador',NULL,58,1,NULL,NULL),(250,41,'egipto','Egipto',NULL,59,1,NULL,NULL),(251,41,'el_salvador','El Salvador',NULL,60,1,NULL,NULL),(252,41,'emiratos_arabes_unidos','Emiratos Árabes Unidos',NULL,61,1,NULL,NULL),(253,41,'eritrea','Eritrea',NULL,62,1,NULL,NULL),(254,41,'eslovaquia','Eslovaquia',NULL,63,1,NULL,NULL),(255,41,'eslovenia','Eslovenia',NULL,64,1,NULL,NULL),(256,41,'espana','España',NULL,65,1,NULL,NULL),(257,41,'estados_unidos_de_america','Estados Unidos de América',NULL,66,1,NULL,NULL),(258,41,'estonia','Estonia',NULL,67,1,NULL,NULL),(259,41,'etiopia','Etiopía',NULL,68,1,NULL,NULL),(260,41,'filipinas','Filipinas',NULL,69,1,NULL,NULL),(261,41,'finlandia','Finlandia',NULL,70,1,NULL,NULL),(262,41,'fiyi','Fiyi',NULL,71,1,NULL,NULL),(263,41,'francia','Francia',NULL,72,1,NULL,NULL),(264,41,'gabon','Gabón',NULL,73,1,NULL,NULL),(265,41,'gambia','Gambia',NULL,74,1,NULL,NULL),(266,41,'georgia','Georgia',NULL,75,1,NULL,NULL),(267,41,'ghana','Ghana',NULL,76,1,NULL,NULL),(268,41,'gibraltar','Gibraltar',NULL,77,1,NULL,NULL),(269,41,'granada','Granada',NULL,78,1,NULL,NULL),(270,41,'grecia','Grecia',NULL,79,1,NULL,NULL),(271,41,'groenlandia','Groenlandia',NULL,80,1,NULL,NULL),(272,41,'guadalupe','Guadalupe',NULL,81,1,NULL,NULL),(273,41,'guam','Guam',NULL,82,1,NULL,NULL),(274,41,'guatemala','Guatemala',NULL,83,1,NULL,NULL),(275,41,'guayana_francesa','Guayana Francesa',NULL,84,1,NULL,NULL),(276,41,'guernsey','Guernsey',NULL,85,1,NULL,NULL),(277,41,'guinea','Guinea',NULL,86,1,NULL,NULL),(278,41,'guinea_ecuatorial','Guinea Ecuatorial',NULL,87,1,NULL,NULL),(279,41,'guinea_bissau','Guinea-Bissau',NULL,88,1,NULL,NULL),(280,41,'guyana','Guyana',NULL,89,1,NULL,NULL),(281,41,'haiti','Haití',NULL,90,1,NULL,NULL),(282,41,'honduras','Honduras',NULL,91,1,NULL,NULL),(283,41,'hong_kong','Hong kong',NULL,92,1,NULL,NULL),(284,41,'hungria','Hungría',NULL,93,1,NULL,NULL),(285,41,'india','India',NULL,94,1,NULL,NULL),(286,41,'indonesia','Indonesia',NULL,95,1,NULL,NULL),(287,41,'iran','Irán',NULL,96,1,NULL,NULL),(288,41,'irak','Irak',NULL,97,1,NULL,NULL),(289,41,'irlanda','Irlanda',NULL,98,1,NULL,NULL),(290,41,'isla_bouvet','Isla Bouvet',NULL,99,1,NULL,NULL),(291,41,'isla_de_man','Isla de Man',NULL,100,1,NULL,NULL),(292,41,'isla_de_navidad','Isla de Navidad',NULL,101,1,NULL,NULL),(293,41,'isla_norfolk','Isla Norfolk',NULL,102,1,NULL,NULL),(294,41,'islandia','Islandia',NULL,103,1,NULL,NULL),(295,41,'islas_bermudas','Islas Bermudas',NULL,104,1,NULL,NULL),(296,41,'islas_caiman','Islas Caimán',NULL,105,1,NULL,NULL),(297,41,'islas_cocos_keeling','Islas Cocos (Keeling)',NULL,106,1,NULL,NULL),(298,41,'islas_cook','Islas Cook',NULL,107,1,NULL,NULL),(299,41,'islas_de_aland','Islas de Åland',NULL,108,1,NULL,NULL),(300,41,'islas_feroe','Islas Feroe',NULL,109,1,NULL,NULL),(301,41,'islas_georgias_del_sur_y_sandwich_del_sur','Islas Georgias del Sur y Sandwich del Sur',NULL,110,1,NULL,NULL),(302,41,'islas_heard_y_mcdonald','Islas Heard y McDonald',NULL,111,1,NULL,NULL),(303,41,'islas_maldivas','Islas Maldivas',NULL,112,1,NULL,NULL),(304,41,'islas_malvinas','Islas Malvinas',NULL,113,1,NULL,NULL),(305,41,'islas_marianas_del_norte','Islas Marianas del Norte',NULL,114,1,NULL,NULL),(306,41,'islas_marshall','Islas Marshall',NULL,115,1,NULL,NULL),(307,41,'islas_pitcairn','Islas Pitcairn',NULL,116,1,NULL,NULL),(308,41,'islas_salomon','Islas Salomón',NULL,117,1,NULL,NULL),(309,41,'islas_turcas_y_caicos','Islas Turcas y Caicos',NULL,118,1,NULL,NULL),(310,41,'islas_ultramarinas_menores_de_estados_unidos','Islas Ultramarinas Menores de Estados Unidos',NULL,119,1,NULL,NULL),(311,41,'islas_virgenes_britanicas','Islas Vírgenes Británicas',NULL,120,1,NULL,NULL),(312,41,'islas_virgenes_de_los_estados_unidos','Islas Vírgenes de los Estados Unidos',NULL,121,1,NULL,NULL),(313,41,'israel','Israel',NULL,122,1,NULL,NULL),(314,41,'italia','Italia',NULL,123,1,NULL,NULL),(315,41,'jamaica','Jamaica',NULL,124,1,NULL,NULL),(316,41,'japon','Japón',NULL,125,1,NULL,NULL),(317,41,'jersey','Jersey',NULL,126,1,NULL,NULL),(318,41,'jordania','Jordania',NULL,127,1,NULL,NULL),(319,41,'kazajistan','Kazajistán',NULL,128,1,NULL,NULL),(320,41,'kenia','Kenia',NULL,129,1,NULL,NULL),(321,41,'kirgizstan','Kirgizstán',NULL,130,1,NULL,NULL),(322,41,'kiribati','Kiribati',NULL,131,1,NULL,NULL),(323,41,'kuwait','Kuwait',NULL,132,1,NULL,NULL),(324,41,'libano','Líbano',NULL,133,1,NULL,NULL),(325,41,'laos','Laos',NULL,134,1,NULL,NULL),(326,41,'lesoto','Lesoto',NULL,135,1,NULL,NULL),(327,41,'letonia','Letonia',NULL,136,1,NULL,NULL),(328,41,'liberia','Liberia',NULL,137,1,NULL,NULL),(329,41,'libia','Libia',NULL,138,1,NULL,NULL),(330,41,'liechtenstein','Liechtenstein',NULL,139,1,NULL,NULL),(331,41,'lituania','Lituania',NULL,140,1,NULL,NULL),(332,41,'luxemburgo','Luxemburgo',NULL,141,1,NULL,NULL),(333,41,'mexico','México',NULL,142,1,NULL,NULL),(334,41,'monaco','Mónaco',NULL,143,1,NULL,NULL),(335,41,'macao','Macao',NULL,144,1,NULL,NULL),(336,41,'macedonia','Macedônia',NULL,145,1,NULL,NULL),(337,41,'madagascar','Madagascar',NULL,146,1,NULL,NULL),(338,41,'malasia','Malasia',NULL,147,1,NULL,NULL),(339,41,'malawi','Malawi',NULL,148,1,NULL,NULL),(340,41,'mali','Mali',NULL,149,1,NULL,NULL),(341,41,'malta','Malta',NULL,150,1,NULL,NULL),(342,41,'marruecos','Marruecos',NULL,151,1,NULL,NULL),(343,41,'martinica','Martinica',NULL,152,1,NULL,NULL),(344,41,'mauricio','Mauricio',NULL,153,1,NULL,NULL),(345,41,'mauritania','Mauritania',NULL,154,1,NULL,NULL),(346,41,'mayotte','Mayotte',NULL,155,1,NULL,NULL),(347,41,'micronesia','Micronesia',NULL,156,1,NULL,NULL),(348,41,'moldavia','Moldavia',NULL,157,1,NULL,NULL),(349,41,'mongolia','Mongolia',NULL,158,1,NULL,NULL),(350,41,'montenegro','Montenegro',NULL,159,1,NULL,NULL),(351,41,'montserrat','Montserrat',NULL,160,1,NULL,NULL),(352,41,'mozambique','Mozambique',NULL,161,1,NULL,NULL),(353,41,'namibia','Namibia',NULL,162,1,NULL,NULL),(354,41,'nauru','Nauru',NULL,163,1,NULL,NULL),(355,41,'nepal','Nepal',NULL,164,1,NULL,NULL),(356,41,'nicaragua','Nicaragua',NULL,165,1,NULL,NULL),(357,41,'niger','Niger',NULL,166,1,NULL,NULL),(358,41,'nigeria','Nigeria',NULL,167,1,NULL,NULL),(359,41,'niue','Niue',NULL,168,1,NULL,NULL),(360,41,'noruega','Noruega',NULL,169,1,NULL,NULL),(361,41,'nueva_caledonia','Nueva Caledonia',NULL,170,1,NULL,NULL),(362,41,'nueva_zelanda','Nueva Zelanda',NULL,171,1,NULL,NULL),(363,41,'oman','Omán',NULL,172,1,NULL,NULL),(364,41,'paises_bajos','Países Bajos',NULL,173,1,NULL,NULL),(365,41,'pakistan','Pakistán',NULL,174,1,NULL,NULL),(366,41,'palau','Palau',NULL,175,1,NULL,NULL),(367,41,'palestina','Palestina',NULL,176,1,NULL,NULL),(368,41,'panama','Panamá',NULL,177,1,NULL,NULL),(369,41,'papua_nueva_guinea','Papúa Nueva Guinea',NULL,178,1,NULL,NULL),(370,41,'paraguay','Paraguay',NULL,179,1,NULL,NULL),(371,41,'peru','Perú',NULL,180,1,NULL,NULL),(372,41,'polinesia_francesa','Polinesia Francesa',NULL,181,1,NULL,NULL),(373,41,'polonia','Polonia',NULL,182,1,NULL,NULL),(374,41,'portugal','Portugal',NULL,183,1,NULL,NULL),(375,41,'puerto_rico','Puerto Rico',NULL,184,1,NULL,NULL),(376,41,'qatar','Qatar',NULL,185,1,NULL,NULL),(377,41,'reino_unido','Reino Unido',NULL,186,1,NULL,NULL),(378,41,'republica_centroafricana','República Centroafricana',NULL,187,1,NULL,NULL),(379,41,'republica_checa','República Checa',NULL,188,1,NULL,NULL),(380,41,'republica_dominicana','República Dominicana',NULL,189,1,NULL,NULL),(381,41,'reunion','Reunión',NULL,190,1,NULL,NULL),(382,41,'ruanda','Ruanda',NULL,191,1,NULL,NULL),(383,41,'rumania','Rumanía',NULL,192,1,NULL,NULL),(384,41,'rusia','Rusia',NULL,193,1,NULL,NULL),(385,41,'sahara_occidental','Sahara Occidental',NULL,194,1,NULL,NULL),(386,41,'samoa','Samoa',NULL,195,1,NULL,NULL),(387,41,'samoa_americana','Samoa Americana',NULL,196,1,NULL,NULL),(388,41,'san_bartolome','San Bartolomé',NULL,197,1,NULL,NULL),(389,41,'san_cristobal_y_nieves','San Cristóbal y Nieves',NULL,198,1,NULL,NULL),(390,41,'san_marino','San Marino',NULL,199,1,NULL,NULL),(391,41,'san_martin_francia','San Martín (Francia)',NULL,200,1,NULL,NULL),(392,41,'san_pedro_y_miquelon','San Pedro y Miquelón',NULL,201,1,NULL,NULL),(393,41,'san_vicente_y_las_granadinas','San Vicente y las Granadinas',NULL,202,1,NULL,NULL),(394,41,'santa_elena','Santa Elena',NULL,203,1,NULL,NULL),(395,41,'santa_lucia','Santa Lucía',NULL,204,1,NULL,NULL),(396,41,'santo_tome_y_principe','Santo Tomé y Príncipe',NULL,205,1,NULL,NULL),(397,41,'senegal','Senegal',NULL,206,1,NULL,NULL),(398,41,'serbia','Serbia',NULL,207,1,NULL,NULL),(399,41,'seychelles','Seychelles',NULL,208,1,NULL,NULL),(400,41,'sierra_leona','Sierra Leona',NULL,209,1,NULL,NULL),(401,41,'singapur','Singapur',NULL,210,1,NULL,NULL),(402,41,'siria','Siria',NULL,211,1,NULL,NULL),(403,41,'somalia','Somalia',NULL,212,1,NULL,NULL),(404,41,'sri_lanka','Sri lanka',NULL,213,1,NULL,NULL),(405,41,'sudafrica','Sudáfrica',NULL,214,1,NULL,NULL),(406,41,'sudan','Sudán',NULL,215,1,NULL,NULL),(407,41,'suecia','Suecia',NULL,216,1,NULL,NULL),(408,41,'suiza','Suiza',NULL,217,1,NULL,NULL),(409,41,'surinam','Surinám',NULL,218,1,NULL,NULL),(410,41,'svalbard_y_jan_mayen','Svalbard y Jan Mayen',NULL,219,1,NULL,NULL),(411,41,'swazilandia','Swazilandia',NULL,220,1,NULL,NULL),(412,41,'tadjikistan','Tadjikistán',NULL,221,1,NULL,NULL),(413,41,'tailandia','Tailandia',NULL,222,1,NULL,NULL),(414,41,'taiwan','Taiwán',NULL,223,1,NULL,NULL),(415,41,'tanzania','Tanzania',NULL,224,1,NULL,NULL),(416,41,'territorio_britanico_del_oceano_indico','Territorio Británico del Océano Índico',NULL,225,1,NULL,NULL),(417,41,'territorios_australes_y_antarticas_franceses','Territorios Australes y Antárticas Franceses',NULL,226,1,NULL,NULL),(418,41,'timor_oriental','Timor Oriental',NULL,227,1,NULL,NULL),(419,41,'togo','Togo',NULL,228,1,NULL,NULL),(420,41,'tokelau','Tokelau',NULL,229,1,NULL,NULL),(421,41,'tonga','Tonga',NULL,230,1,NULL,NULL),(422,41,'trinidad_y_tobago','Trinidad y Tobago',NULL,231,1,NULL,NULL),(423,41,'tunez','Tunez',NULL,232,1,NULL,NULL),(424,41,'turkmenistan','Turkmenistán',NULL,233,1,NULL,NULL),(425,41,'turquia','Turquía',NULL,234,1,NULL,NULL),(426,41,'tuvalu','Tuvalu',NULL,235,1,NULL,NULL),(427,41,'ucrania','Ucrania',NULL,236,1,NULL,NULL),(428,41,'uganda','Uganda',NULL,237,1,NULL,NULL),(429,41,'uruguay','Uruguay',NULL,238,1,NULL,NULL),(430,41,'uzbekistan','Uzbekistán',NULL,239,1,NULL,NULL),(431,41,'vanuatu','Vanuatu',NULL,240,1,NULL,NULL),(432,41,'venezuela','Venezuela',NULL,241,1,NULL,NULL),(433,41,'vietnam','Vietnam',NULL,242,1,NULL,NULL),(434,41,'wallis_y_futuna','Wallis y Futuna',NULL,243,1,NULL,NULL),(435,41,'yemen','Yemen',NULL,244,1,NULL,NULL),(436,41,'yibuti','Yibuti',NULL,245,1,NULL,NULL),(437,41,'zambia','Zambia',NULL,246,1,NULL,NULL),(438,41,'zimbabue','Zimbabue',NULL,247,1,NULL,NULL),(439,42,'nunca_asistio','Nunca asistió',NULL,1,1,NULL,NULL),(440,42,'jardin_de_infantes','Jardín de infantes',NULL,2,1,NULL,NULL),(441,42,'pre_escolar','Pre escolar',NULL,3,1,NULL,NULL),(442,42,'primaria_incompleta','Primaria incompleta',NULL,4,1,NULL,NULL),(443,42,'primaria_completa','Primaria completa',NULL,5,1,NULL,NULL),(444,42,'secundaria_incompleta','Secundaria incompleta',NULL,6,1,NULL,NULL),(445,42,'secundaria_completa','Secundaria completa',NULL,7,1,NULL,NULL),(446,42,'terciario_incompleto','Terciario incompleto',NULL,8,1,NULL,NULL),(447,42,'terciario_completo','Terciario completo',NULL,9,1,NULL,NULL),(448,42,'universitario_incompleto','Universitario incompleto',NULL,10,1,NULL,NULL),(449,42,'universitario_completo','Universitario completo',NULL,11,1,NULL,NULL),(450,42,'sin_datos','Sin datos',NULL,12,1,NULL,NULL),(451,43,'si','Sí',NULL,4,1,NULL,NULL),(452,43,'no','No',NULL,2,1,NULL,NULL),(453,43,'sin_datos','Sin datos',NULL,3,1,NULL,NULL),(454,44,'posee_n_dni','Posee N° DNI',NULL,1,1,NULL,NULL),(455,44,'no_posee_n_dni','No posee N° DNI',NULL,2,1,NULL,NULL),(456,44,'dni_en_tramite','DNI en trámite',NULL,3,1,NULL,NULL),(457,44,'posee_n_doc_extranjero','Posee N° doc. Extranjero',NULL,4,1,NULL,NULL),(458,44,'perdida_de_documentacion','Perdida de documentación',NULL,5,1,NULL,NULL),(459,44,'sin_inscripcion','Sin inscripción',NULL,6,1,NULL,NULL),(460,44,'sin_datos','Sin datos',NULL,7,1,NULL,NULL),(461,45,'buenos_aires','Buenos Aires',NULL,1,1,NULL,NULL),(462,45,'caba','CABA',NULL,2,1,NULL,NULL),(463,45,'catamarca','Catamarca',NULL,3,1,NULL,NULL),(464,45,'chaco','Chaco',NULL,4,1,NULL,NULL),(465,45,'chubut','Chubut',NULL,5,1,NULL,NULL),(466,45,'cordoba','Córdoba',NULL,6,1,NULL,NULL),(467,45,'corrientes','Corrientes',NULL,7,1,NULL,NULL),(468,45,'entre_rios','Entre Ríos',NULL,8,1,NULL,NULL),(469,45,'formosa','Formosa',NULL,9,1,NULL,NULL),(470,45,'jujuy','Jujuy',NULL,10,1,NULL,NULL),(471,45,'la_pampa','La Pampa',NULL,11,1,NULL,NULL),(472,45,'la_rioja','La Rioja',NULL,12,1,NULL,NULL),(473,45,'mendoza','Mendoza',NULL,13,1,NULL,NULL),(474,45,'misiones','Misiones',NULL,14,1,NULL,NULL),(475,45,'neuquen','Neuquén',NULL,15,1,NULL,NULL),(476,45,'rio_negro','Río Negro',NULL,16,1,NULL,NULL),(477,45,'salta','Salta',NULL,17,1,NULL,NULL),(478,45,'san_juan','San Juan',NULL,18,1,NULL,NULL),(479,45,'san_luis','San Luis',NULL,19,1,NULL,NULL),(480,45,'santa_cruz','Santa Cruz',NULL,20,1,NULL,NULL),(481,45,'santa_fe','Santa Fe',NULL,21,1,NULL,NULL),(482,45,'santiago_del_estero','Santiago del Estero',NULL,22,1,NULL,NULL),(483,45,'tierra_del_fuego','Tierra del Fuego',NULL,23,1,NULL,NULL),(484,45,'tucuman','Tucumán',NULL,24,1,NULL,NULL),(485,46,'masculino','Masculino',NULL,1,1,NULL,NULL),(486,46,'femenino','Femenino',NULL,2,1,NULL,NULL),(487,46,'otros','Otros',NULL,3,1,NULL,NULL),(488,47,'masculino','Masculino',NULL,1,1,NULL,NULL),(489,47,'femenino','Femenino',NULL,2,1,NULL,NULL),(490,47,'otros','Otros',NULL,3,1,NULL,NULL),(491,47,'sin_datos','Sin datos',NULL,4,1,NULL,NULL),(492,48,'asiste','Asiste',NULL,1,1,NULL,NULL),(493,48,'no_asiste','No asiste',NULL,2,1,NULL,NULL),(494,48,'sin_datos','Sin datos',NULL,3,1,NULL,NULL),(495,49,'restitucion_de_derechos','Restitución de derechos',NULL,1,1,NULL,NULL),(496,49,'fortalecimiento_familiar','Fortalecimiento familiar',NULL,2,1,NULL,NULL),(497,49,'ambos','Ambos',NULL,3,1,NULL,NULL),(498,50,'mental','Mental',NULL,1,1,NULL,NULL),(499,50,'fisica','Física',NULL,2,1,NULL,NULL),(500,50,'mixta','Mixta',NULL,3,1,NULL,NULL),(501,50,'sin_datos','Sin datos',NULL,4,1,NULL,NULL),(502,51,'publica','Publica',NULL,4,1,NULL,NULL),(503,51,'privada','Privada',NULL,2,1,NULL,NULL),(504,51,'sin_datos','Sin datos',NULL,3,1,NULL,NULL),(507,53,'ambos_padres','Ambos padres',NULL,1,1,NULL,NULL),(508,53,'madre','Madre',NULL,2,1,NULL,NULL),(509,53,'padre','Padre',NULL,3,1,NULL,NULL),(510,53,'familiar','Familiar',NULL,4,1,NULL,NULL),(511,53,'referente_afectivo','Referente afectivo',NULL,5,1,NULL,NULL),(512,53,'otros','Otros',NULL,6,1,NULL,NULL),(513,53,'sin_datos','Sin datos',NULL,7,1,NULL,NULL),(514,54,'nunca_asistio','Nunca asistió',NULL,1,1,NULL,NULL),(515,54,'materno_infantil','Materno Infantil',NULL,2,1,NULL,NULL),(516,54,'jardin_de_infantes','Jardín de infantes',NULL,3,1,NULL,NULL),(517,54,'pre_escolar','Pre escolar',NULL,4,1,NULL,NULL),(518,54,'primaria_incompleta','Primaria incompleta',NULL,5,1,NULL,NULL),(519,54,'primaria_completa','Primaria completa',NULL,6,1,NULL,NULL),(520,54,'secundaria_incompleta','Secundaria incompleta',NULL,7,1,NULL,NULL),(521,54,'secundaria_completa','Secundaria completa',NULL,8,1,NULL,NULL),(522,54,'sin_datos','Sin datos',NULL,9,1,NULL,NULL),(523,55,'abandono','Abandono',NULL,1,1,NULL,NULL),(524,55,'abuso_sexual_infanto_juvenil','Abuso sexual infanto-juvenil',NULL,2,1,NULL,NULL),(525,55,'dificultad_en_el_acceso_a_la_escolaridad','Dificultad en el acceso a la escolaridad',NULL,3,1,NULL,NULL),(526,55,'dificultad_en_el_acceso_a_la_justicia','Dificultad en el acceso a la justicia',NULL,4,1,NULL,NULL),(527,55,'dificultad_en_el_acceso_a_la_vivienda_y_espacio_saludable','Dificultad en el acceso a la vivienda y espacio saludable',NULL,5,1,NULL,NULL),(528,55,'dificultad_en_el_acceso_y_sostenimiento_de_la_seguridad_social','Dificultad en el acceso y sostenimiento de la seguridad social',NULL,6,1,NULL,NULL),(529,55,'dificultad_en_el_acceso_a_la_salud','Dificultad en el acceso a la salud',NULL,7,1,NULL,NULL),(530,55,'dificultades_en_el_ejercicio_de_la_responsabilidad_parental','Dificultades en el ejercicio de la responsabilidad parental',NULL,8,1,NULL,NULL),(531,55,'explotacion_y_trabajo_infantil_adolescente','Explotación y trabajo infantil adolescente',NULL,9,1,NULL,NULL),(532,55,'negligencia','Negligencia',NULL,10,1,NULL,NULL),(533,55,'restriccion_a_la_libertad_de_expresion','Restricción a la libertad de expresión',NULL,11,1,NULL,NULL),(534,55,'trata_y_trafico','Trata y tráfico',NULL,12,1,NULL,NULL),(535,55,'violencia','Violencia',NULL,13,1,NULL,NULL),(536,55,'vulneracion_a_la_identidad_y_discriminacion','Vulneración a la identidad y discriminación',NULL,14,1,NULL,NULL),(537,55,'situacion_de_calle','Situación de calle',NULL,15,1,NULL,NULL),(538,55,'consumo_problematico','Consumo problemático',NULL,16,1,NULL,NULL),(539,55,'salud_mental','Salud mental',NULL,17,1,NULL,NULL),(540,55,'otros','Otros',NULL,18,1,NULL,NULL),(541,56,'dificultades_en_el_acceso_a_la_informacion','Dificultades en el acceso a la información',NULL,1,1,NULL,NULL),(542,56,'falta_de_documentacion','Falta de documentación',NULL,2,1,NULL,NULL),(543,56,'busqueda_de_origen','Búsqueda de origen',NULL,3,1,NULL,NULL),(544,56,'discriminacion_por_genero_creencia_religiosas_ideologia_raza_nacionalidad_orientacion_sexual','Discriminación por género, creencia religiosas, ideología raza, nacionalidad, orientación sexual',NULL,4,1,NULL,NULL),(545,56,'apropiacion','Apropiación',NULL,5,1,NULL,NULL),(546,56,'abandono_sin_datos_de_las_os_adultos','Abandono Sin datos de las/os adultos',NULL,6,1,NULL,NULL),(547,56,'sin_posibilidad_y_o_voluntad_de_ejercer_el_cuidado_transitoria_o_permanente_de_quien_tiene_a_85661b','Sin posibilidad y /o voluntad de ejercer el cuidado ( transitoria o permanente) de quien tiene a cargo la responsabilidad parental',NULL,7,1,NULL,NULL),(548,56,'dificultades_en_el_ejercicio_de_la_responsabilidad_parental','Dificultades en el ejercicio de la responsabilidad parental',NULL,8,1,NULL,NULL),(549,56,'ausencia_de_adulto_responsable','Ausencia de adulto responsable',NULL,9,1,NULL,NULL),(550,56,'dificultades_en_el_acceso_y_sostenimiento_en_la_seguridad_social','Dificultades en el acceso y sostenimiento en la seguridad social',NULL,10,1,NULL,NULL),(551,56,'violencia','Violencia',NULL,11,1,NULL,NULL),(552,56,'violencia_institucional','Violencia institucional',NULL,12,1,NULL,NULL),(553,56,'negligencia','Negligencia',NULL,13,1,NULL,NULL),(554,56,'asi_abuso_sexual_a_ninas_ninos_y_adolescentes','ASI ( abuso sexual a niñas niños y adolescentes)',NULL,14,1,NULL,NULL),(555,56,'trata_y_trafico','Trata y Tráfico',NULL,15,1,NULL,NULL),(556,56,'explotacion','Explotación',NULL,16,1,NULL,NULL),(557,56,'trabajo_infantil_trabajo_adolescente','Trabajo infantil / trabajo adolescente',NULL,17,1,NULL,NULL),(558,56,'dificultades_en_el_acceso_y_en_los_tratamientos_de_salud_segun_autonomia_progresiva_y_o_adult_54d178','Dificultades en el acceso y en los tratamientos de salud (según autonomía progresiva y o adultos responsables)',NULL,18,1,NULL,NULL),(559,56,'dificultades_en_el_acceso_a_las_prestaciones_de_salud_por_parte_de_los_organismos_del_estado_871cda','Dificultades en el acceso a las prestaciones de salud por parte de los Organismos del Estado y la sociedad civil.',NULL,19,1,NULL,NULL),(560,56,'dificultades_en_el_acceso_a_la_vivienda_y_o_a_condiciones_saludables_del_medio_ambiente','Dificultades en el acceso a la vivienda y/o a condiciones saludables del medio ambiente',NULL,20,1,NULL,NULL),(561,56,'dificultades_en_la_inclusion_en_trayectorias_educativas_juego_y_recreacion_vinculado_a_los_ad_932996','Dificultades en la inclusión en trayectorias educativas, juego y recreación ( vinculado a los adultos responsables del cuidado o al propio NNyA según autonomía progresiva)',NULL,21,1,NULL,NULL),(562,56,'dificultades_en_el_acceso_a_la_inclusion_y_a_las_trayectorias_educativas_juego_y_recreacion_p_75e15f','Dificultades en el acceso a la inclusión y a las trayectorias educativas, juego y recreación por parte de los Organismos del Estado o de la sociedad civil.',NULL,22,1,NULL,NULL),(563,56,'restriccion_a_la_libre_asociacion','Restricción a la libre asociación',NULL,23,1,NULL,NULL),(564,56,'accesibilidad_a_la_justicia','Accesibilidad a la justicia',NULL,24,1,NULL,NULL),(565,56,'otros','Otros',NULL,25,1,NULL,NULL),(566,57,'n_y_o_a','N y/o A',NULL,1,1,NULL,NULL),(567,57,'grupo_familiar','Grupo familiar',NULL,2,1,NULL,NULL),(568,57,'sin_datos','Sin datos',NULL,3,1,NULL,NULL),(569,58,'n_y_o_a','N y/o A',NULL,1,1,NULL,NULL),(570,58,'grupo_familiar','Grupo familiar',NULL,2,1,NULL,NULL),(571,58,'ambos','Ambos',NULL,3,1,NULL,NULL),(572,58,'sin_datos','Sin datos',NULL,4,1,NULL,NULL),(573,59,'visual','Visual',NULL,1,1,NULL,NULL),(574,59,'auditiva','Auditiva',NULL,2,1,NULL,NULL),(575,59,'mental','Mental',NULL,3,1,NULL,NULL),(576,59,'motora','Motora',NULL,4,1,NULL,NULL),(577,59,'visceral','Visceral',NULL,5,1,NULL,NULL),(578,59,'otros','Otros',NULL,6,1,NULL,NULL),(579,59,'sin_datos','Sin datos',NULL,7,1,NULL,NULL),(580,60,'visual','Visual',NULL,1,1,NULL,NULL),(581,60,'auditiva','Auditiva',NULL,2,1,NULL,NULL),(582,60,'mental','Mental',NULL,3,1,NULL,NULL),(583,60,'motora','Motora',NULL,4,1,NULL,NULL),(584,60,'visceral','Visceral',NULL,5,1,NULL,NULL),(585,60,'otros','Otros',NULL,6,1,NULL,NULL),(586,60,'mas_de_una','Más de una',NULL,7,1,NULL,NULL),(587,60,'sin_datos','Sin datos',NULL,8,1,NULL,NULL),(588,61,'si','Sí',NULL,1,1,NULL,NULL),(589,61,'no','No',NULL,2,1,NULL,NULL),(590,61,'en_tramite','En trámite',NULL,3,1,NULL,NULL),(591,61,'sin_datos','Sin datos',NULL,4,1,NULL,NULL),(592,62,'si','Sí',NULL,1,1,NULL,NULL),(593,62,'no','No',NULL,2,1,NULL,NULL),(594,62,'en_tramite','En trámite',NULL,3,1,NULL,NULL),(595,62,'vencido','Vencido',NULL,4,1,NULL,NULL),(596,62,'sin_datos','Sin datos',NULL,5,1,NULL,NULL),(597,63,'ocupado_a','Ocupado/a',NULL,1,1,NULL,NULL),(598,63,'desocupado_a','Desocupado/a',NULL,2,1,NULL,NULL),(599,63,'inactivo_a','Inactivo/a',NULL,3,1,NULL,NULL),(600,64,'ocupado_a','Ocupado/a',NULL,1,1,NULL,NULL),(601,64,'desocupado_a','Desocupado/a',NULL,2,1,NULL,NULL),(602,64,'inactivo_a','Inactivo/a',NULL,3,1,NULL,NULL),(603,64,'sin_datos','Sin datos',NULL,4,1,NULL,NULL),(604,65,'ocupado_a_con_trabajo_registrado','Ocupado/a con trabajo registrado',NULL,1,1,NULL,NULL),(605,65,'changas','Changas',NULL,2,1,NULL,NULL),(606,65,'desocupado_a','Desocupado/a',NULL,3,1,NULL,NULL),(607,65,'inactivo_a','Inactivo/a',NULL,4,1,NULL,NULL),(608,66,'demanda_espontanea','Demanda espontánea',NULL,1,1,NULL,NULL),(609,66,'derivacion_judicial','Derivación judicial',NULL,2,1,NULL,NULL),(610,66,'derivacion_escolar','Derivación escolar',NULL,3,1,NULL,NULL),(611,66,'derivacion_sanitaria','Derivación sanitaria',NULL,4,1,NULL,NULL),(612,66,'derivacion_policial','Derivación policial',NULL,5,1,NULL,NULL),(613,66,'derivacion_ong','Derivación ONG',NULL,6,1,NULL,NULL),(614,66,'otros','Otros',NULL,7,1,NULL,NULL),(615,67,'demanda_espontanea','Demanda espontánea',NULL,1,1,NULL,NULL),(616,67,'derivacion_judicial','Derivación judicial',NULL,2,1,NULL,NULL),(617,67,'derivacion_escolar','Derivación escolar',NULL,3,1,NULL,NULL),(618,67,'derivacion_sanitaria','Derivación sanitaria',NULL,4,1,NULL,NULL),(619,67,'derivacion_policial','Derivación policial',NULL,5,1,NULL,NULL),(620,67,'derivacion_ong','Derivación ONG',NULL,6,1,NULL,NULL),(621,67,'otros','Otros',NULL,7,1,NULL,NULL),(622,67,'sin_datos','Sin datos',NULL,8,1,NULL,NULL),(940,76,'encuentro_espontaneo','Encuentro espontáneo',NULL,1,1,NULL,NULL),(941,76,'educacion','Educación',NULL,2,1,NULL,NULL),(942,76,'salud','Salud',NULL,3,1,NULL,NULL),(943,76,'policia','Policía',NULL,4,1,NULL,NULL),(944,76,'juzgado','Juzgado',NULL,5,1,NULL,NULL),(945,76,'otros','Otros',NULL,6,1,NULL,NULL),(946,77,'reintegro_familiar','Reintegro familiar',NULL,1,1,NULL,NULL),(947,77,'adopcion','Adopción',NULL,2,1,NULL,NULL),(948,77,'autonomia','Autonomía',NULL,3,1,NULL,NULL),(949,77,'otros','Otros',NULL,4,1,NULL,NULL),(1021,83,'alojamiento_formal','Alojamiento formal',NULL,1,1,NULL,NULL),(1022,83,'familia_ampliada','Familia ampliada',NULL,2,1,NULL,NULL),(1023,83,'familia_de_acogimiento','Familia de acogimiento',NULL,3,1,NULL,NULL),(1024,83,'otro','Otro',NULL,4,1,NULL,NULL),(1032,86,'asiste','Asiste',NULL,1,1,NULL,NULL),(1033,86,'no_asiste','No asiste',NULL,2,1,NULL,NULL),(1335,94,'si_asiste','Sí asiste',NULL,1,1,NULL,NULL),(1336,94,'no_asiste_pero_asistio','No asiste pero asistió',NULL,2,1,NULL,NULL),(1337,94,'nunca_asistio','Nunca asistió',NULL,3,1,NULL,NULL),(1338,94,'sin_datos','Sin datos',NULL,4,1,NULL,NULL),(1350,97,'pami','PAMI',NULL,1,1,NULL,NULL),(1351,97,'ioma','IOMA',NULL,2,1,NULL,NULL),(1352,97,'obra_social_provincial','Obra social provincial',NULL,3,1,NULL,NULL),(1353,97,'obra_social_privada','Obra social privada',NULL,4,1,NULL,NULL),(1354,97,'prepaga','Prepaga',NULL,5,1,NULL,NULL),(1355,97,'sin_cobertura','Sin cobertura',NULL,6,1,NULL,NULL),(1356,97,'sin_datos','Sin datos',NULL,7,1,NULL,NULL),(1357,98,'egreso_con_familia_referente','Egreso con familia/referente',NULL,1,1,NULL,NULL),(1358,98,'egreso_en_el_domicilio','Egreso en el domicilio',NULL,2,1,NULL,NULL),(1359,98,'egreso_sistema_proteccion','Egreso Sistema Protección',NULL,3,1,NULL,NULL),(1360,98,'dispositivo_penal_en_territorio','Dispositivo penal en territorio',NULL,4,1,NULL,NULL),(1361,98,'dispositivo_de_restriccion','Dispositivo de restricción',NULL,5,1,NULL,NULL),(1362,98,'dispositivo_de_privacion','Dispositivo de privación',NULL,6,1,NULL,NULL),(1363,98,'egreso_familia_sistema_proteccion','Egreso familia + Sistema Protección',NULL,7,1,NULL,NULL),(1364,98,'abandono_fuga','Abandono/fuga',NULL,8,1,NULL,NULL),(1365,98,'mayoria_de_edad','Mayoría de edad',NULL,9,1,NULL,NULL),(1366,98,'sin_datos','Sin datos',NULL,10,1,NULL,NULL),(1419,102,'percibe_auh','Percibe AUH',NULL,1,1,NULL,NULL),(1420,102,'no_percibe_pero_corresponde','No percibe pero corresponde',NULL,2,1,NULL,NULL),(1421,102,'no_percibe_y_no_corresponde','No percibe y no corresponde',NULL,3,1,NULL,NULL),(1422,102,'sin_datos','Sin datos',NULL,4,1,NULL,NULL),(1423,103,'policia_provincial','Policía provincial',NULL,1,1,NULL,NULL),(1424,103,'gendarmeria','Gendarmería',NULL,2,1,NULL,NULL),(1425,103,'prefectura','Prefectura',NULL,3,1,NULL,NULL),(1426,103,'infanteria','Infantería',NULL,4,1,NULL,NULL),(1427,103,'cad','CAD',NULL,5,1,NULL,NULL),(1428,103,'comisaria','Comisaría',NULL,6,1,NULL,NULL),(1429,103,'juzgado','Juzgado',NULL,7,1,NULL,NULL),(1430,103,'establecimiento_de_privacion_de_libertad','Establecimiento de Privación de Libertad',NULL,8,1,NULL,NULL),(1431,103,'establecimiento_de_restriccion_de_libertad','Establecimiento de Restricción de Libertad',NULL,9,1,NULL,NULL),(1432,103,'medida_penal_en_territorio','Medida Penal en Territorio',NULL,10,1,NULL,NULL),(1433,103,'defensoria_de_menores','Defensoría de menores',NULL,11,1,NULL,NULL),(1434,103,'otros','Otros',NULL,12,1,NULL,NULL),(1435,103,'sin_datos','Sin datos',NULL,13,1,NULL,NULL),(1436,104,'investigacion_penal','Investigación penal',NULL,1,1,NULL,NULL),(1437,104,'elevacion_a_juicio','Elevación a juicio',NULL,2,1,NULL,NULL),(1438,104,'declaracion_de_responsabilidad','Declaración de responsabilidad',NULL,3,1,NULL,NULL),(1439,104,'ejecucion_penal','Ejecución penal',NULL,4,1,NULL,NULL),(1440,104,'sentencia_a_revision','Sentencia a revisión',NULL,5,1,NULL,NULL),(1441,104,'otros','Otros',NULL,6,1,NULL,NULL),(1442,104,'sin_datos','Sin datos',NULL,7,1,NULL,NULL),(1443,105,'medida_penal_en_territorio','Medida Penal en Territorio',NULL,1,1,NULL,NULL),(1444,105,'establecimiento_de_restriccion_de_libertad','Establecimiento de Restricción de Libertad',NULL,2,1,NULL,NULL),(1445,105,'establecimiento_de_privacion_de_libertad','Establecimiento de Privación de Libertad',NULL,3,1,NULL,NULL),(1446,105,'prision_domiciliara','Prisión Domiciliara',NULL,4,1,NULL,NULL),(1447,106,'medida_penal_en_territorio','Medida Penal en Territorio',NULL,1,1,NULL,NULL),(1448,106,'establecimiento_de_restriccion_de_libertad','Establecimiento de Restricción de Libertad',NULL,2,1,NULL,NULL),(1449,106,'establecimiento_de_privacion_de_libertad','Establecimiento de Privación de Libertad',NULL,3,1,NULL,NULL),(1450,106,'prision_domiciliaria','Prisión Domiciliaria',NULL,4,1,NULL,NULL),(1451,107,'centro_de_admision_y_derivacion','Centro de Admisión y Derivación',NULL,1,1,NULL,NULL),(1452,107,'guardia_en_comisaria','Guardia en Comisaría',NULL,2,1,NULL,NULL),(1453,108,'contravencion','Contravención',NULL,1,1,NULL,NULL),(1454,108,'presunto_delito','Presunto delito',NULL,2,1,NULL,NULL),(1455,108,'presunto_delito_flagrancia','Presunto delito/flagrancia',NULL,3,1,NULL,NULL),(1456,108,'averiguacion_de_antecedentes','Averiguación de antecedentes',NULL,4,1,NULL,NULL),(1457,108,'proteccion_de_derechos','Protección de derechos',NULL,5,1,NULL,NULL),(1458,108,'vulneracion_de_derechos','Vulneración de derechos',NULL,6,1,NULL,NULL),(1459,108,'sin_datos','Sin datos',NULL,7,1,NULL,NULL),(1460,109,'policia_provincial','Policía Provincial',NULL,1,1,NULL,NULL),(1461,109,'policia_municipal','Policía Municipal',NULL,2,1,NULL,NULL),(1462,109,'policia_federal','Policía Federal',NULL,3,1,NULL,NULL),(1463,109,'gendarmeria','Gendarmería',NULL,4,1,NULL,NULL),(1464,109,'prefectura','Prefectura',NULL,5,1,NULL,NULL),(1465,109,'infanteria','Infantería',NULL,6,1,NULL,NULL),(1466,109,'otros','Otros',NULL,7,1,NULL,NULL),(1467,109,'sin_datos','Sin datos',NULL,8,1,NULL,NULL),(1468,110,'no_corresponde','No corresponde',NULL,1,1,NULL,NULL),(1469,110,'hasta_12_hs','Hasta 12 hs',NULL,2,1,NULL,NULL),(1470,110,'entre_12_y_24_hs','Entre 12 y 24 hs',NULL,3,1,NULL,NULL),(1471,110,'entre_24_y_48_hs','Entre 24 y 48 hs',NULL,4,1,NULL,NULL),(1472,110,'entre_48_y_72_hs','Entre 48 y 72 hs',NULL,5,1,NULL,NULL),(1473,110,'entre_3_y_7_dias','Entre 3 y 7 días',NULL,6,1,NULL,NULL),(1474,110,'entre_7_y_15_dias','Entre 7 y 15 días',NULL,7,1,NULL,NULL),(1475,110,'entre_15_y_30_dias','Entre 15 y 30 días',NULL,8,1,NULL,NULL),(1476,110,'entre_1_y_2_meses','Entre 1 y 2 meses',NULL,9,1,NULL,NULL),(1477,110,'entre_2_y_3_meses','Entre 2 y 3 meses',NULL,10,1,NULL,NULL),(1478,110,'mas_de_3_meses','Más de 3 meses',NULL,11,1,NULL,NULL),(1479,110,'sin_datos','Sin datos',NULL,12,1,NULL,NULL),(1480,1,'sin_datos','Sin datos',NULL,3,1,NULL,NULL),(1788,182,'dni','DNI',NULL,1,1,NULL,NULL),(1789,182,'documento_extranjero','Documento extranjero',NULL,2,1,NULL,NULL),(1790,182,'otro_tipo_de_documentacion','Otro tipo de documentación',NULL,3,1,NULL,NULL),(1791,182,'sin_documentacion','Sin documentación',NULL,4,1,NULL,NULL),(1792,183,'argentina','Argentina',NULL,1,1,NULL,NULL),(1793,183,'bolivia','Bolivia',NULL,2,1,NULL,NULL),(1794,183,'brasil','Brasil',NULL,3,1,NULL,NULL),(1795,183,'chile','Chile',NULL,4,1,NULL,NULL),(1796,183,'paraguay','Paraguay',NULL,5,1,NULL,NULL),(1797,183,'uruguay','Uruguay',NULL,6,1,NULL,NULL),(1798,183,'venezuela','Venezuela',NULL,7,1,NULL,NULL),(1799,183,'colombia','Colombia',NULL,8,1,NULL,NULL),(1800,183,'peru','Perú',NULL,9,1,NULL,NULL),(1801,183,'otro','Otro',NULL,10,1,NULL,NULL),(1802,183,'sin_datos','Sin datos',NULL,11,1,NULL,NULL),(1803,184,'no_presenta_discapacidad','No presenta discapacidad',NULL,1,1,NULL,NULL),(1804,184,'visual','Visual',NULL,2,1,NULL,NULL),(1805,184,'auditiva','Auditiva',NULL,3,1,NULL,NULL),(1806,184,'mental','Mental',NULL,4,1,NULL,NULL),(1807,184,'motora','Motora',NULL,5,1,NULL,NULL),(1808,184,'visceral','Visceral',NULL,6,1,NULL,NULL),(1809,184,'otros','Otros',NULL,7,1,NULL,NULL),(1810,184,'sin_dato','Sin dato',NULL,8,1,NULL,NULL),(1811,185,'publica_exclusivamente','Pública exclusivamente',NULL,1,1,NULL,NULL),(1812,185,'obra_social','Obra Social',NULL,2,1,NULL,NULL),(1813,185,'prepaga','Prepaga',NULL,3,1,NULL,NULL),(1814,185,'otra_cobertura','Otra cobertura',NULL,4,1,NULL,NULL),(1815,185,'sin_datos','Sin datos',NULL,5,1,NULL,NULL),(1816,186,'masculino','Masculino',NULL,1,1,NULL,NULL),(1817,186,'femenino','Femenino',NULL,2,1,NULL,NULL),(1818,186,'otros_generos','Otros géneros',NULL,3,1,NULL,NULL),(1850,190,'sin_datos','Sin datos',NULL,1,1,NULL,NULL),(1858,192,'si','Sí',NULL,1,1,NULL,NULL),(1859,192,'no','No',NULL,2,1,NULL,NULL),(1860,192,'en_tramite','En trámite',NULL,3,1,NULL,NULL),(1861,192,'vencido','Vencido',NULL,4,1,NULL,NULL),(1862,192,'no_aplica','No aplica',NULL,5,1,NULL,NULL),(1863,192,'sin_datos','Sin datos',NULL,6,1,NULL,NULL),(2850,257,'opn','OPN',NULL,1,1,NULL,NULL),(2851,257,'justicia','Justicia',NULL,2,1,NULL,NULL),(2852,257,'otro','Otro',NULL,3,1,NULL,NULL),(2853,257,'tipo_de_dispositivo','Tipo de dispositivo',NULL,4,1,NULL,NULL),(2854,257,'residencial','Residencial',NULL,5,1,NULL,NULL),(2855,257,'familiar','Familiar',NULL,6,1,NULL,NULL),(2856,257,'familia_ampliada','Familia ampliada',NULL,7,1,NULL,NULL),(2857,257,'periodo_que_informa','Período que informa',NULL,8,1,NULL,NULL),(2858,257,'trim1','Trim1',NULL,9,1,NULL,NULL),(2859,257,'trim2','Trim2',NULL,10,1,NULL,NULL),(2860,257,'trim3','Trim3',NULL,11,1,NULL,NULL),(2861,257,'trim4','Trim4',NULL,12,1,NULL,NULL),(2862,258,'abandono','Abandono',NULL,1,1,NULL,NULL),(2863,258,'abuso_sexual_infanto_juvenil','Abuso sexual infanto-juvenil',NULL,2,1,NULL,NULL),(2864,258,'dificultad_en_el_acceso_a_la_escolaridad','Dificultad en el acceso a la escolaridad',NULL,3,1,NULL,NULL),(2865,258,'dificultad_en_el_acceso_a_la_justicia','Dificultad en el acceso a la justicia',NULL,4,1,NULL,NULL),(2866,258,'dificultad_en_el_acceso_a_la_vivienda_y_espacio_saludable','Dificultad en el acceso a la vivienda y espacio saludable',NULL,5,1,NULL,NULL),(2867,258,'dificultad_en_el_acceso_y_sostenimiento_de_la_seguridad_social','Dificultad en el acceso y sostenimiento de la seguridad social',NULL,6,1,NULL,NULL),(2868,258,'dificultad_en_el_acceso_a_la_salud','Dificultad en el acceso a la salud',NULL,7,1,NULL,NULL),(2869,258,'dificultades_en_el_ejercicio_de_la_responsabilidad_parental','Dificultades en el ejercicio de la responsabilidad parental',NULL,8,1,NULL,NULL),(2870,258,'explotacion_y_trabajo_infantil_adolescente','Explotación y trabajo infantil adolescente',NULL,9,1,NULL,NULL),(2871,258,'negligencia','Negligencia',NULL,10,1,NULL,NULL),(2872,258,'restriccion_a_la_libertad_de_expresion','Restricción a la libertad de expresión',NULL,11,1,NULL,NULL),(2873,258,'trata_y_trafico','Trata y tráfico',NULL,12,1,NULL,NULL),(2874,258,'violencia','Violencia',NULL,13,1,NULL,NULL),(2875,258,'vulneracion_a_la_identidad_y_discriminacion','Vulneración a la identidad y discriminación',NULL,14,1,NULL,NULL),(2876,258,'situacion_de_calle','Situación de calle',NULL,15,1,NULL,NULL),(2877,258,'consumo_problematico','Consumo problemático',NULL,16,1,NULL,NULL),(2878,258,'salud_mental','Salud mental',NULL,17,1,NULL,NULL),(2879,258,'otros','Otros',NULL,18,1,NULL,NULL),(2880,258,'motivo_de_cese','Motivo de cese',NULL,19,1,NULL,NULL),(2881,258,'cese_por_etorno_a_sus_padres_o_familia_conviviente','Cese por etorno a sus padres o familia conviviente',NULL,20,1,NULL,NULL),(2882,258,'cese_por_guarda_o_tutela_a_familiares_o_referentes_afectivos','Cese por guarda o tutela a familiares o referentes afectivos',NULL,21,1,NULL,NULL),(2883,258,'cese_por_guarda_o_tutela_a_adultos_no_parientes_y_sin_vinculo_afectivo_previo_acreditado','Cese por guarda o tutela a adultos no parientes y sin vínculo afectivo previo acreditado',NULL,22,1,NULL,NULL),(2884,258,'cese_por_guarda_con_fines_de_adopcion','Cese por guarda con fines de adopción',NULL,23,1,NULL,NULL),(2885,258,'cese_por_mayoria_de_edad_con_proyecto_autonomo_con_pae','Cese por mayoría de edad CON proyecto autónomo (CON PAE)',NULL,24,1,NULL,NULL),(2886,258,'cese_por_mayoria_de_edad_con_proyecto_autonomo_sin_pae','Cese por mayoría de edad CON proyecto autónomo (SIN PAE)',NULL,25,1,NULL,NULL),(2887,258,'cese_por_mayoria_de_edad_sin_proyecto_autonomo','Cese por mayoría de edad SIN proyecto autónomo',NULL,26,1,NULL,NULL),(2888,258,'otros_motivos_de_cese_de_la_mpe','Otros motivos de cese de la MPE',NULL,27,1,NULL,NULL),(2914,260,'opn','OPN',NULL,1,1,NULL,NULL),(2915,260,'justicia','Justicia',NULL,2,1,NULL,NULL),(2916,260,'otro','Otro',NULL,3,1,NULL,NULL),(2917,261,'trim1','Trim1',NULL,1,1,NULL,NULL),(2918,261,'trim2','Trim2',NULL,2,1,NULL,NULL),(2919,261,'trim3','Trim3',NULL,3,1,NULL,NULL),(2920,261,'trim4','Trim4',NULL,4,1,NULL,NULL),(2925,263,'cese_por_guarda_con_fines_de_adopcion','Cese por guarda con fines de adopción',NULL,1,1,NULL,NULL),(2926,263,'cese_por_mayoria_de_edad_con_proyecto_autonomo_con_pae','Cese por mayoría de edad CON proyecto autónomo (CON PAE)',NULL,2,1,NULL,NULL),(2927,263,'cese_por_mayoria_de_edad_con_proyecto_autonomo_sin_pae','Cese por mayoría de edad CON proyecto autónomo (SIN PAE)',NULL,3,1,NULL,NULL),(2928,263,'cese_por_mayoria_de_edad_sin_proyecto_autonomo','Cese por mayoría de edad SIN proyecto autónomo',NULL,4,1,NULL,NULL),(2929,263,'otros_motivos_de_cese_de_la_mpe','Otros motivos de cese de la MPE',NULL,5,1,NULL,NULL);
/*!40000 ALTER TABLE `runac_c1_catalogo_opcion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c1_dimension`
--

DROP TABLE IF EXISTS `runac_c1_dimension`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c1_dimension` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `hoja_id` bigint NOT NULL COMMENT 'Hoja a la que pertenece la dimensión.',
  `nombre_esperado` varchar(255) NOT NULL COMMENT 'Texto que debe aparecer en la celda combinada ubicada sobre los títulos de las columnas.',
  `descripcion` text COMMENT 'Descripción funcional del grupo de campos representado por la dimensión.',
  `orden` int NOT NULL COMMENT 'Orden en que aparece la dimensión dentro de la hoja.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c1_dimension_index_2` (`hoja_id`,`orden`),
  CONSTRAINT `runac_c1_dimension_ibfk_1` FOREIGN KEY (`hoja_id`) REFERENCES `runac_c1_hoja` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Define los encabezados que agrupan conjuntos de campos dentro de una hoja.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c1_dimension`
--

LOCK TABLES `runac_c1_dimension` WRITE;
/*!40000 ALTER TABLE `runac_c1_dimension` DISABLE KEYS */;
INSERT INTO `runac_c1_dimension` VALUES (1,7,'Datos institucionales','Columnas A a H del Excel (8 campos).',1),(2,7,'El establecimiento cuenta con...','Columnas J a O del Excel (6 campos).',2),(3,7,'Cuenta con PROTOCOLO ...','Columnas P a R del Excel (3 campos).',3),(4,7,'Capacidad /cobertura','Columnas S a U del Excel (3 campos).',4),(5,7,'Perfiles poblacionales admitidos','Columnas V a AE del Excel (10 campos).',5),(6,7,'Personal del dispositivo: CANTIDAD DE PERSONAS','Columnas AF a AI del Excel (4 campos).',6),(7,7,'CAPACITACIONES RECIBIDAS POR EL PERSONAL QUE TRABAJA EN EL DISPOSITIVO EN EL ÚLTIMO AÑO','Columnas AJ a AW del Excel (14 campos).',7),(8,7,'SOBRE EL PROYECTO DE RESTITUCIÓN DE DERECHOS','Columnas AX a AZ del Excel (3 campos).',8),(9,7,'INSERCIÓN FAMILIAR Y COMUNITARIA','Columnas BA a BI del Excel (9 campos).',9),(10,8,'Dispositivo/espacio','Columnas B a J del Excel (9 campos).',1),(11,8,'Niño o adolescente','Columnas K a AM del Excel (29 campos).',2),(12,8,'Referente','Columnas AN a BE del Excel (18 campos).',3),(13,8,'Medida','Columnas BF a BK del Excel (6 campos).',4),(14,9,'Modalidad de cuidado','Columnas B a C del Excel (2 campos).',1),(15,9,'Modalidad formal residencial','Columnas D a F del Excel (3 campos).',2),(16,9,'Niño o adolescente','Columnas G a AA del Excel (21 campos).',3),(17,9,'Modalidad Formal Familiar','Columnas AB a AC del Excel (2 campos).',4),(18,9,'Modalidad Familia Ampliada','Columnas AD a AE del Excel (2 campos).',5),(19,9,'Medida de Protección Excepcional','Columnas AF a AN del Excel (9 campos).',6),(26,20,'NyA','Columnas A a D del Excel (4 campos).',1),(27,20,'Medida de Protección Expcecional (MPE)','Columnas E a M del Excel (9 campos).',2),(28,20,'Modalidad formal residencial','Columnas N a O del Excel (2 campos).',3),(29,20,'Modalidad Formal Familiar','Columnas P a R del Excel (3 campos).',4),(30,20,'Modalidad Familia Ampliada','Columnas S a V del Excel (4 campos).',5),(31,20,'Proyecto de Restitución','Columnas W a Y del Excel (3 campos).',6),(32,20,'Situación del NyA','Columnas Z a AB del Excel (3 campos).',7),(33,20,'Cese de MPE','Columnas AC a AD del Excel (2 campos).',8),(34,21,'Dispositivo','Columnas B a F del Excel (5 campos).',1),(35,21,'Niño o adolescente','Columnas G a AA del Excel (21 campos).',2),(36,21,'Datos penales / Medida','Columnas AB a AK del Excel (10 campos).',3),(37,22,'Dispositivo/espacio','Columnas B a F del Excel (5 campos).',1),(38,22,'Niño o adolescente','Columnas G a Z del Excel (20 campos).',2),(39,22,'Datos penales / Medida','Columnas AA a AP del Excel (16 campos).',3);
/*!40000 ALTER TABLE `runac_c1_dimension` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c1_hoja`
--

DROP TABLE IF EXISTS `runac_c1_hoja`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c1_hoja` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `archivo_version_id` bigint NOT NULL COMMENT 'Versión de archivo a la que pertenece la hoja.',
  `nombre_esperado` varchar(255) NOT NULL COMMENT 'Nombre exacto que debe tener la hoja dentro del archivo Excel.',
  `descripcion` text COMMENT 'Descripción funcional de la información contenida en la hoja.',
  `orden_procesamiento` int NOT NULL COMMENT 'Orden en que debe procesarse dentro del archivo.',
  `fila_encabezados` int NOT NULL DEFAULT '1' COMMENT 'Fila donde se encuentran los nombres de los campos. Los datos comienzan en la fila siguiente.',
  `obligatoria` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Indica si la ausencia de la hoja impide continuar con la importación.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c1_hoja_index_0` (`archivo_version_id`,`nombre_esperado`),
  UNIQUE KEY `runac_c1_hoja_index_1` (`archivo_version_id`,`orden_procesamiento`),
  CONSTRAINT `runac_c1_hoja_ibfk_1` FOREIGN KEY (`archivo_version_id`) REFERENCES `runac_c1_archivo_version` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Define las hojas que deben encontrarse dentro de cada versión de archivo.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c1_hoja`
--

LOCK TABLES `runac_c1_hoja` WRITE;
/*!40000 ALTER TABLE `runac_c1_hoja` DISABLE KEYS */;
INSERT INTO `runac_c1_hoja` VALUES (7,2,'M Residencial','Listado de dispositivos de modalidad de cuidado residencial. MODELO PARA COMPLETAR Y ADJUNTAR',1,3,1),(8,3,'MPI','Registro NyA con Medida de Protección Integral',1,3,1),(9,4,'MPE','Registro NyA con Medida de Protección Excepcional',1,3,1),(12,1,'CRC','Listado de los dispositivos penales Centros de Régimen Cerrado. MODELO PARA COMPLETAR Y ADJUNTAR',1,2,1),(13,1,'CRSC','Listado de los dispositivos penales Centros de Régimen Semicerrado. MODELO PARA COMPLETAR Y ADJUNTAR',2,2,1),(14,1,'MPT','Listado de Dispositivos de Medidas Penales en Territorio. MODELO PARA COMPLETAR Y ADJUNTAR',3,2,1),(15,1,'CAD','Listado de Centro de Admisión y Derivación (CAD). MODELO PARA COMPLETAR Y ADJUNTAR',4,2,1),(16,1,'Guardia Comisaría','Listado de Equipos de guardia especializada en dependencias POLICIALES. MODELO PARA COMPLETAR Y ADJUNTAR',5,2,1),(18,7,'NyA',NULL,1,2,1),(19,7,'Prov_Dto_Localidad',NULL,2,1,1),(20,8,'MPE',NULL,1,3,1),(21,5,'MPJ','Relevamiento Dispositivos Penales Juveniles',1,3,1),(22,5,'DAE','Relevamiento CAD y Guardia en Comisaría',2,3,1);
/*!40000 ALTER TABLE `runac_c1_hoja` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c1_regla`
--

DROP TABLE IF EXISTS `runac_c1_regla`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c1_regla` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `tipo_regla_id` bigint NOT NULL COMMENT 'Tipo de validación que debe ejecutar el importador.',
  `nombre` varchar(255) NOT NULL COMMENT 'Nombre técnico y estable que identifica la regla concreta.',
  `descripcion` text COMMENT 'Explicación funcional de la validación.',
  `parametros` json DEFAULT NULL COMMENT 'Valores necesarios para ejecutar la regla, de acuerdo con los parámetros definidos para su tipo.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`),
  KEY `tipo_regla_id` (`tipo_regla_id`),
  CONSTRAINT `runac_c1_regla_ibfk_1` FOREIGN KEY (`tipo_regla_id`) REFERENCES `runac_c1_tipo_regla` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=155 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Una validación concreta, reutilizable en distintos campos.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c1_regla`
--

LOCK TABLES `runac_c1_regla` WRITE;
/*!40000 ALTER TABLE `runac_c1_regla` DISABLE KEYS */;
INSERT INTO `runac_c1_regla` VALUES (1,2,'mpi_fecha_del_relevamiento_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(2,8,'mpi_mail_de_contacto_ejecutar_funcion','el campo es una dirección de correo (confianza alta)','{\"funcion\": \"validar_mail\"}'),(3,6,'mpi_n_dni_unico_en_hoja','el requerimiento pide que en un mismo Excel no haya un DNI repetido (confianza alta)','{}'),(4,7,'mpi_n_dni_unico_combinado','el apartado técnico da como ejemplo no repetir la combinación de documento y fecha de inicio de la medida (confianza media)','{\"campos_combinados\": [\"n_dni\", \"fecha_de_la_medida_mpi\"]}'),(5,8,'mpi_n_de_cuil_ejecutar_funcion','el campo es un CUIL y el apartado técnico ya prevé esa función (confianza alta)','{\"funcion\": \"validar_cuil\"}'),(6,5,'mpi_n_de_cuil_formato','formato de CUIL indicado como ejemplo en el apartado técnico (confianza media)','{\"formato\": \"NN-NNNNNNNN-N\"}'),(7,2,'mpi_fecha_de_nacimiento_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(8,1,'mpi_edad_rango','el registro es de niños, niñas y adolescentes (confianza baja)','{\"maximo\": 17, \"minimo\": 0}'),(9,3,'mpi_tipo_de_discapacidad_obligatorio_si','sólo tiene sentido completarlo cuando \"¿Presenta alguna discapacidad?\" es \"Si\" (confianza media)','{\"operador\": \"IGUAL\", \"campo_condicion\": \"presenta_alguna_discapacidad\", \"valor_condicion\": \"Si\"}'),(10,3,'mpi_posee_cud_obligatorio_si','sólo tiene sentido completarlo cuando \"¿Presenta alguna discapacidad?\" es \"Si\" (confianza media)','{\"operador\": \"IGUAL\", \"campo_condicion\": \"presenta_alguna_discapacidad\", \"valor_condicion\": \"Si\"}'),(11,3,'mpi_pueblo_originario_especificar_obligatorio_si','sólo tiene sentido completarlo cuando \"¿Se identifica con algún pueblo originario?\" es \"Sí\" (confianza media)','{\"operador\": \"IGUAL\", \"campo_condicion\": \"se_identifica_con_algun_pueblo_originario\", \"valor_condicion\": \"Sí\"}'),(12,2,'mpi_fecha_de_nacimiento_del_referente_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(13,8,'mpi_telefono_y_mail_del_referente_ejecutar_funcion','el campo es una dirección de correo (confianza alta)','{\"funcion\": \"validar_mail\"}'),(14,2,'mpi_fecha_de_la_medida_mpi_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(15,2,'mpe_fecha_del_relevamiento_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(16,6,'mpe_n_dni_unico_en_hoja','el requerimiento pide que en un mismo Excel no haya un DNI repetido (confianza alta)','{}'),(17,7,'mpe_n_dni_unico_combinado','el apartado técnico da como ejemplo no repetir la combinación de documento y fecha de inicio de la medida (confianza media)','{\"campos_combinados\": [\"n_dni\", \"fecha_de_inicio_mpe\"]}'),(18,8,'mpe_n_de_cuil_ejecutar_funcion','el campo es un CUIL y el apartado técnico ya prevé esa función (confianza alta)','{\"funcion\": \"validar_cuil\"}'),(19,5,'mpe_n_de_cuil_formato','formato de CUIL indicado como ejemplo en el apartado técnico (confianza media)','{\"formato\": \"NN-NNNNNNNN-N\"}'),(20,2,'mpe_fecha_de_nacimiento_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(21,1,'mpe_edad_rango','el registro es de niños, niñas y adolescentes (confianza baja)','{\"maximo\": 17, \"minimo\": 0}'),(22,3,'mpe_tipo_de_discapacidad_obligatorio_si','sólo tiene sentido completarlo cuando \"¿Presenta alguna discapacidad?\" es \"Si\" (confianza media)','{\"operador\": \"IGUAL\", \"campo_condicion\": \"presenta_alguna_discapacidad\", \"valor_condicion\": \"Si\"}'),(23,3,'mpe_posee_cud_obligatorio_si','sólo tiene sentido completarlo cuando \"¿Presenta alguna discapacidad?\" es \"Si\" (confianza media)','{\"operador\": \"IGUAL\", \"campo_condicion\": \"presenta_alguna_discapacidad\", \"valor_condicion\": \"Si\"}'),(24,3,'mpe_pueblo_originario_especificar_obligatorio_si','es el campo de detalle de \"¿Pertenece a pueblo originario?\" (confianza baja)','{\"operador\": \"EN_LISTA\", \"campo_condicion\": \"pertenece_a_pueblo_originario\", \"valor_condicion\": \"Otros\"}'),(25,2,'mpe_familia_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(26,2,'mpe_id_familia_ampliada_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(27,2,'mpe_familia_ampliada_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(28,2,'mpe_fecha_de_inicio_mpe_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(29,2,'mpj_dae_fecha_del_relevamiento_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(30,6,'mpj_dae_n_dni_unico_en_hoja','el requerimiento pide que en un mismo Excel no haya un DNI repetido (confianza alta)','{}'),(31,7,'mpj_dae_n_dni_unico_combinado','el apartado técnico da como ejemplo no repetir la combinación de documento y fecha de inicio de la medida (confianza media)','{\"campos_combinados\": [\"n_dni\", \"fecha_de_ingreso_al_dispositivo\"]}'),(32,2,'mpj_dae_fecha_de_nacimiento_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(33,1,'mpj_dae_edad_rango','el registro es de niños, niñas y adolescentes (confianza baja)','{\"maximo\": 17, \"minimo\": 0}'),(34,3,'mpj_dae_tipo_de_discapacidad_obligatorio_si','sólo tiene sentido completarlo cuando \"¿Presenta alguna discapacidad?\" es \"Si\" (confianza media)','{\"operador\": \"IGUAL\", \"campo_condicion\": \"presenta_alguna_discapacidad\", \"valor_condicion\": \"Si\"}'),(35,3,'mpj_dae_posee_cud_obligatorio_si','sólo tiene sentido completarlo cuando \"¿Presenta alguna discapacidad?\" es \"Si\" (confianza media)','{\"operador\": \"IGUAL\", \"campo_condicion\": \"presenta_alguna_discapacidad\", \"valor_condicion\": \"Si\"}'),(36,3,'mpj_dae_pueblo_originario_especificar_obligatorio_si','sólo tiene sentido completarlo cuando \"¿Se identifica con algún pueblo originario?\" es \"Sí\" (confianza media)','{\"operador\": \"IGUAL\", \"campo_condicion\": \"se_identifica_con_algun_pueblo_originario\", \"valor_condicion\": \"Sí\"}'),(37,2,'mpj_dae_fecha_de_ingreso_al_dispositivo_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(38,3,'mpj_dae_especificar_procedencia_obligatorio_si','es el campo de detalle de \"Procedencia inmediata\" (confianza baja)','{\"operador\": \"EN_LISTA\", \"campo_condicion\": \"procedencia_inmediata\", \"valor_condicion\": \"Otros\"}'),(39,2,'mpj_dae_fecha_de_egreso_del_dispositivo_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(40,4,'mpj_dae_fecha_de_egreso_del_dispositivo_comparar_campo','\"Fecha de egreso del dispositivo\" no puede ser anterior a \"Fecha de ingreso al dispositivo\" (confianza alta)','{\"operador\": \"MAYOR_IGUAL\", \"campo_comparacion\": \"fecha_de_ingreso_al_dispositivo\"}'),(41,2,'mpj_dae_especificar_destino_al_egreso_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(42,4,'mpj_dae_especificar_destino_al_egreso_comparar_campo','\"Especificar destino al egreso\" no puede ser anterior a \"Fecha de ingreso al dispositivo\" (confianza alta)','{\"operador\": \"MAYOR_IGUAL\", \"campo_comparacion\": \"fecha_de_ingreso_al_dispositivo\"}'),(43,3,'mpj_dae_especificar_destino_al_egreso_obligatorio_si','es el campo de detalle de \"Destino al egreso\" (confianza baja)','{\"operador\": \"EN_LISTA\", \"campo_condicion\": \"destino_al_egreso\", \"valor_condicion\": \"Otros\"}'),(53,2,'mpj_dae_hora_de_ingreso_al_dispositivo_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(56,2,'mpj_dae_hora_de_egreso_del_dispositivo_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(57,4,'mpj_dae_hora_de_egreso_del_dispositivo_comparar_campo','\"Hora de egreso del dispositivo\" no puede ser anterior a \"Fecha de ingreso al dispositivo\" (confianza alta)','{\"operador\": \"MAYOR_IGUAL\", \"campo_comparacion\": \"fecha_de_ingreso_al_dispositivo\"}'),(61,1,'mpj_dae_edad_al_ingreso_rango','el registro es de niños, niñas y adolescentes (confianza baja)','{\"maximo\": 17, \"minimo\": 0}'),(62,2,'mpj_dae_edad_al_ingreso_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(63,41,'mpi_n_dni_prohibido_si','El número de DNI no se completa cuando la situación de documentación declara que no hay número.','{\"operador\": \"EN_LISTA\", \"campo_condicion\": \"situacion_de_documentacion\", \"valor_condicion\": [\"No posee N° DNI\", \"Sin inscripción\", \"DNI en trámite\"]}'),(64,41,'mpe_n_dni_prohibido_si','El número de DNI no se completa cuando la situación de documentación declara que no hay número.','{\"operador\": \"EN_LISTA\", \"campo_condicion\": \"situacion_de_documentacion\", \"valor_condicion\": [\"No posee N° DNI\", \"Sin inscripción\", \"DNI en trámite\"]}'),(65,41,'mpj_n_dni_prohibido_si','El número de DNI no se completa cuando la situación de documentación declara que no hay número.','{\"operador\": \"EN_LISTA\", \"campo_condicion\": \"situacion_de_documentacion\", \"valor_condicion\": [\"No posee N° DNI\", \"Sin inscripción\", \"DNI en trámite\"]}'),(66,41,'dae_n_dni_prohibido_si','El número de DNI no se completa cuando la situación de documentación declara que no hay número.','{\"operador\": \"EN_LISTA\", \"campo_condicion\": \"situacion_de_documentacion\", \"valor_condicion\": [\"No posee N° DNI\", \"Sin inscripción\", \"DNI en trámite\"]}'),(67,42,'mpj_nombre_del_dispositivo_existe_en_archivo','El dispositivo nombrado en la nómina tiene que estar declarado en el archivo de dispositivos penales.','{\"campo\": \"nombre_del_dispositvo\", \"archivo\": \"DISP_PENAL\"}'),(68,42,'dae_nombre_del_dispositivo_existe_en_archivo','El dispositivo nombrado en la nómina tiene que estar declarado en el archivo de dispositivos penales.','{\"campo\": \"nombre_del_dispositvo\", \"archivo\": \"DISP_PENAL\"}'),(69,3,'mpi_n_dni_obligatorio_si','El número de DNI es obligatorio cuando la situación de documentación declara que la persona lo tiene.','{\"operador\": \"EN_LISTA\", \"campo_condicion\": \"situacion_de_documentacion\", \"valor_condicion\": [\"Posee N° DNI\", \"Perdida de documentación\"]}'),(70,3,'mpe_n_dni_obligatorio_si','El número de DNI es obligatorio cuando la situación de documentación declara que la persona lo tiene.','{\"operador\": \"EN_LISTA\", \"campo_condicion\": \"situacion_de_documentacion\", \"valor_condicion\": [\"Posee N° DNI\", \"Perdida de documentación\"]}'),(71,3,'mpj_n_dni_obligatorio_si','El número de DNI es obligatorio cuando la situación de documentación declara que la persona lo tiene.','{\"operador\": \"EN_LISTA\", \"campo_condicion\": \"situacion_de_documentacion\", \"valor_condicion\": [\"Posee N° DNI\", \"Perdida de documentación\"]}'),(72,3,'dae_n_dni_obligatorio_si','El número de DNI es obligatorio cuando la situación de documentación declara que la persona lo tiene.','{\"operador\": \"EN_LISTA\", \"campo_condicion\": \"situacion_de_documentacion\", \"valor_condicion\": [\"Posee N° DNI\", \"Perdida de documentación\"]}'),(77,6,'legajo_nya_n_dni_unico_en_hoja','el requerimiento pide que en un mismo Excel no haya un DNI repetido (confianza alta)','{}'),(78,8,'legajo_nya_n_de_cuil_ejecutar_funcion','el campo es un CUIL y el apartado técnico ya prevé esa función (confianza alta)','{\"funcion\": \"validar_cuil\"}'),(79,5,'legajo_nya_n_de_cuil_formato','formato de CUIL indicado como ejemplo en el apartado técnico (confianza media)','{\"formato\": \"NN-NNNNNNNN-N\"}'),(80,6,'legajo_nya_otro_nuero_de_documentacion_de_identidad_si_no_cuenta_con_dni_unico_en_hoja','el requerimiento pide que en un mismo Excel no haya un DNI repetido (confianza alta)','{}'),(81,2,'legajo_nya_fecha_de_nacimiento_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(82,2,'legajo_nya_departamento_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(83,3,'legajo_nya_pueblo_originario_especificar_obligatorio_si','sólo tiene sentido completarlo cuando \"¿Pertenece a pueblo originario? (o se identifica con algún pueblo originario?)\" es \"Sí\" (confianza media)','{\"operador\": \"IGUAL\", \"campo_condicion\": \"pertenece_a_pueblo_originario_o_se_identifica_con_algun_p_003571\", \"valor_condicion\": \"Sí\"}'),(84,2,'legajo_nya_fecha_de_actualizacion_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(85,8,'mpe_cuil_o_documento_de_identidad_ejecutar_funcion','el campo es un CUIL y el apartado técnico ya prevé esa función (confianza alta)','{\"funcion\": \"validar_cuil\"}'),(86,5,'mpe_cuil_o_documento_de_identidad_formato','formato de CUIL indicado como ejemplo en el apartado técnico (confianza media)','{\"formato\": \"NN-NNNNNNNN-N\"}'),(88,2,'mpe_departamento_de_residencia_de_la_familia_dispositivo_fami_597d04_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(91,2,'mpe_vinculo_con_el_nya_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(92,2,'mpe_departamento_de_residencia_de_la_familia_dispositivo_fami_e8c08b_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(93,2,'mpe_fecha_de_cese_comparar_valor','una fecha registrada no debería ser futura (confianza media)','{\"valor\": \"HOY\", \"operador\": \"MENOR_IGUAL\"}'),(94,4,'mpe_fecha_de_cese_comparar_campo','\"Fecha de cese\" no puede ser anterior a \"Fecha de inicio MPE\" (confianza alta)','{\"operador\": \"MAYOR_IGUAL\", \"campo_comparacion\": \"fecha_de_inicio_mpe\"}'),(136,42,'mpe_nombre_de_la_residencia_existe_en_archivo','La residencia u hogar que nombra el MPE tiene que estar declarada en el archivo de dispositivos de cuidado.','{\"campo\": \"nombre_del_dispositvo\", \"archivo\": \"DISP_SCP\"}'),(137,1,'rango_horas_semanales','Las horas semanales no pueden superar las que tiene una semana.','{\"maximo\": 168, \"minimo\": 0}'),(138,1,'rango_plantel','Cantidad de personas que trabajan en el dispositivo. El máximo es provisorio.','{\"maximo\": 200, \"minimo\": 0}'),(139,1,'rango_alojados','Cantidad de chicas y chicos alojados. El máximo es provisorio.','{\"maximo\": 200, \"minimo\": 0}'),(140,1,'rango_dias_de_permanencia','Días de permanencia. El máximo provisorio son diez años.','{\"maximo\": 3650, \"minimo\": 0}'),(141,1,'rango_no_negativo','Una cantidad informada no puede ser negativa.','{\"minimo\": 0}'),(142,1,'rango_identificador','Un identificador empieza en uno: no es cero ni negativo.','{\"minimo\": 1}'),(144,1,'tope_plantel','Techo imposible para la cantidad de personas que trabajan en un dispositivo.','{\"maximo\": 5000, \"minimo\": 0}'),(145,1,'tope_alojados','Techo imposible para la cantidad de chicas y chicos alojados.','{\"maximo\": 5000, \"minimo\": 0}'),(146,1,'tope_dias_de_permanencia','Techo imposible para los días de permanencia: cien años.','{\"maximo\": 36500, \"minimo\": 0}'),(147,1,'tope_edad','Techo imposible para una edad.','{\"maximo\": 120, \"minimo\": 0}'),(148,1,'tope_monto_de_la_pena','El monto de la pena no puede ser negativo ni desmesurado.','{\"maximo\": 100000, \"minimo\": 0}'),(149,1,'tope_identificador','Un identificador empieza en uno y no puede ser desmesurado.','{\"maximo\": 999999999, \"minimo\": 1}'),(151,1,'rango_horas_de_permanencia','Permanencia declarada en horas: más de una semana llama la atención en un dispositivo de tránsito.','{\"maximo\": 168, \"minimo\": 0}'),(152,1,'tope_horas_de_permanencia','Más de un año en horas no es un dato: es un error de carga.','{\"maximo\": 8760, \"minimo\": 0}'),(153,41,'mpe_residencia_solo_si_alojamiento_formal','La residencia no se nombra cuando la modalidad de cuidado no es alojamiento formal.','{\"operador\": \"DISTINTO\", \"campo_condicion\": \"modalidad_de_cuidado\", \"valor_condicion\": \"Alojamiento formal\"}'),(154,3,'mpe_residencia_obligatoria_si_alojamiento_formal','Si la modalidad de cuidado es alojamiento formal, hay que decir en qué residencia.','{\"operador\": \"IGUAL\", \"campo_condicion\": \"modalidad_de_cuidado\", \"valor_condicion\": \"Alojamiento formal\"}');
/*!40000 ALTER TABLE `runac_c1_regla` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c1_tipo_regla`
--

DROP TABLE IF EXISTS `runac_c1_tipo_regla`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c1_tipo_regla` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre técnico y estable del tipo de regla, por ejemplo RANGO, OBLIGATORIO_SI, EXISTE_EN o EJECUTAR_FUNCION.',
  `descripcion` text COMMENT 'Explica el comportamiento general de la validación.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=127 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Vocabulario genérico de validaciones. Los mismos tipos sirven para cualquier relevamiento; cambian los parámetros.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c1_tipo_regla`
--

LOCK TABLES `runac_c1_tipo_regla` WRITE;
/*!40000 ALTER TABLE `runac_c1_tipo_regla` DISABLE KEYS */;
INSERT INTO `runac_c1_tipo_regla` VALUES (1,'RANGO','Verifica que el valor se encuentre entre un mínimo y un máximo.'),(2,'COMPARAR_VALOR','Compara el contenido del campo con un valor determinado.'),(3,'OBLIGATORIO_SI','Determina que un campo sea obligatorio cuando otro campo cumple una condición.'),(4,'COMPARAR_CAMPO','Compara el contenido del campo con otro campo del mismo registro.'),(5,'FORMATO','Verifica que el contenido respete un formato determinado.'),(6,'UNICO_EN_HOJA','Verifica que el valor no se repita dentro de la misma hoja importada.'),(7,'UNICO_COMBINADO','Verifica que no se repita una combinación determinada de campos.'),(8,'EJECUTAR_FUNCION','Ejecuta una función de validación implementada y habilitada previamente en SISOC.'),(41,'PROHIBIDO_SI','Determina que un campo deba quedar vacío cuando otro campo cumple una condición.'),(42,'EXISTE_EN_ARCHIVO','Verifica que el valor exista en otro archivo ya importado del mismo período.');
/*!40000 ALTER TABLE `runac_c1_tipo_regla` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c1_tipo_regla_parametro`
--

DROP TABLE IF EXISTS `runac_c1_tipo_regla_parametro`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c1_tipo_regla_parametro` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `tipo_regla_id` bigint NOT NULL COMMENT 'Tipo de regla al que pertenece el parámetro.',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre técnico del parámetro dentro del JSON, por ejemplo minimo, maximo, operador o campo_condicion.',
  `tipo_parametro` enum('TEXTO','ENTERO','DECIMAL','FECHA','HORA','BOOLEANO','CAMPO','LISTA') NOT NULL COMMENT 'Tipo de valor que debe contener el parámetro.',
  `obligatorio` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Indica si el parámetro debe estar presente para configurar la regla.',
  `orden` int NOT NULL COMMENT 'Orden de presentación del parámetro.',
  `descripcion` text COMMENT 'Explica el significado y uso del parámetro.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c1_tipo_regla_parametro_index_8` (`tipo_regla_id`,`nombre`),
  UNIQUE KEY `runac_c1_tipo_regla_parametro_index_9` (`tipo_regla_id`,`orden`),
  CONSTRAINT `runac_c1_tipo_regla_parametro_ibfk_1` FOREIGN KEY (`tipo_regla_id`) REFERENCES `runac_c1_tipo_regla` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=199 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Define los parámetros esperados por cada tipo de regla.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c1_tipo_regla_parametro`
--

LOCK TABLES `runac_c1_tipo_regla_parametro` WRITE;
/*!40000 ALTER TABLE `runac_c1_tipo_regla_parametro` DISABLE KEYS */;
INSERT INTO `runac_c1_tipo_regla_parametro` VALUES (1,1,'minimo','DECIMAL',1,1,'Valor mínimo admitido, inclusive.'),(2,1,'maximo','DECIMAL',1,2,'Valor máximo admitido, inclusive.'),(3,2,'operador','TEXTO',1,1,'IGUAL, DISTINTO, MAYOR, MAYOR_IGUAL, MENOR, MENOR_IGUAL, EN_LISTA o NO_EN_LISTA.'),(4,2,'valor','TEXTO',1,2,'Valor contra el que se compara.'),(5,3,'campo_condicion','CAMPO',1,1,'Campo cuyo valor dispara la obligatoriedad.'),(6,3,'operador','TEXTO',1,2,'IGUAL, DISTINTO, ES_VACIO, NO_ES_VACIO, EN_LISTA o NO_EN_LISTA.'),(7,3,'valor_condicion','TEXTO',0,3,'Valor de la condición, cuando el operador lo requiere.'),(8,4,'campo_comparacion','CAMPO',1,1,'Campo del mismo registro contra el que se compara.'),(9,4,'operador','TEXTO',1,2,'IGUAL, DISTINTO, MAYOR, MAYOR_IGUAL, MENOR o MENOR_IGUAL.'),(10,5,'formato','TEXTO',1,1,'Patrón esperado, por ejemplo NN-NNNNNNNN-N.'),(11,7,'campos_combinados','LISTA',1,1,'Nombres de los campos que en conjunto no pueden repetirse.'),(12,8,'funcion','TEXTO',1,1,'Nombre de la función habilitada, por ejemplo validar_cuil.'),(61,41,'campo_condicion','CAMPO',1,1,'Campo cuyo valor prohíbe completar este.'),(62,41,'operador','TEXTO',1,2,'IGUAL, DISTINTO, ES_VACIO, NO_ES_VACIO, EN_LISTA o NO_EN_LISTA.'),(63,41,'valor_condicion','TEXTO',0,3,'Valor de la condición, cuando el operador lo requiere.'),(64,42,'archivo','TEXTO',1,1,'Código del archivo referenciado.'),(65,42,'hoja','TEXTO',0,2,'Hoja del archivo referenciado; se puede omitir si tiene una sola.'),(66,42,'campo','CAMPO',1,3,'Campo del archivo referenciado donde tiene que existir el valor.');
/*!40000 ALTER TABLE `runac_c1_tipo_regla_parametro` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_disp_penal_v1_cad`
--

DROP TABLE IF EXISTS `runac_c2_disp_penal_v1_cad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_disp_penal_v1_cad` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `importacion_id` bigint NOT NULL COMMENT 'Importación a la que pertenece la fila.',
  `numero_fila` int NOT NULL COMMENT 'Número de fila en el Excel, tal como lo ve quien completa la planilla.',
  `estado` enum('VALIDA','CON_ADVERTENCIA','EDITADA') NOT NULL DEFAULT 'VALIDA' COMMENT 'Resultado de la validación de la fila. Las filas con bloqueantes no llegan a incorporarse.',
  `hash_contenido` char(40) DEFAULT NULL COMMENT 'Huella del contenido, para detectar duplicados exactos y cambios entre períodos.',
  `nombre_del_dispositvo` varchar(120) NOT NULL COMMENT 'A — Nombre del dispositvo',
  `dependencia_institucional` varchar(255) DEFAULT NULL COMMENT 'B — Dependencia institucional',
  `localidad` varchar(120) DEFAULT NULL COMMENT 'C — Localidad',
  `direccion` varchar(255) DEFAULT NULL COMMENT 'D — Dirección',
  `telefono` varchar(50) DEFAULT NULL COMMENT 'E — Teléfono',
  `cuenta_con_proyecto_institucional` varchar(38) DEFAULT NULL COMMENT 'F — Cuenta con Proyecto Institucional (valor de catálogo)',
  `cuenta_con_resolucion_de_creacion` varchar(20) DEFAULT NULL COMMENT 'G — Cuenta con resolución de creación (valor de catálogo)',
  `cuenta_con_normativa_convivencial` varchar(38) DEFAULT NULL COMMENT 'H — Cuenta con Normativa Convivencial (valor de catálogo)',
  `cuenta_con_protocolos_de_articulacion_interministerial_co_5e1a90` varchar(34) DEFAULT NULL COMMENT 'I — Cuenta con protocolos de articulación interministerial. Con qué áreas (valor de catálogo)',
  `cuenta_con_protocolos_de_ingreso` varchar(20) DEFAULT NULL COMMENT 'J — Cuenta con protocolos de ingreso (valor de catálogo)',
  `cuenta_con_protocolo_de_requisa` varchar(20) DEFAULT NULL COMMENT 'K — Cuenta con protocolo de requisa (valor de catálogo)',
  `cuenta_con_protocolo_de_denuncias_por_malos_tratos` varchar(20) DEFAULT NULL COMMENT 'L — Cuenta con protocolo de denuncias por malos tratos (valor de catálogo)',
  `cuenta_con_protocolos_de_actuacion_ante_conflictos_entre_pares` varchar(20) DEFAULT NULL COMMENT 'M — Cuenta con protocolos de actuación ante conflictos entre pares (valor de catálogo)',
  `cuenta_con_protocolo_de_abordaje_del_suicidio` varchar(20) DEFAULT NULL COMMENT 'N — Cuenta con protocolo de abordaje del suicidio (valor de catálogo)',
  `cuenta_con_protocolo_de_sanciones` varchar(20) DEFAULT NULL COMMENT 'O — Cuenta con protocolo de sanciones (valor de catálogo)',
  `capacidad_de_alojamiento_mujeres_plazas_disponibles` int DEFAULT NULL,
  `capacidad_de_alojamiento_varones_plazas_disponibles` int DEFAULT NULL,
  `cantidad_de_agentes_equipo_tecnico_y_profesional_incluye_efd962` bigint DEFAULT NULL COMMENT 'R — Cantidad de agentes: equipo técnico y profesional (incluye cuidadores)',
  `cantidad_agentes_de_salud` bigint DEFAULT NULL COMMENT 'S — Cantidad agentes de salud',
  `cantidad_de_personal_administrativo_limpieza_cocina_y_man_7d034d` bigint DEFAULT NULL COMMENT 'T — Cantidad de personal: administrativo, limpieza, cocina y mantenimiento',
  `cantidad_de_personal_seguridad` bigint DEFAULT NULL COMMENT 'U — Cantidad de personal seguridad',
  `cuenta_con_celdas_secas` varchar(20) DEFAULT NULL COMMENT 'V — Cuenta con celdas secas (valor de catálogo)',
  `cuenta_con_celdas_humedas` varchar(20) DEFAULT NULL COMMENT 'W — Cuenta con celdas humedas (valor de catálogo)',
  `cuenta_con_mobiliario_en_las_celdas` varchar(20) DEFAULT NULL COMMENT 'X — Cuenta con mobiliario en las celdas (valor de catálogo)',
  `cuenta_con_colchones_ignifugos` varchar(20) DEFAULT NULL COMMENT 'Y — Cuenta con colchones ignífugos (valor de catálogo)',
  `jurisdicciones_dentro_de_la_provincia_en_las_que_tiene_al_d231ec` varchar(120) DEFAULT NULL COMMENT 'Z — Jurisdicciones dentro de la provincia en las que tiene alcancce territorial el dispositivo',
  `tiempo_maximo_de_permanencia_dentro_del_dispositivo_en_horas` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c2_disp_penal_v1_cad_fila` (`importacion_id`,`numero_fila`),
  CONSTRAINT `runac_c2_disp_penal_v1_cad_ibfk_1` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3151 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Datos de DISP_PENAL v1, hoja "CAD". Generada desde la Capa 1. Sólo entran filas que superaron las validaciones bloqueantes.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_disp_penal_v1_cad`
--

LOCK TABLES `runac_c2_disp_penal_v1_cad` WRITE;
/*!40000 ALTER TABLE `runac_c2_disp_penal_v1_cad` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_disp_penal_v1_cad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_disp_penal_v1_crc`
--

DROP TABLE IF EXISTS `runac_c2_disp_penal_v1_crc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_disp_penal_v1_crc` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `importacion_id` bigint NOT NULL COMMENT 'Importación a la que pertenece la fila.',
  `numero_fila` int NOT NULL COMMENT 'Número de fila en el Excel, tal como lo ve quien completa la planilla.',
  `estado` enum('VALIDA','CON_ADVERTENCIA','EDITADA') NOT NULL DEFAULT 'VALIDA' COMMENT 'Resultado de la validación de la fila. Las filas con bloqueantes no llegan a incorporarse.',
  `hash_contenido` char(40) DEFAULT NULL COMMENT 'Huella del contenido, para detectar duplicados exactos y cambios entre períodos.',
  `nombre_del_dispositvo` varchar(120) NOT NULL COMMENT 'A — Nombre del dispositvo',
  `dependencia_institucional` varchar(255) DEFAULT NULL COMMENT 'B — Dependencia institucional',
  `localidad` varchar(120) DEFAULT NULL COMMENT 'C — Localidad',
  `direccion` varchar(255) DEFAULT NULL COMMENT 'D — Dirección',
  `telefono` varchar(50) DEFAULT NULL COMMENT 'E — Teléfono',
  `capacidad_de_alojamiento_mujeres_plazas_disponibles` int DEFAULT NULL,
  `capacidad_de_alojamiento_varones_plazas_disponibles` int DEFAULT NULL,
  `cuenta_con_proyecto_institucional` varchar(38) DEFAULT NULL COMMENT 'H — ¿Cuenta con Proyecto Institucional? (valor de catálogo)',
  `cuenta_con_normativa_convivencial` varchar(38) DEFAULT NULL COMMENT 'I — ¿Cuenta con Normativa Convivencial? (valor de catálogo)',
  `cantidad_de_agentes_equipo_tecnico_y_profesional_incluye_efd962` bigint DEFAULT NULL COMMENT 'J — Cantidad de agentes: equipo técnico y profesional (incluye cuidadores)',
  `cantidad_agentes_de_salud` bigint DEFAULT NULL COMMENT 'K — Cantidad agentes de salud',
  `cantidad_de_personal_administrativo_limpieza_cocina_y_man_7d034d` bigint DEFAULT NULL COMMENT 'L — Cantidad de personal: administrativo, limpieza, cocina y mantenimiento',
  `cantidad_de_personal_seguridad` bigint DEFAULT NULL COMMENT 'M — Cantidad de personal seguridad',
  `cuenta_con_protocolos_de_ingreso` varchar(20) DEFAULT NULL COMMENT 'N — Cuenta con protocolos de ingreso (valor de catálogo)',
  `cuenta_con_protocolo_de_requisa` varchar(20) DEFAULT NULL COMMENT 'O — Cuenta con protocolo de requisa (valor de catálogo)',
  `cuenta_con_protocolo_de_denuncias_por_malos_tratos` varchar(20) DEFAULT NULL COMMENT 'P — Cuenta con protocolo de denuncias por malos tratos (valor de catálogo)',
  `cuenta_con_protocolos_de_actuacion_ante_conflictos_entre_pares` varchar(20) DEFAULT NULL COMMENT 'Q — Cuenta con protocolos de actuación ante conflictos entre pares (valor de catálogo)',
  `protocolo_de_abordaje_del_suicidio` varchar(20) DEFAULT NULL COMMENT 'R — Protocolo de abordaje del suicidio (valor de catálogo)',
  `cuenta_con_protocolo_de_sanciones` varchar(20) DEFAULT NULL COMMENT 'S — Cuenta con protocolo de sanciones (valor de catálogo)',
  `cantidad_de_horas_semanales_destinadas_al_contacto_presen_510115` bigint DEFAULT NULL COMMENT 'T — Cantidad de horas semanales destinadas al contacto presencial, afectivo/familiar',
  `cuenta_con_espacios_para_visitas_socioafectivas` varchar(20) DEFAULT NULL COMMENT 'U — Cuenta con espacios para visitas socioafectivas (valor de catálogo)',
  `cumple_con_los_niveles_de_obligatoriedad_de_educacion_primaria` varchar(20) DEFAULT NULL COMMENT 'V — Cumple con los niveles de obligatoriedad de educación primaria (valor de catálogo)',
  `cantidad_de_horas_semanales_dedicadas_a_la_educacion_primaria` bigint DEFAULT NULL COMMENT 'W — Cantidad de horas semanales dedicadas a la educación primaria',
  `cumple_con_los_niveles_de_obligatoriedad_de_educacion_secundaria` varchar(20) DEFAULT NULL COMMENT 'X — Cumple con los niveles de obligatoriedad de educación secundaria (valor de catálogo)',
  `cantidad_de_horas_semanales_dedicadas_a_la_educacion_secundaria` bigint DEFAULT NULL COMMENT 'Y — Cantidad de horas semanales dedicadas a la educación secundaria',
  `tiene_aulas_destinadas_a_la_educacion_obligatoria` varchar(20) DEFAULT NULL COMMENT 'Z — Tiene aulas destinadas a la educación obligatoria (valor de catálogo)',
  `cantidad_de_horas_semanales_dedicadas_a_la_formacion_profesional` bigint DEFAULT NULL COMMENT 'AA — Cantidad de horas semanales dedicadas a la formación profesional',
  `cantidad_de_horas_semanales_dedicadas_a_talleres_deportiv_bedd8e` bigint DEFAULT NULL COMMENT 'AB — Cantidad de horas semanales dedicadas a talleres deportivos y culturales',
  `cuenta_con_espacio_para_talleres` varchar(20) DEFAULT NULL COMMENT 'AC — Cuenta con espacio para talleres (valor de catálogo)',
  `cuenta_con_asesoramiento_tecnico_juridico` varchar(20) DEFAULT NULL COMMENT 'AD — Cuenta con asesoramiento técnico jurídico (valor de catálogo)',
  `cuenta_con_patio_abierto` varchar(20) DEFAULT NULL COMMENT 'AE — Cuenta con patio abierto (valor de catálogo)',
  `cuenta_con_patio_techado` varchar(20) DEFAULT NULL COMMENT 'AF — Cuenta con patio techado (valor de catálogo)',
  `cuenta_con_celdas_secas` varchar(20) DEFAULT NULL COMMENT 'AG — Cuenta con celdas secas (valor de catálogo)',
  `cuenta_con_celdas_humedas` varchar(20) DEFAULT NULL COMMENT 'AH — Cuenta con celdas humedas (valor de catálogo)',
  `cuenta_con_mobiliario_en_las_celdas` varchar(20) DEFAULT NULL COMMENT 'AI — Cuenta con mobiliario en las celdas (valor de catálogo)',
  `cuenta_con_colchones_ignifugos` varchar(20) DEFAULT NULL COMMENT 'AJ — Cuenta con colchones ignífugos (valor de catálogo)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c2_disp_penal_v1_crc_fila` (`importacion_id`,`numero_fila`),
  CONSTRAINT `runac_c2_disp_penal_v1_crc_ibfk_1` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3151 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Datos de DISP_PENAL v1, hoja "CRC". Generada desde la Capa 1. Sólo entran filas que superaron las validaciones bloqueantes.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_disp_penal_v1_crc`
--

LOCK TABLES `runac_c2_disp_penal_v1_crc` WRITE;
/*!40000 ALTER TABLE `runac_c2_disp_penal_v1_crc` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_disp_penal_v1_crc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_disp_penal_v1_crsc`
--

DROP TABLE IF EXISTS `runac_c2_disp_penal_v1_crsc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_disp_penal_v1_crsc` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `importacion_id` bigint NOT NULL COMMENT 'Importación a la que pertenece la fila.',
  `numero_fila` int NOT NULL COMMENT 'Número de fila en el Excel, tal como lo ve quien completa la planilla.',
  `estado` enum('VALIDA','CON_ADVERTENCIA','EDITADA') NOT NULL DEFAULT 'VALIDA' COMMENT 'Resultado de la validación de la fila. Las filas con bloqueantes no llegan a incorporarse.',
  `hash_contenido` char(40) DEFAULT NULL COMMENT 'Huella del contenido, para detectar duplicados exactos y cambios entre períodos.',
  `nombre_del_dispositvo` varchar(120) NOT NULL COMMENT 'A — Nombre del dispositvo',
  `dependencia_institucional` varchar(255) DEFAULT NULL COMMENT 'B — Dependencia institucional',
  `localidad` varchar(120) DEFAULT NULL COMMENT 'C — Localidad',
  `direccion` varchar(255) DEFAULT NULL COMMENT 'D — Dirección',
  `telefono` varchar(50) DEFAULT NULL COMMENT 'E — Teléfono',
  `cuenta_con_proyecto_institucional` varchar(38) DEFAULT NULL COMMENT 'F — Cuenta con Proyecto Institucional (valor de catálogo)',
  `cuenta_con_normativa_convivencial` varchar(38) DEFAULT NULL COMMENT 'G — Cuenta con Normativa Convivencial (valor de catálogo)',
  `cuenta_con_protocolos_de_ingreso` varchar(20) DEFAULT NULL COMMENT 'H — Cuenta con protocolos de ingreso (valor de catálogo)',
  `cuenta_con_protocolo_de_requisa` varchar(20) DEFAULT NULL COMMENT 'I — Cuenta con protocolo de requisa (valor de catálogo)',
  `cuenta_con_protocolo_de_denuncias_por_malos_tratos` varchar(20) DEFAULT NULL COMMENT 'J — Cuenta con protocolo de denuncias por malos tratos (valor de catálogo)',
  `cuenta_con_protocolos_de_actuacion_ante_conflictos_entre_pares` varchar(20) DEFAULT NULL COMMENT 'K — Cuenta con protocolos de actuación ante conflictos entre pares (valor de catálogo)',
  `protocolo_de_abordaje_del_suicidio` varchar(20) DEFAULT NULL COMMENT 'L — Protocolo de abordaje del suicidio (valor de catálogo)',
  `cuenta_con_protocolo_de_sanciones` varchar(20) DEFAULT NULL COMMENT 'M — Cuenta con protocolo de sanciones (valor de catálogo)',
  `capacidad_de_alojamiento_mujeres_plazas_disponibles` int DEFAULT NULL,
  `capacidad_de_alojamiento_varones_plazas_disponibles` int DEFAULT NULL,
  `cantidad_de_agentes_equipo_tecnico_y_profesional_incluye_efd962` bigint DEFAULT NULL COMMENT 'P — Cantidad de agentes: equipo técnico y profesional (incluye cuidadores)',
  `cantidad_agentes_de_salud` bigint DEFAULT NULL COMMENT 'Q — Cantidad agentes de salud',
  `cantidad_de_personal_administrativo_limpieza_cocina_y_man_7d034d` bigint DEFAULT NULL COMMENT 'R — Cantidad de personal: administrativo, limpieza, cocina y mantenimiento',
  `cantidad_de_personal_seguridad` bigint DEFAULT NULL COMMENT 'S — Cantidad de personal seguridad',
  `cantidad_de_horas_semanales_destinadas_al_contacto_presen_510115` bigint DEFAULT NULL COMMENT 'T — Cantidad de horas semanales destinadas al contacto presencial, afectivo/familiar',
  `cuenta_con_espacios_para_visitas_socioafectivas` varchar(20) DEFAULT NULL COMMENT 'U — Cuenta con espacios para visitas socioafectivas (valor de catálogo)',
  `cumple_con_los_niveles_de_obligatoriedad_de_educacion_primaria` varchar(20) DEFAULT NULL COMMENT 'V — Cumple con los niveles de obligatoriedad de educación primaria (valor de catálogo)',
  `cantidad_de_horas_semanales_dedicadas_a_la_educacion_primaria` bigint DEFAULT NULL COMMENT 'W — Cantidad de horas semanales dedicadas a la educación primaria',
  `cumple_con_los_niveles_de_obligatoriedad_de_educacion_secundaria` varchar(20) DEFAULT NULL COMMENT 'X — Cumple con los niveles de obligatoriedad de educación secundaria (valor de catálogo)',
  `cantidad_de_horas_semanales_dedicadas_a_la_educacion_secundaria` bigint DEFAULT NULL COMMENT 'Y — Cantidad de horas semanales dedicadas a la educación secundaria',
  `tiene_aulas_destinadas_a_la_educacion_obligatoria` varchar(20) DEFAULT NULL COMMENT 'Z — Tiene aulas destinadas a la educación obligatoria (valor de catálogo)',
  `cantidad_de_horas_semanales_dedicadas_a_la_formacion_profesional` bigint DEFAULT NULL COMMENT 'AA — Cantidad de horas semanales dedicadas a la formación profesional',
  `cantidad_de_horas_semanales_dedicadas_a_talleres_deportiv_bedd8e` bigint DEFAULT NULL COMMENT 'AB — Cantidad de horas semanales dedicadas a talleres deportivos y culturales',
  `cuenta_con_espacio_para_talleres` varchar(20) DEFAULT NULL COMMENT 'AC — Cuenta con espacio para talleres (valor de catálogo)',
  `cuenta_con_asesoramiento_tecnico_juridico` varchar(20) DEFAULT NULL COMMENT 'AD — Cuenta con asesoramiento técnico jurídico (valor de catálogo)',
  `cuenta_con_patio_abierto` varchar(20) DEFAULT NULL COMMENT 'AE — Cuenta con patio abierto (valor de catálogo)',
  `cuenta_con_patio_techado` varchar(20) DEFAULT NULL COMMENT 'AF — Cuenta con patio techado (valor de catálogo)',
  `cuenta_con_celdas_secas` varchar(20) DEFAULT NULL COMMENT 'AG — Cuenta con celdas secas (valor de catálogo)',
  `cuenta_con_celdas_humedas` varchar(20) DEFAULT NULL COMMENT 'AH — Cuenta con celdas humedas (valor de catálogo)',
  `cuenta_con_mobiliario_en_las_celdas` varchar(20) DEFAULT NULL COMMENT 'AI — Cuenta con mobiliario en las celdas (valor de catálogo)',
  `cuenta_con_colchones_ignifugos` varchar(20) DEFAULT NULL COMMENT 'AJ — Cuenta con colchones ignífugos (valor de catálogo)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c2_disp_penal_v1_crsc_fila` (`importacion_id`,`numero_fila`),
  CONSTRAINT `runac_c2_disp_penal_v1_crsc_ibfk_1` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3151 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Datos de DISP_PENAL v1, hoja "CRSC". Generada desde la Capa 1. Sólo entran filas que superaron las validaciones bloqueantes.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_disp_penal_v1_crsc`
--

LOCK TABLES `runac_c2_disp_penal_v1_crsc` WRITE;
/*!40000 ALTER TABLE `runac_c2_disp_penal_v1_crsc` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_disp_penal_v1_crsc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_disp_penal_v1_guardiacomis`
--

DROP TABLE IF EXISTS `runac_c2_disp_penal_v1_guardiacomis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_disp_penal_v1_guardiacomis` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `importacion_id` bigint NOT NULL COMMENT 'Importación a la que pertenece la fila.',
  `numero_fila` int NOT NULL COMMENT 'Número de fila en el Excel, tal como lo ve quien completa la planilla.',
  `estado` enum('VALIDA','CON_ADVERTENCIA','EDITADA') NOT NULL DEFAULT 'VALIDA' COMMENT 'Resultado de la validación de la fila. Las filas con bloqueantes no llegan a incorporarse.',
  `hash_contenido` char(40) DEFAULT NULL COMMENT 'Huella del contenido, para detectar duplicados exactos y cambios entre períodos.',
  `nombre_del_dispositvo` varchar(120) NOT NULL COMMENT 'A — Nombre del dispositvo',
  `dependencia_institucional` varchar(255) DEFAULT NULL COMMENT 'B — Dependencia institucional',
  `telefono` varchar(50) DEFAULT NULL COMMENT 'C — Teléfono',
  `cuenta_con_resolucion_de_creacion` varchar(20) DEFAULT NULL COMMENT 'D — Cuenta con resolución de creación (valor de catálogo)',
  `cuenta_con_protocolos_de_articulacion_interministerial_co_5e1a90` varchar(34) DEFAULT NULL COMMENT 'E — Cuenta con protocolos de articulación interministerial. Con qué áreas (valor de catálogo)',
  `cuenta_con_protocolo_de_denuncias_por_malos_tratos` varchar(20) DEFAULT NULL COMMENT 'F — Cuenta con protocolo de denuncias por malos tratos (valor de catálogo)',
  `cantidad_de_agentes_equipo_tecnico_y_profesional_incluye_efd962` bigint DEFAULT NULL COMMENT 'G — Cantidad de agentes: equipo técnico y profesional (incluye cuidadores)',
  `jurisdicciones_dentro_de_la_provincia_en_las_que_tiene_al_d231ec` varchar(120) DEFAULT NULL COMMENT 'H — Jurisdicciones dentro de la provincia en las que tiene alcancce territorial el dispositivo',
  `tiempo_maximo_de_permanencia_dentro_del_dispositivo_en_horas` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c2_disp_penal_v1_guardiacomis_fila` (`importacion_id`,`numero_fila`),
  CONSTRAINT `runac_c2_disp_penal_v1_guardiacomis_ibfk_1` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3151 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Datos de DISP_PENAL v1, hoja "Guardia Comisaría". Generada desde la Capa 1. Sólo entran filas que superaron las validaciones bloqueantes.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_disp_penal_v1_guardiacomis`
--

LOCK TABLES `runac_c2_disp_penal_v1_guardiacomis` WRITE;
/*!40000 ALTER TABLE `runac_c2_disp_penal_v1_guardiacomis` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_disp_penal_v1_guardiacomis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_disp_penal_v1_mpt`
--

DROP TABLE IF EXISTS `runac_c2_disp_penal_v1_mpt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_disp_penal_v1_mpt` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `importacion_id` bigint NOT NULL COMMENT 'Importación a la que pertenece la fila.',
  `numero_fila` int NOT NULL COMMENT 'Número de fila en el Excel, tal como lo ve quien completa la planilla.',
  `estado` enum('VALIDA','CON_ADVERTENCIA','EDITADA') NOT NULL DEFAULT 'VALIDA' COMMENT 'Resultado de la validación de la fila. Las filas con bloqueantes no llegan a incorporarse.',
  `hash_contenido` char(40) DEFAULT NULL COMMENT 'Huella del contenido, para detectar duplicados exactos y cambios entre períodos.',
  `nombre_del_dispositvo` varchar(120) NOT NULL COMMENT 'A — Nombre del dispositvo',
  `dependencia_institucional` varchar(255) DEFAULT NULL COMMENT 'B — Dependencia institucional',
  `localidad` varchar(120) DEFAULT NULL COMMENT 'C — Localidad',
  `direccion` varchar(255) DEFAULT NULL COMMENT 'D — Dirección',
  `telefono` varchar(50) DEFAULT NULL COMMENT 'E — Teléfono',
  `cuenta_con_proyecto_institucional` varchar(38) DEFAULT NULL COMMENT 'F — Cuenta con Proyecto Institucional (valor de catálogo)',
  `cuenta_con_espacio_de_grupalidad` varchar(20) DEFAULT NULL COMMENT 'G — Cuenta con espacio de grupalidad (valor de catálogo)',
  `cantidad_de_agentes_equipo_tecnico_y_profesional_incluye_efd962` bigint DEFAULT NULL COMMENT 'H — Cantidad de agentes: equipo técnico y profesional (incluye cuidadores)',
  `cuenta_con_asesoramiento_tecnico_juridico` varchar(20) DEFAULT NULL COMMENT 'I — Cuenta con asesoramiento técnico jurídico (valor de catálogo)',
  `jurisdicciones_dentro_de_la_provincia_en_las_que_el_dispo_a48f6b` varchar(120) DEFAULT NULL COMMENT 'J — Jurisdicciones dentro de la provincia en las que el dispositivo tiene alcance',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c2_disp_penal_v1_mpt_fila` (`importacion_id`,`numero_fila`),
  CONSTRAINT `runac_c2_disp_penal_v1_mpt_ibfk_1` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3151 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Datos de DISP_PENAL v1, hoja "MPT". Generada desde la Capa 1. Sólo entran filas que superaron las validaciones bloqueantes.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_disp_penal_v1_mpt`
--

LOCK TABLES `runac_c2_disp_penal_v1_mpt` WRITE;
/*!40000 ALTER TABLE `runac_c2_disp_penal_v1_mpt` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_disp_penal_v1_mpt` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_disp_scp_v1`
--

DROP TABLE IF EXISTS `runac_c2_disp_scp_v1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_disp_scp_v1` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `importacion_id` bigint NOT NULL COMMENT 'Importación a la que pertenece la fila.',
  `numero_fila` int NOT NULL COMMENT 'Número de fila en el Excel, tal como lo ve quien completa la planilla.',
  `estado` enum('VALIDA','CON_ADVERTENCIA','EDITADA') NOT NULL DEFAULT 'VALIDA' COMMENT 'Resultado de la validación de la fila. Las filas con bloqueantes no llegan a incorporarse.',
  `hash_contenido` char(40) DEFAULT NULL COMMENT 'Huella del contenido, para detectar duplicados exactos y cambios entre períodos.',
  `nombre_del_dispositvo` varchar(120) NOT NULL COMMENT 'A — Nombre del dispositvo',
  `dependencia_institucional` varchar(255) DEFAULT NULL COMMENT 'B — Dependencia institucional',
  `tipo_de_gestion` varchar(20) DEFAULT NULL COMMENT 'C — Tipo de gestión (valor de catálogo)',
  `tiene_convenio_con_el_opn_solo_para_los_de_gestion_no_gub_ce242a` varchar(20) DEFAULT NULL COMMENT 'D — ¿Tiene convenio con el OPN? (Solo para los de gestión no gubernamental y gestión mixta) (valor de catálogo)',
  `localidad` varchar(120) DEFAULT NULL COMMENT 'E — Localidad',
  `direccion` varchar(255) DEFAULT NULL COMMENT 'F — Dirección',
  `codigo_postal` varchar(10) DEFAULT NULL COMMENT 'G — Código postal',
  `telefono` varchar(50) DEFAULT NULL COMMENT 'H — Teléfono',
  `el_dispositivo_registra_las_intervenciones_en_el_sistema_c4fc90` varchar(20) DEFAULT NULL COMMENT 'I — El dispositivo, ¿registra las intervenciones en el Sistema Nominal digital del OPN provincial? (valor de catálogo)',
  `proyecto_institucional` varchar(31) DEFAULT NULL COMMENT 'J — ... Proyecto institucional? (valor de catálogo)',
  `reglamento_de_convivencia` varchar(31) DEFAULT NULL COMMENT 'K — …reglamento de convivencia? (valor de catálogo)',
  `habilitacion_municipal` varchar(20) DEFAULT NULL COMMENT 'L — ... habilitación municipal? (valor de catálogo)',
  `con_rampas_o_condiciones_para_el_acceso_y_circulacion_de_ecfaaf` varchar(38) DEFAULT NULL COMMENT 'M — ... con rampas o condiciones para el acceso y circulación de personas con discapacidad (valor de catálogo)',
  `tablets_o_computadoras_para_los_nya_alojados_en_el_dispositivo` varchar(48) DEFAULT NULL COMMENT 'N — ... tablets o computadoras para los NyA alojados en el dispositivo (valor de catálogo)',
  `wifi_en_el_dispositivo` varchar(20) DEFAULT NULL COMMENT 'O — ... WIFI en el dispositivo (valor de catálogo)',
  `para_el_ingreso_del_nya_al_dispositivo` varchar(20) DEFAULT NULL COMMENT 'P — ... para el ingreso del NyA al dispositivo (valor de catálogo)',
  `para_el_abordaje_de_conflictos_o_violencia_entre_nya` varchar(20) DEFAULT NULL COMMENT 'Q — …para el abordaje de conflictos o violencia entre NyA (valor de catálogo)',
  `para_el_abordaje_de_crisis_y_urgencias_en_salud_mental` varchar(20) DEFAULT NULL COMMENT 'R — ... para el abordaje de crisis y urgencias en salud mental (valor de catálogo)',
  `capacidad_de_alojamiento_plazas` int DEFAULT NULL,
  `cantidad_de_nya_alojados_en_el_dispositivo_al_momento_de_4d0f88` bigint DEFAULT NULL COMMENT 'T — Cantidad de NyA alojados en el dispositivo (al momento de la carga de la información)',
  `cantidad_de_nya_que_es_posible_alojar_por_dormitorio` varchar(26) DEFAULT NULL COMMENT 'U — Cantidad de NyA que es posible alojar por dormitorio (valor de catálogo)',
  `genero_admitido` varchar(39) DEFAULT NULL COMMENT 'V — Género admitido (valor de catálogo)',
  `grupos_de_hermanos` varchar(20) DEFAULT NULL COMMENT 'W — grupos de hermanos? (valor de catálogo)',
  `nya_dolescentes_con_discapacidad` varchar(20) DEFAULT NULL COMMENT 'X — NyA dolescentes con discapacidad (valor de catálogo)',
  `nya_con_padecimiento_de_salud_mental` varchar(20) DEFAULT NULL COMMENT 'Y — NyA con padecimiento de salud mental (valor de catálogo)',
  `nya_con_uso_o_abuso_de_sustancias` varchar(20) DEFAULT NULL COMMENT 'Z — NyA con uso o abuso de sustancias (valor de catálogo)',
  `adolescentes_con_hijos` varchar(20) DEFAULT NULL COMMENT 'AA — Adolescentes con hijos (valor de catálogo)',
  `aloja_ninos_de_0_a_5_anos` varchar(20) DEFAULT NULL COMMENT 'AB — Aloja niños de 0 a 5 años (valor de catálogo)',
  `aloja_ninos_de_6_a_12_anos` varchar(20) DEFAULT NULL COMMENT 'AC — Aloja niños de 6 a 12 años (valor de catálogo)',
  `aloja_poblacion_de_13_a_17_anos` varchar(20) DEFAULT NULL COMMENT 'AD — Aloja población de 13 a 17 años (valor de catálogo)',
  `aloja_poblacion_de_18_anos_y_mas` varchar(20) DEFAULT NULL COMMENT 'AE — Aloja población de 18 años y más (valor de catálogo)',
  `que_conforman_el_equipo_tecnico` varchar(28) DEFAULT NULL COMMENT 'AF — … que conforman el equipo técnico (valor de catálogo)',
  `destinadas_al_cuidado_del_nya` varchar(32) DEFAULT NULL COMMENT 'AG — ... destinadas al cuidado del NyA (valor de catálogo)',
  `destinadas_a_tareas_de_apoyo_administrativo_mantenimiento_1e125d` varchar(31) DEFAULT NULL COMMENT 'AH — ... destinadas a tareas de apoyo (administrativo, mantenimiento, cocina, etc) (valor de catálogo)',
  `del_equipo_de_conduccion` varchar(36) DEFAULT NULL COMMENT 'AI — … del equipo de conducción (valor de catálogo)',
  `recibio_capacitacion_en_promocion_de_cuidados` varchar(20) DEFAULT NULL COMMENT 'AJ — Recibió capacitación en PROMOCION DE CUIDADOS (valor de catálogo)',
  `recibio_capacitacion_en_alimentacion_saludable` varchar(20) DEFAULT NULL COMMENT 'AK — Recibió capacitación en ALIMENTACION SALUDABLE (valor de catálogo)',
  `recibio_capacitacion_en_reanimacion_cardiopulmonar` varchar(20) DEFAULT NULL COMMENT 'AL — Recibió capacitación en REANIMACION CARDIOPULMONAR (valor de catálogo)',
  `recibio_capacitacion_en_primeros_auxilios` varchar(20) DEFAULT NULL COMMENT 'AM — Recibió capacitación en PRIMEROS AUXILIOS (valor de catálogo)',
  `recibio_capacitacion_en_abuso_sexual_infantil_juvenil` varchar(20) DEFAULT NULL COMMENT 'AN — Recibió capacitación en ABUSO SEXUAL INFANTIL /JUVENIL (valor de catálogo)',
  `recibio_capacitacion_en_paradigma_de_proteccion_integral` varchar(20) DEFAULT NULL COMMENT 'AO — Recibió capacitación en PARADIGMA DE PROTECCION INTEGRAL (valor de catálogo)',
  `recibio_capacitacion_en_autonomia_progresiva` varchar(20) DEFAULT NULL COMMENT 'AP — Recibió capacitación en AUTONOMIA PROGRESIVA (valor de catálogo)',
  `recibio_capacitacion_en_abordaje_en_salud_mental` varchar(20) DEFAULT NULL COMMENT 'AQ — Recibió capacitación en ABORDAJE EN SALUD MENTAL (valor de catálogo)',
  `recibio_capacitacion_en_consumos_problematicos` varchar(20) DEFAULT NULL COMMENT 'AR — Recibió capacitación en CONSUMOS PROBLEMATICOS (valor de catálogo)',
  `recibio_capacitacion_en_cultura_digital` varchar(20) DEFAULT NULL COMMENT 'AS — Recibió capacitación en CULTURA DIGITAL (valor de catálogo)',
  `recibio_capacitacion_en_discapacidad` varchar(20) DEFAULT NULL COMMENT 'AT — Recibió capacitación en DISCAPACIDAD (valor de catálogo)',
  `recibio_capacitacion_en_administracion_financiera` varchar(20) DEFAULT NULL COMMENT 'AU — Recibió capacitación en ADMINISTRACION FINANCIERA (valor de catálogo)',
  `recibio_capacitacion_en_otras_tematicas` varchar(20) DEFAULT NULL COMMENT 'AV — Recibió capacitación en OTRAS TEMÁTICAS (valor de catálogo)',
  `otras_tematicas_especifique` varchar(255) DEFAULT NULL COMMENT 'AW — Otras temáticas. Especifique',
  `el_dipositivo_participa_en_la_formulacion_del_proyecto_de_f26a26` varchar(34) DEFAULT NULL COMMENT 'AX — El dipositivo participa en la formulación del proyecto de restitución de derechos (valor de catálogo)',
  `participa_el_nya_en_el_proyecto_de_restitucion_de_derechos_per` varchar(32) DEFAULT NULL COMMENT 'AY — Participa el NyA en el proyecto de restitución de derechos (PER) (valor de catálogo)',
  `existe_articulacion_entre_el_per_y_el_plan_de_estadia` varchar(32) DEFAULT NULL COMMENT 'AZ — Existe articulación entre el PER y el plan de estadía? (valor de catálogo)',
  `promueve_el_contacto_con_la_familia_y_o_referentes_afecti_f4339a` varchar(20) DEFAULT NULL COMMENT 'BA — ¿Promueve el contacto con la familia y/o referentes afectivos a través de redes, mails, cartas? (valor de catálogo)',
  `promueve_el_contacto_con_la_familia_y_o_referentes_afecti_c9002f` varchar(20) DEFAULT NULL COMMENT 'BB — ¿Promueve el contacto con la familia y/o referentes afectivos a través de encuentros fuera del dispositivo? (valor de catálogo)',
  `promueve_el_contacto_con_la_familia_y_o_referentes_afecti_e14bff` varchar(20) DEFAULT NULL COMMENT 'BC — ¿Promueve el contacto con la familia y/o referentes afectivos a través de visitas presenciales? (valor de catálogo)',
  `promueve_el_contacto_con_la_familia_y_o_referentes_afecti_5370e5` varchar(20) DEFAULT NULL COMMENT 'BD — ¿Promueve el contacto con la familia y/o referentes afectivos a través de llamadas y videollamadas? (valor de catálogo)',
  `con_que_frecuencia_los_nya_alojados_en_el_dispositivo_rea_254ee2` varchar(26) DEFAULT NULL COMMENT 'BE — ¿Con que frecuencia los NyA alojados en el dispositivo realizan actividades fuera del dispositivo? (valor de catálogo)',
  `con_que_frecuencia_los_nya_alojados_en_el_dispositivo_rea_0a47aa` varchar(26) DEFAULT NULL COMMENT 'BF — ¿Con que frecuencia los NyA alojados en el dispositivo realizan Actividades ARTISTICAS? (valor de catálogo)',
  `con_que_frecuencia_los_nya_alojados_en_el_dispositivo_rea_0516fc` varchar(26) DEFAULT NULL COMMENT 'BG — ¿Con que frecuencia los NyA alojados en el dispositivo realizan Actividades DEPORTIVAS? (valor de catálogo)',
  `con_que_frecuencia_los_nya_alojados_en_el_dispositivo_rea_0010d4` varchar(26) DEFAULT NULL COMMENT 'BH — ¿Con que frecuencia los NyA alojados en el dispositivo realizan Actividades RECREATIVAS? (valor de catálogo)',
  `con_que_frecuencia_los_nya_alojados_en_el_dispositivo_rea_b4d710` varchar(26) DEFAULT NULL COMMENT 'BI — ¿Con que frecuencia los NyA alojados en el dispositivo realizan OTRAS Actividades? (valor de catálogo)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c2_disp_scp_v1_fila` (`importacion_id`,`numero_fila`),
  CONSTRAINT `runac_c2_disp_scp_v1_ibfk_1` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2521 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Datos de DISP_SCP v1, hoja "M Residencial". Generada desde la Capa 1. Sólo entran filas que superaron las validaciones bloqueantes.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_disp_scp_v1`
--

LOCK TABLES `runac_c2_disp_scp_v1` WRITE;
/*!40000 ALTER TABLE `runac_c2_disp_scp_v1` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_disp_scp_v1` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_errores_de_importacion`
--

DROP TABLE IF EXISTS `runac_c2_errores_de_importacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_errores_de_importacion` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `importacion_id` bigint NOT NULL COMMENT 'Intento en el que se detectó.',
  `tipo` enum('HOJA_FALTANTE','HOJA_NOMBRE_DISTINTO','COLUMNA_FALTANTE','COLUMNA_NO_ESPERADA','COLUMNA_FUERA_DE_ORDEN','FILA_VACIA_INTERCALADA','ARCHIVO_ILEGIBLE','ERROR_TECNICO') NOT NULL COMMENT 'Los cinco primeros son discrepancias con la estructura esperada. FILA_VACIA_INTERCALADA es una fila en blanco en el medio de los datos, que el requerimiento pide corregir antes de importar. ARCHIVO_ILEGIBLE y ERROR_TECNICO no dependen del contenido: formato no reconocido, archivo dañado, interrupción del proceso o pérdida de conexión.',
  `hoja` varchar(255) DEFAULT NULL COMMENT 'Hoja donde se detectó, cuando corresponde.',
  `numero_fila` int DEFAULT NULL COMMENT 'Fila del Excel, cuando el problema tiene una ubicación puntual.',
  `esperado` varchar(255) DEFAULT NULL COMMENT 'Nombre de hoja, título de columna o posición que se esperaba encontrar.',
  `encontrado` varchar(255) DEFAULT NULL COMMENT 'Qué se encontró en su lugar.',
  `descripcion` text NOT NULL COMMENT 'Mensaje en lenguaje claro para el operador.',
  `detalle_tecnico` text COMMENT 'Traza del error, para soporte. No se muestra al usuario.',
  PRIMARY KEY (`id`),
  KEY `runac_c2_errores_importacion` (`importacion_id`,`tipo`),
  CONSTRAINT `runac_c2_errores_de_importacion_ibfk_1` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=377 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Motivos por los que un archivo no pudo importarse. Un archivo equivocado suele fallar por varias razones a la vez: se informan todas juntas para que el operador corrija una sola vez.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_errores_de_importacion`
--

LOCK TABLES `runac_c2_errores_de_importacion` WRITE;
/*!40000 ALTER TABLE `runac_c2_errores_de_importacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_errores_de_importacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_historial_cambios`
--

DROP TABLE IF EXISTS `runac_c2_historial_cambios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_historial_cambios` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `importacion_id` bigint NOT NULL COMMENT 'Importación cuyos datos se editaron.',
  `numero_fila` int NOT NULL COMMENT 'Fila editada.',
  `campo_id` bigint NOT NULL COMMENT 'Campo editado.',
  `identificador_registro` varchar(100) DEFAULT NULL COMMENT 'Identificador provincial del registro editado.',
  `observacion_id` bigint DEFAULT NULL COMMENT 'Observación que motivó el cambio, cuando corresponde.',
  `valor_anterior` text COMMENT 'Contenido previo al cambio.',
  `valor_nuevo` text COMMENT 'Contenido posterior al cambio.',
  `motivo` text COMMENT 'Justificación del cambio.',
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento del cambio.',
  `usuario` varchar(150) NOT NULL COMMENT 'Usuario que realizó el cambio.',
  PRIMARY KEY (`id`),
  KEY `runac_c2_historial_ubicacion` (`importacion_id`,`numero_fila`),
  KEY `campo_id` (`campo_id`),
  KEY `observacion_id` (`observacion_id`),
  CONSTRAINT `runac_c2_historial_cambios_ibfk_1` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`),
  CONSTRAINT `runac_c2_historial_cambios_ibfk_2` FOREIGN KEY (`campo_id`) REFERENCES `runac_c1_campo` (`id`),
  CONSTRAINT `runac_c2_historial_cambios_ibfk_3` FOREIGN KEY (`observacion_id`) REFERENCES `runac_c2_observacion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=194 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Correcciones sobre los datos importados, con usuario, fecha, valor anterior y valor nuevo. Responde a la pregunta: el Excel decía X y el operador puso Y. No confundir con el historial de la Capa 3, que registra la evolución del dato consolidado entre períodos.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_historial_cambios`
--

LOCK TABLES `runac_c2_historial_cambios` WRITE;
/*!40000 ALTER TABLE `runac_c2_historial_cambios` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_historial_cambios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_importacion`
--

DROP TABLE IF EXISTS `runac_c2_importacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_importacion` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `presentacion_id` bigint NOT NULL COMMENT 'Presentación a la que pertenece este intento.',
  `archivo_id` bigint NOT NULL COMMENT 'Archivo que el operador declaró estar cargando. El operador elige el archivo: el nombre del fichero no lo determina.',
  `archivo_version_id` bigint DEFAULT NULL COMMENT 'Versión contra la que se validó. Queda vacío cuando el archivo no se pudo identificar.',
  `nombre_archivo` varchar(255) NOT NULL COMMENT 'Nombre del archivo tal como lo subió el usuario.',
  `sha1` char(40) DEFAULT NULL COMMENT 'Huella del archivo subido. Permite detectar que se volvió a subir el mismo.',
  `bytes` bigint DEFAULT NULL COMMENT 'Tamaño del archivo.',
  `ruta_archivo` varchar(500) DEFAULT NULL COMMENT 'Ubicación del archivo recibido, tal como llegó. Es lo que permite devolver al operador su propio Excel con las celdas marcadas, y el respaldo documental de lo presentado.',
  `estado` enum('VALIDA','ANULADA','FALLIDA') NOT NULL COMMENT 'VALIDA: admitida e incorporada. ANULADA: reemplazada por una importación posterior del mismo archivo. FALLIDA: rechazada en el control de admisión o interrumpida por un error técnico. Dado que la importación es restrictiva, un archivo con bloqueantes no genera una importación válida.',
  `filas_leidas` int NOT NULL DEFAULT '0' COMMENT 'Filas de datos leídas del archivo.',
  `filas_incorporadas` int NOT NULL DEFAULT '0' COMMENT 'Filas efectivamente incorporadas.',
  `bloqueantes` int NOT NULL DEFAULT '0' COMMENT 'Cantidad de reglas incumplidas con severidad bloqueante.',
  `advertencias` int NOT NULL DEFAULT '0' COMMENT 'Cantidad de reglas incumplidas con severidad advertencia.',
  `iniciada_el` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento en que se recibió el archivo.',
  `terminada_el` datetime DEFAULT NULL COMMENT 'Momento en que terminó el procesamiento.',
  `duracion_ms` int DEFAULT NULL COMMENT 'Duración del procesamiento, en milisegundos.',
  `usuario` varchar(150) DEFAULT NULL COMMENT 'Usuario que subió el archivo.',
  `anulada_por` bigint DEFAULT NULL COMMENT 'Importación posterior que dejó sin efecto a esta. Conserva el historial de intentos.',
  PRIMARY KEY (`id`),
  KEY `runac_c2_importacion_presentacion` (`presentacion_id`,`archivo_id`,`estado`),
  KEY `archivo_id` (`archivo_id`),
  KEY `archivo_version_id` (`archivo_version_id`),
  KEY `anulada_por` (`anulada_por`),
  CONSTRAINT `runac_c2_importacion_ibfk_1` FOREIGN KEY (`presentacion_id`) REFERENCES `runac_c2_presentacion` (`id`),
  CONSTRAINT `runac_c2_importacion_ibfk_2` FOREIGN KEY (`archivo_id`) REFERENCES `runac_c1_archivo` (`id`),
  CONSTRAINT `runac_c2_importacion_ibfk_3` FOREIGN KEY (`archivo_version_id`) REFERENCES `runac_c1_archivo_version` (`id`),
  CONSTRAINT `runac_c2_importacion_ibfk_4` FOREIGN KEY (`anulada_por`) REFERENCES `runac_c2_importacion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=491 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Cada intento de importación de un archivo, incluidos los que fallaron. Nunca se borra: es la trazabilidad. Permite distinguir a quien no cargó de quien intentó cargar y no pudo.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_importacion`
--

LOCK TABLES `runac_c2_importacion` WRITE;
/*!40000 ALTER TABLE `runac_c2_importacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_importacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_jurisdiccion`
--

DROP TABLE IF EXISTS `runac_c2_jurisdiccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_jurisdiccion` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `codigo` varchar(20) NOT NULL COMMENT 'Código estable de la jurisdicción.',
  `nombre` varchar(120) NOT NULL COMMENT 'Denominación de la jurisdicción.',
  `modalidad` enum('PRESENTACION_PERIODICA','GESTION_CONTINUA') NOT NULL DEFAULT 'PRESENTACION_PERIODICA' COMMENT 'PRESENTACION_PERIODICA: aporta archivos en cada corte, y una nueva importación reemplaza a la anterior. GESTION_CONTINUA: registra novedades dentro del sistema, y la importación incorpora sin descartar lo existente.',
  `activa` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Baja lógica.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Unidad que presenta. Es una entidad y no un texto, para que el mismo mecanismo sirva a provincias, municipios u organismos.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_jurisdiccion`
--

LOCK TABLES `runac_c2_jurisdiccion` WRITE;
/*!40000 ALTER TABLE `runac_c2_jurisdiccion` DISABLE KEYS */;
INSERT INTO `runac_c2_jurisdiccion` VALUES (1,'CHUBUT','Chubut','PRESENTACION_PERIODICA',1),(2,'SALTA','Salta','PRESENTACION_PERIODICA',1),(3,'CHACO','Chaco','PRESENTACION_PERIODICA',1),(4,'FORMOSA','Formosa','PRESENTACION_PERIODICA',1),(5,'CABA','CABA','PRESENTACION_PERIODICA',1),(6,'BUENOS AIRES','Buenos Aires','PRESENTACION_PERIODICA',1),(7,'CATAMARCA','Catamarca','PRESENTACION_PERIODICA',1),(8,'CÓRDOBA','Córdoba','PRESENTACION_PERIODICA',1);
/*!40000 ALTER TABLE `runac_c2_jurisdiccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_legajo_nya_v1_nya`
--

DROP TABLE IF EXISTS `runac_c2_legajo_nya_v1_nya`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_legajo_nya_v1_nya` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `importacion_id` bigint NOT NULL COMMENT 'Importación a la que pertenece la fila.',
  `numero_fila` int NOT NULL COMMENT 'Número de fila en el Excel, tal como lo ve quien completa la planilla.',
  `estado` enum('VALIDA','CON_ADVERTENCIA','EDITADA') NOT NULL DEFAULT 'VALIDA' COMMENT 'Resultado de la validación de la fila. Las filas con bloqueantes no llegan a incorporarse.',
  `hash_contenido` char(40) DEFAULT NULL COMMENT 'Huella del contenido, para detectar duplicados exactos y cambios entre períodos.',
  `apellido_s` varchar(120) NOT NULL COMMENT 'A — Apellido/s',
  `nombre_s` varchar(120) NOT NULL COMMENT 'B — Nombre/s',
  `tipo_de_documento_de_identidad` varchar(26) DEFAULT NULL COMMENT 'C — Tipo de documento de identidad (valor de catálogo)',
  `n_dni` varchar(15) NOT NULL,
  `n_de_cuil` varchar(13) NOT NULL COMMENT 'E — Nº de CUIL',
  `otro_nuero_de_documentacion_de_identidad_si_no_cuenta_con_dni` varchar(15) NOT NULL COMMENT 'F — Otro núero de documentación de identidad (si no cuenta con DNI)',
  `genero` varchar(20) DEFAULT NULL COMMENT 'G — Género (valor de catálogo)',
  `pais_de_nacimiento` varchar(20) DEFAULT NULL COMMENT 'H — País de nacimiento (valor de catálogo)',
  `fecha_de_nacimiento` date NOT NULL COMMENT 'I — Fecha de nacimiento',
  `domicilio_actual` varchar(255) DEFAULT NULL COMMENT 'J — Domicilio actual',
  `provincia` varchar(120) DEFAULT NULL COMMENT 'K — Provincia',
  `departamento` date DEFAULT NULL COMMENT 'L — Departamento',
  `localidad` varchar(120) DEFAULT NULL COMMENT 'M — Localidad',
  `pertenece_a_pueblo_originario_o_se_identifica_con_algun_p_003571` varchar(20) DEFAULT NULL COMMENT 'N — ¿Pertenece a pueblo originario? (o se identifica con algún pueblo originario?) (valor de catálogo)',
  `pueblo_originario_especificar` text COMMENT 'O — Pueblo originario (especificar)',
  `presenta_algun_tipo_de_discapacidad` varchar(20) DEFAULT NULL COMMENT 'P — ¿Presenta algún tipo de discapacidad? (valor de catálogo)',
  `posee_cud` varchar(20) DEFAULT NULL COMMENT 'Q — ¿Posee CUD? (valor de catálogo)',
  `cobertura_salud` varchar(20) DEFAULT NULL COMMENT 'R — Cobertura salud (valor de catálogo)',
  `tiene_hijos_as` varchar(20) DEFAULT NULL COMMENT 'S — ¿Tiene hijos/as? (valor de catálogo)',
  `fecha_de_actualizacion` date DEFAULT NULL COMMENT 'T — Fecha de actualización',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c2_legajo_nya_v1_nya_fila` (`importacion_id`,`numero_fila`),
  CONSTRAINT `runac_c2_legajo_nya_v1_nya_ibfk_1` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Datos de LEGAJO_NYA v1, hoja "NyA". Generada desde la Capa 1. Sólo entran filas que superaron las validaciones bloqueantes.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_legajo_nya_v1_nya`
--

LOCK TABLES `runac_c2_legajo_nya_v1_nya` WRITE;
/*!40000 ALTER TABLE `runac_c2_legajo_nya_v1_nya` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_legajo_nya_v1_nya` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_legajo_nya_v1_prov_dto_loc`
--

DROP TABLE IF EXISTS `runac_c2_legajo_nya_v1_prov_dto_loc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_legajo_nya_v1_prov_dto_loc` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `importacion_id` bigint NOT NULL COMMENT 'Importación a la que pertenece la fila.',
  `numero_fila` int NOT NULL COMMENT 'Número de fila en el Excel, tal como lo ve quien completa la planilla.',
  `estado` enum('VALIDA','CON_ADVERTENCIA','EDITADA') NOT NULL DEFAULT 'VALIDA' COMMENT 'Resultado de la validación de la fila. Las filas con bloqueantes no llegan a incorporarse.',
  `hash_contenido` char(40) DEFAULT NULL COMMENT 'Huella del contenido, para detectar duplicados exactos y cambios entre períodos.',
  `provincia` varchar(120) DEFAULT NULL COMMENT 'A — PROVINCIA',
  `depto` varchar(255) DEFAULT NULL COMMENT 'B — DEPTO',
  `localidad` varchar(120) DEFAULT NULL COMMENT 'C — LOCALIDAD',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c2_legajo_nya_v1_prov_dto_loc_fila` (`importacion_id`,`numero_fila`),
  CONSTRAINT `runac_c2_legajo_nya_v1_prov_dto_loc_ibfk_1` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Datos de LEGAJO_NYA v1, hoja "Prov_Dto_Localidad". Generada desde la Capa 1. Sólo entran filas que superaron las validaciones bloqueantes.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_legajo_nya_v1_prov_dto_loc`
--

LOCK TABLES `runac_c2_legajo_nya_v1_prov_dto_loc` WRITE;
/*!40000 ALTER TABLE `runac_c2_legajo_nya_v1_prov_dto_loc` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_legajo_nya_v1_prov_dto_loc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_mpe_v1`
--

DROP TABLE IF EXISTS `runac_c2_mpe_v1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_mpe_v1` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `importacion_id` bigint NOT NULL COMMENT 'Importación a la que pertenece la fila.',
  `numero_fila` int NOT NULL COMMENT 'Número de fila en el Excel, tal como lo ve quien completa la planilla.',
  `estado` enum('VALIDA','CON_ADVERTENCIA','EDITADA') NOT NULL DEFAULT 'VALIDA' COMMENT 'Resultado de la validación de la fila. Las filas con bloqueantes no llegan a incorporarse.',
  `hash_contenido` char(40) DEFAULT NULL COMMENT 'Huella del contenido, para detectar duplicados exactos y cambios entre períodos.',
  `fecha_del_relevamiento` date NOT NULL COMMENT 'A — Fecha del relevamiento',
  `provincia` varchar(20) DEFAULT NULL COMMENT 'B — Provincia (valor de catálogo)',
  `modalidad_de_cuidado` varchar(22) DEFAULT NULL,
  `nombre_de_la_residencia_hogar` varchar(120) DEFAULT NULL,
  `dependencia_institucional` varchar(255) DEFAULT NULL COMMENT 'E — Dependencia institucional',
  `localidad` varchar(120) DEFAULT NULL COMMENT 'F — Localidad',
  `id_del_nino_nina_o_adolescente` varchar(255) DEFAULT NULL COMMENT 'G — ID del Niño, niña o Adolescente',
  `apellido_s` varchar(120) NOT NULL COMMENT 'H — Apellido/s',
  `nombre_s` varchar(120) NOT NULL COMMENT 'I — Nombre/s',
  `situacion_de_documentacion` varchar(255) DEFAULT NULL COMMENT 'J — Situación de documentación',
  `n_dni` varchar(15) DEFAULT NULL,
  `n_de_cuil` varchar(13) NOT NULL COMMENT 'L — Nº de CUIL',
  `genero` varchar(20) DEFAULT NULL COMMENT 'M — Género (valor de catálogo)',
  `pais_de_nacimiento` varchar(44) DEFAULT NULL COMMENT 'N — País de nacimiento (valor de catálogo)',
  `fecha_de_nacimiento` date NOT NULL COMMENT 'O — Fecha de nacimiento',
  `edad` bigint DEFAULT NULL COMMENT 'P — Edad',
  `asiste_a_institucion_educativa` varchar(20) DEFAULT NULL COMMENT 'Q — ¿Asiste a institución educativa? (valor de catálogo)',
  `maximo_nivel_educativo_alcanzado` varchar(255) DEFAULT NULL COMMENT 'R — Máximo nivel educativo alcanzado',
  `enfermedad_cronica` varchar(20) DEFAULT NULL COMMENT 'S — Enfermedad crónica (valor de catálogo)',
  `consumo_problematico_de_sustancias` varchar(20) DEFAULT NULL COMMENT 'T — Consumo problemático de sustancias (valor de catálogo)',
  `presenta_alguna_discapacidad` varchar(20) DEFAULT NULL COMMENT 'U — ¿Presenta alguna discapacidad? (valor de catálogo)',
  `tipo_de_discapacidad` varchar(20) DEFAULT NULL COMMENT 'V — Tipo de discapacidad (valor de catálogo)',
  `posee_cud` varchar(20) DEFAULT NULL COMMENT 'W — ¿Posee CUD? (valor de catálogo)',
  `cobertura_salud` varchar(20) DEFAULT NULL COMMENT 'X — Cobertura salud (valor de catálogo)',
  `pertenece_a_pueblo_originario` varchar(20) DEFAULT NULL COMMENT 'Y — ¿Pertenece a pueblo originario? (valor de catálogo)',
  `pueblo_originario_especificar` text COMMENT 'Z — Pueblo originario (especificar)',
  `tiene_hijos_as` varchar(20) DEFAULT NULL COMMENT 'AA — ¿Tiene hijos/as? (valor de catálogo)',
  `id_familia` bigint DEFAULT NULL COMMENT 'AB — ID familia',
  `familia` varchar(120) DEFAULT NULL,
  `id_familia_ampliada` bigint DEFAULT NULL,
  `familia_ampliada` varchar(120) DEFAULT NULL,
  `fecha_de_inicio_mpe` date DEFAULT NULL COMMENT 'AF — Fecha de inicio MPE',
  `dias_de_permanencia` bigint DEFAULT NULL COMMENT 'AG — Días de permanencia',
  `origen_de_la_demanda` varchar(20) DEFAULT NULL COMMENT 'AH — Origen de la demanda (valor de catálogo)',
  `motivo_de_intervencion` varchar(255) DEFAULT NULL COMMENT 'AI — Motivo de intervención',
  `submotivo_de_intervencion` varchar(255) DEFAULT NULL COMMENT 'AJ — Submotivo de intervención',
  `tipo_de_proyecto_de_restitucion` varchar(20) DEFAULT NULL COMMENT 'AK — Tipo de proyecto de restitución (valor de catálogo)',
  `elevacion_dictamen_mpe_a_juzgado` varchar(20) DEFAULT NULL COMMENT 'AL — Elevación dictamen MPE a juzgado (valor de catálogo)',
  `decreto_judicial_de_adoptabilidad` varchar(20) DEFAULT NULL COMMENT 'AM — Decreto judicial de adoptabilidad (valor de catálogo)',
  `solicitud_inclusion_proy_autonomia` varchar(20) DEFAULT NULL COMMENT 'AN — Solicitud inclusión proy. autonomía (valor de catálogo)',
  `observaciones` text COMMENT 'AO — Observaciones',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c2_mpe_v1_fila` (`importacion_id`,`numero_fila`),
  CONSTRAINT `runac_c2_mpe_v1_ibfk_1` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2011 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Datos de MPE v1, hoja "MPE". Generada desde la Capa 1. Sólo entran filas que superaron las validaciones bloqueantes.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_mpe_v1`
--

LOCK TABLES `runac_c2_mpe_v1` WRITE;
/*!40000 ALTER TABLE `runac_c2_mpe_v1` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_mpe_v1` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_mpe_v2`
--

DROP TABLE IF EXISTS `runac_c2_mpe_v2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_mpe_v2` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `importacion_id` bigint NOT NULL COMMENT 'Importación a la que pertenece la fila.',
  `numero_fila` int NOT NULL COMMENT 'Número de fila en el Excel, tal como lo ve quien completa la planilla.',
  `estado` enum('VALIDA','CON_ADVERTENCIA','EDITADA') NOT NULL DEFAULT 'VALIDA' COMMENT 'Resultado de la validación de la fila. Las filas con bloqueantes no llegan a incorporarse.',
  `hash_contenido` char(40) DEFAULT NULL COMMENT 'Huella del contenido, para detectar duplicados exactos y cambios entre períodos.',
  `id_del_nino_nina_o_adolescente` varchar(255) DEFAULT NULL COMMENT 'A — ID del Niño, niña o Adolescente',
  `apellido_s` varchar(20) NOT NULL COMMENT 'B — Apellido/s (valor de catálogo)',
  `nombre_s` varchar(120) NOT NULL COMMENT 'C — Nombre/s',
  `cuil_o_documento_de_identidad` varchar(13) NOT NULL COMMENT 'D — Cuil o documento de identidad',
  `origen_de_la_demanda` varchar(20) DEFAULT NULL COMMENT 'E — Origen de la demanda (valor de catálogo)',
  `organismo_que_toma_la_mpe` varchar(20) DEFAULT NULL COMMENT 'F — Organismo que toma la MPE (valor de catálogo)',
  `fecha_de_inicio_mpe` date DEFAULT NULL COMMENT 'G — Fecha de inicio MPE',
  `ultima_fecha_de_renovacion` varchar(20) DEFAULT NULL COMMENT 'H — Última fecha de renovación (valor de catálogo)',
  `motivo_de_toma_de_mpe` varchar(255) DEFAULT NULL COMMENT 'I — Motivo de toma de MPE',
  `submotivo_de_toma_de_mpe` varchar(255) DEFAULT NULL COMMENT 'J — Submotivo de toma de MPE',
  `elevacion_dictamen_mpe_a_juzgado` varchar(20) DEFAULT NULL COMMENT 'K — Elevación dictamen MPE a juzgado (valor de catálogo)',
  `control_de_legalidad_por_autoridad_judicial` varchar(20) DEFAULT NULL COMMENT 'L — Control de legalidad por autoridad judicial (valor de catálogo)',
  `modalidad_de_cuidado` varchar(20) DEFAULT NULL COMMENT 'M — Modalidad de cuidado (valor de catálogo)',
  `id_dispositivo_residencial` varchar(255) DEFAULT NULL COMMENT 'N — ID dispositivo residencial',
  `nombre_de_la_residencia_hogar` varchar(120) NOT NULL COMMENT 'O — Nombre de la residencia/hogar',
  `id_familia` bigint DEFAULT NULL COMMENT 'P — ID familia',
  `familia` bigint DEFAULT NULL COMMENT 'Q — Familia',
  `departamento_de_residencia_de_la_familia_dispositivo_fami_597d04` date DEFAULT NULL COMMENT 'R — Departamento de residencia de la familia (dispositivo familiar)',
  `id_familia_ampliada` date DEFAULT NULL COMMENT 'S — ID familia ampliada',
  `familia_ampliada` date DEFAULT NULL COMMENT 'T — Familia Ampliada',
  `vinculo_con_el_nya` date DEFAULT NULL COMMENT 'U — Vínculo con el NyA',
  `departamento_de_residencia_de_la_familia_dispositivo_fami_e8c08b` date DEFAULT NULL COMMENT 'V — Departamento de residencia de la familia (dispositivo familiar)',
  `tipo_de_proyecto_de_restitucion` varchar(20) DEFAULT NULL COMMENT 'W — Tipo de proyecto de restitución (valor de catálogo)',
  `decreto_judicial_de_adoptabilidad` varchar(20) DEFAULT NULL COMMENT 'X — Decreto judicial de adoptabilidad (valor de catálogo)',
  `solicitud_inclusion_proy_autonomia` varchar(20) DEFAULT NULL COMMENT 'Y — Solicitud inclusión proy. autonomía (valor de catálogo)',
  `asiste_actualmente_a_una_institucion_educativa` varchar(20) DEFAULT NULL COMMENT 'Z — ¿Asiste actualmente a una institución educativa? (valor de catálogo)',
  `maximo_nivel_educativo_alcanzado` varchar(24) DEFAULT NULL COMMENT 'AA — Máximo nivel educativo alcanzado (valor de catálogo)',
  `consumo_problematico_de_sustancias` varchar(20) DEFAULT NULL COMMENT 'AB — Consumo problemático de sustancias (valor de catálogo)',
  `fecha_de_cese` date DEFAULT NULL COMMENT 'AC — Fecha de cese',
  `motivo_de_cese` varchar(56) DEFAULT NULL COMMENT 'AD — Motivo de cese (valor de catálogo)',
  `observaciones` text COMMENT 'AE — Observaciones',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c2_mpe_v2_fila` (`importacion_id`,`numero_fila`),
  CONSTRAINT `runac_c2_mpe_v2_ibfk_1` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Datos de MPE v2, hoja "MPE". Generada desde la Capa 1. Sólo entran filas que superaron las validaciones bloqueantes.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_mpe_v2`
--

LOCK TABLES `runac_c2_mpe_v2` WRITE;
/*!40000 ALTER TABLE `runac_c2_mpe_v2` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_mpe_v2` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_mpi_v1`
--

DROP TABLE IF EXISTS `runac_c2_mpi_v1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_mpi_v1` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `importacion_id` bigint NOT NULL COMMENT 'Importación a la que pertenece la fila.',
  `numero_fila` int NOT NULL COMMENT 'Número de fila en el Excel, tal como lo ve quien completa la planilla.',
  `estado` enum('VALIDA','CON_ADVERTENCIA','EDITADA') NOT NULL DEFAULT 'VALIDA' COMMENT 'Resultado de la validación de la fila. Las filas con bloqueantes no llegan a incorporarse.',
  `hash_contenido` char(40) DEFAULT NULL COMMENT 'Huella del contenido, para detectar duplicados exactos y cambios entre períodos.',
  `fecha_del_relevamiento` date NOT NULL COMMENT 'A — Fecha del relevamiento',
  `provincia` varchar(20) DEFAULT NULL COMMENT 'B — Provincia (valor de catálogo)',
  `nombre_del_programa_dispositivo` varchar(120) NOT NULL COMMENT 'C — Nombre del programa/dispositivo',
  `dependencia_institucional` varchar(255) DEFAULT NULL COMMENT 'D — Dependencia institucional',
  `localidad` varchar(120) DEFAULT NULL COMMENT 'E — Localidad',
  `domicilio` varchar(255) DEFAULT NULL COMMENT 'F — Domicilio',
  `equipo_interviniente_dispositivo_espacio` varchar(255) DEFAULT NULL COMMENT 'G — Equipo interviniente',
  `responsable_del_programa` varchar(255) DEFAULT NULL COMMENT 'H — Responsable del programa',
  `telefono_de_contacto` varchar(50) DEFAULT NULL COMMENT 'I — Teléfono de contacto',
  `mail_de_contacto` varchar(120) DEFAULT NULL COMMENT 'J — Mail de contacto',
  `apellido_s` varchar(120) NOT NULL COMMENT 'K — Apellido/s',
  `nombre_s` varchar(120) NOT NULL COMMENT 'L — Nombre/s',
  `situacion_de_documentacion` varchar(24) DEFAULT NULL COMMENT 'M — Situación de documentación (valor de catálogo)',
  `n_dni` varchar(15) DEFAULT NULL,
  `n_de_cuil` varchar(13) NOT NULL COMMENT 'O — Nº de CUIL',
  `genero` varchar(20) DEFAULT NULL COMMENT 'P — Género (valor de catálogo)',
  `pais_de_nacimiento` varchar(44) DEFAULT NULL COMMENT 'Q — País de nacimiento (valor de catálogo)',
  `fecha_de_nacimiento` date NOT NULL COMMENT 'R — Fecha de nacimiento',
  `edad` bigint DEFAULT NULL COMMENT 'S — Edad',
  `asistencia_escolar` varchar(20) DEFAULT NULL COMMENT 'T — Asistencia escolar (valor de catálogo)',
  `maximo_nivel_educativo_alcanzado` varchar(23) DEFAULT NULL COMMENT 'U — Máximo nivel educativo alcanzado (valor de catálogo)',
  `domicilio_actual` varchar(255) DEFAULT NULL COMMENT 'V — Domicilio actual',
  `provincia_nya` varchar(20) DEFAULT NULL COMMENT 'W — Provincia (NyA) (valor de catálogo)',
  `localidad_nya` varchar(120) DEFAULT NULL COMMENT 'X — Localidad (NyA)',
  `partido` varchar(120) DEFAULT NULL COMMENT 'Y — Partido',
  `codigo_postal` varchar(10) DEFAULT NULL COMMENT 'Z — Código postal',
  `destinatario` varchar(20) DEFAULT NULL COMMENT 'AA — Destinatario (valor de catálogo)',
  `linea_de_accion` varchar(24) DEFAULT NULL COMMENT 'AB — Línea de acción (valor de catálogo)',
  `enfermedad_cronica` varchar(255) DEFAULT NULL COMMENT 'AC — Enfermedad crónica',
  `problematica_de_salud` varchar(20) DEFAULT NULL COMMENT 'AD — Problemática de salud (valor de catálogo)',
  `consumo_problematico_de_sustancias` varchar(255) DEFAULT NULL COMMENT 'AE — Consumo problemático de sustancias',
  `presenta_alguna_discapacidad` varchar(20) DEFAULT NULL COMMENT 'AF — ¿Presenta alguna discapacidad? (valor de catálogo)',
  `tipo_de_discapacidad` varchar(20) DEFAULT NULL COMMENT 'AG — Tipo de discapacidad (valor de catálogo)',
  `posee_cud` varchar(20) DEFAULT NULL COMMENT 'AH — ¿Posee CUD? (valor de catálogo)',
  `cobertura_salud` varchar(20) DEFAULT NULL COMMENT 'AI — Cobertura salud (valor de catálogo)',
  `seguridad_social` varchar(255) DEFAULT NULL COMMENT 'AJ — Seguridad social',
  `se_identifica_con_algun_pueblo_originario` varchar(20) DEFAULT NULL COMMENT 'AK — ¿Se identifica con algún pueblo originario? (valor de catálogo)',
  `pueblo_originario_especificar` text COMMENT 'AL — Pueblo originario (especificar)',
  `tiene_hijos_as` varchar(20) DEFAULT NULL COMMENT 'AM — ¿Tiene hijos/as? (valor de catálogo)',
  `relacion_vincular_del_referente` varchar(20) DEFAULT NULL COMMENT 'AN — Relación vincular del referente (valor de catálogo)',
  `apellido_s_del_referente` varchar(120) NOT NULL COMMENT 'AO — Apellido/s del referente',
  `nombre_s_del_referente` varchar(120) NOT NULL COMMENT 'AP — Nombre/s del referente',
  `dni_del_referente` varchar(15) NOT NULL COMMENT 'AQ — DNI del referente',
  `genero_del_referente` varchar(20) DEFAULT NULL COMMENT 'AR — Género del referente (valor de catálogo)',
  `fecha_de_nacimiento_del_referente` date NOT NULL COMMENT 'AS — Fecha de nacimiento del referente',
  `nacionalidad_del_referente` varchar(44) DEFAULT NULL COMMENT 'AT — Nacionalidad del referente (valor de catálogo)',
  `domicilio_actual_del_referente` varchar(255) DEFAULT NULL COMMENT 'AU — Domicilio actual del referente',
  `codigo_postal_del_referente` varchar(10) DEFAULT NULL COMMENT 'AV — Código postal del referente',
  `localidad_del_referente` varchar(120) DEFAULT NULL COMMENT 'AW — Localidad del referente',
  `partido_del_referente` varchar(120) DEFAULT NULL COMMENT 'AX — Partido del referente',
  `provincia_del_referente` varchar(20) DEFAULT NULL COMMENT 'AY — Provincia del referente (valor de catálogo)',
  `telefono_y_mail_del_referente` varchar(50) DEFAULT NULL COMMENT 'AZ — Teléfono y mail del referente',
  `nivel_escolar_del_referente` varchar(24) DEFAULT NULL COMMENT 'BA — Nivel escolar del referente (valor de catálogo)',
  `situacion_laboral_del_referente` varchar(20) DEFAULT NULL COMMENT 'BB — Situación laboral del referente (valor de catálogo)',
  `seguridad_social_del_referente` varchar(255) DEFAULT NULL COMMENT 'BC — Seguridad social del referente',
  `el_referente_se_identifica_con_algun_pueblo_originario` varchar(20) DEFAULT NULL COMMENT 'BD — ¿El referente se identifica con algún pueblo originario? (valor de catálogo)',
  `pueblo_originario_del_refrente` varchar(255) DEFAULT NULL COMMENT 'BE — Pueblo originario del refrente',
  `equipo_interviniente_medida` varchar(255) DEFAULT NULL COMMENT 'BF — Equipo Interviniente',
  `origen_de_la_demanda` varchar(20) DEFAULT NULL COMMENT 'BG — Origen de la demanda (valor de catálogo)',
  `causas_de_las_medidas` varchar(255) DEFAULT NULL COMMENT 'BH — Causas de las medidas',
  `fecha_de_la_medida_mpi` date DEFAULT NULL COMMENT 'BI — Fecha de la medida MPI',
  `plazos_en_la_intervencion` varchar(255) DEFAULT NULL COMMENT 'BJ — Plazos en la intervención',
  `causas_del_cese_de_la_mpi` varchar(255) DEFAULT NULL COMMENT 'BK — Causas del cese de la MPI',
  `observaciones` text COMMENT 'BL — Observaciones',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c2_mpi_v1_fila` (`importacion_id`,`numero_fila`),
  CONSTRAINT `runac_c2_mpi_v1_ibfk_1` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2281 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Datos de MPI v1, hoja "MPI". Generada desde la Capa 1. Sólo entran filas que superaron las validaciones bloqueantes.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_mpi_v1`
--

LOCK TABLES `runac_c2_mpi_v1` WRITE;
/*!40000 ALTER TABLE `runac_c2_mpi_v1` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_mpi_v1` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_mpj_dae_v1_dae`
--

DROP TABLE IF EXISTS `runac_c2_mpj_dae_v1_dae`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_mpj_dae_v1_dae` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `importacion_id` bigint NOT NULL COMMENT 'Importación a la que pertenece la fila.',
  `numero_fila` int NOT NULL COMMENT 'Número de fila en el Excel, tal como lo ve quien completa la planilla.',
  `estado` enum('VALIDA','CON_ADVERTENCIA','EDITADA') NOT NULL DEFAULT 'VALIDA' COMMENT 'Resultado de la validación de la fila. Las filas con bloqueantes no llegan a incorporarse.',
  `hash_contenido` char(40) DEFAULT NULL COMMENT 'Huella del contenido, para detectar duplicados exactos y cambios entre períodos.',
  `fecha_del_relevamiento` date NOT NULL COMMENT 'A — Fecha del relevamiento',
  `provincia` varchar(20) DEFAULT NULL COMMENT 'B — Provincia (valor de catálogo)',
  `nombre_del_dispositivo` varchar(120) NOT NULL COMMENT 'C — Nombre del dispositivo',
  `tipo_de_dispositivo` varchar(31) DEFAULT NULL COMMENT 'D — Tipo de dispositivo (valor de catálogo)',
  `dependencia_institucional` varchar(255) DEFAULT NULL COMMENT 'E — Dependencia institucional',
  `localidad` varchar(120) DEFAULT NULL COMMENT 'F — Localidad',
  `id_del_nino_nina_o_adolescente` varchar(255) DEFAULT NULL COMMENT 'G — ID del Niño, niña o Adolescente',
  `apellido_s` varchar(120) NOT NULL COMMENT 'H — Apellido/s',
  `nombre_s` varchar(120) NOT NULL COMMENT 'I — Nombre/s',
  `situacion_de_documentacion` varchar(24) DEFAULT NULL COMMENT 'J — Situación de documentación (valor de catálogo)',
  `n_dni` varchar(15) DEFAULT NULL,
  `genero` varchar(20) DEFAULT NULL COMMENT 'L — Género (valor de catálogo)',
  `pais_de_nacimiento` varchar(44) DEFAULT NULL COMMENT 'M — País de nacimiento (valor de catálogo)',
  `fecha_de_nacimiento` date NOT NULL COMMENT 'N — Fecha de nacimiento',
  `edad` bigint DEFAULT NULL COMMENT 'O — Edad',
  `asiste_a_institucion_educativa` varchar(22) DEFAULT NULL COMMENT 'P — ¿Asiste a institución educativa? (valor de catálogo)',
  `maximo_nivel_educativo_alcanzado` varchar(24) DEFAULT NULL COMMENT 'Q — Máximo nivel educativo alcanzado (valor de catálogo)',
  `enfermedad_cronica` varchar(20) DEFAULT NULL COMMENT 'R — Enfermedad crónica (valor de catálogo)',
  `consumo_problematico_de_sustancias` varchar(20) DEFAULT NULL COMMENT 'S — Consumo problemático de sustancias (valor de catálogo)',
  `presenta_alguna_discapacidad` varchar(20) DEFAULT NULL COMMENT 'T — ¿Presenta alguna discapacidad? (valor de catálogo)',
  `tipo_de_discapacidad` varchar(20) DEFAULT NULL COMMENT 'U — Tipo de discapacidad (valor de catálogo)',
  `posee_cud` varchar(20) DEFAULT NULL COMMENT 'V — ¿Posee CUD? (valor de catálogo)',
  `cobertura_salud` varchar(22) DEFAULT NULL COMMENT 'W — Cobertura salud (valor de catálogo)',
  `se_identifica_con_algun_pueblo_originario` varchar(20) DEFAULT NULL COMMENT 'X — ¿Se identifica con algún pueblo originario? (valor de catálogo)',
  `pueblo_originario_especificar` text COMMENT 'Y — Pueblo originario (especificar)',
  `tiene_hijos_as` varchar(20) DEFAULT NULL COMMENT 'Z — ¿Tiene hijos/as? (valor de catálogo)',
  `motivo_de_la_aprehension` varchar(28) DEFAULT NULL COMMENT 'AA — Motivo de la aprehensión (valor de catálogo)',
  `descripcion_causa_contravencion` text COMMENT 'AB — Descripción causa/contravención',
  `fecha_de_ingreso_al_dispositivo` date DEFAULT NULL COMMENT 'AC — Fecha de ingreso al dispositivo',
  `hora_de_ingreso_al_dispositivo` time DEFAULT NULL,
  `fuerza_de_seguridad` varchar(20) DEFAULT NULL COMMENT 'AE — Fuerza de seguridad (valor de catálogo)',
  `n_comisaria_o_dependencia` varchar(255) DEFAULT NULL COMMENT 'AF — N° comisaría o dependencia',
  `departamento_de_la_dependencia` varchar(255) DEFAULT NULL COMMENT 'AG — Departamento de la dependencia',
  `paso_por_comisaria_previo_ingreso` varchar(20) DEFAULT NULL COMMENT 'AH — ¿Pasó por comisaría previo ingreso? (valor de catálogo)',
  `tiempo_en_comisaria` varchar(20) DEFAULT NULL COMMENT 'AI — Tiempo en comisaría (valor de catálogo)',
  `fecha_de_egreso_del_dispositivo` date DEFAULT NULL COMMENT 'AJ — Fecha de egreso del dispositivo',
  `hora_de_egreso_del_dispositivo` time DEFAULT NULL,
  `destino_al_egreso` varchar(35) DEFAULT NULL COMMENT 'AL — Destino al egreso (valor de catálogo)',
  `especificar_destino_al_egreso` varchar(255) DEFAULT NULL,
  `denuncia_por_apremios_ilegales` varchar(20) DEFAULT NULL COMMENT 'AN — Denuncia por apremios ilegales (valor de catálogo)',
  `dependencia_judicial` varchar(255) DEFAULT NULL COMMENT 'AO — Dependencia judicial',
  `edad_al_ingreso` int DEFAULT NULL,
  `observaciones` text COMMENT 'AQ — Observaciones',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c2_mpj_dae_v1_dae_fila` (`importacion_id`,`numero_fila`),
  CONSTRAINT `runac_c2_mpj_dae_v1_dae_ibfk_1` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1831 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Datos de MPJ_DAE v1, hoja "DAE". Generada desde la Capa 1. Sólo entran filas que superaron las validaciones bloqueantes.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_mpj_dae_v1_dae`
--

LOCK TABLES `runac_c2_mpj_dae_v1_dae` WRITE;
/*!40000 ALTER TABLE `runac_c2_mpj_dae_v1_dae` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_mpj_dae_v1_dae` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_mpj_dae_v1_mpj`
--

DROP TABLE IF EXISTS `runac_c2_mpj_dae_v1_mpj`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_mpj_dae_v1_mpj` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `importacion_id` bigint NOT NULL COMMENT 'Importación a la que pertenece la fila.',
  `numero_fila` int NOT NULL COMMENT 'Número de fila en el Excel, tal como lo ve quien completa la planilla.',
  `estado` enum('VALIDA','CON_ADVERTENCIA','EDITADA') NOT NULL DEFAULT 'VALIDA' COMMENT 'Resultado de la validación de la fila. Las filas con bloqueantes no llegan a incorporarse.',
  `hash_contenido` char(40) DEFAULT NULL COMMENT 'Huella del contenido, para detectar duplicados exactos y cambios entre períodos.',
  `fecha_del_relevamiento` date NOT NULL COMMENT 'A — Fecha del relevamiento',
  `provincia` varchar(20) DEFAULT NULL COMMENT 'B — Provincia (valor de catálogo)',
  `nombre_del_dispositivo` varchar(120) NOT NULL COMMENT 'C — Nombre del dispositivo',
  `tipo_de_dispositivo` varchar(42) DEFAULT NULL COMMENT 'D — Tipo de dispositivo (valor de catálogo)',
  `dependencia_institucional` varchar(255) DEFAULT NULL COMMENT 'E — Dependencia institucional',
  `localidad` varchar(120) DEFAULT NULL COMMENT 'F — Localidad',
  `id_del_nino_nina_o_adolescente` bigint DEFAULT NULL COMMENT 'G — ID del Niño, niña o Adolescente',
  `apellido_s` varchar(120) NOT NULL COMMENT 'H — Apellido/s',
  `nombre_s` varchar(120) NOT NULL COMMENT 'I — Nombre/s',
  `situacion_de_documentacion` varchar(24) DEFAULT NULL COMMENT 'J — Situación de documentación (valor de catálogo)',
  `n_dni` varchar(15) DEFAULT NULL,
  `genero` varchar(20) DEFAULT NULL COMMENT 'L — Género (valor de catálogo)',
  `pais_de_nacimiento` varchar(44) DEFAULT NULL COMMENT 'M — País de nacimiento (valor de catálogo)',
  `fecha_de_nacimiento` date NOT NULL COMMENT 'N — Fecha de nacimiento',
  `edad` bigint DEFAULT NULL COMMENT 'O — Edad',
  `asiste_a_institucion_educativa` varchar(22) DEFAULT NULL COMMENT 'P — ¿Asiste a institución educativa? (valor de catálogo)',
  `maximo_nivel_educativo_alcanzado` varchar(24) DEFAULT NULL COMMENT 'Q — Máximo nivel educativo alcanzado (valor de catálogo)',
  `enfermedad_cronica` varchar(20) DEFAULT NULL COMMENT 'R — Enfermedad crónica (valor de catálogo)',
  `consumo_problematico_de_sustancias` varchar(20) DEFAULT NULL COMMENT 'S — Consumo problemático de sustancias (valor de catálogo)',
  `presenta_alguna_discapacidad` varchar(20) DEFAULT NULL COMMENT 'T — ¿Presenta alguna discapacidad? (valor de catálogo)',
  `tipo_de_discapacidad` varchar(20) DEFAULT NULL COMMENT 'U — Tipo de discapacidad (valor de catálogo)',
  `posee_cud` varchar(20) DEFAULT NULL COMMENT 'V — ¿Posee CUD? (valor de catálogo)',
  `cobertura_salud` varchar(22) DEFAULT NULL COMMENT 'W — Cobertura salud (valor de catálogo)',
  `se_identifica_con_algun_pueblo_originario` varchar(20) DEFAULT NULL COMMENT 'X — ¿Se identifica con algún pueblo originario? (valor de catálogo)',
  `pueblo_originario_especificar` text COMMENT 'Y — Pueblo originario (especificar)',
  `asignacion_universal_por_hijo` varchar(27) DEFAULT NULL COMMENT 'Z — Asignación Universal por Hijo (valor de catálogo)',
  `tiene_hijos_as` varchar(20) DEFAULT NULL COMMENT 'AA — ¿Tiene hijos/as? (valor de catálogo)',
  `descripcion_causa_penal_contravencion` text COMMENT 'AB — Descripción causa penal/contravención',
  `fecha_de_ingreso_al_dispositivo` date DEFAULT NULL COMMENT 'AC — Fecha de ingreso al dispositivo',
  `procedencia_inmediata` varchar(42) DEFAULT NULL COMMENT 'AD — Procedencia inmediata (valor de catálogo)',
  `especificar_procedencia` text COMMENT 'AE — Especificar procedencia',
  `dependencia_judicial` varchar(255) DEFAULT NULL COMMENT 'AF — Dependencia judicial',
  `situacion_procesal` varchar(30) DEFAULT NULL COMMENT 'AG — Situación procesal (valor de catálogo)',
  `monto_de_la_pena` decimal(18,4) DEFAULT NULL COMMENT 'AH — Monto de la pena',
  `fecha_de_egreso_del_dispositivo` date DEFAULT NULL COMMENT 'AI — Fecha de egreso del dispositivo',
  `destino_al_egreso` varchar(35) DEFAULT NULL COMMENT 'AJ — Destino al egreso (valor de catálogo)',
  `especificar_destino_al_egreso` varchar(255) DEFAULT NULL,
  `observaciones` text COMMENT 'AL — Observaciones',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c2_mpj_dae_v1_mpj_fila` (`importacion_id`,`numero_fila`),
  CONSTRAINT `runac_c2_mpj_dae_v1_mpj_ibfk_1` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1831 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Datos de MPJ_DAE v1, hoja "MPJ". Generada desde la Capa 1. Sólo entran filas que superaron las validaciones bloqueantes.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_mpj_dae_v1_mpj`
--

LOCK TABLES `runac_c2_mpj_dae_v1_mpj` WRITE;
/*!40000 ALTER TABLE `runac_c2_mpj_dae_v1_mpj` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_mpj_dae_v1_mpj` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_observacion`
--

DROP TABLE IF EXISTS `runac_c2_observacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_observacion` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `presentacion_id` bigint NOT NULL COMMENT 'Presentación observada.',
  `importacion_id` bigint DEFAULT NULL COMMENT 'Importación puntual observada.',
  `numero_fila` int DEFAULT NULL COMMENT 'Fila puntual observada.',
  `campo_id` bigint DEFAULT NULL COMMENT 'Campo puntual observado.',
  `identificador_registro` varchar(100) DEFAULT NULL COMMENT 'Identificador provincial del registro observado.',
  `texto` text NOT NULL COMMENT 'La observación, escrita por el revisor técnico nacional.',
  `estado` enum('ABIERTA','RESPONDIDA','SUBSANADA','DESESTIMADA') NOT NULL DEFAULT 'ABIERTA' COMMENT 'Seguimiento de la observación.',
  `respuesta` text COMMENT 'Respuesta de la jurisdicción.',
  `creada_el` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento en que se formuló.',
  `usuario_observa` varchar(150) NOT NULL COMMENT 'Revisor que la formuló.',
  `respondida_el` datetime DEFAULT NULL COMMENT 'Momento de la respuesta.',
  `usuario_responde` varchar(150) DEFAULT NULL COMMENT 'Usuario provincial que respondió.',
  PRIMARY KEY (`id`),
  KEY `runac_c2_observacion_presentacion` (`presentacion_id`,`estado`),
  KEY `importacion_id` (`importacion_id`),
  KEY `campo_id` (`campo_id`),
  CONSTRAINT `runac_c2_observacion_ibfk_1` FOREIGN KEY (`presentacion_id`) REFERENCES `runac_c2_presentacion` (`id`),
  CONSTRAINT `runac_c2_observacion_ibfk_2` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`),
  CONSTRAINT `runac_c2_observacion_ibfk_3` FOREIGN KEY (`campo_id`) REFERENCES `runac_c1_campo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Observaciones del revisor nacional. El revisor no modifica datos provinciales: observa. El ciclo de observación y subsanación no tiene límite de rondas.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_observacion`
--

LOCK TABLES `runac_c2_observacion` WRITE;
/*!40000 ALTER TABLE `runac_c2_observacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_observacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_periodo`
--

DROP TABLE IF EXISTS `runac_c2_periodo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_periodo` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `codigo` varchar(30) NOT NULL COMMENT 'Código del período, por ejemplo 2026_T1.',
  `anio` smallint NOT NULL COMMENT 'Año del corte.',
  `numero` tinyint NOT NULL COMMENT 'Número de corte dentro del año. Con periodicidad trimestral va de 1 a 4.',
  `fecha_desde` date NOT NULL COMMENT 'Primer día del período de referencia.',
  `fecha_hasta` date NOT NULL COMMENT 'Último día del período de referencia. Es la fecha de corte: la fotografía se toma a ese día.',
  `estado` enum('PREPARACION','ABIERTO','CERRADO') NOT NULL DEFAULT 'PREPARACION' COMMENT 'PREPARACION: se está definiendo la estructura y la Capa 1 todavía puede cambiar. ABIERTO: las jurisdicciones importan y la estructura queda congelada. CERRADO: no se admiten más cargas.',
  `declaro_cambios` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'El administrador declaró, al abrir el período, si había cambios de estructura respecto del anterior.',
  `usuario_declara` varchar(150) DEFAULT NULL COMMENT 'Usuario que realizó la declaración.',
  `declarado_el` datetime DEFAULT NULL COMMENT 'Momento de la declaración.',
  `abierto_el` datetime DEFAULT NULL COMMENT 'Momento en que se habilitó la carga.',
  `cerrado_el` datetime DEFAULT NULL COMMENT 'Momento en que se cerró la carga.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  UNIQUE KEY `runac_c2_periodo_anio_numero` (`anio`,`numero`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Períodos de corte. Mientras un período está ABIERTO la estructura que utiliza no puede modificarse: alguna jurisdicción ya pudo haber importado.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_periodo`
--

LOCK TABLES `runac_c2_periodo` WRITE;
/*!40000 ALTER TABLE `runac_c2_periodo` DISABLE KEYS */;
INSERT INTO `runac_c2_periodo` VALUES (1,'2026_T1',2026,1,'2026-01-01','2026-03-31','ABIERTO',0,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `runac_c2_periodo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_periodo_archivo`
--

DROP TABLE IF EXISTS `runac_c2_periodo_archivo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_periodo_archivo` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `periodo_id` bigint NOT NULL COMMENT 'Período.',
  `archivo_version_id` bigint NOT NULL COMMENT 'Versión de estructura que rige para ese archivo en ese período.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c2_periodo_archivo_unica` (`periodo_id`,`archivo_version_id`),
  KEY `archivo_version_id` (`archivo_version_id`),
  CONSTRAINT `runac_c2_periodo_archivo_ibfk_1` FOREIGN KEY (`periodo_id`) REFERENCES `runac_c2_periodo` (`id`),
  CONSTRAINT `runac_c2_periodo_archivo_ibfk_2` FOREIGN KEY (`archivo_version_id`) REFERENCES `runac_c1_archivo_version` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Qué versión de cada archivo rige en cada período. Si no hubo cambios, dos períodos apuntan a la misma versión y no se duplica ninguna definición. El nombre de la tabla receptora se deduce por convención del archivo y la versión.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_periodo_archivo`
--

LOCK TABLES `runac_c2_periodo_archivo` WRITE;
/*!40000 ALTER TABLE `runac_c2_periodo_archivo` DISABLE KEYS */;
INSERT INTO `runac_c2_periodo_archivo` VALUES (1,1,1),(2,1,2),(4,1,3),(8,1,4),(5,1,5);
/*!40000 ALTER TABLE `runac_c2_periodo_archivo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_presentacion`
--

DROP TABLE IF EXISTS `runac_c2_presentacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_presentacion` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `periodo_id` bigint NOT NULL COMMENT 'Período al que corresponde la presentación.',
  `jurisdiccion_id` bigint NOT NULL COMMENT 'Jurisdicción que presenta.',
  `version` int NOT NULL DEFAULT '1' COMMENT 'Número de versión. Una subsanación genera una versión nueva; la anterior se conserva con sus observaciones.',
  `estado` enum('EN_CARGA','CERRADA','EN_REVISION','OBSERVADA','SUBSANADA','HABILITADA','PRESENTADA','CONSOLIDADA') NOT NULL DEFAULT 'EN_CARGA' COMMENT 'Estado del circuito jurisdicción-Nación. No se mezcla con el estado de cada importación: una presentación puede tener importaciones anuladas y estar igual en condiciones de cerrarse.',
  `cerrada_el` datetime DEFAULT NULL COMMENT 'Cierre de carga: el responsable provincial declaró terminada la carga y la envió a revisión.',
  `habilitada_el` datetime DEFAULT NULL COMMENT 'Momento en que el revisor técnico nacional habilitó la presentación formal.',
  `presentada_el` datetime DEFAULT NULL COMMENT 'Presentación formal. Se generó el comprobante.',
  `consolidada_el` datetime DEFAULT NULL COMMENT 'Momento en que los datos se incorporaron a la Capa 3.',
  `expediente` varchar(100) DEFAULT NULL COMMENT 'Número GDE, incorporado por el responsable provincial tras remitir el comprobante. Su ausencia no impide la consolidación: es un resguardo documental de la jurisdicción.',
  `usuario_cierra` varchar(150) DEFAULT NULL COMMENT 'Responsable provincial que cerró la carga.',
  `usuario_habilita` varchar(150) DEFAULT NULL COMMENT 'Revisor técnico nacional que habilitó la presentación.',
  `usuario_presenta` varchar(150) DEFAULT NULL COMMENT 'Responsable provincial que presentó formalmente.',
  `reemplaza_a` bigint DEFAULT NULL COMMENT 'Presentación anterior que esta versión subsana.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `runac_c2_presentacion_unica` (`periodo_id`,`jurisdiccion_id`,`version`),
  KEY `jurisdiccion_id` (`jurisdiccion_id`),
  KEY `reemplaza_a` (`reemplaza_a`),
  CONSTRAINT `runac_c2_presentacion_ibfk_1` FOREIGN KEY (`periodo_id`) REFERENCES `runac_c2_periodo` (`id`),
  CONSTRAINT `runac_c2_presentacion_ibfk_2` FOREIGN KEY (`jurisdiccion_id`) REFERENCES `runac_c2_jurisdiccion` (`id`),
  CONSTRAINT `runac_c2_presentacion_ibfk_3` FOREIGN KEY (`reemplaza_a`) REFERENCES `runac_c2_presentacion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=503 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Presentación de una jurisdicción para un período. Agrupa las importaciones de los distintos archivos.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_presentacion`
--

LOCK TABLES `runac_c2_presentacion` WRITE;
/*!40000 ALTER TABLE `runac_c2_presentacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_presentacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c2_reglas_incumplidas`
--

DROP TABLE IF EXISTS `runac_c2_reglas_incumplidas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c2_reglas_incumplidas` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno.',
  `importacion_id` bigint NOT NULL COMMENT 'Importación en la que se detectó.',
  `campo_id` bigint NOT NULL COMMENT 'Campo de Capa 1 afectado. Siempre presente: un incumplimiento sin campo es un problema del archivo y va a runac_c2_errores_de_importacion.',
  `regla_id` bigint DEFAULT NULL COMMENT 'Regla de Capa 1 que no se cumplió. Queda vacío cuando el incumplimiento es de una validación intrínseca del campo —tipo de dato, obligatoriedad, valor de catálogo o longitud máxima—, que se define en runac_c1_campo y no en runac_c1_regla. El código indica de cuál se trata.',
  `codigo` varchar(50) NOT NULL COMMENT 'Código estable del incumplimiento, para contarlos y agruparlos: qué regla se incumple con más frecuencia, si se repite entre períodos.',
  `severidad` enum('BLOQUEANTE','ADVERTENCIA') NOT NULL COMMENT 'Tomada de la regla aplicada al campo.',
  `nombre_hoja` varchar(255) NOT NULL COMMENT 'Hoja del Excel donde está el problema.',
  `numero_fila` int NOT NULL COMMENT 'Fila del Excel, tal como la ve el usuario.',
  `columna` varchar(10) DEFAULT NULL COMMENT 'Letra de la columna en el Excel.',
  `nombre_campo` varchar(255) DEFAULT NULL COMMENT 'Título de la columna, para que el informe se entienda sin unir tablas.',
  `identificador_registro` varchar(100) DEFAULT NULL COMMENT 'Identificador provincial de la fila afectada.',
  `valor_encontrado` text COMMENT 'El valor que provocó el incumplimiento, tal como vino.',
  `descripcion` text NOT NULL COMMENT 'Mensaje en lenguaje claro, tomado de la definición de la regla.',
  `resuelta` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Indica si la advertencia fue corregida o justificada dentro del sistema.',
  PRIMARY KEY (`id`),
  KEY `runac_c2_reglas_incumplidas_sev` (`importacion_id`,`severidad`),
  KEY `runac_c2_reglas_incumplidas_ubic` (`importacion_id`,`numero_fila`),
  KEY `runac_c2_reglas_incumplidas_codigo` (`codigo`),
  KEY `campo_id` (`campo_id`),
  KEY `regla_id` (`regla_id`),
  CONSTRAINT `runac_c2_reglas_incumplidas_ibfk_1` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`),
  CONSTRAINT `runac_c2_reglas_incumplidas_ibfk_2` FOREIGN KEY (`campo_id`) REFERENCES `runac_c1_campo` (`id`),
  CONSTRAINT `runac_c2_reglas_incumplidas_ibfk_3` FOREIGN KEY (`regla_id`) REFERENCES `runac_c1_regla` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11574 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Validaciones no superadas en un archivo que SÍ fue admitido. Una fila por incumplimiento, con su ubicación exacta.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c2_reglas_incumplidas`
--

LOCK TABLES `runac_c2_reglas_incumplidas` WRITE;
/*!40000 ALTER TABLE `runac_c2_reglas_incumplidas` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c2_reglas_incumplidas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_cambio`
--

DROP TABLE IF EXISTS `runac_c3_cambio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_cambio` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `entidad` varchar(40) NOT NULL,
  `entidad_id` bigint NOT NULL,
  `campo` varchar(100) NOT NULL,
  `valor_anterior` text,
  `valor_nuevo` text,
  `presentacion_id` bigint DEFAULT NULL,
  `usuario` varchar(150) DEFAULT NULL,
  `motivo` enum('CONSOLIDACION','PRECEDENCIA','NORMALIZACION','REPROCESO') DEFAULT NULL,
  `justificacion` text,
  `fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_cambio_entidad` (`entidad`,`entidad_id`,`campo`),
  KEY `fk_cambio_pres` (`presentacion_id`),
  CONSTRAINT `fk_cambio_pres` FOREIGN KEY (`presentacion_id`) REFERENCES `runac_c2_presentacion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='El historial campo a campo. No es un accesorio de auditoria: es la fuente de las series historicas, porque la base guarda una sola fila por chico con el dato vigente. Por eso registra el valor ANTERIOR y la presentacion que produjo el cambio.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_cambio`
--

LOCK TABLES `runac_c3_cambio` WRITE;
/*!40000 ALTER TABLE `runac_c3_cambio` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_cambio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_coincidencia`
--

DROP TABLE IF EXISTS `runac_c3_coincidencia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_coincidencia` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `importacion_id` bigint NOT NULL,
  `numero_fila` int DEFAULT NULL,
  `persona_candidata_id` bigint DEFAULT NULL,
  `motivo` varchar(255) NOT NULL,
  `puntaje` decimal(5,2) DEFAULT NULL,
  `estado` enum('PENDIENTE','CONFIRMADA','DESCARTADA') NOT NULL DEFAULT 'PENDIENTE',
  `resuelta_por` varchar(150) DEFAULT NULL,
  `resuelta_el` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_coincidencia_estado` (`estado`),
  KEY `fk_coincidencia_imp` (`importacion_id`),
  KEY `fk_coincidencia_persona` (`persona_candidata_id`),
  CONSTRAINT `fk_coincidencia_imp` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`),
  CONSTRAINT `fk_coincidencia_persona` FOREIGN KEY (`persona_candidata_id`) REFERENCES `runac_c3_persona` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Coincidencias de identidad que no se pueden decidir solas: documento y nombre que coinciden parcialmente, o nombre y fecha de nacimiento sin documento.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_coincidencia`
--

LOCK TABLES `runac_c3_coincidencia` WRITE;
/*!40000 ALTER TABLE `runac_c3_coincidencia` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_coincidencia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_disp_alcance_territorial`
--

DROP TABLE IF EXISTS `runac_c3_disp_alcance_territorial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_disp_alcance_territorial` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `dispositivo_id` bigint NOT NULL,
  `jurisdiccion_alcanzada` varchar(120) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_alcance` (`dispositivo_id`,`jurisdiccion_alcanzada`),
  CONSTRAINT `fk_alcance_disp` FOREIGN KEY (`dispositivo_id`) REFERENCES `runac_c3_dispositivo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='MPT, CAD y guardia informan VARIAS jurisdicciones de alcance. Por eso es una relacion y no un campo de texto: permite responder que dispositivos alcanzan a un municipio determinado.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_disp_alcance_territorial`
--

LOCK TABLES `runac_c3_disp_alcance_territorial` WRITE;
/*!40000 ALTER TABLE `runac_c3_disp_alcance_territorial` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_disp_alcance_territorial` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_disp_cad`
--

DROP TABLE IF EXISTS `runac_c3_disp_cad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_disp_cad` (
  `dispositivo_id` bigint NOT NULL,
  PRIMARY KEY (`dispositivo_id`),
  CONSTRAINT `fk_disp_cad` FOREIGN KEY (`dispositivo_id`) REFERENCES `runac_c3_dispositivo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='27 campos, 22 compartidos con CRC. Propios: resolucion de creacion, articulacion interministerial, alcance territorial y tiempo maximo de permanencia en horas.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_disp_cad`
--

LOCK TABLES `runac_c3_disp_cad` WRITE;
/*!40000 ALTER TABLE `runac_c3_disp_cad` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_disp_cad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_disp_crc`
--

DROP TABLE IF EXISTS `runac_c3_disp_crc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_disp_crc` (
  `dispositivo_id` bigint NOT NULL,
  PRIMARY KEY (`dispositivo_id`),
  CONSTRAINT `fk_disp_crc` FOREIGN KEY (`dispositivo_id`) REFERENCES `runac_c3_dispositivo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='36 campos. Grupos: capacidad por genero, proyecto institucional y normativa convivencial, personal por funcion, 6 protocolos, contacto socioafectivo, educacion obligatoria por nivel y horas, formacion profesional y talleres, espacios, condiciones de las celdas.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_disp_crc`
--

LOCK TABLES `runac_c3_disp_crc` WRITE;
/*!40000 ALTER TABLE `runac_c3_disp_crc` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_disp_crc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_disp_crsc`
--

DROP TABLE IF EXISTS `runac_c3_disp_crsc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_disp_crsc` (
  `dispositivo_id` bigint NOT NULL,
  PRIMARY KEY (`dispositivo_id`),
  CONSTRAINT `fk_disp_crsc` FOREIGN KEY (`dispositivo_id`) REFERENCES `runac_c3_dispositivo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='36 campos IDENTICOS a los de CRC: mismos nombres, misma cantidad. Se mantiene como registro propio porque son regimenes distintos y sus cuestionarios pueden diferenciarse. Consulta abierta a la DNPYPI: corresponde relevar lo mismo?';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_disp_crsc`
--

LOCK TABLES `runac_c3_disp_crsc` WRITE;
/*!40000 ALTER TABLE `runac_c3_disp_crsc` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_disp_crsc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_disp_guardia`
--

DROP TABLE IF EXISTS `runac_c3_disp_guardia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_disp_guardia` (
  `dispositivo_id` bigint NOT NULL,
  PRIMARY KEY (`dispositivo_id`),
  CONSTRAINT `fk_disp_guardia` FOREIGN KEY (`dispositivo_id`) REFERENCES `runac_c3_dispositivo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='9 campos, todos contenidos en CAD: es un subconjunto exacto. Consulta abierta a la DNPYPI: faltan campos propios de la guardia?';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_disp_guardia`
--

LOCK TABLES `runac_c3_disp_guardia` WRITE;
/*!40000 ALTER TABLE `runac_c3_disp_guardia` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_disp_guardia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_disp_mpt`
--

DROP TABLE IF EXISTS `runac_c3_disp_mpt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_disp_mpt` (
  `dispositivo_id` bigint NOT NULL,
  PRIMARY KEY (`dispositivo_id`),
  CONSTRAINT `fk_disp_mpt` FOREIGN KEY (`dispositivo_id`) REFERENCES `runac_c3_dispositivo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='10 campos, 8 de ellos tambien en CRC. Propios: espacio de grupalidad y alcance territorial. Es un programa en territorio, no un lugar de alojamiento.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_disp_mpt`
--

LOCK TABLES `runac_c3_disp_mpt` WRITE;
/*!40000 ALTER TABLE `runac_c3_disp_mpt` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_disp_mpt` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_disp_residencial`
--

DROP TABLE IF EXISTS `runac_c3_disp_residencial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_disp_residencial` (
  `dispositivo_id` bigint NOT NULL,
  PRIMARY KEY (`dispositivo_id`),
  CONSTRAINT `fk_disp_resid` FOREIGN KEY (`dispositivo_id`) REFERENCES `runac_c3_dispositivo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='61 campos. Grupos: datos institucionales, gestion y convenio con el OPN, el establecimiento cuenta con..., protocolos, capacidad y cobertura, perfiles poblacionales admitidos, personal por funcion, 14 capacitaciones, proyecto de restitucion de derechos, insercion familiar y comunitaria. Comparte con los penales solo 5 de sus 61 campos, los de identificacion: son instrumentos distintos.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_disp_residencial`
--

LOCK TABLES `runac_c3_disp_residencial` WRITE;
/*!40000 ALTER TABLE `runac_c3_disp_residencial` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_disp_residencial` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_dispositivo`
--

DROP TABLE IF EXISTS `runac_c3_dispositivo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_dispositivo` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'ID SISOC del dispositivo. Las plantillas siguientes deben traerlo.',
  `jurisdiccion_id` bigint NOT NULL,
  `tipo` enum('RESIDENCIAL','CRC','CRSC','MPT','CAD','GUARDIA') NOT NULL,
  `denominacion` varchar(255) NOT NULL,
  `dependencia_institucional` varchar(255) DEFAULT NULL,
  `localidad` varchar(120) DEFAULT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  `telefono` varchar(60) DEFAULT NULL,
  `estado` enum('ACTIVO','BAJA_TEMPORAL','BAJA_DEFINITIVA') NOT NULL DEFAULT 'ACTIVO',
  `creado_el` datetime DEFAULT CURRENT_TIMESTAMP,
  `actualizado_el` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dispositivo` (`jurisdiccion_id`,`denominacion`,`tipo`),
  CONSTRAINT `fk_dispositivo_jur` FOREIGN KEY (`jurisdiccion_id`) REFERENCES `runac_c2_jurisdiccion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='El lugar donde se lleva a cabo la medida. Identificacion comun a los seis tipos: un identificador unico que el resto del sistema referencia sin conocer el tipo. Son los cinco campos que efectivamente aparecen en las seis hojas. Localidad y direccion faltan en la hoja Guardia Comisaria: omision senalada a la DNPYPI.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_dispositivo`
--

LOCK TABLES `runac_c3_dispositivo` WRITE;
/*!40000 ALTER TABLE `runac_c3_dispositivo` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_dispositivo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_familia_acogimiento`
--

DROP TABLE IF EXISTS `runac_c3_familia_acogimiento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_familia_acogimiento` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `jurisdiccion_id` bigint NOT NULL,
  `modalidad` enum('FORMAL','AMPLIADA') NOT NULL,
  `id_provincial` varchar(60) DEFAULT NULL,
  `denominacion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_familia` (`jurisdiccion_id`,`modalidad`,`id_provincial`),
  CONSTRAINT `fk_familia_jur` FOREIGN KEY (`jurisdiccion_id`) REFERENCES `runac_c2_jurisdiccion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='La planilla MPE informa dos modalidades en columnas paralelas, y hoy reune identificador y apellido de los cuidadores en un mismo campo. La separacion fue solicitada a la DNPYPI.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_familia_acogimiento`
--

LOCK TABLES `runac_c3_familia_acogimiento` WRITE;
/*!40000 ALTER TABLE `runac_c3_familia_acogimiento` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_familia_acogimiento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_medida_dae`
--

DROP TABLE IF EXISTS `runac_c3_medida_dae`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_medida_dae` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nino_adolescente_id` bigint NOT NULL,
  `jurisdiccion_id` bigint NOT NULL,
  `dispositivo_id` bigint DEFAULT NULL COMMENT 'CAD o guardia especializada.',
  `fecha_hora_ingreso` datetime DEFAULT NULL,
  `fecha_hora_egreso` datetime DEFAULT NULL,
  `fuerza_interviniente` varchar(120) DEFAULT NULL,
  `dependencia` varchar(255) DEFAULT NULL,
  `tiempo_permanencia` varchar(60) DEFAULT NULL,
  `destino` varchar(120) DEFAULT NULL,
  `denuncia_por_apremios` varchar(30) DEFAULT NULL,
  `presentacion_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dae` (`nino_adolescente_id`,`dispositivo_id`,`fecha_hora_ingreso`),
  KEY `fk_dae_jur` (`jurisdiccion_id`),
  KEY `fk_dae_disp` (`dispositivo_id`),
  KEY `fk_dae_pres` (`presentacion_id`),
  CONSTRAINT `fk_dae_disp` FOREIGN KEY (`dispositivo_id`) REFERENCES `runac_c3_dispositivo` (`id`),
  CONSTRAINT `fk_dae_jur` FOREIGN KEY (`jurisdiccion_id`) REFERENCES `runac_c2_jurisdiccion` (`id`),
  CONSTRAINT `fk_dae_nya` FOREIGN KEY (`nino_adolescente_id`) REFERENCES `runac_c3_nino_adolescente` (`id`),
  CONSTRAINT `fk_dae_pres` FOREIGN KEY (`presentacion_id`) REFERENCES `runac_c2_presentacion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Ingreso y egreso de CAD o permanencia en dependencia policial. A diferencia de las otras tres, describe un HECHO ya ocurrido: se acumula, no se actualiza. Puede haber varios por chico. El requerimiento advierte que no debe confundirse con una medida penal prolongada.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_medida_dae`
--

LOCK TABLES `runac_c3_medida_dae` WRITE;
/*!40000 ALTER TABLE `runac_c3_medida_dae` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_medida_dae` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_medida_mpe`
--

DROP TABLE IF EXISTS `runac_c3_medida_mpe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_medida_mpe` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nino_adolescente_id` bigint NOT NULL,
  `jurisdiccion_id` bigint NOT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_cese` date DEFAULT NULL,
  `estado` enum('VIGENTE','CESADA','NO_INFORMADA') DEFAULT NULL,
  `motivo_cese` varchar(255) DEFAULT NULL,
  `modalidad_cuidado` enum('RESIDENCIAL','FAMILIAR_FORMAL','FAMILIA_AMPLIADA') DEFAULT NULL,
  `dispositivo_id` bigint DEFAULT NULL COMMENT 'Solo cuando la modalidad es residencial.',
  `familia_id` bigint DEFAULT NULL COMMENT 'Familia de acogimiento formal.',
  `familia_ampliada_id` bigint DEFAULT NULL COMMENT 'Familia ampliada.',
  `motivo` varchar(255) DEFAULT NULL,
  `proyecto_restitucion` varchar(120) DEFAULT NULL,
  `participa_nya_en_per` varchar(30) DEFAULT NULL,
  `articulacion_per_plan_estadia` varchar(30) DEFAULT NULL,
  `intervencion_judicial` varchar(120) DEFAULT NULL,
  `control_legalidad_juzgado_familia` varchar(30) DEFAULT NULL,
  `adoptabilidad` varchar(60) DEFAULT NULL,
  `autonomia` varchar(60) DEFAULT NULL,
  `pae` varchar(30) DEFAULT NULL COMMENT 'Programa de Acompanamiento para el Egreso.',
  `presentacion_alta_id` bigint DEFAULT NULL,
  `presentacion_actualizacion_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_mpe` (`nino_adolescente_id`,`jurisdiccion_id`,`fecha_inicio`),
  KEY `ix_mpe_estado` (`estado`),
  KEY `fk_mpe_jur` (`jurisdiccion_id`),
  KEY `fk_mpe_disp` (`dispositivo_id`),
  KEY `fk_mpe_familia` (`familia_id`),
  KEY `fk_mpe_familia_amp` (`familia_ampliada_id`),
  KEY `fk_mpe_pres_alta` (`presentacion_alta_id`),
  KEY `fk_mpe_pres_act` (`presentacion_actualizacion_id`),
  CONSTRAINT `fk_mpe_disp` FOREIGN KEY (`dispositivo_id`) REFERENCES `runac_c3_dispositivo` (`id`),
  CONSTRAINT `fk_mpe_familia` FOREIGN KEY (`familia_id`) REFERENCES `runac_c3_familia_acogimiento` (`id`),
  CONSTRAINT `fk_mpe_familia_amp` FOREIGN KEY (`familia_ampliada_id`) REFERENCES `runac_c3_familia_acogimiento` (`id`),
  CONSTRAINT `fk_mpe_jur` FOREIGN KEY (`jurisdiccion_id`) REFERENCES `runac_c2_jurisdiccion` (`id`),
  CONSTRAINT `fk_mpe_nya` FOREIGN KEY (`nino_adolescente_id`) REFERENCES `runac_c3_nino_adolescente` (`id`),
  CONSTRAINT `fk_mpe_pres_act` FOREIGN KEY (`presentacion_actualizacion_id`) REFERENCES `runac_c2_presentacion` (`id`),
  CONSTRAINT `fk_mpe_pres_alta` FOREIGN KEY (`presentacion_alta_id`) REFERENCES `runac_c2_presentacion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Medida de Proteccion Excepcional. La modalidad determina si se enlaza a un dispositivo residencial o a una familia.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_medida_mpe`
--

LOCK TABLES `runac_c3_medida_mpe` WRITE;
/*!40000 ALTER TABLE `runac_c3_medida_mpe` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_medida_mpe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_medida_mpi`
--

DROP TABLE IF EXISTS `runac_c3_medida_mpi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_medida_mpi` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nino_adolescente_id` bigint NOT NULL,
  `jurisdiccion_id` bigint NOT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_cese` date DEFAULT NULL,
  `estado` enum('VIGENTE','CESADA','NO_INFORMADA') DEFAULT NULL,
  `motivo_cese` varchar(255) DEFAULT NULL,
  `origen_demanda` varchar(120) DEFAULT NULL,
  `causas` varchar(255) DEFAULT NULL,
  `destinatario` varchar(120) DEFAULT NULL COMMENT 'La planilla lo agrupa entre los datos del chico, pero describe la medida.',
  `linea_de_accion` varchar(120) DEFAULT NULL COMMENT 'Idem.',
  `plazo_previsto` varchar(120) DEFAULT NULL,
  `referente_adulto_id` bigint DEFAULT NULL,
  `relacion_vincular` varchar(60) DEFAULT NULL COMMENT 'Vinculo del referente con este chico.',
  `unidad_interviniente_id` bigint DEFAULT NULL COMMENT 'Referencia normalizada.',
  `unidad_denominacion_informada` varchar(255) DEFAULT NULL COMMENT 'Tal como la informo la jurisdiccion. Sostiene la trazabilidad.',
  `unidad_dependencia` varchar(255) DEFAULT NULL,
  `unidad_localidad` varchar(120) DEFAULT NULL,
  `unidad_domicilio` varchar(255) DEFAULT NULL,
  `unidad_equipo` varchar(255) DEFAULT NULL,
  `unidad_responsable` varchar(255) DEFAULT NULL,
  `unidad_telefono` varchar(60) DEFAULT NULL,
  `unidad_mail` varchar(120) DEFAULT NULL,
  `presentacion_alta_id` bigint DEFAULT NULL,
  `presentacion_actualizacion_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_mpi` (`nino_adolescente_id`,`jurisdiccion_id`,`fecha_inicio`),
  KEY `ix_mpi_estado` (`estado`),
  KEY `fk_mpi_jur` (`jurisdiccion_id`),
  KEY `fk_mpi_referente` (`referente_adulto_id`),
  KEY `fk_mpi_unidad` (`unidad_interviniente_id`),
  KEY `fk_mpi_pres_alta` (`presentacion_alta_id`),
  KEY `fk_mpi_pres_act` (`presentacion_actualizacion_id`),
  CONSTRAINT `fk_mpi_jur` FOREIGN KEY (`jurisdiccion_id`) REFERENCES `runac_c2_jurisdiccion` (`id`),
  CONSTRAINT `fk_mpi_nya` FOREIGN KEY (`nino_adolescente_id`) REFERENCES `runac_c3_nino_adolescente` (`id`),
  CONSTRAINT `fk_mpi_pres_act` FOREIGN KEY (`presentacion_actualizacion_id`) REFERENCES `runac_c2_presentacion` (`id`),
  CONSTRAINT `fk_mpi_pres_alta` FOREIGN KEY (`presentacion_alta_id`) REFERENCES `runac_c2_presentacion` (`id`),
  CONSTRAINT `fk_mpi_referente` FOREIGN KEY (`referente_adulto_id`) REFERENCES `runac_c3_referente_adulto` (`id`),
  CONSTRAINT `fk_mpi_unidad` FOREIGN KEY (`unidad_interviniente_id`) REFERENCES `runac_c3_unidad_interviniente` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Medida de Proteccion Integral. Se actualiza cuando presenta novedades.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_medida_mpi`
--

LOCK TABLES `runac_c3_medida_mpi` WRITE;
/*!40000 ALTER TABLE `runac_c3_medida_mpi` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_medida_mpi` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_medida_mpj`
--

DROP TABLE IF EXISTS `runac_c3_medida_mpj`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_medida_mpj` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nino_adolescente_id` bigint NOT NULL,
  `jurisdiccion_id` bigint NOT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_cese` date DEFAULT NULL,
  `estado` enum('VIGENTE','CESADA','NO_INFORMADA') DEFAULT NULL,
  `descripcion_causa_penal` varchar(500) DEFAULT NULL,
  `dependencia_judicial` varchar(255) DEFAULT NULL,
  `situacion_procesal` varchar(120) DEFAULT NULL,
  `monto_de_la_pena` decimal(10,2) DEFAULT NULL,
  `dispositivo_id` bigint DEFAULT NULL COMMENT 'Dispositivo penal donde se encuentra el adolescente.',
  `fecha_ingreso_dispositivo` date DEFAULT NULL,
  `edad_al_ingreso` int DEFAULT NULL,
  `procedencia` varchar(120) DEFAULT NULL,
  `procedencia_dispositivo_id` bigint DEFAULT NULL COMMENT 'Cuando la procedencia es otro dispositivo del padron.',
  `fecha_egreso_dispositivo` date DEFAULT NULL,
  `destino_al_egreso` varchar(120) DEFAULT NULL,
  `destino_dispositivo_id` bigint DEFAULT NULL COMMENT 'Cuando el egreso es hacia otro dispositivo penal.',
  `presentacion_alta_id` bigint DEFAULT NULL,
  `presentacion_actualizacion_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_mpj` (`nino_adolescente_id`,`jurisdiccion_id`,`fecha_inicio`),
  KEY `ix_mpj_estado` (`estado`),
  KEY `fk_mpj_jur` (`jurisdiccion_id`),
  KEY `fk_mpj_disp` (`dispositivo_id`),
  KEY `fk_mpj_disp_proc` (`procedencia_dispositivo_id`),
  KEY `fk_mpj_disp_dest` (`destino_dispositivo_id`),
  KEY `fk_mpj_pres_alta` (`presentacion_alta_id`),
  KEY `fk_mpj_pres_act` (`presentacion_actualizacion_id`),
  CONSTRAINT `fk_mpj_disp` FOREIGN KEY (`dispositivo_id`) REFERENCES `runac_c3_dispositivo` (`id`),
  CONSTRAINT `fk_mpj_disp_dest` FOREIGN KEY (`destino_dispositivo_id`) REFERENCES `runac_c3_dispositivo` (`id`),
  CONSTRAINT `fk_mpj_disp_proc` FOREIGN KEY (`procedencia_dispositivo_id`) REFERENCES `runac_c3_dispositivo` (`id`),
  CONSTRAINT `fk_mpj_jur` FOREIGN KEY (`jurisdiccion_id`) REFERENCES `runac_c2_jurisdiccion` (`id`),
  CONSTRAINT `fk_mpj_nya` FOREIGN KEY (`nino_adolescente_id`) REFERENCES `runac_c3_nino_adolescente` (`id`),
  CONSTRAINT `fk_mpj_pres_act` FOREIGN KEY (`presentacion_actualizacion_id`) REFERENCES `runac_c2_presentacion` (`id`),
  CONSTRAINT `fk_mpj_pres_alta` FOREIGN KEY (`presentacion_alta_id`) REFERENCES `runac_c2_presentacion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Medida Penal Juvenil. Referencia hasta tres dispositivos: el actual, la procedencia y el destino al egreso. DEFINICION PENDIENTE: como informan las jurisdicciones el traslado de un adolescente entre dispositivos por la misma causa penal.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_medida_mpj`
--

LOCK TABLES `runac_c3_medida_mpj` WRITE;
/*!40000 ALTER TABLE `runac_c3_medida_mpj` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_medida_mpj` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_nino_adolescente`
--

DROP TABLE IF EXISTS `runac_c3_nino_adolescente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_nino_adolescente` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `persona_id` bigint NOT NULL,
  `apellidos` varchar(120) DEFAULT NULL,
  `nombres` varchar(120) DEFAULT NULL,
  `situacion_documentacion` varchar(60) DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `edad` int DEFAULT NULL,
  `genero` varchar(30) DEFAULT NULL,
  `pais_nacimiento` varchar(120) DEFAULT NULL,
  `asiste_institucion_educativa` varchar(30) DEFAULT NULL,
  `maximo_nivel_educativo` varchar(60) DEFAULT NULL,
  `cobertura_salud` varchar(60) DEFAULT NULL,
  `enfermedad_cronica` varchar(30) DEFAULT NULL,
  `problematica_salud` varchar(255) DEFAULT NULL,
  `consumo_problematico` varchar(30) DEFAULT NULL,
  `presenta_discapacidad` varchar(30) DEFAULT NULL,
  `tipo_discapacidad` varchar(60) DEFAULT NULL,
  `posee_cud` varchar(30) DEFAULT NULL,
  `seguridad_social` varchar(60) DEFAULT NULL,
  `asignacion_universal_por_hijo` varchar(30) DEFAULT NULL,
  `pueblo_originario` varchar(30) DEFAULT NULL,
  `pueblo_originario_especificar` varchar(120) DEFAULT NULL,
  `tiene_hijos` varchar(30) DEFAULT NULL,
  `domicilio_actual` varchar(255) DEFAULT NULL COMMENT 'Solo lo releva el MPI: en proteccion integral el chico vive ahi.',
  `provincia` varchar(120) DEFAULT NULL,
  `localidad` varchar(120) DEFAULT NULL,
  `partido` varchar(120) DEFAULT NULL,
  `codigo_postal` varchar(20) DEFAULT NULL,
  `creado_el` datetime DEFAULT CURRENT_TIMESTAMP,
  `actualizado_el` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_nya_persona` (`persona_id`),
  CONSTRAINT `fk_nya_persona` FOREIGN KEY (`persona_id`) REFERENCES `runac_c3_persona` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Todo lo relevado sobre el chico, con independencia del archivo que lo informo y de la medida que tenga: la medida es circunstancial y el chico no. UNA fila por chico, con el dato vigente; si una presentacion informa un valor distinto se actualiza y el cambio va a runac_c3_cambio, que es la fuente de las series historicas.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_nino_adolescente`
--

LOCK TABLES `runac_c3_nino_adolescente` WRITE;
/*!40000 ALTER TABLE `runac_c3_nino_adolescente` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_nino_adolescente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_nya_id_provincial`
--

DROP TABLE IF EXISTS `runac_c3_nya_id_provincial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_nya_id_provincial` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nino_adolescente_id` bigint NOT NULL,
  `jurisdiccion_id` bigint NOT NULL,
  `identificador` varchar(60) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_id_provincial` (`jurisdiccion_id`,`identificador`),
  KEY `ix_id_prov_nya` (`nino_adolescente_id`),
  CONSTRAINT `fk_id_prov_jur` FOREIGN KEY (`jurisdiccion_id`) REFERENCES `runac_c2_jurisdiccion` (`id`),
  CONSTRAINT `fk_id_prov_nya` FOREIGN KEY (`nino_adolescente_id`) REFERENCES `runac_c3_nino_adolescente` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Identificador provincial del chico. Uno por jurisdiccion: un chico informado por dos provincias tiene un identificador en cada una y ambos lo designan. Debe ser obligatorio y estable en el tiempo. FALTA EN EL MPI: omision senalada a la DNPYPI.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_nya_id_provincial`
--

LOCK TABLES `runac_c3_nya_id_provincial` WRITE;
/*!40000 ALTER TABLE `runac_c3_nya_id_provincial` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_nya_id_provincial` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_origen`
--

DROP TABLE IF EXISTS `runac_c3_origen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_origen` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `entidad` varchar(40) NOT NULL COMMENT 'Tabla de Capa 3 a la que pertenece el registro.',
  `entidad_id` bigint NOT NULL,
  `presentacion_id` bigint NOT NULL,
  `importacion_id` bigint NOT NULL,
  `numero_fila` int DEFAULT NULL,
  `accion` enum('ALTA','ACTUALIZACION','SIN_CAMBIOS') DEFAULT NULL,
  `fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_origen_entidad` (`entidad`,`entidad_id`),
  KEY `fk_origen_pres` (`presentacion_id`),
  KEY `fk_origen_imp` (`importacion_id`),
  CONSTRAINT `fk_origen_imp` FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`),
  CONSTRAINT `fk_origen_pres` FOREIGN KEY (`presentacion_id`) REFERENCES `runac_c2_presentacion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Responde de donde salio cada dato: provincia, periodo, archivo, hoja, fila y version.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_origen`
--

LOCK TABLES `runac_c3_origen` WRITE;
/*!40000 ALTER TABLE `runac_c3_origen` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_origen` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_persona`
--

DROP TABLE IF EXISTS `runac_c3_persona`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_persona` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'ID SISOC. Se asigna una vez y no cambia.',
  `ciudadano_id` bigint DEFAULT NULL COMMENT 'Vinculo con ciudadanos.Ciudadano de SISOC. Definicion pendiente.',
  `tipo_documento` varchar(30) DEFAULT NULL,
  `numero_documento` varchar(20) DEFAULT NULL,
  `cuil` varchar(13) DEFAULT NULL,
  `creada_el` datetime DEFAULT CURRENT_TIMESTAMP,
  `actualizada_el` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_persona_documento` (`tipo_documento`,`numero_documento`),
  KEY `ix_persona_cuil` (`cuil`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='El mismo ser humano, y unicamente su identidad resuelta. Todo lo relevado sobre una persona vive en su caracterizacion: nino o adolescente, o referente adulto. Una misma persona puede tener las dos.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_persona`
--

LOCK TABLES `runac_c3_persona` WRITE;
/*!40000 ALTER TABLE `runac_c3_persona` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_persona` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_precedencia`
--

DROP TABLE IF EXISTS `runac_c3_precedencia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_precedencia` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `entidad` varchar(40) NOT NULL,
  `entidad_id` bigint DEFAULT NULL,
  `campo` varchar(100) NOT NULL,
  `valor_elegido` text,
  `regla` varchar(120) DEFAULT NULL COMMENT 'Jerarquia por archivo, ultimo informado, fuente externa, o decision manual.',
  `usuario` varchar(150) DEFAULT NULL,
  `fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_precedencia_entidad` (`entidad`,`entidad_id`,`campo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='La decision sobre que valor prevalece, conservada para las presentaciones siguientes: la misma discrepancia no se resuelve dos veces.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_precedencia`
--

LOCK TABLES `runac_c3_precedencia` WRITE;
/*!40000 ALTER TABLE `runac_c3_precedencia` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_precedencia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_referente_adulto`
--

DROP TABLE IF EXISTS `runac_c3_referente_adulto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_referente_adulto` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `persona_id` bigint NOT NULL,
  `apellidos` varchar(120) DEFAULT NULL,
  `nombres` varchar(120) DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `genero` varchar(30) DEFAULT NULL,
  `nacionalidad` varchar(120) DEFAULT NULL,
  `domicilio_actual` varchar(255) DEFAULT NULL,
  `provincia` varchar(120) DEFAULT NULL,
  `localidad` varchar(120) DEFAULT NULL,
  `partido` varchar(120) DEFAULT NULL,
  `codigo_postal` varchar(20) DEFAULT NULL,
  `telefono` varchar(60) DEFAULT NULL,
  `mail` varchar(120) DEFAULT NULL,
  `nivel_escolar` varchar(60) DEFAULT NULL,
  `situacion_laboral` varchar(60) DEFAULT NULL,
  `creado_el` datetime DEFAULT CURRENT_TIMESTAMP,
  `actualizado_el` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_referente_persona` (`persona_id`),
  CONSTRAINT `fk_referente_persona` FOREIGN KEY (`persona_id`) REFERENCES `runac_c3_persona` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='18 campos, informados unicamente en el MPI. Limitacion: la planilla no preve identificador propio del referente; sin documento, cada presentacion lo registra como un adulto distinto.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_referente_adulto`
--

LOCK TABLES `runac_c3_referente_adulto` WRITE;
/*!40000 ALTER TABLE `runac_c3_referente_adulto` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_referente_adulto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_unidad_alias`
--

DROP TABLE IF EXISTS `runac_c3_unidad_alias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_unidad_alias` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `jurisdiccion_id` bigint NOT NULL,
  `denominacion_informada` varchar(255) NOT NULL,
  `unidad_interviniente_id` bigint DEFAULT NULL COMMENT 'Vacio mientras esta pendiente de normalizar.',
  `estado` enum('RESUELTA','PENDIENTE') NOT NULL DEFAULT 'PENDIENTE',
  `resuelta_por` varchar(150) DEFAULT NULL,
  `resuelta_el` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_alias` (`jurisdiccion_id`,`denominacion_informada`),
  KEY `ix_alias_unidad` (`unidad_interviniente_id`),
  CONSTRAINT `fk_alias_jur` FOREIGN KEY (`jurisdiccion_id`) REFERENCES `runac_c2_jurisdiccion` (`id`),
  CONSTRAINT `fk_alias_unidad` FOREIGN KEY (`unidad_interviniente_id`) REFERENCES `runac_c3_unidad_interviniente` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='El diccionario. Opera en la importacion (Capa 2) y se perfecciona en cada iteracion: lo ya conocido se resuelve solo, lo nuevo queda pendiente y su resolucion incorpora una entrada para la proxima vez. Su mejora se puede aplicar a lo ya consolidado; ese reproceso queda en runac_c3_cambio.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_unidad_alias`
--

LOCK TABLES `runac_c3_unidad_alias` WRITE;
/*!40000 ALTER TABLE `runac_c3_unidad_alias` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_unidad_alias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runac_c3_unidad_interviniente`
--

DROP TABLE IF EXISTS `runac_c3_unidad_interviniente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runac_c3_unidad_interviniente` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `jurisdiccion_id` bigint NOT NULL,
  `denominacion_normalizada` varchar(255) NOT NULL,
  `dependencia` varchar(255) DEFAULT NULL,
  `tipo_espacio` varchar(60) DEFAULT NULL COMMENT 'Recomendado a la DNPYPI: servicio local, programa municipal, programa provincial, hogar o residencia, centro de dia, otro.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_unidad` (`jurisdiccion_id`,`denominacion_normalizada`),
  CONSTRAINT `fk_unidad_jur` FOREIGN KEY (`jurisdiccion_id`) REFERENCES `runac_c2_jurisdiccion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla referencial de servicios, equipos y programas de proteccion integral. No es un padron que las jurisdicciones completen: se construye con lo que efectivamente se informa. El universo es abierto y por eso no admite un padron cerrado.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runac_c3_unidad_interviniente`
--

LOCK TABLES `runac_c3_unidad_interviniente` WRITE;
/*!40000 ALTER TABLE `runac_c3_unidad_interviniente` DISABLE KEYS */;
/*!40000 ALTER TABLE `runac_c3_unidad_interviniente` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-17 11:39:25
