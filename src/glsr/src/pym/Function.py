# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Function.py,v 1.9 2004/11/10 16:27:05 port001 Exp $
#

import sys
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

class stderr_redirect:

    def write(self, msg):

        if Config.Debug == True:

            if Config.HTMLHeadersSent == False:
                print "Content-type:text/html\n\n"
                Config.HTMLHeadersSent = True

            print "<font color=\"FF0000\"><b>DEBUG:</b></font> %s <br />" % msg.strip()
        
        else:
            sys.__stderr__.write(msg)
