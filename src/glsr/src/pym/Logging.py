# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#

import traceback
from time import gmtime, strftime

import State
import Config

__revision__ = '$Id: Logging.py,v 1.16 2005/01/26 22:15:03 port001 Exp $'
__modulename__ = 'Logging'

def FlushErrorReportLog():
    """Blank the ErrorReport log"""

    try:
        fd = open(Config.ErrorReportLog, 'w')
        fd.close()
    except:
        pass

def logwrite(msg, modname, type, error_uncaught=False):
    """
	Write given message to the log file and error log if required.
    Type can be: Error, Query, Info, Warn
	"""

    logtime = gmtime()
    logtype = ''

    if type.lower() == 'error':
        logtype = 'error'
    elif type.lower() == 'query':
        logtype = 'query'
    elif type.lower() == 'info':
        logtype = 'info'
    elif type.lower() == 'warn':
        logtype = 'warn'
    else:
        logtype = '????'

    if Config.Logging == True:

        if isinstance(msg, list):
            msg = "".join(msg)

        try:
            fd = open(Config.LogFile, 'a')
            fd.write("[%s] [%s] [%s] %s\n" %
                     (strftime('%d %b %Y %H:%M:%S', logtime),
                      logtype, modname, msg))
            fd.close()
        except IOError:
            pass

    if Config.ErrorReporting == True and logtype == 'error':
	# FIXME: log warnings also
	
        contents = []

        try:
            readfd = open(Config.ErrorReportLog, 'r')
            contents = readfd.readlines()
            readfd.close()
        except IOError:
            pass

        try:
            writefd = open(Config.ErrorReportLog, 'w')
            if error_uncaught == True:
            # FIXME: Print the traceback directly to log
                writefd.write("%s||Unknown||Uncaught exception, see glsr.log entry for this date and time.\n" \
			                                                        % strftime('%d %b %Y %H:%M:%S', logtime))
            else:
                writefd.write("%s||%s||%s\n" % (strftime('%d %b %Y %H:%M:%S', logtime),
                                                                         modname, msg))
            writefd.write(''.join(contents))
            writefd.close()
        except IOError:
            pass

def ReturnErrorReports(list_offset):

    reports = []
    count = 0

    try:
        fd = open(Config.ErrorReportLog, 'r')
        contents = fd.readlines()
        fd.close()
    except:
        return False

    row = 'even'
    for line in contents:
        
        if line == '\n':
            continue

        if count == list_offset:
            break

        try:
            (date, module, error) = line.split('||', 2)
            reports.append({'row': row, 'date': date, 'module': module,
                            'error': error.strip()})
        except:
            reports.append({'row': row, 'date': 'N/A', 'module': 'N/A',
                            'error': 'Corrupt report'})

        if row == 'even':
            row = 'odd'
        else:
            row = 'even'

        count += 1

    if not len(reports):
        return False

    return reports
