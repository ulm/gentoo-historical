#!/usr/bin/python
                                                                                                                                                                                         
import cgi
import os
import sys

sys.path.insert(0, "/usr/lib/glsr/pym")
                                                                                                                                                                                         
import Auth
import Session as SessionHandler
ThisSession = SessionHandler.New()
ThisSession.RemoveCookie()                                                                                                                                                         
                                                                                                                                                                                         
print "Content-Type: text/html\n\n"

                                                                                                                                                                          
print "<br><br><b>Returned Cookie Data:</b>\n<br>"                                                                                                                                                     

try:
    parp =  os.environ["HTTP_COOKIE"]
except KeyError:
    print "Cookie removed!" 
else:
    print parp   
