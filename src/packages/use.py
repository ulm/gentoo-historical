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
"""Module for dealing with the USE flag descriptions"""

import logging
import re

logging.basicConfig(level=logging.ERROR)

def parse(fd):
    """
    Parse the file.  return a dict of:

    [[category/name:]flag] = description
    """

    uses = dict()

    for line in fd:
        stripped = line.strip()
        if stripped == '' or stripped[0] == '#':
            continue

        name, description = stripped.rsplit('-', 1)
        name, description = name.strip(), description.strip()
        logging.info('%s: %s', name, description)

        uses[name] = description

    return uses



if __name__ == '__main__':
    from sys import stdin
    print parse(stdin)
