# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/Attic/stage1_target.py,v 1.19 2005/12/16 14:42:07 rocket Exp $

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
		self.settings["stage_path"]=normpath(self.settings["chroot_path"]+self.settings["root_path"])
		print "stage1 stage path is "+self.settings["stage_path"]
	def set_root_path(self):
	       # ROOT= variable for emerges
		self.settings["root_path"]=normpath("/tmp/stage1root")
		print "stage1 root path is "+self.settings["root_path"]
	def set_dest_path(self):
                self.settings["destpath"]=normpath(self.settings["chroot_path"]+self.settings["root_path"])
	def set_cleanables(self):
		generic_stage_target.set_cleanables(self)
		self.settings["cleanables"].extend(["/usr/share/gettext","/usr/lib/python2.2/test", "/usr/lib/python2.2/encodings","/usr/lib/python2.2/email", "/usr/lib/python2.2/lib-tk","/usr/share/zoneinfo"])

	def set_portage_overlay(self):
		generic_stage_target.set_portage_overlay(self)
		if self.settings.has_key("portage_overlay"):
			print "\nWARNING !!!!!"
			print "\tUsing an portage overlay for earlier stages could cause build issues."
			print "\tIf you break it, you buy it. Don't complain to us about it."
			print "\tDont say we did not warn you\n"
def register(foo):
	foo.update({"stage1":stage1_target})
	return foo
