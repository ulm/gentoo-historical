"""
Gentoo Linux Installer

$Id: GLIClientController.py,v 1.3 2004/08/11 16:14:43 samyron Exp $
Copyright 2004 Gentoo Technologies Inc.

"""

import os, GLIClientConfiguration, GLIInstallProfile, GLIUtility

class GLIClientController:
	def __init__(self,configuration=None,install_profile=None,configuration_generator=None,install_profile_generator=None):

		if configuration == None and os.path.isfile('/etc/gli.conf'):
			print "Using /etc/gli.conf..."
			configuration = GLIClientConfiguration.ClientConfiguration()
			configuration.parse('/etc/gli.conf')
		elif configuration == None:
			if configuration_generator != None:
				configuration = configuration_generator()
			else:
				print "Configuration file not found and no function given to generate a valid configuration."

		if install_profile == None:
			if configuration != None:
				success = GLIUtility.get_uri(configuration.get_profile_uri(),'/tmp/install_profile.xml')
				if success:
					print "Profile downloaded succesfully, loading it now."
					install_profile = GLIInstallProfile.InstallProfile()
					install_profile.parse('/tmp/install_profile.xml')
				else:
					print "The installer could not download the profile specified by:", self._configuration.get_profile_uri() + "."
					# Generate one, if we can
					if install_profile_generator != None:
						install_profile = install_profile_generator()
			else:
				if install_profile_generator != None:
					install_profile = install_profile_generator()				

		self._install_profile = install_profile
		self._configuration = configuration
		self._install_profile_generator = install_profile_generator
		self._configuration_generator = configuration_generator

	def set_install_profile(self, install_profile):
		self._install_profile = install_profile

	def get_install_profile(self):
		return self._install_profile

	def set_configuration(self, configuration):
		self._configuration = configuration

	def get_configuration(self):
		return self._configuration

	def run(self):
		# This method will use the InstallProfile to install the system with the specified options. The 
		# configuration comes later, with execute_profile()
		pass

	def execute_profile(self):
		# This method will use the InstallProfile to apply the specified options. It is basically the 
		# configuration after the machine has been installed.
		pass

if __name__ == '__main__':
	controller = GLIClientController()
	controller.run()
