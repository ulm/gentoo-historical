# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Language.py,v 1.5 2005/01/26 22:22:20 port001 Exp $
#

__modulename__ = "Language"

import Config
from Error import error
from GLSRBackend import GLSRBackend as Parent

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
            error("Invalid User ID!", __modulename__)
            return False
