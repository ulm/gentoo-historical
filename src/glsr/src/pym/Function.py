# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Function.py,v 1.17 2005/01/27 04:19:15 port001 Exp $
#

from time import time

import State
import Config

__modulename__ = "Function"

def start_timer():

    return time()

def stop_timer():

    return time()

def eval_timer(start, end):

    return float(end - start)

def dprint(str):
    """ Used for printing debug statements to the screen """
    
    if not Config.Debug:
        return True

    if State.HTMLHeadersSent == False:
        print "Content-type:text/html\n\n"
        State.HTMLHeadersSent = True

    print "DEBUG:%s\n" % str
    return True

class _Values:

    def _store_params(self, params):

        self._params = params

    def getlist(self, key):

        list = []

        for key in self._params:
            list.append({key: self._params[key]})

        return list

    def getvalue(self, key, *args):

        if self._params.has_key(key):
            return self._params[key]
        else:
            if len(args) >= 1:
                return args[0]

            return None

    def keys(self):

        return self._params.keys()
        
    def has_key(self, key):

        if self._params.has_key(key):
            return True

        return False
