"""
Gentoo Linux Installer

$Id: GLIClientController.py,v 1.55 2005/05/03 02:17:46 agaffney Exp $
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

TEMPLATE_DIR = 'templates'

##
# This class provides an interface between the backend and frontend
class GLIClientController(Thread):

	##
	# Initialization function for the GLIClientController class
	# @param configuration=None GLIClientConfiguration object
	# @param install_profile=None GLIInstallProfile object
	# @param pretend=False Pretend mode. If pretending, no steps will actually be performed
	def __init__(self,configuration=None,install_profile=None,pretend=False):
		Thread.__init__(self)

		self._verbose = True

		if configuration == None and os.path.isfile('/etc/gli.conf'):
			self.output("Using /etc/gli.conf...")
			configuration = GLIClientConfiguration.ClientConfiguration()
			configuration.parse('/etc/gli.conf')

		self.set_install_profile(install_profile)
		self.set_configuration(configuration)
		self._install_event = Event()
		self._notification_queue = Queue.Queue(50)
		self._install_step = -1
		self._install_steps = None
		self._pretend = pretend
		self.setDaemon(True)

	##
	# Sets the GLIInstallProfile object
	# @param install_profile GLIInstallProfile object
	def set_install_profile(self, install_profile):
		self._install_profile = install_profile

	##
	# Returns the GLIInstallProfile object
	def get_install_profile(self):
		return self._install_profile

	##
	# Sets the GLIClientConfiguration object
	# @param configuration GLIClientConfiguration object
	def set_configuration(self, configuration):
		self._configuration = configuration
		if self._configuration != None:
			self._verbose = self._configuration.get_verbose()
			self._logger = GLILogger.Logger(self._configuration.get_log_file())

	##
	# Returns the GLIClientConfiguration object
	def get_configuration(self):
		return self._configuration

	##
	# This function runs as a second thread to do the actual installation (only used internally)
	def run(self):
		interactive = self._configuration.get_interactive()

		if self._configuration == None and not interactive and not self._pretend:
			print "You can not do a non-interactive install without a ClientConfiguration!"
			sys.exit(1)

		steps = [self.load_kernel_modules, self.set_proxys, self.set_root_passwd, self.configure_networking, self.enable_ssh, self.start_portmap]
		# Do Pre-install client-specific things here.
		while len(steps) > 0:
			try:
				step = steps.pop(0)
				if not self._pretend:
					step()
			except GLIException, error:
				if error.get_error_level() != 'fatal':
					self._logger.log("Error: "+ error.get_function_name() + ": " + error.get_error_msg())
					self.output("Non-fatal error... continuing...")
				else:
					raise error

		# Wait for the self._install_event to be set before starting the installation.
		# start_install() is called to pass here
		self._install_event.wait()
		self._install_event.clear()

		if self._install_profile == None and not interactive:	
			print "You can not do a non-interactive install without an InstallProfile!"
			sys.exit(1)

		#self.output("Starting install now...")

		templates = {	'x86':		'x86ArchitectureTemplate',
				'sparc':	'sparcArchitectureTemplate',
				'amd64':	'amd64ArchitectureTemplate',
				'mips':		'mipsArchitectureTemplate',
				'hppa':		'hppaArchitectureTemplate',
				'alpha':	'alphaArchitectureTemplate',
				'ppc':		'ppcArchitectureTemplate',
				'ppc64':	'ppc64ArchitectureTemplate'
			}
				
		if self._configuration.get_architecture_template() not in templates.keys():
			self.addNotification(GLINotification("exception", UnsupportedArchitectureError('fatal', 'run', self._configuration.get_architecture_template() + ' is not supported by the Gentoo Linux Installer!')))

		try:
			template = __import__(TEMPLATE_DIR + '/' + templates[self._configuration.get_architecture_template()])
			self._arch_template = getattr(template, templates[self._configuration.get_architecture_template()])(self._configuration, self._install_profile, self._pretend)
		except ImportError:
			self.addNotification(GLINotification("exception", UnsupportedArchitectureError('fatal', 'run', 'The Gentoo Linux Installer could not import the install template for this architecture!')))
		except AttributeError:
			self.addNotification(GLINotification("exception", UnsupportedArchitectureError('fatal', 'run', 'This architecture template was not defined properly!')))

		self._install_steps = self._arch_template.get_install_steps()
		self.addNotification("int", NEXT_STEP_READY)
#		self._install_event.wait()

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
					self._logger.log("Exception received during '" + self._install_steps[self._install_step][1] + "': " + error)
					self.addNotification("exception", error)
					self._install_event.clear()
				except Exception, error:
					# Something very bad happened
					self._logger.log("This is a bad thing. An exception occured outside of the normal install errors. The error was: '" + error + "'")
					self.addNotification("exception", error)
					self._install_event.clear()
			else:
				break

		# This keeps the thread running until the FE exits
		self._install_event.clear()
		self._install_event.wait()

	##
	# Returns the number of steps in the install process
	def get_num_steps(self):
		return len(self._install_steps)

	##
	# Returns information about the next install step
	def get_next_step_info(self):
		return self._install_steps[(self._install_step + 1)][1]

	##
	# Performs the next install step
	def next_step(self):
		self._install_step = self._install_step + 1
		self._install_event.set()

	##
	# Retries the current install step
	def retry_step(self):
		self._install_event.set()

	##
	# Returns True if there are more install steps remaining
	def has_more_steps(self):
		return (self._install_step < (len(self._install_steps) - 1))

	##
	# Sets proxy information from the environment
	def set_proxys(self):
		if self._configuration.get_ftp_proxy() != "":
			os.environ['FTP_PROXY'] = self._configuration.get_ftp_proxy()

		if self._configuration.get_http_proxy() != "":
			os.environ['HTTP_PROXY'] = self._configuration.get_http_proxy()

		if self._configuration.get_rsync_proxy() != "":
			os.environ['RSYNC_PROXY'] = self._configuration.get_rsync_proxy()

	##
	# Loads kernel modules specified in the GLIClientConfiguration object
	def load_kernel_modules(self):
		modules = self._configuration.get_kernel_modules()
		for module in modules:
			try:
				ret = GLIUtility.spawn('modprobe ' + module, quiet=True)
				if not GLIUtility.exitsuccess(ret):
					self._logger.log("ERROR! : Could not load module: "+module)
				#	raise GLIException("KernelModuleError", 'warning', 'load_kernel_modules', 'Could not load module: ' + module)
				else:
					self._logger.log('kernel module: ' + module + ' loaded.')
			except KernelModuleError, error:
				self.output(error)
				self._logger.log(error.get_error_level() + '! ' + error.get_error_msg())

	##
	# Sets the root password specified in the GLIClientConfiguration object
	def set_root_passwd(self):
		self._logger.log("Setting root password.")
		if self._configuration.get_root_passwd() != "":
			# The password specified in the configuration is encrypted.
			status = GLIUtility.spawn('echo "root:' + self._configuration.get_root_passwd() + '" | chpasswd -e',quiet=True)
	
			if not GLIUtility.exitsuccess(status):
				self._logger.log("ERROR! : Could not set the root password on the livecd environment!")
			#	raise GLIException("PasswordError", 'warning', 'set_root_passwd', "Could not set the root password!")
			else:
				self._logger.log("Livecd root password set.")

	##
	# Starts portmap if specified in the GLIClientConfiguration object
	def start_portmap(self):
		status = GLIUtility.spawn('/etc/init.d/portmap start') #, display_on_tty8=True)
		if not GLIUtility.exitsuccess(status):
			self._logger.log("ERROR! : Could not start the portmap service!")
		#	raise GLIException("PortmapError", 'warning', 'start_portmap', "Could not start the portmap service!")
		else:
			self._logger.log("Portmap started.")

	##
	# Configures networking as specified in the GLIClientConfiguration object
	def configure_networking(self):
		# Do networking setup right here.
		if self._configuration.get_network_type() != None:
			type = self._configuration.get_network_type()
			if type == "dhcp":
				# Run dhcpcd.
				try:
					interface = self._configuration.get_network_interface()
				except:
					self._logger.log("No interface found.. defaulting to eth0.")
					interface = "eth0"

				if interface:
					status = GLIUtility.spawn("dhcpcd -n " + interface, quiet=True)
				else:
					status = GLIUtility.spawn("dhcpcd -n", quiet=True)

				if not GLIUtility.exitsuccess(status):
					raise GLIException("DHCPError", 'fatal', 'configure_networking', "Failed to get a dhcp address for " + interface + ".")

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
				net_interface = self._configuration.get_network_interface()
				net_ip        = self._configuration.get_network_ip()
				net_broadcast = self._configuration.get_network_broadcast()
				net_netmask   = self._configuration.get_network_netmask()
				if not GLIUtility.set_ip(net_interface, net_ip, net_broadcast, net_netmask):
					raise GLIException("SetIPError", 'fatal', 'configure_networking', "Could not set the IP address!")

				route = self._configuration.get_network_gateway()
				if not GLIUtility.set_default_route(route):
					raise GLIException("DefaultRouteError", 'fatal','configure_networking', "Could not set the default route!")

	##
	# Enables SSH if specified in the GLIClientConfiguration object
	def enable_ssh(self):
		if self._configuration.get_enable_ssh():
			status = GLIUtility.spawn("/etc/init.d/sshd start", quiet=True)
			if not GLIUtility.exitsuccess(status):
				self._logger.log("ERROR! : Could not start the SSH daemon!")
			#	raise GLIException("SSHError", 'warning','enable_ssh',"Could not start SSH daemon!")
			else:
				self._logger.log("SSH Started.")



	##
	# Loads the install profile
	def load_install_profile(self):
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
					raise GLIException("InstallProfileError", 'fatal', 'get_install_profile', 'Could not download/copy the install profile from: ' + self._configuration.get_profile_uri())

		self._install_profile = install_profile

	##
	# Starts the install
	def start_install(self):
		self._install_event.set()

	##
	# Starts the secondary thread running. The thread will wait to continue until start_install() is called
	def start_pre_install(self):
		self.start()

	##
	# Displays specified output
	# @param str String to display
	def output(self, str):
		if self._verbose:
			print str

	##
	# Returns a notification object from the queue
	def getNotification(self):
		notification = None
		try:
			notification = self._notification_queue.get_nowait()
		except:
			pass
		return notification

	##
	# Adds a notification object to the queue
	# @param type Notification type
	# @param data Notification contents
	def addNotification(self, type, data):
		notification = GLINotification.GLINotification(type, data)
		try:
			self._notification_queue.put_nowait(notification)
		except:
			# This should only ever happen if the frontend is not checking for notifications
			pass
