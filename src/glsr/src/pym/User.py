# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: User.py,v 1.11 2005/01/26 03:59:01 hadfield Exp $
#

__modulename__ = "User"

from time import strftime, gmtime

from MySQL import MySQL
import Config
from GLSRBackend import GLSRBackend as Parent

MySQLHandler = MySQL()

class User(Parent):

    _logged_in = False
    tablename = Config.MySQL["user_table"]

    def Create(self, details):
        """ Add a new user to the database,
            details contains [alias, fullname, email, type, passwd] """

        passwd = details["passwd"]
        del details["passwd"]
        details.update({"rank": 0, "joined": strftime("%Y-%m-%d", gmtime())})
        return Parent.Create(self, details, encrypt = {"passwd": passwd})

    
    def Modify(self, details):
        """ Modify user's details,
            details contains [alias, fullname, email, type] and optionally
            'passwd' """

        if details["passwd"] == None:
            del details["passwd"]
            passwd = details["passwd"]

            return Parent.Modify(self, details, encrypt = {"passwd": passwd})
        else:
            return Parent.Modify(self, details)


    def UpdateIP(self, ipaddr):
        """Update lastip for given uid"""

        return Parent.Modify(self, {"lastip": ipaddr})


    def AliasExists(self, alias):
        """Check for existence of given user alias"""

        return Parent.Exists(self, "alias", alias)
    

    def GetUid(self, alias):
        """Return UID for given alias"""

        result = MySQLHandler.query("SELECT %s_id FROM %s%s WHERE %s_alias=" %
                                   (self.tablename, Config.MySQL["prefix"],
                                    self.tablename, self.tablename) +
                                    "%s", alias, fetch="one")

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
        
        result = MySQLHandler.query(
            "SELECT rank FROM %s%s WHERE %s_submitter_id = " %
            (Config.MySQL["prefix"], Config.MySQL["script_table"],
             Config.MySQL["script_table"]) + "%s", (self.id), fetch="all")

        for tuple in result:
            rank = rank + tuple[0]

        return rank

    def ValidateAlias(self, alias, password):

        result = MySQLHandler.query(
            "SELECT * FROM %s%s " % (Config.MySQL["prefix"], self.tablename) +
            "WHERE %s_alias = %%s AND " % self.tablename +
            "%s_passwd = PASSWORD(%%s)" % self.tablename, (alias, password))

        if len(result) == 0:
            return False
        else:
            return result[0]
    
    def GetLastIP(self):
        """ Return the last recorded IP for the given uid """

        result = self.GetDetails()

        if result == None:
            return False
        else:
            return result["%s_lastip" % self.tablename]

    def SetLoggedIn(self):

        self._logged_in = True

    def SetLoggedOut(self):

        self._logged_in = False

    def IsLoggedIn(self):

        return self._logged_in
