# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Stat.py,v 1.1 2004/06/04 06:38:36 port001 Exp $
#

__modulename__ = "Stat"

import MySQL
import Config
  
def DBSize():

    dbsize = 0

    result = MySQL.Query("SHOW TABLE STATUS", fetch="all")

    for row in result:
	dbsize += row["Data_length"] + row["Index_length"]

    return str(dbsize)

def UserCount():

    result = MySQL.Query("SELECT count(*) FROM %s%s" %
                         (Config.MySQL["prefix"], Config.MySQL["user_table"]),
                          fetch="one")

    return str(result["count(*)"])

def ScriptCount():

    result = MySQL.Query("SELECT count(*) FROM %s%s" %
                         (Config.MySQL["prefix"],
                          Config.MySQL["script_table"]), fetch="one")

    return str(result["count(*)"])

def SubScriptCount():

    result = MySQL.Query("SELECT count(*) FROM %s%s" %
                         (Config.MySQL["prefix"],
                          Config.MySQL["subscript_table"]), fetch="one")

    return str(result["count(*)"])

def CommentCount():

    result = MySQL.Query("SELECT count(*) FROM %s%s" %
                         (Config.MySQL["prefix"],
                          Config.MySQL["comment_table"]), fetch="one")

    return str(result["count(*)"])

def CategoryCount():

    result = MySQL.Query("SELECT count(*) FROM %s%s" %
                         (Config.MySQL["prefix"],
                          Config.MySQL["category_table"]), fetch="one")

    return str(result["count(*)"])

def SessionCount():

    result = MySQL.Query("SELECT count(*) FROM %s%s" %
                         (Config.MySQL["prefix"],
                          Config.MySQL["session_table"]), fetch="one")

    return str(result["count(*)"])
