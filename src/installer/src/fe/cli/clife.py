#!/usr/bin/python
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/installer/src/fe/cli/clife.py,v 1.1 2005/06/12 09:50:08 robbat2 Exp $

import sys
sys.path.append("../..")

import GLIInstallProfile
import GLIClientConfiguration
import GLIClientController
import time
from optparse import OptionParser

usage = "usage: %prog [options] CLIENT.xml INSTALL.xml"
parser = OptionParser(usage)
parser.add_option("-p", "--pretend", dest="pretend_install",action="store_true",help="Pretend",default=False)
(options, args) = parser.parse_args()

if len(args) != 2:
	sys.stderr.write("You must specify both client and install profiles!\n")
	sys.exit(-1)

client_config_xml_file = args[0]
install_profile_xml_file = args[1]

client_profile = GLIClientConfiguration.ClientConfiguration()
install_profile = GLIInstallProfile.InstallProfile()
cc = GLIClientController.GLIClientController(pretend=options.pretend_install)

print "Loading client profile: "+client_config_xml_file
client_profile.parse(client_config_xml_file)
client_profile.set_interactive(None, False, None)
cc.set_configuration(client_profile)
cc.start_pre_install()

print "Loading install profile: "+install_profile_xml_file
install_profile.parse(install_profile_xml_file)
cc.set_install_profile(install_profile)
cc.start_install()
if options.pretend_install:
	print "Pretending ",
print "Installation Started!"
num_steps_completed = 1
while 1:
	notification = cc.getNotification()
	if notification == None:
		time.sleep(1)
		continue
	type = notification.get_type()
	data = notification.get_data()
	if type == "exception":
		print "Exception ("+repr(data)+") received:"
		print data 
	elif type == "int":
		if data == GLIClientController.NEXT_STEP_READY:
			next_step = cc.get_next_step_info()
			num_steps = cc.get_num_steps()
			i = (num_steps_completed*100)/num_steps
			s = "On step %d of %d. Current step: %s" % (num_steps_completed, num_steps, next_step)
			print s
			num_steps_completed += 1
			if cc.has_more_steps():
				cc.next_step()
			continue
		if data == GLIClientController.INSTALL_DONE:
			print "Install completed"
			print "Install done!"
			sys.exit(0)
