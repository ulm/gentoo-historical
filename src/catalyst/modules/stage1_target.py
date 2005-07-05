# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/Attic/stage1_target.py,v 1.6.2.1 2005/07/05 21:47:46 wolf31o2 Exp $

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
	
	def set_stage_path(self):
		self.settings["stage_path"]=self.settings["chroot_path"]+"/tmp/stage1root"
		print "stage1 stage path is "+self.settings["stage_path"]

def register(foo):
	foo.update({"stage1":stage1_target})
	return foo
