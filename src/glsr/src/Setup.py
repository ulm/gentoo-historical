#!/usr/bin/env python2
#
# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Setup.py,v 1.1 2004/06/04 06:38:33 port001 Exp $
#

import sys
import operator
import MySQLdb
import getpass
from time import strftime, gmtime

sys.path.insert(0, "/usr/lib/glsr/pym")
sys.path.insert(0, "/var/www/buffmuthers.com/htdocs/projects/glsr/pym")

import Config
import Const

db = MySQLdb.connect(host=Config.MySQL["host"], user=Config.MySQL["user"], passwd=Config.MySQL["passwd"], db=Config.MySQL["db"])
cursor = db.cursor()

print "Creating MySQL tables:"

print "  >>> %s%s" % (Config.MySQL["prefix"], Config.MySQL["user_table"])
user_table = ("CREATE TABLE " + Config.MySQL["prefix"] + """%s (
	%s_id		MEDIUMINT(5)	unsigned NOT NULL auto_increment,
	%s_alias	VARCHAR(25)	NOT NULL,
	%s_fullname	VARCHAR(40)	NOT NULL,
	%s_passwd	VARCHAR(32)	NOT NULL,
	%s_email	VARCHAR(50)	NOT NULL,
	%s_rank		MEDIUMINT(5)	NOT NULL default '0',
	%s_type		TINYINT(1)	unsigned NOT NULL default '0',
	%s_joined	DATE		NOT NULL,
	%s_lastip	VARCHAR(15)	NULL,
	PRIMARY		KEY(%s_id),
	KEY		%s_id(%s_id));""" %
              tuple(operator.repeat([Config.MySQL["user_table"]], 13)))

cursor.execute(user_table)
db.commit()

print "  >>> %s%s" % (Config.MySQL["prefix"], Config.MySQL["category_table"])
category_table = ("CREATE TABLE " + Config.MySQL["prefix"] + """%s (
	%s_id		SMALLINT(3)	unsigned NOT NULL auto_increment,
	%s_name		VARCHAR(50)	NOT NULL,
	%s_descr	VARCHAR(100)	NULL,
	%s_parent_id	SMALLINT(3)	unsigned NOT NULL default '0',
	PRIMARY		KEY(%s_id),
	KEY		%s_id(%s_id));""" %
                  tuple(operator.repeat([Config.MySQL["category_table"]], 8)))

cursor.execute(category_table)
db.commit()

print "  >>> %s%s" % (Config.MySQL["prefix"], Config.MySQL["language_table"])
category_table = ("CREATE TABLE " + Config.MySQL["prefix"] + """%s (
	%s_id		SMALLINT(3)	unsigned NOT NULL auto_increment,
	%s_name		VARCHAR(50)	NOT NULL,
	%s_descr	VARCHAR(100)	NULL,
	PRIMARY		KEY(%s_id),
	KEY		%s_id(%s_id));""" %
                  tuple(operator.repeat([Config.MySQL["language_table"]], 7)))

cursor.execute(category_table)
db.commit()


print "  >>> %s%s" % (Config.MySQL["prefix"], Config.MySQL["comment_table"])
comment_table = ("CREATE TABLE " + Config.MySQL["prefix"] + """%s (
	%s_id		MEDIUMINT(6)	unsigned NOT NULL auto_increment,
	%s_submitter_id	MEDIUMINT(5)	unsigned NOT NULL,
	%s_date		DATETIME	NULL,
	%s_subject	VARCHAR(30)	NULL,
	%s_lastedited	DATETIME	NULL,
	%s_body		TEXT		NOT NULL,
	%s_ofscript	MEDIUMINT(6)	unsigned NOT NULL,
	%s_ofversion	INT(10)		unsigned NULL,
	PRIMARY		KEY(%s_id),
	KEY		%s_id(%s_id));""" %
                 tuple(operator.repeat([Config.MySQL["comment_table"]], 12)))

cursor.execute(comment_table)
db.commit()

print "  >>> %s%s" % (Config.MySQL["prefix"], Config.MySQL["script_table"])
script_table = ("CREATE TABLE " + Config.MySQL["prefix"] + """%s (
	%s_id		MEDIUMINT(7)	unsigned NOT NULL auto_increment,
	%s_submitter_id	MEDIUMINT(5)	unsigned NOT NULL,
	%s_category_id	SMALLINT(3)	unsigned NOT NULL,
     	%s_language_id	SMALLINT(3)	unsigned NOT NULL,
	%s_rank		TINYINT(1)	NOT NULL default '0',
	%s_name		VARCHAR(30)	NOT NULL,
	%s_descr	VARCHAR(100)	NOT NULL,
	PRIMARY		KEY(%s_id),
	KEY		%s_id(%s_id));""" %
                tuple(operator.repeat([Config.MySQL["script_table"]], 11)))

