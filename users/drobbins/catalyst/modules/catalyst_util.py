#!/usr/bin/python
# Copyright 2003 Gentoo Technologies, Inc.; http://www.gentoo.org
# Released under the GNU General Public License version 2

import sys,os

subarches=["amd64", "hppa", "hppa1.1", "hppa2.0", "x86", "i386", "i486", "i586", "i686",
"athlon", "athlon-xp", "athlon-mp", "pentium-mmx", "pentium3", "pentium4", "ppc", "g3",
"g4", "sparc", "sparc64", "mips", "alpha", "ev4", "ev5", "ev56", "pca56", "ev6", "ev67" ]

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
	
def mainloop():
	global subarches
	#argument processing

	if len(sys.argv)==1 or sys.argv[1] in ["-h","--help"]:
		usage()
	elif os.getuid()!=0:
		#non-root callers can still get -h and --help to work.
		die("This script requires root privileges to operate.")	
	elif sys.argv[1] in modes:
		pass
		#initial mode selection ok, now validate any additional arguments
		#later, we will perform the specified actions
	else:
		usage()

if __name__ == "__main__":
	mainloop()



