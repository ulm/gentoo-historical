"""
Gentoo Linux Installer Test Suite
Copyright 2004 Gentoo Technologies, Inc.
$Header: /var/cvsroot/gentoo/src/installer/src/tests/test_GLI_InstallProfile.py,v 1.2 2004/02/15 02:11:27 esammer Exp $
"""

import unittest
import os
import GLI

class test_GLIInstallProfile (unittest.TestCase):

	def testInstantiate(self):
		profile = GLI.InstallProfile();

		self.failUnless(profile, "Could not instantiate InstallProfile");

	def testParse(self):
		profile = GLI.InstallProfile()

		self.failUnless(profile, "Could not instantiate InstallProfile");

		path = os.getcwd()
		path = os.path.join(path, "tests", "gli_test_profile.xml")

		profile.parse("file://" + path)

		self.assertEquals(profile.get_time_zone(), "GMT")

if __name__ == '__main__':
	unittest.main()
