#!/usr/bin/python -OO

import config
import sys
import os
import time
import re
import changelogs
import MySQLdb

# import portage, but temporarily redirect stderr
if 'portage' not in dir():
    null = open('/dev/null', 'w')
    tmp = sys.stderr
    sys.stderr = null
    sys.path = ["/usr/lib/portage/pym"]+sys.path
    import portage
    sys.stderr = tmp
    sys.path = sys.path[1:]

def db_connect():
    return MySQLdb.connect(host = config.HOST,
        user = config.USER,
        passwd = config.PASSWD,
        db = config.DATABASE)
    
def find_ebuilds():
    #print "walking..."
    ebuilds=[]
    # yeah, i know we can os.path.walk, but this runs faster ;-)
    pipe = os.popen("find %s -name '*.ebuild'" % config.PORTAGE_DIR)
    s = pipe.read()
    pipe.close()
    return s.split()
    
def parse_ebuild(s):
    """Parse ebuild info based on path name"""
    parsed = {}
    s=s.split('/')
    parsed['category'] = s[-3]
    package = s[-1].split('.ebuild')[0]
    pieces = portage.pkgsplit(package)
    if not pieces:
        return None
    parsed['name'] = pieces[0]
    if pieces[2] == 'r0':
        parsed['version'] = pieces[1]
    else:
        parsed['version'] = '-'.join(pieces[1:])

    return parsed

def get_ebuild_record(db,ebinfo):
    c = db.cursor()
    query = ('SELECT * FROM ebuild WHERE category="%s" AND name="%s" '   
        'AND version="%s" LIMIT 1' % (ebinfo['category'], ebinfo['name'],
        ebinfo['version']))
    c.execute(query)
    result = c.fetchone()
    return result

def create_ebuild_record(db,ebinfo):
    c = db.cursor()
    d = db.cursor()
    # update the package table

    # this is a really ugly dict comprehension
    escaped = dict([(x,MySQLdb.escape_string(y)) for (x,y) in ebinfo.items()])
    query="""REPLACE INTO package VALUES ("%(category)s","%(name)s",\
        "%(homepage)s","%(description)s","%(license)s");""" % escaped
    c.execute(query)

    # then add particular ebuild
    query = ('INSERT INTO ebuild VALUES ("%(category)s","%(name)s",'
        '"%(version)s",%(time)s,"%(archs)s","%(changelog)s","")' 
        % escaped)
    d.execute(query)
    
def update_ebuild_record(db,ebinfo):
    c = db.cursor()
    escaped = dict([(x,MySQLdb.escape_string(y)) for (x,y) in ebinfo.items()])
    query="""REPLACE INTO package VALUES ("%(category)s","%(name)s",\
        "%(homepage)s","%(description)s","%(license)s");""" % escaped
    c.execute(query)
    
    query = ('UPDATE ebuild '
        'SET when_found="%(time)s",'
        'arch="%(archs)s",'
        'changelog="%(changelog)s",'
        'prevarch="%(prevarch)s" '
        'WHERE category="%(category)s" '
        'AND name="%(name)s" '
        'AND version="%(version)s" ' % escaped)
    try:
        c.execute(query)
    except MySQLdb.MySQLError, data:
        print 'error occurred: '
        print 'query: %s' % query
        print 'error: %s' % data
        

def get_extended_info(ebuild):
    filename = os.path.join(config.PORTAGE_DIR,'metadata/cache',
        ebuild['category'],'%s-%s' % (ebuild['name'],ebuild['version']))
    try:
        lines = open(filename,'r').readlines()
    except IOError:
        lines = []
    lines = [ s.strip() for s in lines ]
    try:
        ebuild['archs'] = lines[8]
    except IndexError:
        ebuild['archs'] = ''
    try:
        ebuild['homepage'] = lines[5]
    except IndexError:
        ebuild['homepage'] = 'http://www.gentoo.org/'
    try:
        ebuild['license'] = lines[6]
    except IndexError:
        ebuild['license'] = ''
    try:
        ebuild['description'] = lines[7]
    except IndexError:
        ebuild['description'] = ''
    return ebuild

def get_mtime(s):
    """Get mtime of file, return in format that MySQL would like"""
    try:
        t = os.path.getmtime(s)
    except:
        return 'NULL'
    str = time.strftime("%Y%m%d%H%M%S",time.localtime(t))
    return str

def main(): 
    ebuilds = find_ebuilds()
    db = db_connect()
    
    for s in ebuilds:
        fields = parse_ebuild(s)
        if not fields:
            continue
        result = get_ebuild_record(db,fields)
        fields = get_extended_info(fields)
        fields['changelog'] = changelogs.changelog('%s/ChangeLog' 
            % os.path.dirname(s))
        fields['time'] = get_mtime(s)
        if not result:
            create_ebuild_record(db,fields)
        elif result[4] != fields['archs']:
            #print 'ebuild archs=',fields['archs']
            #print 'db archs=',result[4]
            #print
            # keywords change, update db
            fields['prevarch'] = result[4]
            update_ebuild_record(db,fields)
        
if __name__ == '__main__':
    main()
