# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/users/zhen/catalyst/include/build_functions.sh,v 1.4 2003/10/12 01:12:03 zhen Exp $

# <zhen@gentoo.org> We source this file to get the build functions

get_arch() {

	if [ "${SUBARCH}" = "athlon-mp" ]
	then
		SUBARCH=athlon-xp
	fi

	case "${SUBARCH}" in
	custom)
		#use the settings from the livecd config file.
		;;
	ia64)
		MAINARCH="ia64"
		CFLAGS="-O2"
		CHOST="ia64-unknown-linux-gnu"
		jobs="$((`grep -c ^[Pp]rocessor /proc/cpuinfo` * 2))"
		;;
	amd64)
		MAINARCH="amd64"
		CFLAGS="-O2 -fPIC"
		CHOST="x86_64-pc-linux-gnu"
		jobs="$((`grep -c ^[Pp]rocessor /proc/cpuinfo` * 2))"
		;;
	hppa|hppa1.1|hppa2.0)
		MAINARCH="hppa"
		case "${SUBARCH}" in
			hppa|hppa1.1)
				CFLAGS="-march=1.1"
				;;
			hppa2.0)
				CLAGS="-march=2.0"
				;;
		esac
		CHOST="hppa-unknown-linux-gnu"
		CFLAGS="-O2 $CFLAGS"
		jobs="$((`grep -c ^[Pp]rocessor /proc/cpuinfo` * 2))"
		;;
	x86|i386|i486|i586|i686|athlon|athlon-xp|athlon-mp|pentium-mmx|pentium3|pentium4 )
		MAINARCH="x86"
		if [ "$1" = "x86" ]
		then
			CFLAGS="-O3 -mcpu=i686"
		elif [ "$1" = "athlon-mp" ]
		then
			#MP and XP are functionally equivalent
			CFLAGS="-O2 -march=athlon-xp"
		elif [ "$1" = "athlon-xp" ]
		then
			CFLAGS="-O2 -march=athlon-xp"
		else
			CFLAGS="-O3 -march=${1}"
		fi
		# some additional optimizations; don't change these without checking
		# with drobbins
		case "$i{SUBARCH}" in
			i386|i486|i586)
				CHOST="${1}-pc-linux-gnu"
				;;
			x86)
				CHOST="i486-pc-linux-gnu"
				;;
			*)
				CHOST=i686-pc-linux-gnu
				;;
		esac
		case "${SUBARCH}" in
			pentium-mmx|pentium3|pentium4 )
				CFLAGS="$CFLAGS -fprefetch-loop-arrays"
				;;
		esac
		if [ "${SUBARCH:0:6}" != "athlon" ]
		then
			CFLAGS="$CFLAGS -funroll-loops"
		fi
		# Athlon XP and MP get just an -O2 -march for stability, since
		# we've had some issues with the 1.4 release and Athlon (drobbins, 12 Sep 03)
		jobs="$((`grep -c ^[Pp]rocessor /proc/cpuinfo` * 2))"
		;;
	ppc|g3|g4 )
		MAINARCH="ppc"
		CHOST="powerpc-unknown-linux-gnu"
		CFLAGS="-O2 -fsigned-char"
		if [ "${SUBARCH}" = "g3" ]
		then
			CFLAGS="-O2 -mcpu=750 -mpowerpc-gfxopt -fsigned-char"
		elif [ "${SUBARCH}" = "g4" ]
		then
			CFLAGS="-O2 -mcpu=7400 -maltivec -mabi=altivec -mpowerpc-gfxopt -fsigned-char"
		fi
		# ppc has "processor", but only when compiled with SMP
		if [ "`grep -c "^processor" /proc/cpuinfo`" -eq 1 ]
		then
			jobs="$((`grep -c ^processor /proc/cpuinfo` * 2))"
		else
			jobs=2
		fi
		;;
	sparc|sparc64 )
		MAINARCH="${SUBARCH}"
		CHOST="sparc-unknown-linux-gnu"
		CFLAGS=""
		if [ "${SUBARCH}" = "sparc" ]
		then
			CFLAGS="-O2"
		else
			CFLAGS="-O3 -mcpu=ultrasparc -mtune=ultrasparc"
		fi
		# sparc always has "ncpus active"
		jobs="$((`grep "^ncpus active" /proc/cpuinfo | sed -e "s/^.*: //"` * 2))"
		;;
	mips )
		MAINARCH="mips"
		CHOST="mips-unknown-linux-gnu"
		CFLAGS="-O2"
		jobs="$((`grep -c ^[Pp]rocessor /proc/cpuinfo` * 2))"
		;;
	alpha|ev4|ev5|ev56|pca56|ev6|ev67 )
		MAINARCH="alpha"
		if [ "${SUBARCH}" = "alpha" ]
		then
		        # defaults to ev5 code, which runs on anything
			CHOST="alpha-unknown-linux-gnu"
			CFLAGS="-O3 -mcpu=ev5"
		else
			CHOST="alpha${SUBARCH}-linux-gnu"
			CFLAGS="-O3 -mcpu=${SUBARCH}"
		fi
		# alpha has "cpus active", but only when compiled with SMP
		if [ "`grep -c "^cpus active" /proc/cpuinfo`" -eq 1 ]
		then
			jobs="$((`grep "^cpus active" /proc/cpuinfo | sed -e "s/^.*: //"` * 2))"
		else
			jobs=2
		fi
		;;
	* )
		echo "$0: Unsupported sub-architecture. Please use one of the following:"
		echo "$SUBARCHES"
		die
		;;
	esac
	
		
} #end get_arch()

