# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2  
#
# $Id: SiteModule.py,v 1.2 2004/12/30 14:08:09 port001 Exp $  
#

__modulename__ = 'SiteModule'

import string

import Config
from GLSRException import GLSRException
from Template import Template

class SiteModule:
    """
    The parent class for all site modules
    """

    show_border = True
    
    _template = None
    _reports = {}
    _object = None
    _obj_attributes = None
    _class_name = None
    _params = {}

    _tmpl = Template()
    _action_inputs = []
    _mode = 'show'
    _report = ''
    _report_type = 'normal'
    _main_loop = []
    _add_obj = 0
    _modify_obj = 0
    _options = ('show_all', 'show_add', 'show_modify',
                'add', 'modify', 'delete')
    
    def __init__(self, req, **args):

        self._req = req
	
	self._page = args['page']
	self._uid = args['uid']
	self._alias = args['alias']
	self._session = args['session']

        self._action_inputs = self._req.Values.keys()

        try:
	    self.init()
	except:
	    pass
	    
        self._sanity_check()
        self._map_attributes()

    def _sanity_check(self):

	if self._template == None:
	    raise GLSRException('Template not specified')

    def _map_attributes(self):

        attributes = self._obj_attributes
        self._obj_attributes = {}

        if attributes != None:
   	    for attribute in attributes:
	        self._obj_attributes[attribute] = ''

    def _set_attributes(self):

        for key in self._obj_attributes.keys():
	    self._obj_attributes[key] = self._req.Values.getvalue(key)
	    
    def _set_report(self):

        if self._mode.startswith('show'):
	    self._report = ''
	else:
 	    self._report = self._reports[self._mode]

    def _select_action(self):

        for action in self._action_inputs:
	    if action in self._options:
	         exec "self._%s()" % action
	         break

        self._set_report()

    def _add(self):
    
        self._mode = 'add'
        self._set_attributes()
	self._object.Create(self._obj_attributes)

    def _modify(self):

        self._mode = 'modify'
        self._set_attributes()
	self._object.SetID(self._req.Values.getvalue("%s_id" % self._class_name))
	self._object.Modify(self._obj_attributes)

    def _delete(self):

        self._mode = 'delete'
        for id in self._req.Values.getlist('delete_btn'):
	    if self._object.SetID(id):
	        self._object.Remove()

	self._show_all()

    def _show_all(self):

        self._mode = 'show_all'
        row = 'even'

	for record in self._object.List():
	    record.update({'row': row})
	    self._main_loop.append(record)
	    if row == 'even':
	        row = 'odd'
	    else:
	        row = 'even'
	
	if not len(self._main_loop):
	    self._report_type = 'warn'

    def _show_add(self):
    
        self._mode = 'show_add'
        self._add_obj = True
	self._modify_obj = True

    def _show_modify(self):
    
        self._mode = 'show_modify'
        self._modify_obj = self._req.Values.getvalue('show_modify')
	self._object.SetID(self._modify_obj)
	obj_info = self._object.GetDetails()

	for key in self._obj_attributes.keys():
	    self._obj_attributes[key] = obj_info["%s_%s" %
	                                         (self._class_name, key)]

    def display(self):

        self._select_action()
        
	self._tmpl.param('GLSR_URL', Config.URL)
        self._tmpl.param('TOTAL', len(self._main_loop))
        self._tmpl.param('MODIFY', self._modify_obj)
        self._tmpl.param('ADD_FORM', self._add_obj)
        self._tmpl.param('REPORT', self._report)
        self._tmpl.param('REPORT_TYPE', self._report_type)
        self._tmpl.param('MAIN_LOOP', self._main_loop, 'loop')

        for key, value in self._obj_attributes.items():
            self._tmpl.param(string.upper(key), value)

        for key in self._params.keys():
            if self._mode in self._params[key].keys():
	        self._tmpl.param(string.upper(key), self._params[key][self._mode])
	        
	self._tmpl.compile(self._template)
        return self._tmpl

class Redirect(Exception): pass
