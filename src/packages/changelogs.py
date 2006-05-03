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

import mstring
import re
from cgi import escape

#BUG_REGEX = re.compile(r'#[0-9]+|bug [0-9]+',re.I)
BUG_REGEX = re.compile(r'((\B#|\bbug )([0-9]+))', re.I)
DATE_REGEX = re.compile(
    r'[0-9]{2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [0-9]{4}[;:]',
    re.M)
GENTOO_DEV = re.compile(r'&lt;((.+))@gentoo.org&gt;', re.I)
BUG_URL = 'http://bugs.gentoo.org/show_bug.cgi?id='
CIA_URL = 'http://cia.navi.cx/stats/author/'

def bugs_to_html(string):
    """Convert bug #'s to html, escape other html text"""
    string = string.strip()
    string = escape(string)
    index = 0
    string = BUG_REGEX.sub('<a href="%s\\3">\\1</a>' % BUG_URL, string)
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
    string = GENTOO_DEV.sub('(<a href="%s\\2">\\1</a>)' % CIA_URL, string)
    return '<span style="white-space: pre">%s\n\n</span>' % string

def changelog(filename):
	try:
		#print filename
		fp = open(filename,'r')
	except IOError:
		return ""


	s = ""
	# find first line that isn't blank or a comment
	while True:
		line = fp.readline()
		if not line: break
		#print line
		if line[0] not in ['#','','\n']:
			s = s + line
			break
	
	# append next strings until you reach next "*"
	while True:
		line = fp.readline()
		#print repr(line)
		if not line or line[0] == '*': break
		else: s= s + line
	
	return s