pre_build() {
	case $1 in
		1)
			SRCSTAGE=2
			SRCVER=${2}
			SRCARCH=${MAINARCH}
			DESTARCH=${MAINARCH}
			SRCFORTAR=${CHROOTDIR}/tmp/stage1root
		;;
		2)
			SRCSTAGE=1
			SRCVER=${2}
			SRCARCH=${MAINARCH}
			DESTARCH=${SUBARCH}
		;;
		3)
			SRCSTAGE=2
			SRCVER=${2}
			SRCARCH=${SUBARCH}
			DESTARCH=${SUBARCH}
		;;
		grp)
			SRCSTAGE=3
			SRCVER=${2}
			SRCARCH=${SUBARCH}
			DESTARCH=${SUBARCH}
		;;

	esac
	if [ "$1" = "grp" ]
	then
		MY_PKGDIR="${BASEDIR}/packages/grp-${DESTARCH}-${DESTVER}"
	else
		MY_PKGDIR="${BASEDIR}/packages/stage${DESTSTAGE}-${DESTARCH}-${DESTVER}"
	fi
	install -d ${STAGEDIR} ${MY_PKGDIR} ${SNAPDIR}

	if [ "`uname -m`" = "x86_64" -a "$MAINARCH" = "x86" ]
	then
		if [ ! -e /bin/linux32 ]
		then
			eerror "Can't find linux32 executable. Please emerge sys-apps/linux32"
			eerror "and try again."
			die "linux32 not found; aborting."
		fi
		CHROOT="linux32 chroot"
	else
		CHROOT=chroot
	fi
	
	# necessary internal definitions
	
	if [ ${BUILDTYPE} = "hardened" ]
	then
	
		DESTBALL="${BASEDIR}/stages/stage${1}-${DESTARCH}-etdyn-ssp-${3}.tar.bz2"
	
		if [ ${DESTSTAGE} = 2 ] && [ ${SRCSTAGE} != 1 ]
		then
			SRCBALL="${BASEDIR}/stages/stage${SRCSTAGE}-${SRCARCH}-${SRCVER}.tar.bz2"
		else
			SRCBALL="${BASEDIR}/stages/stage${SRCSTAGE}-${SRCARCH}-etdyn-ssp-${SRCVER}.tar.bz2"
		fi

	elif [ ${BUILDTYPE} = "selinux" ]
	then
		DESTBALL="${BASEDIR}/stages/stage${1}-${DESTARCH}-selinux-${3}.tar.bz2"
	
		if [ ${DESTSTAGE} = 2 ] && [ ${SRCSTAGE} != 1 ]
		then
			SRCBALL="${BASEDIR}/stages/stage${SRCSTAGE}-${SRCARCH}-${SRCVER}.tar.bz2"
		else
			SRCBALL="${BASEDIR}/stages/stage${SRCSTAGE}-${SRCARCH}-selinux-${SRCVER}.tar.bz2"
		fi

	else
		DESTBALL="${BASEDIR}/stages/stage${1}-${DESTARCH}-${3}.tar.bz2"
		SRCBALL="${BASEDIR}/stages/stage${SRCSTAGE}-${SRCARCH}-${SRCVER}.tar.bz2"

	fi

	einfo "Cleaning up build directory..."
	rm -rf ${CHROOTDIR}
	install -d ${CHROOTDIR}

	#enable our signal handler
	trap "die" INT QUIT 

	umount_all
	[ ! -e ${SRCBALL} ] && die "Can't find source tarball ${SRCBALL}; exiting."
	einfo "Unpacking ${SRCBALL}..."
	unpack ${SRCBALL}
	#bind-mount filesystems/directories
	mount_all
	print_build

	#copy resolv.conf
	cp /etc/resolv.conf ${CHROOTDIR}/etc || die

	if [ $1 = "2" ] && [ ${BUILDTYPE} = "hardened" ]
	then
		# copy our bootstrap file
		cp -a ${BASEDIR}/bin/bootstrap.sh ${CHROOTDIR}/usr/portage || die
	fi

	#install our make.conf into the main compilation dir
	makeconf $CHROOTDIR

	#now, it's time to build...
	cd ${CHROOTDIR}
	if [ -e ${BASEDIR}/make.profile ]
	then
		rm ${BASEDIR}/make.profile
	fi
	ln -sf /usr/portage/profiles/${BUILDTYPE}-${MAINARCH}-${MAINVERSION} ${BASEDIR}/make.profile
	if [ -n ${CCACHE} ]
	then
		export FEATURES="ccache"
	fi

	if [ ${1} != "grp" ]
	then
		einfo "Destination tarball: ${DESTBALL}"
	else
		einfo "Target: GRP build"
	fi
	einfo "Build Settings:"
	if [ -n ${CCACHE} ]
	then
		einfo " ccache support: Enabled"
	else
		einfo " ccache support: Disabled"
	fi
} #end pre_build()

