# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Admin.py,v 1.2 2004/11/12 20:37:49 port001 Exp $
#

import MySQL
import Config
from Logging import err
from time import strftime, gmtime

__modulename__ = "Admin"

def optimize_tables():

    tables_str = ""
    failure_count = 0

    for table in MySQL.Query("SHOW TABLES", fetch="all"):
        tables_str += "%s, " % table["Tables_in_%s" % Config.MySQL["prefix"][:-1]]

    for result in MySQL.Query("OPTIMIZE TABLES %s" % tables_str[:-2], fetch="all"):
        if result["Msg_type"] == "error":
            err("Optimization error: %s" % result["Msg_text"], __modulename__)
            sys.exit(1)

    MySQL.Query("UPDATE %s%s SET %s_table_opt = " %
               (Config.MySQL["prefix"], Config.MySQL["state_table"], Config.MySQL["state_table"])
                + "%s", strftime("%Y-%m-%d", gmtime()), fetch="none")

def get_optimize_days():

    result = MySQL.Query("SELECT %s_table_opt FROM %s%s " %
                      (Config.MySQL["state_table"], Config.MySQL["prefix"], Config.MySQL["state_table"]),
                       fetch = "one")

    return result["state_table_opt"]
