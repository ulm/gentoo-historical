CREATE TABLE `package` (
  `category` varchar(30) NOT NULL default '',
  `name` varchar(40) NOT NULL default '',
  `homepage` varchar(100) default NULL,
  `description` text,
  `when_found` datetime NOT NULL default '0000-00-00 00:00:00',
  PRIMARY KEY  (`category`,`name`)
)
