#!/usr/bin/python -OO

import sys
import config
import ebuilddb
import gentoo
import os
import time
from genarchbar import genarchbar

print 'Status: 200 Ok'
print 'Content-type: text/html'
print

def error():
	print ('<div class="centerpage">\n'
	'<table class="ebuild">\n'
	'<tr><td class="fields">Error in request</td></tr><br>\n'
	'<tr><td class="item"><img src="%s/?category=generic" align="right" alt="">'
	'<p>An error was encountered processing your request.  Request a '
	'different page or check the <a href="%s">packages.gentoo.org main page</a>.'
	'</p></td></tr>'
	'</table>'
	'</div>') % (config.ICONS,config.FEHOME)

try:
	uri = os.environ['REQUEST_URI']
	datestring = uri.split('/daily/')[1]
except KeyError:
	datestring =""

params = datestring.split('/')
today = time.gmtime(time.time())
try:
	year,month,day  = [int(i) for i in params[:3]]
except ValueError:
	year,month,day = today[:3]

try:
	arch = params[4]
except IndexError:
	arch = ''

if arch not in [''] + config.ARCHLIST:
	arch = ''

try:
	branch = params[5]
except IndexError:
	branch = ''

if branch not in ('','stable','testing'):
	branch = ''
	
# see if we're cached, if so write the cache and exit
if today[:3] == (year,month,day):
	# today is always cached ;-)
	archnav = os.path.join(config.LOCALHOME,arch,branch,'archnav.html')
	filename = os.path.join(config.LOCALHOME,arch,branch,'main.shtml')
	sys.stdout.write(open(archnav,'r').read())
	sys.stdout.write('<br>\n')
	sys.stdout.write(open(filename,'r').read())
	sys.exit(0)
else:
	filename = os.path.join(config.LOCALHOME,'daily','cache',
		'%d%02d%02d-%s-%s.html' % (year,month,day,arch,branch))
if os.path.exists(filename):
	sys.stdout.write(open(filename,'r').read())
	sys.exit(0)
	
db = ebuilddb.db_connect()
c = db.cursor()

extra = ''
if arch:
    stable_extra = ('ebuild.arch REGEXP "^%s| %s" '
        ' AND ebuild.prevarch NOT REGEXP"^%s| %s"'
        % (arch,arch,arch,arch))
    testing_extra = ('ebuild.arch REGEXP "^~%s| ~%s" '
        ' AND ebuild.prevarch NOT REGEXP "^~%s| ~%s"'
        % (arch,arch,arch,arch))
    if branch == 'stable':
        extra = ' AND (%s) ' % stable_extra
    elif branch == 'testing':
        extra = ' AND (%s) ' % testing_extra
    else:
        extra = ' AND ((%s) OR (%s)) ' % (stable_extra, testing_extra)

query = ('SELECT ebuild.category,'
	'ebuild.name,'
	'version,'
	'when_found,'
	'description,'
	'changelog,'
	'arch,'
	'homepage,'
	'license '
	'FROM ebuild,package '
	'WHERE SUBSTRING(when_found FROM 1 FOR 8) = "%s%02d%02d" '
	'AND ebuild.name = package.name '
	'AND ebuild.category = package.category %s'
	'ORDER BY when_found desc' %
	(year, month, day,extra))
	
c.execute(query)
results = c.fetchall()

s = genarchbar('%sdaily/%d/%02d/%02d/' % (config.FEHOME,year,month,day),arch,branch) + '<br>\n'
for result in results:
	ebuild = gentoo.query_to_dict(result)
	s = s + gentoo.ebuild_to_html(ebuild) + '<br>\n'
print s

# cache to file, if not todays date
if today[:3] != (year,month,day):
	filename = os.path.join(config.LOCALHOME,'daily','cache',
		'%d%02d%02d-%s-%s.html' % (year,month,day,arch,branch))
	open(filename,'w').write(s)
