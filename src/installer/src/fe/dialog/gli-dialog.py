#!/usr/bin/python
# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.

import sys
sys.path.append("../..")

import dialog
import GLIException, GLIInstallProfile, GLIClientConfiguration, GLIClientController, GLIUtility, GLIStorageDevice
from GLIGenDialog import GLIGenCF,GLIGenIP
import string, copy, time, re, glob, os, platform
import gettext
_ = gettext.gettext

class Setup_CConfig(GLIGenCF):
	def __init__(self, client_profile, local_install, advanced_mode, networkless):
		GLIGenCF.__init__(self, client_profile, local_install, advanced_mode, networkless)
		self.set_arch_template()
		self.set_verbose()
		self.set_logfile()
		self.set_root_mount_point()
		self.set_client_networking()
		self.set_enable_ssh()
		self.set_livecd_password()
		self.set_client_kernel_modules()
		self.client_config_xml_file = None
		if advanced_mode:
			if d.yesno(_(u"Do you want to save the ClientConfiguration XML file before continuing? (it will be automatically saved before the install begins)")) == DLG_YES:
				self.client_config_xml_file = self.save_client_profile()

class Setup_InstallProfile(GLIGenIP):
	def __init__(self, client_profile, install_profile, local_install, advanced_mode, skip_wizard_question, networkless):
		GLIGenIP.__init__(self, client_profile, install_profile, local_install, advanced_mode, networkless)
		show_review_menu = True
		if not skip_wizard_question:
			#Change the Yes/No buttons to new labels for this question.
			d.add_persistent_args(["--yes-label", _(u"Wizard Mode")])
			d.add_persistent_args(["--no-label", _(u"Skip to Menu")])
			if d.yesno(_(u"The Gentoo Linux Installer can either take you step by step through the installation settings (recommended), or you can instead go straight to the Revisions menu to set your settings before the installation begins."), width=66) == DLG_YES:
				self.set_partitions()
				self.set_network_mounts()
				self.set_install_stage()
				self.set_portage_tree()
				self.set_make_conf()
				if advanced_mode:
					self.set_distcc()
				self.set_kernel()
				self.set_boot_loader()
				self.set_timezone()
				self.set_networking()
				if advanced_mode:
					self.set_cron_daemon()
					self.set_logger()
				self.set_extra_packages()
				if advanced_mode:
					self.set_services()
				self.set_rc_conf()
				self.set_root_password()
				self.set_additional_users()
				self.show_settings()
				#Reset the Yes/No labels.
				d.add_persistent_args(["--yes-label", "Yes"])
				d.add_persistent_args(["--no-label","No"])
				if d.yesno(_(u"Do you want to change any of your settings before starting the actual installation?")) == DLG_NO:
					show_review_menu = False
		if show_review_menu:
			self._fn = (
				{ 'text': "Partitioning", 'fn': self.set_partitions },
				{ 'text': "Network mounts", 'fn': self.set_network_mounts },
				{ 'text': "Install Stage", 'fn': self.set_install_stage },
				{ 'text': "Portage Tree", 'fn': self.set_portage_tree },
				{ 'text': "make.conf", 'fn': self.set_make_conf },
				{ 'text': "distcc", 'fn': self.set_distcc },
				{ 'text': "etc/portage/*", 'fn': self.set_etc_portage },
				{ 'text': "Kernel", 'fn': self.set_kernel },
				{ 'text': "Bootloader", 'fn': self.set_boot_loader },
				{ 'text': "Timezone", 'fn': self.set_timezone },
				{ 'text': "Networking", 'fn': self.set_networking },
				{ 'text': "Cron daemon", 'fn': self.set_cron_daemon },
				{ 'text': "Logging daemon", 'fn': self.set_logger },
				{ 'text': "Extra packages", 'fn': self.set_extra_packages },
				{ 'text': "Services", 'fn': self.set_services },
				{ 'text': "Configuration Settings", 'fn': self.set_rc_conf },
				{ 'text': "Root password", 'fn': self.set_root_password },
				{ 'text': "Additional Users", 'fn': self.set_additional_users })
			self._menu_list = []
			for item in self._fn:
				self._menu_list.append(item['text'])
			current_item = 0
			while 1:
				code, menuitem = self._d.menu("Choose an option", choices=self._dmenu_list_to_choices(self._menu_list), default_item=str(current_item), height=23, menu_height=17, cancel="Done")
				if code != DLG_OK:
					break
				current_item = int(menuitem)
				menuitem = self._menu_list[int(menuitem)-1]
				for item in self._fn:
					if menuitem == item['text']:
						item['fn']()
						current_item += 1
			self.install_profile_xml_file = None
		#Reset the Yes/No labels.
		d.add_persistent_args(["--yes-label", "Yes"])
		d.add_persistent_args(["--no-label","No"])
		if d.yesno(_(u"Do you want to save the InstallProfile XML file?")) == DLG_YES:
			self.install_profile_xml_file = self.save_install_profile()

