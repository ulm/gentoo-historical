#
# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: News.py,v 1.1.1.1 2004/06/04 06:38:36 port001 Exp $
#

__modulename__ = "News"

from time import strftime, gmtime

import MySQL
import Config
from GLSRBackend import GLSRBackend as Parent

class News(Parent):

    tablename = Config.MySQL["news_table"]

    def Create(self, subject, author, body):
        """Add a new announcement to the database"""

        return Parent.Create(self,
                             {"subject": subject,
                              "author_id": author,
                              "date": strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                              "body": body})
    

    def Modify(self, subject, author, body):
        """ Modify announcement details """

        return Parent.Modify(self, ["subject", "author_id", "body"],
                             {"subject": subject, "author_id": author,
                              "body": body})


    def AnnidExists(self, annid):
        """ Check for existence of given AnnID """

        return Parent.Exists(self, "id", annid)
