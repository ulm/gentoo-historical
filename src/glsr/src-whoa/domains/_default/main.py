# Copyright 2004-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = "$Id: main.py,v 1.4 2005/06/06 19:25:52 hadfield Exp $"
__modulename__ = "main"

from domains._parent.basepage import BasePage
from setup import config

class Page(BasePage):

    def setup(self):
        BasePage.set_template(self, "main.tpl")
