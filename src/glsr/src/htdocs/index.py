#!/usr/bin/python -t
#
# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: index.py,v 1.11 2004/11/04 00:14:53 port001 Exp $
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

sys.path.insert(0, "/usr/local/share/glsr/pym/")
sys.path.insert(0, "/usr/local/share/glsr/")
sys.path.insert(0, "../pym")
sys.path.insert(0, "../")

from Error import exception_handler
sys.excepthook = exception_handler

from Function import stderrRedirect
sys.stderr = stderrRedirect()

import Config
from Function import start_timer, stop_timer, eval_timer
from GLSRException import GLSRException
import Logging as LogHandler
import Session as SessionHandler
import Template as TemplateHandler
from User import User
from Validation import CheckPageRequest

import site_modules
from site_modules import Redirect
from site_modules import *

def main():

    uid = 0
    alias = ""
    session = None

    tmpl_page = None
    show_border = True

    ThisSession = SessionHandler.New()
    ThisUser = User()

    t_start = start_timer()

    #print "Content-type:text/html\n\n",
    form = cgi.FieldStorage()
    page = form.getvalue("page")

    # Does the user have a cookie for me? Load and eat.
    if os.environ.has_key("HTTP_COOKIE"):
        if ThisSession.ValidateCookie(os.environ["HTTP_COOKIE"]):
            (uid, session) = self.ThisSession.LoadCookieData(
                                          os.environ["HTTP_COOKIE"])
            # OK, we have a returning user.
            ThisSession.UpdateTS(uid, session)
            ThisUser.SetID(uid)
            ThisUser.UpdateIP(os.environ['REMOTE_ADDR'])
            alias = ThisUser.GetAlias()

    for Module in site_modules.__all__:

        module_object = eval("%s.%s(form, uid)" % (Module, Module))

        try:
            for mod_page in module_object.pages:
                if page == mod_page:
                    try:
                        #verifyFormInputs(form, module_object.required)
                        tmpl_page = module_object.display()
                        show_border = module_object.show_border
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

    if tmpl_page == None:
        failover = eval("%s.%s(form, username)" %
                        (site_modules.failover, site_modules.failover))
        tmpl_page = failover.display()
        
    if tmpl_page == "nodisplay":
        sys.exit(0)

    if Config.HTMLHeadersSent == False:
        print "Content-type:text/html\n\n",
        Config.HTMLHeadersSent = True

    if show_border:
        tmpl_head = TemplateHandler.Template()
        tmpl_head.compile(Config.Template["header"],
                          {"GLSR_URL":          Config.URL,
                           "USER_ALIAS":	alias})
        print tmpl_head.output()

    print tmpl_page.output()

    if show_border:
        tmpl_foot = TemplateHandler.Template()
        tmpl_foot.compile(Config.Template["footer"],
                          {"GLSR_VERSION":	Config.Version,
                           "GLSR_URL":		Config.URL,
                           "CONTACT":		Config.Contact})
        print tmpl_foot.output()

    LogHandler.logwrite("Request for page '%s' completed in %.5f(s)" %
                        (page, eval_timer(t_start, stop_timer())),
                        __modulename__, "Info")

if __name__ == "__main__":

    main()
