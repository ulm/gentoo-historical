# Copyright 2004-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = "$Id: main.py,v 1.1 2005/05/09 20:21:31 hadfield Exp $"
__modulename__ = "main"

from core.template import Template
from setup import config

def output(page, request):
    tmpl = Template()
    tmpl.compile(config.template_loc + "/main.tpl",
                 {"GLSR_URL":          config.url,
                  "THEME":             config.theme,
                  "GLSR_VERSION":      config.__version__,
                  "USER_ALIAS":        "",
                  "USER_ID":           ""})
    return tmpl
