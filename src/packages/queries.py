#
# Copyright (C) 2005, marduk <marduk@python.net>
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
The idea is to keep all the SQL queries here.  That way if the database
schema changes we only need to edit one module.

Functions here should make queries based on their arguments and return lists
of "formatted" objects, not the tuples returned by fetch[all]()

REMEMBER: Return value is *ALWAYS* a list.
"""

__revision__ = "$Revision: 1.1.2.2 $"
# $Source: /var/cvsroot/gentoo/src/packages/Attic/queries.py,v $

from re import compile
from datetime import datetime, timedelta
from MySQLdb import escape_string
from packages.config import db, DAYS_NEW, DEFAULT_LIMIT

SECS_PER_DAY = 86400
TIMEFRAME_RE = compile(r'([1-9][0-9]?)(hour|day|week)s?')

def get_tip(tip_id = None, count = 1):
    """
    Return [(tip_id, tip)] for tip_id.  If tip_id is None return a random
    tip from the table
    """

    if tip_id is None:
        query = 'SELECT * FROM tip WHERE 1=1 ORDER BY RAND() LIMIT ' + `count`
    else:
        query = 'SELECT * FROM tip WHERE tip_id=%(tip_id)s' % locals()

    c = db.cursor()
    c.execute(query)

    results = c.fetchall()

    return results

def get_updates(platform = '', branch = '', count = DEFAULT_LIMIT, timeframe = None,
    new = False):
    """query function for Updates Platform"""
    from packages.portage import Ebuild

    c = db.cursor()
    extra = ''
    #print branch
    if platform:
        #stable_extra = ('ebuild.arch REGEXP "^%s[[:>:]]|[[:blank:]]%s[[:>:]]" '
        #    % (platform, platform))
        stable_extra = 'FIND_IN_SET("%s", ebuild.arch) > 0 AND ' \
            'FIND_IN_SET("%s", ebuild.prevarch) = 0 ' % (platform, platform)
        #testing_extra = ('ebuild.arch REGEXP "[~]%s[[:>:]]" ' % platform)
        testing_extra = 'FIND_IN_SET("~%s", ebuild.arch) > 0 AND ' \
            'FIND_IN_SET("~%s", ebuild.prevarch) = 0 ' % (platform, platform)

        if branch == 'stable':
            extra = ' AND (%s) ' % stable_extra
        elif branch == 'testing':
            extra = ' AND (%s) ' % testing_extra
        else:
            extra = ' AND ((%s) OR (%s)) ' % (stable_extra, testing_extra)

    if timeframe:
        match = TIMEFRAME_RE.search(timeframe) or TIMEFRAME_RE.search('3hours')

        try:
            factor = int(match.groups()[0])
        except ValueError:
            factor = 3

        units = match.groups()[1]

        #print(factor, units)
        if units == 'hour':
            delta = timedelta(hours = factor, microseconds = 0)
        elif units == 'day':
            delta = timedelta(days = factor, microseconds = 0)
        else:
            delta = timedelta(weeks = factor, microseconds = 0)

        #print datetime.utcnow()
        starttime = (datetime.now() - delta).replace(microsecond = 0)
        #print starttime

        extra = '%s AND ebuild.when_found >= "%s" ' % (extra, starttime)
        count = 120


##    if new:
##        secs = SECS_PER_DAY * DAYS_NEW
##        extra = ('%s AND (UNIX_TIMESTAMP(NOW()) - \
##            UNIX_TIMESTAMP(package.when_found)<%s) ' % (extra, secs))

    order = ['ebuild.when_found', 'package.when_found'][new]

    query = ('SELECT ebuild.category, ebuild.name, version, ebuild.when_found, '
        'description, changelog, arch, homepage, ebuild.license, is_masked, '
        'package.when_found FROM ebuild, package WHERE ebuild.name = package.name AND '
        'ebuild.category = package.category %s ORDER by %s DESC LIMIT %s' %
        (extra, order, count))

    #print query
    c.execute(query)
    results = c.fetchall()

    return [ Ebuild(category = result[0],
        name = result[1],
        version = result[2],
        when_found = result[3],
        description = result[4],
        changelog = result[5],
        arch = result[6],
        homepage = result[7],
        license = result[8],
        masked = result[9],
        package_datetime = result[10]
        ) for result in results ]

def get_bumps(platform = '', branch = '', count = DEFAULT_LIMIT, timeframe = None):

    from packages.portage import Ebuild

    c = db.cursor()
    extra = ''
    #print branch
    if platform:
        stable_extra = ('ebuild.arch REGEXP "^%s[[:>:]]|[[:blank:]]%s[[:>:]]"'
            % (platform, platform))

        testing_extra = ('ebuild.arch REGEXP "[~]%s[[:>:]]"' % platform)

        if branch == 'stable':
            extra = ' AND (%s) ' % stable_extra
        elif branch == 'testing':
            extra = ' AND (%s) ' % testing_extra
        else:
            extra = ' AND ((%s) OR (%s)) ' % (stable_extra, testing_extra)

    if timeframe:
        match = TIMEFRAME_RE.search(timeframe) or TIMEFRAME_RE.search('3hours')

        try:
            factor = int(match.groups()[0])
        except ValueError:
            factor = 3

        units = match.groups()[1]

        #print(factor, units)
        if units == 'hour':
            delta = timedelta(hours = factor, microseconds = 0)
        elif units == 'day':
            delta = timedelta(days = factor, microseconds = 0)
        else:
            delta = timedelta(weeks = factor, microseconds = 0)

        #print datetime.utcnow()
        starttime = (datetime.now() - delta).replace(microsecond = 0)
        #print starttime

        extra = '%s AND ebuild.when_found >= "%s" ' % (extra, starttime)
        count = 120

    secs = SECS_PER_DAY * DAYS_NEW
    query = ('SELECT ebuild.category, ebuild.name, version, ebuild.when_found, '
        'description, changelog, arch, homepage, ebuild.license, is_masked FROM '
        'ebuild, package WHERE ebuild.name = package.name AND '
        'ebuild.category = package.category AND prevarch="" AND version '
        'NOT LIKE "%%-r_" AND version NOT LIKE "%%-r__" AND '
        '(UNIX_TIMESTAMP(NOW()) - UNIX_TIMESTAMP(package.when_found)>=%s) %s '
        'ORDER by when_found DESC LIMIT %s' % (secs, extra, count))

    #print query
    c.execute(query)
    results = c.fetchall()
    return [ Ebuild(category = result[0],
        name = result[1],
        version = result[2],
        when_found = result[3],
        description = result[4],
        changelog = result[5],
        arch = result[6],
        homepage = result[7],
        license = result[8],
        masked = result[9]
        ) for result in results ]
