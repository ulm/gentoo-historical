# Copyright 2004-2005 Ian Leitch
# Copyright 2004-2005 Scott Hadfield
# Copyright 1999-2005 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = '$Id: Session.py,v 1.8 2005/01/26 02:18:55 port001 Exp $'
__modulename__ = 'Session'

import sha
import hmac
from time import time
from random import Random

import Cookie

import Config
import MySQL

MySQLHandler = MySQL.MySQL()

class Session:

    full_tablename = Config.MySQL['prefix'] + Config.MySQL['session_table']
    tablename = Config.MySQL['session_table']

    def __init__(self, req, page):

        self._req = req
        self._page = page

        self.is_registered = False

        self._sid = None
        self._hash = None

    def _gen_hash(self):

        return hmac.new(Config.CookieSecret, self._sid, sha).hexdigest()[:10]

    def _gen_sid(self):

        ran = Random()

        return sha.new(str(time() * ran.randint(0, 10000000000000000000000000)) + \
                       str(self._req.environ.get('UNIQUE_ID'))).hexdigest()[:10]

    def _set_cookie(self):

        bourbon = Cookie.SimpleCookie()

        bourbon['glsrid'] = self._sid + self._hash
	# FIXME: Uncomment the following for releases
        #bourbon["glsrid"]["domain"] = Config.CookieDomain
        #bourbon["glsrid"]["path"] = Config.CookiePath

        if Config.CookieSecure:
            bourbon['glsrid']['secure'] = 1

        self._req.add_header('Set-Cookie', bourbon['glsrid'].OutputString())

    def _remove_cookie(self):

        chocchip = self._req.cookies

        chocchip['glsrid'] = None
        chocchip['glsrid']['max-age'] = 0

        self._req.add_header('Set-Cookie', chocchip['glsrid'].OutputString())
        
    def _remove_session(self):

        MySQLHandler.query("DELETE FROM %s WHERE %s_id = " %
                          (self.full_tablename, self.tablename) + "%s", self._sid,
                          fetch = 'none')

    def _load_cookie(self):

        if self._req.cookies.has_key('glsrid'):
            self._sid = self._req.cookies['glsrid'].value[:10]
            self._hash = self._req.cookies['glsrid'].value[10:]
            return True
        else:
            return False

    def _is_valid(self):

        if self._hash != self._gen_hash():
            self._sid = None
            return False

        return True

    def _update_ts(self):

        MySQLHandler.query("UPDATE %s SET %s_time = UNIX_TIMESTAMP() " %
                           (self.full_tablename, self.tablename) +
                           "WHERE %s_id =" % self.tablename + " %s",
                           self._sid, fetch='none')

    def _save_session(self):
        
        MySQLHandler.query("INSERT INTO %s (%s_id) " % 
                           (self.full_tablename, self.tablename) +
                           "VALUES (%s)", self._sid, fetch='none')

    def _resume(self):

        self._update_ts()

    def _create(self):

        self._sid = self._gen_sid()
        self._hash = self._gen_hash()
        self._save_session()
        self._update_ts()
        self._set_cookie()

    def _is_registered(self):

        result = MySQLHandler.query("SELECT %s_user_id FROM %s " % 
                                    (self.tablename, self.full_tablename) +
                                    "WHERE %s_id = " % self.tablename + "%s",
                                    self._sid, fetch='one')

        if result == None:
            return False
        elif result["%s_user_id" % self.tablename] == 0:
            return False

        return True

    def _has_expired(self):

        result = MySQLHandler.query("SELECT %s_id FROM %s " %
                                    (self.tablename, self.full_tablename) +
                                    "WHERE %s_id =  " % self.tablename +
				    "%s " + "AND %s_keep = 0 " % self.tablename +
                                    "AND %s_time " % self.tablename +
                                    "< UNIX_TIMESTAMP() - %s", (self._sid, Config.SessionTimeout),
                                    fetch='one')

        return result != None

    def init(self):

        if self._load_cookie() and self._is_valid():
            if self._page != 'logout':
                if self._is_registered():
                    self.is_registered = True
                    self._resume()
                elif self._has_expired():
                    self._remove_session()
                    self._create()
                else:
                    self._resume()
        else:
             self._create()

    def assign_uid(self, uid, keep=0):

        MySQLHandler.query("UPDATE %s SET " % self.full_tablename +
                           "%s_user_id " % self.tablename +
                           "= %s, " + 
                           "%s_keep " % self.tablename +
			   "= %s " +
			   "WHERE %s_id" % self.tablename +
                           "= %s", (uid, keep, self._sid), fetch='none')

    def remove(self):

        self._remove_cookie()
        self._remove_session()

    def get_uid(self):

        return MySQLHandler.query("SELECT %s_user_id FROM %s " %
                                  (self.tablename, self.full_tablename) +
                                  "WHERE %s_id = " % self.tablename +
                                  "%s", self._sid, fetch='one')["%s_user_id" %
                                                                self.tablename]
    def get_active(self, grace):

        guest_count = 0
        user_list = []

        result =  MySQLHandler.query("SELECT %s_user_id FROM %s " %
                                     (self.tablename, self.full_tablename) +
                                     "WHERE (UNIX_TIMESTAMP() - %s_time) <= " %
                                     self.tablename + "%s", grace, fetch='all')
        for session in result:
            if session['session_user_id'] == 0:
                guest_count += 1
            else:
                user_list.append(session['session_user_id'])

        return (user_list, guest_count)

    get_active = classmethod(get_active)
