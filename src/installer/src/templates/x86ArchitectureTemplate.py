"""
Gentoo Linux Installer

$Id: x86ArchitectureTemplate.py,v 1.1 2004/11/30 21:38:57 samyron Exp $
Copyright 2004 Gentoo Technologies Inc.


This fills in x86 specific functions.
"""

import GLIUtility
from GLIArchitectureTemplate import ArchitectureTemplate
from GLIException import *


class x86ArchitectureTemplate(ArchitectureTemplate):
        def __init__(self,configuration=None, install_profile=None, client_controller=None):
		ArchitectureTemplate.__init__(self, configuration, install_profile, client_controller)
		self._architecture_name = 'x86'
		self._install_steps = [self.stage1, self.stage2, self.stage3]

	def partition(self):
		GLIUtility.run_bash("cfdisk")

