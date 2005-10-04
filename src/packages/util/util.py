#!/usr/bin/python
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

"""Various Utilities/Scriptlets for packages.gentoo.org"""


import sys
import config
from ebuilddb import parse_ebuild, get_extended_info

class Util:
    def convert_archs(self):
        """Run only once!  Converts arch and prevarch to new layout (comma-
        delimited instead of space-delimited"""

        c = config.db.cursor()
        d = config.db.cursor()

        c.execute('SELECT category, name, version, arch, prevarch FROM ebuild')
        while True:
            result = c.fetchone()
            if result is None: break
            category, name, version, arch, prevarch = result
            new_arch = ','.join(arch.split())
            new_prevarch = ','.join(prevarch.split())
            print '"%(arch)s", "%(prevarch)s" -> "%(new_arch)s", "%(new_prevarch)s"' % locals()
            d.execute('UPDATE ebuild SET arch=%(new_arch)s, '
                'prevarch=%(new_prevarch)s WHERE category=%(category)s AND '
                'name=%(name)s and version=%(version)s', locals())

        config.db.commit()

    def fix_timestamps(self):
        """Fix timestamps on ebuilds in db wrt .ebuild files"""
        import os, datetime
        db = config.db
        cursorA = db.cursor()
        cursorB = db.cursor()

        cursorA.execute('SELECT category, name, version, when_found FROM ebuild')
        while True:
            result = cursorA.fetchone()
            if result is None: break
            category, name, version, when_found = result
            ebuild = config.PORTAGE_DIR + '/' + \
                '%(category)s/%(name)s/%(name)s-%(version)s.ebuild' % locals()
            if not os.path.exists(ebuild): continue
            filestamp = datetime.datetime.fromtimestamp(os.path.getmtime(ebuild))
            if filestamp != when_found:
                print('ebuild and when_found differ for '
                    '%(category)s/%(name)s-%(version)s' % locals())
                cursorB.execute('UPDATE ebuild SET when_found=%(filestamp)s '
                'WHERE category=%(category)s AND name=%(name)s AND '
                'version=%(version)s', locals())
        db.commit()

    def homepage_update(self):
        """Update the HOMEPAGE Column for packages based on last updated Ebuild"""

        sys.path = ["/usr/lib/portage/pym"]+sys.path
        import portage
        sys.path = sys.path[1:]

        try:
            c = config.db.cursor()
        except AttributeError:
            # old version of p.g.o
            from ebuilddb import db_connect
            config.db = db_connect()
            c = config.db.cursor()

        portage_dir = config.PORTAGE_DIR
        query = ('SELECT category,name,version from ebuild GROUP BY category,name '
            ' ORDER BY when_found DESC')
        c.execute(query)
        for category, name, version in c.fetchall():
            ebuild_path = ('%(portage_dir)s/%(category)s/%(name)s/%(name)s-'
                '%(version)s.ebuild' % locals())
            ebuild = parse_ebuild(ebuild_path, portage.pkgsplit)
            ebuild = get_extended_info(ebuild)

            homepage = ebuild['homepage']
            c.execute = ("""
                UPDATE package
                SET homepage = %s
                WHERE category=%s
                AND name = %s
                """, (homepage, category, name))
        config.db.commit()

    def update_license_data(self):
        """ONe time call"""
        sys.path = ["/usr/lib/portage/pym"]+sys.path
        import portage
        sys.path = sys.path[1:]

        try:
            c = config.db.cursor()
        except AttributeError:
            # old version of p.g.o
            from ebuilddb import db_connect
            config.db = db_connect()
            c = config.db.cursor()

        for data in find_ebuilds():
            ebuild = parse_ebuild(data, portage.pkgsplit)
            if not ebuild:
                continue
            ebuild = get_extended_info(ebuild)

            license = ebuild['license']
            c.execute("""
                UPDATE ebuild
                SET license = %s
                WHERE category = %s
                AND name = %s
                AND version = %s
                """, (ebuild["license"], ebuild["category"], ebuild["name"],
                ebuild["version"]))
        config.db.commit()

if __name__ == '__main__':
    from sys import argv, stderr, exit
    from types import FunctionType

    myUtil = Util()
    util_dict = Util.__dict__
    FUNCS = [x for x in util_dict if type(util_dict[x]) is FunctionType]

    try:
        func_name = argv[1]
    except IndexError:
        stderr.write('Usage %s <function>\n' % argv[0])
        exit(1)

    print func_name

    if func_name in FUNCS:
        util_dict[func_name](myUtil)

    else:
        stderr.write('%s is not defined\n' % func_name)
        stderr.write('Available functions:\n%s\n' % '\n'.join(FUNCS))
        exit(1)
