DROP USER IF EXISTS `mp_user`@`localhost`;
DROP DATABASE IF EXISTS `openedx_plugin_nacar`;

CREATE USER `mp_user`@`localhost` IDENTIFIED BY 'mp';
CREATE DATABASE `openedx_plugin_nacar`;
GRANT ALL PRIVILEGES ON `openedx_plugin_nacar`.* TO "mp_user"@"localhost";
FLUSH PRIVILEGES;
