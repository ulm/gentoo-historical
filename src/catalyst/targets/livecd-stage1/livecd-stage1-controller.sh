# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage1/Attic/livecd-stage1-controller.sh,v 1.2 2005/04/06 14:07:11 wolf31o2 Exp $

. ${clst_sharedir}/targets/support/functions.sh

## START RUNSCRIPT

case $1 in
	preclean)
		# move over the motd (if applicable)
		if [ -n "${clst_livecd_motd}" ]
		then
			cp -a ${clst_livecd_motd} ${clst_chroot_path}/etc/motd
		else
			cp -a ${clst_sharedir}/livecd/files/generic.motd.txt \
				${clst_sharedir}/livecd/files/universal.motd.txt \
				${clst_sharedir}/livecd/files/minimal.motd.txt \
				${clst_sharedir}/livecd/files/environmental.motd.txt \
				${clst_sharedir}/livecd/files/gamecd.motd.txt \
				${clst_chroot_path}/etc
		fi
	
		# move over the xinitrc (if applicable)
		if [ -n "${clst_livecd_xinitrc}" ]
		then
			cp -a ${clst_livecd_xinitrc} ${clst_chroot_path}/etc/X11/xinit/xinitrc
		fi

		# move over the environment
		cp ${clst_sharedir}/livecd/files/livecd-bash_profile \
			${clst_chroot_path}/root/.bash_profile
		touch ${clst_chroot_path}/root/.bashrc
		cp ${clst_sharedir}/livecd/files/livecd-local.start \
			${clst_chroot_path}/etc/conf.d/local.start
		cp ${clst_sharedir}/livecd/files/mkvardb \
			${clst_chroot_path}/tmp
		mkdir -p /usr/share/faces
		cp ${clst_sharedir}/livecd/files/gentoo.png \
			${clst_chroot_path}/usr/share/faces

		# touch /etc/startx if our livecd/type requires it
		if [ "${clst_livecd_type}" = "gentoo-release-environmental" ] \
		|| [ "${clst_livecd_type}" = "gentoo-gamecd" ]
		then
			touch ${clst_chroot_path}/etc/startx
		fi
		
		# now, finalize and tweak the livecd fs (inside of the chroot)
		exec_in_chroot  ${clst_sharedir}/targets/support/livecdfs-update.sh

		# execute gamecdfs-update.sh if we're a gamecd
		if [ "${clst_livecd_type}" = "gentoo-gamecd" ]
		then
			if [ -n "${clst_gamecd_conf}" ]
			then
				cp ${clst_gamecd_conf} ${clst_chroot_path}/tmp/gamecd.conf
			else
				echo "gamecd/conf is required for a gamecd!"
				exit 1
			fi
			exec_in_chroot ${clst_sharedir}/targets/support/gamecdfs-update.sh
			rm -f ${clst_chroot_path}/tmp/gamecd.conf
		fi
		
		# if the user has their own fs update script, execute it
		if [ -n "${clst_livecd_fsscript}" ]
		then
			exec_in_chroot ${clst_livecd_fsscript}
		fi
		;;
		
	build_packages)
		shift
		export clst_packages="$*"
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-chroot.sh
		;;

	clean)
		find ${clst_chroot_path}/usr/lib -iname "*.pyc" -exec rm -f {} \;
	;;
esac
exit 0 
