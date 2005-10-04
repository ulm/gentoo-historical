"""

Gentoo Online Package Database 
==============================

Dependencies
------------
This package depends on:
    * Quixote_        
    * MySQL_
    * 'MySQL Python'_
    * ElementTree_

.. _Gentoo Online Package Database: http://packages.gentoo.org/
.. _Quixote: http://www.mems-exchange.org/software/quixote/
.. _MySQL: http://www.mysql.com/
.. _MySQL Python: http://sourceforge.net/projects/mysql-python/
.. _ElementTree: http://effbot.org/zone/element-index.htm

"""

__all__ = []
__docformat__ = 'reStructuredText'

_q_exports = (("portage", "portage_ui"), "updates", "new", "bumps", "css",
    "stats", "licenses","bugs", "images", ("robots.txt", "robots"))

from quixote import enable_ptl
enable_ptl()
from quixote.util import StaticFile
from quixote.html import htmltext
from packages.ui.main import page, sidebox

import os
curdir = os.path.dirname(__file__)

def _q_index(dummy):
    """The main page for packages.gentoo.org"""

    # We basically return a flat file for the main content
    body = open('%s/index.html' % curdir).read()
    sb1 = sidebox('motd', open('%s/motd' % curdir).read())
##    sb2 = sidebox('search', htmltext('<input type="text" name="search">'))
    return page("Welcome to packages.gentoo.org", [htmltext(body), sb1],
            noparent = True)

# Out main sub-pages
# This appears to speed things up
from packages import portage_ui, updates, new, bumps, licenses, bugs, stats, images

# Static files throughout the site
# Defined below
css = StaticFile('%s/style.css' % curdir)
robots = StaticFile('%s/robots.txt' % curdir)

