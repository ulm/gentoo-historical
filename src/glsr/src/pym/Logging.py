# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Logging.py,v 1.4 2004/07/19 00:55:24 hadfield Exp $
#

import traceback
from time import time, gmtime, strftime

import Config

__modulename__ = "Logging"

def err(msg, modname):
    """Send given error message to logwrite(), display error message to
    user then report the error"""

    if Config.ErrorReporting == True:
    	try:
            fd = open(Config.ErrorReportLog, "a")
	    fd.write("%s||%s||%s\n" % (strftime("%d %b %Y %H:%M:%S", gmtime()), modname, msg))
	    fd.close()
	except:
	    pass

    logwrite(msg, modname, "Error")
  
    if Config.HTMLHeadersSent == False:      
        print "Content-type:text/html\n\n"
        Config.HTMLHeadersSent = True

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
	for line in tb[:-1]:
            print line.replace("\n", "<br>")
		
        if modname == "Template":
            print ("<br />\n" +
                     "<b>Template module recursion averted.</b>\n" +
                   "<br /><br />\n")

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

    # Only print the footer if we think the header got printed.
    if Config.HTMLHeadersSent == True:
        # Don't print the footer if the error came from the Template module.
        if modname != "Template":
            import Template as TemplateHandler

            FooterTemplate = TemplateHandler.New()
            FooterTemplate.Compile(Config.Template["footer"],
                                   {"GLSR_VERSION":     Config.Version,
                                    "CONTACT":          Config.Contact})
            FooterTemplate.Print()
    
def FlushErrorReportLog():
    """Blank the ErrorReport log"""

    try:
        fd = open(Config.ErrorReportLog, "w")
	fd.close()
    except:
	pass

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

def ReturnErrorReports():

    Reports = []
    row = "even"

    try:
        fd = open(Config.ErrorReportLog, "r")
        contents = fd.readlines()
        fd.close()
    except:
        return False

    for line in contents:
        if line == "\n":
            continue

        try:
            (date, module, error) = line.split("||", 2)
            Reports.append({"row": row, "date": date, "module": module, "error": error.strip()})
        except:
            Reports.append({"row": row, "date": "N/A", "module": "N/A", "error": "Corrupt report"})

        if row == "even":
            row = "odd"
        else:
            row = "even"

    if not len(Reports):
        return False

    return Reports
