# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Main.py,v 1.6 2004/12/25 01:36:24 port001 Exp $
#

import Config
from site_modules import SiteModule

class Page_Main(SiteModule):

    __modulename__ = "Page_Main"

    def __init__(self, req, **args):

        self.template = Config.Template["main"]

    def _set_params(self):

        self.tmpl.param("GLSR_URL", Config.URL)

    def display(self):

        self._set_params()
        self.tmpl.compile(self.template)
        return self.tmpl
