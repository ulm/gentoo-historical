#!/usr/bin/python
# Copyright 2003 Gentoo Technologies, Inc.; http://www.gentoo.org
# Released under the GNU General Public License version 2

import sys,os,string,stat

subarches=["amd64", "hppa", "hppa1.1", "hppa2.0", "x86", "i386", "i486", "i586", "i686",
"athlon", "athlon-xp", "athlon-mp", "pentium-mmx", "pentium3", "pentium4", "ppc", "g3",
"g4", "sparc", "sparc64", "mips", "alpha", "ev4", "ev5", "ev56", "pca56", "ev6", "ev67" ]

#this target stuff is not completed, but I've added it as a general template.
"""
setting name			bash equivalent		defined how?
====================================================================
pkgdir				PKGDIR			default (package cache dir)
distdir				DISTDIR			default (/usr/portage/distfiles)
subarch				SUBARCH			user (from spec)
rel_version			REL_VERSION		user (from spec) (was MAINVERSION)
rel_type			REL_TYPE		user (from spec) (was BUILDTYPE)
version_stamp			VERSION_STAMP		user (from spec)
snapshot			SNAPSHOT		user (from spec)
source_tarball			SOURCE_TARBALL		user (from spec)
target				TARGET			user (from spec)
cflags				CFLAGS			auto
hostuse				HOSTUSE			auto
chost				CHOST			auto
mainarch			MAINARCH		auto
"""
class generic_target:
	def __init__(self,myset):
		self.settings=myset
		self.envmap={"CFLAGS":"cflags" }
	def path(self):
		#temp file paths: 
		#/var/tmp/catalyst/default-x86-1.4/stage1-pentium4-20030911/work
		#/var/tmp/catalyst/default-x86-1.4/stage1-pentium4-20030911/packages (if there is a package cache)
		
		#final paths:
		#snapshots/portage-20030911.tar.bz2
		#builds/default-x86-1.4/stage1-pentium4-20030911.tar.bz2
		#builds/default-x86-1.4/stage2-pentium4-20030911.tar.bz2
		#builds/default-x86-1.4/stage3-pentium4-20030911.tar.bz2
		#builds/default-x86-1.4/grp-pentium4-20030911/cd1/packages/All
		#builds/default-x86-1.4/grp-pentium4-20030911/cd2/packages/All
		#builds/default-x86-1.4/livecd-20030911.tar.bz2
		#builds/buildtype-mainarch-mainversion/buildtype-subarch-version_stamp
		#now where to put the work files.
		return "stages/stage1-"+self.settings["subarch"]+"-"+self.settings["buildno"]+".tar.bz2"
	def read_spec_file(self,myfile):
		#settings from this file:
		#pkgdir, distdir, subarch, mainversion, version_stamp, snapshot, source tarball
		#default default  user     user         user           user      user
		#read in a spec file, grab settings we need.
		pass
	def execute_script(self,myscript,myargs):
		#export env vars here
		return os.system(myscript+" "+string.join(myargs," "))
		pass
	def export_variables(self):
		#export environment variables
		#export:
		# CFLAGS, HOSTUSE, CHOST, MAINARCH, MAINVERSION, BUILDTYPE, MAKEOPTS, BASEDIR, CHROOTDIR, FEATURES
		# auto    auto     auto   auto      spec         spec auto default  auto       default	
	def build(self):
		#do the actual stage1 building
		return execute_script("targets/stage1/build.sh")
	def unpack(self):
		#unpack stages
	def mount_all(self):
		#mount mount points; let's handle this from python
	def umount_all(self):
		#umount mount points; let's handle this from python
	def mount_safety_check(self,mypath):
		#check and verify that none of our paths in mypath are mounted. We don't want to clean up with things still
		#mounted, and this allows us to check. returns 1 on ok, 0 on "something is still mounted" case.
		paths=["usr/portage/packages","/usr/portage/distfiles", "/var/tmp/distfiles", "/proc", "/root/.ccache", "/dev"]
		if not os.path.exists(mypath):
			return 1 
		mypstat=os.stat(mypath)[ST_DEV]
		for x in paths:
			if not os.path.exists(x):
				continue
			teststat=os.stat(x)[ST_DEV]
			if teststat!=mypstat:
				#something is still mounted
				return 0
		return 1
	def prep(self):
		#prepare stage for packing up
	def clean(self):
		#clean up temporary build directory
	def pack(self):
		#tar up anything like a stage and put in right place
	def run(self):
		self.mount_safety_check()
		self.unpack()
		self.setup()
		self.mount_all()
		retval=self.build() #check for failure
		self.umount_all()
		self.mount_safety_check()
		self.prep()
		self.pack()
		self.clean()

