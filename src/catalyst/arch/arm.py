# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/arch/Attic/arm.py,v 1.3 2004/10/15 02:36:00 zhen Exp $

import builder,os
from catalyst_support import *

class generic_arm(builder.generic):
	"Abstract base class for all arm builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="arm"
		self.settings["CHROOT"]="chroot"
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CXXFLAGS"]="-O1 -pipe"

class arch_arm(generic_arm):
	"Builder class for arm target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="arm-unknown-linux-gnu"

class arch_armv4l(generic_arm):
	"Builder class for armv4l (StrongArm-110) target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -mcpu=strongarm110"
		self.settings["CHOST"]="armv4l-unknown-linux-gnu"

def register(foo):
	"Inform main catalyst program of the contents of this plugin."
	foo.update({
		"arm"    : arch_arm,
		"armv4l" : arch_armv4l
	})
