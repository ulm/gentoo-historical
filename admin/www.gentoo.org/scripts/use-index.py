#!/usr/bin/python

import os,sys
import portage
import string
import time

if not os.environ["WEBROOT"]:
	print "$WEBROOT not set; exiting"
	sys.exit(1)
outpath=os.environ["WEBROOT"]+"/dyn"
outfn=outpath+"/use-index.xml"
if not os.path.exists(outpath):
	os.makedirs(outpath)
outfile=open(outfn,"w")
outfile.write("""<?xml version='1.0'?>
<?xml-stylesheet href="/xsl/guide.xsl" type="text/xsl"?>
<guide link="/use.html"><title>Gentoo Linux Use Variable Descriptions</title>
<version>1.0</version><date>"""+time.asctime(time.localtime())+"""</date><chapter><title>Use Descriptions</title>
<section><body><p>A small table of currently available use variables and a short description of each</p><table>
<tr><th>Variable</th><th>Description</th></tr>""")
infn=portage.settings["PORTDIR"]+"/profiles/use.desc"
infile=open(infn,"r")
infilelines=infile.readlines()
infile.close()
for ln in infilelines:
	if len(ln)==1:
		continue
	if ln[0]=="#":
		continue
	lnsplit=string.split(ln," ")
	lnkey=lnsplit[0]
	lndes=string.join(lnsplit[2:]," ")
	outfile.write("<tr><ti>"+lnkey+"</ti><ti>"+lndes+"</ti></tr>\n")
outfile.write("</table></body></section></chapter></guide>\n")
outfile.close()
print "USE index generated :)"
