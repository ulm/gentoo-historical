import os,stat,string,imp
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

		#ensure we have all required user-supplied settings before proceeding
		for x in requiredspec:
			if not self.settings.has_key(x):
				raise CatalystError, "Required value \""+x+"\" not specified."
		
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
		print "Host architecture:",self.settings["hostarch"]
		print "Supported architectures for targets:",string.join(targetmap[self.settings["hostarch"]])
		print "Loading all valid plugins for this machine:",
		self.archmap={}
		self.subarchmap={}
		for x in targetmap[self.settings["hostarch"]]:
			fh=open("arch/"+x+".py")
			#this next line loads the plugin as a module and assigns it to archmap[x]
			self.archmap[x]=imp.load_module(x,fh,"arch/"+x+".py",(".py","r",imp.PY_SOURCE))
			#this next line registers all the subarches supported in the plugin
			self.archmap[x].register(self.subarchmap)
			fh.close()	
		print x,
		print
		print "Available subarches:",string.join(self.subarchmap.keys())
		#call arch constructor, pass our settings
		self.arch=self.subarchmap[self.settings["subarch"]](self.settings)
		self.settings["target_subpath"]=self.settings["rel_type"]+"-"+self.settings["mainarch"]+"-"+self.settings["rel_version"]
		self.settings["target_subpath"]+="/"+self.settings["target"]+"-"+self.settings["subarch"]+"-"+self.settings["version_stamp"]
		st=self.settings["storedir"]
		self.settings["snapshot_path"]=st+"/snapshots/portage-"+self.settings["snapshot"]+".tar.bz2"
		self.settings["target_path"]=st+"/builds/"+self.settings["target_subpath"]+".tar.bz2"
		self.settings["source_path"]=st+"/builds/"+self.settings["source_subpath"]+".tar.bz2"
		self.settings["chroot_path"]=st+"/tmp/"+self.settings["target_subpath"]
		self.settings["pkgcache_path"]=st+"/packages/"+self.settings["target_subpath"]

	def mount_safety_check(self):
		mypath=self.settings["chroot_path"]
		#check and verify that none of our paths in mypath are mounted. We don't want to clean up with things still
		#mounted, and this allows us to check. returns 1 on ok, 0 on "something is still mounted" case.
		paths=["/usr/portage/packages","/usr/portage/distfiles", "/var/tmp/distfiles", "/proc", "/root/.ccache", "/dev"]
		if not os.path.exists(mypath):
			return 
		mypstat=os.stat(mypath)[stat.ST_DEV]
		for x in paths:
			if not os.path.exists(mypath+x):
				continue
			teststat=os.stat(mypath+x)[stat.ST_DEV]
			if teststat!=mypstat:
				#something is still mounted
				raise CatalystError, x+" is still mounted; aborting."
		return 1
		
	def dir_setup(self):
		self.mount_safety_check()
		retval=os.system("rm -rf "+self.settings["chroot_path"])
		if retval != 0:
			raise CatalystError,"Could not remove existing directory: "+self.settings["chroot_path"]
		os.makedirs(self.settings["chroot_path"])
		if not os.path.exists(self.settings["pkgcache_path"]):
			os.makedirs(self.settings["pkgcache_path"])
		
	def unpack_and_bind(self):
		retval=os.system("tar xjpf "+self.settings["source_path"]+" -C "+self.settings["chroot_path"])
		if retval!=0:
			raise CatalystError,"Error unpacking tarball"
		retval=os.system("tar xjpf "+self.settings["snapshot_path"]+" -C "+self.settings["chroot_path"]+"/usr")
		if retval!=0:
			raise CatalystError,"Error unpacking snapshot"
		for x in [[self.settings["distdir"],"/usr/portage/distfiles"],
				["/proc","/proc"],["/dev","/dev"]]:
			if not os.path.exists(self.settings["chroot_path"]+x[1]):
				os.makedirs(self.settings["chroot_path"]+x[1])
			
			retval=os.system("mount --bind "+x[0]+" "+self.settings["chroot_path"]+x[1])
			if retval!=0:
				self.unbind()
				raise CatalystError,"Couldn't bind mount "+x[0]

	def unbind(self):
		for x in ["/usr/portage/distfiles","/proc","/dev"]:
			retval=os.system("umount "+self.settings["chroot_path"]+x)
			if retval!=0:
				warning("Couldn't umount bind mount: "+self.settings["chroot_path"]+x)

	def setup(self):
		#setup will leave everything in unbound state if there is a failure
		self.dir_setup()
		self.unpack_and_bind()

	def run(self):
		self.setup()
		try:
			pass
		finally:
			#always unbind
			self.unbind()
	
class snapshot_target(generic_target):
	def __init__(self,myspec,addlargs):
		self.valid_values=["version_stamp","target"]
		self.required_values=self.valid_values
		generic_target.__init__(myspec,addlargs)
		
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
			retval=os.system("rm -rf "+mytmp)
			if retval != 0:
				raise CatalystError, "Could not remove existing directory: "+mytmp
		os.makedirs(mytmp)
		retval=os.system("rsync -a --exclude /packages/ --exclude /distfiles/ --exclude CVS/ "+self.settings["portdir"]+"/ "+mytmp+"/portage/")
		if retval != 0:
			raise CatalystError,"Snapshot failure"
		print "Compressing Portage snapshot tarball..."
		retval=os.system("tar cjf "+self.settings["snapshot_path"]+" -C "+mytmp+" portage")
		if retval != 0:
			raise CatalystError,"Snapshot creation failure"
		self.cleanup()

	def cleanup(self):
		mytmp=self.settings["tmp_path"]+"/"+self.settings["target_subpath"]
		print "Cleaning up temporary snapshot directory..."
		#Be a good citizen and clean up after ourselves
		retval=os.system("rm -rf "+mytmp)
		if retval != 0:
			raise CatalystError,"Snapshot cleanup failure"
			
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
	
