#!/usr/bin/python -O

__revision__ = '$Revision: 1.8.2.1 $'
# $Source: /var/cvsroot/gentoo/src/packages/ebuilddb.py,v $

import config
import sys
import os
import time
import changelogs
import MySQLdb

def db_connect():
    return MySQLdb.connect(host = config.HOST,
        user = config.USER,
        passwd = config.PASSWD,
        db = config.DATABASE)

def find_ebuilds():
    #print "walking..."
    # yeah, i know we can os.path.walk, but this runs faster ;-)
    pipe = os.popen("find %s -name '*.ebuild'" % config.PORTAGE_DIR)
    s = pipe.read()
    pipe.close()
    return s.split()

def parse_ebuild(s, pkgsplit):
    """Parse ebuild info based on path name"""
    parsed = {}
    s=s.split('/')
    parsed['category'] = s[-3]
    package = s[-1].split('.ebuild')[0]
    pieces = pkgsplit(package)
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
    escaped = {}
    for item in ebinfo.items():
        x, y = item
        if type(y) is str:
            y = MySQLdb.escape_string(y)
        escaped[x] = y

    query=('INSERT INTO package SET category="%(category)s",name="%(name)s",'
        'homepage="%(homepage)s",description="%(description)s",'
        'license="%(license)s"' % escaped)
    try:
        c.execute(query)
    except MySQLdb.cursors.IntegrityError:
        # duplicate key (we hope)
        query = ('REPLACE INTO package VALUES ("%(category)s","%(name)s",'
            '"%(homepage)s","%(description)s","%(license)s",0)' % escaped)
        c.execute(query)

    # then add particular ebuild
    query = ('INSERT INTO ebuild VALUES ("%(category)s","%(name)s",'
        '"%(version)s",%(time)s,"%(archs)s","%(changelog)s","",%(masked)d)'
        % escaped)
    d.execute(query)

def update_ebuild_record(db,ebinfo):
    c = db.cursor()
    escaped = {}
    for item in ebinfo.items():
        x, y = item
        if type(y) is str:
            y = MySQLdb.escape_string(y)
        escaped[x] = y

    query="""REPLACE INTO package VALUES ("%(category)s","%(name)s",\
        "%(homepage)s","%(description)s","%(license)s",0);""" % escaped
    c.execute(query)

    query = ('UPDATE ebuild '
        'SET when_found="%(time)s",'
        'arch="%(archs)s",'
        'changelog="%(changelog)s",'
        'prevarch="%(prevarch)s", '
        'is_masked=%(masked)d '
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
        print 'Error opening %s' % filename
        lines = []
    lines = [ s.strip() for s in lines ]
    try:
        ebuild['archs'] = ','.join(lines[8].split())
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
        mtime = os.path.getmtime(s)
    except OSError:
        return 'NULL'
    strftime = time.strftime("%Y%m%d%H%M%S",time.localtime(mtime))
    return strftime

def is_masked(tree, ebuild):
    """Return true if packages is masked in tree"""
    return (not tree.visible(['%(category)s/%(name)s-%(version)s' % ebuild]))

def main(argv = []):
    """Main program entry point"""
    # We need to "fake" as repoman so portage will ignore local system
    # settings
    os.environ['PORTAGE_CALLER'] = 'repoman'

    ebuilds = find_ebuilds()
    db = db_connect()

    sys.path = ["/usr/lib/portage/pym"]+sys.path
    import portage
    # ... and then wait like a f**king hour
    sys.path = sys.path[1:]

    # We want to use the base profile, not any system-specific one
    p_config = portage.config(config_profile_path='/usr/portage/profiles/base',
            local_config=False)

    tree = portage.portdbapi('/usr/portage', p_config)

    # are we updating the db or just rebuilding it?
    rebuild = len(argv) == 2 and argv[1] == 'rebuild'
    for s in ebuilds:
        fields = parse_ebuild(s, portage.pkgsplit)
        if not fields:
            continue
        result = get_ebuild_record(db,fields)
        fields = get_extended_info(fields)
        fields['changelog'] = changelogs.changelog('%s/ChangeLog'
            % os.path.dirname(s))
        fields['time'] = get_mtime(s)
        fields['masked'] = int(is_masked(tree, fields))

        if not (result or rebuild):
            create_ebuild_record(db,fields)
        elif result and rebuild:
            fields['prevarch'] = result[6]
            if ' ' in fields['prevarch']:
                # old db layout
                fields['prevarch'] = ','.join(fields['prevarch'].split())
            fields['arch'] = [4]
            update_ebuild_record(db, fields)
        elif rebuild:
            pass
        elif result[4].split(',') != fields['archs'].split(','):
            #print 'ebuild archs=',fields['archs']
            #print 'db archs=',result[4]
            #print
            # keywords change, update db
            fields['prevarch'] = result[4]
            update_ebuild_record(db,fields)
        elif result[7] != fields['masked']:
            #print 'mask changed for %s-%s' % (fields['name'], fields['version'])
            #print fields['masked']
            fields['prevarch'] = result[4]
            update_ebuild_record(db,fields)

    db.commit()
if __name__ == '__main__':
    sys.exit(main(sys.argv))
