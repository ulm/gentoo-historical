# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/Attic/builder.py,v 1.7.2.1 2005/07/05 21:47:46 wolf31o2 Exp $

class generic:
	def __init__(self,myspec):
		self.settings=myspec
	def mount_safety_check(self):
		"""make sure that no bind mounts exist in chrootdir (to use before
		cleaning the directory, to make sure we don't wipe the contents of
		a bind mount"""
		pass
	def mount_all(self):
		"""do all bind mounts"""
		pass
	def umount_all(self):
		"""unmount all bind mounts"""
		pass
