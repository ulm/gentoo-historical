# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#

""" This module is considered fail proof, i.e. its not allowed to break,
    because things that break depend on these functions. 
    imports also go in each function where needed, just to reduce
    the possibility of breakage from importing a dodgy module
    a function might not use. """

__revision__ = "$Id: Error.py,v 1.5 2004/11/14 23:00:31 port001 Exp $"
__rating__ = "9.09/10"
__modulename__ = "Error"

def exception_handler(tbtype, value, traceb):
    """ Print uncaught exceptions to stdout; glsr style. """

    import traceback
    from time import gmtime, strftime

    import State
    import Config
    from Logging import logwrite

    lines = traceback.format_exception(tbtype, value, traceb)

    if Config.ErrorReporting == True:

        contents = []

        try:
            readfd = open(Config.ErrorReportLog, "r")
            contents = readfd.readlines()
            readfd.close()
        except IOError:
            pass

        try:
            writefd = open(Config.ErrorReportLog, "w")
            writefd.write("%s||Unknown||Uncaught exception, see glsr.log entry for this date and time.\n" \
                            % strftime("%d %b %Y %H:%M:%S", gmtime()))
            writefd.write("".join(contents))
            writefd.close()
        except IOError:
            pass

    if Config.Logging == True:
        logwrite(lines, "Unknown", "Error") 

    if State.HTMLHeadersSent == False:
        print "Content-type:text/html\n\n"
        State.HTMLHeadersSent = True

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
            print "Please contact <b>%s</b> and quote the time '<b>%s</b>'" \
                   % (Config.Contact, time)

        print ("     <br />\n" +
                    "</td>\n" +
                  "</tr>\n" +
               "</table>\n")

