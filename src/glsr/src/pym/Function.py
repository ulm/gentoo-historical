# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Function.py,v 1.6 2004/07/19 00:54:47 hadfield Exp $
#

from time import time

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

    if Config.HTMLHeadersSent == False:
        print "Content-type:text/html\n\n"
        Config.HTMLHeadersSent = True

    print "DEBUG:%s\n" % str
    return True
