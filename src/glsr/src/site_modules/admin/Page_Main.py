# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Main.py,v 1.4 2004/07/09 21:09:10 port001 Exp $
#

MetaData = {"page" : ("main", None), "params" : "form"}

import Template as TemplateHandler
import Session
import Config
from User import User
from SiteModuleBE import SiteModuleBE as Parent

def Display(form):

    page = Page_Main()
    page.selectDisplay(form)

class Page_Main(Parent):

    template = Config.Template["admin_main"]
    
    def selectDisplay(self, form):

        # Not sure if this is the right place for this...
        flush = form.getvalue("error_reports")
        if flush:
            FlushErrorReportLog()

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
                                                                                                                              
        tmpl = TemplateHandler.New()
        tmpl.Compile(
            self.template,
            {"GLSR_URL":                Config.URL,
             "USER_ONLINE_LIST":        user_online_list,
             "ERROR_REPORTING":         error_reporting},
            {"ERROR_REPORT_LIST":       error_report_list})
        tmpl.Print()
