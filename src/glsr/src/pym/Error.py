# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Error.py,v 1.1 2004/07/24 01:54:35 port001 Exp $
#

""" This module is considered fail proof, i.e. its not allowed to break,
    because things that break depend on these functions. 
    imports also go in each function where needed, just to reduce
    the possibility of breakage from importing a dodgy module
    a function might not use. """

__modulename__ = "Error"

def ExceptionHandler(type, value, tb):
    """ Print uncaught exceptions to stdout; glsr style. """

    import traceback
    from time import gmtime, strftime

    import Config
    from Logging import logwrite

    lines = traceback.format_exception(type, value, tb)

    if Config.ErrorReporting == True:
        try:
            fd = open(Config.ErrorReportLog, "a")
            fd.write("%s||Unknown||Uncaught exception, see glsr.log entry for this date and time.\n" % strftime("%d %b %Y %H:%M:%S", gmtime()))
            fd.close()
        except:
            pass

    if Config.Logging == True:
        logwrite(lines, "Unknown", "Error") 

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
                       "<b>Internal Error</b> (Uncaught exception)<b>:</b>\n" +
                       "<br /><br />\n" +
                       "<b>Traceback:</b>\n" +
                       "<br /><br />\n")

        for line in lines[1:-1]:
            print line.replace("\n", "<br>").replace(" ", "&nbsp;")

        print ("     <b>Exception:</b>\n" +
               "     <br /><br />\n")

        print lines[-1].replace("\n", "<br>").replace(" ", "&nbsp;")

        print ("     <br /><br />\n" +
               "     <b>Execution terminated.<b>\n" +
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

