# Copyright 2004-2005 Ian Leitch
# Copyright 1999-2005 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = '$Id: mysql.py,v 1.1 2005/03/27 04:02:34 hadfield Exp $'
__modulename__ = 'mysql'

import MySQLdb
from _mysql_exceptions import MySQLError, OperationalError
import types

#from Logging import logwrite
#from GLSRException import MySQLModuleError
#from Function import start_timer, stop_timer, eval_timer

DEFAULT_PORT = 3308

class MySQL:

    def __init__(self, parameters):
        """Initialize the MySQL object.
        
        'parameters' should be a dict containing the following variables:
          host   - The database host server
          port   - The port the database is running on. (optional)
          user   - The username to connect with
          passwd - The password to connect with
          db     - The name of the database
        """
        
        self._db = None
        self._cursor = None
        self._fetch = ""
        self._args = None
        self._query = None
        self._parameters = parameters

        if not self._parameters.has_key("port") \
           or not isinstance(self._parameters["port"], types.IntType):
            self._parameters["port"] = DEFAULT_PORT
        

    def _connect(self):
        """Connect to the mysql database."""
        
        try:
            self._db = MySQLdb.connect(
                host   = self._parameters["host"],
                port   = self._parameters["port"],
                user   = self._parameters["user"],
                passwd = self._parameters["passwd"],
                db     = self._parameters["db"])
        
        except OperationalError, errmsg:
            raise MySQLModuleError(
                "Caught an OperationError exception from module 'MySQLdb'",
                errmsg)
                                                                        
        self._cursor = self._db.cursor(MySQLdb.cursors.DictCursor)

    def _init_query(self):

        self._connect()

        try:
            self._cursor.execute(self._query, self._args)
        
        except MySQLError, errmsg:
            raise MySQLModuleError(
                "Caught an MySQLError exception from module 'MySQLdb'%s",
                "%s<br />\nQuery: %s<br />\nValues: %s" %
                (errmsg, self._query, self._args))

        self._db.commit()
        
    def _get_result(self):

        retval = None
        
        if self._fetch == "one":
            retval = self._cursor.fetchone()
        elif self._fetch == "none":
            retval = None
        else:
            retval = self._cursor.fetchall()

        return retval

    def query(self, query, args = None, fetch = "all"):
        """Runs the specified query with 'args'.

        Returns a list of dictionaries of {column: value} pairs.
        Each dictionary in the list represents one record for the query.
        e.g ({uid: 1043, name: Ian}, {uid: 3456, Scott})
        """

        self._query = query
        self._args = args
        self._fetch = fetch

        #t_start = start_timer()

        self._init_query()
        result = self._get_result()

        #logwrite("%s, Args: %s, Timing: %.5f(s)" %
        #         (self._query, self._args,
        #          eval_timer(t_start, stop_timer()))
        #         __modulename__, "Query")
        
        return result


# FIXME: This exception is only here until exception handling is properly setup
class MySQLModuleError(Exception): pass
