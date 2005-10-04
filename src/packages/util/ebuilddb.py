#!/usr/bin/python -O
#
# Copyright (C) 2003-2005, marduk <marduk@python.net>
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions
# of the GNU General Public License v.2.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
Ebuild database manipulater:

The primary purpose of this module is to sync the database with what is
currently in portage.  It is intended to be used as a script.
"""
import sys
import os

# I want to ignore overlays
os.environ['PORTDIR_OVERLAY'] = ''

sys.path = ["/usr/lib/portage/pym"]+sys.path
import portage
# ... and then wait like a f**king hour
sys.path = sys.path[1:]

from packages import config, changelogs
import time
import MySQLdb
from elementtree.ElementTree import parse
import logging

# our interface to the portage api
# We want to use the base profile, not any system-specific one
pconfig = portage.config(config_profile_path = '%s/profiles/base'
    % config.PORTAGE_DIR, config_incrementals = ['BUGUS'])
tree = portage.portdbapi(config.PORTAGE_DIR, pconfig)

logging.basicConfig(level=logging.INFO)

# description cache
desc_cache = {}

def find_ebuilds():
    """Traverse the portage tree and return list of ebuilds"""
    logging.info("walking...")
    for cat_pkg in tree.cp_all():
        if '/' not in cat_pkg:
            continue
        for ebuild in tree.cp_list(cat_pkg):
            yield ebuild

def parse_ebuild(ebuild):
    """Parse ebuild info"""
    parsed = {}
    split = portage.pkgsplit(ebuild)
    if not split:
        return None
    cat_pkg, version, revision = split
    parsed['category'], parsed['name'] = cat_pkg.split('/', 1)
    if revision == 'r0':
        parsed['version'] = version
    else:
        parsed['version'] = '-'.join([version, revision])
    return parsed

def get_ebuild_record(db, ebinfo):
    """Return the ebuild data as found in the database -> tuple"""
    c = db.cursor()
    query = ('SELECT * FROM ebuild WHERE category="%s" AND name="%s" '
        'AND version="%s" LIMIT 1' % (ebinfo['category'], ebinfo['name'],
        ebinfo['version']))
    c.execute(query)
    result = c.fetchone()
    return result

def create_ebuild_record(db, ebinfo):
    """Create a database record according to ebinfo dict"""
    logging.info('CREATING %(category)s/%(name)s-%(version)s' % ebinfo)
    c = db.cursor()
    d = db.cursor()
    # update the package table

    try:
        c.execute('INSERT INTO package SET category=%s, name=%s, '
            'homepage=%s, description=%s, when_found=%s', (ebinfo['category'],
            ebinfo['name'], ebinfo['homepage'],
            ebinfo['description'], ebinfo['time']))
    except MySQLdb.cursors.IntegrityError:
        c.execute('UPDATE package SET homepage=%(homepage)s, description='
            '%(description)s WHERE category=%(category)s AND name=%(name)s',
            ebinfo)
##        category=%s, name=%s, '
##            'homepage=%s, description=%s, when_found=%s', (ebinfo['category'],
##            ebinfo['name'], ebinfo['homepage'],
##            ebinfo['description'], ebinfo['time']))

    # then add particular ebuild
    try:
        d.execute('INSERT INTO ebuild VALUES (%(category)s, %(name)s, %(version)s,'
            '%(time)s, %(archs)s, %(changelog)s, "", %(masked)s, %(license)s)',
            ebinfo)
        d.execute('INSERT INTO deps VALUES (%(category)s, %(name)s, %(version)s,'
            '%(depend)s, %(rdepend)s, %(pdepend)s)', ebinfo)
    except MySQLdb.MySQLError, data:
        logging.error('error occorred: ')
        loggine.error('error: %s' % data)

def update_ebuild_record(db, ebinfo):
    """Create a database record according to ebinfo dict.  Ebuild must already
    exist in the db (or else use create_ebuild_record).
    """
    logging.info('UPDATING %(category)s/%(name)s-%(version)s' % ebinfo)
    c = db.cursor()
    c.execute('UPDATE package SET homepage=%(homepage)s, description='
        '%(description)s WHERE category=%(category)s AND name=%(name)s', ebinfo)
    try:
        c.execute('UPDATE ebuild SET when_found=%(time)s, arch=%(archs)s, '
            'changelog=%(changelog)s, prevarch=%(prevarch)s, '
            'is_masked=%(masked)s, license=%(license)s '
            'WHERE category=%(category)s AND name=%(name)s AND '
            'version=%(version)s', ebinfo)
        c.execute('UPDATE deps SET depend=%(depend)s, rdepend=%(rdepend)s, '
            'pdepend=%(pdepend)s WHERE category=%(category)s AND name=%(name)s '
            'AND version=%(version)s', ebinfo)
    except MySQLdb.MySQLError, data:
        logging.error('error occurred: ')
        logging.error('error: %s' % data)


def get_extended_info(ebuild):
    """Return a dict with extended info about ebuild dict"""
    cpv = '%(category)s/%(name)s-%(version)s' % ebuild
    archs, homepage, _license, description = tree.aux_get(cpv, ('KEYWORDS',
        'HOMEPAGE', 'LICENSE', 'DESCRIPTION'))

    ebuild['archs'] = ','.join(archs.split())
    ebuild['homepage'] = homepage or 'http://www.gentoo.org/'
    ebuild['license'] = _license
    ebuild['license'] = ebuild['license'].replace('(', '')
    ebuild['license'] = ebuild['license'].replace(')', '')
    ebuild['license'] = ebuild['license'].strip()
    ebuild['description'] = description #.encode('latin-1','replace')

    # dependencies
    (ebuild['depend'], ebuild['rdepend'], ebuild['pdepend']) = \
        tree.aux_get(cpv, ('DEPEND', 'RDEPEND', 'PDEPEND'))
    # check to see it description is in cache
    catname = '%(category)s/%(name)s' % ebuild
    if desc_cache.has_key(catname):
        ebuild['description'] = desc_cache[catname]
    else:
        # now get description from metadata info, if exists
        metadata_filename = os.path.join(config.PORTAGE_DIR,
                ebuild['category'], ebuild['name'], 'metadata.xml')

        if os.path.exists(metadata_filename):
            logging.debug('Processing %s', metadata_filename)
            xml_tree = parse(metadata_filename)
            if xml_tree:
                descriptions = xml_tree.findall('longdescription')
                description_text = ''
                for description in descriptions:
                    lang = description.attrib.get('lang')
                    if not (description.text and description.text.strip()):
                        logging.debug('NODESC: %s/%s lang=%s' %
                            (ebuild['category'], ebuild['name'], lang))
                    if lang == 'en':
                        description_text = description.text
                        break
            try:
                ebuild['description'] = (description_text or
                    descriptions[0].text or ebuild['description'])
                ebuild['description'] = ebuild['description'].strip()\
                    .replace('\n', ' ')
                ebuild['description'] = ebuild['description'].encode('latin-1',
                    'replace')
            except IndexError:
                # no descriptions in xml file
                logging.debug("bastard had no description for %s/%s",
                        ebuild['category'], ebuild['name'])
    desc_cache[catname] = ebuild['description']
    return ebuild

def get_mtime(ebuild):
    """Get mtime of file, return in format that MySQL would like"""
    pathname = tree.findname('%(category)s/%(name)s-%(version)s' % ebuild)
    if not pathname:
        return 'NULL'
    try:
        mtime = os.path.getmtime(pathname)
    except OSError:
        return 'NULL'
    strftime = time.strftime("%Y%m%d%H%M%S", time.localtime(mtime))
    return strftime

def is_masked(ebuild):
    """Return true if packages is masked in tree"""
    return (not tree.visible(['%(category)s/%(name)s-%(version)s' % ebuild]))

def build():
    """Update/Create ebuild/packages in tree based on what's in portage"""
    db = config.db

    for ebuild in find_ebuilds():
        fields = parse_ebuild(ebuild)
        if not fields:
            continue
        result = get_ebuild_record(db, fields)
        fields = get_extended_info(fields)
        ebuild_path = tree.findname('%(category)s/%(name)s-%(version)s' % fields)
        fields['changelog'] = changelogs.changelog('%s/ChangeLog'
            % os.path.dirname(ebuild_path))
        fields['time'] = get_mtime(fields)
        fields['masked'] = int(is_masked(fields))

        if not result:
            try:
                create_ebuild_record(db, fields)
            except MySQLdb.MySQLError:
                print 'error creating record for %s/%s-%s' % (
                    fields['category'], fields['name'], fields['version'])
                raise
        elif result[4].split(',') != fields['archs'].split(','):
            # keywords change, update db
            fields['prevarch'] = result[4]
            update_ebuild_record(db, fields)
        elif result[7] != fields['masked']:
            #print 'mask changed for %s-%s' % (fields['name'], fields['version'])
            #print fields['masked']
            fields['prevarch'] = result[4]
            update_ebuild_record(db, fields)

    db.commit()

def purge():
    """Purge ebuilds/packages that no longer exist in portage"""

    c = config.db.cursor()
    c.execute('SELECT category, name, version FROM ebuild')
    c2 = config.db.cursor()
    while 1:
        result = c.fetchone()
        if result is None:
            break
        #category, name, version = result
        cpv = '%s/%s-%s' % result
        if not tree.cpv_exists(cpv):
            logging.info('REMOVING %s' % cpv)
            c2.execute('DELETE FROM ebuild WHERE category=%s AND name=%s '
                'AND version=%s', result)
            c2.execute('DELETE FROM deps WHERE category=%s AND name=%s '
                'AND version=%s', result)
    config.db.commit()

    c.execute('SELECT category, name FROM package')
    c3 = config.db.cursor()
    while 1:
        package = c.fetchone()
        if package is None:
            break
        c2.execute('SELECT COUNT(*) FROM ebuild WHERE category=%s AND name=%s',
            package)
        count = c2.fetchone()[0]
        if not count:
            logging.info('REMOVING %s/%s' % package)
            c3.execute('DELETE FROM package WHERE category=%s AND '
                'name=%s', package)
    config.db.commit()


if __name__ == '__main__':
    build()
    purge()
    sys.exit(0)
