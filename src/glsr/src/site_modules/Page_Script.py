# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Script.py,v 1.1 2004/07/13 15:13:34 hadfield Exp $
#

MetaData = {"page" : ("yourscripts",), "params" : "form, uid"}

import string

import Template as TemplateHandler
import Config
from Script import Script
from Language import Language
from Category import Category
from SiteModuleBE import SiteModuleBE as Parent

def Display(form, uid):

    page = Page_Script(form, uid)
    page.selectDisplay()

class Page_Script(Parent):

    class_type = "script"
    script_arr = []
    template = Config.Template["script"]
    obj_attributes = {"name": "", "descr": "",
                      "language_id": 0, "category_id": 0}
    
    sub_attributes = {"body": "", "parent_id": 0}
    
    obj = Script()

    messages = {"add": "Script Successfully Created",
                "modify": "Script Successfully Created"}
    
    def add(self):

        self.setAttributes()
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

    def delete(self):
        pass

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

        row = "even"
        for record in self.obj.CombineLists():
            record.update({"row": row})
            exec "self.%s_arr.append(record)" % self.class_type
            if row == "even":
                row = "odd"
            else:
                row = "even"

        if not len(eval("self.%s_arr" % self.class_type)):
            self.warn_message = 1