# ------------------------------------------------------------------
if __name__ == '__main__':

	d = dialog.Dialog()
	client_profile = GLIClientConfiguration.ClientConfiguration()
	install_profile = GLIInstallProfile.InstallProfile()
	cc = GLIClientController.GLIClientController(pretend=False)
	exception_waiting = None
	client_config_xml_file = None
	install_profile_xml_file = None
	next_step_waiting = False
	install_done = False
	local_install = True
	advanced_mode = False
	networkless = False

	DLG_OK = 0
	DLG_YES = 0
	DLG_CANCEL = 1
	DLG_NO = 1
	DLG_ESC = 2
	DLG_ERROR = 3
	DLG_EXTRA = 4
	DLG_HELP = 5

	d.setBackgroundTitle("Gentoo Linux Installer")
	welcome_string = _(u"""Welcome to the Gentoo Linux Installer!  This program will help install Gentoo on your computer.
Before proceeding please thoroughly read the Gentoo Installation Handbook available at 
http://www.gentoo.org/doc/en/handbook/index.xml \n
This installer works by first asking a series of questions to generate an \"installation profile\",
which contains all the information needed to install Gentoo.\n
NO Changes will be made to your system until you select the "Install!" button.  
You can save your profile at any time by exiting the installer.
You can also load a previously made profile at any time.\n
If choosing expert mode, you will make a second profile with configuration settings for the livecd environment and the installer.\n
Press OK to continue""")
	d.msgbox(welcome_string, height=25, width=78, title="Welcome")

	#Change the Yes/No buttons to new labels for this question.
	d.add_persistent_args(["--yes-label", _(u"Simulate")])
	d.add_persistent_args(["--no-label", _(u"Real Install")])
	#This is a temporary question during the development process.  In a beta release a real install will be implied.
	if d.yesno(_(u"Are we performing an actual install or just simulating?"), width=45) == DLG_NO:
		cc._pretend = False
	else:
		cc._pretend = True
	
	#Set the Yes/No labels.
	d.add_persistent_args(["--yes-label", "Standard"])
	d.add_persistent_args(["--no-label","Advanced"])
	advanced_string = _(u"""This installer has two modes, an advanced mode for those knowledgable with the inner details of their computer and a standard mode where many of the defaults will be chosen for the user for simplicity and to speed up the install process.  The advanced mode offers full customizability and is required for generating profiles to be used other computers. \nThe advanced mode is recommended by the developers.
	""")
	if d.yesno(advanced_string, width=55, height=15) == DLG_NO:
		advanced_mode = True
		local_install = True
		
	networkless_string = _(u"Do you want to do a networkless installation?  This will limit the customizability of your install due to the limitations of the LiveCD.  For example, choosing networkless will set your installation stage, portage snapshot, and limit your extra packages selections.  NOTE: It is easily possible to do a networkless installation on a machine with an active Internet connection; in fact this may result in the fastest installations for many users.")
	#Change the Yes/No buttons
	d.add_persistent_args(["--yes-label", _(u"Networkless")])
	d.add_persistent_args(["--no-label", _(u"Internet enabled")])
	if d.yesno(networkless_string, width=65, height=20) == DLG_YES:
		networkless = True
	else:
		networkless = False


