#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript/Attic/ia64-archscript.sh,v 1.1.2.6 2005/07/15 20:53:07 wolf31o2 Exp $

case $1 in
	kernel)
	;;

	preclean)
	;;

	clean)
	;;

	bootloader)
		# Create a filesystem tree for the ISO at
		# ${clst_cdroot_path}. We extract the "cdtar" to this directory,
		# which will normally contains a pre-built binary
		# boot-loader/filesystem skeleton for the ISO. 
		
		cdtar=${clst_livecd_cdtar}
		[ -z "$cdtar" ] && die "Required key livecd/cdtar not specified, exiting"
		/bin/tar xjpvf ${cdtar} -C ${clst_cdroot_path} || die "Couldn't extract cdtar ${cdtar}"
		[ -z "${clst_boot_kernel}" ] && die "Required key boot/kernel not specified, exiting"
		
		# unpack the kernel(s) that were built in kmerge.sh
		first=""
		for x in ${clst_boot_kernel}
		do
			kbinary="${clst_chroot_path}/usr/portage/packages/gk_binaries/${x}-${clst_version_stamp}.tar.bz2"
			[ ! -e "${kbinary}" ] && die "Can't find kernel tarball at ${kbinary}"
			
			/bin/tar xjvf ${kbinary} -C ${clst_cdroot_path}/boot
			
			# change kernel name from "kernel" to "gentoo", for example
			mv ${clst_cdroot_path}/boot/kernel* ${clst_cdroot_path}/boot/efi/boot/${x}
			
			# change initrd name from "initrd" to "gentoo.igz", for example
			if [ -e ${clst_cdroot_path}/boot/initrd* ]
			then
			    mv "${clst_cdroot_path}"/boot/initrd* "${clst_cdroot_path}"/boot/efi/boot/"${x}".igz
			fi
			if [ -e ${clst_cdroot_path}/boot/initramfs* ]
			then
			    mv "${clst_cdroot_path}"/boot/initramfs* "${clst_cdroot_path}"/boot/efi/boot/"${x}".igz
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

		iacfg=${clst_cdroot_path}/boot/elilo.conf
		echo 'prompt' > ${iacfg}
		echo 'message=/efi/boot/elilo.msg' >> ${iacfg}
		echo 'chooser=simple' >> ${iacfg}
		echo 'timeout=50' >> ${iacfg}
		echo >> ${iacfg}
		for x in ${clst_boot_kernel}
		do
			echo "image=/efi/boot/${x}" >> ${iacfg}
			echo "  label=${x}" >> ${iacfg}
			echo "  append=\"initrd=${x}.igz root=/dev/ram0 init=/linuxrc acpi=off ${cmdline_opts} ${custom_kopts} cdroot\"" >> ${iacfg}
			echo "  initrd=/efi/boot/${x}.igz" >> ${iacfg}
			echo >> ${iacfg}
			echo "image=/efi/boot/${x}" >> ${iacfg}
			echo "  label=${x}-serial">> ${iacfg}
			echo "  append=\"initrd=${x}.igz root=/dev/ram0 init=/linuxrc acpi=off ${cmdline_opts} ${custom_kopts} cdroot console=tty0 console=ttyS0,9600\"" >> ${iacfg}
			echo "  initrd=/efi/boot/${x}.igz" >> ${iacfg}
			echo >> ${iacfg}
		done
		cp ${iacfg} ${clst_cdroot_path}/boot/efi/boot
		mv ${clst_cdroot_path}/boot/${x}{,.igz} $1/boot/efi/boot
	;;

	cdfs)
	;;

	iso)
		# Set sensible default volume ID
		if [ -z "${iso_volume_id}" ]
		then
			case ${clst_livecd_type} in
				gentoo-*)
					iso_volume_id="Gentoo Linux - IA64"
				;;
				*)
					iso_volume_id="Catalyst LiveCD"
				;;
			esac
		fi
		if [ ! -e ${clst_cdroot_path}/gentoo.efimg ]
		then
			iaSizeTemp=$(du -sk ${clst_cdroot_path}/boot 2>/dev/null)
			iaSizeB=$(echo ${iaSizeTemp} | cut '-d ' -f1)
			iaSize=$((${iaSizeB}+32)) # Add slack

			dd if=/dev/zero of=${clst_cdroot_path}/gentoo.efimg bs=1k count=${iaSize}
			mkdosfs -F 16 -n GENTOO ${clst_cdroot_path}/gentoo.efimg

			mkdir ${clst_cdroot_path}/gentoo.efimg.mountPoint
			mount -t vfat -o loop ${clst_cdroot_path}/gentoo.efimg ${clst_cdroot_path}/gentoo.efimg.mountPoint

			echo '>> Populating EFI image...'
			cp -av ${clst_cdroot_path}/boot/* ${clst_cdroot_path}/gentoo.efimg.mountPoint
			umount ${clst_cdroot_path}/gentoo.efimg.mountPoint
			rmdir ${clst_cdroot_path}/gentoo.efimg.mountPoint
		else
			echo ">> Found populated EFI image at ${clst_cdroot_path}/gentoo.efimg"
		fi

		echo '>> Removing /boot...'
		rm -rf ${clst_cdroot_path}/boot

		echo '>> Generating ISO...'

		# this is for the livecd-final target, and calls the proper
		# command to build the iso file
		case ${clst_livecd_cdfstype} in
			zisofs)
				mkisofs -J -R -l -z -V "${iso_volume_id}" -o ${2} -b gentoo.efimg -c boot.cat -no-emul-boot ${clst_cdroot_path}  || die "Cannot make ISO image"
			;;
			*)
				mkisofs -J -R -l -V "${iso_volume_id}" -o ${2} -b gentoo.efimg -c boot.cat -no-emul-boot ${clst_cdroot_path} || die "Cannot make ISO image"
			;;
		esac
	;;
esac
