"""
Gentoo Linux Installer

$Id: GLILogger.py,v 1.7 2005/04/17 07:13:28 codeman Exp $
Copyright 2004 Gentoo Technologies Inc.

Logger is a singleton style generic logger object.
"""

import time

class Logger(object):

	_LOG_FILE_PATH = "install.log"
	_SHARED_LOGGER = None

	##
	# Creates a shared logger like in GLIClientConfiguration
	# @param cls It's just done like that.
	def shared_logger(cls):
		if Logger._SHARED_LOGGER == None:
			Logger._SHARED_LOGGER = Logger()

		return Logger._SHARED_LOGGER

	##
	# Basic Initialization function.  Appends to the given logfile
	# @param logfile=None file to log stuff to.
	def __init__(self,logfile=None):
		if logfile == None:
			self._file = file(Logger._LOG_FILE_PATH, 'a')
		else:
			self._file = file(logfile,'a')

	##
	# Logs the given message to the logfile
	# @param message Parameter description
	def log(self, message):
		self._file.write("GLI: " + time.strftime("%h %m %Y %H:%M:%S") + " - " + message + "\n")
		self._file.flush()
		
	##
	# Inserts a mark into the logfile.
	def mark(self):
		self.log(" -- MARK -- ")

	shared_logger = classmethod(shared_logger)
