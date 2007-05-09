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
/stats/
Like /licenses/ this is only a redirector. Redirect to bugzilla.
"""
from quixote import redirect

_q_exports = []

SBASE = 'http://cia.vc/stats/author/'

def _q_index(_):
    """This should never be called"""
    return redirect(SBASE)

def _q_lookup(_, component):
    """Redirect: component should be a bug number"""
    return redirect('%s%s' % (SBASE, component))
