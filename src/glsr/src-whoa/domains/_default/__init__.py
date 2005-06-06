# Copyright 2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = '$Id: __init__.py,v 1.3 2005/06/06 19:25:52 hadfield Exp $'
__modulename__ = "_default"

__all__ = [
    "login",
    "main"
    ]

#    "memberlist": ["memberlist"],
#    "register": ["register", "create_user"],
#    "script": ["create_script", "save_script"],
#    "search": ["script_search"],
#    "view_cript": ["view_script", "post_comment"]
#    }

def process(page_req, request):

    for page in __all__:
        if page == page_req:
            page_mod = __import__(page, globals(), locals(), page)
            page_obj = page_mod.Page(request)
            page_obj.setup()
            print page_obj.output()
            return

    # Fallback to the main page
    page_mod = __import__("main", globals(), locals(), "main")
    page_obj = page_mod.Page(request)
    page_obj.setup()
    print page_obj.output()
    
