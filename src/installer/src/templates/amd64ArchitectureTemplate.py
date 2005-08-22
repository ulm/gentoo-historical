"""
# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.
Gentoo Linux Installer

$Id: amd64ArchitectureTemplate.py,v 1.5 2005/08/22 18:35:52 codeman Exp $
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

	def _configure_lilo(self):
		raise Exception("BootLoaderError", "fatal", "_configure_lilo", "This function should *never* get called for amd64")
