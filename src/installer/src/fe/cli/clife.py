#!/usr/bin/python
# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.
# $Header: /var/cvsroot/gentoo/src/installer/src/fe/cli/clife.py,v 1.7 2005/10/15 17:24:46 agaffney Exp $

import sys
sys.path.append("../..")

import time
from optparse import OptionParser

import GLIClientConfiguration
import GLIClientController
import GLIInstallProfile
from GLILogger import Logger
import GLIUtility

clilog = None

def msg(s):
	print s
	if clilog != None:
		clilog.log(s)
	

def main():
	clilog = Logger("/var/log/installer-cli.log")
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
	
	msg("Loading client profile: "+client_config_xml_file)
	if not GLIUtility.get_uri( client_config_xml_file, "/var/tmp/clientconfiguration.xml" ):
		msg("Couldn't open client profile: "+client_config_xml_file)
		sys.exit(-1)
	client_profile.parse("/var/tmp/clientconfiguration.xml")
	client_profile.set_interactive(None, False, None)
	cc.set_configuration(client_profile)
	cc.start_pre_install()
	
	msg("Loading install profile: "+install_profile_xml_file)
	if not GLIUtility.get_uri( install_profile_xml_file, "/var/tmp/installprofile.xml" ):
		msg("Couldn't open client profile: "+client_config_xml_file)
		sys.exit(-1)
	install_profile.parse("/var/tmp/installprofile.xml")
	cc.set_install_profile(install_profile)
	cc.start_install()
	if options.pretend_install:
		msg("Pretending ")

	msg("Serializing XML for test reasons.")
	f = open("/var/tmp/clientconfiguration-serialized.xml","w")
	f.write(install_profile.serialize())
	f.close()
	f = open("/var/tmp/installprofile-serialized.xml","w")
	f.write(install_profile.serialize())
	f.close()

	msg("Installation Started!")
	num_steps_completed = 1
	while 1:
		notification = cc.getNotification()
		if notification == None:
			time.sleep(1)
			continue
		notify_type = notification.get_type()
		notify_data = notification.get_data()
		if notify_type == "exception":
			msg("Exception ("+repr(notify_data)+") received:\n"+str(notify_data))
		elif notify_type == "int":
			if notify_data == GLIClientController.NEXT_STEP_READY:
				next_step = cc.get_next_step_info()
				num_steps = cc.get_num_steps()
				i = (num_steps_completed*100)/num_steps
				s = "On step %d of %d. Current step: %s" % (num_steps_completed, num_steps, next_step)
				msg(s)
				num_steps_completed += 1
				if cc.has_more_steps():
					cc.next_step()
				continue
			if notify_data == GLIClientController.INSTALL_DONE:
				msg("Install completed")
				msg("Install done!")
				sys.exit(0)

if __name__ == "__main__":
	main()
