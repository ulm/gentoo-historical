#!/usr/bin/python

"""Various Utilities/Scriptlets for packages.gentoo.org"""


import sys
import config
from ebuilddb import parse_ebuild, get_extended_info

class Util:
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
