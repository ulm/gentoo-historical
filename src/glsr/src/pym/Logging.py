# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Logging.py,v 1.8 2004/09/30 03:03:46 hadfield Exp $
#

import traceback
from time import gmtime, strftime

import Config

__modulename__ = "Logging"

def err(msg, modname):
    """Displays and records errors.

    Send given error message to logwrite(), display error message to
    user then report the error.
    """

    if Config.ErrorReporting == True:
        try:
            fd = open(Config.ErrorReportLog, "a")
            fd.write("%s||%s||%s\n" % (strftime("%d %b %Y %H:%M:%S", gmtime()),
                                       modname, msg))
            fd.close()
        except:
            pass

    logwrite(msg, modname, "Error")
  
    if Config.HTMLHeadersSent == False:      
        print "Content-type:text/html\n\n"
        Config.HTMLHeadersSent = True

    output = ("""
    <table align="center" width="90%">
      <tr>
        <td align="left">
          <br />""")
    
    if Config.Debug == True:
        output += ("""
          <font color="FF0000"><b>Debug Mode</b></font>
          <br /><br />""")

        output += "<b>Internal Error</b> (in module '%s')<b>:</b>\n" % modname
        output += "<br /><br />\n%s\n" % msg
        output += ("""
           <br /><br />
           <b>Traceback:</b>
           <br /><br />""")

        tb = traceback.format_stack(None)
        for line in tb[:-1]:
            print line.replace("\n", "<br>")
        
        if modname == "Template":
            output += ("""
            <br />
            <b>Template module recursion averted.</b>
            <br /><br />""")

    else:
        cur_time = strftime("%d/%b/%Y %H:%M:%S", gmtime())

        output += ("""
           <b>Ooops!</b>
           <br /><br />
           It looks like you've encountered an internal error!
           <br /><br />""")
        
        if Config.ErrorReporting == True:
            output += "This error has been reported to the administration.\n"
        
        else:              
            output += ("Please contact <b>%s</b> and quote the time " %
                       Config.Contact + "'<b>%s</b>'" % cur_time)

    output += ("""
           <br />
         </td>
       </tr>
     </table>""")

    print output
    
    # Only print the footer if we think the header got printed.
    # And don't print the footer if the error came from the Template module.
    if Config.HTMLHeadersSent == True and modname != "Template":
        import Template as TemplateHandler

        FooterTemplate = TemplateHandler.Template()
        FooterTemplate.compile(Config.Template["footer"],
                               {"GLSR_VERSION":     Config.Version,
                                "CONTACT":          Config.Contact})
        print FooterTemplate.output()

    
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

        if isinstance(msg, list):
            msg = "".join(msg)

        try:
            fd = open(Config.LogFile, "a")
            fd.write("[%s] [%s] [%s] %s\n" %
                     (strftime("%d %b %Y %H:%M:%S", gmtime()),
                      logtype, modname, msg))
            fd.close()
        except:
            pass

def ReturnErrorReports():

    Reports = []

    try:
        fd = open(Config.ErrorReportLog, "r")
        contents = fd.readlines()
        fd.close()
    except:
        return False

    row = "even"
    for line in contents:
        
        if line == "\n":
            continue

        try:
            (date, module, error) = line.split("||", 2)
            Reports.append({"row": row, "date": date, "module": module,
                            "error": error.strip()})
        except:
            Reports.append({"row": row, "date": "N/A", "module": "N/A",
                            "error": "Corrupt report"})

        if row == "even":
            row = "odd"
        else:
            row = "even"

    if not len(Reports):
        return False

    return Reports
