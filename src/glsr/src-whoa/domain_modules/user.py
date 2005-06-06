# Copyright 2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = "$Id: user.py,v 1.1 2005/06/06 19:23:37 hadfield Exp $"
__authors__ = ["Scott Hadfield <hadfield@gentoo.org>",
               "Ian Leitch <port001@gentoo.org>"]
__modulename__ = "user"

from setup import config
from core.db.mysql import SQLdb

class User:

    def __init__(self, uid = 0, username = ""):
        
        self.uid = uid
        self.username = username

        self.sql_obj = SQLdb(config.db)
        
        if self.uid == 0 and self.username != "":
            self._update_uid()
        if self.uid != 0 and self.username == "":
            self._update_username()

    def _update_uid(self):
        
        result = self.sql_obj.query(
            "SELECT user_id FROM %suser WHERE " % config.db["prefix"] +
            "user_alias = %s", self.username, fetch="one")

        if result is None:
            self.uid = 0
        else:
            self.uid = result["user_id"]

    def _update_username(self):
        
        result = self.sql_obj.query(
            "SELECT user_alias FROM %suser WHERE " % config.db["prefix"] +
            "user_uid = %s", self.uid, fetch="one")

        if result is None:
            self.username = ""
        else:
            self.username = result["user_alias"]

    def check_password(self, password):
        """Verify that 'password' matches this user's password."""
        
        result = self.sql_obj.query(
            "SELECT user_id FROM %suser WHERE " % config.db["prefix"] +
            "user_alias = %s AND user_passwd = PASSWORD(%s)",
            (self.username, password), fetch="one")
        
        if result is None:
            return False

        return True
                
    def get_lastIP(self):
        """Return the last recorded IP."""
        pass
    
    def logged_in(self):
        """Return True if user is logged in. False otherwise."""
        pass

    def updateIP(self, ip):
        """Update lastip for this user"""

        result = self.sql_obj.query(
            "UPDATE %suser SET " % config.db["prefix"] +
            "user_lastip = %%s WHERE user_id = %s" % self.uid, ip,
            fetch = "none")

    def setup_session(self, remember = False, restrict = False):
        pass

def create(self, details):
    """Add a new user to the database.

    details should contain [alias, fullname, email, type, passwd]
    Returns a User object
    """
    pass
