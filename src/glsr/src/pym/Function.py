# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Function.py,v 1.12 2004/12/25 21:05:03 port001 Exp $
#

import sys
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

class stderr_redirect:

    def write(self, msg):

        if Config.Debug == True:

            if State.HTMLHeadersSent == False:
                print "Content-type:text/html\n\n"
                State.HTMLHeadersSent = True

            print "<font color=\"FF0000\"><b>DEBUG:</b></font> %s <br />" % str(msg).strip()
        
        else:
            sys.__stderr__.write(msg)

def values(self, key, *args):

    if self.params.has_key(key):
        return self.params[key]
    else:
        if len(args) >= 1:
            return args[0]

        return None
