#!/usr/bin/python
#
# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Login.py,v 1.5 2004/11/04 00:14:53 port001 Exp $
#

import os

import Config
from User import User
import Session as SessionHandler
from site_modules import SiteModule

class Page_Login(SiteModule):

    def __init__(self, form, uid = 0):

        self.pages = ["login", "perform_login", "logout"]
        self.page = form.getvalue("page")
        self.form = form
        
        self.template = Config.Template["login"]
        self.username = self.form.getvalue("username")
        self.password = self.form.getvalue("password")
        self.alias = ""
        self.uid = uid
        self.sess = None
        self.user_obj = User()

        self.ThisSession = SessionHandler.New()
        
    def display(self):

        # Is the user logging in or logging out?
        if self.page == "perform_login":

            if self._login_user():
                self.alias = self.form.getvalue("username")
                self.uid = self.user_obj.GetUid(self.alias)
        
            self.template = Config.Template["main"]
 
        elif self.page == "logout":
        
            if self.ThisSession.ValidateSession(self.uid, self.sess):
                self.ThisSession.RemoveCookie(self.sess)
            # Get session by uid first then remove cookie
            # or get session from index..        

            self.uid = 0
            self.alias = ""
            self.template = Config.Template["main"]

        # we fell through, the user wants to login
        self.tmpl.compile(self.template)
        return self.tmpl 

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
