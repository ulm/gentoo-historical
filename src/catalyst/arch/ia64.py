# Distributed under the GNU General Public License version 2
# Copyright 2003-2004 Gentoo Technologies, Inc.

import builder,os
from catalyst_support import *

class arch_ia64(build.generic):
	"builder class for ia64"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="ia64"
		self.settings["CHROOT"]="chroot"
		self.settings["CFLAGS"]="-O2"
		self.settings["CHOST"]="ia64-unknown-linux-gnu"

def register(foo):
	"Inform main catalyst program of the contents of this plugin."
	foo.update({ "ia64":arch_ia64 })
