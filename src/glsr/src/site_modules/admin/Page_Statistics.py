# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Statistics.py,v 1.5 2004/12/30 03:05:19 port001 Exp $
#

import Stat
import Config
from SiteModule import SiteModule

class Page_Statistics(SiteModule):

    __modulename__ = 'Page_Statistics'

    def init(self):

        self._template = Config.Template['admin_statistics']

    def _set_params(self):

        self._tmpl.param('GLSR_URL', Config.URL)
        self._tmpl.param('USER_COUNT', Stat.UserCount())
        self._tmpl.param('SESSION_COUNT', Stat.SessionCount())
        self._tmpl.param('SCRIPT_COUNT', Stat.ScriptCount())
        self._tmpl.param('SUBSCRIPT_COUNT', Stat.SubScriptCount())
        self._tmpl.param('CATEGORY_COUNT', Stat.CategoryCount())
        self._tmpl.param('COMMENT_COUNT', Stat.CommentCount())
        self._tmpl.param('DBSIZE', Stat.DBSize())

    def display(self):

        self._set_params()
        self._tmpl.compile(self._template)
        return self._tmpl
