#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript-support/Attic/kmerge.sh,v 1.20 2005/01/11 22:49:44 wolf31o2 Exp $

die() {
	echo "$1"
	exit 1
}

build_kernel() {
	# default genkernel args
	GK_ARGS="${clst_livecd_gk_mainargs} \
			 ${clst_livecd_gk_kernargs} \
			 --no-mountboot \
			 --kerneldir=/usr/src/linux \
			 --kernel-config=/var/tmp/${clst_kname}.config \
			 --minkernpackage=/usr/portage/packages/gk_binaries/${clst_kname}-${clst_version_stamp}.tar.bz2 all"
	
	# extra genkernel options that we have to test for
	if [ "${clst_livecd_splash_type}" == "bootsplash" -a -n "${clst_livecd_splash_theme}" ]
	then
		GK_ARGS="${GK_ARGS} --bootsplash=${clst_livecd_splash_theme}"
	fi
	
	if [ "${clst_livecd_splash_type}" == "gensplash" -a -n "${clst_livecd_splash_theme}" ]
	then
		GK_ARGS="${GK_ARGS} --gensplash=${clst_livecd_splash_theme}"
	fi

	if [ -n "${clst_CCACHE}" ]
	then
		GK_ARGS="${GK_ARGS} --kernel-cc=/usr/lib/ccache/bin/gcc --utils-cc=/usr/lib/ccache/bin/gcc"
	fi
	
	if [  -e "/var/tmp/${clst_kname}.postconf" ]
	then
		for x in $( cat /var/tmp/${clst_kname}.postconf )
		do
			clst_kernel_postconf="${clst_kernel_postconf} ${x}"
		done
	fi

	if [ -e "/var/tmp/${clst_kname}.packages" ]
	then
		for x in $( cat /var/tmp/${clst_kname}.packages )
		do
			clst_kernel_merge="${clst_kernel_merge} ${x}"
		done
	fi
	
	if [ "${clst_livecd_devmanager}" == "udev" ]
	then
		GK_ARGS="${GK_ARGS} --udev"
	fi
	
	# build with genkernel using the set options
	# callback and postconf are put here to avoid escaping issues
	if [ -e "/var/tmp/${clst_kname}.packages" -a \
	-e "/var/tmp/${clst_kname}.postconf" ]
	then
		genkernel --callback="emerge ${clst_kernel_merge}" \
			--postconf="emerge ${clst_kernel_postconf}" \
			${GK_ARGS} || exit 1
	elif [ -e "/var/tmp/${clst_kname}.packages" ]
	then
		genkernel --callback="emerge ${clst_kernel_merge}" \
			${GK_ARGS} || exit 1
	elif [ -e "/var/tmp/${clst_kname}.postconf" ]
	then
		genkernel --postconf="emerge ${clst_kernel_postconf}" \
			${GK_ARGS} || exit 1
	else
		genkernel ${GK_ARGS} || exit 1
	fi

	# pack up the modules for resuming
	if [ -n "${clst_KERNCACHE}" ]
	then
		tar cjpf /usr/portage/packages/gk_binaries/${1}-modules-${clst_version_stamp}.tar.bz2 \
			/lib/modules/${1} || die "Could not package kernel modules, exiting"
	fi
}

# Script to build each kernel, kernel-related packages
/usr/sbin/env-update
source /etc/profile

[ -n "${clst_ENVSCRIPT}" ] && source /tmp/envscript
export CONFIG_PROTECT="-*"
rm -f /usr/src/linux

#set the timezone for the kernel build
rm /etc/localtime
ln -s /usr/share/zoneinfo/UTC /etc/localtime

[ -e "/var/tmp/${clst_kname}.use" ] && export USE="$( cat /var/tmp/${clst_kname}.use )" || unset USE
[ -e "/var/tmp/${clst_kname}.gk_kernargs" ] && source /var/tmp/${clst_kname}.gk_kernargs

# Don't use pkgcache here, as the kernel source may get emerge with different USE variables
# (and thus different patches enabled/disabled.) Also, there's no real benefit in using the
# pkgcache for kernel source ebuilds.
emerge "${clst_ksource}" || exit 1
[ ! -e /usr/src/linux ] && die "Can't find required directory /usr/src/linux"
	
#if catalyst has set NULL_VALUE, extraversion wasn't specified so we skip this part
if [ "${clst_kextversion}" != "NULL_VALUE" ]
then
	sed -i -e "s:EXTRAVERSION \(=.*\):EXTRAVERSION \1-${clst_kextversion}:" /usr/src/linux/Makefile
fi
	
if [ -n "${clst_CCACHE}" ]
then
	#enable ccache for genkernel
	export PATH="/usr/lib/ccache/bin:${PATH}"
fi

# grep out the kernel version so that we can do our modules magic
VER=`grep ^VERSION\ \= /usr/src/linux/Makefile | awk '{ print $3 };'`
PAT=`grep ^PATCHLEVEL\ \= /usr/src/linux/Makefile | awk '{ print $3 };'`
SUB=`grep ^SUBLEVEL\ \= /usr/src/linux/Makefile | awk '{ print $3 };'`
EXV=`grep ^EXTRAVERSION\ \= /usr/src/linux/Makefile | sed -e "s/EXTRAVERSION =//" -e "s/ //g"`
clst_fudgeuname=${VER}.${PAT}.${SUB}${EXV}

# kernel building happens here
# does the old config exist? if it does not, we build by default
if [ -e "/usr/portage/packages/gk_binaries/${clst_kname}-${clst_version_stamp}.config" ]
then
	# test to see if the kernel .configs are the same, if so, then we skip kernel building
	test1=$(md5sum /var/tmp/${clst_kname}.config | cut -d " " -f 1)
	test2=$(md5sum /usr/portage/packages/gk_binaries/${clst_kname}-${clst_version_stamp}.config | cut -d " " -f 1)
	if [ "${test1}" == "${test2}" -a -n "${clst_KERNCACHE}" ]
	then
		echo
		echo "No kernel configuration change, skipping kernel build..."
		echo
		sleep 5

		# unpack our modules to the LiveCD fs
		echo
		echo "Unpacking kernel modules from the previous build..."
		echo
		[ ! -d /lib/modules ] && mkdir /lib/modules
		tar xjpf /usr/portage/packages/gk_binaries/${clst_fudgeuname}-modules-${clst_version_stamp}.tar.bz2 \
			-C / || die "Could not unpack kernel modules"
	else
		build_kernel ${clst_fudgeuname}
	fi

else
	build_kernel ${clst_fudgeuname}
	
fi

/sbin/modules-update --assume-kernel=${clst_fudgeuname}

#now the unmerge... (wipe db entry)
emerge -C ${clst_ksource}
unset USE

echo
# keep the config around so that we can resume at some point
if [ -n "${clst_KERNCACHE}" ]
then
 	cp /var/tmp/${clst_kname}.config \
	/usr/portage/packages/gk_binaries/${clst_kname}-${clst_version_stamp}.config
fi
echo
