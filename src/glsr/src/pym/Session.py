# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Session.py,v 1.1 2004/06/04 06:38:36 port001 Exp $
#

__modulename__ = "Session"

import MySQL
import Config


class New:

    full_tablename = Config.MySQL["prefix"] + Config.MySQL["session_table"]
    tablename = Config.MySQL["session_table"]
    
    def GenerateSessionID(self):

        # This could be done a lot faster, no need to fetch the whole table. 

        from random import Random, random
    
        sessid = ""
        i = 0
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
        result = MySQL.Query("SELECT %s_id FROM %s " %
                             (self.tablename, self.full_tablename),
                             fetch="all")
        ran = Random()
        
	while 1:
            num = ran.randint(0, 10000000000000000000000000)
    
            while i < 30:
                sessid = sessid + ran.choice(chars + str(num))
                i += 1
	    
	    if sessid not in result:
	        break
    
        return sessid

    def SessionIDExists(self, uid, sessid):

        result = MySQL.Query("SELECT %s_id FROM %s WHERE %s_id = " %
                             (self.tablename, self.full_tablename,
                              self.tablename) +
                             "%s", sessid.value, fetch="one")

        return result != None

    def SetCookie(self, uid, sessid):

        import Cookie
        import Config
        
        bourbon = Cookie.SimpleCookie()

        bourbon["glsr_sessid"] = sessid
        #bourbon["glsr_sessid"]["domain"] = Config.CookieDomain
        #bourbon["glsr_sessid"]["path"] = Config.CookiePath
        if Config.CookieSecure == "Yes":
            bourbon["glsr_sessid"]["secure"] = 1
    
        bourbon["glsr_uid"] = uid
        #bourbon["glsr_uid"]["domain"] = Config.CookieDomain
        #bourbon["glsr_uid"]["path"] = Config.CookiePath
        if Config.CookieSecure == "Yes":
            bourbon["glsr_uid"]["secure"] = 1

        print bourbon

    def RemoveCookie(self, sessid):

        import Cookie
    
        chocchip = Cookie.SimpleCookie()
        
        self.DeleteSession(sessid)
        
        # Who the fuck designed cookies? This is fucking stupid! 
        chocchip["glsr_sessid"] = None
        chocchip["glsr_sessid"]["max-age"] = 0
	chocchip["glsr_uid"] = None
        chocchip["glsr_uid"]["max-age"] = 0

        print chocchip

    def DeleteSession(self, sessid):
    
        MySQL.Query("DELETE FROM %s WHERE %s_id = " %
                    (self.full_tablename, self.tablename) + "%s", sessid,
                    fetch = "none")

        return True

    
    def ValidateCookie(self, HTTP_COOKIE):
        """ Checks that the COOKIE matches valid glsr cookie data """

        import Cookie, sys
        
        fudge = Cookie.SimpleCookie(HTTP_COOKIE)

        if (not fudge.has_key("glsr_uid") or not
            fudge.has_key("glsr_sessid")):
            return False

        if (not self.ValidateCookieData(fudge["glsr_uid"].value,
                                        fudge["glsr_sessid"].value)):
            return False

        if (not self.ValidateSession(fudge["glsr_uid"].value,
                                     fudge["glsr_sessid"].value)):
            return False

        # Check the database for a matchine session
        if not self.SessionIDExists(fudge["glsr_uid"], fudge["glsr_sessid"]):
            return False

        return True

    
    def ValidateCookieData(self, uid, sessid):

        import re
    
        sessid_regex = "^[\da-zA-Z]{30}$"
        uid_regex = "^[\d]{1,5}$"
    
        p_sessid = re.compile(sessid_regex)
        p_uid = re.compile(uid_regex)

        o_sessid =  p_sessid.match(sessid)
        if not o_sessid:
	    return "Invalid"
        o_uid = p_uid.match(str(uid))
        if not o_uid:
	    return "Invalid"

        return "Valid"

    def LoadCookieData(self, HTTP_COOKIE):

        import Cookie

	custardcream = Cookie.SimpleCookie()
	custardcream.load(HTTP_COOKIE)

	return (custardcream["glsr_uid"].value,
                custardcream["glsr_sessid"].value)

    def ValidateSession(self, uid, sessid):
    
        # Delete all old sessions
        MySQL.Query("DELETE FROM %s WHERE " % self.full_tablename +
                    "(%s_user_id = %%s AND " % self.tablename +
                    "%s_id != %%s) OR " % self.tablename +
                    "%s_time < UNIX_TIMESTAMP() - %%s" % self.tablename,
                    (uid, sessid, Config.SessionTimeOut),
                    fetch = "none")
        
        result = MySQL.Query("SELECT * FROM %s WHERE %s_user_id = " %
                             (self.full_tablename, self.tablename) + "%s", uid,
                             fetch="one")

        return result != None

    def CreateSession(self, uid, sessid):

        # Check to see if the session is new, or just needs updating
        if self.ValidateSession(uid, sessid):
            self.UpdateTS(uid, sessid)
        else:
            MySQL.Query("INSERT INTO %s (%s_id, %s_user_id, %s_time) " %
                        (self.full_tablename, self.tablename, self.tablename,
                         self.tablename) +
                        "VALUES (%s, %s, UNIX_TIMESTAMP())", (sessid, uid),
                        fetch="none")
            
    def UpdateTS(self, uid, sessid):
        """ Update the sessions timestamp """
        
        MySQL.Query("UPDATE %s SET %s_time = UNIX_TIMESTAMP() " %
                    (self.full_tablename, self.tablename) +
                    "WHERE %s_id = %%s AND %s_user_id = " %
                    (self.tablename, self.tablename) +
                    "%s", (sessid, uid), fetch="none")

    def ListSessionsOnline(self, grace):

        return MySQL.Query("SELECT %s_id, %s_user_id FROM %s " %
                           (self.tablename, self.tablename,
                            self.full_tablename) +
                           "WHERE (UNIX_TIMESTAMP() - %s_time) <= " %
                           self.tablename + "%s", grace, fetch="all")
