# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: MySQL.py,v 1.6 2004/07/24 19:03:28 hadfield Exp $
#

import sys
from time import strftime, gmtime
from _mysql_exceptions import MySQLError, OperationalError

import Config

if Config.Memcache == True:
    import memcache

import Const
import MySQLdb
from Function import start_timer, stop_timer, eval_timer
from Logging import err, logwrite
import Template as TemplateHandler

__modulename__ = "MySQL"

def Connect():
    try:
        db = MySQLdb.connect(host=Config.MySQL["host"],
                             user=Config.MySQL["user"],
                             passwd=Config.MySQL["passwd"],
                             db=Config.MySQL["db"])
    except OperationalError, errmsg:
        err(errmsg, __modulename__)
        sys.exit(1)

    return db.cursor(MySQLdb.cursors.DictCursor), db

def ValidateArgs(table, args):
    """ A last ditch effort to make sure that no database inputs are too
    long. """
    retval = []
    for key,val in args.iteritems():
        retval.append(val[:Const.FIELD_LEN[table][key]])
    return retval

def Query(query, args=None, fetch="all"):
    """ Returns a list of dictionaries of {column: value} pairs.
    Each dictionary in the list represents one record for the query.
    e.g ({uid: 1043, name: Ian}, {uid: 3456, Scott})
    """
    
    return _Fetch(_InitQuery(query, args), query, args, fetch)


def _InitQuery(query, args):
    t_start = start_timer()
    cursor, db = Connect()
    
    try:
        cursor.execute(query, args)
    except MySQLError, errmsg:
        err("%s<br />\nQuery: %s<br />\nValues: %s" % (errmsg, query, args),
            __modulename__)
        sys.exit(1)

    db.commit()
    return cursor, t_start

def _Fetch((cursor, t_start), query, args, fetch):
    if fetch == "one":
        result = cursor.fetchone()
        logwrite("""%s, Args: %s, Timing: %.5f(s)""" % (query, args, eval_timer(t_start, stop_timer())), __modulename__, "Query")
    elif fetch == "none":
        logwrite("""%s, Args: %s, Timing: %.5f(s)""" % (query, args, eval_timer(t_start, stop_timer())), __modulename__, "Query")
        return
    else:
        result = cursor.fetchall()
        logwrite("""%s, Args: %s, Timing: %.5f(s)""" % (query, args, eval_timer(t_start, stop_timer())), __modulename__, "Query")

    return result        
