# $Header: /var/cvsroot/gentoo/src/catalyst/arch/Attic/sparc64.py,v 1.7 2006/10/02 20:41:53 wolf31o2 Exp $

import builder,os
from catalyst_support import *

class generic_sparc64(builder.generic):
	"abstract base class for all sparc64 builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="sparc64"
		self.settings["CHROOT"]="chroot"

class arch_sparc64(generic_sparc64):
	"builder class for generic sparc64 (sun4u)"
	def __init__(self,myspec):
		generic_sparc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mcpu=ultrasparc -pipe"
		self.settings["CXXFLAGS"]="-O2 -mcpu=ultrasparc -pipe"
		self.settings["CHOST"]="sparc-unknown-linux-gnu"

def register(foo):
	"Inform main catalyst program of the contents of this plugin."
	foo.update({"sparc64":arch_sparc64})
