# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Validation.py,v 1.1 2004/06/04 06:38:34 port001 Exp $
#

__modulename__ = "Validation"

from Config import MySQL
from MySQL import Query
from Auth import GenMd5
from re import compile,match

def CheckPageRequest(page):
                                                                                
    if page:
        page_regex = "^[a-z]{1,6}$"
                                                                                
        p_page = compile(page_regex)
        o_page = p_page.match(page)
                                                                                
        if not o_page:
            return "Invalid"
                                                                                
    return "Valid"

def ValidatePasswd(uid, passwd):
                                                                                
    unknownmd5 = GenMd5(passwd)
    correctmd5 = Query("SELECT passwd FROM %s " % MySQL["user_table"] + "WHERE uid = %s", uid, fetch="one")                                                                                
    if unknownmd5 != correctmd5[0]:
        return "Invalid"
    else:
        return "Valid"
    
