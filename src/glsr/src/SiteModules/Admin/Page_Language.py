# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Language.py,v 1.2 2004/06/30 19:48:34 port001 Exp $
#

MetaData = {"page" : ("language",), "params" : "form"}

import Config

from Language import Language
from SiteModuleBE import SiteModuleBE as Parent

def Display(form):

    page = Page_Language(form)
    page.selectDisplay()

class Page_Language(Parent):

    class_type = "language"
    language_arr = []
    template = Config.Template["admin_languages"]
    obj_attributes = {"name": "", "descr": "", "def_keywords": "",
                      "def_expr": "", "clo_expr": "", "clo_s_keywords": ""}
    
    obj = Language()

    messages = {"add": "Language Successfully Added",
                "modify": "Language Successfully Modified",
                "delete": "Languages Successfully Deleted"}


