# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Validation.py,v 1.4 2004/12/16 14:06:26 port001 Exp $
#

__modulename__ = "Validation"

from re import compile,match

from Config
from MySQL import MySQL
from Auth import GenMd5

MySQLHandler = MySQL()

def CheckPageRequest(page):

    if page:

        page_regex = "^[a-z]{1,13}$"
        p_page = compile(page_regex)
        o_page = p_page.match(page)
        
        if not o_page:
            return "Invalid"
    
    return "Valid"

def ValidatePasswd(uid, passwd):

    unknownmd5 = GenMd5(passwd)
    correctmd5 = MySQLHandler.query("SELECT passwd FROM %s " % Config.MySQL["user_table"] +
                       "WHERE uid = %s", uid, fetch="one")

    if unknownmd5 != correctmd5[0]:
        return "Invalid"
    else:
        return "Valid"
    
