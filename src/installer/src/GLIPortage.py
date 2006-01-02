"""
# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.
Gentoo Linux Installer

$Id: GLIPortage.py,v 1.19 2006/01/02 18:23:34 agaffney Exp $
"""

import re
import GLIUtility
from GLIException import GLIException

class GLIPortage(object):

	def __init__(self, chroot_dir, grp_install, logger, debug, cc, compile_logfile):
		self._chroot_dir = chroot_dir
		self._grp_install = grp_install
		self._logger = logger
		self._debug = debug
		self._cc = cc
		self._compile_logfile = compile_logfile

	def get_deps(self, pkgs):
		pkglist = []
		if isinstance(pkgs, str):
			pkgs = pkgs.split()
		for pkg in pkgs:
			if self._debug: self._logger.log("get_deps(): pkg is " + pkg)
			if not self._grp_install or not self.get_best_version_vdb(pkg):
				if self._debug: self._logger.log("get_deps(): grabbing compile deps")
				tmppkglist = GLIUtility.spawn("emerge -p " + pkgs + r" | grep -e '^\[[a-z]' | cut -d ']' -f2 | sed -e 's:^ ::' -e 's: .\+$::'", chroot=self._chroot_dir, return_output=True)[1].strip().split("\n")
			else:
				if self._debug: self._logger.log("get_deps(): grabbing binary deps")
				# Until I have a unified method of getting binary and compile deps, I can't reliably merge the deptrees
#				tmppkglist = GLIUtility.spawn("python ../../runtimedeps.py " + self._chroot_dir + " " + pkg, return_output=True)[1].strip().split("\n")
				tmppkglist = []
				for tmppkg in GLIUtility.spawn("emerge -p " + pkgs + r" | grep -e '^\[[a-z]' | cut -d ']' -f2 | sed -e 's:^ ::' -e 's: .\+$::'", chroot=self._chroot_dir, return_output=True)[1].strip().split("\n")
					if self.get_best_version_vdb_chroot("=" + tmppkg):
						tmppkglist.append(tmppkg)
			if self._debug: self._logger.log("get_deps(): deplist for " + pkg + ": " + str(tmppkglist))
			for tmppkg in tmppkglist:
				if self._debug: self._logger.log("get_deps(): checking to see if " + tmppkg + " is already in pkglist")
				if not tmppkg in pkglist and not self.get_best_version_vdb_chroot("=" + tmppkg):
					if self._debug: self._logger.log("get_deps(): adding " + tmppkg + " to pkglist")
					pkglist.append(tmppkg)
		if self._debug: self._logger.log("get_deps(): pkglist is " + str(pkglist))
		return pkglist

	def copy_pkg_to_chroot(self, package, use_root=False):
		symlinks = { '/bin/': '/mnt/livecd/bin/', '/boot/': '/mnt/livecd/boot/', '/lib/': '/mnt/livecd/lib/', 
		             '/opt/': '/mnt/livecd/opt/', '/sbin/': '/mnt/livecd/sbin/', '/usr/': '/mnt/livecd/usr/',
		             '/etc/gconf/': '/usr/livecd/gconf/' }

		root_cmd = ""
		tmp_chroot_dir = self._chroot_dir
		portage_tmpdir = "/var/tmp/portage"
		if use_root:
			root_cmd = "ROOT=" + self._chroot_dir
			tmp_chroot_dir = ""
			portage_tmpdir = self._chroot_dir + "/var/tmp/portage"

		# Copy the vdb entry for the package from the LiveCD to the chroot
		if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): copying vdb entry for " + package)
		if not GLIUtility.exitsuccess(GLIUtility.spawn("mkdir -p " + self._chroot_dir + "/var/db/pkg/" + package + " && cp -a /var/db/pkg/" + package + "/* " + self._chroot_dir + "/var/db/pkg/" + package)):
			raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not copy vdb entry for " + package)

		# Create list of files for tar to work with from CONTENTS file in vdb entry
		entries = GLIUtility.parse_vdb_contents("/var/db/pkg/" + package + "/CONTENTS")
		if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot: files for " + package + ": " + str(entries))
		try:
			tarfiles = open("/tmp/tarfilelist", "w")
			for entry in entries:
				parts = entry.split(" ")
				# Hack for symlink crappiness
				for symlink in symlinks:
					if parts[0].startswith(symlink):
						parts[0] = symlinks[symlink] + parts[0][len(symlink):]
				tarfiles.write(parts[0] + "\n")
			tarfiles.close()
		except:
			raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not create filelist for " + package)

		# Use tar to transfer files into IMAGE directory
		tmpdir = "/var/tmp/portage"
		image_dir = tmpdir + "/" + package.split("/")[1] + "/image"
		if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): running 'mkdir -p " + self._chroot_dir + image_dir + " && tar -c --files-from=/tmp/tarfilelist --no-recursion 2>/dev/null | tar -C " + self._chroot_dir + image_dir + " -x'")
		if not GLIUtility.exitsuccess(GLIUtility.spawn("mkdir -p " + self._chroot_dir + image_dir + " && tar -c --files-from=/tmp/tarfilelist --no-recursion 2>/dev/null | tar -C " + self._chroot_dir + image_dir + " -x")):
			raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not execute tar for " + package)

		# More symlink crappiness hacks
		for symlink in symlinks:
			if GLIUtility.is_file(self._chroot_dir + image_dir + symlinks[symlink]):
