# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Statistics.py,v 1.3 2004/12/16 15:43:31 port001 Exp $
#

import Stat
import Config
from site_modules import SiteModule

class Page_Statistics(SiteModule):

    __modulename__ = "Page_Statistics"

    def __init__(self, **args):

        self.pages = ["stat"]
        self.template = Config.Template["admin_statistics"]

    def _set_params(self):

        self.tmpl.param("GLSR_URL", Config.URL)
        self.tmpl.param("USER_COUNT", Stat.UserCount())
        self.tmpl.param("SESSION_COUNT", Stat.SessionCount())
        self.tmpl.param("SCRIPT_COUNT", Stat.ScriptCount())
        self.tmpl.param("SUBSCRIPT_COUNT", Stat.SubScriptCount())
        self.tmpl.param("CATEGORY_COUNT", Stat.CategoryCount())
        self.tmpl.param("COMMENT_COUNT", Stat.CommentCount())
        self.tmpl.param("DBSIZE", Stat.DBSize())

    def display(self):

        self._set_params()
        self.tmpl.compile(self.template)
        return self.tmpl
