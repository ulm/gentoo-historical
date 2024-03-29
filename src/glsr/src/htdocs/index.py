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

__revision__ = '$Id: index.py,v 1.43 2005/03/09 01:16:31 port001 Exp $'
__modulename__ = 'index'

import os
import sys
import cgi
import __main__

import jon.cgi as cgi
import jon.fcgi as fcgi

sys.path.insert(0, "/var/www/scripts.gentoo.org/gentoo/src/glsr/src/pym")
sys.path.insert(0, "/var/www/scripts.gentoo.org/gentoo/src/glsr/src")

#sys.path.insert(0, "/usr/local/share/glsr/pym/")
#sys.path.insert(0, "/usr/local/share/glsr/")
#sys.path.insert(0, "../pym")
#sys.path.insert(0, "../")

import State
import Config
from User import User
from Session import Session
from Logging import logwrite
from Template import Template
from Error import error_uncaught
from GLSRException import Redirect
from Validation import CheckPageRequest
from Function import start_timer, stop_timer, eval_timer, _Values

class RequestHandler(cgi.Handler):

    def process(self, req):

        req.set_buffering(False)

        # OK, this is pretty hacky but its the best solution I could
        # come up with atm. Rewrite later.
        req.Values = req._Values()
        req.Values._store_params(req.params)

        Dispatcher = _PageDispatch(req)

        Dispatcher.log_request()
        Dispatcher.check_session()
        Dispatcher.check_access()
        Dispatcher.select_module()
        Dispatcher.dispatch_header()
        Dispatcher.dispatch_page()
        Dispatcher.dispatch_footer()
        Dispatcher.log_request_end()

    def traceback(self, req):

        error_uncaught(req)

class _PageDispatch:

    def __init__(self, req):

        self._req = req

        self._tmpl_page = None
        self._show_border = True
        self._t_start = 0
        self._failover = ""
        self._form = self._req.params
        if self._req.params.has_key('page'):
            self._page = self._req.params['page']
        else:
            self._page = None
        self._domain = "user"
        if self._req.params.has_key('domain'):
            if self._req.params['domain'] == 'admin':
                self._domain = 'admin'
				
        self._user_detail = {"uid": 0,
                             "alias": "",
                             "session": None}

        State.UserDetail = self._user_detail
        State.Domian = self._domain
        State.Req = self._req

        self._ThisSession = Session(self._req, self._page)        
        self._ThisUser = User()

        # Make the session instance available to only the modules that need it
        State.ThisSession = self._ThisSession

        self._init_timer()

    def _init_timer(self):

        self._t_start = start_timer() 

    def check_session(self):

        self._ThisSession.init()

        if self._ThisSession.is_registered:
            self._user_detail['uid'] = self._ThisSession.get_uid()
            self._ThisUser.SetID(self._user_detail['uid'])

            if str(self._ThisUser.GetLastIP()) != str(os.environ['REMOTE_ADDR']) \
               and self._ThisSession.is_restricted() == True:

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
                logwrite(
                    "Request for page '%s', domain 'admin'" % self._page +
                    " denied for IP address '%s'" % os.environ["REMOTE_ADDR"],
                    __modulename__, "Warn")
                os.abort()

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
            logwrite("Request fell through to failover page '%s'" %
                      self._page, __modulename__, "Info")

        module_object = eval(matched_module + "(" +
                             "self._req," +
                             "page = self._page," +
                             "uid = self._user_detail[\"uid\"]," +
                             "alias = self._user_detail[\"alias\"]," +
                             "session = self._user_detail[\"session\"])")

        self._tmpl_page = module_object.display()
        self._show_border = module_object.show_border

    def _send_headers(self):

        if State.HTMLHeadersSent == False:
            #self._req.set_encoding("utf-8", "iso-8859-1") # In the docs but not the API????
            self._req.set_header("Content-Type", "text/html; charset=utf-8")
            State.HTMLHeadersSent = True # not needed anymore?

        self._req.output_headers()

    def dispatch_header(self):

        tmpl_str = ""

        self._send_headers()
 
        if self._show_border:
            tmpl_head = Template()
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
            tmpl_foot = Template()
            tmpl_foot.compile(Config.Template["footer"],
                              {"GLSR_VERSION":  Config.Version,
                               "GLSR_URL":      Config.URL,
                               "CONTACT":       Config.Contact})
            print tmpl_foot.output()

    def log_request(self):

        logwrite("Received request for page '%s'" % self._page,
                  __modulename__, "Info")

    def log_request_end(self):

        logwrite("Request for page '%s', " % self._page +
                 "domain '%s' completed in %.5f(s)" %
                 (self._domain, eval_timer(self._t_start,
                                           stop_timer())),
                   __modulename__, "Info")

if __name__ == '__main__':
    setattr(cgi.Request, _Values.__name__, _Values)
    fcgi.Server({fcgi.FCGI_RESPONDER: RequestHandler}).run()