class stage2(generic_target):
	#subclass of generic_target
	def path(self):
		return "stages/stage2-"+self.settings["subarch"]+"-"+self.settings["buildno"]+".tar.bz2"

class stage3(generic_target):
	def path(self):
		return "stages/stage3-"+self.settings["subarch"]+"-"+self.settings["buildno"]+".tar.bz2"

class grp(generic_target):
	def path(self):
		return "stages/stage3-"+self.settings["subarch"]+"-"+self.settings["buildno"]+".tar.bz2"

class livecd(target):
	def path(self):
		return "stages/stage3-"+self.settings["subarch"]+"-"+self.settings["buildno"]+".tar.bz2"

class settings:
	def __init__(self):
		self.vals={}
		self.debug=0
	def __getitem__(self,myitem):
		return self.vals[myitem]
	def __setitem__(self,myitem,myval):
		if self.debug:
			sys.stderr.write("setting "+myitem+" to "+repr(myval)+"\n")
		self.vals[myitem]=myval
	def dump(self):
		for x in self.vals.keys():
			print x+":", self.vals[x]

def verify_os(myset):
	if sys.platform=="linux2":
		myset["os_userland"]="GNU"
	else:
		raise OSError, "Platform "+sys.platform+" not recognized."

def job_defaults(mainarch):
	return "to be completed"

def verify_subarch(myset,subarch):
	global subarches
	if subarch not in subarches:
		raise ValueError, "Sub-architecture "+mysubarch+" not recognized."
	myset["subarch"]=subarch

	if subarch == "athlon-mp":
		subarch="athlon-xp"

	results=None

	if subarch == "ia64":
		results=["ia64","-O2","ia64-unknown-linux-gnu",[]]
	elif subarch == "amd64":
		results=["amd64","-O2 -fPIC","x86_64-pc-linux-gnu",[]]
	elif subarch in ["hppa","hppa1.1","hppa2.0"]:
		results=["hppa","-O2","hppa-unknown-linux-gnu",[]]
		if subarch == "hppa2.0":
			results[1] += " -march=2.0"
		else:
			results[1] += " -march=1.1"
	elif subarch in ["x86","i386","i486","i586","i686","athlon","athlon-xp","athlon-mp","pentium-mmx","pentium3","pentium4"]:
		#With recent gcc compilers (gcc-3.1+,) gcc produces generally slower code with -O3 as compared to -O2
		#So we are tweaking things here. 
		uf=[]
		if subarch == "x86":
			cf="-O2 -mcpu=i686 -fomit-frame-pointer"
		elif subarch == "athlon-xp":
			#we've intentionally lowered optimizations here to address compile bugs. It is very likely safe to
			#go up to -O3 without any additional -f goodies (like unroll-loops and prefetch-loop-arrays) tacked
			#on. Note that we don't add any extra -f goodies if we are athlon* below.
			cf="-O2 -march=athlon-xp -fomit-frame-pointer"
		else:
			cf="-O2 -march="+subarch+" -fomit-frame-pointer"
		if subarch[0:6] == "athlon":
			uf.append("3dnow")
		if subarch in [ "athlon","athlon-xp","athlon-mp","pentium-mmx","pentium3","pentium4" ]:
			uf.append("mmx")
		if subarch in [ "pentium3", "pentium4" ]:
			uf.append("sse")
		if subarch in ["pentium3", "pentium4", "athlon", "athlon-xp", "athlon-mp", "i686"]:
			cf += " -finline-functions -finline-limit=800"
		if subarch in ["i386","i486","i586"]:
			results=["x86",cf,subarch+"-pc-linux-gnu",[]]
		elif subarch == "x86":
			results=["x86",cf,"i486-pc-linux-gnu",[]]
		elif subarch == "pentium-mmx":
			results=["x86",cf,"i586-pc-linux-gnu",uf]
		else:
			results=["x86",cf,"i686-pc-linux-gnu",uf]
		
	elif subarch in ["ppc","g3","g4"]:
		if subarch == "ppc":
			results=["ppc","-O2 -fsigned-char",[]]
		elif subarch == "g3":
			results=["ppc","-O2 -mcpu=750 -mpowerpc-gfxopt -fsigned-char"]
		elif subarch == "g4":
			results=["ppc","-O2 -mcpu=7400 -maltivec -mabi=altivec -mpowerpc-gfxopt -fsigned-char"]
		results.extend(["powerpc-unknown-linux-gnu",[]])
	elif subarch in ["sparc","sparc64"]:
		if subarch == "sparc":
			results=["sparc","-O2"]
		else:
			results=["sparc64","-O3 -mcpu=ultrasparc -mtune=ultrasparc"]
		results.extend(["sparc-unknown-linux-gnu",[]])
	elif subarch == "mips":
		results=["mips","-O2","mips-unknown-linux-gnu",[]]
	elif subarch in ["alpha","ev4","ev5","ev56","pca56","ev6","ev67"]:
		if subarch == "alpha":
			results=["alpha","-O3 -mcpu=ev5","alpha-unknown-linux-gnu",[]]
		else:
			results=["alpha","-O3 -mcpu="+subarch,"alpha"+subarch+"-linux-gnu",[]]
	if results==None:
		raise ValueError, "Invalid subarch value passed to compile_defaults (you should not see this)"
	myset["mainarch"]=results[0]
	myset["cflags"]=results[1]
	myset["chost"]=results[2]
	myset["hostuse"]=results[3]
	
