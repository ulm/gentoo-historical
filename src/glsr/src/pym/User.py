#!/usr/bin/env python2
#
# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: User.py,v 1.1 2004/06/04 06:38:33 port001 Exp $
#

from time import strftime, gmtime

__modulename__ = "User"
__productname__ = "glsr"

import MySQL
import Config
import Function
from GLSRBackend import GLSRBackend as Parent

class User(Parent):

    tablename = Config.MySQL["user_table"]

    def Create(self, fullname, alias, passwd, email, type):
        """Add a new user to the database"""

        return Parent.Create(self,
                             {"alias":		alias,
                              "fullname": 	fullname,
                              "passwd":		passwd,
                              "email":		email,
                              "rank":		0,
                              "type":		type,
                              "joined":		strftime("%Y-%m-%d", gmtime())
                              })

    
    def Modify(self, alias, fullname, email, type, password):
        """Modify users details"""

        details = {"alias": alias, "fullname": fullname,
                   "email": email, "type": type}

        if password != None:
            details.update({"passwd": password})
        
        return Parent.Modify(self, ["alias", "fullname", "email", "type",
                                    "passwd"], details)


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
    
