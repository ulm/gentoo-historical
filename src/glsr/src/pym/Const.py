# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Const.py,v 1.2 2004/06/14 23:40:31 port001 Exp $
#

__modulename__ = "Const"

import Config

TYPE = {
    "user":		0,
    "developer":	1,
    "admin":		3
    }

_DATE_LEN = 20
_TEXT_LEN = 65536
_UID_LEN = 5

FIELD_LEN = {
    "categories": {
    "catid": 3,
    "name": 50,
    "descr": 100,
    "parent": 3
    },
    
    "comments": {
    "comid": 6,
    "submitter": _UID_LEN,
    "date": _DATE_LEN,
    "subject": 30,
    "lastedited": _DATE_LEN,
    "body": _TEXT_LEN,
    "ofscript": 6,
    "ofversion": 10
    },

    "languages": {
    "langid": 3,
    "name": 50,
    "descr": 100,
    "def_keywords": 100,
    "def_expr": 100,
    "col_expr": 100,
    "col_s_keywords": 100
    },

    "news": {
    "annid": 10,
    "author": _UID_LEN,
    "date": _DATE_LEN,
    "subject": 100,  # <= Table must be changed
    "body": _TEXT_LEN
    },

    "scripts": {
    "submitter": _UID_LEN,
    "category": 3,
    "rank": 1,
    "name": 30,
    "descr": 100,
    "language": 3
    },

    "sessions": {
    "sessid": 30,
    "uid": _UID_LEN,
    "time": 10
    },

    "subscripts": {
    "subscid": 10,
    "parent": 7,
    "version": 10,
    "body": _TEXT_LEN,
    "changelog": _TEXT_LEN,
    "date": _DATE_LEN,
    "approved": 1,
    "approvedby": _UID_LEN,
    },

    Config.MySQL["user_table"]: {
    "uid": _UID_LEN,
    "alias":25,
    "fullname":40,
    "passwd":32,
    "email":50,
    "rank":5,
    "type":1,
    "joined":_DATE_LEN,
    "lastip":15
    }
}
