# Distributed under the GNU General Public License version 2
# Copyright 2003-2004 Gentoo Technologies, Inc.

import os,stat,string,imp,types
from catalyst_support import *

class generic_target:

	def __init__(self,myspec,addlargs):
		addl_arg_parse(myspec,addlargs,self.required_values,self.valid_values)
		self.settings=myspec
		pass

class generic_stage_target(generic_target):

	def __init__(self,myspec,addlargs):
		
		self.required_values.extend(["version_stamp","target","subarch","rel_type","rel_version","snapshot","source_subpath"])
		self.valid_values.extend(["version_stamp","target","subarch","rel_type","rel_version","snapshot","source_subpath"])
		generic_target.__init__(self,addlargs,myspec)
		# map the mainarch we are running under to the mainarches we support for
		# building stages and LiveCDs. (for example, on amd64, we can build stages for
		# x86 or amd64.
		
		targetmap={ 	"x86" : ["x86"],
				"amd64" : ["x86","amd64"],
				"sparc64" : ["sparc64"],
				"ia64" : ["ia64"],
				"alpha" : ["alpha"],
				"sparc" : ["sparc"],
				"ppc" : ["ppc"],
				"hppa" : ["hppa"]
		}
		
		machinemap={ 	"i386" : "x86",
				"i486" : "x86",
				"i586" : "x86",
				"i686" : "x86",
				"x86_64" : "amd64",
				"sparc64" : "sparc64",
				"ia64" : "ia64",
				"alpha" : "alpha",
				"sparc" : "sparc",
				"ppc" : "ppc",
				"parisc" : "hppa",
				"parisc64" : "hppa"
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
				#this next line loads the plugin as a module and assigns it to archmap[x]
				self.archmap[x]=imp.load_module(x,fh,"arch/"+x+".py",(".py","r",imp.PY_SOURCE))
				#this next line registers all the subarches supported in the plugin
				self.archmap[x].register(self.subarchmap)
				fh.close()	
			except IOError:
				msg("Can't find "+x+".py plugin in "+self.settings["sharedir"]+"/arch/")
		#call arch constructor, pass our settings
		self.arch=self.subarchmap[self.settings["subarch"]](self.settings)
		#self.settings["mainarch"] should now be set by our arch constructor, so we print
		#a nice informational message:
		if self.settings["mainarch"]==self.settings["hostarch"]:
			print "Building natively for",self.settings["hostarch"]
		else:
			print "Building on",self.settings["hostarch"],"for alternate machine type",self.settings["mainarch"]
			
		self.settings["target_profile"]=self.settings["rel_type"]+"-"+self.settings["mainarch"]+"-"+self.settings["rel_version"]
		self.settings["target_subpath"]=self.settings["target_profile"]+"/"+self.settings["target"]+"-"+self.settings["subarch"]+"-"+self.settings["version_stamp"]
		st=self.settings["storedir"]
		self.settings["snapshot_path"]=st+"/snapshots/portage-"+self.settings["snapshot"]+".tar.bz2"
		if self.settings["target"] in ["grp","tinderbox"]:
			#grp creates a directory of packages and sources rather than a compressed tarball
			self.settings["target_path"]=st+"/builds/"+self.settings["target_subpath"]
			self.settings["source_path"]=st+"/builds/"+self.settings["source_subpath"]+".tar.bz2"
		elif self.settings["target"] == "livecd-stage2":
			#we have a main directory and a tarball in this case
			os.makedirs(st+"/builds/"+self.settings["target_subpath"])
			self.settings["target_path"]=st+"/builds/"+self.settings["target_subpath"]+"/"+self.settings["target_subpath"]+".tar.bz2"
			self.settings["source_path"]=st+"/builds/"+self.settings["source_subpath"]+".tar.bz2"
		elif self.settings["target"]=="livecd-stage3":
			# the loop-prep/ dir is for unpacking the chroot image, and will be used to prep it.
			self.settings["target_path"]=st+"/builds/"+self.settings["target_subpath"]+"/loop-prep"
			self.settings["cdroot_path"]=st+"/builds/"+self.settings["target_subpath"]+"/cdroot"
			os.makedirs(self.settings["target_path"])
			os.makedirs(self.settings["cdroot_path"])
			self.settings["source_path"]=st+"/builds/"+self.settings["source_subpath"]+"/"+self.settings["source_subpath"]+".tar.bz2"
		else:
			self.settings["target_path"]=st+"/builds/"+self.settings["target_subpath"]+".tar.bz2"
			self.settings["source_path"]=st+"/builds/"+self.settings["source_subpath"]+".tar.bz2"
		self.settings["chroot_path"]=st+"/tmp/"+self.settings["target_subpath"]
		
		self.mounts=[ "/proc","/dev","/dev/pts","/usr/portage/distfiles" ]
		self.mountmap={"/proc":"/proc", "/dev":"/dev", "/dev/pts":"/dev/pts","/usr/portage/distfiles":self.settings["distdir"]}
		if self.settings.has_key("PKGCACHE"):
			self.settings["pkgcache_path"]=st+"/packages/"+self.settings["target_subpath"]
			self.mounts.append("/usr/portage/packages")
			self.mountmap["/usr/portage/packages"]=self.settings["pkgcache_path"]

		if self.settings.has_key("CCACHE"):
			self.mounts.append("/root/.ccache")
			self.mountmap["/root/.ccache"]="/root/.ccache"
		if self.settings["target"]=="grp":
			self.mounts.append("/tmp/grp")
			self.mountmap["/tmp/grp"]=self.settings["target_path"]
		if self.settings["target"]=="livecd-stage2":
			self.mounts.append("/tmp/binaries")
			self.mountmap["/tmp/binaries"]=st+"/builds/"+self.settings["target_subpath"]+"/binaries"
			
	def mount_safety_check(self):
		mypath=self.settings["chroot_path"]
		#check and verify that none of our paths in mypath are mounted. We don't want to clean up with things still
		#mounted, and this allows us to check. returns 1 on ok, 0 on "something is still mounted" case.
		if not os.path.exists(mypath):
			return 
		for x in self.mounts:
			if not os.path.exists(mypath+x):
				continue
			if ismount(mypath+x):
				#something is still mounted
				try:
					print x+" is still mounted; performing auto-bind-umount..."
					#try to umount stuff ourselves
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
		cmd("rm -rf "+self.settings["chroot_path"],"Could not remove existing directory: "+self.settings["chroot_path"])
		os.makedirs(self.settings["chroot_path"])
		if self.settings.has_key("PKGCACHE"):	
			if not os.path.exists(self.settings["pkgcache_path"]):
				os.makedirs(self.settings["pkgcache_path"])
		
	def unpack_and_bind(self):
		print "Unpacking stage tarball..."
		cmd("tar xjpf "+self.settings["source_path"]+" -C "+self.settings["chroot_path"],"Error unpacking tarball")
		print "Unpacking portage tree snapshot..."
		cmd("tar xjpf "+self.settings["snapshot_path"]+" -C "+self.settings["chroot_path"]+"/usr","Error unpacking snapshot")
		for x in self.mounts: 
			if not os.path.exists(self.settings["chroot_path"]+x):
				os.makedirs(self.settings["chroot_path"]+x)
			if not os.path.exists(self.mountmap[x]):
				os.makedirs(self.mountmap[x])
			src=self.mountmap[x]
			retval=os.system("mount --bind "+src+" "+self.settings["chroot_path"]+x)
			if retval!=0:
				self.unbind()
				raise CatalystError,"Couldn't bind mount "+src
		print "Configuring profile link..."
		cmd("rm -f "+self.settings["chroot_path"]+"/etc/make.profile","Error zapping profile link")
		cmd("ln -sf ../usr/portage/profiles/"+self.settings["target_profile"]+" "+self.settings["chroot_path"]+"/etc/make.profile","Error creating profile link")

	def unbind(self):
		ouch=0
		mypath=self.settings["chroot_path"]
		myrevmounts=self.mounts[:]
		myrevmounts.reverse()
		#unmount in reverse order for nested bind-mounts
		for x in myrevmounts:
			if not os.path.exists(mypath+x):
				continue
			if not ismount(mypath+x):
				#it's not mounted, continue
				continue
			retval=os.system("umount "+mypath+x)
			if retval!=0:
				ouch=1
				warn("Couldn't umount bind mount: "+mypath+x)
				#keep trying to umount the others, to minimize damage if developer makes a mistake
		if ouch:
			#if any bind mounts really failed, then we need to raise this to potentially prevent
			#an upcoming bash stage cleanup script from wiping our bind mounts.
			raise CatalystError,"Couldn't umount one or more bind-mounts; aborting for safety."

	def chroot_setup(self):
		cmd("cp /etc/resolv.conf "+self.settings["chroot_path"]+"/etc","Could not copy resolv.conf into place.")
		cmd("rm -f "+self.settings["chroot_path"]+"/etc/make.conf")

		myf=open(self.settings["chroot_path"]+"/etc/make.conf","w")
		myf.write("# These settings were set by the catalyst build script that automatically built this stage\n")
		myf.write('CFLAGS="'+self.settings["CFLAGS"]+'"\n')
		myf.write('CHOST="'+self.settings["CHOST"]+'"\n')
		myusevars=[]
		if self.settings.has_key("HOSTUSE"):
			myusevars.extend(self.settings["HOSTUSE"])
		if self.settings["target"]=="grp":
			myusevars.append("bindist")
			myusevars.extend(self.settings["grp/use"])
		elif self.settings["target"]=="tinderbox":
			myusevars.extend(self.settings["tinderbox/use"])
		elif self.settings["target"]=="livecd-stage1":
			myusevars.extend(self.settings["livecd-stage1/use"])
		myf.write('USE="'+string.join(myusevars)+'"\n')
		if self.settings.has_key("CXXFLAGS"):
			myf.write('CXXFLAGS="'+self.settings["CXXFLAGS"]+'"\n')
		else:
			myf.write('CXXFLAGS="$CFLAGS"\n')
		myf.close()
		
	def clean(self):
		destpath=self.settings["chroot_path"]
		cleanables=["/etc/resolv.conf","/usr/portage","/var/tmp/*","/tmp/*","/root/*","/root/.ccache"]
		if self.settings["target"]=="stage1":
			destpath+="/tmp/stage1root"
			#this next stuff can eventually be integrated into the python and glibc ebuilds themselves (USE="build"):
			cleanables.extend(["/usr/share/gettext","/usr/lib/python2.2/test","/usr/lib/python2.2/encodings","/usr/lib/python2.2/email","/usr/lib/python2.2/lib-tk","/usr/share/zoneinfo"])
		if self.settings["target"]=="livecd-stage3":
			if self.settings.has_key("livecd-stage3/clean"):
				if type(self.settings["livecd-stage3/clean"])==types.StringType:
					cleanables.append(self.settings["livecd-stage3/clean"])
				else:
					#a list of directories to clean
					cleanables.extend(self.settings["livecd-stage3/clean"])
		for x in cleanables: 
			print "Cleaning chroot: "+x+"..."
			cmd("rm -rf "+destpath+x,"Couldn't clean "+x)
		cmd(self.settings["sharedir"]+"/targets/"+self.settings["target"]+"/"+self.settings["target"]+".sh clean","clean script failed.")
	
	def preclean(self):
		try:
			cmd(self.settings["sharedir"]+"/targets/"+self.settings["target"]+"/"+self.settings["target"]+".sh preclean","preclean script failed.")
		except:
			self.unbind()
			raise

	def capture(self):
		"""capture target in a tarball"""
		mypath=self.settings["target_path"].split("/")
		#remove filename from path
		mypath=string.join(mypath[:-1],"/")
		#now make sure path exists
		if not os.path.exists(mypath):
			os.makedirs(mypath)
		print "Creating stage tarball..."
		if self.settings["target"]=="stage1":
			cmd("tar cjf "+self.settings["target_path"]+" -C "+self.settings["chroot_path"]+"/tmp/stage1root .","Couldn't create stage tarball")
		else:
			cmd("tar cjf "+self.settings["target_path"]+" -C "+self.settings["chroot_path"]+" .","Couldn't create stage tarball")

	def run_local(self):
		try:
			cmd(self.settings["sharedir"]+"/targets/"+self.settings["target"]+"/"+self.settings["target"]+".sh run","build script failed")
		except CatalystError:
			self.unbind()
			raise CatalystError,"Stage build aborting due to error."
			pass

	def run(self):
		self.dir_setup()
		self.unpack_and_bind()
		try:
			self.chroot_setup()
		except:
			self.unbind()
			raise
		#modify the current environment. This is an ugly hack that should be fixed. We need this
		#to use the os.system() call since we can't specify our own environ:
		for x in self.settings.keys():
			varname="clst_"+x
			#"/" is replaced with "_", "-" is also replaced with "_"
			string.replace(varname,"/-","__")
			if type(self.settings[x])==types.StringType:
				#prefix to prevent namespace clashes:
				os.environ[varname]=self.settings[x]
			elif type(self.settings[x])==types.ListType:
				os.environ[varname]=string.join(self.settings[x])
			
		self.run_local()
		if self.settings["target"] in ["stage1","stage2","stage3","livecd-stage3"]:
			self.preclean()
		self.unbind()
		if self.settings["target"] in ["stage1","stage2","stage3"]:
			#clean is for removing things after bind-mounts are unmounted (general file removal and cleanup)
			self.clean()
		if self.settings["target"] in ["stage1","stage2","stage3","livecd-stage1","livecd-stage2"]:
			self.capture()
			
class snapshot_target(generic_target):
	def __init__(self,myspec,addlargs):
		self.required_values=["version_stamp","target"]
		self.valid_values=["version_stamp","target"]
		generic_target.__init__(self,myspec,addlargs)
		self.settings=myspec
		self.settings["target_subpath"]="portage-"+self.settings["version_stamp"]
		st=self.settings["storedir"]
		self.settings["snapshot_path"]=st+"/snapshots/"+self.settings["target_subpath"]+".tar.bz2"
		self.settings["tmp_path"]=st+"/tmp/"+self.settings["target_subpath"]

	def setup(self):
		x=self.settings["storedir"]+"/snapshots"
		if not os.path.exists(x):
			os.makedirs(x)

	def run(self):
		self.setup()
		print "Creating Portage tree snapshot "+self.settings["version_stamp"]+" from "+self.settings["portdir"]+"..."
		mytmp=self.settings["tmp_path"]
		if os.path.exists(mytmp):
			cmd("rm -rf "+mytmp,"Could not remove existing directory: "+mytmp)
		os.makedirs(mytmp)
		cmd("rsync -a --exclude /packages/ --exclude /distfiles/ --exclude CVS/ "+self.settings["portdir"]+"/ "+mytmp+"/portage/","Snapshot failure")
		print "Compressing Portage snapshot tarball..."
		cmd("tar cjf "+self.settings["snapshot_path"]+" -C "+mytmp+" portage","Snapshot creation failure")
		self.cleanup()

	def cleanup(self):
		print "Cleaning up temporary snapshot directory..."
		#Be a good citizen and clean up after ourselves
		cmd("rm -rf "+self.settings["tmp_path"],"Snapshot cleanup failure")
			
class stage1_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=[]
		self.valid_values=[]
		generic_stage_target.__init__(self,spec,addlargs)

class stage2_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=[]
		self.valid_values=[]
		generic_stage_target.__init__(self,spec,addlargs)

class stage3_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=[]
		self.valid_values=[]
		generic_stage_target.__init__(self,spec,addlargs)

class grp_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=["version_stamp","target","subarch","rel_type","rel_version","snapshot","source_subpath"]
		self.valid_values=self.required_values[:]
		if not addlargs.has_key("grp"):
			raise CatalystError,"Required value \"grp\" not specified in spec."
		self.required_values.extend(["grp","grp/use"])
		for x in addlargs["grp"]:
			self.required_values.append("grp/"+x+"/packages")
			self.required_values.append("grp/"+x+"/type")
		generic_stage_target.__init__(self,spec,addlargs)

	def run_local(self):
		for pkgset in self.settings["grp"]:
			#example call: "grp.sh run pkgset cd1 xmms vim sys-apps/gleep"
			try:
				cmd(self.settings["sharedir"]+"/targets/grp/grp.sh run "+self.settings["grp/"+pkgset+"/type"]+" "+pkgset+" "+string.join(self.settings["grp/"+pkgset+"/packages"]))
			except CatalystError:
				self.unbind()
				raise CatalystError,"GRP build aborting due to error."

class tinderbox_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=["tinderbox/packages","tinderbox/use"]
		self.valid_values=self.required_values[:]
		generic_stage_target.__init__(self,spec,addlargs)

	def run_local(self):
		#tinderbox
		#example call: "grp.sh run xmms vim sys-apps/gleep"
		try:
			cmd(self.settings["sharedir"]+"/targets/tinderbox/tinderbox.sh run "+string.join(self.settings["tinderbox/packages"]))
		except CatalystError:
			self.unbind()
			raise CatalystError,"Tinderbox aborting due to error."

class livecd_stage1_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=["livecd-stage1/packages","livecd-stage1/use"]
		self.valid_values=self.required_values[:]
		generic_stage_target.__init__(self,spec,addlargs)

	def run_local(self):
		try:
			cmd(self.settings["sharedir"]+"/targets/livecd-stage1/livecd-stage1.sh run "+string.join(self.settings["livecd-stage1/packages"]))
		except CatalystError:
			self.unbind()
			raise CatalystError,"GRP build aborting due to error."

class livecd_stage2_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=["boot/kernel"]
		if not addlargs.has_key("boot/kernel"):
			raise CatalystError, "Required value boot/kernel not specified."
		if type(addlargs["boot/kernel"]) == types.StringType:
			loopy=[addlargs["boot/kernel"]]
		else:
			loopy=addlargs["boot/kernel"]
		for x in loopy:
			self.required_values.append("boot/kernel/"+x+"/sources")
			self.required_values.append("boot/kernel/"+x+"/config")
		self.valid_values=self.required_values[:]
		generic_stage_target.__init__(self,spec,addlargs)
	
	def run_local(self):
		mynames=self.settings["boot/kernel"]
		if type(mynames)==types.StringType:
			mynames=[mynames]
		args=`len(mynames)`
		for x in mynames:
			args=args+" "+x+" "+self.settings["boot/kernel/"+x+"/sources"]
			if not os.path.exists(self.settings["boot/kernel/"+x+"/config"]):
				raise CatalystError, "Can't find kernel config: "+self.settings["boot/kernel/"+x+"/config"]
			retval=os.system("cp "+self.settings["boot/kernel/"+x+"/config"]+" "+self.settings["chroot_path"]+"/var/tmp/"+x+".config")
			if retval!=0:
				raise CatalystError, "Couldn't copy kernel config: "+self.settings["boot/kernel/"+x+"/config"]
		try:
			cmd(self.settings["sharedir"]+"/targets/livecd-stage2/livecd-stage2.sh run "+args)
		except CatalystError:
			self.unbind()
			raise CatalystError,"GRP build aborting due to error."

class livecd_stage3_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=["boot/kernel","livecd-stage3/runscript"]
		self.valid_values=self.required_values[:]
		self.valid_values.append("livecd-stage3/cdtar","livecd-stage3/clean")
		generic_stage_target.__init__(self,spec,addlargs)

def register(foo):
	foo.update({"stage1":stage1_target,"stage2":stage2_target,"stage3":stage3_target,
	"grp":grp_target,"livecd-stage1":livecd_stage1_target,
	"livecd-stage2":livecd_stage2_target,"livecd-stage3":livecd_stage3_target,
	"snapshot":snapshot_target,"tinderbox":tinderbox_target})
	return foo
	
