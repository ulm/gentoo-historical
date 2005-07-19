# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/Attic/grp_target.py,v 1.6.2.4 2005/07/19 21:26:29 rocket Exp $

"""
The builder class for GRP (Gentoo Reference Platform) builds.
"""

import os,types
from catalyst_support import *
from generic_stage_target import *

class grp_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=["version_stamp","target","subarch",\
			"rel_type","profile","snapshot","source_subpath"]
		
		self.valid_values=self.required_values[:]
		if not addlargs.has_key("grp"):
			raise CatalystError,"Required value \"grp\" not specified in spec."
		
		self.required_values.extend(["grp"])
		if type(addlargs["grp"])==types.StringType:
			addlargs["grp"]=[addlargs["grp"]]

		if addlargs.has_key("grp/use"):
		    if type(addlargs["grp/use"])==types.StringType:
			    addlargs["grp/use"]=[addlargs["grp/use"]]
			
		for x in addlargs["grp"]:
			self.required_values.append("grp/"+x+"/packages")
			self.required_values.append("grp/"+x+"/type")
			
		generic_stage_target.__init__(self,spec,addlargs)
	
	def set_target_path(self):
	    self.settings["target_path"]=self.settings["storedir"]+"/builds/"+self.settings["target_subpath"]
	
	def run_local(self):
		for pkgset in self.settings["grp"]:
			# example call: "grp.sh run pkgset cd1 xmms vim sys-apps/gleep"
			mypackages=list_bashify(self.settings["grp/"+pkgset+"/packages"])
			try:
				cmd("/bin/bash "+self.settings["sharedir"]+\
					"/targets/grp/grp.sh run "+self.settings["grp/"+pkgset+"/type"]\
					+" "+pkgset+" "+mypackages)
			
			except CatalystError:
				self.unbind()
				raise CatalystError,"GRP build aborting due to error."

	def set_action_sequence(self):
	    self.settings["action_sequence"]=["dir_setup","unpack_and_bind","chroot_setup",\
	    				    "setup_environment","run_local","unbind"]
	
	def set_use(self):
	    if self.settings.has_key("grp/use"):
		self.settings["use"]=self.settings["grp/use"]
		self.settings["use"].append("bindist")
	    else:
		self.settings["use"]=["bindist"]

	def set_mounts(self):
	    self.mounts.append("/tmp/grp")
            self.mountmap["/tmp/grp"]=self.settings["target_path"]

def register(foo):
	foo.update({"grp":grp_target})
	return foo
