# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Script.py,v 1.4 2004/09/30 03:09:36 hadfield Exp $
#

import Config
import Script
import Category
import Language
from site_modules import SiteModule, Redirect

__modulename__ = "Page_Script"

class Page_Script(SiteModule):

    def __init__(self, form = None, uid = 0):

        self.pages = [None, "create_script", "save_script"]
        self.page = form.getvalue("page")
        self.template = Config.Template["create_script"]
        self.form = form

        self.script_id = form.getvalue("script_id", "0")

        # Set the scripts parent id automatically if the script already has id.
        if self.script_id == "0":
            self.parent_script_id = form.getvalue("parent_script_id", "0")
        else:
            script_obj = Script.SubScript(self.script_id)
            self.parent_script_id = script_obj.GetParentID()

        if self.form.has_key("save_script"):
            self.required = {}


    def _set_params(self):

        self.tmpl.param("SCRIPT_ID", self.script_id)
        self.tmpl.param("PARENT_SCRIPT_ID", self.parent_script_id)
        
        if self.script_id == "0":
            
            self.tmpl.param("MESSAGE", "")
            
            self.tmpl.param("NAME", "")
            self.tmpl.param("DESCR", "")
            self.tmpl.param("VERSION", "1.0")

            category_obj = Category.Category()
            language_obj = Language.Language()
            self.tmpl.param("CATEGORY_LOOP", category_obj.List(), "loop")
            self.tmpl.param("LANGUAGE_LOOP", language_obj.List(), "loop")
            self.tmpl.param("BODY", "")
            self.tmpl.param("CHANGELOG", "")

        else:

            subscript_obj = Script.SubScript(self.script_id)
            script_obj = Script.Script(self.parent_script_id)
            script_details = script_obj.GetDetails()
            subscript_details = subscript_obj.GetDetails()
            
            self.tmpl.param("MESSAGE", "")
            
            self.tmpl.param("NAME", script_details["script_name"])
            self.tmpl.param("DESCR", script_details["script_descr"])
            self.tmpl.param("VERSION", subscript_details["subscript_version"])

            category_obj = Category.Category()
            language_obj = Language.Language()
            self.tmpl.param("CATEGORY_LOOP", category_obj.List(), "loop")
            self.tmpl.param("LANGUAGE_LOOP", language_obj.List(), "loop")
            self.tmpl.param("BODY", subscript_details["subscript_body"])
            self.tmpl.param("CHANGELOG",
                            subscript_details["subscript_changelog"])

    def _action_save(self):

        # Setup/save the parent script.
        script_details = {"name": self.form.getvalue("name"),
                          "descr": self.form.getvalue("descr"),
                          "category_id": self.form.getfirst("category_ids"),
                          "language_id": self.form.getvalue("language_id")}

        if self.parent_script_id == "0":
            script_obj = Script.Script()
            script_obj.Create(script_details)
            self.parent_script_id = script_obj.id

        else:
            script_obj = Script.Script(self.parent_script_id)
            script_obj.Modify(script_details)

        # Setup/save the subscript.
        subscript_details = {"version": self.form.getvalue("version"),
                             "body": self.form.getvalue("body"),
                             "changelog": self.form.getvalue("changelog")}

        # Does the script need approval?
        if Config.RequireApproval or self.form.has_key("get_script_reviewed"):
            subscript_details["approved"] = "0"

        else:
            subscript_details["approved"] = "1"

        if self.script_id == "0":
            subscript_details["parent_id"] = self.parent_script_id
            subscript_obj = Script.SubScript()
            subscript_obj.Create(subscript_details)
            self.script_id = subscript_obj.id

        else:
            subscript_obj = Script.SubScript(self.script_id)
            subscript_obj.Modify(self.parent_script_id, subscript_details)


    def _select_action(self):

        if self.page == "save_script":
            self._action_save()

    
    def display(self):

        self._select_action()

        if (self.form.has_key("save_script") or
            self.form.has_key("publish_script") or
            self.form.has_key("get_script_reviewed")):
            raise Redirect, ("index.py?page=create_script&script_id=%s" %
                             self.script_id + "&parent_script_id=%s" %
                             self.parent_script_id)
        
        self._set_params()
        self.tmpl.compile(self.template)
        return self.tmpl
