# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Language.py,v 1.1 2004/06/04 06:38:36 port001 Exp $
#

__modulename__ = "Language"

import MySQL
import Config
from GLSRBackend import GLSRBackend as Parent

class Language(Parent):

    tablename = Config.MySQL["language_table"]

    def Create(self, name, description):

        return Parent.Create(self, {"name": name, "descr": description},
                             ["name"])


    def Modify(self, name, descr):

        return Parent.Modify(self, ["name", "descr"],
                             {"name": name, "descr": descr})

