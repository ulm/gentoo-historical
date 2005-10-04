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
