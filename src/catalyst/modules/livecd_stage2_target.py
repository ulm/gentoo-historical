# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/Attic/livecd_stage2_target.py,v 1.34 2005/04/14 14:59:48 rocket Exp $

"""
Builder class for a LiveCD stage2 build.
"""

import os,string,types,stat,shutil
from catalyst_support import *
from generic_stage_target import *

class livecd_stage2_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=["boot/kernel","livecd/cdfstype"]
		
		self.valid_values=[]
		
		self.valid_values.extend(self.required_values)
		self.valid_values.extend(["livecd/cdtar","livecd/empty","livecd/rm",\
			"livecd/unmerge","livecd/iso","livecd/gk_mainargs","livecd/type",\
			"livecd/motd","livecd/overlay","livecd/modblacklist","livecd/splash_theme",\
			"livecd/rcadd","livecd/rcdel","livecd/fsscript","livecd/xinitrc",\
			"livecd/root_overlay","livecd/devmanager","livecd/splash_type",\
			"gamecd/conf","portage_overlay"])
		
		generic_stage_target.__init__(self,spec,addlargs)
		
		file_locate(self.settings, ["livecd/cdtar","controller_file"])
		

	def set_target_path(self):
	    self.settings["target_path"]=self.settings["storedir"]+"/builds/"+self.settings["target_subpath"]
	    	
	def set_source_path(self):
	    self.settings["source_path"]=self.settings["storedir"]+"/builds/"+self.settings["source_subpath"]+".tar.bz2"
	    if os.path.isfile(self.settings["source_path"]):
		if os.path.exists(self.settings["source_path"]):
		    self.settings["source_path_md5sum"]=calc_md5(self.settings["source_path"])
	    else:
		self.settings["source_path"]=self.settings["storedir"]+"/tmp/"+self.settings["source_subpath"]
	
	def set_spec_prefix(self):
	    self.settings["spec_prefix"]="livecd"

		
	def unpack(self):
		if not os.path.isdir(self.settings["source_path"]):
			generic_stage_target.unpack(self)
		else:
		    if self.settings.has_key("AUTORESUME") \
			    and os.path.exists(self.settings["autoresume_path"]+"unpack"):
			    print "Resume point detected, skipping unpack operation..."
		    else:
			    if not os.path.exists(self.settings["chroot_path"]):
				    os.makedirs(self.settings["chroot_path"])
				
			    print "Copying livecd-stage1 result to new livecd-stage2 work directory..."
			    cmd("rsync -a --delete "+self.settings["source_path"]+"/* "+self.settings["chroot_path"],\
				    "Error copying initial livecd-stage2")
			    touch(self.settings["autoresume_path"]+"unpack")

	def run_local(self):
		# first clean up any existing target stuff
		if os.path.exists(self.settings["target_path"]):
			print "cleaning previous livecd-stage2 build"
			cmd("rm -rf "+self.settings["target_path"],
				"Could not remove existing directory: "+self.settings["target_path"])
			
		if not os.path.exists(self.settings["target_path"]):
			os.makedirs(self.settings["target_path"])
				
		# what modules do we want to blacklist?
		if self.settings.has_key("livecd/modblacklist"):
			try:
				myf=open(self.settings["chroot_path"]+"/etc/hotplug/blacklist","a")
			except:
				self.unbind()
				raise CatalystError,"Couldn't open "+self.settings["chroot_path"]+"/etc/hotplug/blacklist."
			myf.write("\n#Added by Catalyst:")
			for x in self.settings["livecd/modblacklist"]:
				myf.write("\n"+x)
			myf.close()

	def set_action_sequence(self):
	    self.settings["action_sequence"]=["dir_setup","unpack","unpack_snapshot",\
			    "config_profile_link","setup_confdir","portage_overlay",\
			    "bind","chroot_setup","setup_environment","run_local",\
			    "root_overlay","build_kernel","bootloader","preclean",\
			    "fsscript","rcupdate","unmerge","unbind","remove",\
			    "empty","target_setup",\
			    "setup_overlay","create_iso","clear_autoresume"]

def register(foo):
	foo.update({"livecd-stage2":livecd_stage2_target})
	return foo
