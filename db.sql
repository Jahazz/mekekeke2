-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               10.4.8-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Version:             10.2.0.5599
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- Dumping database structure for mekekeke
CREATE DATABASE IF NOT EXISTS `mekekeke` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;
USE `mekekeke`;

-- Dumping structure for table mekekeke.conversations
CREATE TABLE IF NOT EXISTS `conversations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `conversation_id` varchar(50) DEFAULT NULL,
  `first_user_id` varchar(50) DEFAULT NULL,
  `second_user_id` varchar(50) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `end_reason` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=507 DEFAULT CHARSET=utf8mb4;

-- Data exporting was unselected.

-- Dumping structure for table mekekeke.messages
CREATE TABLE IF NOT EXISTS `messages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `author_id` varchar(50) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `message` varchar(9999) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1267 DEFAULT CHARSET=utf8mb4;

-- Data exporting was unselected.

-- Dumping structure for view mekekeke.messages_in_conversations
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `messages_in_conversations` (
	`conversation_id` VARCHAR(50) NULL COLLATE 'utf8mb4_general_ci',
	`COUNT(*)` BIGINT(21) NOT NULL
) ENGINE=MyISAM;

-- Dumping structure for procedure mekekeke.get_conversation_if_id
DELIMITER //
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_conversation_if_id`(
	IN `conversation_id_param` CHAR(50)
)
BEGIN
SELECT  m.timestamp, if( m.author_id = c.first_user_id , 'A' , 'B' ) AS author,message,m.author_id FROM conversations c 
JOIN messages m ON c.first_user_id = m.author_id OR c.second_user_id = m.author_id
WHERE c.conversation_id = conversation_id_param
ORDER BY m.timestamp;
END//
DELIMITER ;

-- Dumping structure for view mekekeke.messages_in_conversations
-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `messages_in_conversations`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `messages_in_conversations` AS SELECT conversation_id, COUNT(*) FROM conversations c 
JOIN messages m ON c.first_user_id = m.author_id OR c.second_user_id = m.author_id
GROUP BY conversation_id
ORDER BY conversation_id ;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
