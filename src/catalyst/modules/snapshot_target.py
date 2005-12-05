# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/Attic/snapshot_target.py,v 1.13 2005/12/05 18:13:12 rocket Exp $

"""
Builder class for snapshots.
"""

import os
from catalyst_support import *
from generic_stage_target import *

class snapshot_target(generic_target):
	def __init__(self,myspec,addlargs):
		self.required_values=["version_stamp","target"]
		self.valid_values=["version_stamp","target","portdir_overlay"]
		
		generic_target.__init__(self,myspec,addlargs)
		self.settings=myspec
		self.settings["target_subpath"]="portage"
		st=self.settings["storedir"]
		self.settings["snapshot_path"]=normpath(st+"/snapshots/portage-"+self.settings["version_stamp"]\
			+".tar.bz2")
		self.settings["tmp_path"]=normpath(st+"/tmp/"+self.settings["target_subpath"])

	def setup(self):
		x=normpath(self.settings["storedir"]+"/snapshots")
		if not os.path.exists(x):
			os.makedirs(x)
	
	def mount_safety_check(self):
		pass
		
	def run(self):
		self.setup()
		print "Creating Portage tree snapshot "+self.settings["version_stamp"]+\
			" from "+self.settings["portdir"]+"..."
		
		mytmp=self.settings["tmp_path"]
		if not os.path.exists(mytmp):
			os.makedirs(mytmp)
		
		cmd("rsync -a --delete --exclude /packages/ --exclude /distfiles/ --exclude /local/ --exclude CVS/ "+\
			self.settings["portdir"]+"/ "+mytmp+"/portage/","Snapshot failure",env=self.env)
		
		if self.settings.has_key("portdir_overlay"):
			print "Adding Portage overlay to the snapshot..."
			cmd("rsync -a --exclude /packages/ --exclude /distfiles/ --exclude /local/ --exclude CVS/ "+\
				self.settings["portdir_overlay"]+"/ "+mytmp+"/portage/","Snapshot/ overlay addition failure",\
				env=self.env)
			
		print "Compressing Portage snapshot tarball..."
		cmd("tar cjf "+self.settings["snapshot_path"]+" -C "+mytmp+" portage",\
			"Snapshot creation failure",env=self.env)
		self.cleanup()
		print "snapshot: complete!"
	
	def kill_chroot_pids(self):
		pass

	def cleanup(self):
		print "Cleaning up..."
			
def register(foo):
	foo.update({"snapshot":snapshot_target})
	return foo
