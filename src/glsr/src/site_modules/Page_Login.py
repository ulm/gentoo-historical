#!/usr/bin/python
#
# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Login.py,v 1.9 2004/12/25 01:36:24 port001 Exp $
#

import os

import State
import Config
from User import User
import Session as SessionHandler
from site_modules import SiteModule, Redirect

class Page_Login(SiteModule):

    def __init__(self, req, **args):

        self.req = req       
        self.page = args['page']
        self.template = Config.Template["login"]
        if self.req.params.has_key('username'):
            self.username = self.req.params['username']
        else:
            self.username = None
        if self.req.params.has_key('password'):
            self.password = self.req.params['password']
        else:
            self.password = None
        self.alias = args["alias"]
        self.uid = args["uid"]
        self.session = args["session"]

        self.user_obj = User()
        self.ThisSession = SessionHandler.New()
        
    def display(self):

        # Is the user logging in or logging out?
        if self.page == "perform_login":

            if self._login_user():
                self.alias = self.req.params["username"]
                self.uid = self.user_obj.GetUid(self.alias)
        
            raise Redirect, "index.py?page=main"
 
        elif self.page == "logout":
        
            if self.ThisSession.ValidateSession(self.uid, self.session):
                self.ThisSession.RemoveCookie(self.session)        

            self.uid = 0
            self.alias = ""

            raise Redirect, "index.py?page=main"

        # we fell through, the user wants to login
        self.tmpl.compile(self.template)
        return self.tmpl 

    def _login_user(self):

        uid = self.user_obj.GetUid(self.username)

        self.user_obj.SetID(uid)

        if not self.user_obj.ValidateAlias(self.username, self.password):
            return False

        # Update IP address
        self.user_obj.UpdateIP(os.environ['REMOTE_ADDR'])
    
        # Assign uid to current session
        State.ThisSession.assign_uid(uid)
    
        return True
