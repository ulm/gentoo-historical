# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: MySQL.py,v 1.9 2004/12/18 02:14:12 port001 Exp $
#

__modulename__ = "MySQL"

import sys
from time import strftime, gmtime

import MySQLdb
from _mysql_exceptions import MySQLError, OperationalError

import Config
import Const
from Logging import err, logwrite
from Function import start_timer, stop_timer, eval_timer

class MySQL:

    def __init__(self):

        self._db = None
        self._cursor = None
        self._t_start = 0
        self._fetch = ""
	self._result = None

    def _connect(self):

        try:
            self._db = MySQLdb.connect(host=Config.MySQL["host"],
                                 user=Config.MySQL["user"],
                                 passwd=Config.MySQL["passwd"],
                                 db=Config.MySQL["db"])
        except OperationalError, errmsg:
            err(errmsg, __modulename__)
            sys.exit(1)
                                                                        
        self._cursor = db.cursor(MySQLdb.cursors.DictCursor)

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
            err("%s<br />\nQuery: %s<br />\nValues: %s" % (errmsg, self._query, self._args),
                __modulename__)
            sys.exit(1)
                                                                                
        self._db.commit()
        
    def _get_result(self):
                                                                                                                                      
        if self._fetch == "one":
            self._result = self._cursor.fetchone()
            logwrite("""%s, Args: %s, Timing: %.5f(s)""" % (self._query, self._args, eval_timer(self._t_start, stop_timer())), __modulename__, "Query")
        elif self._fetch == "none":
            self._result = None
            logwrite("""%s, Args: %s, Timing: %.5f(s)""" % (self._query, self._args, eval_timer(self._t_start, stop_timer())), __modulename__, "Query")
        else:
            self._result = self._cursor.fetchall()
            logwrite("""%s, Args: %s, Timing: %.5f(s)""" % (self._query, self._args, eval_timer(self._t_start, stop_timer())), __modulename__, "Query") 

    def query(self, query, args=None, fetch="all"):
        """ Returns a list of dictionaries of {column: value} pairs.
        Each dictionary in the list represents one record for the query.
        e.g ({uid: 1043, name: Ian}, {uid: 3456, Scott})
        """

        self._query = query
        self._args = args
        self._fetch = fetch

        self._init_query()
        self._get_result()

        return self._result

    validate_args = classmethod(validate_args)

