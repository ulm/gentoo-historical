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
/bumps/ portion of site
We basically subclass Platform :-)
"""

__revision__ = "$Revision: 1.1.2.2 $"
# $Source: /var/cvsroot/gentoo/src/packages/Attic/bumps.py,v $

from packages.config import ARCHLIST, DEFAULT_LIMIT
from packages.platform import Platform
from packages.queries import get_bumps

class BumpsPlatform(Platform):
    """bumps platform, all we really need to do is override query()"""
    def query(self, branch = '', count = DEFAULT_LIMIT, timeframe = None):
        """The query used to get bumps. Imported from the queries module"""
        return get_bumps(self.platform_name, branch, count, timeframe)

def _q_index(request):
    """Page entry point"""
    return platforms[''].index(request, '')

def stable(request):
    """Stable branch"""
    return platforms[''].index(request, 'stable')

def testing(request):
    """Testing branch"""
    return platforms[''].index(request, 'testing')

def _q_resolve(component):
    """If stable/testing is called?"""
    global platforms
    if component in ARCHLIST:
        return platforms[component]

platforms = {}
# we create our various bumps pages for all the architectures
for arch in [''] + ARCHLIST:
    platforms[arch] = BumpsPlatform('bumps', arch, description = 'Version Bumps')

_q_exports = list(ARCHLIST) + ['stable', 'testing']