def die(msg=None):
	if msg:
		print "catalyst: "+msg
	sys.exit(1)

def warn(msg):
	print "catalyst: "+msg

modes=["snap","enter","umount","livecd","stage"]
modesdesc={ 	"snap":"Create a snapshot of the Portage tree for building",
		"enter":"Enter the specified build chroot (interactive)",
		"umount":"Unmount the specified build chroot mount points",
		"livecd":"Build the specified LiveCD runtime image",
		"stage":"Build the specified stage tarball or package set",
}

def usage():
	print "catalyst: Gentoo Linux stage/LiveCD/GRP building tool"
	print
	for x in modes:
		print x+":",modesdesc[x]
	die()

def read_settings(myset,myfn):
	"""Grab local settings from a specified file myfn, dump values we are interested in to settings dictionary myset"""
	if not os.path.exists(myfn):
		raise OSError, "Cannot find settings file "+myfn
	valdict={}
	#this next line might throw an exception; it runs the file myfn as python code
	#and dumps all variable definitions in the valdict dictionary.
	try:
		execfile(myfn,valdict,valdict)
	except:
		raise ValueError, "Error parsing settings file: "+myfn
	#now we look inside the valdict dictionary and grab the settings we're interested
	#in.
	for x in ["buildtype","portdir","distdir","ccache"]:
		if valdict.has_key(x):
			myset[x]=valdict[x]

def mainloop():
	global subarches
	#argument processing

	if len(sys.argv)==1 or sys.argv[1] in ["-h","--help"]:
		usage()
	elif os.getuid()!=0:
		#non-root callers can still get -h and --help to work.
		die("This script requires root privileges to operate.")	
	elif sys.argv[1] in modes:
		#set up internal configuration settings dictionary
		myset=settings()
		verify_os(myset)
		#initial mode selection ok, now validate any additional arguments
		#later, we will perform the specified actions
		if os.environ.has_key("HOME"):
			#reading ~/.catalystrc is more an example than anything
			if os.path.exists(os.environ["HOME"]+"/.catalystrc"):
				read_settings(myset,os.environ["HOME"]+"/.catalystrc")
		else:
			warn("HOME environment variable not defined, skipping ~/.catalystrc.")		
		myset.dump()
		print "Done!"
		sys.exit(0)
	else:
		usage()

if __name__ == "__main__":
	mainloop()



