#!/usr/bin/env python2
#
# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Script.py,v 1.1 2004/06/04 06:38:35 port001 Exp $
#

__modulename__ = "Script"

import types
import string

import MySQL
import Config
from GLSRBackend import GLSRBackend as Parent

class Script(Parent):

    tablename = Config.MySQL["script_table"]

    def Create(self, submitter, category, name, descr, body):
        """Add a new script to the database"""

        return Parent.Create(self,
                             {"submitter":	submitter,
                              "category":	category,
                              "rank":		0,
                              "name":		name,
                              "descr":		description,
                              "body":		body})

    
    def Approve(self, uid):
        """Mark script as approved"""

        return Parent.Modify(self, ["approved", "approvedby"],
                             {"approved": 1,
                              "approvedby": uid})


    def Search(self, Terms):
        """
        Search for scripts in the DB.
        Terms should be a dictionary of (field, value) pairs. If 'value' is a
        ListType then they will be OR'd
        (i.e. field = value[0] OR field = value[1]...)

        Searchable values include: language, category, status, name, descr,
        submitter
        """

        import operator
        
        qStr = self.__mk_query(["language", "category"], Terms)
        if qStr != "":
            qStr = "WHERE " + qStr

        scripts = MySQL.Query("SELECT * FROM %s%s %s" %
                              (Config.MySQL["prefix"], self.tablename, qStr))

        found = []
        for script in scripts:
            for key in ["name", "descr", "submitter"]:
                if key in Terms.keys():
                    if script[key].find(Terms[key]) != -1:
                        found.append(script)


        # Get the subscripts
        qStr = self.__mk_query(["status"], Terms)
        if qStr != "":
            qStr = "AND " + qStr

        loop = len(found) # Since found will be modified, this is necessary.
        for i in range(loop):

            qStr = ("SELECT %s_version, %s_date, %s_status, %s_approvedby" %
                    tuple(operator.repeat(Config.MySQL["subscript_table"], 4))+
                    " FROM %s%s WHERE status != 'draft' AND parent = %s " %
                    (Config.MySQL["prefix"], Config.MySQL["subscript_table"],
                     found[i]["scid"]) + qStr)
            
            if "most_recent" in Terms.keys():
                
                subscript = MySQL.Query(qStr + " ORDER BY version",
                                        fetch = "one")
                found[i].update(subscript)
                
            else:
                
                subscripts = MySQL.Query(qStr, fetch = "all")
                
                for subscript in subscripts[1:]:
                    found.append(found[i])
                    found[len(found)].update(subscript)

                found[i].update(subscripts[0])

        return found


    def __mk_query_str(self, field, Terms):

        qStr = field + " IN "
        if type(Terms[field]) == types.ListType:
            
            if not len(Terms[field]):
                return ""
            
            newlist = map(lambda x: "'%s'" % x, Terms[field])
            value = string.join(newlist, "," % field)
            
        else:
            value = Terms[field]
        
        return "%s (%s)" % (qStr, value)


    def __mk_query(self, fields, Terms):
        
        qStr = ""
        for (key,value) in Terms.items():
        
            if key in fields:
            
                if qStr != "":
                    qStr = qStr + " AND "

                qStr = qStr + self.__mk_query_str(key, Terms)
        
        return qStr


