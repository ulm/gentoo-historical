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
"""/updates/ portion of site"""

__revision__ = "$Revision: 1.1.2.2 $"
# $Source: /var/cvsroot/gentoo/src/packages/Attic/updates.py,v $

from config import ARCHLIST
from packages.platform import Platform, TIMEFRAME_RE
from packages.queries import get_updates
from packages.config import DEFAULT_LIMIT

class UpdatesPlatform(Platform):

    def query(self,
        branch,
        count = DEFAULT_LIMIT,
        timeframe = None,
        new = False):
        """Search the db based on criteria"""
        return get_updates(self.platform_name, branch, count = count,
            timeframe = timeframe, new = new)

def _q_index(request):
    return platforms[''].index(request, '')

def stable(request):
    return platforms[''].index(request, 'stable')

def testing(request):
    return platforms[''].index(request, 'testing')


platforms = {}
for arch in [''] + ARCHLIST:
    platforms[arch] = UpdatesPlatform('updates', arch, description =
        'Updates')

def _q_resolve(component):
    print component
    global platforms
    if component in ARCHLIST:
        return platforms[component]

def _q_lookup(request, component):
    print component

_q_exports = list(ARCHLIST) + ['stable', 'testing']
