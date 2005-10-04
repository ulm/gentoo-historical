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
CREATE TABLE `package` (
  `category` varchar(30) NOT NULL default '',
  `name` varchar(40) NOT NULL default '',
  `homepage` varchar(100) default NULL,
  `description` text,
  `when_found` datetime NOT NULL default '0000-00-00 00:00:00',
  PRIMARY KEY  (`category`,`name`)
)
