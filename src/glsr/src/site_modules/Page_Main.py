# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Main.py,v 1.2 2004/08/22 23:23:39 hadfield Exp $
#

MetaData = {"page" : ("main", None), "params" : ""}

import Template as TemplateHandler
import Session
import Config
from User import User
from Logging import ReturnErrorReports
from SiteModuleBE import SiteModuleBE as Parent

def Display():

    page = Page_Main()
    page.selectDisplay()

class Page_Main(Parent):

    template = Config.Template["main"]
    
    def selectDisplay(self):

        self.display()

    def display(self):

        error_reporting = "True"
        error_report_list = []
        user_online_list = ""
        sess_obj = Session.New()
        sessions = sess_obj.ListSessionsOnline(Config.WhoIsOnlineOffset)

        if len(sessions) == 0:
            user_online_list = "No registered accounts active."
        else:
            for session in sessions:
                user_obj = User(session["session_user_id"])
                user_online_list = "%s %s" % (user_online_list,
                                              user_obj.GetAlias())

        if Config.ErrorReporting == True:
            error_report_list = ReturnErrorReports()
            if error_report_list == False:
                error_reporting = "False"
        else:
            error_reportig = "False"

        if error_reporting == "False":
            error_report_list = []

        tmpl = TemplateHandler.Template()
        tmpl.compile(
            self.template,
            {"GLSR_URL":                Config.URL,
             "USER_ONLINE_LIST":        user_online_list,
             "ERROR_REPORTING":         error_reporting},
            {"ERROR_REPORT_LIST":       error_report_list})
        print tmpl.output()
