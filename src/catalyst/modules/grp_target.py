# Distributed under the GNU General Public License version 2
# Copyright 2003-2004 Gentoo Technologies, Inc.
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/Attic/grp_target.py,v 1.2 2004/07/03 00:33:37 zhen Exp $

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
		
		self.required_values.extend(["grp","grp/use"])
		if type(addlargs["grp"])==types.StringType:
			addlargs["grp"]=[addlargs["grp"]]
			
		for x in addlargs["grp"]:
			self.required_values.append("grp/"+x+"/packages")
			self.required_values.append("grp/"+x+"/type")
			
		generic_stage_target.__init__(self,spec,addlargs)

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

def register(foo):
	foo.update({"grp":grp_target})
	return foo
