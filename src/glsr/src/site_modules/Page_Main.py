# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Main.py,v 1.4 2004/11/04 00:59:22 port001 Exp $
#

import Config
from site_modules import SiteModule

class Page_Main(SiteModule):

    __modulename__ = "Page_Main"

    def __init__(self, **args):

        self.pages = [None, "main"]
        self.template = Config.Template["main"]

    def _set_params(self):

        self.tmpl.param("GLSR_URL", Config.URL)

    def display(self):

        self._set_params()
        self.tmpl.compile(self.template)
        return self.tmpl
