#!/usr/bin/python

subarches=["amd64", "hppa", "hppa1.1", "hppa2.0", "i386", "i486", "i586", "i686",
"athlon", "athlon-xp", "athlon-mp", "pentium-mmx", "pentium3", "pentium4", "ppc", "g3",
"g4", "sparc", "sparc64", "mips", "alpha", "ev4", "ev5", "ev56", "pca56", "ev6", "ev67" ]

def job_defaults(mainarch):
	return "to be completed"

def compile_defaults(subarch):
	"""Accepts a single string argument containing "subarch"
	Returns a list containing [mainarch,CFLAGS,CHOST,aux. [USE settings]],
	or None if invalid subarch"""
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
		uf=[]
		if subarch == "x86":
			cf="-O3 -mcpu=i686"
		elif subarch == "athlon-xp":
			#we've intentionally lowered optimizations here to address compile bugs. It is very likely safe to
			#go up to -O3 without any additional -f goodies (like unroll-loops and prefetch-loop-arrays) tacked
			#on. Note that we don't add any extra -f goodies if we are athlon* below.
			cf="-O3 -march=athlon-xp"
		else:
			cf="-O3 -march="+subarch
		if subarch[0:6] != "athlon":
			cf+=" -funroll-loops"
		else:
			uf.append("3dnow")
		if subarch in [ "athlon","athlon-xp","athlon-mp","pentium-mmx","pentium3","pentium4" ]:
			uf.append("mmx")
		if subarch in [ "pentium3", "pentium4" ]:
			uf.append("sse")
		if subarch in ["pentium-mmx", "pentium3", "pentium4"]:
			cf+=" -fprefetch-loop-arrays"
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
		results=["mips","-O2","mips-unknown-linux-gnu"]
	elif subarch in ["alpha","ev4","ev5","ev56","pca56","ev6","ev67"]:
		if subarch == "alpha":
			results=["alpha","-O3 -mcpu=ev5","alpha-unknown-linux-gnu",[]]
		else:
			results=["alpha","-O3 -mcpu="+subarch,"alpha"+subarch+"-linux-gnu",[]]

	return results			

if __name__ == "__main__":
	#test harness, baby!
	fails=[]
	for x in subarches:
		print x+":",
		mydef=compile_defaults(x)	
		if mydef == None:
			fails.append(x)
		print mydef
	print
	if not len(fails): 
		print "TEST SUCCESSFUL"
	else:
		print len(fails),"TEST FAILURES:",fails
	print
