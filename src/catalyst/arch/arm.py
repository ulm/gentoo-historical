# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/arch/Attic/arm.py,v 1.5 2005/04/04 17:48:32 rocket Exp $

import builder,os
from catalyst_support import *

class generic_arm(builder.generic):
	"Abstract base class for all arm (little endian) builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="arm"
		self.settings["CHROOT"]="chroot"
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CXXFLAGS"]="-O1 -pipe"
   
class generic_armeb(builder.generic):
	"Abstract base class for all arm (big endian) builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="arm"
		self.settings["CHROOT"]="chroot"
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CXXFLAGS"]="-O1 -pipe"

class arch_arm(generic_arm):
	"Builder class for arm (little endian) target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="arm-unknown-linux-gnu"

class arch_armeb(generic_armeb):
	"Builder class for arm (big endian) target"
	def __init__(self,myspec):
		generic_armeb.__init__(self,myspec)
		self.settings["CHOST"]="armeb-unknown-linux-gnu"

class arch_armv4l(generic_arm):
	"Builder class for armv4l (StrongArm-110) target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -mcpu=strongarm110"
		self.settings["CHOST"]="armv4l-unknown-linux-gnu"

class arch_armv5b(generic_arm):
	"Builder class for armv5b (XScale) target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -mcpu=xscale"
		self.settings["CHOST"]="armv5b-unknown-linux-gnu"

def register(foo):
	"Inform main catalyst program of the contents of this plugin."
	foo.update({
		"arm"    : arch_arm,
		"armv4l" : arch_armv4l,
		"armeb"  : arch_armeb,
		"armv5b" : arch_armv5b

	})
