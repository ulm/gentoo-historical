# 
# Library of actions that config-kernel can perform
# $Header: /var/cvsroot/gentoo/src/kernel/config-kernel/config_kernel/ck_actions.py,v 1.1 2004/03/16 03:52:52 latexer Exp $
#

import os, sys, glob
import string

from tempfile import gettempdir
from shutil import copy
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
	printopt("--allow-writable=[yes|no]", "Allow portage to make /usr/src/linux writable during emerges or not")
	printopt("--auto-symlink=[yes|no]", "Enable/Disable portage pointing /usr/src/linux to newly merged sources")
	printopt("--auto-config=[yes|no]", "Enable/Disable portage copying your .config into newly merged sources")
	printopt("--output-dir=[path]", "Set the directory prefix for kernel output files to 'path'.\n\tCan specifiy 'none' to disable or 'default' for the Gentoo default")
	printopt("--make-koutput=[path]", "Convert the kernel found at 'path' to use output all generated files to a seperate\n\tSpecify the special keyword 'current' to convert the kernel found in /usr/src/linux.")

def listkernels():
	print green("Available Kernel Targets:")
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
	if not os.path.islink("/usr/src/linux"):
		warn("/usr/src/linux is not a symlink!")
		sys.exit()
		
	if not os.path.isdir(os.path.join("/", "usr", "src", "linux-" + version)):
		warn("Version " + version + " not found!")
		sys.exit()
		
	print green("Pointing /usr/src/linux to /usr/src/linux-" + version)
	ret = os.system("rm /usr/src/linux")
	if ret:
		warn ("Unable to remove the /usr/src/linux symlink!")
		sys.exit(2)

	command = "ln -s /usr/src/linux-" + version + " /usr/src/linux"
	ret = os.system(command)
	if ret:
		warn ("Unable to remove the /usr/src/linux symlink!")
		sys.exit(2)

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

# makekoutput converts the kernel found at "path" to using a seperate output
# directory
def makekoutput(path):
	# Check that we're got a sane configuration
	makekoutputCheck(path)
	
	outputpath = makekoutputGetDir(path)

	print green("Changing kernel found in " + path)
	print green("to output to " + outputpath)
	# Backup our config
	print green("Backing up your .config file")
	if os.path.isfile(os.path.join(path, ".config")):
		copy(os.path.join(path , ".config"), gettempdir())
	
	print green("Running 'make mrproper to clean your kernel tree (This make take a while)")
	os.chdir(path)
	tochild, fromchild, childerror = os.popen3("make mrproper")
	error = childerror.readlines()
	if len(error) > 0:
		for line in error:
			print (string.strip(line))
		warn ("Error running 'make mrproper' in your kernel tree")
		sys.exit(2)

	# Use sed to add new KBUILD_OUTPUT path
	command = "sed -i 's:\(^EXTRAVERSION.*\):\\1\\nKBUILD_OUTPUT = " + outputpath + ":' "
	command += os.path.join(path, "Makefile")
	ret = os.system(command)
	if ret:
		warn ("Error editing your kernel's toplevel Makefile!")
		copy(os.path.join(gettempdir(), ".config"),outputpath)
		warn ("Restoring your .config to " + path)
		sys.exit(2)

	os.mkdir(outputpath)
	print green("Copying your .config into " + outputpath)
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

# Used to determine where the kernel should output it's files too
def makekoutputGetDir(path):
	outputdir, error = getenv('KBUILD_OUTPUT_PREFIX')
	#outputdir.strip("\"")
	print outputdir
	if not outputdir:
		warn ("No output location has been specified, using the Gentoo default of")
		warn ("/var/tmp/kernel-output/$KV")
		outputdir = os.path.join("/", "var", "tmp", "kernel-output")
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
	
	return outputdir
	
# Prints the current contents /etc/env.d/05kernel
def printenv():
	err, vars = readEnvFile()
	if err:
		warn ("No variables defined")
	print green("These variables are currently set:")
	for key in vars:
		if vars[key]:
			print key + "=" + vars[key]

# vim:ts=4:
