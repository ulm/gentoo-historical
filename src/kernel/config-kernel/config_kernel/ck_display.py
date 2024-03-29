#
# Library for printing stuff
#
# $Header: /var/cvsroot/gentoo/src/kernel/config-kernel/config_kernel/ck_display.py,v 1.3 2004/03/25 20:09:40 latexer Exp $

import sys

sys.path.append('/usr/portage/pym')
from output import *

def printopt(option, details):
	print ""
	print red("   " + option)
	print red("\t" + details)

def warn(text):
	sys.stderr.write(" " + red("*") + " " + text + "\n")

def info(text):
	sys.stdout.write(" " + green("*") + " " + text + "\n")
