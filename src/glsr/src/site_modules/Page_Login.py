#!/usr/bin/python
#
# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Login.py,v 1.2 2004/08/22 23:23:39 hadfield Exp $
#

import os

import Session as SessionHandler
from User import User

MetaData = {"page" : ("login",), "params" : "username, password"}

def Login_User(username, password):

    user_obj = User()
    user_obj.SetID(user_obj.GetUid(username))

    if not user_obj.ValidateAlias(username, password):
        return False

    # Update IP address
    user_obj.UpdateIP(os.environ['REMOTE_ADDR'])
    
    # Setup Session Variables
    sess = SessionHandler.New()
    sessid = sess.GenerateSessionID()
    sess.SetCookie(user_obj.id, sessid)

    # Update session table in the db
    sess.CreateSession(user_obj.id, sessid)
    
    return True
