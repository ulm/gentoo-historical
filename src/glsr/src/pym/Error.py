# Copyright 2004-2005 Ian Leitch
# Copyright 1999-2005 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#

"""
This module is considered fail proof, i.e. its not allowed to break,
because things that break depend on these functions. 
imports also go in each function where needed, just to reduce
the possibility of breakage from importing a dodgy module
a function might not use.
"""

__revision__ = '$Id: Error.py,v 1.8 2005/01/26 05:37:02 port001 Exp $'
__modulename__ = 'Error'

def error_tb(req):

    import sys
    import traceback
    from time import gmtime, strftime

    from jon.cgi import SequencingError

    import Config
    from Logging import logwrite

    try:
	req.clear_output()
    except SequencingError:
        pass

    exception_time = strftime("%d/%b/%Y %H:%M:%S", gmtime())
    
    (tbtype, value, traceb) = sys.exc_info()
    tblines = traceback.format_exception(tbtype, value, traceb)
    # FIXME: multine line statements are getting chopped off somewhere in the traceback module.

    if Config.ErrorReporting == True:
    # FIXME: Print the exception directly to the ErrorReportLog so we don't need to rely on Logging to be enabled
    # Need to sort out the html for viewing errors first though.

        contents = []

        try:
            readfd = open(Config.ErrorReportLog, 'r')
            contents = readfd.readlines()
            readfd.close()
        except IOError:
            pass

        try:
            writefd = open(Config.ErrorReportLog, 'w')
	    if Config.Logging == True:
                writefd.write("%s||Unknown||Uncaught exception, see glsr.log entry for this date and time.\n" \
                               % exception_time)
	    else:
	        writefd.write("%s||Unknown||Uncaught exception. Logging has been disabled!\n" \
                               % exception_time) # see above FIXME
            writefd.write(''.join(contents))
            writefd.close()
        except IOError:
            pass

    if Config.Logging == True:
        logwrite(tblines, 'Unknown', 'Error') 

    if Config.Debug == True:
        req.write("""<table align="center" width="90%">\n
                     <tr>\n
                     <td align="left">\n
                     <br />\n
                     <font color="FF0000"><b>Debug Mode</b></font>\n
                     <br /><br />\n
                     <b>Internal Error</b> (Uncaught exception)<b>:</b>\n
                     <br /><br />\n
		  """)

        req.write("""<b>Exception:</b>\n 
                     <br /><br />\n
	          """)

        req.write(tblines[-1].replace('\n', '<br />').replace(' ', '&nbsp;'))
	    
        req.write("""<br />
	             <b>Traceback:</b>\n
                     <br /><br />\n
	          """)
		      
        for line in tblines:
	    req.write(line.replace('\n', '<br />').replace(' ', '&nbsp;'))

        req.write("""<br /><br />\n
                     <b>Execution terminated.<b>\n
                     </td>\n
                     </tr>\n
                     </table>\n
	          """)
    else:
        req.write("""<table align="center" width="90%">\n
                     <tr>\n
                     <td align="left">\n
                     <br />\n
                     <b>Ooops!</b>\n
                     <br /><br />\n
                     It looks like you've encountered an internal error!\n
                     <br /><br />\n
    	          """)

        if Config.ErrorReporting == True:
            req.write('This error has been reported to the administration.\n')
        else:
            req.write("Please contact <b>%s</b> and quote the time '<b>%s</b>'" \
                       % (Config.Contact, exception_time))

        req.write("""<br />\n
                     </td>\n
                     </tr>\n
                     </table>\n
                  """)
