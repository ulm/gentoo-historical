# Copyright 2004-2005 Ian Leitch
# Copyright 2004-2005 Scott Hadfield
# Copyright 1999-2005 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = '$Id: Page_Login.py,v 1.14 2005/01/27 04:19:15 port001 Exp $'
__modulename__ = 'Page_Login'

import State
import Config
from User import User
from SiteModule import SiteModule
from GLSRException import Redirect

class Page_Login(SiteModule):

    def init(self):

        self._template = Config.Template['login']
        self._username = self._req.Values.getvalue('username')
        self._password = self._req.Values.getvalue('password')

        self._user_obj = User()
	
    def _login_user(self):

        self._uid = self._user_obj.GetUid(self._username)

        self._user_obj.SetID(self._uid)

        if not self._user_obj.ValidateAlias(self._username, self._password):
            return False

        # Update IP address
        self._user_obj.UpdateIP(self._req.environ['REMOTE_ADDR'])
    
        # Assign uid to current session
        if self._req.Values.has_key('remember'):
            State.ThisSession.assign_uid(self._uid, keep=1)
        else:
            State.ThisSession.assign_uid(self._uid)
    
        return True

    def display(self):

        # Is the user logging in or logging out?
        if self._page == 'perform_login':

            if self._login_user():
                self._alias = self._req.Values.getvalue('username')
                self._uid = self._user_obj.GetUid(self._alias)
        
            raise Redirect('index.py?page=main', __modulename__)
 
        elif self._page == 'logout':
        
            State.ThisSession.remove()        

            self._uid = 0
            self._alias = ''

            raise Redirect('index.py?page=main', __modulename__)

        # we fell through, the user wants to login
        self._tmpl.compile(self._template)
        return self._tmpl 


