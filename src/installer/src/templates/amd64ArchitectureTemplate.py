"""
Gentoo Linux Installer

$Id: amd64ArchitectureTemplate.py,v 1.3 2005/03/30 05:27:48 agaffney Exp $
Copyright 2004 Gentoo Technologies Inc.


This fills in amd64 specific functions.
"""

import GLIUtility, string
#from GLIArchitectureTemplate import ArchitectureTemplate
from x86ArchitectureTemplate import x86ArchitectureTemplate
from GLIException import *
import parted

class amd64ArchitectureTemplate(x86ArchitectureTemplate):
        def __init__(self,configuration=None, install_profile=None, client_controller=None):
		x86ArchitectureTemplate.__init__(self, configuration, install_profile, client_controller)
		self._architecture_name = 'amd64'
	#	self._kernel_bzimage = "arch/i386/boot/bzImage"  I don't think this is used anywhere

	"""
	def install_bootloader(self):
		"Installs and configures bootloader"
		#
		# THIS IS ARCHITECTURE DEPENDANT!!!
		# This is the amd64 way.. it uses grub but must do it staticly.
		
		if self._install_profile.get_boot_loader_pkg():
			exitstatus = self._emerge(self._install_profile.get_boot_loader_pkg())
			if exitstatus != 0:
				raise GLIException("BootLoaderEmergeError", 'fatal', 'install_bootloader', "Could not emerge bootloader!")
		else:
			pass
		
		if self._install_profile.get_boot_loader_pkg() == "grub":
			self._install_grub()
		else:
			raise Exception("BootLoaderError",'fatal','install_bootloader',"Invalid bootloader selected:"+self._install_profile.get_boot_loader_pkg())
	"""

	def _install_lilo(self):
		raise Exception("BootLoaderError", "fatal", "_install_lilo", "This function should *never* get called for amd64")
