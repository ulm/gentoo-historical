#!/usr/bin/python
#
# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Page_Script.py,v 1.1 2004/06/04 06:38:38 port001 Exp $
#

MetaData = {"page" : ("script",), "params" : "form"}

import Template as TemplateHandler
import Config

from Script import Script
from Category import Category
from Language import Language

def Display(form):

    if "open_search_page" in form.keys():
        
        displaySearchForm()
        
    elif "list_all_scripts" in form.keys():
        
        displayMainPage()
        displaySearchResults(form)
        
    elif (form.has_key("show_all_categories") or
          form.has_key("show_add_new_cat") or
          form.has_key("show_modify_cat") or
          form.has_key("add_new_cat") or
          form.has_key("modify_cat") or
          form.has_key("delete_cats")):
        
        displayMainPage()
        displayCategories(form)
        
    elif (form.has_key("show_all_languages") or
          form.has_key("show_add_new_lang") or
          form.has_key("show_modify_lang") or
          form.has_key("add_new_lang") or
          form.has_key("modify_lang") or
          form.has_key("delete_langs")):
        
        displayMainPage()
        displayLanguages(form)

    elif "search_script" in form.keys():
        
        displaySearchResults(form)
        
    else:
        
        displayMainPage()

def displayCategories(form):

    cats = []
    parents = []
    add_cat = 0
    modify_cat = 0
    name = ""
    descr = ""
    parent = ""
    message = ""
    warn_message = 0
    form_inputs = form.keys()

    cat_obj = Category()
    
    if "add_new_cat" in form.keys():

        cat_obj.Create(form.getvalue("name"), form.getvalue("descr"),
                       form.getvalue("parent"))
        message = "Category Successfully Added"
        form_inputs.append("show_all_categories")
        
    elif "modify_cat" in form.keys():
        
        cat_obj.SetID(form.getvalue("catid"))
        cat_obj.Modify(form.getvalue("name"), form.getvalue("descr"),
                        form.getvalue("parent"))
        message = "Category Successfully Modified"
        form_inputs.append("show_all_categories")
    
    elif "delete_cats" in form.keys():
        
        for catid in form.getlist("delete"):
            if cat_obj.SetID(catid):
                cat_obj.Remove()
        
        message = "Categories Successfully Deleted"
        form_inputs.append("show_all_categories")


    if "show_all_categories" in form_inputs:

        def listCats(parent_id, padding = 12):
            list = []
            
            for record in cat_obj.List(parent_id):
                if record["category_parent_id"]:
                    cat_obj.SetID(record["category_parent_id"])
                    parent_details = cat_obj.GetDetails()
                    record["parent_name"] = parent_details["category_name"]
                else:
                    record["parent_name"] = "None"

                record["padding"] = padding
                list.append(record)
                list = list + listCats(record["category_id"], padding + 12)

            return list
                
        cats = listCats(0)
        for i in range(len(cats)):
            if i % 2:
                cats[i].update({"row": "odd"})
            else:
                cats[i].update({"row": "even"})
        
        if not len(cats):
            warn_message = 1
    
    elif "show_add_new_cat" in form_inputs:

        add_cat = 1
        modify_cat = 1
        parents = cat_obj.List()
        
    elif "show_modify_cat" in form_inputs:
    
        modify_cat = form.getvalue("show_modify_cat")
        cat_obj.SetID(form["show_modify_cat"].value)
        cat_info = cat_obj.GetDetails()
        name = cat_info["category_name"]
        descr = cat_info["category_descr"]
        parent = cat_info["category_parent_id"]
        parents = cat_obj.List()


    CategoriesTemplate = TemplateHandler.New()
    CategoriesTemplate.Compile(Config.Template["admin_categories"],
                               {"GLSR_URL":	Config.URL,
                                "TOTAL_CATS":	len(cats),
                                "MODIFY_CAT": 	modify_cat,
                                "ADD_CAT_FORM":	add_cat,
                                "NAME": 	name,
                                "DESCR": 	descr,
                                "PARENT": 	parent,
                                "MESSAGE":	message,
                                "WARN_MESSAGE":	warn_message},
                               {"CAT_LOOP": 	cats,
                                "PARENT_LOOP":	parents})
    CategoriesTemplate.Print()

