# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Search.py,v 1.4 2004/11/04 00:59:22 port001 Exp $
#

import Config
from site_modules import SiteModule

import Script
import User
import Category
import Language

__modulename__ = "Page_Search"

class Page_Search(SiteModule):

    def __init__(self, **args):

        self.pages = ["script_search"]
        self.template = Config.Template["script_search"]
        self.form = args["form"]

    def _set_params(self):
        
        if self.form.has_key("search"):
            scripts = self._search()

        elif self.form.has_key("search_submitter_id"):
            scripts = self._search_submitter()

        elif self.form.has_key("list_all"):
            scripts = self._list_all()

        else:
            return

        self.template = Config.Template["view_scripts"]
        submitter_id = self.form.getvalue("search_submitter_id", 0)

        row = "even"
        for script in scripts:

            user_obj = User.User(script["script_submitter_id"])
            
            category_obj = Category.Category(script["script_category_id"])
            language_obj = Language.Language(script["script_language_id"])

            script.update({"script_submitter": user_obj.GetAlias(),
                           "script_category": category_obj.Name(),
                           "script_language": language_obj.Name(),
                           "row": row})
            
            if row == "even":
                row = "odd"
            else:
                row = "even"
        
        self.tmpl.param("MAIN_LOOP_LEN", len(scripts))
        self.tmpl.param("MAIN_LOOP", scripts, "loop")

    
    def _search(self):

        script_obj = Script.Script()
        terms = {}

        if self.form.has_key("name"):
            terms["name"] = self.form.getvalue("name")

        if self.form.has_key("descr"):
            terms["descr"] = self.form.getvalue("descr")

        if self.form.has_key("submitter"):

            user_obj = User.User()
            user_id = user_obj.GetUid(self.form.getvalue("submitter"))
            terms["submitter_id"] = user_id

        recent_only = self.form.getvalue("most_recent")

        return script_obj.Search(terms)

    def _search_submitter(self):

        script_obj = Script.Script()
        submitter_id = self.form.getvalue("search_submitter_id")
        scripts = script_obj.ListScripts({"submitter_id": submitter_id})
        
        return scripts

    def _list_all(self):

        script_obj = Script.Script()
        return script_obj.ListScripts()
        
        
    def display(self):

        self._set_params()
        
        self.tmpl.compile(self.template)
        return self.tmpl
