#! /usr/bin/env python
# genpkgxml-v2.py
# Based upon the genpkgxml.py by Grant Goodyear, this script extends the fuctionality and general look and feel.


import portage, string, os, os.path, time, sys, re
from stat import *
if not os.environ["WEBROOT"]:
	print "$WEBROOT not set; exiting"
	sys.exit(1)

#####################################
# prog start, and main variable, and compiled regex's
#####################################
license_re=     re.compile(r"^LICENSE=\"([^\"]*)\"",re.M|re.I|re.S)
homepage_re=    re.compile(r"^HOMEPAGE=\"([^\"]*)\"",re.M|re.I|re.S)
desc_re=        re.compile(r"^DESCRIPTION=\"([^\"]*)\"",re.M|re.I|re.S)
pkgdir=os.environ["WEBROOT"]+"/dyn/newpkgs/" 
oldpkgdir=os.environ["WEBROOT"]+"/dyn/oldpkgs/"
curpkgdir=os.environ["WEBROOT"]+"/dyn/pkgs/"
try:
	os.makedirs(pkgdir)
except OSError:
	#exists already
	pass

############
# Subroutine time
############
# XML output
############

def do_header(package_name):
	header ="""<?xml version='1.0'?>
<?xml-stylesheet href="/xsl/guide.xsl" type="text/xsl"?>
<mainpage id="packages">
	<title>Gentoo Linux Packages</title>
	<author title="Colin Morey"><mail link="peitolm@gentoo.org">Colin Morey</mail></author>
	<author title="Grant Goodyear"><mail link="g2boojum@gentoo.org">Grant Goodyear</mail></author>
	<version>Current</version>
	<date>""" +  time.asctime(time.localtime()) + """</date>
	<chapter>
		<section><title>Gentoo Package List - """ +  package_name +"""</title>
			<body>
"""
	return header

def do_footer():
	footer = """
			</body>
		</section>
	</chapter>
</mainpage>
	"""
	return footer
###############
# Aparently a sorting function
###############
def fsort(L, f=cmp):
	"""A "functional" sort that returns a copy of L, with all its contents
	sorted out."""
	L2 = L[:]
	L2.sort(f)
	return L2
###############
# This is where i need to get the stuff from portage :)
###############
# get a sorted list of "current" packages, where each
# list entry is [<PN>, <PV>, <PR>, <category>]
###############

def create_pkg_db(db):
	TotalPkgNum=0
	tree = portage.portagetree()
	for node in tree.getallnodes():
		TotalPkgNum += 1
		mybest=tree.dep_bestmatch(node)
		if not mybest:
			continue
			#no match
		mysplit=mybest.split("/")
		PN, PV, PR = portage.pkgsplit(mysplit[1])
		if (PR== "r0"):
			PnV = PV
		else:
			PnV=PV + "-"+PR
			
		cpv=mysplit[0]+"/"+PN+"-"+ PnV
		myebuild = portage.db["/"]["porttree"].getname(cpv)
		myroot = "/"
		edebug=0
		homepage, license, description, depend, rdepend = portage.db["/"]["porttree"].dbapi.aux_get(mybest,["HOMEPAGE","LICENSE","DESCRIPTION","DEPEND","RDEPEND"])

		if (PR== "r0"):
			PnV = PV
		else:
			PnV=PV + PR
		#print PN+"-"+PnV
		
		#XMLize common characters
		depend=string.replace(depend,'<','&lt;')
		depend=string.replace(depend,'>','&gt;')
		rdepend=string.replace(rdepend,'<','&lt;')
		rdepend=string.replace(rdepend,'>','&gt;')
		description=string.replace(description,'&','&amp;')
		description=string.replace(description,'<','&lt;')
		description=string.replace(description,'>','&gt;')
		license=string.replace(license,'&','&amp;')
		license=string.replace(license,'<','&lt;')
		license=string.replace(license,'>','&gt;')
		
		####################
		# whack in the version
		####################
		if not db.has_key(mysplit[0]):
			db[mysplit[0]]={}
		if not db[mysplit[0]].has_key(PN):
			db[mysplit[0]][PN]={}
		db[mysplit[0]][PN]['version']=PnV
		db[mysplit[0]][PN]['description'] = description
		db[mysplit[0]][PN]['license']   = license
		db[mysplit[0]][PN]['homepage']  = homepage

		##########################
		# now we have the dependancies, lets wassname.. throw them into the db
		##########################
		# Theses will need to be cleaned up before final realease
		##########################
		db[mysplit[0]][PN]['depend']    = depend
		db[mysplit[0]][PN]['rdepend']   = rdepend
		if not db[mysplit[0]].has_key('package_count'): 
			db[mysplit[0]]['package_count'] = 0
		db[mysplit[0]]['package_count'] += 1
	db['totalnumberofpackages'] = str(TotalPkgNum)	
	return db

