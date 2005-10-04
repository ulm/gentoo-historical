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
# $Source: /var/cvsroot/gentoo/src/packages/Attic/new.py,v $

from config import ARCHLIST, DEFAULT_LIMIT
from packages.updates import UpdatesPlatform

class NewPlatform(UpdatesPlatform):

    def query(self, branch = '', count = DEFAULT_LIMIT, timeframe = None):
        return UpdatesPlatform.query(self, branch, count = count,
            timeframe = timeframe, new = True)

def _q_index(request):
    return platforms[''].index(request, '')

def stable(request):
    return platforms[''].index(request, 'stable')

def testing(request):
    return platforms[''].index(request, 'testing')

def _q_resolve(component):
    global platforms
    if component in ARCHLIST:
        return platforms[component]

platforms = {}
for arch in [''] + ARCHLIST:
    platforms[arch] = NewPlatform('new', arch, description = 'New Packages')

_q_exports = list(ARCHLIST) + ['stable', 'testing']
