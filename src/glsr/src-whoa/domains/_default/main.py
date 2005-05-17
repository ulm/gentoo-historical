# Copyright 2004-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = "$Id: main.py,v 1.3 2005/05/17 16:30:40 hadfield Exp $"
__modulename__ = "main"

from domains._parent.basepage import BasePage
from setup import config

class Page(BasePage):

    def setup(self, page, request):

        BasePage.set_template(self, "main.tpl")
        self.tmpl.param("USER_ALIAS", "")
        self.tmpl.param("USER_ID", "")
