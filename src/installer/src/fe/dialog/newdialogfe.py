#!/usr/bin/python

import sys
sys.path.append("../..")

import dialog
import GLIException
import GLIInstallProfile
import GLIClientConfiguration
import GLIClientController
import GLIUtility
import GLIStorageDevice
from GLIGenDialog import GLIGenCF,GLIGenIP
import string
import copy
import time
import re
import glob
import os
import platform

class CFDialog(GLIGenCF):
	def __init__(self):
		GLIGenCF.__init__(self)
		self._set_arch_template()
		self._set_logfile()
		self._set_root_mount_point()
		self._set_client_networking()
		self._set_livecd_password()
		self._set_enable_ssh()
		self._set_client_kernel_modules()
		self.client_config_xml_file = None
		if d.yesno("Do you want to save the ClientConfiguration XML file?") == DLG_YES:
			self.client_config_xml_file = self._save_client_profile()

class IPDialog(GLIGenIP):
	def __init__(self, local_install):
		GLIGenIP.__init__(self, local_install)
		self.install_profile_xml_file = None
		if d.yesno("Do you want to save the InstallProfile XML file?") == DLG_YES:
			self.install_profile_xml_file = self._save_install_profile()

# ------------------------------------------------------------------
if __name__ == '__main__':

	d = dialog.Dialog()
	client_profile = GLIClientConfiguration.ClientConfiguration()
	install_profile = GLIInstallProfile.InstallProfile()
	cc = GLIClientController.GLIClientController(pretend=True)
	exception_waiting = None
	next_step_waiting = False
	install_done = False
	local_install = True

	DLG_OK = 0
	DLG_YES = 0
	DLG_CANCEL = 1
	DLG_NO = 1
	DLG_ESC = 2
	DLG_ERROR = 3
	DLG_EXTRA = 4
	DLG_HELP = 5

	d.setBackgroundTitle("Gentoo Linux Installer")
	d.msgbox("Welcome to The Gentoo Linux Installer. This is a TESTING release. If your system dies a horrible, horrible death, don't come crying to us (okay, you can cry to klieber).", height=10, width=50, title="Welcome")

	if d.yesno("Are we running in Pretend mode? Yes means safe, No means actually install!") == DLG_NO:
		cc._pretend = False
	else:
		cc._pretend = True
	
	if d.yesno("Are the profiles being generated to be used for an install on the current computer?") == DLG_NO:
		local_install = False
	

	if d.yesno("Do you want to use the ClientController? (if doing an install, say YES)") == DLG_YES:
		client_config_xml_file = None
		while 1:
			if d.yesno("Do you have a previously generated XML file for the ClientConfiguration?") == DLG_YES:
				code, client_config_xml_file = d.inputbox("Enter the filename of the XML file")
				if code != DLG_OK: 
					break
				if GLIUtility.is_file(client_config_xml_file): 
					break
				d.msgbox("Cannot open file " + client_config_xml_file, height=7, width=50)
				client_config_xml_file = None
				continue
			else:
				break
			
	if client_config_xml_file != None:
		client_profile.parse(client_config_xml_file)
	# code to actually run the client_controller functions
	else:
		gen_client_conf = CFDialog()
		if gen_client_conf.client_config_xml_file:
			client_profile.parse(gen_client_conf.client_config_xml_file)
		else:
			client_profile = gen_client_conf.client_profile()
			
	d.msgbox("ClientController done")

	client_profile.set_interactive(None, True, None)
	cc.set_configuration(client_profile)

	cc.start_pre_install()

	install_profile_xml_file = None

	while 1:
		if d.yesno("Do you have a previously generated InstallProfile XML file?") == DLG_YES:
			code, install_profile_xml_file = d.inputbox("Enter the filename of the XML file")
			if code != DLG_OK: 
				break
			if GLIUtility.is_file(install_profile_xml_file): 
				break
			d.msgbox("Cannot open file " + install_profile_xml_file, height=7, width=50)
			install_profile_xml_file = None
		else:
			break
	
	if install_profile_xml_file != None:
		install_profile.parse(install_profile_xml_file)
	else:
		gen_install_profile = IPDialog(local_install)
		if gen_install_profile.client_config_xml_file:
			install_profile.parse(gen_install_profile.client_config_xml_file)
		else:
			install_profile = gen_install_profile.install_profile()
	
	d.msgbox("InstallProfile done")	
	
	current_item = 0
	
	while 1:
		cc.set_install_profile(install_profile)
		cc.start_install()
		d.gauge_start("Installation Started!", title="Installation progress")
		num_steps_completed = 1
		while 1:
			notification = cc.getNotification()
			if notification == None:
				time.sleep(1)
				continue
			type_r = notification.get_type()
			data = notification.get_data()
			if type_r == "exception":
				print "Exception received:"
				print data
			elif type_r == "int":
				if data == GLIClientController.NEXT_STEP_READY:
					next_step_waiting = False
					next_step = cc.get_next_step_info()
					num_steps = cc.get_num_steps()
					i = (num_steps_completed*100)/num_steps
					d.gauge_update(i, "On step %d of %d. Current step: %s" % (num_steps_completed, num_steps, next_step), update_text=1)
					num_steps_completed += 1
					#print "Next step: " + next_step
					if cc.has_more_steps():
						cc.next_step()
					continue
				if data == GLIClientController.INSTALL_DONE:
					d.gauge_update(100, "Install completed!", update_text=1)
					d.gauge_stop()
					print "Install done!"
					sys.exit(0)
