#!/usr/bin/python -OO

import cgi
from urllib import quote
import os
import sys
import config
import gentoo
import ebuilddb
from MySQLdb import escape_string

sys.stdout.write('Content-type: text/html; charset=iso-8859-1\n\n')

def cmp_results(a, b):
    """Compare results a and b"""
    category_a = a[0]
    category_b = b[0]
    
    order = cmp(category_a, category_b)
    if order != 0:
        return order
        
    
def query_to_dict(q):
    pkginfo = {}
    keys = ('category','name','homepage','description','license')
    for i in range(len(keys)):
        try:
            pkginfo[keys[i]] = q[i]
        except IndexError:
            continue
    return pkginfo


form = cgi.FieldStorage()
name = form.getvalue("name","")
category = form.getvalue("category","")
offset = form.getvalue("offset","0")

query = ('SELECT category,name,homepage,description,license '
    'FROM package WHERE category="%s"' % escape_string(category))
    
if name:
    query = ('%s AND name="%s"' %(query,escape_string(name)))

query = ('%s LIMIT %s,%s' % (query,offset,config.MAX_CATEGORIES))

db = ebuilddb.db_connect()
c = db.cursor()
c.execute(query)
results = c.fetchall()

#print query
if results:
    if name:
        for result in results:
            #print result
            pkg = query_to_dict(result)
            sys.stdout.write('%s<br>\n<br>\n' 
                % gentoo.package_to_html(pkg,db))
    else:
        sys.stdout.write('<table class="centerpage">\n')
        sys.stdout.write('<tr><th class="category">'
            '%s</th></tr>\n<tr><td>' % category)
        for result in results:
            pkg = query_to_dict(result)
            sys.stdout.write(gentoo.package_to_html(pkg, db))
        sys.stdout.write('</td></tr></table>\n')
    if offset !="0":
        sys.stdout.write('<a href="?category=%s;name=%s'
            ';offset=%s">[Previous]</a> '
            % (category,name,int(offset) - config.MAX_CATEGORIES))
    if len(results) == config.MAX_CATEGORIES:
        sys.stdout.write('<a href="?category=%s;name=%s;offset=%s">[Next]</a> '
        % (category,name,int(offset) + config.MAX_CATEGORIES))

else:
    sys.stdout.write('<div class="centerpage">\n'
        '<table width="100%%" border="0"  align="center"'
        ' cellspacing="0"><tr><td colspan="3" class="fields">'
        'Sorry, dude.  I could not find that package.<br></td></tr>\n'
        '<tr><td class="item" colspan="3">'
        '<img '
        'src="%s?category=404"'
        'align="right" alt=""> <p>Information on the package you requested'
        ' could not be found.  Be sure to check the'
        ' <a HREF="%s">'
        'packages.gentoo.org main page</a>.</p></td></tr></table>\n'
        '</div>' % (config.ICONS,config.FEHOME))
