#!/usr/bin/python -t
#
# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: index.py,v 1.28 2004/12/18 22:05:18 port001 Exp $
#

"""
The main page dispatcher for glsr.

This script simply prints the header, determines the page and calls the
appropriate page handler, and prints out the footer.

It also manages session handling and errors.
"""

__modulename__ = "index"

import os
import sys
import cgi
import __main__

sys.path.insert(0, "/usr/local/share/glsr/pym/")
sys.path.insert(0, "/usr/local/share/glsr/")
sys.path.insert(0, "../pym")
sys.path.insert(0, "../")

from Error import exception_handler
sys.excepthook = exception_handler

from Function import stderr_redirect
sys.stderr = stderr_redirect()

import State
import Config
from User import User
import Logging as LogHandler
import Session as SessionHandler
import Template as TemplateHandler
from GLSRException import GLSRException
from Validation import CheckPageRequest
from Function import start_timer, stop_timer, eval_timer

from site_modules import Redirect

class PageDispatch:

    def __init__(self):

        self._tmpl_page = None
        self._show_border = True
        self._t_start = 0
        self._failover = ""
        self._form = cgi.FieldStorage()
        self._page = self._form.getvalue("page")
        self._domain = "user"
        if self._form.getvalue("domain") == "admin":
            self._domain = "admin"
        self._user_detail = {"uid": 0,
                             "alias": "",
                             "session": None}

        self._ThisSession = SessionHandler.New()
        self._ThisUser = User()

        self._init_timer()

    def _init_timer(self):

        self._t_start = start_timer() 

    def check_session(self):

        # Does the user have a cookie for me? Load and eat.
        if (os.environ.has_key("HTTP_COOKIE") and
            self._ThisSession.ValidateCookie(os.environ["HTTP_COOKIE"])):
            
            (self._user_detail["uid"], self._user_detail["session"]) = (
                self._ThisSession.LoadCookieData(os.environ["HTTP_COOKIE"]))
                
            # OK, we have a returning user.
            self._ThisSession.UpdateTS(self._user_detail["uid"], 
                                       self._user_detail["session"])
            self._ThisUser.SetID(self._user_detail["uid"])
            self._ThisUser.UpdateIP(os.environ['REMOTE_ADDR'])
            
            # TODO: check here if this IP matches their last one,
            # if not, make them log back in.
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
                LogHandler.logwrite(
                    "Request for page '%s', domain 'admin'" % self._page +
                    "denied for IP address '%s'" % os.environ["REMOTE_ADDR"],
                    __modulename__, "Warn")
                sys.exit(0) 

    def _load_module(self, module):

        module_object = None

        if self._domain == "admin":
            module_object = __import__("site_modules.admin.%s" % module,
                                       globals(), locals(), [module])
        else:
            module_object = __import__("site_modules.%s" % module,
                                       globals(), locals(), [module])

        setattr(__main__, module, vars(module_object)[module])

    def select_module(self):

        page_metadata = None
        page_matched = False
        matched_module = ""

        if self._domain == "admin":
            import site_modules.admin
            self._failover = site_modules.admin.failover
            page_metadata = site_modules.admin.__all__
        else:
            import site_modules
            self._failover = site_modules.failover
            page_metadata = site_modules.__all__

        for module in page_metadata:
            if self._page in page_metadata[module]:
                matched_module = module
                self._load_module(matched_module)
                page_matched = True
                break

        if not page_matched:
            matched_module = self._failover["module"]
            self._load_module(matched_module)
            self._page = self._failover["page"]
            LogHandler.logwrite("Request fell through to failover page '%s'" %
                                 self._page, __modulename__, "Info")

        module_object = eval(matched_module + "(" +
                             "form = self._form," +
                             "uid = self._user_detail[\"uid\"]," +
                             "alias = self._user_detail[\"alias\"]," +
                             "session = self._user_detail[\"session\"])")

        try:
            self._tmpl_page = module_object.display()
            self._show_border = module_object.show_border
                                                                                                    
        except Redirect, location_str:
            print "Location: %s\n\n" % location_str
            sys.exit(0)
                                                                                                    
        except GLSRException, error:
            output_str = error.__str__()
            output_str = output_str.replace("\n", "<br />")
            output_str = output_str.replace(" ", "&nbsp;")
            LogHandler.err(output_str,
                           module_object.__modulename__)
            sys.exit(0)

    def _send_headers(self):

        if State.HTMLHeadersSent == False:
            print "Content-type:text/html\n\n",
            State.HTMLHeadersSent = True

    def dispatch_header(self):

        tmpl_str = ""

        self._send_headers()
 
        if self._show_border:
            tmpl_head = TemplateHandler.Template()
            if self._domain == "admin":
                tmpl_str = "admin_header"
            else:
                tmpl_str = "header"

            tmpl_head.compile(Config.Template[tmpl_str],
                          {"GLSR_URL":          Config.URL,
                           "USER_ALIAS":        self._user_detail["alias"],
                           "USER_ID":           self._user_detail["uid"]})
            print tmpl_head.output()
        
        State.HeaderTmplSent = True

    def dispatch_page(self):

        print self._tmpl_page.output()

    def dispatch_footer(self):

        if self._show_border:
            tmpl_foot = TemplateHandler.Template()
            tmpl_foot.compile(Config.Template["footer"],
                              {"GLSR_VERSION":	Config.Version,
                               "GLSR_URL":	Config.URL,
                               "CONTACT":	Config.Contact})
            print tmpl_foot.output()

    def log_request(self):

        LogHandler.logwrite("Received request for page '%s'" % self._page,
                             __modulename__, "Info")

    def log_request_end(self):

        LogHandler.logwrite("Request for page '%s', " % self._page +
                            "domain '%s' completed in %.5f(s)" %
                            (self._domain, eval_timer(self._t_start,
                                                      stop_timer())),
                            __modulename__, "Info")

if __name__ == "__main__":

    Dispatcher = PageDispatch()

    Dispatcher.log_request()
    Dispatcher.check_session()
    Dispatcher.check_access()
    Dispatcher.select_module()
    Dispatcher.dispatch_header()
    Dispatcher.dispatch_page()
    Dispatcher.dispatch_footer()
    Dispatcher.log_request_end()
