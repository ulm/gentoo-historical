# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: View_Script.py,v 1.6 2004/12/30 03:05:19 port001 Exp $
#

import time

import Config
from User import User
from Comment import Comment
from Language import Language
from Category import Category
from SiteModule import SiteModule
from Script import Script, SubScript

__modulename__ = 'View_Script'

class View_Script(SiteModule):

    def init(self):

        self._template = Config.Template['view_script']

    def _set_params(self):

        script_id = self._req.Values.getvalue('script_id')
        script_obj = Script(script_id)
        scripts = script_obj.ListScripts({'id': script_id})
        
        if len(scripts):
            
            details = scripts[0]

            category_obj = Category(details['script_category_id'])
            language_obj = Language(details['script_language_id'])
            user_obj = User(details['script_submitter_id'])
            
            self._tmpl.param('NAME', details['script_name'])
            self._tmpl.param('DESCR', details['script_descr'])
            self._tmpl.param('RANK', details['script_rank'])
            self._tmpl.param('CATEGORY', category_obj.Name())
            self._tmpl.param('LANGUAGE', language_obj.Name())
            self._tmpl.param('AUTHOR', user_obj.GetAlias())

            self._tmpl.param('CREATION_DATE', details['subscript_date'])
            self._tmpl.param('VERSION', details['subscript_version'])
            self._tmpl.param('BODY', details['subscript_body'])
            self._tmpl.param('SCRIPT_ID', script_id)
            self._tmpl.param('SUBSCRIPT_ID', details['subscript_id'])

            comment_obj = Comment()
            comments = comment_obj.List({'script_id': details['script_id']})
	    
            for comment in comments:
                user_obj2 = User(comment['comment_submitter_id'])
                comment['submitter'] = user_obj2.GetAlias()
                date = time.strptime(comment['comment_date'],
                                      "%Y-%m-%d %H:%M:%S")
                comment['date'] = time.strftime("%a %b %d, %Y %I:%M %p", date)

            self._tmpl.param('COMMENTS_LOOP_COUNT', len(comments))
            self._tmpl.param('COMMENTS_LOOP', comments, 'loop')

        else:
            self._report_type = "warn"
	    
    def _action_save_comment(self):

        subscript_id = self._req.Values.getvalue('subscript_id')
        subscript_obj = SubScript(subscript_id)
        script_id = subscript_obj.GetParentID()

        # Don't save the comment if there is no body or subject
        if (self._req.Values.getvalue('body') is None and
            self._req.Values.getvalue('subject') is None):
            return
        
        details = {
            'submitter_id': self._uid,
            'script_id': script_id,
            'subscript_id': subscript_id,
            'subject': self._req.Values.getvalue('subject', ''),
            'body': self._req.Values.getvalue('body')
            }

        comment_obj = Comment()
        comment_obj.Create(details)
        
    def _select_action(self):

        if self.page == 'post_comment':
            self._action_save_comment()
        
    def display(self):

        self._select_action()
        self._set_params()
        self._tmpl.compile(self._template)
        return self._tmpl
    
    
