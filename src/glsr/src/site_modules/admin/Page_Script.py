# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Script.py,v 1.4 2004/12/30 14:08:09 port001 Exp $
#

import Config
from Script import Script
from SiteModule import SiteModule

class Page_Script(SiteModule):

    __modulename__ = 'Page_Script'

    def init(self):

        self._template = Config.Template['admin_script']
	self._class_name = 'script'
	self._object = Script()
	self._tmpl.params('TOTAL_SCRIPTS', 0)

    def _select_action(self):

        if "open_search_page" in self._action_inputs:
	    self._template = Config.Template['admin_script_search']
	elif "search_script"in self._action_inputs:
	    self._template = Config.Template['admin_script_results']
	    self._get_search_results()    

    def _get_search_results(self):

        search_terms = {}
        search_terms["language"] = []
        search_terms["category"] = []
        search_terms["status"] = []

        for key in self._req.Values.keys():

            if key[:key.find('_')] == "lang":
                search_terms["language"].append(key[key.find('_')+1:])

            elif key[:key.find('_')] == "cat":
                search_terms["category"].append(key[key.find('_')+1:])

            elif key[:key.find('_')] == "stat":
                search_terms["status"].append(key[key.find('_')+1:])

        for key in ["name", "descr", "submitter", "most_recent"]:
            if key in self._req.Values.keys():
                search_terms[key] = self._req.Values.getvalue(key)

        results = self._object.Search(search_terms)

        if not len(results):
            self._report_type = "warn"

	self._tmpl.param('TOTAL_SCRIPTS', len(results))
	self._tmpl.param('SCRIPT_LOOP', results, 'loop')
