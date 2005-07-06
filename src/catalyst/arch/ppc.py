# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/arch/Attic/ppc.py,v 1.12.2.3 2005/07/06 22:07:18 wolf31o2 Exp $

import os,builder
from catalyst_support import *

# gcc-3.3.3 required to do G5 optimizations
# install a 32bit kernel personality changer (that works) before building on a ppc64 host
# new gcc optimization feature requires -fno-strict-aliasing needed, otherwise code complains 
# use the experimental thing for nptl builds

class generic_ppc(builder.generic):
	"abstract base class for all ppc builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="ppc"
		self.settings["CHOST"]="powerpc-unknown-linux-gnu"
		if self.settings["hostarch"]=="ppc64":
			if not os.path.exists("/usr/bin/linux32"):
				raise CatalystError,"required /usr/bin/linux32 executable not found."
			self.settings["CHROOT"]="/usr/bin/linux32 chroot"
		else:   
			self.settings["CHROOT"]="chroot"

class arch_power_ppc(generic_ppc):
	"builder class for generic powerpc/power"
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mtune=common -fno-strict-aliasing -pipe"

class arch_ppc(generic_ppc):
	"builder class for generic powerpc"
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mtune=powerpc -fno-strict-aliasing -pipe"

class arch_power(generic_ppc):
	"builder class for generic power"
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mtune=power -fno-strict-aliasing -pipe"

class arch_g3(generic_ppc):
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mtune=G3 -fno-strict-aliasing -pipe"

class arch_g4(generic_ppc):
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mtune=G4 -maltivec -mabi=altivec -fno-strict-aliasing -pipe"
		self.settings["HOSTUSE"]=["altivec"]

class arch_g5(generic_ppc):
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mtune=G5 -maltivec -mabi=altivec -fno-strict-aliasing -pipe"
		self.settings["HOSTUSE"]=["altivec"]

def register(foo):
	"Inform main catalyst program of the contents of this plugin."
	foo.update({"ppc":arch_ppc,"power":arch_power,"power-ppc":arch_power_ppc,"g3":arch_g3,"g4":arch_g4,"g5":arch_g5})

