# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Category.py,v 1.1 2004/06/27 23:24:58 hadfield Exp $
#

MetaData = {"page" : ("category",), "params" : "form, uid"}

import Template as TemplateHandler
import Config

from Page_Script import Page_Script
from Category import Category
from SiteModuleBE import SiteModuleBE as Parent

def Display(form, uid):

    page = Page_Category(form)
    page.selectDisplay()

class Page_Category(Parent):

    class_type = "category"
    category_arr = []
    parents = []
    template = Config.Template["admin_categories"]
    obj_attributes = {"name": "", "descr": "", "parent_id": ""}
    
    obj = Category()

    messages = {"add": "Category Successfully Added",
                "modify": "Category Successfully Modified",
                "delete": "Categories Successfully Deleted"}


    def display(self):

        self.tmpl.Param("PARENT_LOOP", self.parents, "l")
        Parent.display(self)


    def show_all(self):

        self.category_arr = self.__listCats(0)
        for i in range(len(self.category_arr)):
            if i % 2:
                self.category_arr[i].update({"row": "odd"})
            else:
                self.category_arr[i].update({"row": "even"})

        if not len(self.category_arr):
            self.warn_message = 1
    

    def __listCats(self, parent_id, padding = 12):

        list = []
        for record in self.obj.List(parent_id):
            if record["category_parent_id"]:
                self.obj.SetID(record["category_parent_id"])
                parent_details = self.obj.GetDetails()
                record["parent_name"] = parent_details["category_name"]
            else:
                record["parent_name"] = "None"

            record["padding"] = padding
            list.append(record)
            list = list + self.__listCats(record["category_id"], padding + 12)

        return list


    def show_add(self):

            Parent.show_add(self)
            self.parents = self.obj.List()


