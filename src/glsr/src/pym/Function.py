# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Function.py,v 1.3 2004/07/06 01:16:58 port001 Exp $
#

import traceback
from time import time, gmtime, strftime

import Config
import Template as TemplateHandler

__modulename__ = "Function"

def err(msg, modname):
    """Send given error message to logwrite(), display error message to
    user then report the error"""

    if Config.ErrorReporting == True:
    	try:
            fd = open(Config.ErrorReportLog, "a")
	    fd.write("%s %s %s\n" % (strftime("%d/%b/%Y %H:%M:%S", gmtime()), modname, msg))
	    fd.close()
	except:
	    pass

    logwrite(msg, modname, "Error")
  
    if Config.HTMLHeadersSent == False:      
        print "Content-type:text/html\n\n"

    if Config.Debug == True:
        print ("<table align=\"center\" width=\"90%\">\n" +
		   "<tr>\n" +
                     "<td align=\"left\">\n" +
		       "<br />\n" +
                       "<font color=\"FF0000\"><b>Debug Mode</b></font>\n" +
		       "<br /><br />\n" +
	  	       "<b>Internal Error</b> (in module '%s')<b>:</b>\n" % modname +
		       "<br /><br />\n" +
		       "%s\n" % msg +
                       "<br /><br />\n" +
		       "<b>Traceback:</b>\n" +
		       "<br /><br />\n")

        tb = traceback.format_stack(None)
	for line in tb:
            print line.replace("\n", "<br>")
		
	print ("     <br />\n" +
		    "</td>\n" +
		  "</tr>\n" +
	       "</table>\n")
		       
    else:
        time = strftime("%d/%b/%Y %H:%M:%S", gmtime())

        print ("<table align=\"center\" width=\"90%\">\n" +
                   "<tr>\n" +
                     "<td align=\"left\">\n" +
                       "<br />\n" +
		       "<b>Ooops!</b>\n" + 
		       "<br /><br />\n" +
                       "It looks like you've encountered an internal error!\n" +
		       "<br /><br />\n")
        
        if Config.ErrorReporting == True:
            print "This error has been reported to the administration.\n"
	else:              
            print "Please contact <b>%s</b> and quote the time '<b>%s</b>'" % (Config.Contact, time)

        print ("     <br />\n" +
                    "</td>\n" +
                  "</tr>\n" +
               "</table>\n")

    if Config.HTMLHeadersSent == True:
        # Only print the footer if we think the header got printed.
        FooterTemplate = TemplateHandler.New()
        FooterTemplate.Compile(Config.Template["footer"],
                           {"GLSR_VERSION":     Config.Version,
                            "CONTACT":          Config.Contact})
        FooterTemplate.Print()
    
def logwrite(msg, modname, type):
    """Write Given message to a log file
       Type can be: Error, Query, Info"""
                                                                                                                                   
    logtype = ""
                                                                                                                                   
    if Config.Logging == True:
                                                                                                                                   
        if type.lower() == "error":
            logtype = "error"
        elif type.lower() == "query":
            logtype = "query"
        elif type.lower() == "info":
            logtype = "info"
        else:
            logtype = "????"
                                                                                                                                   
        try:
            fd = open(Config.LogFile, "a")
            fd.write("[%s] [%s] [%s] %s\n" % (strftime("%d %b %Y %H:%M:%S", gmtime()),
                                              logtype, modname, msg))
            fd.close()
        except:
            pass

def start_timer():

    return time()

def stop_timer():

    return time()

def eval_timer(start, end):

    return float(end - start)
