# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/Attic/netboot_target.py,v 1.1 2005/04/04 17:48:33 rocket Exp $

"""
Builder class for a netboot build.
"""

import os,string,types
from catalyst_support import *
from generic_stage_target import *

class netboot_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.valid_values = [
			"netboot/kernel/sources",
			"netboot/kernel/config",
			"netboot/kernel/prebuilt",

			"netboot/busybox_config",

			"netboot/extra_files",
			"netboot/packages"
		]
		self.required_values=[]
			
		try:
			if addlargs.has_key("netboot/packages"):
				if type(addlargs["netboot/packages"]) == types.StringType:
					loopy=[addlargs["netboot/packages"]]
				else:
					loopy=addlargs["netboot/packages"]
			
		#	for x in loopy:
		#		self.required_values.append("netboot/packages/"+x+"/files")
		except:
			raise CatalystError,"configuration error in netboot/packages."
		
		
		
		self.set_build_kernel_vars(addlargs)

		generic_stage_target.__init__(self,spec,addlargs)
		if addlargs.has_key("netboot/busybox_config"):
			file_locate(self.settings, ["netboot/busybox_config"])

		# Custom Kernel Tarball --- use that instead ...

		# unless the user wants specific CFLAGS/CXXFLAGS, let's use -Os
		
		for envvar in "CFLAGS", "CXXFLAGS":
			if not os.environ.has_key(envvar) and not addlargs.has_key(envvar):
				self.settings[envvar] = "-Os -pipe"
	
	def set_target_path(self):
		self.settings["target_path"]=self.settings["storedir"]+"/builds/"+self.settings["target_subpath"]

#        def set_root_path(self):
#		# ROOT= variable for emerges
#		self.settings["root_path"]="/tmp/image"

	def set_dest_path(self):
		#destpath=self.settings["chroot_path"]+self.settings["root_path"]
		destpath=self.settings["chroot_path"]+"/tmp/image"

#	def build_packages(self):
#		# build packages
#		if self.settings.has_key("netboot/packages"):
#			mypack=list_bashify(self.settings["netboot/packages"])
#		try:
#			cmd("/bin/bash "+self.settings["controller_file"]+" packages "+mypack)
#		except CatalystError:
#			self.unbind()
#			raise CatalystError,"netboot build aborting due to error."
	
	def build_busybox(self):
		# build busybox
		if self.settings.has_key("netboot/busybox_config"):
			mycmd = self.settings["netboot/busybox_config"]
		else:
			mycmd = ""
		try:
			cmd("/bin/bash "+self.settings["controller_file"]+" busybox "+ mycmd)
		except CatalystError:
			self.unbind()
			raise CatalystError,"netboot build aborting due to error."
	

	def copy_files_to_image(self):
		# create image
		myfiles=[]
		if self.settings.has_key("netboot/packages"):
			if type(self.settings["netboot/packages"]) == types.StringType:
				loopy=[self.settings["netboot/packages"]]
			else:
				loopy=self.settings["netboot/packages"]
		
		for x in loopy:
			if self.settings.has_key("netboot/packages/"+x+"/files"):
			    if type(self.settings["netboot/packages/"+x+"/files"]) == types.ListType:
				    myfiles.extend(self.settings["netboot/packages/"+x+"/files"])
			    else:
				    myfiles.append(self.settings["netboot/packages/"+x+"/files"])

		if self.settings.has_key("netboot/extra_files"):
			if type(self.settings["netboot/extra_files"]) == types.ListType:
				myfiles.extend(self.settings["netboot/extra_files"])
			else:
				myfiles.append(self.settings["netboot/extra_files"])

		try:
			cmd("/bin/bash "+self.settings["controller_file"]+\
				" image " + list_bashify(myfiles))
		except CatalystError:
			self.unbind()
			raise CatalystError,"netboot build aborting due to error."


	def create_netboot_files(self):
		# finish it all up
		try:
			cmd("/bin/bash "+self.settings["controller_file"]+" finish")
		except CatalystError:
			self.unbind()
			raise CatalystError,"netboot build aborting due to error."

		# end
		print "netboot: build finished !"


	def set_action_sequence(self):
	    self.settings["action_sequence"]=["dir_setup","unpack","unpack_snapshot",
	    				"config_profile_link","setup_confdir","bind","chroot_setup",\
						"setup_environment","build_packages","build_busybox",\
						"build_kernel","copy_files_to_image","clear_autoresume",\
						"clean","create_netboot_files","unbind"]

def register(foo):
	foo.update({"netboot":netboot_target})
	return foo
