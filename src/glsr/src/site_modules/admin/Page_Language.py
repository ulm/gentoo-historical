# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Language.py,v 1.4 2004/12/31 17:03:12 port001 Exp $
#

import Config
from Language import Language
from SiteModule import SiteModule

class Page_Language(SiteModule):

    __modulename__ = 'Page_Language'

    def init(self):

	self._template = Config.Template['admin_script_languages']
	self._class_name = "language"
        self._object = Language()
        self._permited_methods = ('add', 'modify', 'delete',
                                  'show_add', 'show_modify', 'show_all')
        self._obj_attributes = ('name', 'descr', 'def_keywords',
                                'def_expr', 'clo_expr', 'clo_s_keywords')
        self._reports = {'add': 'Language Successfully Added',
                         'modify': 'Language Successfully Modified',
                         'delete': 'Languages Successfully Deleted'}
