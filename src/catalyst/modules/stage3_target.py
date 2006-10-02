# $Header: /var/cvsroot/gentoo/src/catalyst/modules/Attic/stage3_target.py,v 1.7 2006/10/02 20:41:54 wolf31o2 Exp $

"""
Builder class for a stage3 installation tarball build.
"""

from catalyst_support import *
from generic_stage_target import *

class stage3_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=[]
		self.valid_values=[]
		generic_stage_target.__init__(self,spec,addlargs)

        def set_portage_overlay(self):
			generic_stage_target.set_portage_overlay(self)
			if self.settings.has_key("portage_overlay"):
				print "\nWARNING !!!!!"
				print "\tUsing an overlay for earlier stages could cause build issues."
				print "\tIf you break it, you buy it. Don't complain to us about it."
				print "\tDont say we did not warn you\n"

def register(foo):
	foo.update({"stage3":stage3_target})
	return foo
