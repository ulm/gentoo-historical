# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Main.py,v 1.11 2004/11/14 23:34:23 port001 Exp $
#

import Config
import Session
from User import User
from site_modules import SiteModule, Redirect
from Admin import optimize_tables, get_optimize_days
from Logging import ReturnErrorReports, FlushErrorReportLog

class Page_Main(SiteModule):

    __modulename__ = "Page_Main"

    def __init__(self, **args):

        self.pages = [None, "main"]
        self.form = args["form"]
        self.page = self.form.getvalue("page")
        self.template = Config.Template["admin_main"]
    
        self.ThisSession = Session.New() 
    
    def _set_params(self):

        users_online_list = []
        row = "even"

        # Count active users
        active_sessions = self.ThisSession.ListSessionsOnline(Config.WhoIsOnlineOffset)

        if len(active_sessions) == 0:
            self.tmpl.param("USERS_ONLINE", "False")
            self.tmpl.param("USERS_ONLINE_LIST", [], "loop")
        else:
            self.tmpl.param("USERS_ONLINE", "True")
            for session in active_sessions:
                ThisUser = User(session["session_user_id"])
                alias = ThisUser.GetAlias()
                ip = ThisUser.GetLastIP()

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

            self.tmpl.param("USERS_ONLINE_LIST", users_online_list, "loop")

        if Config.ErrorReporting == True:
            list_offset = int()
            if self.form.has_key("error_report_offset"):
                list_offset = self.form.getvalue("error_report_offset")
                if str(list_offset).lower() == "all":
                    list_offset = -1
                else:
                    list_offset = int(list_offset)
            else:
                list_offset = Config.ErrorReportListOffset
            error_report_list = ReturnErrorReports(list_offset)
            if error_report_list == False:
                self.tmpl.param("ERROR_REPORTING", "False")
                self.tmpl.param("ERROR_REPORT_LIST", [], "loop")
            else:
                self.tmpl.param("ERROR_REPORTING", "True")
                self.tmpl.param("ERROR_REPORT_LIST", error_report_list, "loop")
        else:
            self.tmpl.param("ERROR_REPORTING", "False")
            self.tmpl.param("ERROR_REPORT_LIST", [], "loop")

        self.tmpl.param("OPTIMIZE_DAYS", get_optimize_days())
        self.tmpl.param("GLSR_URL", Config.URL)

    def _select_action(self):

        if self.form.getvalue("flush_error_reports"):
            FlushErrorReportLog()

        if self.form.getvalue("optimize_tables"):
            optimize_tables()

    def display(self):

        self._select_action()
        self._set_params()
        self.tmpl.compile(self.template)
        return self.tmpl
