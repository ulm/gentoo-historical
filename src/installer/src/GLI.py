"""
Gentoo Linux Installer

$Id: GLI.py,v 1.2 2004/02/11 03:36:04 esammer Exp $
Copyright 2004 Gentoo Technologies Inc.

The GLI module contains all classes used in the Gentoo Linux Installer (or GLI).
"""

class InstallProfile(object):
	"""
	An object representation of a profile.

	InstallProfile is an object representation of a parsed installation
	profile file.
	"""

	_timezone = ""

	def __init__(self):
		pass
	
	def parse(self, path):
		pass

	def get_timezone(self):
		return _timezone
	
	def set_timezone(self, timezone):
		_timezone = timezone

