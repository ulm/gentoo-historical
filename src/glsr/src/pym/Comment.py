# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Comment.py,v 1.2 2004/09/30 03:09:36 hadfield Exp $
#

__modulename__ = "Comment"

from time import strftime, gmtime

import User
import MySQL
import Config
from GLSRBackend import GLSRBackend as Parent

class Comment(Parent):

    tablename = Config.MySQL["comment_table"]

    def Create(self, details):
        """Add a new comment to the database."""

        details.update({"date": strftime("%Y-%m-%d %H:%M:%S", gmtime())})
        return Parent.Create(self, details)