def getcurrentpkgs():
	tree = portage.portagetree()
	currentlist = []
	for node in tree.getallnodes():
		best = tree.dep_bestmatch(node)
		cat, PN, PV, PR = portage.catpkgsplit(best)
		currentlist.append([PN, PV, PR, cat])
	currentlist.sort()
	return currentlist

# take a package (a [PN, PV, PR, category] list) and return the table entry
# for that package:
# <name> <version> <category>
def do_pkgentry(db,pkgname,category):
	nice_homepage=string.replace(db[category][pkgname]["homepage"],'&','&amp;')
	pkgentry ="""
	<title>"""+category+"/"+pkgname+"""</title>
	<body>
	<p>
	<table>
	<tr>
	<th>Package name</th>
	<ti>"""+ pkgname+"""</ti>
	</tr>
	<tr>
	<th>Package version</th>
	<ti>"""+db[category][pkgname]["version"]+"""</ti>
	</tr>
	<tr>    
	<th>Package Homepage</th>"""
	if db[category][pkgname]["homepage"]:
		nice_homepage=string.replace(db[category][pkgname]["homepage"],'&','&amp;')
		nice_homepage=string.replace(nice_homepage,' ','</uri> , <uri>')
		pkgentry += "<ti><uri>"+nice_homepage+"</uri></ti>"
	else:
		pkgentry += "<ti><e>(No homepage specified)</e></ti>"
	pkgentry += """	
	</tr>
	<tr>
	<th>Package Dependencies</th>
	<ti>"""+db[category][pkgname]["depend"]+"""</ti>
	</tr>
	<tr>
	<th>Run-Time Dependencies</th>
	<ti>"""+db[category][pkgname]["rdepend"]+"""</ti>
	</tr>
	<tr>
	<th>Licensed under</th>"""
	if db[category][pkgname]["license"]:
		pkgentry += "<ti>"+db[category][pkgname]["license"]+"</ti>"
	else:
		pkgentry += "<ti><e>(No license specified)</e></ti>"
	pkgentry +="""
	</tr>
	<tr>
	<th>Package Description</th>"""
	if db[category][pkgname]["description"]:
		pkgentry += "<ti>"+db[category][pkgname]["description"]+"</ti>"
	else:
		pkgentry += "<ti><e>(No description specified)</e></ti>"
	pkgentry += """
	</tr>
	<tr>
	<th>View CVS Repository</th>
	<ti><uri>http://cvs.gentoo.org/cgi-bin/viewcvs.cgi/gentoo-x86/"""+category +"/" +pkgname+"""/</uri></ti>
	</tr>
	</table>
	</p>"""
	return pkgentry
############
# main processing loop
############
TotalPkgNum=0
db ={}
create_pkg_db(db)
out = open(pkgdir+"index.xml", "w")
header=do_header('index')
content="""<p>
	Total number of packages available: """ + db['totalnumberofpackages'] + """
	<table>
	<tr>
	<th>Category</th>
	</tr>
"""
del db['totalnumberofpackages']
out.write(header)
out.write(content)
side='1'
for category in fsort(db.keys()):
	if (side=='1'):
		out.write('<tr>\n') 
		out.write('<ti><uri link="/dyn/pkgs/'+category+'/index.xml">'+category+'</uri></ti>\n')
		side='2'
	elif (side=='2'):
		out.write('<ti><uri link="/dyn/pkgs/'+category+'/index.xml">'+category+'</uri></ti>\n')
		side='3'
	elif (side=='3'):
		out.write('<ti><uri link="/dyn/pkgs/'+category+'/index.xml">'+category+'</uri></ti>\n')
		out.write('</tr>\n')
		side='1'
