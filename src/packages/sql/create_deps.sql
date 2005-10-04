CREATE TABLE `deps` (
  `category` varchar(30) NOT NULL default '',
  `name` varchar(45) NOT NULL default '',
  `version` varchar(30) NOT NULL default '',
  `depend` mediumtext,
  `rdepend` mediumtext,
  `pdepend` mediumtext,
  PRIMARY KEY  (`category`,`name`,`version`)
)
