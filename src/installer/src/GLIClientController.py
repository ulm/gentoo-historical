"""
Gentoo Linux Installer

$Id: GLIClientController.py,v 1.10 2004/08/25 21:42:13 samyron Exp $
Copyright 2004 Gentoo Technologies Inc.

Steps (based on the ClientConfiguration):
	1. Load any modules?  (this may have to be done manually, using a shell - not implemented)
	2. Set the root password (may need to generate one. GLIUtility.generate_random_password())
	3. Add users? (not implemented yet)
	4. Start ssh
	5. Network setup
	6. Start the ArchTemplate doing it's thing. - maybe.. this might get called from elsewhere

"""

import os, GLIClientConfiguration, GLIInstallProfile, GLIUtility, GLILogger, sys
from GLIException import *
from threading import Thread, Event

class GLIClientController(Thread):

	def __init__(self,configuration=None,install_profile=None):
		Thread.__init__(self)
		if configuration == None and os.path.isfile('/etc/gli.conf'):
			print "Using /etc/gli.conf..."
			configuration = GLIClientConfiguration.ClientConfiguration()
			configuration.parse('/etc/gli.conf')

		self._install_profile = install_profile
		self._configuration = configuration
		self._logger = GLILogger.Logger(self._configuration.get_log_file())
		self._install_event = Event()

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
			print "You can not do a non-interactive install without a ClientConfiguration!"
			sys.exit(1)

		steps = [self.load_kernel_modules, self.set_proxys, self.set_root_passwd, self.configure_networking, self.get_install_profile, self.enable_ssh]
		# Do Pre-install client-specific things here.
		while len(steps) > 0:
			try:
				step = steps.pop(0)
				step()
			except GLIException, error:
				if error.get_error_level() != 'fatal':
					self._logger.log("Error:", error.get_function_name() + ": " + error.get_error_msg())
					print "Non-fatal error... continuing..."
				else:
					raise error

		# Wait for the self._install_event to be set before starting the installation.
		self._install_event.wait()

		if self._install_profile == None and not interactive:	
			print "You can not do a non-interactive install without an InstallProfile!"
			sys.exit(1)

		print "Starting install now..."

	def set_proxys(self):
		if self._configuration.get_ftp_proxy() != "":
			os.environ['FTP_PROXY'] = self._configuration.get_ftp_proxy()

		if self._configuration.get_http_proxy() != "":
			os.environ['HTTP_PROXY'] = self._configuration.get_http_proxy()

		if self._configuration.get_rsync_proxy() != "":
			os.environ['RSYNC_PROXY'] = self._configuration.get_rsync_proxy()

	def load_kernel_modules(self):
		modules = self._configuration.get_kernel_modules()
		for module in modules:
			try:
				ret = GLIUtility.run_cmd('modprobe ' + module, quiet=True)
				if not GLIUtility.exitsuccess(ret):
					raise KernelModuleError('warning', 'load_kernel_modules', 'Could not load module: ' + module)
				else:
					self._logger.log('kernel module: ' + module + ' loaded.')
			except KernelModuleError, error:
				print error
				self._logger.log(error.get_error_level() + '! ' + error.get_error_msg())

	def set_root_passwd(self):
		self._logger.log("Setting root password.")
		if self._configuration.get_root_passwd() == "":
			passwd = GLIUtility.generate_random_password()
			status = GLIUtility.run_cmd('echo "root:' + passwd + '" | chpasswd',quiet=True)
		else:
			# The password specified in the configuration is encrypted.
			status = GLIUtility.run_cmd('echo "root:' + self._configuration.get_root_passwd() + '" | chpasswd -e',quiet=True)
	
		if not GLIUtility.exitsuccess(status):
			raise PasswordError('warning', 'set_root_passwd()',"Could not set the root password!")

	def configure_networking(self):
		# Do networking setup right here.
		if self._configuration.get_network_type() != None:
			type = self._configuration.get_network_type()
			if type == "dhcp":
				# Run dhcpcd.
				net_info = self._configuration.get_network_info()
				try:
					interface = net_info[0]
				except:
					self._logger.log("No interface found.. defaulting to eth0.")
					interface = "eth0"

				if interface:
					status = GLIUtility.run_cmd("dhcpcd " + interface, quiet=True)
				else:
					status = GLIUtility.run_cmd("dhcpcd", quiet=True)

				if not GLIUtility.exitsuccess(status):
					raise DHCPError('fatal', 'configure_networking', "Failed to get a dhcp address for " + interface + ".")

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
					raise SetIPError('fatal', 'configure_networking', "Could not set the IP address!")

				route = self._configuration.get_default_gateway()[1]
				if not GLIUtility.set_default_route(route):
					raise DefaultRouteError('fatal','configure_networking', "Could not set the default route!")

	def enable_ssh(self):
		if self._configuration.get_enable_ssh():
			status = GLIUtility.run_cmd("/etc/init.d/sshd start", quiet=True)
			if not GLIUtility.exitsuccess(status):
				raise SSHError('warning','enable_ssh',"Could not start SSH daemon!")
			else:
				self._logger.log("SSH Started.")



	def get_install_profile(self):
		install_profile=None
		if self._install_profile == None:
			if self._configuration != None:
				success = GLIUtility.get_uri(self._configuration.get_profile_uri(),'/tmp/install_profile.xml')
				if success:
					self._logger.log("Profile downloaded succesfully, loading it now.")
					print "Profile downloaded... loading it now..."
					install_profile = GLIInstallProfile.InstallProfile()
					install_profile.parse('/tmp/install_profile.xml')
				else:
					raise InstallProfileError('fatal', 'get_install_profile', 'Could not download/copy the install profile from: ' + self._configuration.get_profile_uri())

		self._install_profile = install_profile

	def start_install(self):
		self._install_event.set()
