# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/Attic/stage1_target.py,v 1.5 2004/12/17 21:18:06 wolf31o2 Exp $

"""
Builder class for a stage1 installation tarball build.
"""

from catalyst_support import *
from generic_stage_target import *

class stage1_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=[]
		self.valid_values=[]
		generic_stage_target.__init__(self,spec,addlargs)

def register(foo):
	foo.update({"stage1":stage1_target})
	return foo