#				parts[0] = symlinks[symlink] + parts[len(symlink):]
				if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): fixing /usr/livecd/gconf/ stuff in " + image_dir + " for " + package)
				if not GLIUtility.exitsuccess(GLIUtility.spawn("mv " + self._chroot_dir + image_dir + symlinks[symlink] + " " + self._chroot_dir + image_dir + symlink)):
					raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not fix /usr/livecd/gconf/ stuff for " + package)

		# Run pkg_setup
		if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): running pkg_setup for " + package)
		if not GLIUtility.exitsuccess(GLIUtility.spawn("env " + root_cmd + " PORTAGE_TMPDIR=" + portage_tmpdir + " ebuild /var/db/pkg/" + package + "/*.ebuild setup", chroot=tmp_chroot_dir)):
			raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not execute pkg_setup for " + package)

		# Run qmerge
#		if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): running qmerge for " + package)
#		if not GLIUtility.exitsuccess(GLIUtility.spawn("env ROOT=" + self._chroot_dir + " PORTAGE_TMPDIR=" + self._chroot_dir + tmpdir + " ebuild " + self._chroot_dir + "/var/db/pkg/" + package + "/*.ebuild qmerge")):
#			raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not execute qmerge for " + package)

		# Run pkg_preinst
		if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): running preinst for " + package)
		if not GLIUtility.exitsuccess(GLIUtility.spawn("env " + root_cmd + " PORTAGE_TMPDIR=" + portage_tmpdir + " ebuild /var/db/pkg/" + package + "/*.ebuild preinst", chroot=tmp_chroot_dir)):
			raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not execute preinst for " + package)

		# Copy files from image_dir to chroot
		if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): copying files from " + image_dir + " to / for " + package)
		if not GLIUtility.exitsuccess(GLIUtility.spawn("cp -a " + self._chroot_dir + image_dir + "/* " + self._chroot_dir)):
			raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not copy files from " + image_dir + " to / for " + package)

		# Run pkg_postinst
		if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): running postinst for " + package)
		if not GLIUtility.exitsuccess(GLIUtility.spawn("env " + root_cmd + " PORTAGE_TMPDIR=" + portage_tmpdir + " ebuild /var/db/pkg/" + package + "/*.ebuild postinst", chroot=tmp_chroot_dir)):
			raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not execute postinst for " + package)

		# Remove image_dir
		if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): removing + " + image_dir + " for " + package)
		if not GLIUtility.exitsuccess(GLIUtility.spawn("rm -rf " + self._chroot_dir + image_dir)):
			raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not remove + " + image_dir + " for " + package)

	def add_pkg_to_world(self, package):
		if package.find("/") == -1:
			package = self.get_best_version_vdb_chroot(package)
		if not package: return False
		expr = re.compile('^=?(.+?/.+?)(-\d.+)?$')
		res = expr.match(package)
		if res:
			GLIUtility.spawn("echo " + res.group(1) + " >> " + self._chroot_dir + "/var/lib/portage/world")

	def get_best_version_vdb(self, package):
		return GLIUtility.spawn("portageq best_version / " + package, return_output=True)[1].strip()

	def get_best_version_vdb_chroot(self, package):
		return GLIUtility.spawn("portageq best_version / " + package, chroot=self._chroot_dir, return_output=True)[1].strip()

#	def get_best_version_tree(self, package):
#		return portage.best(tree.match(package))

	def emerge(self, packages, add_to_world=True):
		if isinstance(packages, str):
			packages = packages.split()
		pkglist = self.get_deps(packages)
		if self._debug: self._logger.log("install_packages(): pkglist is " + str(pkglist))
		for i, pkg in enumerate(pkglist):
			if self._debug: self._logger.log("install_packages(): processing package " + pkg)
			self._cc.add_notification("progress", (float(i) / len(pkglist), "Emerging " + pkg + " (" + str(i+1) + "/" + str(len(pkglist)) + ")"))
			if not self.get_best_version_vdb("=" + pkg):
				status = GLIUtility.spawn("emerge -1 =" + pkg, display_on_tty8=True, chroot=self._chroot_dir, logfile=self._compile_logfile, append_log=True)
#				status = self._emerge("=" + pkg)
				if not GLIUtility.exitsuccess(status):
					raise GLIException("EmergePackageError", "fatal", "emerge", "Could not emerge " + pkg + "!")
			else:
#				try:
				self.copy_pkg_to_chroot(pkg)
#				except:
#					raise GLIException("EmergePackageError", "fatal", "emerge", "Could not emerge " + pkg + "!")
		if add_to_world:
			for package in packages:
				self.add_pkg_to_world(package)
