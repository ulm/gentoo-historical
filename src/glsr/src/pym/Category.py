# Copyright 2004-2005 Ian Leitch
# Copyright 2004-2005 Scott Hadfield
# Copyright 1999-2005 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = '$Id: Category.py,v 1.7 2005/01/27 04:19:15 port001 Exp $'
__modulename__ = 'Category'

import Config
from MySQL import MySQL
from GLSRBackend import GLSRBackend as Parent
from GLSRException import CategoryModuleError

class Category(Parent):
    
    tablename = Config.MySQL["category_table"]

    def Create(self, details):
        """ details is a dictionary with keys [name, descr, parent_id] """

        if (int(details["parent_id"]) > 0 and
            not self.Exists("id", details["parent_id"])):
            # FIXME: We should throw an error here
            return False

        if not details["parent_id"] > 0:
            details["parent_id"] = 0

        return Parent.Create(self, details, ["name"])
   
    def Remove(self):

        # check for child cats and scripts that are under the cat and
        # scripts under child cats of the parent.
        # Note: I think that deleting scripts too might be a bit risky.
        
        for child_id in self.Children():
            child = Category(child_id)
            child.Remove()

        return Parent.Remove(self)

    def Modify(self, details):

        if not details["parent_id"] > 0:
            details["parent_id"] = 0

        return Parent.Create(self, details, ["name"])
    
    def Remove(self):

        # check for child cats and scripts that are under the cat and
        # scripts under child cats of the parent.
        # Note: I think that deleting scripts too might be a bit risky.
        
        for child_id in self.Children():
            child = Category(child_id)
            child.Remove()

        return Parent.Remove(self)

    def Modify(self, details):

        return Parent.Modify(self, details, ["name"])

    def List(self, parent_id = -1):

        if parent_id == -1:
            return Parent.List(self)
        else:
            return Parent.List(self, {"parent_id": parent_id})

    def Children(self):
        """Return the id's for all of this categories children."""

        return (MySQLHandler.query("SELECT %s_id FROM %s%s " %
                                   (self.tablename, Config.MySQL["prefix"],
                                    self.tablename) +
                                    "WHERE %s_parent_id = " % self.tablename + "%s",
                                    self.id, fetch="all").values())

    def Name(self):

        results = self.GetDetails()
        if results != None:
            return results["%s_name" % self.tablename]
        
        else:
            raise CategoryModuleError('Invalid user ID')
