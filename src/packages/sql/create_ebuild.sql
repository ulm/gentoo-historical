/*
 * Copyright (C) 2005, marduk <marduk@python.net>
 *
 * This copyrighted material is made available to anyone wishing to use,
 * modify, copy, or redistribute it subject to the terms and conditions
 * of the GNU General Public License v.2.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */
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
  `iuse` mediumtext NOT NULL,
  PRIMARY KEY  (`category`,`name`,`version`)
)
