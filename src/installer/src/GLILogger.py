"""
Gentoo Linux Installer

$Id: GLILogger.py,v 1.1 2004/04/09 02:30:00 esammer Exp $
Copyright 2004 Gentoo Technologies Inc.

Logger is a singleton style generic logger object.
"""

import time

class Logger(object):

	_LOG_FILE_PATH = "install.log"
	_SHARED_LOGGER = None

	_file_handle = None

	def shared_logger(cls):
		if Logger._SHARED_LOGGER == None:
			Logger._SHARED_LOGGER = Logger()

		return Logger._SHARED_LOGGER

	def __init__(self):
		self._file = file(Logger._LOG_FILE_PATH, 'a')

	def log(self, message):
		self._file.write("GLI: " + time.strftime("%h %m %Y %H:%M:%S") + " - " + message + "\n")

	def mark(self):
		self.log(" -- MARK -- ")

	shared_logger = classmethod(shared_logger)
