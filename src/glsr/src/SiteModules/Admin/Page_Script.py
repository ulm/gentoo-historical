# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Script.py,v 1.2 2004/06/27 23:24:58 hadfield Exp $
#

MetaData = {"page" : ("script","category","language"), "params" : "form"}

import Template as TemplateHandler
import Config

from Script import Script
from SiteModuleBE import SiteModuleBE as Parent

def Display(form):

    page = Page_Script(form)
    page.selectDisplay()


class Page_Script(Parent):

    class_type = "script"
    script_arr = []
    template = Config.Template["admin_script"]
    obj_attributes = {}

    obj = Script()

    def selectDisplay(self):

        if "open_search_page" in self.form_inputs:
            self.__displaySearchForm()

        elif "list_all_scripts" in self.form_inputs:
            self.display()
            #self.__displaySearchResults()

        elif "search_script" in self.form_inputs:
            self.__displaySearchResults()

        else:
            self.display()

    def display(self):

        AdminScriptTemplate = TemplateHandler.New()
        AdminScriptTemplate.Compile(
            self.template,
            {"GLSR_URL":	Config.URL,
             "MESSAGE":		"Operation not yet implemented :-).",
             "WARN_MESSAGE": 	0,
             "TOTAL_SCRIPTS": 	0})
        AdminScriptTemplate.Print()
        

    def __displaySearchResults(self):

        search_terms = {}
        search_terms["language"] = []
        search_terms["category"] = []
        search_terms["status"] = []

        for key in self.form.keys():

            if key[:key.find('_')] == "lang":
                search_terms["language"].append(key[key.find('_')+1:])

            elif key[:key.find('_')] == "cat":
                search_terms["category"].append(key[key.find('_')+1:])

            elif key[:key.find('_')] == "stat":
                search_terms["status"].append(key[key.find('_')+1:])

        for key in ["name", "descr", "submitter", "most_recent"]:
            if key in self.form.keys():
                search_terms[key] = self.form[key].value

        script_obj = Script()
        results = script_obj.Search(search_terms)

        warn_message = 0
        if not len(results):
            warn_message = 1

        ScriptResultsTemplate = TemplateHandler.New()
        ScriptResultsTemplate.Compile(Config.Template["admin_script_results"],
                                          {"GLSR_URL":	Config.URL,
                                           "TOTAL_SCRIPTS":	len(results),
                                           "WARN_MESSAGE":	warn_message},
                                          {"SCRIPT_LOOP": 	results})
        ScriptResultsTemplate.Print()

    def __displaySearchForm(self):
        
        ScriptSearchTemplate = TemplateHandler.New()
        ScriptSearchTemplate.Compile(Config.Template["admin_script_search"],
                                     {"GLSR_URL":	Config.URL})
        ScriptSearchTemplate.Print()
