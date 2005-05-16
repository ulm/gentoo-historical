# Copyright 2004-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = "$Id: basepage.py,v 1.1 2005/05/16 19:44:42 hadfield Exp $"
__modulename__ = "basepage"

from core.template import Template
from setup import config

class BasePage:

    def __init__(self):

        self.tmpl = Template()
        self.tmpl.param("GLSR_URL", config.url)
        self.tmpl.param("THEME", config.theme)
        self.tmpl.param("GLSR_VERSION", config.__version__)

        self.page = ""
    
    def set_page(self, page_name):
        
        self.page = page_name
    
    def output(self):

        self.tmpl.compile(config.template_loc + "/" + self.page)
        return self.tmpl.output()
