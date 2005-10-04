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



















