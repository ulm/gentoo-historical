# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: GLSRBackend.py,v 1.3 2004/07/13 15:06:41 hadfield Exp $
#

__modulename__ = "GLSRBackend"

import string
import operator
import types

import MySQL
import Config

class GLSRBackend:

    def __init__(self, id = 0):

        if id != 0:
            self.SetID(id)
        else:
            self.id = 0

    def Create(self, details, keys = ()):
        """ Creates the row with 'details'. Keys contains a list of restraints.
        So, if you can't have two identical 'name's then add 'name' to the list
        of keys and it won't add the field. If you have two or more fields that
        can't be used in combination then make a sub tuple in keys """

        # Check restrictions
        for field in keys:
            
            if type(field) == types.TupleType:
                try:
                    for f in field:
                        if not self.Exists(f, details[f]):
                            raise
                    return True
                except:
                    continue
                    
            elif self.Exists(field, details[field]):
                return True

        fields = string.join(map(lambda x: "%s_%s" % (self.tablename, x),
                                 details.keys()), ", ")
        
        values = string.join(
            operator.repeat(['%s'], len(details.keys())), ", ")
        
        if fields == "" or values == "":  # No fields to set?
            return False

        MySQL.Query("INSERT INTO %s%s" %
                    (Config.MySQL["prefix"], self.tablename) +
                    " (%s) VALUES (%s)" % (fields, values),
                    details.values(), fetch="none")

        # Get the id for the record that was just inserted
        cmp = string.join(map(lambda x: "%s_%s=%%s" % (self.tablename, x),
                              details.keys()), " AND ")

        if cmp != "":
            
            results = MySQL.Query(
                "SELECT %s_id FROM %s%s " %
                (self.tablename, Config.MySQL["prefix"], self.tablename) +
                "WHERE %s" % cmp, details.values(), fetch="all")

            if len(results) > 1:
                """ Ambiguous results. We can't get an id """
                return True
            else:
                self.id = results[0]["%s_id" % self.tablename]
            
        

    def Remove(self):

        if not self.id:
            return False
        
        MySQL.Query("DELETE FROM %s%s " %
                    (Config.MySQL["prefix"], self.tablename) +
                    "WHERE %s_id = " % self.tablename + "%s", self.id,
                    fetch="none")


    def Modify(self, fields, details):
        """ Modify the specified 'fields' if they were set in 'details' """

        if not self.id:
            return False

        for key in fields:
            if key in details.keys():
                MySQL.Query("UPDATE %s%s" %
                            (Config.MySQL["prefix"], self.tablename) +
                            " SET %s_%s = " % (self.tablename, key) +
                            "%%s WHERE %s_id = " % self.tablename +
                            "%s", (details[key], self.id), fetch="none")


    def List(self, constraint = {}):
        """ Return all rows from self.tablename.
        constraint is a dictionary or {field: value} pairs that requires
        a field == value in order to return that row """

        where_str = string.join(map(lambda x: "%s_%s = %%s" %
                                    (self.tablename, x),
                                    constraint.keys()), " AND ")

        if where_str != "":
            where_str = "WHERE %s" % where_str

        return MySQL.Query("SELECT * FROM %s%s %s" %
                           (Config.MySQL["prefix"], self.tablename,
                            where_str), constraint.values(), fetch="all")

    
    def GetDetails(self):

        if not self.id:
            # An error should probably be thrown here.
            return None
        
        return MySQL.Query("SELECT * FROM %s%s" %
                           (Config.MySQL["prefix"], self.tablename) +
                           " WHERE %s_id = " % self.tablename + "%s", self.id,
                           fetch="one")

    
    def Exists(self, field, value):
        
        result = MySQL.Query("SELECT %s_%s FROM %s%s WHERE %s_%s = " %
                             (self.tablename, field, Config.MySQL["prefix"],
                              self.tablename, self.tablename, field) +
                             "%s", value, fetch = "one")

        return (result != None)

        
    def SetID(self, id):

        if self.Exists("id", id):
            self.id = id
            return True
        else:
            return False
