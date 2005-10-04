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
"""Images Directory"""


_q_exports = (('opdlogo.png', 'opdlogo'),
    ('pgoimage.png', 'pgoimage'),
    ('favicon.ico', 'favicon'),
    ('bgcolor.png', 'bgcolor'),
    ('purplebevel.png', 'purplebevel'),
    ('bugs.png', 'bugs_png'),
    ('forums.png', 'forums_png'),
    ('homepage.png', 'homepage_png'),
    ('changelog.png', 'changelog_png'),
    ('alpha.png', 'alpha_png'),
    ('triangle_bullet.gif', 'triangle_bullet'),
    ('gtop-www.jpg', 'gtop_www')
)

import os
curdir = os.path.dirname(__file__)
from quixote.util import StaticFile

opdlogo = StaticFile('%s/opd.png' % curdir)
pgoimage = StaticFile('%s/pgo.png' % curdir)
favicon = StaticFile('%s/favicon.ico' % curdir,
    mime_type='image/x-icon')
bgcolor = StaticFile('%s/bgcolor.png' % curdir)
purplebevel = StaticFile('%s/purplebevel.png' % curdir)

# P.G.O. Icons contributed by Alexandre Rostovtsev <tetromino@gmail.com>
bugs_png = StaticFile('%s/bugs.png' % curdir)
forums_png = StaticFile('%s/forums.png' % curdir)
homepage_png = StaticFile('%s/homepage.png' % curdir)
changelog_png = StaticFile('%s/changelog.png' % curdir)
alpha_png = StaticFile('%s/alpha.png' % curdir)
triangle_bullet = StaticFile('%s/triangle_bullet.gif' % curdir)
gtop_www = StaticFile('%s/gtop-www.jpg' % curdir)



















