#!/usr/bin/env python2
#
# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Script.py,v 1.4 2004/09/30 03:09:36 hadfield Exp $
#

__modulename__ = "Script"

import types
import string
from time import strftime, gmtime

import MySQL
import Config
from Logging import err
from GLSRBackend import GLSRBackend as Parent

class Script(Parent):

    tablename = Config.MySQL["script_table"]

    def Create(self, details):
        """Add a new script to the database."""

        details.update({"rank": 0})
        return Parent.Create(self, details, (("submitter_id", "name"),))

#     def CreateSub(self, parent_id, details):
#         """Add a new subscript"""

#         if not parent_id or parent_id == "0":
#             err("Invalid Parent ID", __modulename__)
#             return False
        
#         self.tablename = Config.MySQL["subscript_table"]

#         details.update({"date":  strftime("%Y-%m-%d", gmtime())})
#         retval = Parent.Create(self, details)
        
#         self.tablename = Config.MySQL["script_table"]
#         return retval

#     def ModifySub(self, script_id, parent_id, details):
#         """Add a new subscript."""

#         if not details["parent_id"] or details["parent_id"] == "0":
#             err("Invalid Parent ID", __modulename__)
#             return False

#         self.tablename = Config.MySQL["subscript_table"]
#         self.SetID(script_id)
        
#         details.update({"date":  strftime("%Y-%m-%d", gmtime()),
#                         "approved": 0})
#         retval = Parent.Modify(self, details)
        
#         self.tablename = Config.MySQL["script_table"]
#         return retval
            
    def ListSubs(self, constraint = None):
        """Returns a list of all subscripts."""

        if constraint is None:
            constraint = {}
        
        self.tablename = Config.MySQL["subscript_table"]
        retval = self.List(constraint)
        self.tablename = Config.MySQL["script_table"]

        return retval

    def ListScripts(self, script_restrict = None, subscript_restrict = None):
        """Returns a list of each script combined with its most recent
        subscript."""

        if script_restrict is None:
            script_restrict = {}

        if subscript_restrict is None:
            subscript_restrict = {}
        
        script_arr = self.List(script_restrict)
        subscript_arr = self.ListSubs(subscript_restrict)

        recent_scripts = {}
        # Strip out all but the most recent scripts from subscript_arr
        for subscript in subscript_arr:
            parent = subscript["subscript_parent_id"]
            try:
                if (recent_scripts[parent]["subscript_version"] <
                    subscript["subscript_version"]):
                    recent_scripts[parent] = subscript
            except KeyError:
                recent_scripts.update({parent:subscript})

        for parent,script in recent_scripts.iteritems():
            for i in range(0, len(script_arr)):
                if script_arr[i]["script_id"] == parent:
                    script_arr[i].update(script)

        return script_arr
        
    def Approve(self, uid):
        """Mark script as approved"""

        return Parent.Modify(self, {"approved": 1,
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

        # FIXME: This won't work because submitter is not in the script table,
        # submitter_id is. Thus we can't obtain a partial match on the
        # submitter name so easily.
        found = []
        for script in scripts:
            for key in ["name", "descr", "submitter"]:
                if key in Terms.keys():
                    if script["script_%s" % key].find(Terms[key]) != -1:
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




class SubScript(Parent):

    tablename = Config.MySQL["subscript_table"]

    def Create(self, details):
        """Add a new subscript"""

        if not details["parent_id"] or details["parent_id"] == "0":
            err("Invalid Parent ID", __modulename__)
            return False

        details.update({"date":  strftime("%Y-%m-%d", gmtime())})
        return Parent.Create(self, details)

    def Modify(self, script_id, parent_id, details):
        """Add a new subscript."""

        if not details["parent_id"] or details["parent_id"] == "0":
            err("Invalid Parent ID", __modulename__)
            return False

        details.update({"date":  strftime("%Y-%m-%d", gmtime()),
                        "approved": 0})
        return Parent.Modify(self, details)
            
    def Approve(self, uid):
        """Mark script as approved"""

        return Parent.Modify(self, {"approved": 1,
                                    "approvedby": uid})

    def GetParentID(self):

        return self.GetDetails()["subscript_parent_id"]
        

        
