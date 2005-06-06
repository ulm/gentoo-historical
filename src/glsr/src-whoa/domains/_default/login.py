# Copyright 2004-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = '$Id: login.py,v 1.1 2005/06/06 19:25:52 hadfield Exp $'
__authors__ = ["Scott Hadfield <hadfield@gentoo.org>",
               "Ian Leitch <port001@gentoo.org>"]
__modulename__ = 'login'

from domains._parent.basepage import BasePage
from core.error import InvalidAction
from domain_modules import user
from setup import config

class Page(BasePage):

    def setup(self):

        if self.action in (None, "", "show"):
            self._prompt()
        elif self.action == "login":
            self._login()
        elif self.action == "logout":
            self._logout()
        else:
            raise InvalidAction

    def _prompt(self):
        """Display the login prompt."""
        
        BasePage.set_template(self, "login.tpl")
        
    def _login(self):

        import os
        
        username = self.request.getvalue("username", "")
        password = self.request.getvalue("password", "")

        user_obj = user.User(username = username)

        if user_obj.logged_in():
            self.redirect("_default/main")
            return

        if not user_obj.check_password(password):
            self.template.param("WARN_MESSAGE", "Invalid username or password")
            self._prompt()
            return

        # Update IP address
        if os.environ.has_key("REMOTE_ADDR"):
            user_obj.updateIP(os.environ["REMOTE_ADDR"])
        else:
            user_obj.updateIP("0.0.0.0")

        # Setup this user's session
        remember = self.request.getvalue("remember", False)
        restrict = self.request.getvalue("restrict", False)            
        user_obj.setup_session(remember, restrict)
        
        self.redirect("_default/main")

    def _logout(self):
        pass
