#!/usr/bin/python -OO

import sys
import config
import cgi
import ebuilddb
import gentoo
import os
from MySQLdb import escape_string

form = cgi.FieldStorage()
type = form.getvalue("type","")
sstring = form.getvalue("sstring","")
offset = form.getvalue("offset","0")

if not sstring:
	sys.exit(0)

if type == 'desc':
	col = "description"
else:
	col = "name"

def query_to_dict(q):
	pkginfo = {}
	keys = ('category','name','homepage','description','license')
	for i in range(len(keys)):
		try:
			pkginfo[keys[i]] = q[i]
		except IndexError:
			continue
	return pkginfo

def write_to_cache(s):
	open(cachefile,'w').write(s)

# if it's in the cache, just write that out
qs = sys.argv[1]
cachefile = os.path.join(config.LOCALHOME,'search/cache',qs)
if os.path.exists(cachefile):
	#sys.stdout.write('<div class="centerpage">using cached results</div>\n')
	sys.stdout.write(open(cachefile,'r').read())
	sys.exit(0)

escaped = escape_string(sstring)
query = ('SELECT category,name,homepage,description,license '
	'FROM package WHERE name REGEXP "%s" or description REGEXP "%s" '
	'LIMIT %s,%s' 
	% (escaped,escaped,offset,config.MAXPERPAGE))

db = ebuilddb.db_connect()
c = db.cursor()
try:
	c.execute(query)
	results = c.fetchall()
except:
	results = None

if not results:
	s = ( '<div class="centerpage">\n'
	'<table width="100%%" border="0"  align="center"'
	' cellspacing="0"><tr><td colspan="3" class="fields">'
	'Nothing found.<br></td></tr>\n'
	'<tr><td class="item" colspan="3">'
	'<img '
	'src="%s/?category=generic"'
	'align="right" alt=""> <p>I could not find any ebuild that match'
	' your query.  Try a different query or check the'
	' <a HREF="%s">'
	'fresh ebuilds main page</a>.</p></td></tr></table>\n'
	'</div>\n' % (config.ICONS,config.FEHOME))
	sys.stdout.write(s)
	write_to_cache(s)
	sys.exit(0)

pkgs = [ query_to_dict(i) for i in results ]

s = ''
for pkg in pkgs:
	#print pkg
	html = gentoo.package_to_html(pkg,db)
	s = '%s\n%s<br>\n<br>\n' % (s,gentoo.package_to_html(pkg,db))

if offset != "0":
	s = '%s<a href="?sstring=%s;offset=%s">[Previous]</a> ' % (s,sstring,int(offset) - config.MAXPERPAGE)
if len(results) == config.MAXPERPAGE:
	s = '%s<a href="?sstring=%s;offset=%s">[Next]</a> ' % (s,sstring,int(offset) + config.MAXPERPAGE)

sys.stdout.write(s)
write_to_cache(s)