cursor.execute(script_table)
db.commit()

print "  >>> %s%s" % (Config.MySQL["prefix"], Config.MySQL["subscript_table"])
subscript_table = ("CREATE TABLE " + Config.MySQL["prefix"] + """%s (
	%s_id		INT(10)		unsigned NOT NULL auto_increment,
	%s_parent_id	MEDIUMINT(7)	unsigned NOT NULL,
	%s_version	VARCHAR(10)	NOT NULL,
	%s_body		TEXT		NOT NULL,
	%s_changelog	TEXT		NOT NULL,
	%s_date		DATETIME	NULL,
	%s_approved	TINYINT(1)	NOT NULL default '-1',
	%s_approvedby	MEDIUMINT(5)	unsigned NULL,
	PRIMARY		KEY(%s_id),
	KEY		%s_id(%s_id));""" %
                   tuple(operator.repeat([Config.MySQL["subscript_table"]],
                                         12)))

cursor.execute(subscript_table)
db.commit()

print "  >>> %s%s" % (Config.MySQL["prefix"], Config.MySQL["session_table"])
session_table = ("CREATE TABLE " + Config.MySQL["prefix"] + """%s (
	%s_id		VARCHAR(30)	NOT NULL,
	%s_user_id	MEDIUMINT(5)	unsigned NOT NULL,
	%s_time		INT(10)		NOT NULL,
	PRIMARY		KEY(%s_id),
	KEY		%s_id(%s_id));""" %
                 tuple(operator.repeat([Config.MySQL["session_table"]], 7)))

cursor.execute(session_table)
db.commit()

# Error reporting turned out not to be practical, leave this here just incase we decide to use a file based system. 
#print "  >>> %s" % Config.MySQL["error_table"]
#error_table = """CREATE TABLE %s (
#	errid		TINYINT(2)	unsigned NOT NULL auto_increment,
#	errmsg		TEXT		NOT NULL,
#	date		DATETIME	NOT NULL,
#	PRIMARY		KEY(errid),
#	KEY		errid(errid));""" % Config.MySQL["error_table"]
#
#cursor.execute(error_table)
#db.commit()

print "  >>> %s%s" % (Config.MySQL["prefix"], Config.MySQL["news_table"])
news_table = ("CREATE TABLE " + Config.MySQL["prefix"] + """%s (
        %s_id           INT(10)         unsigned NOT NULL auto_increment,
        %s_author_id    MEDIUMINT(5)    unsigned NOT NULL,
        %s_date         DATETIME        NOT NULL,
        %s_subject      VARCHAR(100)    NOT NULL,
        %s_body         TEXT            NOT NULL,
        PRIMARY         KEY(%s_id),
        KEY             %s_id(%s_id));""" %
              tuple(operator.repeat([Config.MySQL["news_table"]], 9)))

cursor.execute(news_table)
db.commit()

admin = raw_input("\nAdmin user: ")
if len(admin) == 0:
    print "ERROR: Zero length username"
    sys.exit(1)

passwd = getpass.getpass("Password: ")
if len(passwd) == 0:
    print "ERROR: Zero length password"
    sys.exit(1)
    
passwd2 = getpass.getpass("Re-type password: ")
if passwd != passwd2:
    print "ERROR: passwords do not match"
    sys.exit(1)

fullname = raw_input("Full Name: ")
email = raw_input("Email: ")

print "Creating admin user %s..." % (admin)

cursor.execute("INSERT INTO %s%s " %
               (Config.MySQL["prefix"], Config.MySQL["user_table"]) +
               """(%s_alias, %s_fullname, %s_passwd, %s_email, %s_rank,
               %s_type, %s_joined)""" %
               tuple(operator.repeat([Config.MySQL["user_table"]], 7)) +
               """ VALUES (%s, %s, PASSWORD(%s), %s, 0, %s, %s)""",
               (admin, fullname, passwd, email, Const.TYPE["admin"],
                strftime("%Y-%m-%d", gmtime())))
db.commit()
cursor.close()
print "\nKeep me safe! You may need me later (if things go wrong ;)."
