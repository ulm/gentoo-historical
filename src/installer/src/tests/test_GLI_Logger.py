"""
Gentoo Linux Installer Test Suite
Copyright 2004 Gentoo Technologies, Inc.
$Header: /var/cvsroot/gentoo/src/installer/src/tests/test_GLI_Logger.py,v 1.1 2004/04/09 03:00:09 esammer Exp $
"""

import unittest
import os
import GLILogger

class test_GLILogger (unittest.TestCase):

	def setUp(self):
		self.failUnless(os.path.exists("GLILogger.py"), "Please run tests from src")

	def testInstantiate(self):
		logger = GLILogger.Logger.shared_logger();

		self.failUnless(logger, "Could not get shared logger");

	def testLogMessage(self):
		logger = GLILogger.Logger.shared_logger();

		self.failUnless(logger, "Could not get shared logger");

		logger.log("Test log message one.")

	def testMark(self):
		logger = GLILogger.Logger.shared_logger();

		self.failUnless(logger, "Could not get shared logger");

		logger.mark()

if __name__ == '__main__':
	unittest.main()
