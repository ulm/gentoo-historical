# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Script.py,v 1.13 2005/01/27 04:19:15 port001 Exp $
#

import Config
from Category import Category
from Language import Language
from Script import Script, SubScript
from SiteModule import SiteModule

__modulename__ = 'Page_Script'

class Page_Script(SiteModule):

    def init(self):

        self._template = Config.Template['create_script']
        self._script_id = self._req.Values.getvalue('script_id', '0')

        # Set the scripts parent id automatically if the script already has id.
        if self._script_id == '0':
            self._parent_script_id = self._req.Values.getvalue('parent_script_id', '0')
        else:
            parent_obj = Script(self._script_id)
            script_obj = SubScript(parent_obj.RecentSub())
            self._parent_script_id = script_obj.GetParentID()

        if self._req.Values.getvalue('save_script') != None:
            self.required = {}

    def _set_params(self):

        self._tmpl.param('SCRIPT_ID', self._script_id)
        self._tmpl.param('PARENT_SCRIPT_ID', self._parent_script_id)
        
        if self._script_id == '0':
            
            self._tmpl.param('MESSAGE', '')
            
            self._tmpl.param('NAME', '')
            self._tmpl.param('DESCR', '')
            self._tmpl.param('VERSION', '1.0')

            category_obj = Category()
            language_obj = Language()
            self._tmpl.param('CATEGORY_LOOP', category_obj.List(), 'loop')
            self._tmpl.param('LANGUAGE_LOOP', language_obj.List(), 'loop')
            self._tmpl.param('BODY', '')
            self._tmpl.param('CHANGELOG', '')

        else:

            subscript_obj = SubScript(self._script_id)
            script_obj = Script(self._parent_script_id)
            script_details = script_obj.GetDetails()
            subscript_details = subscript_obj.GetDetails()
            
            self._tmpl.param('MESSAGE', '')
            
            self._tmpl.param('NAME', script_details['script_name'])
            self._tmpl.param('DESCR', script_details['script_descr'])
            self._tmpl.param('VERSION', subscript_details['subscript_version'])

            category_obj = Category()
            language_obj = Language()
            self._tmpl.param('CATEGORY_LOOP', category_obj.List(), 'loop')
            self._tmpl.param('LANGUAGE_LOOP', language_obj.List(), 'loop')
            self._tmpl.param('BODY', subscript_details['subscript_body'])
            self._tmpl.param('CHANGELOG',
                            subscript_details['subscript_changelog'])

    def _action_save(self):

        # Setup/save the parent script.
        script_details = {'name': self._req.Values.getvalue('name'),
                          'descr': self._req.Values.getvalue('descr'),
                          'category_id': self._req.Values.getvalue('category_ids'),
                          'language_id': self._req.Values.getvalue('language_id'),
                          'submitter_id': self.uid}

        if self._parent_script_id == '0':
            script_obj = Script()
            script_id = script_obj.Create(script_details)
            self._parent_script_id = script_obj.id

        else:
            script_obj = Script(self._parent_script_id)
            script_obj.Modify(script_details)

        # Setup/save the subscript.
        subscript_details = {'version': self._req.Values.getvalue('version'),
                             'body': self._req.Values.getvalue('body'),
                             'changelog': self._req.Values.getvalue('changelog', '')}

        # Does the script need approval?
        if Config.RequireApproval or self._req.Values.getvalue('get_script_reviewed') != None:
            subscript_details['approved'] = '0'

        else:
            subscript_details['approved'] = '1'

        if self._script_id == '0':
            subscript_details['parent_id'] = self._parent_script_id
            subscript_obj = SubScript()
            subscript_obj.Create(subscript_details)
            self._script_id = subscript_obj.id

        else:
            subscript_obj = SubScript(self._script_id)
            subscript_obj.Modify(self._parent_script_id, subscript_details)

    def _select_action(self):

        if self._page == 'save_script':
            self._action_save()

    def display(self):

        self._select_action()

        if (self._req.Values.getvalue('save_script') != None or
            self._req.Values.getvalue('publish_script') != None or
            self._req.Values.getvalue('get_script_reviewed') != None):
            raise Redirect("index.py?page=create_script&script_id=%s" %
                            self._script_id + "&parent_script_id=%s" %
                            self._parent_script_id, __modulename__)
        
        self._set_params()
        self._tmpl.compile(self._template)
        return self._tmpl