def displayLanguages(form):

    langs = []
    add_lang = 0
    modify_lang = 0
    name = ""
    descr = ""
    message = ""
    warn_message = 0
    form_inputs = form.keys()

    lang_obj = Language()
    
    if "add_new_lang" in form.keys():

        name = form.getvalue("name")
        descr = form.getvalue("descr")
        lang_obj.Create(name, descr)
        message = "Language Successfully Added"
        form_inputs.append("show_all_languages")
        
    elif "delete_langs" in form.keys():
        
        for langid in form.getlist("delete"):
            if lang_obj.SetID(langid):
                lang_obj.Remove()
        
        message = "Languages Successfully Deleted"
        form_inputs.append("show_all_languages")

    elif "modify_lang" in form.keys():

        lang_obj.SetID(form.getvalue("langid"))
        lang_obj.Modify(form.getvalue("name"), form.getvalue("descr"))
        
        form_inputs.append("show_all_languages")
    

    if "show_all_languages" in form_inputs:
        
        row = "even"
        for record in lang_obj.List():
            record.update({"row": row})
            langs.append(record)
            if row == "even":
                row = "odd"
            else:
                row = "even"

        if not len(langs):
            warn_message = 1
    
    elif "show_add_new_lang" in form_inputs:

        add_lang = 1
        modify_lang = 1
        
    elif "show_modify_lang" in form_inputs:
    
        modify_lang = form.getvalue("show_modify_lang")
        lang_obj.SetID(form["show_modify_lang"].value)
        lang_info = lang_obj.GetDetails()
        name = lang_info["language_name"]
        descr = lang_info["language_descr"]


    LanguagesTemplate = TemplateHandler.New()
    LanguagesTemplate.Compile(Config.Template["admin_languages"],
                               {"GLSR_URL":		Config.URL,
                                "TOTAL_LANGS":		len(langs),
                                "MODIFY_LANG": 		modify_lang,
                                "ADD_LANG_FORM":	add_lang,
                                "NAME": 		name,
                                "DESCR": 		descr,
                                "MESSAGE":		message,
                                "WARN_MESSAGE":		warn_message},
                               {"LANG_LOOP": 		langs})
    LanguagesTemplate.Print()


def displayMainPage():

    AdminScriptTemplate = TemplateHandler.New()
    AdminScriptTemplate.Compile(Config.Template["admin_script"],
                                {"GLSR_URL":		Config.URL,
                                 "MESSAGE": 		"",
                                 "WARN_MESSAGE": 	0,
                                 "TOTAL_SCRIPTS": 	0})
    AdminScriptTemplate.Print()
        

def displaySearchResults(form):

    search_terms = {}
    search_terms["language"] = []
    search_terms["category"] = []
    search_terms["status"] = []
    
    for key in form.keys():
        
        if key[:key.find('_')] == "lang":
            search_terms["language"].append(key[key.find('_')+1:])

        elif key[:key.find('_')] == "cat":
            search_terms["category"].append(key[key.find('_')+1:])

        elif key[:key.find('_')] == "stat":
            search_terms["status"].append(key[key.find('_')+1:])

    for key in ["name", "descr", "submitter", "most_recent"]:
        if key in form.keys():
            search_terms[key] = form[key].value

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

def displaySearchForm():
        
    ScriptSearchTemplate = TemplateHandler.New()
    ScriptSearchTemplate.Compile(Config.Template["admin_script_search"],
                                 {"GLSR_URL":	Config.URL})
    ScriptSearchTemplate.Print()
