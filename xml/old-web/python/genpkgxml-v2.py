#! /usr/bin/env python
# genpkgxml-v2.py
# Based upon the genpkgxml.py by Grant Goodyear, this script extends the fuctionality and general look and feel.


import portage, string, os, os.path, time, sys, re
from stat import *
#####################################
# prog start, and main variable, and compiled regex's
#####################################
license_re=     re.compile(r"^LICENSE=\"([^\"]*)\"",re.M|re.I|re.S)
homepage_re=    re.compile(r"^HOMEPAGE=\"([^\"]*)\"",re.M|re.I|re.S)
desc_re=        re.compile(r"^DESCRIPTION=\"([^\"]*)\"",re.M|re.I|re.S)
pkgdir  = "../xml/packages/"

############
# Subroutine time
############
# XML output
############

def do_header(package_name):
        header ="""<?xml version='1.0'?>
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
        tree = portage.portagetree()
        for node in tree.getallnodes():
                mybest=tree.dep_bestmatch(node)
                if not mybest:
                        continue
                        #no match
                mysplit=mybest.split("/")
                mydbkey="/var/cache/edb/dep/dep-"+mysplit[1]+".ebuild"
                PN, PV, PR = portage.pkgsplit(mysplit[1])
                cpv=mysplit[0]+"/"+PN+"-"+ PV+"-"+PR
                myebuild = portage.db["/"]["porttree"].getname(cpv)
                myroot = "/"
                edebug=0
                #use the cached info if it is available and more recent than the ebuild itself (mtime)
                dbstat=0
                regen=0
                try:
                        dbstat=os.stat(mydbkey)[ST_MTIME]
                except OSError:
                        regen=1
                if not regen:
                        if dbstat<(os.stat(myebuild)[ST_MTIME]):
                                regen=1
                if regen:
                        portage.doebuild(myebuild,"depend",myroot,edebug)
                mydb=open(mydbkey,"r")
                edepend=eval(mydb.readline())
                mydb.close()

                if (PR== "r0"):
                        PnV = PV
                else:
                        PnV=PV + PR
                ####################
                # whack in the version
                ####################
                if not db.has_key(mysplit[0]):
                        db[mysplit[0]]={}
                if not db[mysplit[0]].has_key(PN):
                        db[mysplit[0]][PN]={}
                db[mysplit[0]][PN]['version']=PnV
                #####################
                # get the ebuild filename and slurp it in
                #####################
                file=open(myebuild,"r")
                filecontent=file.read()
                file.close()
                #####################
                # remove any \ escapes,.. we don't need them,
                #####################
                string.replace(filecontent,'\\',' ')
                #####################
                # get the description
                #####################
                desc_mo=desc_re.search(filecontent)
                if desc_mo != None:
                        description=desc_mo.group(1)
                        description=string.replace(description,'&','&amp;')
                        description=string.replace(description,'<','&lt;')
                        description=string.replace(description,'>','&gt;')
                        description=re.sub('[-a-zA-z\.0-9]+\@[-a-zA-z\.0-9]+','<mail link="\1">\1</mail>',description)
                        db[mysplit[0]][PN]['description'] = description
                else:
                        db[mysplit[0]][PN]['description'] = "No DESCRIPTION !!!!!"
                #####################
                # Get the license
                #####################
                license_mo=license_re.search(filecontent)
                if license_mo != None:
                        db[mysplit[0]][PN]['license']   = license_mo.group(1)
                else:
                        db[mysplit[0]][PN]['license']   = "No Licesne Specified"

                #####################
                # Get the homepage
                #####################
                homepage_mo=homepage_re.search(filecontent)
                if homepage_mo != None:
                        db[mysplit[0]][PN]['homepage']  = homepage_mo.group(1)
                else:
                        db[mysplit[0]][PN]['homepage']  = "No HOMEPAGE!!"

                ##########################
                # now we have the dependancies, lets wassname.. throw them into the db
                ##########################
                # Theses will need to be cleaned up before final realease
                ##########################
                depend=edepend[0]
                depend=string.replace(depend,'<','&lt;')
                depend=string.replace(depend,'>','&gt;')
                rdepend=edepend[1]
                rdepend=string.replace(rdepend,'<','&lt;')
                rdepend=string.replace(rdepend,'>','&gt;')
                db[mysplit[0]][PN]['depend']    = depend
                db[mysplit[0]][PN]['rdepend']   = rdepend
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
        pkgentry ="""
        <title>"""+pkgname+""" Information</title>
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
        <th>Package Homepage</th>
        <ti><uri>"""+db[category][pkgname]["homepage"]+"""</uri></ti>
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
        <th>Licensed under</th>
        <ti>"""+db[category][pkgname]["license"]+"""</ti>
        </tr>
        <tr>
        <th>Package Description</th>
        <ti>"""+db[category][pkgname]["description"]+"""</ti>
        </tr>
        <tr>
        <th>CVS Repository</th>
        <ti><uri link="http://www.gentoo.org/cgi-bin/viewcvs/gentoo-x86/"""+category +"/" +pkgname+'/">' + pkgname + """</uri></ti>
        </tr>
	</table></p>
        """
        return pkgentry
