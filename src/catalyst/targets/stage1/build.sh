#!/bin/bash
		
env-update
source /etc/profile
case $1 in
	build)
		# now, we fix the default make.profile symlink to be in line with the current profile being used.
		cd /etc
		rm -f make.profile
		ln -sf ../usr/portage/profiles/default-${MAINARCH}-${MAINVERSION} make.profile
		#emerge --oneshot --nodeps --usepkg --buildpkg ccache || exit 1
		export ROOT=${2}
		install -d $ROOT
		for x in $(/usr/portage/scripts/build.sh ${MAINARCH}-${MAINVERSION})
		do
			echo $x >> /tmp/build.log
			USE="-* build" emerge --usepkg --buildpkg --noreplace $x || exit 1
		done
	;;

	clean)
		export ROOT=${2}
		#emerge -C ccache
		keepers="sys-kernel/linux-headers sys-devel/binutils sys-devel/gcc sys-apps/baselayout sys-libs/glibc virtual/glibc virtual/kernel sys-devel/gettext"
		# set everything to uid 999 (nouser)
		cd ${ROOT}
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
		find -iname "*.a" | grep -v 'libgcc.a' | grep -v 'nonshared.a' | grep -v '/usr/lib/portage/bin/' | grep -v 'libgcc_eh.a' | xargs rm -f
		chroot ${ROOT} /bin/bash << EOF
		#now, some finishing touches to initialize gcc-config....
		unset ROOT
		if [ -e /usr/sbin/gcc-config ]
		then
			mythang=\$( cd /etc/env.d/gcc; ls ${CHOST}-* )
			gcc-config \${mythang}; env-update; source /etc/profile
		fi
		#fix up profile symlink in chroot
		cd /etc
		rm -f make.profile
		ln -sf ../usr/portage/profiles/default-${MAINARCH}-${MAINVERSION} make.profile
EOF
		;;
esac
	
