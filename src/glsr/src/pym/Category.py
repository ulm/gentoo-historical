# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Category.py,v 1.1.1.1 2004/06/04 06:38:35 port001 Exp $
#

__modulename__ = "Category"

import MySQL
import Config
from GLSRBackend import GLSRBackend as Parent

class Category(Parent):
    
    tablename = Config.MySQL["category_table"]

    def Create(self, name, descr, parent_id):

        if parent_id > 0 and not self.Exists("parent_id", parent_id):
            # We should throw an error here
            return False
        
        if not parent_id > 0:
            parent_id = 0
            
        return Parent.Create(self, {"name": name, "descr": descr,
                                    "parent_id": parent_id}, ["name"])

    
    def Remove(self):

        # check for child cats and scripts that are under the cat and
        # scripts under child cats of the parent.
        # Note: I think that deleting scripts too might be a bit risky.
        
        for child_id in self.Children():
            child = Category(child_id)
            child.Remove()

        return Parent.Remove(self)


    def Modify(self, name, descr, parent_id):

        return Parent.Modify(self, ["name", "descr", "parent_id"],
                             {"name": name, "descr": descr,
                              "parent_id": parent_id})


    def List(self, parent_id = -1):

        if parent_id == -1:
            return Parent.List(self)
        else:
            return Parent.List(self, {"parent_id": parent_id})


    def Children(self):
        " Return the id's for all of this categories children "
        
        return (MySQL.Query("SELECT %s_id FROM %s%s " %
                             (self.tablename, Config.MySQL["prefix"],
                              self.tablename) +
                             "WHERE %s_parent_id = " % self.tablename + "%s",
                             self.id, fetch="all").values())
