# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/arch/Attic/ppc64.py,v 1.2.2.2 2005/07/23 17:34:48 wolf31o2 Exp $

import builder

class generic_ppc64(builder.generic):
	"abstract base class for all ppc64 builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="ppc64"
		self.settings["CHROOT"]="chroot"

class arch_ppc64(generic_ppc64):
	"builder class for generic ppc64 (G5/Power4/Power4+)"
	def __init__(self,myspec):
		generic_ppc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CHOST"]="powerpc64-unknown-linux-gnu"

class arch_970(generic_ppc64):
	"builder class for G5 ppc64"
	def __init__(self,myspec):
		generic_ppc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mtune=970 -mcpu=970 -mabi=altivec -pipe"
		self.settings["HOSTUSE"]=["altivec"]
		self.settings["CHOST"]="powerpc64-unknown-linux-gnu"

class arch_ppc64_32(generic_ppc64):
	"builder class for generic ppc64 with a 32bit userland (G5/Power4/Power4+)"
	def __init__(self,myspec):
		generic_ppc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CHOST"]="powerpc-unknown-linux-gnu"

class arch_970_32(generic_ppc64):
	"builder class for G5 ppc64 with a 32bit userland"
	def __init__(self,myspec):
		generic_ppc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mtune=970 -mcpu=970 -mabi=altivec -pipe"
		self.settings["HOSTUSE"]=["altivec"]
		self.settings["CHOST"]="powerpc-unknown-linux-gnu"

def register(foo):
	"Inform main catalyst program of the contents of this plugin."
	foo.update({"ppc64-64ul":arch_ppc64,"G5-64ul":arch_970,"ppc64-32ul":arch_ppc64_32,"G5-32ul":arch_970_32})
		
