#!/usr/bin/env python2
# 
# Library of actions that config-kernel can perform
#

import os, sys, glob
import string

from tempfile import gettempdir
from shutil import copy
from time import sleep
from ck_env import getenv, setenv, readEnvFile
from ck_display import *

sys.path.insert(0, "/usr/lib/portage/pym")
from output import *
from portage import ExtractKernelVersion

def usage():
	print bold("Usage:") + " " + green("config-kernel [options]")
	printopt("-h, --help", "Print this text")
	printopt("-d, --display", "Show current config-kernel settings")
	printopt("-l, --list-targets", "Show possible targets for --set-symlink")
	printopt("--set-symlink=[target]", "Set the /usr/src/linux symlink to the target kernel")
	printopt("--set-extraversion=[version]", "Set EXTRAVERSION to 'version' for the kernel in /usr/src/linux")
	printopt("--allow-writable=[yes|no]", "Allow portage to make /usr/src/linux writable during emerges or not")
	printopt("--auto-symlink=[yes|no]", "Enable/Disable portage pointing /usr/src/linux to newly merged sources")
	# printopt("--auto-config=[yes|no]", "Enable/Disable portage copying your .config into newly merged sources")
	printopt("--output-dir=[path]", "Set the directory prefix for kernel output files to 'path'.\n\tCan specifiy 'none' to disable or 'default' for the Gentoo default")
	printopt("--make-koutput=[path]", "Convert the kernel found at 'path' to use output all generated files to\n\ta seperate location. Specify the special keyword 'current' to convert\n\tthe kernel found in /usr/src/linux.")

def listkernels():
	info("Available Kernel Targets:")
	os.chdir(os.path.join("/", "usr", "src"))
	kernels = glob.glob("linux-*")
	kernels.sort()
	for target in kernels:
		# Skip those pesky directory symlinks
		if target == "linux" or target == "linux-beta":
			continue	
		target = target.strip("linux-")
		print (target)

# setsymlink(version) sets the /usr/src/linux symlink to some valid
# kernel version found in /usr/src. e.g: setsymlink("2.4.24")
def setsymlink(version):
	newpath=""
	if os.path.exists("/usr/src/linux") and \
		not os.path.islink("/usr/src/linux"):
			warn("/usr/src/linux is not a symlink!")
			sys.exit()
		
	if version[0] == "/":
		if not os.path.isdir(version):
				warn("Path not found. Please specify either a kernel version or a full path to a kernel tree")
				sys.exit(2)
		if not os.path.isfile(os.path.join(version,"Makefile")):
				warn("No toplevel kernel makefile found in "  + version )
				warn("Make sure the specified path points to a valid kernel tree")
				sys.exit(2)
		newpath = version
		info("Pointing /usr/src/linux to " + version)
	else:
		if not os.path.isdir(os.path.join("/", "usr", "src", "linux-" + version)):
			warn("Version " + version + " not found!")
			sys.exit(2)
		else:
			info("Pointing /usr/src/linux to /usr/src/linux-" + version)
			newpath = "/usr/src/linux-" + version
		
	if os.path.islink("/usr/src/linux"):
		ret = os.system("rm /usr/src/linux")
		if ret:
			warn ("Unable to remove the /usr/src/linux symlink!")
			sys.exit(2)

	command = "ln -s " + newpath + " /usr/src/linux"
	ret = os.system(command)
	if ret:
		warn ("Unable to create the /usr/src/linux symlink!")
		sys.exit(2)

# eclasssymlink(version) is a wrapper to setsymlink(version) which only does the
# symlink if AUTO_SYMLINK="yes". Used by kernel-2.eclass to update the symlink
def eclassymlink(version):
	autosym, err = getenv('AUTO_SYMLINK')
	if err or autosym != "yes":
		info("Auto-symlink support disabled. Not updating /usr/src/linux.")
	else:
		info("Auto-symlink support detected.")
		setsymlink(version)
		
