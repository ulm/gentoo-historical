#!/usr/bin/python
#
# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: index.py,v 1.2 2004/06/27 23:24:58 hadfield Exp $
#

import os
import sys
import cgi

sys.path.insert(0, "/usr/local/share/glsr/pym")
sys.path.insert(0, "/usr/local/share/glsr/")
sys.path.insert(0, "/var/www/localhost/htdocs/gentoo/src/glsr/src/pym")
sys.path.insert(0, "/var/www/localhost/htdocs/gentoo/src/glsr/src/")

import Config
import Function
import Session as SessionHandler
import Template as TemplateHandler
from User import User
from Validation import CheckPageRequest

import SiteModules
from SiteModules.Global import *
from SiteModules.Admin import *

def main():

    t_start = Function.start_timer()

    form = cgi.FieldStorage()
    page = form.getvalue("page")

    ThisSession = SessionHandler.New()
    user_obj = User()
    
    uid = 0
    sess = 0
    alias = ""
    
    if os.environ.has_key("HTTP_COOKIE"):

        if ThisSession.ValidateCookie(os.environ["HTTP_COOKIE"]):
            (uid, sess) = ThisSession.LoadCookieData(os.environ["HTTP_COOKIE"])

            if not user_obj.SetID(uid):
                uid = 0
            else:
                user_obj.UpdateIP(os.environ['REMOTE_ADDR'])
                ThisSession.UpdateTS(uid, sess)
                alias = user_obj.GetAlias()


    
    if page == "login":
        
        if SiteModules.Global.Page_Login.Login_User(form.getvalue("username"),
                                                    form.getvalue("password")):
            alias = form.getvalue("username")
            uid = user_obj.GetUid(alias)
        
        page = "main"
        
    elif page == "logout":
        if ThisSession.ValidateSession(uid, sess):
            ThisSession.RemoveCookie(sess)
        uid = 0
        alias = ""
        page = "main"

    print "Content-type:text/html\n\n"

    AdminHeaderTemplate = TemplateHandler.New()
    AdminHeaderTemplate.Compile(Config.Template["admin_header"],
                                {"GLSR_URL":	Config.URL,
                                 "USER_ALIAS":	alias,
                                 "USER_TYPE":	user_obj.GetType()})
    AdminHeaderTemplate.Print()

    # Display the specified page
    found = False
    for Module in SiteModules.Admin.__all__:
        
        MetaData = eval(Module + ".MetaData")
        for p in MetaData["page"]:
            
            if page == p:
                exec "%s.Display(%s)" % (Module, MetaData["params"])
                found = True

    if CheckPageRequest(page) == "Invalid":
        print "Invalid action!"
    elif not found:
        print "No such page."
 	#Page_404():

    FooterTemplate = TemplateHandler.New()
    FooterTemplate.Compile(Config.Template["footer"],
			   {"GLSR_VERSION":	Config.Version,
                            "GLSR_URL":		Config.URL,
			    "CONTACT":		Config.Contact})
    FooterTemplate.Print()

    Function.logwrite("Request for page '%s' completed in %.5f(s)" %
                      (page, Function.eval_timer(t_start,
                                                 Function.stop_timer())),
                      "All")

if __name__ == "__main__":
    main()
