# Copyright 2004-2005 Ian Leitch
# Copyright 2004-2005 Scott Hadfield
# Copyright 1999-2005 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = '$Id: Language.py,v 1.6 2005/01/27 04:19:15 port001 Exp $'
__modulename__ = 'Language'

import Config
from GLSRBackend import GLSRBackend as Parent
from GLSRException import LanguageModuleError

class Language(Parent):

    tablename = Config.MySQL["language_table"]

    def Create(self, details):
        """ details is a dictionary with keys [name, descr] """
        return Parent.Create(self, details, ["name"])

    def Modify(self, details):

        return Parent.Modify(self, details, ["name"])

    def Name(self):

        results = self.GetDetails()
        if results != None:
            return results["%s_name" % self.tablename]
        
        else:
            raise LanguageModuleException('Invalid user ID')
