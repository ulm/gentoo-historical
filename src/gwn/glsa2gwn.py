#!/usr/bin/python

from xml.dom.ext.reader.Sax2 import FromXmlStream
from urllib2 import urlopen
from os.path import basename
import sys

def getText(nodelist):
  lst = []
  for node in nodelist:
    if node.nodeType == node.TEXT_NODE:
      lst.append(node.data)

    return ''.join(lst)

if (len(sys.argv) <= 1):
  print "usage: " + basename(sys.argv[0]) + " files"
  print "if the files are URIs remember to add '?passthru=1' to the end"
  sys.exit(1)
else:
  files = sys.argv[1:len(sys.argv)]

for file in files:
  if file.startswith("http://"):
    fp = urlopen(file)
  else:
    fp = open(file,'r')
  dom = FromXmlStream(fp)

  title = dom.getElementsByTagName('title') [0]

  print "<section>"
  print "<title>" + getText(title.childNodes) + "</title>"
  print "<body>"
  print ""

  synopsis = dom.getElementsByTagName('synopsis') [0]

  print "<p>"
  print getText(synopsis.childNodes)
  print "</p>"
  print ""

  id = dom.getElementsByTagName('glsa') [0].getAttribute('id')

  print "<p>"
  print 'For more information, please see the'
  print '<uri link="http://www.gentoo.org/security/en/glsa/glsa-' + id + '.xml">'
  print 'GLSA Announcement</uri>'
  print "</p>"
  print ""
  print "</body>"
  print "</section>"
  print ""
