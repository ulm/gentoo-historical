#!/usr/bin/python
#
# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Main.py,v 1.1.1.1 2004/06/04 06:38:38 port001 Exp $
#

MetaData = {"page" : ("main", None), "params" : ""}

import Template as TemplateHandler
import Session
import Config
import Stat
from User import User

def Display():

    user_online_list = ""
    sess_obj = Session.New()
    sessions = sess_obj.ListSessionsOnline(Config.WhoIsOnlineOffset)

    if len(sessions) == 0:
        user_online_list = "No registered accounts active."
    else:
        for session in sessions:
            user_obj = User(session["session_user_id"])
            user_online_list = "%s %s" % (user_online_list,
                                          user_obj.GetAlias())

    AdminMainTemplate = TemplateHandler.New()
    AdminMainTemplate.Compile(Config.Template["admin_main"],
                              {"GLSR_URL":		Config.URL,
			       "USER_COUNT":		Stat.UserCount(),
			       "SESSION_COUNT":		Stat.SessionCount(),
			       "SCRIPT_COUNT":		Stat.ScriptCount(),
			       "SUBSCRIPT_COUNT":	Stat.SubScriptCount(),
			       "CATEGORY_COUNT":	Stat.CategoryCount(),
			       "COMMENT_COUNT":		Stat.CommentCount(),
			       "DBSIZE":		Stat.DBSize(),
			       "USER_ONLINE_LIST":      user_online_list})
    AdminMainTemplate.Print()
