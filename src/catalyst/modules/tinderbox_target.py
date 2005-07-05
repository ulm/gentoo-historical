# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/Attic/tinderbox_target.py,v 1.10 2005/07/05 21:53:41 wolf31o2 Exp $

"""
builder class for the tinderbox target
"""

from catalyst_support import *
from generic_stage_target import *

class tinderbox_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=["tinderbox/packages","tinderbox/use"]
		self.valid_values=self.required_values[:]
		generic_stage_target.__init__(self,spec,addlargs)

	def run_local(self):
		# tinderbox
		# example call: "grp.sh run xmms vim sys-apps/gleep"
		try:
			if os.path.exists(self.settings["controller_file"]):
			    cmd("/bin/bash "+self.settings["controller_file"]+" run "+\
				list_bashify(self.settings["tinderbox/packages"]),"run script failed.")
		
		except CatalystError:
			self.unbind()
			raise CatalystError,"Tinderbox aborting due to error."
	
def register(foo):
	foo.update({"tinderbox":tinderbox_target})
	return foo
