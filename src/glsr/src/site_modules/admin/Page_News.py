# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_News.py,v 1.3 2004/12/30 03:05:19 port001 Exp $
#

import Config
from User import User
from News import News
from SiteModule import SiteModule

class Page_News(SiteModule):

    __modulename__ = 'Page_News'

    def init(self):

        self._template = Config.Template['admin_news']
	self._class_name = "news"
	self._obj_attributes = ('author_id', 'subject', 'body')
	self._object = News()
	self._params = {'ANNOUNCE_MODE': {'show_add': 'Make announcement',
	                                  'show_modify': 'Modify announcement'}}
        self._reports = {'add': 'Announcement added',
	                 'modify': 'Announcement updated',
			 'delete': 'Announcement(s) deleted'}
