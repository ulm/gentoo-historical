# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_User.py,v 1.1 2004/07/03 21:51:35 port001 Exp $
#

MetaData = {"page" : ("user",), "params" : "form, uid"}

import Template as TemplateHandler
import Config
import MySQL
from User import User
from SiteModuleBE import SiteModuleBE as Parent

def Display(form, uid):

    page = Page_User(form, uid)
    page.selectDisplay()

class Page_User(Parent):

    class_type = "user"  # The type of variable modified by this display module
    user_arr = []
    template = Config.Template["admin_user_controls"]
    obj_attributes = {"alias": "", "fullname": "", "email": "", "rank": 0,
                      "type": 0}
    
    obj = User()

    messages = {"add": "User Successfully Added",
                "modify": "User's Personal Information Updated",
                "delete": "Users Successfully Deleted"}
    
    def add(self):

        self.__checkPasswd()
        self.obj.SetID(self.form.getvalue("user_id"))
        self.obj.Create({"alias": self.form.getvalue("alias"),
                         "fullname": self.form.getvalue("fullname"),
                         "email": self.form.getvalue("email"),
                         "type": self.form.getvalue("type"),
                         "passwd": self.form.getvalue("password1")})
        
        self.message = self.messages["add"]

        self.show_all()

    def modify(self):

        self.__checkPasswd()
        self.obj.SetID(self.form.getvalue("user_id"))
        self.obj.Modify({"alias": self.form.getvalue("alias"),
                         "fullname": self.form.getvalue("fullname"),
                         "email": self.form.getvalue("email"),
                         "type": self.form.getvalue("type"),
                         "passwd": self.form.getvalue("password1")})
        
        self.message = self.messages["modify"]

        self.show_all()

    def __checkPasswd(self):

        password1 = self.form.getvalue("password1")
        password2 = self.form.getvalue("password2")
        if password1 != password2:
            # An error should be displayed here.
            pass
