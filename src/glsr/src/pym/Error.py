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

__revision__ = '$Id: Error.py,v 1.15 2005/01/27 04:23:03 port001 Exp $'
__modulename__ = 'Error'

def error_uncaught(req):

    import os
    import sys
    import traceback
    from time import gmtime, strftime

    from jon.cgi import SequencingError

    import State
    import Config
    from Logging import logwrite
   
    (tbtype, value, traceb) = sys.exc_info()
    tblines = traceback.format_exception(tbtype, value, traceb)
    # FIXME: multine line statements are getting chopped off somewhere in the traceback module.
	
    exception_time = strftime('%d/%b/%Y %H:%M:%S', gmtime())
    logwrite(tblines, 'Unknown', 'Error', error_uncaught=True) 

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
    os.abort()

def error(msg, modname, extramsg=''):
    """
    Display internal error user, send it to the log and error report log
    """

    import os
    from time import gmtime, strftime

    import State
    import Config
    from Logging import logwrite

    logwrite(msg, modname, 'Error')
    cur_time = strftime("%d/%b/%Y %H:%M:%S", gmtime())

    if State.HTMLHeadersSent == False:      
        State.Req.set_header('Content-Type', 'text/html; charset=utf-8')
        State.Req.output_headers()
        State.HTMLHeadersSent = True

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

        if extramsg != '':
            output += ("""<br /><br />\n
                          <b>Further Details:</b><br /><br />\n
                          %s\n<br /><br />\n""" % extramsg)

        if modname == 'Template':
            output += ("""
            <br />
            <b>Template module recursion averted.</b>
            <br /><br />""")

        output += '<b>Execution terminated.<b><br /><br />'

    else:
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

    State.Req.write(output)
    
    # Only print the footer if we think the header got printed.
    # And don't print the footer if the error came from the Template module.
    if State.HeaderTmplSent == True and modname != 'Template':

        from Template import Template
        
        tmpl_footer = Template()
        tmpl_footer.param('GLSR_VERSION', Config.Version)
        tmpl_footer.param('GLSR_URL', Config.URL)
        tmpl_footer.param('CONTACT', Config.Contact)
        tmpl_footer.compile(Config.Template['footer'])

        State.Req.write(tmpl_footer.output())

    os.abort()

def error_user(title, description):
    """
    Present the user with a given error message.
    To be used for errors based on user input, not internal errors.
    """

    import os

    import Config
    from Template import Template

    if str(title) == '':
        raise ErrorModuleError, 'Zero length error title'
	
    if str(description) == '':
        raise ErrorModuleError, 'Zero length error description'

    tmpl_header = Template()
    tmpl_header.param('GLSR_URL', Config.URL)
    tmpl_header.param('USER_ALIAS', State.UserDetail['alias'])
    tmpl_header.param('USER_ID', State.UserDetail['uid'])
	
    if State.Domain == 'admin':
        tmpl.compile(Config.Template['admin_header'])
    else:
        tmpl.compile(Config.Template['header'])

    State.Req.write(tmpl_header.output())

    tmpl = Template()
    tmpl.param('ERROR_TITLE', title)
    tmpl.param('ERROR_DESCRIPTION', description)
    tmpl.compile(Config.Template['error_user'])
	
    State.Req.write(tmpl.output())

    tmpl_footer = Template()
    tmpl_footer.param('GLSR_VERSION', Config.Version)
    tmpl_footer.param('GLSR_URL', Config.URL)
    tmpl_footer.param('CONTACT', Config.Contact)
    tmpl_footer.compile(Config.Template['footer'])
	
    State.Req.write(tmpl_footer.output())

    os.abort()
