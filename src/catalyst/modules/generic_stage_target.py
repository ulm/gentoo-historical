# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/Attic/generic_stage_target.py,v 1.24.2.1 2005/05/03 15:40:51 rocket Exp $

"""
This class does all of the chroot setup, copying of files, etc. It is
the driver class for pretty much everything that Catalyst does.
"""

import os,string,imp,types,shutil
from catalyst_support import *
from generic_target import *
from stat import *

class generic_stage_target(generic_target):

	def __init__(self,myspec,addlargs):
		
		self.required_values.extend(["version_stamp","target","subarch","rel_type",\
			"profile","snapshot","source_subpath"])
		
		self.valid_values.extend(["version_stamp","target","subarch","rel_type","profile",\
			"snapshot","source_subpath","portage_confdir"])
		generic_target.__init__(self,addlargs,myspec)
		
		# map the mainarch we are running under to the mainarches we support for
		# building stages and LiveCDs. (for example, on amd64, we can build stages for
		# x86 or amd64.
		targetmap={
				"x86" : ["x86"],
				"amd64" : ["x86","amd64"],
				"sparc64" : ["sparc","sparc64"],
				"ia64" : ["ia64"],
				"alpha" : ["alpha"],
				"sparc" : ["sparc"],
				"s390" : ["s390"],
				"ppc" : ["ppc"],
				"ppc64" : ["ppc","ppc64"],
				"hppa" : ["hppa"],
				"mips" : ["mips"],
				"arm" : ["arm"]
		}
		
		machinemap={
				"i386" : "x86",
				"i486" : "x86",
				"i586" : "x86",
				"i686" : "x86",
				"x86_64" : "amd64",
				"sparc64" : "sparc64",
				"ia64" : "ia64",
				"alpha" : "alpha",
				"sparc" : "sparc",
				"s390" : "s390",
				"ppc" : "ppc",
				"ppc64" : "ppc64",
				"parisc" : "hppa",
				"parisc64" : "hppa",
				"mips" : "mips",
				"mips64" : "mips",
				"arm" : "arm",
				"armv4l" : "arm",
				"armeb" : "arm",
				"armv5b" : "arm"
		}
		
		mymachine=os.uname()[4]
		if not machinemap.has_key(mymachine):
			raise CatalystError, "Unknown machine type "+mymachine
			
		self.settings["hostarch"]=machinemap[mymachine]
		self.archmap={}
		self.subarchmap={}
		
		for x in targetmap[self.settings["hostarch"]]:
			try:
				fh=open(self.settings["sharedir"]+"/arch/"+x+".py")
				# this next line loads the plugin as a module and assigns it to archmap[x]
				self.archmap[x]=imp.load_module(x,fh,"arch/"+x+".py",(".py","r",imp.PY_SOURCE))
				# this next line registers all the subarches supported in the plugin
				self.archmap[x].register(self.subarchmap)
				fh.close()	
			
			except IOError:
				msg("Can't find "+x+".py plugin in "+self.settings["sharedir"]+"/arch/")
		
		# call arch constructor, pass our settings
		self.arch=self.subarchmap[self.settings["subarch"]](self.settings)
		
		# self.settings["mainarch"] should now be set by our arch constructor, so we print
		# a nice informational message:
		if self.settings["mainarch"]==self.settings["hostarch"]:
			print "Building natively for",self.settings["hostarch"]
		
		else:
			print "Building on",self.settings["hostarch"],"for alternate machine type",\
				self.settings["mainarch"]
		
		# grab build settings from the environment
		for envvar in "CHOST", "CFLAGS", "CXXFLAGS":
			if os.environ.has_key(envvar):
				self.settings[envvar] = os.environ[envvar]
		
		# define all of our core variables
		self.set_target_profile()
		self.set_target_subpath()
		self.set_snapshot_path()
		self.set_target_path()
		self.set_source_path()
		self.set_chroot_path()
		self.set_action_sequence()
		self.set_use()
		self.set_stage_path()

		# this next line checks to make sure that the specified variables exist on disk.
		file_locate(self.settings,["source_path","snapshot_path","distdir"],expand=0)
		
		# if we are using portage_confdir, check that as well
		if self.settings.has_key("portage_confdir"):
			file_locate(self.settings,["portage_confdir"],expand=0)
		
		# setup our mount points
		self.mounts=[ "/proc","/dev","/dev/pts","/usr/portage/distfiles" ]
		self.mountmap={"/proc":"/proc", "/dev":"/dev", "/dev/pts":"/dev/pts",\
			"/usr/portage/distfiles":self.settings["distdir"]}
		self.set_mounts()

		# configure any user specified options (either in catalyst.conf or on the cmdline)
		if self.settings.has_key("PKGCACHE"):
			self.settings["pkgcache_path"]=self.settings["storedir"]+"/packages/"+self.settings["target_subpath"]
			self.mounts.append("/usr/portage/packages")
			self.mountmap["/usr/portage/packages"]=self.settings["pkgcache_path"]

		if self.settings.has_key("CCACHE"):
			if os.environ.has_key("CCACHE_DIR"):
				ccdir=os.environ["CCACHE_DIR"]
				del os.environ["CCACHE_DIR"]
			else:
				ccdir="/root/.ccache"
			if not os.path.isdir(ccdir):
					raise CatalystError,\
						"Compiler cache support can't be enabled (can't find "+ccdir+")"
			self.mounts.append("/var/tmp/ccache")
			self.mountmap["/var/tmp/ccache"]=ccdir
			# for the chroot:
			os.environ["CCACHE_DIR"]="/var/tmp/ccache"	
		
	def set_target_profile(self):
		self.settings["target_profile"]=self.settings["profile"]
	
	def set_target_subpath(self):
		self.settings["target_subpath"]=self.settings["rel_type"]+"/"+self.settings["target"]+\
			"-"+self.settings["subarch"]+"-"+self.settings["version_stamp"]

	def set_target_path(self):
		self.settings["target_path"]=self.settings["storedir"]+"/builds/"+self.settings["target_subpath"]+".tar.bz2"
	
	def set_source_path(self):
		self.settings["source_path"]=self.settings["storedir"]+"/builds/"+self.settings["source_subpath"]+".tar.bz2"
	
	def set_snapshot_path(self):
		self.settings["snapshot_path"]=self.settings["storedir"]+"/snapshots/portage-"+self.settings["snapshot"]+".tar.bz2"
	
	def set_chroot_path(self):
		self.settings["chroot_path"]=self.settings["storedir"]+"/tmp/"+self.settings["target_subpath"]

	def set_action_sequence(self):
		#Default action sequence for run method
		self.settings["action_sequence"]=["dir_setup","unpack_and_bind","chroot_setup",\
				"setup_environment","run_local","preclean","unbind","clean","capture"]
	
	def set_use(self):
		pass

	def set_stage_path(self):
			self.settings["stage_path"]=self.settings["chroot_path"]
	def set_mounts(self):
		pass
	
        def kill_chroot_pids(self):
		# Force environment variables to be exported so script can see them
		self.setup_environment()

		if os.path.exists(self.settings["sharedir"]+"/targets/support/kill-chroot-pids.sh"):
		    cmd("/bin/bash "+self.settings["sharedir"]+"/targets/support/kill-chroot-pids.sh","kill-chroot-pids script failed.")


	def mount_safety_check(self):
		mypath=self.settings["chroot_path"]
		
		"""
		check and verify that none of our paths in mypath are mounted. We don't want to clean
		up with things still mounted, and this allows us to check. 
		returns 1 on ok, 0 on "something is still mounted" case.
		"""
		if not os.path.exists(mypath):
			return
			
		for x in self.mounts:
			if not os.path.exists(mypath+x):
				continue
			
			if ismount(mypath+x):
				#something is still mounted
				try:
					print x+" is still mounted; performing auto-bind-umount..."
					# try to umount stuff ourselves
					self.unbind()
					if ismount(mypath+x):
						raise CatalystError, "Auto-unbind failed for "+x
					
					else:
						print "Auto-unbind successful, continuing..."
				
				except CatalystError:
					raise CatalystError, "Unable to auto-unbind "+x
		
	def dir_setup(self):
		print "Setting up directories..."
		self.mount_safety_check()
		
		if os.path.exists(self.settings["chroot_path"]):
			cmd("rm -rf "+self.settings["chroot_path"],\
				"Could not remove existing directory: "+self.settings["chroot_path"])
			
		if not os.path.exists(self.settings["chroot_path"]+"/tmp"):
			os.makedirs(self.settings["chroot_path"]+"/tmp",1777)
			
		if not os.path.exists(self.settings["chroot_path"]):
			os.makedirs(self.settings["chroot_path"],0755)
		
		if self.settings.has_key("PKGCACHE"):	
			if not os.path.exists(self.settings["pkgcache_path"]):
				os.makedirs(self.settings["pkgcache_path"],0755)
	
		
	def unpack_and_bind(self):
		print "Unpacking stage tarball..."
		cmd("tar xjpf "+self.settings["source_path"]+" -C "+self.settings["chroot_path"],\
			"Error unpacking tarball")
				
		if os.path.exists(self.settings["chroot_path"]+"/usr/portage"):
			print "Cleaning up existing portage tree snapshot..."
			cmd("rm -rf "+self.settings["chroot_path"]+"/usr/portage",\
				"Error removing existing snapshot directory.")
			
		print "Unpacking portage tree snapshot..."
		cmd("tar xjpf "+self.settings["snapshot_path"]+" -C "+\
			self.settings["chroot_path"]+"/usr","Error unpacking snapshot")
			
		print "Configuring profile link..."
		cmd("rm -f "+self.settings["chroot_path"]+"/etc/make.profile",\
			"Error zapping profile link")
		cmd("ln -sf ../usr/portage/profiles/"+self.settings["target_profile"]+\
			" "+self.settings["chroot_path"]+"/etc/make.profile","Error creating profile link")
		
		if self.settings.has_key("portage_confdir"):
			print "Configuring /etc/portage..."
			cmd("rm -rf "+self.settings["chroot_path"]+"/etc/portage","Error zapping /etc/portage")
			cmd("cp -R "+self.settings["portage_confdir"]+"/ "+self.settings["chroot_path"]+\
				"/etc/portage","Error copying /etc/portage")

		for x in self.mounts: 
			if not os.path.exists(self.settings["chroot_path"]+x):
				os.makedirs(self.settings["chroot_path"]+x,0755)
			
			if not os.path.exists(self.mountmap[x]):
				os.makedirs(self.mountmap[x],0755)
			
			src=self.mountmap[x]
			retval=os.system("mount --bind "+src+" "+self.settings["chroot_path"]+x)
			if retval!=0:
				self.unbind()
				raise CatalystError,"Couldn't bind mount "+src
		
	def unbind(self):
		ouch=0
		mypath=self.settings["chroot_path"]
		myrevmounts=self.mounts[:]
		myrevmounts.reverse()
		# unmount in reverse order for nested bind-mounts
		for x in myrevmounts:
			if not os.path.exists(mypath+x):
				continue
			
			if not ismount(mypath+x):
				# it's not mounted, continue
				continue
			
			retval=os.system("umount "+mypath+x)
			
			if retval!=0:
				ouch=1
				warn("First attempt to unmount: "+mypath+x+" failed.")
				warn("Killing any pids still running in the chroot")

				self.kill_chroot_pids()

				retval2=os.system("umount "+mypath+x)
				if retval2!=0:
				    ouch=1
				    warn("Couldn't umount bind mount: "+mypath+x)
				    # keep trying to umount the others, to minimize damage if developer makes a mistake

		if ouch:
			"""
			if any bind mounts really failed, then we need to raise
			this to potentially prevent an upcoming bash stage cleanup script
			from wiping our bind mounts.
			"""
			raise CatalystError,"Couldn't umount one or more bind-mounts; aborting for safety."

	def chroot_setup(self):
		print "Setting up chroot..."
		cmd("cp /etc/resolv.conf "+self.settings["chroot_path"]+"/etc",\
			"Could not copy resolv.conf into place.")
		
		# copy over the envscript, if applicable
		if self.settings.has_key("ENVSCRIPT"):
			if not os.path.exists(self.settings["ENVSCRIPT"]):
				raise CatalystError, "Can't find envscript "+self.settings["ENVSCRIPT"]
			cmd("cp "+self.settings["ENVSCRIPT"]+" "+self.settings["chroot_path"]+"/tmp/envscript",\
				"Could not copy envscript into place.")

		# copy over /etc/hosts from the host in case there are any specialties in there
		if os.path.exists("/etc/hosts"):
			cmd("mv "+self.settings["chroot_path"]+"/etc/hosts "+self.settings["chroot_path"]+\
				"/etc/hosts.bck", "Could not backup /etc/hosts")
			cmd("cp /etc/hosts "+self.settings["chroot_path"]+"/etc/hosts", "Could not copy /etc/hosts")
		
		# modify and write out make.conf (for the chroot)
		cmd("rm -f "+self.settings["chroot_path"]+"/etc/make.conf")
		myf=open(self.settings["chroot_path"]+"/etc/make.conf","w")
		myf.write("# These settings were set by the catalyst build script that automatically built this stage\n")
		myf.write("# Please consult /etc/make.conf.example for a more detailed example\n")
		myf.write('CFLAGS="'+self.settings["CFLAGS"]+'"\n')
		myf.write('CHOST="'+self.settings["CHOST"]+'"\n')
		# figure out what our USE vars are for building
		myusevars=[]
		if self.settings.has_key("HOSTUSE"):
			myusevars.extend(self.settings["HOSTUSE"])
		
		if self.settings.has_key("use"):
			myusevars.extend(self.settings["use"])
			myf.write('USE="'+string.join(myusevars)+'"\n')
		
		if self.settings.has_key("CXXFLAGS"):
			myf.write('CXXFLAGS="'+self.settings["CXXFLAGS"]+'"\n')
		
		else:
			myf.write('CXXFLAGS="${CFLAGS}"\n')
		myf.close()
	
	def clean(self):
		destpath=self.settings["chroot_path"]
		
		cleanables=["/etc/resolv.conf","/var/tmp/*","/tmp/*","/root/*","/usr/portage"]
			
		if self.settings["target"]=="stage1":
			destpath+="/tmp/stage1root"
			# this next stuff can eventually be integrated into the python
			# and glibc ebuilds themselves (USE="build"):
			cleanables.extend(["/usr/share/gettext","/usr/lib/python2.2/test",\
				"/usr/lib/python2.2/encodings","/usr/lib/python2.2/email",\
				"/usr/lib/python2.2/lib-tk","/usr/share/zoneinfo"])
				
		for x in cleanables: 
			print "Cleaning chroot: "+x+"..."
			cmd("rm -rf "+destpath+x,"Couldn't clean "+x)

		# put /etc/hosts back into place
		cmd("mv -f "+self.settings["chroot_path"]+"/etc/hosts.bck "+self.settings["chroot_path"]+\
				"/etc/hosts", "Could not replace /etc/hosts")
		
		cmd("/bin/bash "+self.settings["sharedir"]+"/targets/"+self.settings["target"]+\
			"/"+self.settings["target"]+".sh clean","clean script failed.")
	
	def preclean(self):
		try:
			cmd("/bin/bash "+self.settings["sharedir"]+"/targets/"+self.settings["target"]+\
				"/"+self.settings["target"]+".sh preclean","preclean script failed.")
		
		except:
			self.unbind()
			raise CatalystError, "Build failed, could not execute preclean"

	def capture(self):
		"""capture target in a tarball"""
		mypath=self.settings["target_path"].split("/")
		# remove filename from path
		mypath=string.join(mypath[:-1],"/")
		
		# now make sure path exists
		if not os.path.exists(mypath):
			os.makedirs(mypath)

		# clean resume points since they are no longer needed
		if self.settings.has_key("AUTORESUME"):
			cmd("rm -f "+self.settings["chroot_path"]+"/tmp/.clst*",\
				"Couldn't remove resume points")
			
		print "Creating stage tarball..."
		
		cmd("tar cjf "+self.settings["target_path"]+" -C "+self.settings["stage_path"]+\
			" .","Couldn't create stage tarball")

	def run_local(self):
		try:
			cmd("/bin/bash "+self.settings["sharedir"]+"/targets/"+self.settings["target"]+\
				"/"+self.settings["target"]+".sh run","build script failed")

		except CatalystError:
			self.unbind()
			raise CatalystError,"Stage build aborting due to error."
	
	def setup_environment(self):
		# modify the current environment. This is an ugly hack that should be fixed. We need this
		# to use the os.system() call since we can't specify our own environ:
		for x in self.settings.keys():
			# "/" is replaced with "_", "-" is also replaced with "_"
			varname="clst_"+string.replace(x,"/","_")
			varname=string.replace(varname,"-","_")
			if type(self.settings[x])==types.StringType:
				# prefix to prevent namespace clashes:
				os.environ[varname]=self.settings[x]
			elif type(self.settings[x])==types.ListType:
				os.environ[varname]=string.join(self.settings[x])
	
	def run(self):
		
		for x in self.settings["action_sequence"]:
			print "Running action sequence: "+x
			if x == 'chroot_setup':
				try:
					self.chroot_setup()
				except:
					self.unbind()
					raise
			else:	
				apply(getattr(self,x))
