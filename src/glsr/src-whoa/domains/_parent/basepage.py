# Copyright 2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = "$Id: basepage.py,v 1.3 2005/06/06 19:25:52 hadfield Exp $"
__modulename__ = "basepage"

from core.template import Template
from setup import config

class BasePage:

    def __init__(self, request = None):

        self.request = request
        self.action = self.request.getvalue("action")
        
        self.template = Template()
        self.template.param("GLSR_URL", config.url)
        self.template.param("THEME", config.theme)
        self.template.param("GLSR_VERSION", config.__version__)
        self.template_path = ""

    def _setup_user(self):
        """Setup the user variables."""
        self.template.param("USER_ALIAS", "")
        self.template.param("USER_ID", "")
        
    def set_template(self, template_name):

        if template_name[0] == "/":
            self.template_path = template_name
        else:
            self.template_path = config.template_loc + "/" + template_name
    
    def output(self):
        
        self._setup_user()
        self.template.compile(self.template_path)
        return self.template.output()
