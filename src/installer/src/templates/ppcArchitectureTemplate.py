"""
Gentoo Linux Installer

$Id: ppcArchitectureTemplate.py,v 1.1 2005/07/22 05:29:31 codeman Exp $
Copyright 2004 Gentoo Technologies Inc.


This fills in amd64 specific functions.
"""

import GLIUtility, string
from x86ArchitectureTemplate import x86ArchitectureTemplate
from GLIException import *
import parted

class ppcArchitectureTemplate(x86ArchitectureTemplate):
        def __init__(self,configuration=None, install_profile=None, client_controller=None):
		ppcArchitectureTemplate.__init__(self, configuration, install_profile, client_controller)
		self._architecture_name = 'ppc'

	
	def install_bootloader(self):
		"Installs and configures bootloader"
		#
		# THIS IS ARCHITECTURE DEPENDANT!!!
		# This is the ppc way.. it uses yaboot for new world.
		
		if self._install_profile.get_boot_loader_pkg():
			exitstatus = self._emerge(self._install_profile.get_boot_loader_pkg())
			if exitstatus != 0:
				raise GLIException("BootLoaderEmergeError", 'fatal', 'install_bootloader', "Could not emerge bootloader!")
		else:
			pass
		
		if self._install_profile.get_boot_loader_pkg() == "yaboot":
			self._install_yaboot()
		else:
			raise Exception("BootLoaderError",'fatal','install_bootloader',"Invalid bootloader selected:"+self._install_profile.get_boot_loader_pkg())

	def _install_lilo(self):
		raise Exception("BootLoaderError", "fatal", "_install_lilo", "This function should *never* get called for amd64")

	def _install_yaboot(self):
		#yabootconfig --chroot /mnt/gentoo --quiet
		#this is the white rabbit object.  ajec: it expects a full fstab, /proc mounted, and a kernel in /boot/vmlinux
		pass