# setextraversion(version) is used to change the value of EXTRAVERSION in the 
# toplevel makefile of the kernel found in /usr/src/linux. Useful if using
# KBUIOD_PREFIX=/some/path/$MAJOR.$MINOR.$PATCHLEVEL$EXTRAVERSION to
# automaticallyhave lots of nice output locations.
def setextraversion(version):
	# List storing values which should be left on the EXTRAVERSION line
	extraSpecial = ["rc", "pre", "alpha", "beta"]
	
	if not os.path.isdir("/usr/src/linux"):
		warn ("Directory /usr/src/linux not found. Make sure this points to")
		warn ("a valid kernel source tree before using --set-extraversion.")
		sys.exit(2)
	
	if not os.path.isfile("/usr/src/linux/Makefile"):
		warn ("No toplevel kernel Makefile detected. Make sure /usr/src/linux")
		warn ("points to a full kernel tree")
		sys.exit(2)

	info("Backing up original makefile to /usr/src/linux/Makefile.orig")
	copy("/usr/src/linux/Makefile","/usr/src/linux/Makefile.orig")

	# Inform them what's going on
	if not version or version == "none":
		version = ""
		info("Unsetting EXTRAVERSION...")
	else:
		# extraversions should really start with a '-'
		if version[0] != "-":
			warn("Prefixing '-' to the version specified")
			version = "-" + version
		info("Setting EXTRAVERSION to '" + version + "'")
	
	# Used to create our sed piece looking for special elements
	# which should be LEFT in EXTRAVERSION
	specials = extraSpecial[0]
	for key in extraSpecial[1:]:
		specials = specials + "\|" + key

	copy("/usr/src/linux/Makefile","/usr/src/linux/Makefile.org")
	command = "sed -i 's:^EXTRAVERSION.*=.*\(-\(" + specials + "\)[0-9]\+\)*.*:EXTRAVERSION = \\1" \
		+ version + ":' /usr/src/linux/Makefile"
	ret = os.system(command)

	# FIXME: Nasty bit of bash hiding in a python program. shame on me.
	tochild , fromchild , childerror = os.popen3("grep '^KBUILD_OUTPUT.*=.*' /usr/src/linux/Makefile | grep VERSION | cut -d'=' -f2  | sed 's:$(VERSION.*::'")
	# If we had errors, then we've probably not found anything
	if childerror.readline():
		return
	
	kbuildprefix = fromchild.readline()

	# If we found something, fix the KBUILD_OUTPUT stuff
	if kbuildprefix:
		# Fix for a random newline we sometimes acquire
		if kbuildprefix[-1] == "\n":
			kbuildprefix = kbuildprefix[:-1]
	
		if kbuildprefix and kbuildprefix != "0":
			newKV, error = ExtractKernelVersion("/usr/src/linux")
			if error:
				warn ("Error determining your new kernel version!")
				sys.exit(2)
			else:
				os.mkdir(os.path.join(kbuildprefix,newKV))

	return

# setoutput(path) defines KBUILD_OUTPUT_PREFIX in envfile, for future
# kernel installations using kernel-2.eclass
def outputdir(path):

	# "default" really means /var/tmp/kernel-output
	if path == "default":
		path = os.path.join("/" , "var", "tmp", "kernel-output")

	# Set the path, setenv will handle the case where path="none"
	setenv('KBUILD_OUTPUT_PREFIX', path)

	if path == "none":
		return

	if not os.path.isdir(path):
		warn("Directory " + path + " does not exist.")
		warn("This path will be created next time you emerge a kernel")

# getoutputPrefix() queries for the current KBUILD_OUTPUT_PREFIX and prints that
# string to stdout. Used in kernel-2.eclass to figure out what to set the output
# to.
def getOutputPrefix():
	out, err = getenv('KBUILD_OUTPUT_PREFIX')
	if err:
		print ""
		sys.exit(2)
	
	if not out:
		print ""
		sys.exit(2)
	else:
		print out
		sys.exit()

# isWritable() queries to find out if the current configuration allows making
# /usr/src/linux writable for 2.6 kernel modules built against traditional
# kernel source layouts
def isWritable():
	writable, err = getenv('LINUX_PORTAGE_WRITABLE')
	if err:
		print "no"
		sys.exit(2)
	else:
		print writable
		sys.exit()

