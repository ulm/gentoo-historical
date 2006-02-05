"""
# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.
Gentoo Linux Installer

$Id: GLIPortage.py,v 1.34 2006/02/05 20:29:40 agaffney Exp $
"""

import re
import os
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
				tmppkglist = GLIUtility.spawn("emerge -p " + pkg + r" 2>/dev/null | grep -e '^\[[a-z]' | cut -d ']' -f2 | sed -e 's:^ ::' -e 's: .\+$::'", chroot=self._chroot_dir, return_output=True)[1].strip().split("\n")
			else:
				if self._debug: self._logger.log("get_deps(): grabbing binary deps")
				# The runtimedeps.py script generates a package install order that is *very* different from emerge itself
#				tmppkglist = GLIUtility.spawn("python ../../runtimedeps.py " + self._chroot_dir + " " + pkg, return_output=True)[1].strip().split("\n")
				tmppkglist = []
				for tmppkg in GLIUtility.spawn("emerge -p " + pkg + r" 2>/dev/null | grep -e '^\[[a-z]' | cut -d ']' -f2 | sed -e 's:^ ::' -e 's: .\+$::'", chroot=self._chroot_dir, return_output=True)[1].strip().split("\n"):
					if self._debug: self._logger.log("get_deps(): looking at " + tmppkg)
					if self.get_best_version_vdb("=" + tmppkg):
						if self._debug: self._logger.log("get_deps(): package " + tmppkg + " in host vdb...adding to tmppkglist")
						tmppkglist.append(tmppkg)
			if self._debug: self._logger.log("get_deps(): deplist for " + pkg + ": " + str(tmppkglist))
			for tmppkg in tmppkglist:
				if self._debug: self._logger.log("get_deps(): checking to see if " + tmppkg + " is already in pkglist")
				if not tmppkg in pkglist and not self.get_best_version_vdb_chroot("=" + tmppkg):
					if self._debug: self._logger.log("get_deps(): adding " + tmppkg + " to pkglist")
					pkglist.append(tmppkg)
		if self._debug: self._logger.log("get_deps(): pkglist is " + str(pkglist))
		return pkglist

	def parse_vdb_contents(self, file):
		entries = []
		try:
			vdbfile = open(file, "r")
		except:
			return entries
		for line in vdbfile.readlines():
			parts = line.strip().split(" ")
			if parts[0] == "obj":
				entries.append(parts[1])
#			elif parts[0] == "dir":
#				entries.append(parts[1] + "/")
			elif parts[0] == "sym":
				entries.append(" ".join(parts[1:4]))
		entries.sort()
		return entries

	def copy_pkg_to_chroot(self, package, use_root=False):
		symlinks = { '/bin': '/mnt/livecd/bin/', '/boot': '/mnt/livecd/boot/', '/lib': '/mnt/livecd/lib/', 
		             '/opt': '/mnt/livecd/opt/', '/sbin': '/mnt/livecd/sbin/', '/usr': '/mnt/livecd/usr/',
		             '/etc/gconf': '/usr/livecd/gconf/' }

		tmpdir = "/var/tmp/portage"
		image_dir = tmpdir + "/" + package.split("/")[1] + "/image"
		root_cmd = ""
		tmp_chroot_dir = self._chroot_dir
		portage_tmpdir = "/var/tmp/portage"
		vdb_dir = "/var/db/pkg/"
		if use_root:
			root_cmd = "ROOT=" + self._chroot_dir
			tmp_chroot_dir = ""
			portage_tmpdir = self._chroot_dir + "/var/tmp/portage"
			vdb_dir = self._chroot_dir + "/var/db/pkg/"

		# Copy the vdb entry for the package from the LiveCD to the chroot
		if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): copying vdb entry for " + package)
		if not GLIUtility.exitsuccess(GLIUtility.spawn("mkdir -p " + self._chroot_dir + "/var/db/pkg/" + package + " && cp -a /var/db/pkg/" + package + "/* " + self._chroot_dir + "/var/db/pkg/" + package)):
			raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not copy vdb entry for " + package)

		# Create the image dir in the chroot
		if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): running 'mkdir -p " + self._chroot_dir + image_dir + "'")
		if not GLIUtility.exitsuccess(GLIUtility.spawn("mkdir -p " + self._chroot_dir + image_dir)):
			raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not create image dir for " + package)

		# Create list of files for tar to work with from CONTENTS file in vdb entry
		entries = self.parse_vdb_contents("/var/db/pkg/" + package + "/CONTENTS")
		if not entries:
			if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): no files for " + package + "...skipping tar and symlink fixup")
		else:
			if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot: files for " + package + ": " + str(entries))
			try:
				tarfiles = open("/tmp/tarfilelist", "w")
				for entry in entries:
					parts = entry.split(" ")
