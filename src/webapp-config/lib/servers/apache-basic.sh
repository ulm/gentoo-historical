#
# -*- mode: sh -*-
#
# /usr/lib/webapp-config/supported-servers/apache-basic.sh
#               Basic support for installing web-based applications so
#               that they will run under the Apache 1|2 web servers
#
#               Part of the webapp-config toolset
#
# Author(s)     Stuart Herbert <stuart@gentoo.org>
#
# Copyright     (c) 1999-2004 Gentoo Technologies, Inc.
#               Released under v2 of the GNU GPL
#
# -------------------------------------------------------------------------

# ASSUMPTIONS:
#
# - /etc/conf.d/webapp-config has been imported

# -------------------------------------------------------------------------
# VARIABLES REQUIRED BY WEBAPP-CONFIG SCRIPT

MY_DESC="supports installation on Apache 1 & 2"
MY_DEP=">=net-www/apache-1.3"
# ------------------------------------------------------------------------
# fn_ws_clean ()
#
# Oh great.  Everyone else got to make a mess, and we're left to clean
# it up ;-)
#
# This (the apache-basic) server support just relies on the functions
# defined

fn_ws_clean ()
{
	libsh_ewarn "fn_ws_clean() called"

	fn_remove_files "$MY_REMOVECONTENTS" "$G_INSTALLDIR"
	fn_remove_dirs "$MY_REMOVECONTENTS" "$G_INSTALLDIR"
}

# ------------------------------------------------------------------------
# fn_ws_clean_verify ()
#
# Perform all server-specific checks, to make sure we can remove this app
# before we go ahead and do so.
#
# If this function returns at all, the caller can assume that it is safe
# to proceed with removing the webapp.
#
# IMPORTANT:
#
#	There's a bit of guesswork here in the design.  I'm assuming that
#	someone will write a server plugin that doesn't use real directories
#	(and therefore doesn't place the CONTENTS file in the same place).
#
#	To try and accomodate this, I've made fn_ws_clean_verify() responsible
#	for setting the location of the CONTENTS file.

fn_ws_clean_verify ()
{
	echo > /dev/null
}

# ------------------------------------------------------------------------

fn_ws_clean_setup ()
{
	[ -z $MY_REMOVECONTENTS ] && MY_REMOVECONTENTS="$G_INSTALLDIR/.webapp-$WEB_PN-$WEB_PVR"
}

# $1 - installation dir (normally $G_INSTALLDIR)
# $2 - package name (normally $G_PN)
# $3 - package version (normally $G_PVR)

fn_ws_echocontents ()
{
	echo "$1/.webapp-$2-$3"
}

# ------------------------------------------------------------------------
# fn_ws_linkfiles ()
#
# Link in all of the files from part of the app's image into the
# final installation directory
#
# Inputs:
#	$1	- directory to start searching for files in
#		  (normally $MY_HTDOCSDIR)
#	$2	- directory to create files in
#		  (normally $G_INSTALLDIR)
#	$3	- are we storing filenames into the CONTENTS file as
#		  relative (1) or absolute (0)?

fn_ws_linkfiles ()
{
	# special case - the source directory does not exist

	if [ ! -d "$1" ] ; then
		libsh_ewarn "    $G_PN-$G_PVR does not install any files from"
		libsh_ewarn "      $1"
		return
	fi

	local my_files="`cd $1 && find . -type f -print`"
	local x
	local my_base="`basename $1`"

	for x in $my_files ; do
		x="`echo \"$x\" | sed -e 's|^./||g;'`"
		fn_mkfile "$my_base" "$x" "$2" "$3"
	done
}

# ========================================================================
# fn_ws_install()
#
# This is where it happens, baby, yeah!
#
# Given this information:
#
#	package name in $G_PN
#	package version in $G_PVR
#	target directory in $G_INSTALLDIR
#	a username:group combo in $G_CONFIG_UID:$G_CONFIG_GID
#	a hostname in $G_HOSTNAME
#
# our job is to install the package so that it works.  Easy, eh?
# ------------------------------------------------------------------------

fn_ws_install ()
{
	libsh_einfo "Installing $G_PN $G_PVR ..."

	# we need to create the directories to place our files in
	#
	# we do this first to make *absolutely* sure that all of
	# the directories are in place *before* we attempt to
	# add any files into the mix

	libsh_einfo "  Creating required directories"
	fn_mkdirs "$MY_HTDOCSDIR" "$G_INSTALLDIR" 1
	fn_mkdirs "$MY_HOSTROOTDIR" "$VHOST_ROOT" 0
	fn_mkdirs "$MY_CGIBINDIR" "$VHOST_ROOT/$MY_CGIBINBASE" 0
	fn_mkdirs "$MY_ICONSDIR" "$VHOST_ROOT/$MY_ICONSBASE" 0
	fn_mkdirs "$MY_ERRORSDIR" "$VHOST_ROOT/$MY_ERRORSBASE" 0

	# now we need to copy in the files

	libsh_einfo "  Linking in required files"
	fn_ws_linkfiles "$MY_HTDOCSDIR" "$G_INSTALLDIR" 1
	fn_ws_linkfiles "$MY_HOSTROOTDIR" "$VHOST_ROOT" 0
	fn_ws_linkfiles "$MY_CGIBINDIR" "$VHOST_ROOT/$MY_CGIBINBASE" 0
	fn_ws_linkfiles "$MY_ICONSDIR" "$VHOST_ROOT/$MY_ICONSBASE" 0
	fn_ws_linkfiles "$MY_ERRORSDIR" "$VHOST_ROOT/$MY_ERRORSBASE" 0

	# and that should be that
}

fn_ws_install_verify ()
{
	if [ ! -d "${G_INSTALLDIR}" ] ; then
		libsh_einfo "Creating installation directory '$G_INSTALLDIR'"

		mkdir -p ${G_INSTALLDIR} || libsh_edie "Unable to create '$G_INSTALLDIR'"

		# default permissions and ownership on directories
		# this will need review before we're ready to roll

		libsh_einfo "Setting default permissions on '$G_INSTALLDIR'"

		chown root:root ${G_INSTALLDIR}
		chmod 755 ${G_INSTALLDIR}
	fi
}

fn_ws_install_setup ()
{
	echo > /dev/null
}
