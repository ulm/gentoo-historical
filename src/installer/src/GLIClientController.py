"""
Gentoo Linux Installer

$Id: GLIClientController.py,v 1.29 2004/11/23 05:35:42 agaffney Exp $
Copyright 2004 Gentoo Technologies Inc.

Steps (based on the ClientConfiguration):
	1. Load any modules?  (this may have to be done manually, using a shell - not implemented)
	2. Set the root password (may need to generate one. GLIUtility.generate_random_password())
	3. Add users? (not implemented yet)
	4. Start ssh
	5. Network setup
	6. Start the ArchTemplate doing it's thing. - maybe.. this might get called from elsewhere

"""

import os, GLIClientConfiguration, GLIInstallProfile, GLIUtility, GLILogger, sys, signal, Queue, GLIArchitectureTemplate, GLINotification
from GLIException import *
from threading import Thread, Event

# Global constants for notifications
NEXT_STEP_READY = 1
INSTALL_DONE = 2

class GLIClientController(Thread):

	def __init__(self,configuration=None,install_profile=None,pretend=False):
		Thread.__init__(self)
		if configuration == None and os.path.isfile('/etc/gli.conf'):
			self.output("Using /etc/gli.conf...")
			configuration = GLIClientConfiguration.ClientConfiguration()
			configuration.parse('/etc/gli.conf')

		self.set_install_profile(install_profile)
		self.set_configuration(configuration)
		self._install_event = Event()
		self._notification_queue = Queue.Queue(50)
		self._install_step = -1
		self._pretend = pretend
		self.setDaemon(True)

	def set_install_profile(self, install_profile):
		self._install_profile = install_profile

	def get_install_profile(self):
		return self._install_profile

	def set_configuration(self, configuration):
		self._configuration = configuration
		if self._configuration != None:
			self._verbose = self._configuration.get_verbose()
			self._logger = GLILogger.Logger(self._configuration.get_log_file())

	def get_configuration(self):
		return self._configuration

	def run(self):
		interactive = self._configuration.get_interactive()

		if self._configuration == None and not interactive and not self._pretend:
			print "You can not do a non-interactive install without a ClientConfiguration!"
			sys.exit(1)

		steps = [self.load_kernel_modules, self.set_proxys, self.set_root_passwd, self.configure_networking, self.get_install_profile, self.enable_ssh]
		# Do Pre-install client-specific things here.
		while len(steps) > 0:
			try:
				step = steps.pop(0)
				if not self._pretend:
					step()
			except GLIException, error:
				if error.get_error_level() != 'fatal':
					self._logger.log("Error:", error.get_function_name() + ": " + error.get_error_msg())
					self.output("Non-fatal error... continuing...")
				else:
					raise error

		# Wait for the self._install_event to be set before starting the installation.
		self._install_event.wait()

		if self._install_profile == None and not interactive:	
			print "You can not do a non-interactive install without an InstallProfile!"
			sys.exit(1)

		self.output("Starting install now...")

		self.addNotification("int", NEXT_STEP_READY)
		self._install_event.wait()
		self._arch_template = GLIArchitectureTemplate.ArchitectureTemplate(configuration=self._configuration, install_profile=self._install_profile)
		self._install_steps = self._arch_template.get_install_steps()
		while 1:
			self._install_event.wait()
			if self._install_step <= (len(self._install_steps) - 1):
				try:
					if not self._pretend:
						self._install_steps[self._install_step][0]()
					self._install_event.clear()
					if self.has_more_steps():
						self.addNotification("int", NEXT_STEP_READY)
					else:
						self.addNotification("int", INSTALL_DONE)
				except GLIException, error:
					self.addNotification("exception", error)
					self._install_event.clear()
			else:
				break

	def get_next_step_info(self):
		return self._install_steps[(self._install_step + 1)][1]

	def next_step(self):
		self._install_step = self._install_step + 1
		self._install_event.set()

	def retry_step(self):
		self._install_event.set()

	def has_more_steps(self):
		return (self._install_step < (len(self._install_steps) - 1))

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
				ret = GLIUtility.spawn('modprobe ' + module, quiet=True)
				if not GLIUtility.exitsuccess(ret):
					raise KernelModuleError('warning', 'load_kernel_modules', 'Could not load module: ' + module)
				else:
					self._logger.log('kernel module: ' + module + ' loaded.')
			except KernelModuleError, error:
				self.output(error)
				self._logger.log(error.get_error_level() + '! ' + error.get_error_msg())

	def set_root_passwd(self):
		self._logger.log("Setting root password.")
		if self._configuration.get_root_passwd() == "":
			passwd = GLIUtility.generate_random_password()
			status = GLIUtility.spawn('echo "root:' + passwd + '" | chpasswd',quiet=True)
		else:
			# The password specified in the configuration is encrypted.
			status = GLIUtility.spawn('echo "root:' + self._configuration.get_root_passwd() + '" | chpasswd -e',quiet=True)
	
		if not GLIUtility.exitsuccess(status):
			raise PasswordError('warning', 'set_root_passwd()',"Could not set the root password!")

	def configure_networking(self):
		# Do networking setup right here.
		if self._configuration.get_network_type() != None:
			type = self._configuration.get_network_type()
			if type == "dhcp":
				# Run dhcpcd.
				net_data = self._configuration.get_network_data()
				try:
					interface = net_data[0]
				except:
					self._logger.log("No interface found.. defaulting to eth0.")
					interface = "eth0"

				if interface:
					status = GLIUtility.spawn("dhcpcd " + interface, quiet=True)
				else:
					status = GLIUtility.spawn("dhcpcd", quiet=True)

				if not GLIUtility.exitsuccess(status):
					raise DHCPError('fatal', 'configure_networking', "Failed to get a dhcp address for " + interface + ".")

			elif type == "manual" and self._configuration.get_interactive():
				# Drop to bash shell and let them configure it themselves
				print "Please configure & test your network device."
				GLIUtility.spawn_bash()
			elif type == "manual" and not self._interactive.get_interactive():
				print "You cannot manually configure the network in non-interactive mode!"
				print "Please fix either the network settings or the interactive mode!"
				sys.exit(1)
			elif type == "static":
				# Configure the network from the settings they gave.
				net_data = self._configuration.get_network_data()
				if not GLIUtility.set_ip(net_data[0], net_data[1], net_data[2], net_data[3]):
					raise SetIPError('fatal', 'configure_networking', "Could not set the IP address!")

				route = self._configuration.get_default_gateway()[1]
				if not GLIUtility.set_default_route(route):
					raise DefaultRouteError('fatal','configure_networking', "Could not set the default route!")

	def enable_ssh(self):
		if self._configuration.get_enable_ssh():
			status = GLIUtility.spawn("/etc/init.d/sshd start", quiet=True)
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
					self.output("Profile downloaded... loading it now...")
					install_profile = GLIInstallProfile.InstallProfile()
					install_profile.parse('/tmp/install_profile.xml')
				else:
					raise InstallProfileError('fatal', 'get_install_profile', 'Could not download/copy the install profile from: ' + self._configuration.get_profile_uri())

		self._install_profile = install_profile

	def start_install(self):
		self._install_event.set()

	def start_pre_install(self):
		self.start()

	def output(self, str):
		if self._verbose:
			print str

	def getNotification(self):
		notification = None
		try:
			notification = self._notification_queue.get_nowait()
		except:
			pass
		return notification

	def addNotification(self, type, data):
		notification = GLINotification.GLINotification(type, data)
		try:
			self._notification_queue.put_nowait(notification)
		except:
			# This should only ever happen if the frontend is not checking for notifications
			pass
#		os.kill(os.getpid(), signal.SIGUSR1)

