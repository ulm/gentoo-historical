#!/usr/bin/python
#
# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_News.py,v 1.1.1.1 2004/06/04 06:38:37 port001 Exp $
#

MetaData = {"page" : ("news",), "params" : "form, uid"}

import Template as TemplateHandler
import Config
from User import User
from News import News

def Display(form, uid):
    
    aliases = []
    message = ""
    warn_message = ""
    announce_mode = ""
    add_announce = 0
    add_modify_announce = 0
    subject = ""
    author = 0
    announcement = ""
    form_inputs = form.keys()

    news_obj = News()

    if "delete_announce" in form_inputs:
        
        count = 0
        
        for annid in form.getlist("delete"):
            if news_obj.AnnidExists(annid):
                news.obj.id = annid
                news_obj.Remove()
		count += 1
        
        if count > 1:
            message = "%s Announcements Successfully Deleted" % count
        else:
    	    message = "%s Announcement Successfully Deleted" % count
        
        form_inputs.append("show_all_announce")

    if "show_all_announce" in form_inputs:

        row = "even"
        for record in news_obj.List():
            record.update({"row": row})
            user_obj = User(record["news_author_id"])
            record["news_author_id"] = user_obj.GetAlias()
            aliases.append(record)
            if row == "even":
                row = "odd"
            else:
                row = "even"

        if len(aliases) == 0:
            warn_message = "No News Announcements Found"

    elif "show_modify_announce" in form_inputs:

        add_modify_announce = form.getvalue("show_modify_announce")
        news_obj.SetID(add_modify_announce)
        announce_info = news_obj.GetDetails()
        
        subject = announce_info["subject"]
        announcement = announce_info["body"]
        announce_mode = "Modify Announcement"

    elif "modify_announce" in form_inputs:

        news_obj.SetID(form.getvalue("annid"))
        news_obj.Modify(form.getvalue("subject"), uid,
                        form.getvalue("announcement"))
        message = "Announcement Updated"

    elif "show_add_new_announce" in form_inputs:

        add_announce = 1
        add_modify_announce = 1
        announce_mode = "Make News Announcement"

    elif "add_new_announce" in form_inputs:

        subject = form.getvalue("subject")
        announcement = form.getvalue("announcement")
        news_obj.Create(subject, uid, announcement)
        message = "Announcement Successfully Added"


    AdminNewsTemplate = TemplateHandler.New()
    AdminNewsTemplate.Compile(Config.Template["admin_news"],
                              {"GLSR_URL":              Config.URL,
			       "MESSAGE":		message,
			       "TOTAL_ANNOUNCE":	len(aliases),
			       "WARN_MESSAGE":		warn_message,
			       "ADD_MODIFY_ANNOUNCE":	add_modify_announce,
			       "ADD_ANNOUNCE_FORM":	add_announce,
			       "ANNOUNCE_MODE":		announce_mode,
			       "SUBJECT":		subject,
			       "ANNOUNCEMENT":		announcement},
			      {"ANNOUNCE_LOOP":		aliases})
    AdminNewsTemplate.Print()
