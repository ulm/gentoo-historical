# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Stat.py,v 1.3 2004/12/16 14:06:26 port001 Exp $
#

__modulename__ = "Stat"

import Config
from MySQL import MySQL

MySQLHandler = MySQL()
  
def DBSize():

    dbsize = 0

    result = MySQLHandler.query("SHOW TABLE STATUS", fetch="all")

    for row in result:
        dbsize += row["Data_length"] + row["Index_length"]

    return str(dbsize)

def UserCount():

    result = MySQLHandler.query("SELECT count(*) FROM %s%s" %
                                (Config.MySQL["prefix"], Config.MySQL["user_table"]),
                                 fetch="one")

    return str(result["count(*)"])

def ScriptCount():

    result = MySQLHandler.query("SELECT count(*) FROM %s%s" %
                                (Config.MySQL["prefix"],
                                 Config.MySQL["script_table"]), fetch="one")

    return str(result["count(*)"])

def SubScriptCount():

    result = MySQLHandler.query("SELECT count(*) FROM %s%s" %
                                (Config.MySQL["prefix"],
                                 Config.MySQL["subscript_table"]), fetch="one")

    return str(result["count(*)"])

def CommentCount():

    result = MySQLHandler.query("SELECT count(*) FROM %s%s" %
                                (Config.MySQL["prefix"],
                                 Config.MySQL["comment_table"]), fetch="one")

    return str(result["count(*)"])

def CategoryCount():

    result = MySQLHandler.query("SELECT count(*) FROM %s%s" %
                                (Config.MySQL["prefix"],
                                 Config.MySQL["category_table"]), fetch="one")

    return str(result["count(*)"])

def SessionCount():

    result = MySQLHandler.query("SELECT count(*) FROM %s%s" %
                                (Config.MySQL["prefix"],
                                 Config.MySQL["session_table"]), fetch="one")

    return str(result["count(*)"])
