# Copyright 2004-2005 Ian Leitch
# Copyright 2004-2005 Scott Hadfield
# Copyright 1999-2005 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = '$Id: GLSRException.py,v 1.3 2005/01/27 04:19:15 port001 Exp $'
__modulename__ = 'GLSRException'

import os
import State
from Error import error
from Logging import logwrite

class GLSRException(Exception):
    """
    The parent exception class
    """
 
    def __init__(self, errmsg, extramsg = ''):
    
        self._errmsg = errmsg
        self._extramsg = extramsg

class Redirect(GLSRException):

    def __str__(self):

        logwrite("Request redirected to %s" % self._errmsg, self._extramsg, type='Info')
        State.Req.add_header('Location', self._errmsg)
        State.Req.output_headers()
        os.abort()

class TemplateModuleError(GLSRException):

    def __str__(self):

        error(self._errmsg, 'Template', self._extramsg)

class AdminModuleError(GLSRException):

    def __str__(self):

        error(self._errmsg, 'Admin', self._extramsg)

class CategoryModuleError(GLSRException):

    def __str__(self):

        error(self._errmsg, 'Category', self._extramsg)

class MySQLModuleError(GLSRException):

    def __str__(self):

        error(self._errmsg, 'MySQL', self._extramsg)

class LanguageModuleError(GLSRException):

    def __str__(self):

        error(self._errmsg, 'Language', self._extramsg)

class ScriptModuleError(GLSRException):

    def __str__(self):

        error(self._errmsg, 'Script', self._extramsg)
