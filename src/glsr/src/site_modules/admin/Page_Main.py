# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Main.py,v 1.15 2004/12/30 03:05:19 port001 Exp $
#

import State
import Config
from User import User
from Session import Session
from SiteModule import SiteModule
from Admin import optimize_tables, get_optimize_days
from Logging import ReturnErrorReports, FlushErrorReportLog

class Page_Main(SiteModule):

    __modulename__ = 'Page_Main'

    def init(self):

        self._template = Config.Template['admin_main']
    
    def _set_params(self):

        registered_sessions_online = []
        row = 'even'

        (user_list, guest_count) = Session.get_active(Config.WhoIsOnlineOffset)

        if len(user_list) == 0 and guest_count == 0:
            self._tmpl.param('REGISTERED_SESSIONS_ONLINE', [], 'loop')
        else:
            self._tmpl.param('GUEST_SESSIONS_ONLINE', guest_count)
            for user in user_list:
                ThisUser = User(user)
                alias = ThisUser.GetAlias()
                ip = ThisUser.GetLastIP()

                if alias == False:
                    alias = 'N/A'
                elif ip == False:
                    ip = 'N/A'

                registered_sessions_online.append({'row': row,
                                                   'user': alias,
                                                   'ip': ip})
                if row == 'even':
                    row = 'odd'
                else:
                    row = 'even'

            self._tmpl.param('REGISTERED_SESSIONS_ONLINE', registered_sessions_online, 'loop')
	    self._tmpl.param('REGISTERED_SESSIONS_ONLINE_COUNT', len(registered_sessions_online))

        if Config.ErrorReporting == True:
            list_offset = int()
            if self._req.Values.getvalue('error_report_offset') != None:
                list_offset = self._req.Values.getvalue('error_report_offset')
                if str(list_offset).lower() == 'all':
                    list_offset = -1
                else:
                    list_offset = int(list_offset)
            else:
                list_offset = Config.ErrorReportListOffset
            error_report_list = ReturnErrorReports(list_offset)
            if error_report_list == False:
                self._tmpl.param('ERROR_REPORTING', 'False')
                self._tmpl.param('ERROR_REPORT_LIST', [], 'loop')
            else:
                self._tmpl.param('ERROR_REPORTING', 'True')
                self._tmpl.param('ERROR_REPORT_LIST', error_report_list, 'loop')
        else:
            self._tmpl.param('ERROR_REPORTING', 'False')
            self._tmpl.param('ERROR_REPORT_LIST', [], 'loop')

        self._tmpl.param('OPTIMIZE_DAYS', get_optimize_days())
        self._tmpl.param('GLSR_URL', Config.URL)

    def _select_action(self):

        if self._req.Values.getvalue('flush_error_reports'):
            FlushErrorReportLog()

        if self._req.Values.getvalue('optimize_tables'):
            optimize_tables()

    def display(self):

        self._select_action()
        self._set_params()
        self._tmpl.compile(self._template)
        return self._tmpl
