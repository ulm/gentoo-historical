#!/usr/bin/python
#
# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_User.py,v 1.1 2004/06/04 06:38:37 port001 Exp $
#

MetaData = {"page" : ("user",), "params" : "form, uid"}

import Template as TemplateHandler
import Config
import MySQL
from User import User

def Display(form, uid):

    aliases = []
    add_user = 0
    modify_user = 0
    alias = ""
    fullname = ""
    email = ""
    rank = 0
    type = 0
    message = ""
    warn_message = ""
    form_inputs = form.keys()

    user_obj = User()
    
    if "add_new_user" in form.keys():
        
        (alias,fullname,email,type,password) = (
            MySQL.ValidateArgs(Config.MySQL["user_table"],
                               {"alias": form.getvalue("alias"),
                                "fullname": form.getvalue("fullname"),
                                "email": form.getvalue("email"),
                                "type": form.getvalue("type"),
                                "passwd": form.getvalue("password1")}))

        user_obj.Create(alias, fullname, email, type, password)
        
        message = "User Successfully Added"
        form_inputs.append("show_add_new_user")
        
    elif "delete_users" in form.keys():
        
        for uid in form.getlist("delete"):
            if user_obj.SetID(uid):
                user_obj.Remove()
        
        message = "Users Successfully Deleted"
        form_inputs.append("show_all_users")
        
    elif "modify_user" in form.keys():
        
        password1 = form.getvalue("password1")
        password2 = form.getvalue("password2")
        if password1 != password2:
            # An error should be displayed here.
            pass
        
        user_obj.SetID(form.getvalue("uid"))
        user_obj.Modify(form.getvalue("alias"), form.getvalue("fullname"),
                        form.getvalue("email"), form.getvalue("type"),
                        form.getvalue("password1"))
        
        message = "User's Personal Information Updated"
        form_inputs.append("show_all_users")


    if "show_all_users" in form_inputs:
        """ Grab a list of all users """
        
        row = "even"
        for record in user_obj.List():
            record.update({"row": row})
            aliases.append(record)
            if row == "even":
                row = "odd"
            else:
                row = "even"

        if len(aliases) == 0:
            warn_message = "No Users Found"

    elif "show_add_new_user" in form_inputs:
        
        add_user = 1
        modify_user = 1
        
    elif "show_modify_user" in form_inputs:
        
        modify_user = form.getvalue("show_modify_user")
        user_obj.SetID(modify_user)
        user_info = user_obj.GetDetails()
        alias = user_info['user_alias']
        fullname = user_info['user_fullname']
        email = user_info['user_email']
        rank = user_info['user_rank']
        type = user_info['user_type']


    AdminUserControlsTemplate = TemplateHandler.New()
    AdminUserControlsTemplate.Compile(Config.Template["admin_user_controls"],
                                      {"GLSR_URL":	Config.URL,
                                       "TOTAL_USERS":	len(aliases),
                                       "ADD_USER_FORM": add_user,
                                       "MODIFY_USER": 	modify_user,
                                       "ALIAS": 	alias,
                                       "FULLNAME": 	fullname,
                                       "EMAIL": 	email,
                                       "RANK": 		rank,
                                       "TYPE": 		type,
                                       "MESSAGE": 	message,
				       "WARN_MESSAGE":	warn_message},
                                      {"USER_LOOP": 	aliases})
    AdminUserControlsTemplate.Print()

    AdminUserTemplate = TemplateHandler.New()
    AdminUserTemplate.Compile(Config.Template["admin_user"],
                              {"GLSR_URL":		Config.URL})
    AdminUserTemplate.Print()

