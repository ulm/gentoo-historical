"""
Gentoo Linux Installer

$Id: GLIArchitectureTemplate.py,v 1.2 2004/08/31 15:34:34 samyron Exp $
Copyright 2004 Gentoo Technologies Inc.


The ArchitectureTemplate is largely meant to be an abstract class and an 
interface (yes, it is both at the same time!). The purpose of this is to create 
subclasses that populate all the methods with working methods for that architecture. 
The only definitions that are filled in here are architecture independent. 

"""

import GLIUtility
from GLIExceptions import *

class ArchitectureTemplate:

	def __init__(self,configuration=None, install_profile=None):
		self._configuration = configuration
		self._install_profile = install_profile

		# These must be filled in by the subclass. _steps is a list of
		# functions, that will carry out the installation. They must be
		# in order.
		#
		# For example, self._steps might be: [preinstall, stage1, stage2, stage3, postinstall],
		# where each entry is a function (with no arguments) that carries out the desired actions.
		# Of course, steps will be different depending on the install_profile

		self._steps = []
		self._architecture_name = "generic"
		
        def _depends(self, depends):
		# Type checking
		if type(depends) not in [ list, str, tuple ]:
			raise "Dependencies must be a string or a list of strings"

		# If it is a string, change it to a list for parsing
		if type(depends) == str:
			depends = [ depends ]

		# Parse dependencies
		for dependency in depends:
			# If the dependency has not been satisfied, check to see if 'ignore' has been turned on
			if not dependency in self._client_configuration.install_steps_completed:

				#If ignore is on, just print a warning
				if self._install_profile.get_ignore_install_step_depends():
					print "Warning: You chose to ignore install step dependencies.  The " + dependency + " was not met.  Ignoring."
				#If ignore is off, then raise exception
				else:
					raise "InstallTemplateError",  "Install step dependency not met!"

	# It is possible to override these methods in each Arch Template.
	# It might be necessary to do so, if the arch needs something 'weird'.

	def stage1(self):
		"Stage 1 install -- bootstraping"
		# Dependency checking
		self._depends("preinstall")

		# If we are doing a stage 1 install, then bootstrap 
		if self._install_profile.get_install_stage() == 1:
			exitstatus = GLIUtility.spawn("/usr/portage/scripts/bootstrap.sh", True)
			if not GLIUtility.exitsuccess(exitstatus):
				raise Stage1Error('fatal','stage1', "Bootstrapping failed!")

		self._configuration.add_install_steps_completed("stage1")

	def stage2(self):
		# Dependency checking
		self._depends("stage1")

		# If we are doing a stage 1 or 2 install, then emerge system
		if self._install_profile.get_install_stage() in [ 1, 2 ]:
			exitstatus = GLIUtility.emerge("system")
			if not GLIUtility.exitsuccess(exitstatus):
				raise Stage2Error('fatal','stage2', "Building the system failed!")

		self._configuration.add_install_steps_completed("stage2")

	def preinstall(self):
		if not os.path.isdir(self._configuration.get_root_mount_point()):
			os.makedirs(self._configuration.get_root_mount_point()):

		# Fetch and unpack the stage tarball here.
		GLIUtility.fetch_and_unpack_tarball(self._install_profile.get_stage_tarball_uri(), self._configuration.get_root_mount_point(),keep_permissions=True)

		ret = GLIUtility.spawn("cp -L /etc/resolv.conf /mnt/gentoo/etc/resolv.conf",True)
		if not GLIUtility.exitsuccess(ret):
			raise CopyError('warning','preinstall','Could not copy resolv.conf!',True)

		ret = GLIUtility.spawn("mount -t proc none /mnt/gentoo /proc")
		if not GLIUtility.exitsuccess(ret):
			raise MountError('fatal','preinstall','Could not mount /proc')

		# Set USE flags here
		# might want to rewrite/use _edit_config from the GLIInstallTemplate
		# Then you should be done... at least with the preinstall.

	# This is part of the interface... subclasses MUST
	# provide these methods filled in.
	def stage3(self):
		# This should probably start with building the kernel,
		# that might be the only thing this actually needs
		# to do.
		pass

	def postinstall(self):
		pass

	def partition(self):
		pass
