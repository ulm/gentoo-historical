# Copyright 2004-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = "$Id: main.py,v 1.2 2005/05/16 22:30:37 hadfield Exp $"
__modulename__ = "main"

from domains._parent.basepage import BasePage
from setup import config

class Page(BasePage):

    def setup(self, page, request):

        BasePage.set_page(self, "main.tpl")
        self.tmpl.param("USER_ALIAS", "")
        self.tmpl.param("USER_ID", "")
