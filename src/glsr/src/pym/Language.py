# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Language.py,v 1.3 2004/07/19 00:48:37 hadfield Exp $
#

__modulename__ = "Language"

import MySQL
import Config
from Logging import err
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
            err("Invalid User ID!", __modulename__)
            return False
