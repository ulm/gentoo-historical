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
"""Module to deal with Changelog files in the portage tree"""

import re
from cgi import escape

BUG_REGEX = re.compile(r'((\B#|\bbug )([0-9]+))', re.I)
DATE_REGEX = re.compile(r"""
    (
        [0-9]{2}\s # Day
        (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s  # Month
        [0-9]{4} # Year
    )
    [;:]""",
    re.M|re.VERBOSE)
GENTOO_DEV = re.compile(r'&lt;((.+))@gentoo.org&gt;', re.I)

def bugs_to_html(string):
    """Convert bug #'s to html, escape other html text"""
    string = string.strip()
    string = escape(string)
    string = BUG_REGEX.sub(r'<a href="/bugs/\3">\1</a>', string)
    match = DATE_REGEX.search(string)
    if match:
        start = match.start()
        next = DATE_REGEX.search(string, match.end() + 1)
        if next:
            end = next.start() - 1
        else:
            end = len(string)
        string = string[start:end]
        string = DATE_REGEX.sub(r'<span class="date">\1</span>: ', string)
    string = GENTOO_DEV.sub(r'(<a href="/stats/\2">\1</a>)', string)
    return '<span class="change">%s</span>' % string

def changelog(filename):
    """(Try to) Extract only the most recent bits from a changelog file"""
    try:
        #print filename
        _file = file(filename, 'r')
    except IOError:
        return ""


    string = ""
    # find first line that isn't blank or a comment
    while True:
        line = _file.readline()
        if not line:
            break
        #print line
        if line[0] not in ['#', '', '\n']:
            string = string + line
            break

    # append next strings until you reach next "*"
    while True:
        line = _file.readline()
        #print repr(line)
        if not line or line[0] == '*':
            break
        else: string = string + line

    return string
