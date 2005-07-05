# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript/Attic/hppa-archscript.sh,v 1.9.2.10 2005/07/05 21:47:46 wolf31o2 Exp $

case $1 in
	kernel)
	;;
	
	preclean)
	;;

	clean)
	;;

	bootloader)
		# CDFSTYPE and loop_opts are exported from the default
		# runscript

		# Create a filesystem tree for the ISO at $clst_cdroot_path.
		# We extract the "cdtar" to this directory, which will normally contains a pre-built
		# binary boot-loader/filesystem skeleton for the ISO. 
		
		cdtar=${clst_livecd_cdtar}
		[ -z "$cdtar" ] && die "Required key livecd/cdtar not specified, exiting"
		/bin/tar xjpvf ${cdtar} -C ${clst_cdroot_path} || die "Couldn't extract cdtar ${cdtar}"
		[ -z "$clst_boot_kernel" ] && die "Required key boot/kernel not specified, exiting"
		
		# install our kernel(s) that were built in kmerge.sh
		first=""
		for x in ${clst_boot_kernel}
		do
			eval custom_kopts=\$${x}_kernelopts
			kbinary="${clst_chroot_path}/usr/portage/packages/gk_binaries/${x}-${clst_version_stamp}.tar.bz2"	
			if [ -z "$first" ]
			then
				# grab name of first kernel
				first="${x}"
			fi
			[ ! -e "${kbinary}" ] && die "Can't find kernel tarball at ${kbinary}"
			/bin/tar xjvf ${kbinary} -C ${clst_cdroot_path}/boot
			
			# change kernel name from "kernel" to "gentoo", for example
			mv ${clst_cdroot_path}/boot/kernel* ${clst_cdroot_path}/boot/${x}

			# change initrd name from "initrd" to "gentoo.igz", for example
			if [ -e ${clst_cdroot_path}/boot/initrd* ]
			then
			    mv "${clst_cdroot_path}"/boot/initrd* "${clst_cdroot_path}"/boot/"${x}".igz
			fi
			
			if [ -e ${clst_cdroot_path}/boot/initramfs* ]
			then
			    mv "${clst_cdroot_path}"/boot/initramfs* "${clst_cdroot_path}"/boot/"${x}".igz
			fi
		done

		# figure out what device manager we are using and handle it accordingly
		if [ "${clst_livecd_devmanager}" == "udev" ]
		then
			cmdline_opts="${cmdline_opts} udev nodevfs"
		elif [ "${clst_livecd_devmanager}" == "devfs" ]
		then
			cmdline_opts="${cmdline_opts} noudev devfs"
		fi

		# Add any additional options
		if [ -n "${clst_livecd_bootargs}" ]
		then
			for x in ${clst_livecd_bootargs}
			do
				cmdline_opts="${cmdline_opts} ${x}"
			done
		fi
		
		# THIS SHOULD BE IMPROVED !
		#mv ${clst_cdroot_path}/boot/kernel* ${clst_cdroot_path}/vmlinux
		#mv ${clst_cdroot_path}/boot/initrd* ${clst_cdroot_path}/initrd
		icfg=${clst_cdroot_path}/boot/palo.conf
		kmsg=${clst_cdroot_path}/boot/kernels.msg
		hmsg=${clst_cdroot_path}/boot/help.msg
		echo "--commandline=0/${first} initrd=${first}.igz root=/dev/ram0 init=/linuxrc ${cmdline_opts}" >> ${icfg}
		echo "--bootloader=boot/iplboot" >> ${icfg}
		echo "--ramdisk=boot/${first}.igz" >> ${icfg}

	;;

	cdfs)
	;;

	iso)
		# Set sensible default volume ID
		if [ -z "${iso_volume_id}" ]
		then
			case ${clst_livecd_type} in
				gentoo-*)
					iso_volume_id="Gentoo Linux - HPPA"
				;;
				*)
					iso_volume_id="Catalyst LiveCD"
				;;
			esac
		fi

		#this is for the livecd-stage2 target, and calls the proper command to build the iso file
		case ${clst_livecd_cdfstype} in
			zisofs)
				mkisofs -J -R -l -z -V "${iso_volume_id}" -o ${2} ${clst_cdroot_path}  || die "Cannot make ISO image"
			;;
			*)
				mkisofs -J -R -l -V "${iso_volume_id}" -o ${2} ${clst_cdroot_path}  || die "Cannot make ISO image"
			;;
		esac
		palo -f boot/palo.conf -C ${2}
	;;
esac
