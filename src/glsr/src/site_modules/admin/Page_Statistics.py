# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Statistics.py,v 1.2 2004/08/22 23:23:39 hadfield Exp $
#

MetaData = {"page" : ("stat", None), "params" : ""}

import Template as TemplateHandler
import Config
import Stat
from SiteModuleBE import SiteModuleBE as Parent

def Display():

    page = Page_Statistics()
    page.selectDisplay()

class Page_Statistics(Parent):

    template = Config.Template["admin_statistics"]
    
    def selectDisplay(self):

        self.display()

    def display(self):

        tmpl = TemplateHandler.Template()
        tmpl.compile(
            self.template,
            {"GLSR_URL":		Config.URL,
             "USER_COUNT":		Stat.UserCount(),
             "SESSION_COUNT":		Stat.SessionCount(),
             "SCRIPT_COUNT":		Stat.ScriptCount(),
             "SUBSCRIPT_COUNT":		Stat.SubScriptCount(),
             "CATEGORY_COUNT":		Stat.CategoryCount(),
             "COMMENT_COUNT":		Stat.CommentCount(),
             "DBSIZE":			Stat.DBSize()
	    })
        print tmpl.output()
