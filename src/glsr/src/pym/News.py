#
# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: News.py,v 1.3 2004/07/19 00:56:45 hadfield Exp $
#

__modulename__ = "News"

from time import strftime, gmtime

import MySQL
import Config
from GLSRBackend import GLSRBackend as Parent

class News(Parent):

    tablename = Config.MySQL["news_table"]

    def Create(self, details):
        """ Add a new announcement to the database.
            'details' contains [subject, author_id, body] """

        details.update({"date": strftime("%Y-%m-%d %H:%M:%S", gmtime())})
        return Parent.Create(self, details)

    def Modify(self, details):
        """ Modify announcement details """

        return Parent.Modify(self, details)


    def AnnidExists(self, annid):
        """ Check for existence of given AnnID """

        return Parent.Exists(self, "id", annid)
