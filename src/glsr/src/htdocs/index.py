#!/usr/bin/python
#
# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: index.py,v 1.4 2004/07/20 15:23:55 port001 Exp $
#

import os
import sys
import cgi

sys.path.insert(0, "/usr/local/share/glsr/pym/")
sys.path.insert(0, "/usr/local/share/glsr/")
sys.path.insert(0, "/var/www/localhost/htdocs/glsr/pym")
sys.path.insert(0, "/var/www/localhost/htdocs/glsr")

import Config
from Function import start_timer, stop_timer, eval_timer
from Logging import logwrite
import Session as SessionHandler
import Template as TemplateHandler
from User import User
from Validation import CheckPageRequest

import site_modules
from site_modules import *

__modulename__ = "index"

def main():

    t_start = start_timer()

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
        
        if Page_Login.Login_User(form.getvalue("username"),
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

    if Config.HTMLHeadersSent == False:
        print "Content-type:text/html\n\n"
        Config.HTMLHeadersSent = True
    
    AdminHeaderTemplate = TemplateHandler.New()
    AdminHeaderTemplate.Compile(Config.Template["header"],
                                {"GLSR_URL":	Config.URL,
                                 "USER_ALIAS":	alias,
                                 "USER_TYPE":	user_obj.GetType()})
    AdminHeaderTemplate.Print()

    # Display the specified page
    if CheckPageRequest(page) == "Invalid":
        print "Invalid action!"

    found = False
    for Module in site_modules.__all__:

        MetaData = eval(Module + ".MetaData")

        for p in MetaData["page"]:

            if page == p:
                exec "%s.Display(%s)" % (Module, MetaData["params"])
                found = True
                
    if not found:
        print "No such page."


    FooterTemplate = TemplateHandler.New()
    FooterTemplate.Compile(Config.Template["footer"],
			   {"GLSR_VERSION":	Config.Version,
                            "GLSR_URL":		Config.URL,
			    "CONTACT":		Config.Contact})
    FooterTemplate.Print()

    logwrite("Request for page '%s' completed in %.5f(s)" %
             (page, eval_timer(t_start, stop_timer())),
             __modulename__, "Info")

if __name__ == "__main__":
    main()
