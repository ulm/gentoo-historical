# Copyright 2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = '$Id: __init__.py,v 1.1 2005/05/09 20:21:31 hadfield Exp $'
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
            page_mod = __import__(page_req, globals(), locals(), [page_req])
            print page_mod.output(page_req, request).output()
