#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/users/zhen/catalyst/include/functions.sh,v 1.3 2003/10/11 19:28:46 drobbins Exp $

usage() {
	einfo "Catalyst: Gentoo Linux Stage Building tool ${VERSION}"
	einfo "Copyright 2003 Gentoo Technologies, Inc."
	einfo "Licensed under the GNU General Public License version 2"
	echo
	einfo "Syntax: catalyst <arch> <stage> srcver destver"
	einfo "Valid stage targets: [0|1|2|3]"
	echo
	einfo "Valid stage target architectures: "
	einfo "${SUBARCHES}"

} #end usage()

print_build() { 
	echo
	einfo "Gentoo Linux staging tool (Catalyst) V${VERSION} starting."
	einfo "Tarball Settings:"
	einfo  " Architecture: ${MAINARCH}"
	einfo  " Sub-architecture: ${SUBARCH}"
	einfo  " CFLAGS: ${CFLAGS}"
	einfo  " CHOST: ${CHOST}"
	einfo  " Source tarball: ${SRCBALL}"
	einfo  " Portage snapshot: ${SNAPBALL}"
	echo

} #end print_build()

umount_all() {
	local x
	for x in /usr/portage/packages /usr/portage/distfiles /var/tmp/distfiles /proc /root/.ccache /dev
	do
		umount ${CHROOTDIR}${x} 2>/dev/null || true 
	done

} #end umount_all()

die() {
	#unmount filesystems if script is aborted
	[ -n "${1}" ] && einfo "${0}: error: ${1}"
	umount_all 
	exit 1

} #end die()

mount_all() {
	local x
	if [ ! -d /root/.ccache ]
	then 
		mkdir /root/.ccache || die "Couldn't create /root/.ccache dir"
	fi
	for x in /root/.ccache /proc  
	do
		[ ! -e ${CHROOTDIR}${x} ] && install -d ${CHROOTDIR}${x}
		mount --bind ${x} ${CHROOTDIR}${x} || die "Couldn't bind-mount ${x}"
	done
	[ ! -e ${SNAPBALL} ] && die "Can't find $SNAPBALL ; exiting." 	
	einfo "Extracting Portage tree snapshot..."
	tar xjf ${SNAPBALL} -C ${CHROOTDIR}/usr || die "Error extracting Portage snapshot"
	[ ! -e ${CHROOTDIR}/usr/portage/packages ] && install -d ${CHROOTDIR}/usr/portage/packages
	mount --bind ${MY_PKGDIR} ${CHROOTDIR}/usr/portage/packages || die
	[ ! -e ${CHROOTDIR}/usr/portage/distfiles ] && install -d ${CHROOTDIR}/usr/portage/distfiles
	mount --bind ${MY_DISTDIR} ${CHROOTDIR}/usr/portage/distfiles || die
	[ ! -e ${CHROOTDIR}/var/tmp/distfiles ] && install -d ${CHROOTDIR}/var/tmp/distfiles
	mount --bind ${MY_DIST_LOCALS} ${CHROOTDIR}/var/tmp/distfiles || die

	if [ "$2" = "3" ]
	then
		#stage3, needed for perl? Let's see.
		mount --bind /dev ${CHROOTDIR}/dev
	fi

} #end mount_all

unpack() {
	[ ! -d ${CHROOTDIR} ] && die "Chroot directory doesn't exist; exiting."
	tar xjpf ${1} -C ${CHROOTDIR} || die "Error unpacking ${1}; exiting."

} #end unpack()

tardir() {
	einfo "Creating ${DESTBALL}..."
	cd ${SRCFORTAR} || die "Couldn't chdir; exiting."
	tar -cjf ${DESTBALL} . --numeric-owner || die "Tarball creation error; exiting."
	cd ${BASEDIR}

} #end tardir()

makeconf() {
	[ ! -d ${1}/etc ] && install -d ${1}/etc
	cat ${BASEDIR}/files/make.conf.${MAINARCH} | sed -e "s:##CFLAGS##:${CFLAGS}:" \
	-e "s:##CHOST##:${CHOST}:" > ${1}/etc/make.conf || die

} #end makeconf()

# vim ts=4