#Reset the Yes/No labels.
	d.add_persistent_args(["--yes-label", "Yes"])
	d.add_persistent_args(["--no-label","No"])
	if advanced_mode:
		#Local install affects the pre-selection of partitions on the local hard drives, amongst other things.
		if d.yesno(_(u"Are the profiles being generated to be used for an install on the current computer?")) == DLG_NO:
			local_install = False
	#Ask 
		while 1:
			string = _(u"""
The first profile needed for an advanced install includes all the 
necessary information for getting the livecd environment set up.  
This includes the livecd networking configuration, where the 
logfile and new root mount point are to be located, etc.  
We call this the ClientConfiguration profile.
Do you have a previously generated XML file for the ClientConfiguration?
""")
			if d.yesno(string, width=70, height=15, defaultno=1) == DLG_YES:
				code, client_config_xml_file = d.inputbox(_(u"Enter the filename of the XML file"))
				if code != DLG_OK: 
					break
				if GLIUtility.is_file(client_config_xml_file): 
					break
				d.msgbox(_(u"Cannot open file ") + client_config_xml_file, height=7, width=50)
				client_config_xml_file = None
				continue
			else:
				break
			
	if client_config_xml_file != None:
		client_profile.parse(client_config_xml_file)
	# code to actually run the client_controller functions
	else:
		#This line does all the work.
		gen_client_conf = Setup_CConfig(client_profile, local_install, advanced_mode, networkless)
		client_profile = gen_client_conf.client_profile()
			
	client_profile.set_interactive(None, True, None)
	cc.set_configuration(client_profile)

	#This will execute all of the CC functions, and set up networking if there is networking to set up.
	cc.start_pre_install()
	
	#Reset the Yes/No labels.
	d.add_persistent_args(["--yes-label", "Yes"])
	d.add_persistent_args(["--no-label","No"])
	while 1:
		if d.yesno(_(u"All of the installation settings are stored in an XML file, which we call the InstallProfile.  If you have previously saved a profile and would like to load it for this install, say Yes.  Otherwise say No.  Do you have a previously generated InstallProfile XML file?"), width=55, defaultno=1) == DLG_YES:
			code, install_profile_xml_file = d.inputbox(_(u"Enter the filename of the XML file"))
			if code != DLG_OK: 
				break
			if GLIUtility.is_file(install_profile_xml_file): 
				break
			d.msgbox(_(u"Cannot open file ") + install_profile_xml_file, height=7, width=50)
			install_profile_xml_file = None
		else:
			break
	skip_wizard_question = False
	if install_profile_xml_file != None:
		install_profile.parse(install_profile_xml_file)
		skip_wizard_question = True
	
	#These are always done
	
	gen_install_profile = Setup_InstallProfile(client_profile, install_profile, local_install, advanced_mode, skip_wizard_question, networkless)
	install_profile = gen_install_profile.install_profile()
	

# INSTALLATION TIME
	current_item = 0
	while 1:
		cc.set_install_profile(install_profile)
		cc.start_install()
		d.gauge_start(_(u"Installation Started!"), title=_(u"Installation progress"))
		num_steps_completed = 1
		next_step = 0
		num_steps = 0
		i = 0
		while 1:
			notification = cc.getNotification()
			if notification == None:
				time.sleep(1)
				continue
			type_r = notification.get_type()
			data = notification.get_data()
			if type_r == "exception":
				#Reset the Yes/No labels.
				d.add_persistent_args(["--yes-label", "Yes"])
				d.add_persistent_args(["--no-label","No"])
				if d.yesno(_(u"There was an Exception received during the install that is outside of the normal install errors.  This is a bad thing. The error was:")+ str(data) + _(u"\nPlease submit a bug report (after searching to make sure it's not a known issue and verifying you didn't do something stupid) with the contents of /var/log/install.log and /tmp/installprofile.xml and the version of the installer you used\nDo you want to cleanup your system to attempt another install?"), width=70) == DLG_YES:
					cc.start_failure_cleanup()
			elif type_r == "progress":
				#SECONDARY UPDATIN' GOIN ON IN HERE
				diff = (data[0]*100)/num_steps
				d.gauge_update(i+diff, "On step %d of %d. Current step: %s\n%s" % (num_steps_completed, num_steps, next_step, data[1]), update_text=1)
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
					d.gauge_update(100, _(u"Install completed!"), update_text=1)
					d.gauge_stop()
					print _(u"Install done!")
					sys.exit(0)
