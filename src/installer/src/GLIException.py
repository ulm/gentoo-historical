"""
Gentoo Linux Installer

$Id: GLIException.py,v 1.7 2004/12/20 19:56:08 samyron Exp $
Copyright 2004 Gentoo Technologies Inc.

"""

from string import upper

class GLIException(Exception):
	error_levels = ['notice', 'warning', 'fatal']

	def __init__(self, error_name, error_level, function_name, error_msg):
		if error_level not in GLIException.error_levels:
			raise GLIException('NoSuchLevelError', 'fatal', '__init__', "No such error level: %s" % error_level)

		Exception.__init__(self, error_name, error_level, function_name, error_msg)

	def get_function_name(self):
		return self.args[2]

	def get_error_level(self):
		return self.args[1]

	def get_error_msg(self):
		return self.args[3]

	def get_error_name(self):
		return self.args[0]

	def __str__(self):
		return "%s :%s: %s: %s" % (self.args[0], upper(self.args[1]), self.args[2], self.args[3])

