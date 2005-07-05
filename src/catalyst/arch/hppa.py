# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/arch/Attic/hppa.py,v 1.4.2.2 2005/07/05 21:47:46 wolf31o2 Exp $

import builder,os
from catalyst_support import *

class generic_hppa(builder.generic):
	"Abstract base class for all hppa builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="hppa"
		self.settings["CHROOT"]="chroot"
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CXXFLAGS"]="-O2 -pipe"

class arch_hppa(generic_hppa):
	"Builder class for hppa systems"
	def __init__(self,myspec):
		generic_hppa.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -march=1.1"
		self.settings["CHOST"]="hppa1.1-unknown-linux-gnu"

class arch_hppa1_1(generic_hppa):
	"Builder class for hppa 1.1 systems"
	def __init__(self,myspec):
		generic_hppa.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -march=1.1"
		self.settings["CHOST"]="hppa1.1-unknown-linux-gnu"

class arch_hppa2_0(generic_hppa):
	"Builder class for hppa 2.0 systems"
	def __init__(self,myspec):
		generic_hppa.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -march=2.0"
		self.settings["CHOST"]="hppa2.0-unknown-linux-gnu"

def register(foo):
	"Inform main catalyst program of the contents of this plugin."
	foo.update({
			"hppa":		arch_hppa,
			"hppa1.1":	arch_hppa1_1,
			"hppa2.0":	arch_hppa2_0
	})
