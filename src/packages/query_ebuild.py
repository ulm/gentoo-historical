#!/usr/bin/python

import cgi
import os
import sys
import config
import gentoo,ebuilddb

DEFAULT_EBUILD = "404"
PKG_DIR = config.EBUILD_FILES

if len(sys.argv):
    ebuild = sys.argv[1]
else:
    ebuild = DEFAULT_EBUILD


html_file = os.path.join(PKG_DIR,"%s.html" % ebuild.replace('..',''))
#if os.path.exists(html_file):
if 0:
    send_file = html_file
else:
    # let's try the database
    # connect
    pieces = gentoo.portage.pkgsplit(ebuild)
    name = pieces[0]
    if pieces[2] == 'r0':
        version = pieces[1]
    else:
        version = '-'.join(pieces[1:])
    db = ebuilddb.db_connect()
    # query
    query = ('SELECT ebuild.category,ebuild.name,version,when_found,'
        'description,changelog,arch,homepage,license '
        'FROM ebuild,package WHERE ebuild.name="%s" AND '
        'version="%s" AND '
        'ebuild.name=package.name AND ebuild.category=package.category '
        'ORDER by when_found DESC LIMIT 1' % (name,version))
    #print query
    c = db.cursor()
    c.execute(query)
    result = c.fetchone()
    if result:
        #print result
        eb = gentoo.query_to_dict(result)
        sys.stdout.write(gentoo.ebuild_to_html(eb,show_bugs=1))
        sys.exit(0)
    # else 404
    else:
        send_file = os.path.join(PKG_DIR,"%s.html" % DEFAULT_EBUILD)

sys.stdout.write(open(send_file,"r").read())
sys.stdout.flush()
