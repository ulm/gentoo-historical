#!/usr/bin/python -t
#
# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: index.py,v 1.20 2004/11/09 18:56:22 port001 Exp $
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

import Config
from User import User
import Logging as LogHandler
import Session as SessionHandler
import Template as TemplateHandler
from GLSRException import GLSRException
from Validation import CheckPageRequest
from Threading import Threader, wait_threads
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
        if os.environ.has_key("HTTP_COOKIE"):
            if self._ThisSession.ValidateCookie(os.environ["HTTP_COOKIE"]):
                (self._user_detail["uid"],
                 self._user_detail["session"]) = self.ThisSession.LoadCookieData(
                                                       os.environ["HTTP_COOKIE"])
                # OK, we have a returning user.
                self._ThisSession.UpdateTS(self._user_detail["uid"], 
                                           self._user_detail["session"])
                self._ThisUser.SetID(self._user_detail["uid"])
                self._ThisUser.UpdateIP(os.environ['REMOTE_ADDR'])
                # TODO: check here if this IP matches their last one,
                # if not, make them log back in.
                self._user_detail["alias"] = self._ThisUser.GetAlias()
                self._ThisUser.SetLoggedIn()

    def _load_module(self, module):

        module_object = None

        if self._domain == "admin":
            module_object = __import__("site_modules.admin.%s" % module, globals(), locals(), [module])
        else:
            module_object = __import__("site_modules.%s" % module, globals(), locals(), [module])

        setattr(__main__, module, vars(module_object)[module])

    def select_module(self):

        module_list = []
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
                LogHandler.logwrite("Request for page '%s', domain 'admin' denied from IP '%s'$
                                    (self._page, os.environ["REMOTE_ADDR"]),
                                     __modulename__, "Warn")
                sys.exit(0)

            import site_modules.admin
            self._failover = site_modules.admin.failover

            for module in site_modules.admin.__all__:
                module_list.append(module)
                Threader(self._load_module, module)
        else:
            import site_modules
            self._failover = site_modules.failover

            for module in site_modules.__all__:
                module_list.append(module)
                Threader(self._load_module, module)
        
        wait_threads()

        for module in module_list:

            module_object = eval("""%s(form = self._form, uid = self._user_detail["uid"], alias = self._user_detail["alias"], session = self._user_detail["session"])""" % module)

            try:
                for mod_page in module_object.pages:
                    if self._page == mod_page:
                        try:
                            #verifyFormInputs(self._form, module_object.required)
                            self._tmpl_page = module_object.display()
                            self._show_border = module_object.show_border
                            raise 'PageFound'

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

                        #except Exception, errmsg:
                        #    LogHandler.err(errmsg, module_object.__modulename__)
                        #    sys.exit(0)

            except 'PageFound':
                break

        if self._tmpl_page == None:
            failover_page = eval("""%s(form = self._form, alias = self._user_detail["alias"])""" %
                                                 self._failover)
            self._tmpl_page = failover_page.display()
        
        if self._tmpl_page == "nodisplay":
            sys.exit(0)

    def _send_headers(self):

        if Config.HTMLHeadersSent == False:
            print "Content-type:text/html\n\n",
            Config.HTMLHeadersSent = True

    def dispatch_header(self):

        self._send_headers()
 
        if self._show_border:
            tmpl_head = TemplateHandler.Template()
            tmpl_head.compile(Config.Template["header"],
                          {"GLSR_URL":          Config.URL,
                           "USER_ALIAS":	self._user_detail["alias"]})
            print tmpl_head.output()

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

        LogHandler.logwrite("Request for page '%s', domain '%s' completed in %.5f(s)" %
                            (self._page, self._domain, eval_timer(self._t_start, stop_timer())),
                            __modulename__, "Info")

if __name__ == "__main__":

    Dispatcher = PageDispatch()

    Dispatcher.check_session()
    Dispatcher.select_module()
    Dispatcher.dispatch_header()
    Dispatcher.dispatch_page()
    Dispatcher.dispatch_footer()
    Dispatcher.log_request()
