# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Search.py,v 1.8 2004/12/30 03:05:19 port001 Exp $
#

import Config
from User import User
from Script import Script
from Category import Category
from Language import Language
from SiteModule import SiteModule

__modulename__ = 'Page_Search'

class Page_Search(SiteModule):

    def init(self):

        self._template = Config.Template['script_search']

    def _set_params(self):
        
        if self._req.Values.getvalue('search') != None:
            scripts = self._search()

        elif self._req.Values.getvalue('search_submitter_id') != None:
            scripts = self._search_submitter()

        elif self._req.Values.getvalue('list_all') != None:
            scripts = self._list_all()

        else:
            return

        self._template = Config.Template['view_scripts']
        submitter_id = self._req.Values.getvalue('search_submitter_id', 0)

        row = 'even'
        for script in scripts:

            user_obj = User(script['script_submitter_id'])
            category_obj = Category(script['script_category_id'])
            language_obj = Language(script['script_language_id'])

            script.update({'script_submitter': user_obj.GetAlias(),
                           'script_category': category_obj.Name(),
                           'script_language': language_obj.Name(),
                           'row': row})
            
            if row == 'even':
                row = 'odd'
            else:
                row = 'even'
        
        self._tmpl.param('MAIN_LOOP_LEN', len(scripts))
        self._tmpl.param('MAIN_LOOP', scripts, 'loop')

    def _search(self):

        script_obj = Script()
        terms = {}

        if self._req.Values.getvalue('name') != None:
            terms['name'] = self._req.Values.getvalue('name')

        if self._req.Values.getvalue('descr') != None:
            terms["descr"] = self._req.Values.getvalue('descr')

        if self._req.Values.getvalue('submitter') != None:

            user_obj = User()
            user_id = user_obj.GetUid(self._req.Values.getvalue('submitter'))
            terms['submitter_id'] = user_id

        recent_only = self._req.Values.getvalue('most_recent')

        return script_obj.Search(terms)

    def _search_submitter(self):

        script_obj = Script()
        submitter_id = self._req.Values.getvalue('search_submitter_id')
        scripts = script_obj.ListScripts({'submitter_id': submitter_id})
        
        return scripts

    def _list_all(self):

        script_obj = Script()
        return script_obj.ListScripts()
        
    def display(self):

        self._set_params()
        
        self._tmpl.compile(self._template)
        return self._tmpl
