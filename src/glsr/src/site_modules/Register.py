# Copyright 2005 Ian Leitch
# Copyright 2005 Scott Hadfield
# Copyright 1999-2005 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Register.py,v 1.1 2005/01/26 03:59:01 hadfield Exp $
#

import Config
from SiteModule import SiteModule, Redirect
from User import User

__modulename__ = 'Register'

class Register(SiteModule):

    def init(self):

        self._template = Config.Template['registration']

    def _set_params(self):

        self._tmpl.param("GLSR_URL", Config.URL)

    def _check_passwd(self, password1, password2):

        if password1 != password2:
            # An error should be raised here.
            return False

        return True

    def _check_alias(self, alias):

        import re

        # Verify that there are no invalid username characters.
        if re.sub(r'[\w\-]', "", alias) != "":
            return False

        # Check for other users with that username
        user_obj = User()
        if user_obj.AliasExists(alias):
            return False

        return True

    def _check_email(self, email):

        import re
        local_part = r'[\w&\'\.\-\+]+'
        domain = r'[a-z0-9\-]+(\.[a-z0-9\-]+)*\.[a-z]+'

        if re.match(r'^%s@%s$' % (local_part, domain), email, re.S | re.I):
            return True

        return False

    def _check_required(self):

        alias = self._req.Values.getvalue("alias")
        email = self._req.Values.getvalue("email")
        password1 = self._req.Values.getvalue("password1")
        password2 = self._req.Values.getvalue("password2")

        if None in (alias, email, password1, password2):
            # raise error here because one of the required fields wasn't filled.
            raise

        self._check_alias(alias)
        self._check_email(email)
        self._check_passwd(password1, password2)

        return True
    
    def _action_create(self):

        from os import environ

        if environ.has_key("REMOTE_ADDR"):
            lastip = environ["REMOTE_ADDR"]
        else:
            lastip = "0.0.0.0"
        
        user_obj = User()

        # Verify valid username and password as well as required fields
        # Verify the required fields
        self._check_required()
        
        user_obj.Create(
            {"alias":           self._req.Values.getvalue("alias"),
             "fullname":        self._req.Values.getvalue("fullname"),
             "email":           self._req.Values.getvalue("email"),
             "type":            0,
             "passwd":          self._req.Values.getvalue("password1"),
             "lastip":          lastip,
             "location":        self._req.Values.getvalue("location"),
             "website":         self._req.Values.getvalue("website"),
             "language":        self._req.Values.getvalue("language")
             })

    def _select_action(self):

        if self._page == 'create_user':
            self._action_create()
        
    
    def display(self):

        self._select_action()

        if self._page == 'create_user':
            raise Redirect, "index.py?page=login"
        
        self._set_params()
        self._tmpl.compile(self._template)
        return self._tmpl
