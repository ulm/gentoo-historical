# Copyright 2004-2005 Ian Leitch
# Copyright 1999-2005 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = '$Id: MySQL.py,v 1.13 2005/01/27 04:19:15 port001 Exp $'
__modulename__ = 'MySQL'

from time import strftime, gmtime

import MySQLdb
from _mysql_exceptions import MySQLError, OperationalError

import Const
import Config
from Logging import logwrite
from GLSRException import MySQLModuleError
from Function import start_timer, stop_timer, eval_timer

class MySQL:

    def __init__(self):

        self._db = None
        self._cursor = None
        self._t_start = 0
        self._fetch = ""

    def _connect(self):

        try:
            self._db = MySQLdb.connect(host=Config.MySQL["host"],
                                 user=Config.MySQL["user"],
                                 passwd=Config.MySQL["passwd"],
                                 db=Config.MySQL["db"])
        except OperationalError, errmsg:
            raise MySQLModuleError("Caught an OperationError exception from module 'MySQLdb'", errmsg)
                                                                        
        self._cursor = self._db.cursor(MySQLdb.cursors.DictCursor)

    def validate_args(self):
        """
        A last ditch effort to make sure that no database inputs are too long.
        """
	
        retval = []
	
        for key,val in self._args.iteritems():
            retval.append(val[:Const.FIELD_LEN[table][key]])
        return retval

    def _init_query(self):

        self._t_start = start_timer()
        self._connect()

        try:
            self._cursor.execute(self._query, self._args)
        except MySQLError, errmsg:
            raise MySQLModuleError("Caught an MySQLError exception from module 'MySQLdb'", 
                                   "%s<br />\nQuery: %s<br />\nValues: %s" % (errmsg, self._query, self._args))
                                                                                
        self._db.commit()
        
    def _get_result(self):

        if self._fetch == "one":
            logwrite("""%s, Args: %s, Timing: %.5f(s)""" % (self._query, self._args, eval_timer(self._t_start, stop_timer())), __modulename__, "Query")
            return self._cursor.fetchone()
        elif self._fetch == "none":
            self._result = None
            logwrite("""%s, Args: %s, Timing: %.5f(s)""" % (self._query, self._args, eval_timer(self._t_start, stop_timer())), __modulename__, "Query")
            return None
        else:
            logwrite("""%s, Args: %s, Timing: %.5f(s)""" % (self._query, self._args, eval_timer(self._t_start, stop_timer())), __modulename__, "Query") 
            return self._cursor.fetchall()

    def query(self, query, args=None, fetch="all"):
        """ Returns a list of dictionaries of {column: value} pairs.
        Each dictionary in the list represents one record for the query.
        e.g ({uid: 1043, name: Ian}, {uid: 3456, Scott})
        """

        self._query = query
        self._args = args
        self._fetch = fetch

        self._init_query()
        return self._get_result()

    validate_args = classmethod(validate_args)

