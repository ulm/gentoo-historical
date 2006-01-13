# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/Attic/netboot2_target.py,v 1.1 2006/01/13 15:09:07 rocket Exp $

"""
Builder class for a netboot build, version 2
"""

import os,string,types
from catalyst_support import *
from generic_stage_target import *

class netboot2_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.valid_values = [
			"netboot2/extra_files",
		]
		self.required_values=[
			"boot/kernel",
			"netboot2/builddate",
			"netboot2/busybox_config",
			"netboot2/packages"			
		]
			
		try:
			if addlargs.has_key("netboot2/packages"):
				if type(addlargs["netboot2/packages"]) == types.StringType:
					loopy=[addlargs["netboot2/packages"]]
				else:
					loopy=addlargs["netboot2/packages"]
		except:
			raise CatalystError,"configuration error in netboot2/packages."
		
		

		generic_stage_target.__init__(self,spec,addlargs)
		self.set_build_kernel_vars(addlargs)

		# Merge packages into the buildroot, and pick out certain files to place in
		# /tmp/image
		self.settings["merge_path"]=normpath("/tmp/image")

		for envvar in "CFLAGS", "CXXFLAGS":
			if not os.environ.has_key(envvar) and not addlargs.has_key(envvar):
				self.settings[envvar] = "-Os -pipe"

	def set_dest_path(self):
		if self.settings.has_key("merge_path"):
			self.settings["destpath"]=normpath(self.settings["chroot_path"]+self.settings["merge_path"])
		else:
			self.settings["destpath"]=normpath(self.settings["chroot_path"])

	def set_target_path(self):
		self.settings["target_path"]=normpath(self.settings["storedir"]+"/builds/"+\
			self.settings["target_subpath"]+"/")
		if self.settings.has_key("AUTORESUME") \
			and os.path.exists(self.settings["autoresume_path"]+"setup_target_path"):
				print "Resume point detected, skipping target path setup operation..."
		else:
			# first clean up any existing target stuff
			if os.path.isfile(self.settings["target_path"]):
				cmd("rm -f "+self.settings["target_path"], \
					"Could not remove existing file: "+self.settings["target_path"],env=self.env)
				touch(self.settings["autoresume_path"]+"setup_target_path")

		if not os.path.exists(self.settings["storedir"]+"/builds/"):
			os.makedirs(self.settings["storedir"]+"/builds/")

	def copy_files_to_image(self):
		# copies specific files from the buildroot to merge_path
		myfiles=[]

		# check for autoresume point
		if self.settings.has_key("AUTORESUME") \
			and os.path.exists(self.settings["autoresume_path"]+"copy_files_to_image"):
				print "Resume point detected, skipping target path setup operation..."
		else:
			if self.settings.has_key("netboot2/packages"):
				if type(self.settings["netboot2/packages"]) == types.StringType:
					loopy=[self.settings["netboot2/packages"]]
				else:
					loopy=self.settings["netboot2/packages"]
		
			for x in loopy:
				if self.settings.has_key("netboot2/packages/"+x+"/files"):
				    if type(self.settings["netboot2/packages/"+x+"/files"]) == types.ListType:
					    myfiles.extend(self.settings["netboot2/packages/"+x+"/files"])
				    else:
					    myfiles.append(self.settings["netboot2/packages/"+x+"/files"])

			if self.settings.has_key("netboot2/extra_files"):
				if type(self.settings["netboot2/extra_files"]) == types.ListType:
					myfiles.extend(self.settings["netboot2/extra_files"])
				else:
					myfiles.append(self.settings["netboot2/extra_files"])

			try:
				cmd("/bin/bash "+self.settings["controller_file"]+\
					" image " + list_bashify(myfiles),env=self.env)
			except CatalystError:
				self.unbind()
				raise CatalystError,"Failed to copy files to image!"

			touch(self.settings["autoresume_path"]+"copy_files_to_image")


	def move_kernels(self):
		# we're done, move the kernels to builds/*
		# no auto resume here as we always want the
		# freshest images moved
		try:
			cmd("/bin/bash "+self.settings["controller_file"]+\
				" final",env=self.env)
			print ">>> Netboot Build Finished!"
		except CatalystError:
			self.unbind()
			raise CatalystError,"Failed to move kernel images!"


	def set_action_sequence(self):
	    self.settings["action_sequence"]=["unpack","unpack_snapshot","config_profile_link",
	    				"setup_confdir","bind","chroot_setup",\
					"setup_environment","build_packages","root_overlay",\
					"copy_files_to_image","build_kernel","move_kernels",\
					"unbind","clean","clear_autoresume"]

def register(foo):
	foo.update({"netboot2":netboot2_target})
	return foo
