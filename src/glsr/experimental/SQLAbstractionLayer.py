#!/usr/bin/python

""" 
    This class aims to provide an easy way of retrieving and working with data from 
    a database, by way of iterators. 

    Example Usage:

         UserTable = AbstractionLayer(table="user")

         # Iteration
         UserTable.set_columns(["user_id", "user_alias", "user_fullname"])
         for id, alias, fullname in UserTable:
             print id, alias, fullname
	 UserTable.set_columns(["user_email"])
	     for email in UserTable:
	         print "Email:", email

         # Membership test
         UserTable.set_focus(["user_fullname"]) # Focus on a specific dolumn (membership tests only)
         if "Mr. Smith" in UserTable:
             pass

         print UserTable.len("user_id") # print length of specific column
         print UserTable.len() # print combined length of all columns 

	 print UserTable() # returns lists of values

	 
"""
import sys
import types

sys.path.insert(0, "/usr/local/share/glsr/pym")

import MySQL
from Logging import err

__modulename__ = "Unknown"

class AbstractionLayer:

    def __init__(self, table):

        self._columns = None
        self._query = "SELECT %s FROM %s WHERE user_rank = " % (self._columns, table) + '%s'
        self._args = ("0")
        self._fetch = "all"
        self._count = 0

        self._cache = {}

    def reset(self):

        self._cache = {}
	self._columns = None

    def set_columns(self, columns):

        # No error checking here as we're trying to be quick,
        # let the MySQL module catch the error
        columns_str = ""
	count = 1

        for column in columns:
	    if count == len(columns):
	        columns_str += "%s" % column
	    else:
	        columns_str += "%s, " % column
            count += 1

        self._query = self._query.replace(str(self._columns), columns_str)
        self._columns = columns_str

        self._count = 0
	self._cache = {}

    def _perform(self):

        if self._columns == None:
	    err("No columns have been set", __modulename__) # reword
	    sys.exit(0)

        if len(self._cache) == 0:
            tmp = MySQL.Query(self._query, self._args, self._fetch)
            if type(tmp) == types.TupleType: # fetch = all
	        #print "tmp", tmp
                for item in tmp:
		    #print "item", item
                    for key in item.keys():
		        #print "key", key
			if not self._cache.has_key(key):
			    self._cache[key] = []
			self._cache[key].append(item[key])
                print self._cache
		
    def __contains__(self, item):

        for list in self._cache.values(): 
	    if item in str(list):
	        return True

        return False

    def __iter__(self):

        index = 0

        self._perform()

	# build a custom list to iter over
	iter_list = []

        print self._cache
        for i in range(len(self._cache) - 1):
	    print i
	    print "Append: %s" % ([self._cache.values()[i][i], self._cache.values()[i + 1][i]])
	    iter_list.append([self._cache.values()[i], self._cache])

        return iter(self._cache.values())

    def __repr__(self):

        return "%s(%s)" % (self.__class__.__name__, self._cache.values())

    def __call__(self):

        return self._cache.values()

    def __len__(self, column = None):

        if column == None:
            return len(self._cache)
	else:
	    return len(self._cache[column])

if __name__ == "__main__":

    UserTable = AbstractionLayer("glsr_user")

    UserTable.set_columns(["user_id", "user_alias"])
    print "!! Loop Test 1"
    for id, alias in UserTable:
        print "Id:", id, "Alias:", alias

    UserTable.set_columns(["user_id", "user_alias", "user_fullname"])
    print "\n!! Loop Test 2"
    for id, alias, fullname in UserTable:
        print "Id:", id, "Alias:", alias, "Fullname:", fullname

    print "\n!! Repr Test"
    print UserTable
    print "\n!! Membership Test"
    if "port001" in UserTable:
        print True
    else:
        print False
    print "\n!! Call Test"
    print UserTable()


