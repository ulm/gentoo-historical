# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/Attic/stage1.sh,v 1.6 2003/11/03 02:43:55 drobbins Exp $

case $1 in
enter)
	$clst_CHROOT $clst_chroot_path /bin/bash
	;;
run)
	cp ${clst_sharedir}/targets/stage1/stage1-chroot.sh ${clst_chroot_path}/tmp
	cp ${clst_sharedir}/targets/stage1/build.sh ${clst_chroot_path}/tmp
	# set up "ROOT in chroot" dir
	install -d ${clst_chroot_path}/tmp/stage1root/etc
	# set up make.conf and make.profile link in "ROOT in chroot":
	cp ${clst_chroot_path}/etc/make.conf ${clst_chroot_path}/tmp/stage1root/etc
	cp -a ${clst_chroot_path}/etc/make.profile ${clst_chroot_path}/tmp/stage1root/etc
	# enter chroot, execute our build script
	$clst_CHROOT ${clst_chroot_path} /tmp/stage1-chroot.sh build /tmp/stage1root
	[ $? -ne 0 ] && exit 1
	;;
preclean)
	#preclean runs with bind mounts active -- for running any commands inside chroot
	$clst_CHROOT ${clst_chroot_path} /tmp/stage1-chroot.sh preclean /tmp/stage1root
	[ $? -ne 0 ] && exit 1
	;;
clean)
	#clean runs after preclean with bind mounts unmounted
	keepers="sys-kernel/linux-headers sys-devel/binutils sys-devel/gcc sys-apps/baselayout sys-libs/glibc virtual/glibc virtual/kernel"
	if [ ${clst_rel_type} = "hardened" ]
	then
		keepers="${keepers} sys-devel/hardened-gcc"
	fi
	# set everything to uid 999 (nouser)
	cd ${clst_chroot_path}/tmp/stage1root
	install -d var/db/pkg2 
	for x in $keepers
	do
		category=${x%%/*}
		package=${x##*/}
		[ "`ls var/db/pkg/${x}* 2>/dev/null`" = "" ] && continue
		install -d var/db/pkg2/${category}
		mv var/db/pkg/${category}/${package}* var/db/pkg2/${category}
	done
	rm -rf var/db/pkg
	mv var/db/pkg2 var/db/pkg

	# clean out man, info and doc files
	rm -rf usr/share/{man,doc,info}/*
	# zap all .pyc and .pyo files
	find -iname "*.py[co]" -exec rm -f {} \;
	# cleanup all .a files except libgcc.a, *_nonshared.a and /usr/lib/portage/bin/*.a
	find -iname "*.a" | `find -iname "*.a" | grep -v 'libgcc.a' | grep -v 'nonshared.a' | grep -v '/usr/lib/portage/bin/' | grep -v 'libgcc_eh.a'` | xargs rm -f
	;;
*)
	exit 1
	;;
esac
exit 0