#if __name__ == "__main__":
#       # xml file to be generated
#       out = file(sys.argv[1], "w")
#       pkglist = getcurrentpkgs()
#       out.write(header)
#       out.write("<chapter>\n")
#       out.write("<section>\n")
#       out.write("<title>Today's list of %d Gentoo Packages</title>\n" % len(pkglist))
#       out.write("<body>\n")
#       out.write(tableheader)
#       for pkg in pkglist:
#               pkgentry = getpkgentry(pkg)
#               out.write(pkgentry)
#       out.write(footer)

############
# main processing loop
############
db ={}
create_pkg_db(db)
out = file(sys.argv[1], "w")
header=do_header('index')
content="""<p>
        <table>
        <tr>
        <th>Category</th>
        </tr>
"""
out.write(header)
out.write(content)
side='1'
for category in fsort(db.keys()):
        if (side=='1'):
                out.write('<tr>\n') 
                out.write('<ti><uri link="/packages/'+category+'/index.html">'+category+'</uri></ti>\n')
                side='2'
        elif (side=='2'):
                out.write('<ti><uri link="/packages/'+category+'/index.html">'+category+'</uri></ti>\n')
                side='3'
        elif (side=='3'):
                out.write('<ti><uri link="/packages/'+category+'/index.html">'+category+'</uri></ti>\n')
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
for category in fsort(db.keys()):
        workdir = pkgdir + category
        if not os.path.exists(workdir):
                os.makedirs(workdir)

        for pkg in db[category].keys():
                pkg_desc_dir = workdir #+ "/" +pkg
                if not os.path.exists(pkg_desc_dir):
                        os.makedirs(pkg_desc_dir)
                pkg_desc= pkg_desc_dir + "/index.xml"
                out=open(pkg_desc,"w")
                header="""<?xml version='1.0'?>
                <mainpage id="packages">
                <title>Gentoo Linux Packages</title> 
                <author title="Grant Goodyear"><mail link="g2boojum@gentoo.org">Grant Goodyear</mail></author>
                <author title="Colin Morey"><mail link="peitolm@gentoo.org">Colin Morey</mail></author>
                <version>Current</version>
                <date>%s</date>
                <chapter>""" % time.asctime(time.localtime())
                out.write(header)
                tableheader="""<section>
                                <title>Package Category """+ category+"""</title>
                                <body>
                                <p>
                                <table>
                                <tr>
                                <th>Package</th>
                                <th>Version</th>
                                </tr>"""
                out.write(tableheader)
                for pkgname in db[category].keys():
                        entry="""<tr>
                                <ti><uri link=\"/packages/"""+category+"/"+pkgname+".html\">"+pkgname+"""</uri></ti>
                                <ti>"""+db[category][pkgname]["version"]+"</ti></tr>"
                        out.write(entry)
			pkg_file=pkg_desc_dir + "/" +pkgname +".xml"
			pkg_out=open(pkg_file,"w")
			header="""<?xml version='1.0'?>
			<mainpage id="packages">
			<title>Gentoo Linux Packages""" + pkgname + """</title>
			<author title="Grant Goodyear"><mail link="g2boojum@gentoo.org">Grant Goodyear</mail></author>
			<author title="Colin Morey"><mail link="peitolm@gentoo.org">Colin Morey</mail></author>
			<version>Current</version>
			<date>%s</date>
			<chapter>
			<section>""" % time.asctime(time.localtime())
			pkg_out.write(header)
			pkg_entry=do_pkgentry(db,pkgname,category)
			pkg_out.write(pkg_entry)
			footer=do_footer()
			pkg_out.write(footer)
			pkg_out.close()
		out.write("</table></p>\n")
		footer=do_footer()
		out.write(footer)
		out.close()
