# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Main.py,v 1.7 2004/12/30 03:05:19 port001 Exp $
#

import Config
from SiteModule import SiteModule

class Page_Main(SiteModule):

    __modulename__ = 'Page_Main'

    def init(self):

        self._template = Config.Template['main']

    def _set_params(self):

        self._tmpl.param('GLSR_URL', Config.URL)

    def display(self):

        self._set_params()
        self._tmpl.compile(self._template)
        return self._tmpl