build() {
	case ${1} in
		1)	
			cp ${BASEDIR}/bin/stage1 ${CHROOTDIR}/tmp
			cp ${BASEDIR}/bin/build.sh ${CHROOTDIR}/tmp
			#CHOST is for the gcc-config initialization step
			export MAINVERSION MAINARCH CHOST BUILDTYPE
			#get our make.conf instide our new tree
			#good idea because make.conf should be there.
			#also necessary because the "stage1" script runs gcc-config, which
			#uses portage, which requires /etc/make.conf to exist.
			makeconf ${CHROOTDIR}/tmp/stage1root
			$CHROOT . /tmp/stage1 build /tmp/stage1root
			[ $? -ne 0 ] && die "Stage 1 build failure"
		;;
		2)	
			export MYPROFILEDIR
			$CHROOT . /bin/bash << EOF
			env-update
			source /etc/profile
			mkdir -p /usr/portage/packages/All
			export EMERGE_OPTS="--usepkg --buildpkg"
			export MAKEOPTS="-j${jobs}"
			if [ -n ${CCACHE} ]
			then
				emerge --oneshot --nodeps ccache || exit 1
			fi
			/usr/portage/bootstrap.sh || exit 1
EOF
			[ $? -ne 0 ] && die "Stage 2 build failure"
		;;
		3)
			$CHROOT . /bin/bash << EOF
			env-update
			source /etc/profile
			if [ -n ${CCACHE} ]
			then
				emerge --oneshot --nodeps --usepkg --buildpkg ccache || exit 1
			fi
			if [ ${BUILDTYPE} = "hardened" ]
			then
				emerge --oneshot --nodeps hardened-gcc || exit 1
			fi
			export CONFIG_PROTECT="-*"
			export MAKEOPTS="-j${jobs}"
			emerge system --usepkg --buildpkg || exit 1
EOF
			[ $? -ne 0 ] && die "Stage 3 build failure"
		;;
		grp) 
			cp ${BASEDIR}/grp/${MAINARCH}.* ${CHROOTDIR}/tmp || die
			$CHROOT . /bin/bash << EOF
			env-update
			source /etc/profile
			export CONFIG_PROTECT="-*"
			source /tmp/${MAINARCH}.conf
			#add bindist for this part
			export USE="\$USE bindist"
			#CD 1 contains "base" packages: kernel sources, hardware, crons, loggers, X
			export PKGDIR=/usr/portage/packages/cd1
			for x in \$( cat /tmp/${MAINARCH}.pkg.cd1  | grep -v ^# )
			do
				emerge --noreplace --buildpkg --usepkg \$x || exit 1
			done
			#CD 2 contains application packages: GNOME, KDE, and others
			export PKGDIR=/usr/portage/packages/cd2
			for x in \$( cat /tmp/${MAINARCH}.pkg.cd2  | grep -v ^# )
			do
				emerge --noreplace --buildpkg --usepkg \$x || exit 1
			done
			source /tmp/${MAINARCH}.conf
			#export GENTOO_MIRRORS="/usr/portage"
			export DISTDIR="/var/tmp/distfiles"
			install -d \$DISTDIR
			for x in \$( cat /tmp/${MAINARCH}.src | grep -v ^# )
			do
				emerge --fetchonly \$x || exit 1
			done
EOF
			[ $? -ne 0 ] && die "GRP build failure"
			;;
	esac
} #end build()

post_build() {
	case "$1" in
	1)
		$CHROOT . /tmp/stage1 clean /tmp/stage1root
		;;
	2|3)
		$CHROOT . /bin/bash << EOF
		if [ -n ${CCACHE} ]
		then
			emerge -C ccache
		fi
EOF
		rm -rf ${CHROOTDIR}/tmp/* 
		rm -rf ${CHROOTDIR}/var/tmp/portage/*
		rm -f ${CHROOTDIR}/etc/ld.so.preload
				;;
	esac
	
	umount_all
	
	if [ -n ${CCACHE} ]
	then
		rm -rf ${CHROOTDIR}/root/.ccache
	fi

	rm ${CHROOTDIR}/etc/resolv.conf
	einfo "Removing Portage tree from chroot image..."
	rm -rf ${CHROOTDIR}/usr/portage

	#pack up directory to ${DESTBALL}
	if [ "$1" != "grp" ]
	then
		tardir
	fi

	einfo "Build Complete!"

} #end postbuild()

