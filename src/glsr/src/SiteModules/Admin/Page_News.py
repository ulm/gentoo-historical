# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_News.py,v 1.2 2004/06/27 23:24:58 hadfield Exp $
#

MetaData = {"page" : ("news",), "params" : "form, uid"}

import Template as TemplateHandler
import Config
from User import User
from News import News
from SiteModuleBE import SiteModuleBE as Parent

def Display(form, uid):

    page = Page_News(form, uid)
    page.selectDisplay()

class Page_News(Parent):

    class_type = "news"
    news_arr = []
    template = Config.Template["admin_news"]
    obj_attributes = {"author_id": 0, "subject": "", "body": ""}
    
    announce_mode = ""

    obj = News()

    messages = {"add": "Announcement Successfully Added",
                "modify": "Announcement Updated"}

    def delete(self):
        
        count = 0
        
        for id in self.form.getlist("delete_btn"):
            if self.obj.SetID(id):
                self.obj.Remove()
		count += 1
        
        if count > 1:
            self.message = "%s Announcements Successfully Deleted" % count
        else:
    	    self.message = "%s Announcement Successfully Deleted" % count
        
        self.show_all()
        

    def setAttributes(self):

        Parent.setAttributes(self)
        self.obj_attributes["author_id"] = self.uid

        
    def display(self):

        self.tmpl.Param("ANNOUNCE_MODE", self.announce_mode)
        Parent.display(self)


    def show_all(self):

        row = "even"
        for record in self.obj.List():
            record.update({"row": row})
            user_obj = User(record["news_author_id"])
            record["news_author_id"] = user_obj.GetAlias()
            self.news_arr.append(record)
            if row == "even":
                row = "odd"
            else:
                row = "even"

        if not len(self.news_arr):
            self.warn_message = 1

    def show_add(self):

        self.announce_mode = "Make News Announcement"
        Parent.show_add(self)
        
    def show_modify(self):

        self.announce_mode = "Modify Announcement"
        Parent.show_modify(self)
