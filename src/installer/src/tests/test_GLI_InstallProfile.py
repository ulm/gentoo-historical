"""
Gentoo Linux Installer Test Suite
Copyright 2004 Gentoo Technologies, Inc.
$Header: /var/cvsroot/gentoo/src/installer/src/tests/test_GLI_InstallProfile.py,v 1.4 2004/04/09 02:46:59 esammer Exp $
"""

import unittest
import os
import GLIInstallProfile

class test_GLIInstallProfile (unittest.TestCase):

	def setUp(self):
		self.failUnless(os.path.exists("GLIInstallProfile.py"), "Please run tests from src")

	def testInstantiate(self):
		profile = GLIInstallProfile.InstallProfile();

		self.failUnless(profile, "Could not instantiate InstallProfile");

	def testParse(self):
		profile = GLIInstallProfile.InstallProfile()

		self.failUnless(profile, "Could not instantiate InstallProfile");

		path = os.getcwd()
		path = os.path.join(path, "tests", "gli_test_profile.xml")

		profile.parse("file://" + path)

		self.assertEquals(profile.get_time_zone(), "GMT")

if __name__ == '__main__':
	unittest.main()
