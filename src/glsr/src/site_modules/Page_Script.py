# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Script.py,v 1.2 2004/07/19 01:01:31 hadfield Exp $
#

MetaData = {"page" : ("yourscripts",), "params" : "form, uid"}

import string

import Template as TemplateHandler
import Config
from Script import Script
from Language import Language
from Category import Category
from SiteModuleBE import SiteModuleBE as Parent

from Language import Language

def Display(form, uid):

    page = Page_Script(form, uid)
    page.selectDisplay()

class Page_Script(Parent):

    class_type = "script"
    script_arr = []
    template = Config.Template["script"]
    obj_attributes = {"name": "", "descr": "",
                      "language_id": 0, "category_id": 0}
    
    sub_attributes = {"body": "", "parent_id": 0, "version": "1.0"}
    
    obj = Script()

    messages = {"add": "Script Successfully Created",
                "modify": "Script Successfully Created"}

    def __init__(self, form, uid):
        
        self.script_id = form.getvalue("script_id")
        Parent.__init__(self, form, uid)
    
    def add(self):

        self.setAttributes()
        self.obj_attributes.update({"submitter_id": self.uid})
        self.obj.Create(self.obj_attributes)
        
        self.sub_attributes.update({"parent_id": self.obj.id})
        self.obj.CreateSub(self.sub_attributes)
        
        self.message = self.messages["add"]

        self.show_all()

    def modify(self):

        self.setAttributes()
        self.sub_attributes.update({"parent_id": self.obj.id})
        self.obj.CreateSub(self.sub_attributes)

        self.message = self.messages["modify"]

        self.show_all()

    def selectDisplay(self):

        self.options = self.options + ["show_parent", "show_subscript"]
        self.options.remove("delete")
        self.tmpl.Param("SHOW_PARENT", "0")

        Parent.selectDisplay(self)
    
    def setAttributes(self):
        
        for key in self.obj_attributes.keys():
            self.obj_attributes[key] = self.form.getvalue(key)

        for key in self.sub_attributes.keys():
            self.sub_attributes[key] = self.form.getvalue(key)
        
    def display(self):

        lang_obj = Language()
        cat_obj = Category()
        
        self.tmpl.Param("LANGUAGE_LOOP", lang_obj.List(), "l")
        self.tmpl.Param("CATEGORY_LOOP", cat_obj.List(), "l")

        for key, value in self.sub_attributes.items():
            self.tmpl.Param(string.upper(key), value)

        Parent.display(self)

    def show_all(self):

        self.__make_loop(self.obj.ListScripts({"submitter_id": self.uid}))

    def __make_loop(self, array):

        row = "even"
        for record in array:

            if record["subscript_approved"] == "0":
                record["subscript_approvedby"] = "Not Approved"

            language_obj = Language(record["script_language_id"])
            category_obj = Category(record["script_category_id"])
            record.update({"row": row,
                           "language": language_obj.Name(),
                           "category": category_obj.Name()})

            exec "self.%s_arr.append(record)" % self.class_type

            if row == "even":
                row = "odd"
            else:
                row = "even"

        if not len(eval("self.%s_arr" % self.class_type)):
            self.warn_message = 1
            
        
    def show_parent(self):

        self.tmpl.Param("SHOW_PARENT", "1")
        parent = self.obj.ListScripts({"id": self.script_id})[0]
        loop = []
        
        for sub in self.obj.ListSubs({"parent_id": self.script_id}):
            tmp_dict = parent
            tmp_dict.update(sub)
            loop.append(tmp_dict)

        self.__make_loop(loop)
