# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: SiteModuleBE.py,v 1.4 2004/09/30 03:09:36 hadfield Exp $
#

import string

import Template as TemplateHandler
import Config
import MySQL

class SiteModuleBE:

    tmpl = TemplateHandler.Template()

    message = ""
    warn_message = 0

    add_obj = 0
    modify_obj = 0

    form_inputs = []
    form = {}
    uid = 0

    display_forms = {"show_all": 1, "show_add": 2, "show_modify": 3}

    # These options match submit button names in the html forms.
    # They should also match function names in the class.
    options = ["show_all", "show_add", "show_modify",
               "add", "modify", "delete"]

    def __init__(self, form = None, uid = 0):

        if form == None:
            form = {}
        
        self.form_inputs = form.keys()
        self.form = form
        self.uid = uid
    
    def add(self):

        self.setAttributes()
        self.obj.Create(self.obj_attributes)

        self.message = self.messages["add"]
        self.show_all()

    def modify(self):
        
        self.setAttributes()
        self.obj.SetID(self.form.getvalue(self.class_type + "_id"))
        self.obj.Modify(self.obj_attributes)

        self.message = self.messages["modify"]
        self.show_all()
        
    def delete(self):
        
        for id in self.form.getlist("delete_btn"):
            if self.obj.SetID(id):
                self.obj.Remove()

        self.message = self.messages["delete"]
        self.show_all()

    def selectDisplay(self):

        # Select the chosen operation
        for option in self.options:
            if option in self.form_inputs:
                exec "self.%s()" % option
                break

        self.display()

    def setAttributes(self):

        for key in self.obj_attributes.keys():

            self.obj_attributes[key] = self.form.getvalue(key)
            #self.obj_attributes[key] = (
            #    MySQL.ValidateArgs(Config.MySQL["user_table"],
            #                       {key: self.form.getvalue(key)}))
    
    def display(self):

        self.tmpl.param("GLSR_URL", Config.URL)
        self.tmpl.param("TOTAL", len(eval("self.%s_arr" % self.class_type)))
        self.tmpl.param("MODIFY", self.modify_obj)
        self.tmpl.param("ADD_FORM", self.add_obj)
        self.tmpl.param("MESSAGE", self.message)
        self.tmpl.param("WARN_MESSAGE", self.warn_message)
        self.tmpl.param("MAIN_LOOP", eval("self.%s_arr" % self.class_type),"l")

        for key, value in self.obj_attributes.items():
            self.tmpl.param(string.upper(key), value)

        self.tmpl.compile(self.template)
        print self.tmpl.output()
        
    def show_all(self):
        
        row = "even"
        for record in self.obj.List():
            record.update({"row": row})
            exec "self.%s_arr.append(record)" % self.class_type
            if row == "even":
                row = "odd"
            else:
                row = "even"

        if not len(eval("self.%s_arr" % self.class_type)):
            self.warn_message = 1

    def show_add(self):

        self.add_obj = 1
        self.modify_obj = 1

    def show_modify(self):

        self.modify_obj = self.form.getvalue("show_modify")
        self.obj.SetID(self.form["show_modify"].value)
        obj_info = self.obj.GetDetails()
        
        for key in self.obj_attributes.keys():
            self.obj_attributes[key] = obj_info["%s_%s" %
                                                (self.class_type, key)]
