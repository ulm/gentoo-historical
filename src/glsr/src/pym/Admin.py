# Copyright 2004-2005 Ian Leitch
# Copyright 1999-2005 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = '$Id: Admin.py,v 1.6 2005/01/27 04:19:15 port001 Exp $'
__modulename__ = 'Admin'

import Config
from MySQL import MySQL
from GLSRException import AdminModuleError

from time import strftime, gmtime

MySQLHandler = MySQL()

def optimize_tables():

    tables_str = ""
    
    for table in MySQLHandler.query("SHOW TABLES", fetch="all"):
        tables_str += "%s, " % table["Tables_in_%s" % Config.MySQL["prefix"][:-1]]

    for result in MySQLHandler.query("OPTIMIZE TABLES %s" % tables_str[:-2], fetch="all"):
        if result["Msg_type"] == "error":
            raise AdminModuleError('Optimization Error', result['Msg_text'])

    MySQLHandler.query("UPDATE %s%s SET %s_table_opt = " %
               (Config.MySQL["prefix"], Config.MySQL["state_table"], Config.MySQL["state_table"])
                + "%s", strftime("%Y-%m-%d", gmtime()), fetch="none")
    
def get_optimize_days():   

    result = MySQLHandler.query("SELECT %s_table_opt FROM %s%s " %
                               (Config.MySQL["state_table"], Config.MySQL["prefix"], Config.MySQL["state_table"]),
                                fetch = "one")

    return result["state_table_opt"]
