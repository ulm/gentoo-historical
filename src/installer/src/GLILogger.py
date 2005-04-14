"""
Gentoo Linux Installer

$Id: GLILogger.py,v 1.6 2005/04/14 15:44:03 agaffney Exp $
Copyright 2004 Gentoo Technologies Inc.

Logger is a singleton style generic logger object.
"""

import time

class Logger(object):

	_LOG_FILE_PATH = "install.log"
	_SHARED_LOGGER = None

	##
	# Brief description of function
	# @param cls Parameter description
	def shared_logger(cls):
		if Logger._SHARED_LOGGER == None:
			Logger._SHARED_LOGGER = Logger()

		return Logger._SHARED_LOGGER

	##
	# Brief description of function
	# @param selflogfile=None Parameter description
	def __init__(self,logfile=None):
		if logfile == None:
			self._file = file(Logger._LOG_FILE_PATH, 'a')
		else:
			self._file = file(logfile,'a')

	##
	# Brief description of function
	# @param self Parameter description
	# @param message Parameter description
	def log(self, message):
		self._file.write("GLI: " + time.strftime("%h %m %Y %H:%M:%S") + " - " + message + "\n")
		self._file.flush()
		
	##
	# Brief description of function
	# @param self Parameter description
	def mark(self):
		self.log(" -- MARK -- ")

	shared_logger = classmethod(shared_logger)
