#!/usr/bin/python -O

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
	
db = ebuilddb.db_connect()
c = db.cursor()

extra = ''
if arch:
    stable_extra = ('FIND_IN_SET("%s", ebuild.arch) > 0 AND '
        'FIND_IN_SET("%s", ebuild.prevarch) = 0 ' % (arch, arch))
    testing_extra = ('FIND_IN_SET("~%s", ebuild.arch) > 0 AND '
        'FIND_IN_SET("%s", ebuild.prevarch) = 0 ' % (arch, arch))
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
	'license, is_masked '
	'FROM ebuild,package '
	'WHERE DATE(when_found) = "%s-%02d-%02d" '
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
