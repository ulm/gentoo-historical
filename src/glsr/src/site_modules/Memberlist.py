# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Memberlist.py,v 1.1 2005/01/25 00:51:59 hadfield Exp $
#

import Config
from SiteModule import SiteModule
from User import User

__modulename__ = 'Memberlist'

class Memberlist(SiteModule):

    def init(self):

        self._template = Config.Template['memberlist']

    def _set_params(self):

        self._tmpl.param("GLSR_URL", Config.URL)
        self._tmpl.param("MEMBER_LOOP",
                         [{"user_id": 1,
                          "user_alias": "hadfield",
                          "user_email": "hadfield@gentoo.org",
                          "user_location": "Canada",
                          "user_joined": "March 21, 2004",
                          "script_count": 1,
                          "user_rank": 0,
                          "user_website": "buffmuthers.com"}], "loop")

    def display(self):

        self._set_params()
        self._tmpl.compile(self._template)
        return self._tmpl
