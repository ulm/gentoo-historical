#!/usr/bin/python
                                                                                                                                                                                         
import cgi
import os
import sys

sys.path.insert(0, "/usr/lib/glsr/pym")
                                                                                                                                                                                         
import Auth
import Session as SessionHandler

ThisSession = SessionHandler.New()
ThisSession.SetCookie(1, "0o36O6NFntO1GM1QIlJ6UGWB934XU1")
                                                                                                                                                                                         
print "Content-Type: text/html\n\n"

print "<b>Sent Cookie Data:</b>\n<br>"
ThisSession.SetCookie(1, "0o36O6NFntO1GM1QIlJ6UGWB934XU1")
                                                                                                                                                                                         
print "<br><br><b>Returned Cookie Data:</b>\n<br>"                                                                                                                                                     

try:
    parp =  os.environ["HTTP_COOKIE"]
except KeyError:
    print "No cookie data returned!" 
else:
    print parp   
