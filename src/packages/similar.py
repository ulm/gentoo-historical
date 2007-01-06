#!/usr/bin/python -OO

import cgi
import os
import re
import string
import sys

from MySQLdb import escape_string

import config
import ebuilddb
import gentoo

form = cgi.FieldStorage()
package = form.getvalue("package","")
offset = form.getvalue("offset","0")

db = ebuilddb.db_connect()

def query_to_dict(q):
	pkginfo = {}
	keys = ('category','name','homepage','description','license')
	for i in range(len(keys)):
		try:
			pkginfo[keys[i]] = q[i]
		except IndexError:
			continue
	return pkginfo

def check_packages(pkg_name):
    """Sanity check the package name"""
    name = pkg_name.strip()
    if not name:
        return False
    if not '/' in name:
        return False
    return True

def get_package_from_db(pkg_name):
    """Query packagbe from database.  If package does not exist in
    database, return None"""

    category, name = pkg_name.split('/')
    query = 'SELECT category, name, homepage, description, license ' + \
            'FROM package WHERE category=%s and NAME=%s'
    
    c = db.cursor()
    c.execute(query, (category, name))
    
    if c.rowcount != 1:
        return None
    
    pkg_tuple = c.fetchone()
    return pkg_tuple

def strip_chars(mystring):
    newstring = ''
    for char in mystring:
        if char not in string.punctuation:
            newstring = newstring + char
        else:
            newstring = newstring + ' '
    return newstring

def do_none_found():
    """Return a "no matches found" message to the user."""
	
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

if not check_packages(package):
    print 'Not a valid package'
    sys.exit(0)

pkg_tuple = get_package_from_db(package)

if pkg_tuple is None:
    do_none_found()
    sys.exit(0)

pkg_dict = query_to_dict(pkg_tuple)

# that We have the package from the db, query again for similar pkgs
description = strip_chars(pkg_dict['description'].lower())
words = [word for word in description.split()
    if word and len(word)>2 and word not in config.EXCLUDED_FROM_SIMILAR]
words = words[:config.SIMILAR_MAX_WORDS] + [pkg_dict['name']]
criteria = ['[[:<:]]%s.*' % word for word in words]
criteria = '(%s){%s,}' % ('|'.join(criteria), config.SIMILAR_MIN_MATCHES)

query = 'SELECT category, name, homepage, description, license ' + \
            'FROM package WHERE name REGEXP %s OR description REGEXP %s'
c = db.cursor()
c.execute(query, (criteria, criteria))
total_rows = c.rowcount

results = c.fetchall()

if not results:
    do_none_found()
    sys.exit(0)

pkgs = [ query_to_dict(i) for i in results ]
pkgs = pkgs[int(offset): int(offset) + config.MAXPERPAGE]
lresults = len(pkgs)

escaped = escape_string(package)

s = ('<div class="category"><strong>Packages Similiar to %(category)s/%(name)s'
    '</strong></div>\n' % pkg_dict) 
s += '<b>Results %s - %s of %s</b><br>' % (int(offset) + 1, 
	int(offset) + lresults, total_rows) 
s = '\n'.join([s] + [gentoo.package_to_html(pkg,db) for pkg in pkgs])

if offset != "0":
	s = '%s<a href="?package=%s;offset=%s">[Previous]</a> ' % (s,package,int(offset) - config.MAXPERPAGE)
if int(offset) + lresults < total_rows:
	s = '%s<a href="?package=%s;offset=%s">[Next]</a> ' % (s,package,int(offset) + config.MAXPERPAGE)

sys.stdout.write(s)
