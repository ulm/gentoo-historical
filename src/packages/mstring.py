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
"""marduk's helpin' heap 'o string functions"""


def replace_sub(string, new, start, end=None):
    """Replacing substring of s with new, return new string, and position
    directly after substitution
    """
    if end is None:
        end = start
    string2 = string[:start] + new + string[end + 1:]
    newpos = start +  len(new)

    return (string2, newpos)
