# einfo.py
# Distributed AS-IS, without warranty. Licensed under the GPL v2 or newer.
# $Header: /var/cvsroot/gentoo/users/jhuebel/einfo/einfo.py,v 1.6 2004/07/19 14:31:45 jhuebel Exp $

__module_name__ = "einfo"
__module_version__ = "0.3"
__module_description__ = "Display emerge info to an xchat channel"

import xchat

import os,sys
os.environ["PORTAGE_CALLER"]="emerge"
sys.path = ["/usr/lib/portage/pym"]+sys.path

import emergehelp,xpak,string,re,commands,time,shutil,traceback,atexit,signal,socket,types
from stat import *
from output import *
import portage

def getgccversion():
        """
        rtype: C{str}
        return:  the current in-use gcc version
        """

        gcc_env_dir = os.path.join('/', 'etc', 'env.d', 'gcc')
        gcc_config_config = os.path.join(gcc_env_dir, 'config')
        gcc_ver_command = '`which gcc` -dumpversion'
        gcc_ver_prefix = 'gcc-'

        gcc_not_found_error = red(
        "!!! No gcc found. You probably need to 'source /etc/profile'\n" +
        "!!! to update the environment of this terminal and possibly\n" +
        "!!! other terminals also."
        )

        gcc_distcc_broken_error = green(
        '!!! Using `which gcc` to gcc locate version, this may break\n' +
        '!!! DISTCC, installing gcc-config and setting your current gcc\n' +
        '!!! profile will fix this'
        )

        def fallback():

                print >>sys.stderr, gcc_distcc_broken_error

                gccout = commands.getstatusoutput(gcc_ver_command)

                if gccout[0] != 0:
                        print >>sys.stderr, gcc_not_found_error
                        gccver = "[unavailable]"
                else:
                        gccver = gcc_ver_prefix + gccout[1]

                return gccver

        if os.path.isfile(gcc_config_config):
                try:
                        gccver = gcc_ver_prefix + open(gcc_config_config).read().strip().split('-')[-1]
                except IndexError:
                        gccver = fallback()

        else:
                import glob
                dir_l = glob.glob(os.path.join(gcc_env_dir, '*-*'))

                if len(dir_l) == 1:
                        try:
                                gccver = gcc_ver_prefix + dir_l[0].split('-')[-1]
                        except IndexError:
                                gccver = fallback()

                else:
                        # There was no "config" file in /etc/env.d/gcc and there was more
                        # than one profile in /etc/env.d/gcc so we can't actively
                        # determine what version of gcc we are using so we fall back on the
                        # old way that breaks distcc

                        gccver = fallback()

        return gccver

def getportageversion():
        try:
                profilever=os.path.basename(os.path.normpath(os.readlink("/etc/make.profile")))
        except:
                profilever="unavailable"
        glibcver=[]
        for x in portage.vardbapi(portage.root).match("glibc"):
                xs=portage.pkgsplit(x)
                if glibcver:
                        glibcver+=","+xs[1]+"-"+xs[2]
                else:
                        glibcver=xs[1]+"-"+xs[2]
        if glibcver==[]:
                glibcver="unavailable"

        gccver = getgccversion()

        unameout=os.uname()[2]

        return "Portage " + portage.VERSION +" ("+profilever+", "+gccver+", glibc-"+glibcver+", "+unameout+")"

def chanmsg(msg):
	mychannel = xchat.get_info('channel')
	xchat.command("msg " + mychannel + " " + msg)

def einfo_all(word, word_el, userdata):
	chanmsg(getportageversion())
	chanmsg("------------------------------------")
	chanmsg(commands.getstatusoutput("/bin/uname -mrp")[1])
	chanmsg(commands.getstatusoutput("cat /etc/gentoo-release")[1])

	output=commands.getstatusoutput("`which distcc` --version")
	if not output[0]:
		if "distcc" in portage.features:
			chanmsg(str(string.split(output[1],"\n",1)[0]) + " [enabled]")
		else:
			chanmsg(str(string.split(output[1],"\n",1)[0]) + " [disabled]")
	
	output=commands.getstatusoutput("`which ccache` -V")
	if not output[0]:
		if "ccache" in portage.features:
			chanmsg(str(string.split(output[1],"\n",1)[0]) + " [enabled]")
		else:
			chanmsg(str(string.split(output[1],"\n",1)[0]) + " [disabled]")
	
	chanmsg("Autoconf: " + string.join(portage.db["/"]["vartree"].dbapi.match("sys-devel/autoconf"), ","))
	chanmsg("Automake: " + string.join(portage.db["/"]["vartree"].dbapi.match("sys-devel/automake"), ","))

	myvars=['GENTOO_MIRRORS', 'CONFIG_PROTECT', 'CONFIG_PROTECT_MASK',
			'PORTDIR', 'DISTDIR', 'PKGDIR', 'PORTAGE_TMPDIR', 'PORTDIR_OVERLAY',
			'USE', 'COMPILER', 'CHOST', 'CFLAGS', 'CXXFLAGS','ACCEPT_KEYWORDS', 
			'MAKEOPTS', 'AUTOCLEAN', 'SYNC', 'FEATURES']
	myvars.sort()
	for x in myvars:
		chanmsg(x + '="' + portage.settings[x] + '"')