#					# Hack for symlink crappiness
#					for symlink in symlinks:
#						if parts[0].startswith(symlink):
#							parts[0] = symlinks[symlink] + parts[0][len(symlink):]
					tarfiles.write(parts[0] + "\n")
				tarfiles.close()
			except:
				raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not create filelist for " + package)

			# Use tar to transfer files into IMAGE directory
			if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): running 'tar -cp --files-from=/tmp/tarfilelist --no-recursion 2>/dev/null | tar -C " + self._chroot_dir + image_dir + " -xp'")
			if not GLIUtility.exitsuccess(GLIUtility.spawn("tar -cp --files-from=/tmp/tarfilelist --no-recursion 2>/dev/null | tar -C " + self._chroot_dir + image_dir + " -xp")):
				raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not execute tar for " + package)

#			# More symlink crappiness hacks
#			for symlink in symlinks:
##				if GLIUtility.is_file(self._chroot_dir + image_dir + symlinks[symlink]):
#				if os.path.islink(self._chroot_dir + image_dir + symlink):
#					if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): fixing " + symlink + " symlink ickiness stuff in " + image_dir + " for " + package)
#					GLIUtility.spawn("rm " + self._chroot_dir + image_dir + symlink)
#					if not GLIUtility.exitsuccess(GLIUtility.spawn("mv " + self._chroot_dir + image_dir + symlinks[symlink] + " " + self._chroot_dir + image_dir + symlink)):
#						raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not fix " + symlink + " symlink ickiness for " + package)

		# Run pkg_setup
		if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): running pkg_setup for " + package)
		if not GLIUtility.exitsuccess(GLIUtility.spawn("env " + root_cmd + " PORTAGE_TMPDIR=" + portage_tmpdir + " ebuild " + vdb_dir + package + "/*.ebuild setup", chroot=tmp_chroot_dir)):
			raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not execute pkg_setup for " + package)

		# Run pkg_preinst
		if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): running preinst for " + package)
		if not GLIUtility.exitsuccess(GLIUtility.spawn("env " + root_cmd + " PORTAGE_TMPDIR=" + portage_tmpdir + " ebuild " + vdb_dir + package + "/*.ebuild preinst", chroot=tmp_chroot_dir)):
			raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not execute preinst for " + package)

		# Copy files from image_dir to chroot
		if not entries:
			if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): no files for " + package + "...skipping copy from image dir to /")
		else:
			if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): copying files from " + image_dir + " to / for " + package)
			if not GLIUtility.exitsuccess(GLIUtility.spawn("cp -a " + self._chroot_dir + image_dir + "/* " + self._chroot_dir)):
				raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not copy files from " + image_dir + " to / for " + package)

		# Run pkg_postinst
		if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): running postinst for " + package)
		if not GLIUtility.exitsuccess(GLIUtility.spawn("env " + root_cmd + " PORTAGE_TMPDIR=" + portage_tmpdir + " ebuild " + vdb_dir + package + "/*.ebuild postinst", chroot=tmp_chroot_dir)):
			raise GLIException("CopyPackageToChrootError", 'fatal', 'copy_pkg_to_chroot', "Could not execute postinst for " + package)

		# Remove image_dir
		if self._debug: self._logger.log("DEBUG: copy_pkg_to_chroot(): removing " + image_dir + " for " + package)
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
		self._cc.addNotification("progress", (0, "Calculating dependencies for " + " ".join(packages)))
		pkglist = self.get_deps(packages)
		if self._debug: self._logger.log("install_packages(): pkglist is " + str(pkglist))
		for i, pkg in enumerate(pkglist):
			if self._debug: self._logger.log("install_packages(): processing package " + pkg)
			self._cc.addNotification("progress", (float(i) / len(pkglist), "Emerging " + pkg + " (" + str(i+1) + "/" + str(len(pkglist)) + ")"))
			if not self._grp_install or not self.get_best_version_vdb("=" + pkg):
				status = GLIUtility.spawn("emerge -1 =" + pkg, display_on_tty8=True, chroot=self._chroot_dir, logfile=self._compile_logfile, append_log=True)
#				status = self._emerge("=" + pkg)
				if not GLIUtility.exitsuccess(status):
					raise GLIException("EmergePackageError", "fatal", "emerge", "Could not emerge " + pkg + "!")
			else:
#				try:
				self.copy_pkg_to_chroot(pkg)
#				except:
#					raise GLIException("EmergePackageError", "fatal", "emerge", "Could not emerge " + pkg + "!")
			self._cc.addNotification("progress", (float(i+1) / len(pkglist), "Done emerging " + pkg + " (" + str(i+1) + "/" + str(len(pkglist)) + ")"))
		if add_to_world:
			for package in packages:
				self.add_pkg_to_world(package)
