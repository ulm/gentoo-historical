#!/usr/bin/python
#
# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Login.py,v 1.3 2004/09/30 03:09:36 hadfield Exp $
#

import os

import Session as SessionHandler
from User import User
from site_modules import SiteModule

class Page_Login(SiteModule):

    def __init__(self, form, uid = 0):

        #self.pages = ["login", "logout", "*"]
        self.pages = []
        self.page = form.getvalue("page")
        self.form = form
        
        self.username = self.form.getvalue("username")
        self.password = self.form.getvalue("password")
        self.alias = ""
        self.uid = 0
        self.sess = None
        self.user_obj = User()

        self.ThisSession = SessionHandler.New()
        
    def _check_session(self):
        """Checks the session and sets alias, sess and uid if it exists."""

        import os

        if os.environ.has_key("HTTP_COOKIE"):

            if self.ThisSession.ValidateCookie(os.environ["HTTP_COOKIE"]):
                
                (self.uid, self.sess) = self.ThisSession.LoadCookieData(
                    os.environ["HTTP_COOKIE"])

                if not self.user_obj.SetID(self.uid):
                    self.uid = 0
                
                else:
                    self.user_obj.UpdateIP(os.environ['REMOTE_ADDR'])
                    self.ThisSession.UpdateTS(self.uid, self.sess)
                    self.alias = self.user_obj.GetAlias()

    
    def display(self):

        self._check_session()

        # Is the user logging in or logging out?
        if self.page == "login":

            if self._login_user():
                self.alias = self.form.getvalue("username")
                self.uid = self.user_obj.GetUid(self.alias)
        
            self.page = "main"
        
        elif self.page == "logout":
        
            if self.ThisSession.ValidateSession(self.uid, self.sess):
                self.ThisSession.RemoveCookie(self.sess)
        
            self.uid = 0
            self.alias = ""
            self.page = "main"

        return self.page, self.alias, self.uid, self.user_obj.GetType()


    def _login_user(self):

        self.user_obj.SetID(self.user_obj.GetUid(self.username))

        if not self.user_obj.ValidateAlias(self.username, self.password):
            return False

        # Update IP address
        self.user_obj.UpdateIP(os.environ['REMOTE_ADDR'])
    
        # Setup Session Variables
        sess = SessionHandler.New()
        sessid = sess.GenerateSessionID()
        sess.SetCookie(self.user_obj.id, sessid)

        # Update session table in the db
        sess.CreateSession(self.user_obj.id, sessid)
    
        return True
