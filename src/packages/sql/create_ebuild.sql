CREATE TABLE `ebuild` (
  `category` varchar(30) NOT NULL default '',
  `name` varchar(45) NOT NULL default '',
  `version` varchar(30) NOT NULL default '',
  `when_found` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `arch` varchar(160) NOT NULL default '',
  `changelog` mediumtext,
  `prevarch` varchar(160) NOT NULL default '',
  `is_masked` tinyint(4) default NULL,
  `license` varchar(30) default NULL,
  PRIMARY KEY  (`category`,`name`,`version`)
)