if (side=='2') or (side=='3'):
	out.write('</tr>\n')
out.write('</table></p>')
footer=do_footer()
out.write(footer)
out.close()
####################
# category index pages
####################
mytime=time.asctime(time.localtime())	
for category in fsort(db.keys()):
	workdir = pkgdir + category
	if not os.path.exists(workdir):
		try:
			os.makedirs(workdir)
		except:
			#exists already
			continue
	pkg_count=db[category]['package_count']
	del db[category]['package_count']
	
	pkg_desc_dir = workdir #+ "/" +pkg
	pkg_desc= pkg_desc_dir + "/index.xml"
	out=open(pkg_desc,"w")
	header="""<?xml version='1.0'?>
<?xml-stylesheet href="/xsl/guide.xsl" type="text/xsl"?>
<mainpage id="packages">
	<title>Gentoo Linux Packages</title> 
	<author title="Grant Goodyear"><mail link="g2boojum@gentoo.org">Grant Goodyear</mail></author>
	<author title="Colin Morey"><mail link="peitolm@gentoo.org">Colin Morey</mail></author>
	<version>Current</version>
	<date>%s</date>
		<chapter>""" % mytime 
	tableheader="""
			<section>
				<title>Package Category """+ category+"""</title>
				<body>
				<p>
	Number of packages in category: """ + str(pkg_count) + """
	<table>
	<tr>
	<th>Package</th>
	<th>Version</th>
	</tr>"""
	out.write(header)
	out.write(tableheader)
	
	for pkg in fsort(db[category].keys()):
		entry="""<tr>
			<ti><uri link=\"/dyn/pkgs/"""+category+"/"+pkg+".xml\">"+pkg+"""</uri></ti>
			<ti>"""+db[category][pkg]["version"]+"</ti></tr>"
		out.write(entry)
		pkg_file=pkg_desc_dir + "/" +pkg +".xml"
		pkg_out=open(pkg_file,"w")
		header="""<?xml version='1.0'?>
<?xml-stylesheet href="/xsl/guide.xsl" type="text/xsl"?>
		<mainpage id="packages">
		<title>Package listing: """ + category+"/"+pkg + """</title>
		<author title="Grant Goodyear"><mail link="g2boojum@gentoo.org">Grant Goodyear</mail></author>
		<author title="Colin Morey"><mail link="peitolm@gentoo.org">Colin Morey</mail></author>
		<version>Current</version>
		<date>%s</date>
		<chapter>
		<section>""" % mytime 
		pkg_out.write(header)
		pkg_entry=do_pkgentry(db,pkg,category)
		pkg_out.write(pkg_entry)
		footer=do_footer()
		pkg_out.write(footer)
		pkg_out.close()
		footer=do_footer()
	out.write("</table></p>\n")
	out.write(footer)
	out.close()

#create plaintext package listing
allpkgs=portage.db["/"]["porttree"].dbapi.cp_all()
bestpkgs={}
mycount=0
mytxt=open(pkgdir+"packages.txt","w")
for x in allpkgs:
	if x not in bestpkgs.keys():
		y=portage.db["/"]["porttree"].dbapi.xmatch("bestmatch-visible",x)
		bestpkgs[x]=y
		if y=="":
			continue
		xs=portage.pkgsplit(bestpkgs[x])
		mytxt.write(xs[0].split("/")[1]+" "+xs[1]+" "+bestpkgs[x]+"\n")
		mycount+=1
mytxt.close()

os.system("rm -rf "+oldpkgdir)
os.system("mv "+curpkgdir+" "+oldpkgdir)
os.system("mv "+pkgdir+" "+curpkgdir)

	
