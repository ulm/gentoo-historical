#!/usr/bin/python

from xml.dom.ext.reader.Sax2 import FromXmlStream
import sys

def getText(nodelist):
  lst = []
  for node in nodelist:
    if node.nodeType == node.TEXT_NODE:
      lst.append(node.data)

    return ''.join(lst)

fp = open(sys.argv[1],'r')
dom = FromXmlStream(fp)

title = dom.getElementsByTagName('title') [0]

print "<section>"
print "<title>" + getText(title.childNodes) + "</title>"
print "<body>"

synopsis = dom.getElementsByTagName('synopsis') [0]

print "<p>"
print getText(synopsis.childNodes)
print "</p>"

id = dom.getElementsByTagName('glsa') [0].getAttribute('id')

print "<p>"
print 'For more information, please see the <uri link="http://www.gentoo.org/security/en/glsa/glsa-' + id + '.xml">GLSA Announcement</uri>'
print "</p>"

print "</body>"
print "</section>"

