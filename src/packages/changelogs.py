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

from packages import mstring
import re
from cgi import escape

#BUG_REGEX = re.compile(r'\B#[0-9]+|\bbug [0-9]+', re.I)
BUG_REGEX = re.compile(r'((\B#|\bbug )([0-9]+))', re.I)
DATE_REGEX = re.compile(
    r'[0-9]{2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [0-9]{4}[;:]',
    re.M)
GENTOO_DEV = re.compile(r'&lt;((.+))@gentoo.org&gt;', re.I)

def bugs_to_html(string):
    """Convert bug #'s to html, escape other html text"""
    string = string.strip()
    string = escape(string)
##    index = 1
##    while 1:
##        match = BUG_REGEX.search(string, index)
##        if not match:
##            break
##        start = match.start()
##        end = match.end()
##        substring = string[start:end]
##        if substring[0] == '#':  # this of the form "#1234"
##            bugid = substring[1:]
##        else: # this is of the form "bug 1234"
##            bugid = substring[4:]
##        url = '<a href="/bugs/%s">%s</a>' % (bugid, substring)
##        (string, index) = mstring.replace_sub(string, url, start , end-1)
    index = 0
    string = BUG_REGEX.sub(r'<a href="/bugs/\3">\1</a>', string)
    match = DATE_REGEX.search(string, index)
    if match:
        start = match.start()
        next = DATE_REGEX.search(string, match.end() + 1)
        if next:
            end = next.start() - 1
        else:
            end = len(string)
        substring = string[start:end]
        html = '<span class="change"><span class="date">%s</span>%s</span>' % \
            (substring[:11], substring[11:])
        (string, index) = mstring.replace_sub(string[:end+1], html, start, end)
    #s = '<ul>' + s + '</ul>\n'
    # convert email address to links to CIA stats
    string = GENTOO_DEV.sub(r'(<a href="/stats/\2">\1</a>)', string)
    return string

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
