# Distributed under the GNU General Public License version 2
# Copyright 2003-2004 Gentoo Technologies, Inc.
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/Attic/stage2_target.py,v 1.1 2004/05/17 01:21:17 zhen Exp $

"""
Builder class for a stage2 installation tarball build.
"""

import os,string,imp,types,shutil
from catalyst_support import *
from generic_stage_target import *
from stat import *

class stage2_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=[]
		self.valid_values=[]
		generic_stage_target.__init__(self,spec,addlargs)

def register(foo):
	foo.update({"stage2":stage2_target})
	return foo