def einfo(word, word_el, userdata):
	if len(word) < 2:
		einfo_help(word, word_el, userdata)
		return xchat.EAT_ALL
	else:
		if word[1] == "help":
			einfo_help(word, word_el, userdata)
		elif word[1] == "version":
			print __module_name__ + " v" + __module_version__
		elif word[1] == "all":
			einfo_all(word, word_el, userdata)
		elif word[1] == "portage":
			chanmsg(getportageversion())
		elif word[1] == "uname":
			chanmsg(commands.getstatusoutput("/bin/uname -mrp")[1])
		elif word[1] == "gentoo":
			chanmsg(commands.getstatusoutput("cat /etc/gentoo-release")[1])
		elif word[1] == "cflags":
			chanmsg('CFLAGS="' + portage.settings["CFLAGS"] + '"')
		elif word[1] == "chost":
			chanmsg('CHOST="' + portage.settings["CHOST"] + '"')
		elif word[1] == "features":
			chanmsg('FEATURES="' + portage.settings["FEATURES"] + '"')
		elif word[1] == "keywords":
			chanmsg('ACCEPT_KEYWORDS="' + portage.settings["ACCEPT_KEYWORDS"] + '"')
		elif word[1] == "use":
			chanmsg('USE="' + portage.settings["USE"] + '"')
		elif word[1] == "allvars":
			myvars=['GENTOO_MIRRORS', 'CONFIG_PROTECT', 'CONFIG_PROTECT_MASK',
				'PORTDIR', 'DISTDIR', 'PKGDIR', 'PORTAGE_TMPDIR', 'PORTDIR_OVERLAY',
				'USE', 'COMPILER', 'CHOST', 'CFLAGS', 'CXXFLAGS','ACCEPT_KEYWORDS', 
				'MAKEOPTS', 'AUTOCLEAN', 'SYNC', 'FEATURES']
			myvars.sort()
			for x in myvars:
				chanmsg(x + '="' + portage.settings[x] + '"')
		elif word[1] == "pkgversion":
			if string.join(portage.db["/"]["vartree"].dbapi.match(word[2]), ",") == "":
				chanmsg(word[2] + " is not installed.")
			else:
				chanmsg(string.join(portage.db["/"]["vartree"].dbapi.match(word[2]), ","))
		elif word[1] == "df":
			chanmsg(commands.getstatusoutput("/bin/df -h")[1])
		elif word[1] == "free":
			chanmsg(commands.getstatusoutput("/usr/bin/free")[1])
		elif word[1] == "uptime":
			chanmsg(commands.getstatusoutput("/usr/bin/uptime")[1])
		elif word[1] == "date":
			chanmsg(commands.getstatusoutput("/bin/date")[1])
		elif word[1] == "utc":
			chanmsg(commands.getstatusoutput("/bin/date --universal")[1])
		else:
			xchat.prnt("Unknown usage of /einfo")
			return xchat.EAT_ALL
		return xchat.EAT_ALL
	    
def einfo_help(word, word_el, userdata):
	print " "
	print __module_name__ + " v" + __module_version__ + ": displays emerge info to a channel"
	print "Distributed AS-IS, WITHOUT WARRANTY"
	print "http://dev.gentoo.org/~jhuebel/einfo/"
	print " "
	print " /einfo [<option>]"
	print " "
	print " General Options:"
	print "   help     = this help"
	print "   version  = print einfo version"
	print " "
	print " Emerge-Related Information:"
	print "   all      = prints all emerge info (not recommended)"
	print "   portage  = show portage and build environment info"
	print "   uname    = show uname"
	print "   gentoo   = show gentoo version"
	print "   cflags   = show CFLAGS variable"
	print "   chost    = show CHOST variable"
	print "   features = show FEATURES variable"
	print "   keywords = show ACCEPT_KEYWORDS variable"
	print "   use      = show USE variable"
	print "   allvars  = show all emerge variables"
	print "   pkgversion <package>"
	print "            = show the version of <package> that is installed"
	print " "
	print " System Information:"
	print "   df       = disk usage"
	print "   free     = memory usage"
	print "   uptime   = uptime statistics"
	print "   date     = display local date/time"
	print "   utc      = display UTC date/time"
	print " "

xchat.hook_command("einfo", einfo, help="/einfo [ help | all | portage | uname | gentoo | cflags | chost | featuers | keywords | use | allvars ]")

xchat.prnt("emerge info script loaded! Type '/einfo help' for options")
