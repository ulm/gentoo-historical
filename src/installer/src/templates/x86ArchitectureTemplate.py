"""
Gentoo Linux Installer

$Id: x86ArchitectureTemplate.py,v 1.2 2005/01/04 09:05:43 codeman Exp $
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
	#	self._install_steps = [self.stage1, self.stage2, self.stage3] um, we ain't doin this this way anymore folks.

	def partition(self):
		GLIUtility.run_bash("cfdisk")

