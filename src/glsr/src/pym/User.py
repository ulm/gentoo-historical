#!/usr/bin/env python2
#
# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: User.py,v 1.3 2004/07/07 01:39:57 port001 Exp $
#

from time import strftime, gmtime

__modulename__ = "User"
__productname__ = "glsr"

import MySQL
import Config
from GLSRBackend import GLSRBackend as Parent

class User(Parent):

    tablename = Config.MySQL["user_table"]

    def Create(self, details):
        """ Add a new user to the database,
            details contains [alias, fullname, email, type, passwd] """

        details.update({"rank": 0, "joined": strftime("%Y-%m-%d", gmtime())})
        return Parent.Create(self, details)

    
    def Modify(self, details):
        """ Modify user's details,
            details contains [alias, fullname, email, type] and optionally
            'passwd' """

        if details["passwd"] == None:
            del details["passwd"]
        
        return Parent.Modify(self, details.keys(), details)


    def UpdateIP(self, ipaddr):
        """Update lastip for given uid"""

        return Parent.Modify(self, ["lastip"], {"lastip": ipaddr})


    def AliasExists(self, alias):
        """Check for existence of given user alias"""

        return Parent.Exists(self, "alias", alias)
    

    def GetUid(self, alias):
        """Return UID for given alias"""

        result = MySQL.Query("SELECT %s_id FROM %s%s" %
                             (self.tablename, Config.MySQL["prefix"],
                              self.tablename), fetch="one")

        if result == None:
            return False
        else:
            return result["%s_id" % self.tablename]
    

    def GetAlias(self):
        """Return alias for given uid"""

        result = self.GetDetails()
        if result == None:
            return  False
        else:
            return result["%s_alias" % self.tablename]


    def GetType(self):

        result = self.GetDetails()
        
        if result == None:
            return False
        else:
            return result["%s_type" % self.tablename]
    

    def CalcRank(self):
        """ Calculate user rank. A users rank is the total of sum of the
        rank of their scripts. """

        rank = 0
        
        result = MySQL.Query("SELECT rank FROM %s%s WHERE %s_submitter_id = " %
                             (Config.MySQL["prefix"],
                              Config.MySQL["script_table"],
                              Config.MySQL["script_table"]) +
                             "%s", (self.id), fetch="all")

        for tuple in result:
            rank = rank + tuple[0]

        return rank


    def ValidateAlias(self, alias, password):

        result = MySQL.Query("SELECT * FROM %s%s " %
                             (Config.MySQL["prefix"], self.tablename) +
                             "WHERE %s_alias = %%s AND " % self.tablename +
                             "%s_passwd = PASSWORD(%%s)" % self.tablename,
                             (alias, password))

        if len(result) == 0:
            return False
        else:
            return result[0]
    
