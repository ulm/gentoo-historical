#!/usr/bin/python -t
#
# Copyright 2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = '$Id: index.py,v 1.1 2005/05/09 20:21:31 hadfield Exp $'
__modulename__ = 'index_main'

import sys
sys.path.insert(0, "../")

import framework.dispatcher as page_handler

page_handler.run("_default")
