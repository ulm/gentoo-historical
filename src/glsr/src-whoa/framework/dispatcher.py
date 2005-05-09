#!/usr/bin/python -t
#
# Copyright 2004-2005 Ian Leitch
# Copyright 2004-2005 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#

"""
The main page dispatcher for glsr.

This script simply prints the header, determines the page and calls the
appropriate page handler, and prints out the footer.

It also manages session handling and errors.
"""

__revision__ = '$Id: dispatcher.py,v 1.1 2005/05/09 20:21:31 hadfield Exp $'
__modulename__ = 'dispatcher'

import os
import sys
import cgi

sys.path.insert(0, "../")

#from User import User
#from Session import Session
#from GLSRException import Redirect

import core
from core.template import Template
from setup import config

class _PageDispatch:

    def __init__(self, req, domain):

        self._req = req
        self._domain = domain
        
        self._page = self._req.getvalue('page', None)

        self._user_detail = {"uid": 0,
                             "alias": "",
                             "session": None}

    def check_session(self):

        self._ThisSession.init()

        if self._ThisSession.is_registered:
            self._user_detail['uid'] = self._ThisSession.get_uid()
            self._ThisUser.SetID(self._user_detail['uid'])

            if (str(self._ThisUser.GetLastIP()) != os.environ['REMOTE_ADDR']
                and self._ThisSession.is_restricted() == True):

                self._ThisUser.UpdateIP(os.environ['REMOTE_ADDR'])
                self._ThisSession.remove()
                
                if os.environ.has_key('HTTP_REFERER'):
                    raise Redirect(os.environ['HTTP_REFERER'], __modulename__)
                else:
                    raise Redirect('?page=main', __modulename__)

            self._ThisUser.UpdateIP(os.environ['REMOTE_ADDR'])
            self._user_detail["alias"] = self._ThisUser.GetAlias()
            self._ThisUser.SetLoggedIn()

    def check_access(self):

        deny = True

        if self._domain == "admin":

            if self._ThisUser.IsLoggedIn():
                if self._ThisUser.GetType() == 3:
                    deny = False
            else:
                deny = True

            if deny == True:
                self._send_headers()
                print "Access Denied"
                os.abort()

    def select_module(self):

        domain = __import__("domains.%s" % self._domain, globals(), locals(),
                            [self._domain])
        self._tmpl_page = domain.process(self._page, self._req)
        

    def _send_headers(self):

        print "Content-Type: text/html; charset=utf-8\n\n",


def run(domain = None):
    
    print "Content-type: text/html;\n"
    request = cgi.FieldStorage()

    dispatch = _PageDispatch(request, domain)

    #dispatch.check_session()
    #dispatch.check_access()
    dispatch.select_module()


if __name__ == '__main__':
    run()
