# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Function.py,v 1.1.1.1 2004/06/04 06:38:37 port001 Exp $
#

import Config
from time import time, gmtime, strftime

__modulename__ = "Function"
__productname__ = "glsr"

clockwatch = 0

def err(msg):
    """Send given error message to logwrite() then display error message to
    user"""
    
    logwrite(msg, "Error")
    Template.err(msg)
    
def logwrite(msg, type):
    """Write Given message to a log file"""
    
    if Config.Logging == "Yes":
        if ((Config.Logtype == "All" and (type == "All" or type == "Error")) or
            (Config.Logtype == "Error" and type == "Error")):
            
            fd = open(Config.LogFile, "a")
            fd.write("%s %s: %s\n" % (strftime("%d/%b/%Y %H:%M:%S", gmtime()),
                                      __productname__, msg))
            fd.close()

def start_timer():

    return time()

def stop_timer():

    return time()

def eval_timer(start, end):

    return float(end - start)

def traceback():
    
    import traceback

    # Incase headers haven't been sent yet.
    print "Content-type:text/html\n\n"

    print "<b>Traceback:</b><br><br>"
    print ("<table align=\"center\" width=\"80%\"><tr><td align=\"left\">" +
           "<font size=\"3\">")
    tb = traceback.format_stack(None)
    for line in tb:
        print line.replace("\n", "<br>")
    print "</td></tr></table>"


