import os,stat,string,imp,types
from catalyst_support import *

class generic_target:

	def __init__(self,myspec,addlargs):
		addl_arg_parse(myspec,addlargs,self.required_values,self.valid_values)
		self.settings=myspec
		pass

class generic_stage_target(generic_target):

	def __init__(self,myspec,addlargs):
		
		self.required_values=["version_stamp","target","subarch","rel_type","rel_version","snapshot","source_subpath"]
		self.valid_values=self.required_values
		generic_target.__init__(self,addlargs,myspec)
		# map the mainarch we are running under to the mainarches we support for
		# building stages and LiveCDs. (for example, on amd64, we can build stages for
		# x86 or amd64.
		
		targetmap={ 	"x86" : ["x86"],
				"amd64" : ["x86","amd64"]
		}
		
		machinemap={ 	"i386" : "x86",
				"i486" : "x86",
				"i586" : "x86",
				"i686" : "x86",
				"x86_64" : "amd64"
		}
	
		mymachine=os.uname()[4]
		if not machinemap.has_key(mymachine):
			raise CatalystError, "Unknown machine type "+mymachine
		self.settings["hostarch"]=machinemap[mymachine]
		self.archmap={}
		self.subarchmap={}
		for x in targetmap[self.settings["hostarch"]]:
			fh=open("arch/"+x+".py")
			#this next line loads the plugin as a module and assigns it to archmap[x]
			self.archmap[x]=imp.load_module(x,fh,"arch/"+x+".py",(".py","r",imp.PY_SOURCE))
			#this next line registers all the subarches supported in the plugin
			self.archmap[x].register(self.subarchmap)
			fh.close()	
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
		self.settings["target_path"]=st+"/builds/"+self.settings["target_subpath"]+".tar.bz2"
		self.settings["source_path"]=st+"/builds/"+self.settings["source_subpath"]+".tar.bz2"
		self.settings["chroot_path"]=st+"/tmp/"+self.settings["target_subpath"]
		
		self.mounts=[ "/proc","/dev","/usr/portage/distfiles" ]
		self.mountmap={"/proc":"/proc", "/dev":"/dev", "/usr/portage/distfiles":self.settings["distdir"]}
		if self.settings.has_key("PKGCACHE"):
			self.settings["pkgcache_path"]=st+"/packages/"+self.settings["target_subpath"]
			self.mounts.append("/usr/portage/packages")
			self.mountmap["/usr/portage/packages"]=self.settings["pkgcache_path"]

		if self.settings.has_key("CCACHE"):
			self.mounts.append("/root/.ccache")
			self.mountmap["/root/.ccache"]="/root/.ccache"
			
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
		for x in self.mounts:
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
		myconf=open(self.settings["chroot_path"]+"/etc/make.conf","r")
		mylines=myconf.readlines()
		myconf.close()
		pos = 0
		while pos < len(mylines):
			if mylines[pos][:16]=="# catalyst start":
				while (pos < len(mylines)) and mylines[pos][:14]!="# catalyst end":
					del mylines[pos]
			elif (mylines[pos][:7]=="CFLAGS=") or (mylines[pos][:6]=="CHOST=") or (mylines[pos][:4]=="USE="):
				mylines[pos]="#"+mylines[pos]
			pos += 1
		pos = 0
		while (pos < len(mylines)) and mylines[pos][0]=="#":
			pos += 1
		cmds=["","# catalyst start","# These settings were added by the catalyst build script that automatically built this stage",
		'CFLAGS="'+self.settings["CFLAGS"]+'"',
		'CHOST="'+self.settings["CHOST"]+'"']
		if self.settings.has_key("HOSTUSE"):
			cmds.append('USE="'+self.settings["HOSTUSE"]+'"')
		else:
			cmds.append('USE=""')
		if self.settings.has_key("CXXFLAGS"):
			cmds.append('CXXFLAGS="'+self.settings["CXXFLAGS"]+'"')
		else:
			cmds.append('CXXFLAGS="$CFLAGS"')
		cmds.append("# catalyst end")

		for x in cmds:
			mylines.insert(pos,x+"\n")
			pos += 1

		myconf=open(self.settings["chroot_path"]+"/etc/make.conf","w")
		myconf.write(string.join(mylines))	
		myconf.close()
		
	def clean(self):
		destpath=self.settings["chroot_path"]
		cleanables=["/etc/resolv.conf","/usr/portage","/var/tmp/*","/tmp/*","/root/*","/root/.ccache"]
		if self.settings["target"]=="stage1":
			destpath+="/tmp/stage1root"
			#this next stuff can eventually be integrated into the python and glibc ebuilds themselves (USE="build"):
			cleanables.extend(["/usr/share/gettext","/usr/lib/python2.2/test","/usr/lib/python2.2/encodings","/usr/lib/python2.2/email","/usr/lib/python2.2/lib-tk","/usr/share/zoneinfo"])
		for x in cleanables: 
			cmd("rm -rf "+destpath+x,"Couldn't clean "+x)
		cmd(self.settings["storedir"]+"/targets/"+self.settings["target"]+"/"+self.settings["target"]+".sh clean","clean script failed.")
	
	def preclean(self):
		try:
			cmd(self.settings["storedir"]+"/targets/"+self.settings["target"]+"/"+self.settings["target"]+".sh preclean","preclean script failed.")
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
			if type(self.settings[x])==types.StringType:
				#prefix to prevent namespace clashes:
				os.environ["clst_"+x]=self.settings[x]
			elif type(self.settings[x])==types.ListType:
				os.environ["clst_"+x]=string.join(self.settings[x])
		try:
			cmd(self.settings["storedir"]+"/targets/"+self.settings["target"]+"/"+self.settings["target"]+".sh run","build script failed")
		finally:
			#pre-clean is for stuff that needs to run with bind-mounts still active
			self.preclean()
			self.unbind()
		#clean is for removing things after bind-mounts are unmounted (general file removal and cleanup)
		self.clean()
		self.capture()
			
class snapshot_target(generic_target):
	def __init__(self,myspec,addlargs):
		self.valid_values=["version_stamp","target"]
		self.required_values=self.valid_values
		generic_target.__init__(self,myspec,addlargs)
		
		self.settings=myspec
		if not self.settings.has_key("version_stamp"):
			raise CatalystError, "Required value \"version_stamp\" not specified."
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
		mytmp=self.settings["tmp_path"]+"/"+self.settings["target_subpath"]
		print "Cleaning up temporary snapshot directory..."
		#Be a good citizen and clean up after ourselves
		cmd("rm -rf "+mytmp,"Snapshot cleanup failure")
			
class stage1_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		generic_stage_target.__init__(self,spec,addlargs)

class stage2_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		generic_stage_target.__init__(self,spec,addlargs)

class stage3_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		generic_stage_target.__init__(self,spec,addlargs)

class grp_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		generic_stage_target.__init__(self,spec,addlargs)

class livecd_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		generic_target.__init__(self,spec,addlargs)

def register(foo):
	foo.update({"stage1":stage1_target,"stage2":stage2_target,"stage3":stage3_target,
	"grp":grp_target,"livecd":livecd_target,"snapshot":snapshot_target})
	return foo
	
