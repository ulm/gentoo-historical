# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Comment.py,v 1.1.1.1 2004/06/04 06:38:36 port001 Exp $
#

import User
import MySQL
import Config
from time import strftime, gmtime

__modulename__ = "Comment"

def Add(submitter, subject, body, ofscript, ofversion):
    """Add comment for script"""
  
    MySQL.Query("INSERT INTO %s " % Config.MySQL["comment_table"] + 
    		"""(submitter, date, subject, body, ofscript, ofversion)
		VALUES
		(%s, %s, %s, %s, %s, %s)""", \
		(submitter, strftime("%Y-%m-%d %H:%M:%S", gmtime()), subject, body, ofscript, ofversion), fetch="none")

def Remove(comid):
    """Remove comment by comid"""

    MySQL.Query("DELETE FROM %s " % Config.MySQL["comment_table"] + "WHERE comid = %s", (comid), fetch="none")

def Modify(comid, details):
    """Modify comment"""

    if "subject" in details:
        MySQL.Query("UPDATE %s " % Config.MySQL["comment_table"] + "SET subject = %s WHERE comid = %s", (details["subject"], comid), fetch="none")
    if "body" in details:
        MySQL.Query("UPDATE %s " % Config.MySQL["comment_table"] + "SET body = %s WHERE comid = %s", (details["body"], comid), fetch="none")

    MySQL.Query("UPDATE %s " % Config.MySQL["comment_table"] + "SET lastedited = %s WHERE comid = %s", (strftime("%Y-%m-%d %H:%M:%S", gmtime()), comid), fetch="none")
