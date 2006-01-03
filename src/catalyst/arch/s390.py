# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/arch/Attic/s390.py,v 1.4 2006/01/03 14:55:11 wolf31o2 Exp $

import builder,os
from catalyst_support import *

class generic_s390(builder.generic):
	"abstract base class for all s390 builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="s390"
		self.settings["CHROOT"]="chroot"

class arch_s390(generic_s390):
	"builder class for generic s390"
	def __init__(self,myspec):
		generic_s390.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CHOST"]="s390-ibm-linux-gnu"

def register(foo):
	"Inform main catalyst program of the contents of this plugin."
	foo.update({"s390":arch_s390})
