# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: GLSRException.py,v 1.2 2004/10/29 01:28:02 hadfield Exp $
#


class GLSRException(Exception):
    """The default error class used by this application."""
 
    def __init__(self, errmsg, extramsg = ""):
        self.errmsg = errmsg
        self.extramsg = extramsg
 
    def __str__(self):
         
        if self.extramsg:
            errstr = ("%s\n\n<b>Further Details:</b>\n%s" %
                      (self.extramsg, self.errmsg))
        else:
            errstr = self.errmsg
 
        return errstr

class InvalidIDError(GLSRException): pass