# makekoutput converts the kernel found at "path" to using a seperate output
# directory
def makekoutput(path):
	# Check that we're got a sane configuration
	makekoutputCheck(path)
	
	outputpath, outputMake = makekoutputGetDir(path)

	info("Changing kernel found in " + path)
	info("to output to " + outputpath)
	warn ("You will lose all of your compiled files in " + path)
	warn ("Hit Control C to cancel this now.")
	for count in range(5):
		i = (5-count)
		print red(str(i)),
		sys.stdout.flush()
		sleep(1)
	print ""

	# Backup our config
	config = os.path.join(path,".config")
	configtemp = os.path.join(gettempdir(),".config")
	if os.path.isfile(config):
		info("Backing up your .config file")
		copy(config, configtemp)
	else:
		config = ""
		configtemp = ""
	
	info("Running 'make mrproper to clean your kernel tree (This make take a while)")
	os.chdir(path)
	tochild, fromchild, childerror = os.popen3("make mrproper")
	error = childerror.readlines()
	if len(error) > 0:
		for line in error:
			print (string.strip(line))
		warn ("Error running 'make mrproper' in your kernel tree")
		sys.exit(2)

	# Use sed to add new KBUILD_OUTPUT path
	command = "sed -i 's:\(^EXTRAVERSION.*\):\\1\\nKBUILD_OUTPUT = " + outputMake + ":' "
	command += os.path.join(path, "Makefile")
	ret = os.system(command)
	if ret:
		warn ("Error editing your kernel's toplevel Makefile!")
		if config:
			copy(os.path.join(gettempdir(), ".config"),outputpath)
			warn ("Restoring your .config to " + path)
		sys.exit(2)

	os.mkdir(outputpath)
	if config:
		info("Copying your .config into " + outputpath)
		copy(os.path.join(gettempdir(), ".config"),outputpath)
		
def makekoutputCheck(path):
	if not os.path.isdir(path):
		warn (path + " does not exist! Please specify a valid path")
		sys.exit(2)

	# Mild sanity check to ensure we at least have the makefile we need to edit
	if not os.path.isfile(os.path.join(path, "Makefile")):
		warn ("Could not find a kernel toplevel Makefile at " + path)
		warn ("Please specify a valid path to a complete 2.6 kernel")
		sys.exit(2)
	
	# 2.4 kernels had a Rules.make file, check to make sure we're not on 2.4
	if os.path.isfile(os.path.join(path, "Rules.make")):
		warn ("Detected a 2.4 kernel. You can only enable seperate output locations")
		warn ("for 2.6 series kernels")
		sys.exit(2)
	
	result = os.popen("grep '^KBUILD_OUTPUT[ ]*=' " + os.path.join(path, "Makefile")).readline()
	if result:
		warn ("Kernel detected to already be using koutput. Exiting...")
		sys.exit(2)

# Used to determine where the kernel should output it's files too
def makekoutputGetDir(path):
	outputdir, error = getenv('KBUILD_OUTPUT_PREFIX')

	if not outputdir:
		warn ("No output location has been specified, using the Gentoo default of")
		warn ("/var/tmp/kernel-output/$KV")
		outputdir = os.path.join("/", "var", "tmp", "kernel-output")

	makeoutput = os.path.join(outputdir, "$(VERSION).$(PATCHLEVEL).$(SUBLEVEL)$(EXTRAVERSION)")

	kv, error = ExtractKernelVersion(path)

	if kv:
		outputdir = os.path.join(outputdir, kv)
	else:
		warn ("Unable to determine the kernel version fount at " + path) 
		sys.exit(2)
	
	if os.path.isdir(outputdir):
		warn ("Output directory already detected. Either your kernel is already set")
		warn ("to use this output, or your kernel versions are confused.")
		sys.exit(2)
	
	return outputdir, makeoutput
	
# Prints the current contents /etc/env.d/05kernel
def printenv():
	err, vars = readEnvFile()
	if err:
		warn ("No variables defined")
	info("These variables are currently set:")
	for key in vars:
		if vars[key]:
			print key + "=" + vars[key]

# vim:ts=4:
