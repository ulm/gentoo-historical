# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: View_Script.py,v 1.5 2004/12/28 19:28:25 port001 Exp $
#

import time

import User
import Config
import Script
import Comment
import Language
import Category
from site_modules import SiteModule

__modulename__ = 'View_Script'

class View_Script(SiteModule):

    def __init__(self, req, **args):

        self.req = req
        self.page = args['page']
        self.template = Config.Template['view_script']
        self.uid = args['uid']

    def _set_params(self):

        script_id = self.req.Values.getvalue('script_id')
        script_obj = Script.Script(script_id)
        scripts = script_obj.ListScripts({'id': script_id})

        self.tmpl.param('MESSAGE', '')
        
        if len(scripts):
            
            details = scripts[0]

            category_obj = Category.Category(details['script_category_id'])
            language_obj = Language.Language(details['script_language_id'])
            user_obj = User.User(details['script_submitter_id'])
            
            self.tmpl.param('NAME', details['script_name'])
            self.tmpl.param('DESCR', details['script_descr'])
            self.tmpl.param('RANK', details['script_rank'])
            self.tmpl.param('CATEGORY', category_obj.Name())
            self.tmpl.param('LANGUAGE', language_obj.Name())
            self.tmpl.param('AUTHOR', user_obj.GetAlias())

            self.tmpl.param('CREATION_DATE', details['subscript_date'])
            self.tmpl.param('VERSION', details['subscript_version'])
            self.tmpl.param('BODY', details['subscript_body'])
            self.tmpl.param('SCRIPT_ID', script_id)
            self.tmpl.param('SUBSCRIPT_ID', details['subscript_id'])

            comment_obj = Comment.Comment()
            comments = comment_obj.List({'script_id': details['script_id']})
            for comment in comments:
                user_obj2 = User.User(comment['comment_submitter_id'])
                comment['submitter'] = user_obj2.GetAlias()
                date = time.strptime(comment['comment_date'],
                                      "%Y-%m-%d %H:%M:%S")
                comment['date'] = time.strftime("%a %b %d, %Y %I:%M %p", date)


            self.tmpl.param('COMMENTS_LOOP_COUNT', len(comments))
            self.tmpl.param('COMMENTS_LOOP', comments, 'loop')

        else:
            self.tmpl.param('WARN_MESSAGE', 1)

    def _action_save_comment(self):

        subscript_id = self.req.Values.getvalue('subscript_id')
        subscript_obj = Script.SubScript(subscript_id)
        script_id = subscript_obj.GetParentID()

        # Don't save the comment if there is not body or subject
        if (self.req.Values.getvalue('body') is None and
            self.req.Values.getvalue('subject') is None):
            return
        
        details = {
            'submitter_id': self.uid,
            'script_id': script_id,
            'subscript_id': subscript_id,
            'subject': self.req.Values.getvalue('subject', ''),
            'body': self.req.Values.getvalue('body')
            }

        comment_obj = Comment.Comment()
        comment_obj.Create(details)
        
    def _select_action(self):

        if self.page == 'post_comment':
            self._action_save_comment()
        
    def display(self):

        self._select_action()
        self._set_params()
        self.tmpl.compile(self.template)
        return self.tmpl
    
    
