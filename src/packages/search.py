#!/usr/bin/python -OO

import sys
import config
import cgi
import gentoo
import os
import re
from MySQLdb import escape_string

form = cgi.FieldStorage()
type = form.getvalue("type","")
sstring = form.getvalue("sstring","")
offset = form.getvalue("offset","0")

# we score search results
POINTS = {
	'exact_match': 25,
	'starts_with': 20,
	'in_name': 10,
	'in_description': 2
}

if not sstring:
	sys.exit(0)

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
    try:
        open(cachefile,'w').write(s)
    except IOError:
        pass

def sort_by_weight(a, b):
    """Right now we just sort based on whether the sstring is in the name"""
    
    for i in [a, b]:
        if i.has_key('score'):
	        # We've already scored this one.  Skip it
            continue

        i['score'] = 0
        words = [word.lower() for word in sstring.split()]
        desc = i['description'].lower()

        wlen = len(words)
        x = wlen + 1

        for word in words:
            name = i['name'].lower()
            if name == word:
                i['score'] = i['score'] + POINTS['exact_match']
            if name.startswith(sstring):
                i['score'] = i['score'] + POINTS['starts_with']

            if word in name:
                i['score'] = i['score'] + POINTS['in_name']
            i['score'] = i['score'] + (desc.count(word) 
                    * POINTS['in_description']) * x
            x = x -1
        
        all_words = True
        desc_words = desc.split()
        for word in words:
            if word not in desc_words:
                all_words = False
                break
        if all_words:
            i['score'] = i['score'] * 2
                
    return cmp(b['score'], a['score'])



# if it's in the cache, just write that out
qs = sys.argv[1]
cachefile = os.path.join(config.LOCALHOME,'search/cache',qs)
if os.path.exists(cachefile):
	#sys.stdout.write('<div class="centerpage">using cached results</div>\n')
	sys.stdout.write(open(cachefile,'r').read())
	sys.exit(0)

words = sstring.split()
criteria = ''
for word in words:
    esc_word = escape_string(word)
    criteria += ('OR name REGEXP "[[:<:]]%s" '
            'OR description REGEXP "[[:<:]]%s[[:>:]]" ' % (esc_word, esc_word))
query = ('SELECT category,name,homepage,description,license '
	'FROM package  WHERE 1=0 %s' % criteria)

import ebuilddb
db = ebuilddb.db_connect()
c = db.cursor()
c.execute(query)
total_rows = c.rowcount

# now run the query again with LIMITS
#query = '%s LIMIT %s,%s' % (query, offset, config.MAXPERPAGE)

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
	'<p>I could not find any ebuild that match'
	' your query.  Try a different query or check the'
	' <a HREF="%s">'
	'packages.gentoo.org main page</a>.</p></td></tr></table>\n'
	'</div>\n' % config.FEHOME)
	sys.stdout.write(s)
	write_to_cache(s)
	sys.exit(0)

pkgs = [ query_to_dict(i) for i in results ]
pkgs.sort(sort_by_weight)

pkgs = pkgs[int(offset): int(offset) + config.MAXPERPAGE]
lresults = len(pkgs)

s = '<b>Results %s - %s of %s</b><br>' % (int(offset) + 1, 
	int(offset) + lresults, total_rows) 
s = '\n'.join([s] + [gentoo.package_to_html(pkg,db) for pkg in pkgs])
#for pkg in pkgs:
#	#print pkg
#	html = gentoo.package_to_html(pkg,db)
#	s = '%s\n%s' % (s,gentoo.package_to_html(pkg,db))

if offset != "0":
	s = '%s<a href="?sstring=%s;offset=%s">[Previous]</a> ' % (s,sstring,int(offset) - config.MAXPERPAGE)
if int(offset) + lresults < total_rows:
	s = '%s<a href="?sstring=%s;offset=%s">[Next]</a> ' % (s,sstring,int(offset) + config.MAXPERPAGE)

sys.stdout.write(s)
write_to_cache(s)
