# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Main.py,v 1.7 2004/08/22 23:23:39 hadfield Exp $
#

MetaData = {"page" : ("main", None), "params" : "form"}

import Template as TemplateHandler
import Session
import Config
from User import User
from SiteModuleBE import SiteModuleBE as Parent
from Logging import ReturnErrorReports, FlushErrorReportLog

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
        users_online = "True"
        users_online_list = []
        row = "even"

        sess_obj = Session.New()
        sessions = sess_obj.ListSessionsOnline(Config.WhoIsOnlineOffset)

        if len(sessions) == 0:
            users_online = "False"
        else:
            for session in sessions:
                user_obj = User(session["session_user_id"])
                alias = user_obj.GetAlias()
                ip = user_obj.GetLastIP()                

                if alias == False:
                    alias = "N/A"
                elif ip == False:
                    ip = "N/A"

                users_online_list.append({"row": row,
                                          "user": alias,
                                          "ip": ip})
                if row == "even":
                    row = "odd"
                else:
                    row = "even"

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
             "USERS_ONLINE":       	users_online,
             "ERROR_REPORTING":         error_reporting},
            {"ERROR_REPORT_LIST":       error_report_list,
	     "USERS_ONLINE_LIST":       users_online_list})
        print tmpl.output()
