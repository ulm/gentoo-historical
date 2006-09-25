#!/usr/bin/env python
#Usage: gwnproc.py foo.xml
import os, sys, popen2, string
sourcetext=open(sys.argv[1], 'r').read()
os.popen(r"""ex -n +'%s/[\n\t]/ /g' +'%s/[ ]\+/ /g' +'%s/\(<[^\/][^>]\?>\) /\1/g' +'%s/<\/\([^>]\+\)>/<\/\1>/g' +'%s/<uri link="#[^>]\+>\([^<]\+\)<\/uri>/\1/g' +'%s/<uri>\([^<]\+\)<\/uri>/\1/g' +'%s/<mail link="\([^"]\+\)">\1<\/mail>/\1/g' +'w!temp.xml' +'q!' """+sys.argv[1])
processedtext=open('temp.xml', 'r').read()
newtext=""

try:
	while 1:

		i=sourcetext.index('<pre')
		j=sourcetext.index('</pre>')
		l=sourcetext[i:].index('>')

		i2=processedtext.index('<pre')
		j2=processedtext.index('</pre>')

		pres=sourcetext[i+l+1:j].split('\n')
		count=0
		for k in pres:
			pres[count]="|"+k
			count=count+1
		newtext=newtext+processedtext[0:i2]
		newtext=newtext+sourcetext[i:i+l+1]+string.join(pres,'\n')+'</pre>'
		sourcetext=sourcetext[j+6:]
		processedtext=processedtext[j2+6:]
except ValueError:
	newtext=newtext+processedtext
xsltout,xsltin=popen2.popen2('xsltproc ~/scripts/email2.xsl -|fold -s -w75')
xsltin.write(newtext)
xsltin.close()
newtext=xsltout.read()
xsltlines=newtext.split('\n')
count=0
for i in xsltlines:
	if i=='=':
		xsltlines[count]=xsltlines[count+2]='='*len(xsltlines[count+1])
		count=count+1
	elif i=='-':
		xsltlines[count]='-'*len(xsltlines[count-1])
		count=count+1
	elif len(i)>0 and i[0]=='|':
		xsltlines[count]=xsltlines[count]+' '*(74-len(xsltlines[count]))+'|'
		count=count+1
	else:
		count=count+1

print string.join(xsltlines, '\n')

