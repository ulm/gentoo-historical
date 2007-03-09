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
"""/licences/ portion of site.  Basically redirects to cvs"""

from quixote import redirect

_q_exports = []

LBASE = 'http://sources.gentoo.org/viewcvs.py/*checkout*/gentoo-x86/licenses'

def _q_index(_):
    """This should never be called..."""
    # TODO:redirect elsewhere as LBASE is not accessible
    return redirect(LBASE)

def _q_lookup(_, component):
    """component will be a particular license"""
    return redirect('%s/%s' % (LBASE, component))
