"""
Gentoo Linux Installer

$Id: GLIClientController.py,v 1.4 2004/08/17 15:32:04 samyron Exp $
Copyright 2004 Gentoo Technologies Inc.

Steps (based on the ClientConfiguration):
	1. Load any modules?  (this may have to be done manually, using a shell - not implemented)
	2. Set the root password (may need to generate one. GLIUtility.generate_random_password())
	3. Add users? (not implemented yet)
	4. Start ssh
	5. Network setup
	6. Start the ArchTemplate doing it's thing. - maybe.. this might get called from elsewhere

"""

import os, GLIClientConfiguration, GLIInstallProfile, GLIUtility, sys

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
		interactive = self._configuration.get_interactive()

		if self._configuration == None and not interactive:
			print "You cannot do a non-interactive install without a ClientConfiguration!"
			sys.exit(1)
		elif self._install_profile == None and not interactive:
			print "You can't do a non-interactive install without an InstallProfile!"
			sys.exit(1)

	def set_root_passwd(self):
		print "GLI: Setting root password."
		if self._configuration.get_root_passwd() == "":
			passwd = GLIUtility.generate_random_password()
			status = GLIUtility.run_cmd('echo "root:' + passwd + '" | chpasswd',quiet=True)
		else:
			# The password specified in the configuration is encrypted.
			status = GLIUtility.run_cmd('echo "root:' + self._configuration.get_root_passwd() + '" | chpasswd -e',quiet=True)
	
		if not GLIUtility.exitsuccess(status):
			raise "PasswordError","Could not set the root password!"

	def configure_networking(self):
		# Do networking setup right here.
		if self._configuration.get_network_type() != "none":
			type = self._configuration.get_network_type()
			if type == "dhcp":
				# Run dhcpcd.
				net_info = self._configuration.get_network_info()
				interface = net_info[0]
				if interface:
					status = GLIUtility.run_cmd("dhcpcd " + interface, quiet=True)
				else:
					status = GLIUtility.run_cmd("dhcpcd", quiet=True)

				if not GLIUtility.exitsuccess(status):
					raise "DHCPError", "Failed to get a dhcp address for " + interface + "."

			elif type == "manual" and self._configuration.get_interactive():
				# Drop to bash shell and let them configure it themselves
				print "Please configure & test your network device."
				GLIUtility.run_bash()
			elif type == "manual" and not self._interactive.get_interactive():
				print "You cannot manually configure the network in non-interactive mode!"
				print "Please fix either the network settings or the interactive mode!"
				sys.exit(1)
			elif type == "static":
				# Configure the network from the settings they gave.
				net_info = self._configuration.get_network_info()
				if not GLIUtility.set_ip(net_info[0], net_info[1], net_info[2], net_info[3]):
					raise "SetIPError", "Could not set the IP address!"

				route = self._configuration.get_default_gateway()[1]
				if not GLIUtility.set_default_route(route):
					raise "DefaultRouteError", "Could not set the default route!"

	def enable_ssh(self):
		if self._configuration.get_enable_ssh():
			status = GLIUtility.run_cmd("/etc/init.d/sshd start", quiet=True)
			if not GLIUtility.exitsuccess(status):
				raise "SSHError","Could not start SSH daemon"
			else:
				print "GLI: SSH Started."



	def execute_profile(self):
		pass

if __name__ == '__main__':
	controller = GLIClientController()
	controller.run()
