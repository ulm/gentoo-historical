# Copyright 2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = '$Id: __init__.py,v 1.2 2005/05/16 22:30:37 hadfield Exp $'
__modulename__ = "_default"

__all__ = {
    "login": ["login", "perform_login", "logout"],
    "main": ["main", None],
    "memberlist": ["memberlist"],
    "register": ["register", "create_user"],
    "script": ["create_script", "save_script"],
    "search": ["script_search"],
    "view_cript": ["view_script", "post_comment"]
    }

def process(page_req, request):

    for page, page_requests in __all__.iteritems():
        if page_req in page_requests:
            page_mod = __import__(page, globals(), locals(), page)
            page_obj = page_mod.Page()
            page_obj.setup(page_req, request)
            print page_obj.output()
