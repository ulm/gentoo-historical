# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript/Attic/ppc-archscript.sh,v 1.10.2.9 2005/07/29 22:13:57 wolf31o2 Exp $

case $1 in
	kernel)
	;;

	preclean)
	;;

	clean)
	;;

	bootloader)
		# PPC requirements: 
		# -----------------
		# The specs indicate the kernels to be build. We need to put
		# those kernels and the corresponding initrd.img.gz(s) in the
		# /boot directory. This directory contains a message boot.msg 
		# containing some info to be displayed on boot, a configuration
		# (yaboot.conf) specifying the boot options (kernel/initrd 
		# combinations). The boot directory also contains a file called
		# yaboot, which normally gets copied from the live environment.
		# For now we supply a prebuilt file, prebuilt configuration 
		# and prebuilt boot message. This can be enhanced later on
		# but the following suffices for now:
		
		cdtar=${clst_livecd_cdtar}
		[ -z "${cdtar}" ] && die "Required key livecd/cdtar not defined, exiting"
		/bin/tar xjpvf ${cdtar} -C ${clst_cdroot_path} || die "Couldn't extract cdtar ${cdtar}"
		[ -z "${clst_boot_kernel}" ] && die "Required key boot/kernel not defined, exiting."
		
		first=""
		# this sets up the config file for yaboot
		icfg=${clst_cdroot_path}/boot/yaboot.conf
		kmsg=${clst_cdroot_path}/boot/boot.msg
		echo "default ${first}" > ${icfg}
		echo "timeout 300" >> ${icfg}
		echo "device=cd:" >> ${icfg}
		echo "root=/dev/ram" >> ${icfg}
		echo "fgcolor=white" >> ${icfg}
		echo "bgcolor=black" >> ${icfg}
		echo "message=/boot/boot.msg" >> ${icfg}

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

		for x in ${clst_boot_kernel}
		do
			kbinary="${clst_chroot_path}/usr/portage/packages/gk_binaries/${x}-${clst_version_stamp}.tar.bz2"
			if [ -z "${first}" ]
			then
				# grab name of first kernel
				first="${x}"
			fi
			[ ! -e "${kbinary}" ] && die  "Can't find kernel tarball at ${kbinary}"
			/bin/tar xjvf ${kbinary} -C ${clst_cdroot_path}/boot
			
			# change kernel name from "kernel" to "gentoo", for example
			if [ -e ${clst_cdroot_path}/boot/kernelz-* ]
			then
				mv ${clst_cdroot_path}/boot/kernelz-* ${clst_cdroot_path}/boot/${x}
			else
				mv ${clst_cdroot_path}/boot/kernel-* ${clst_cdroot_path}/boot/${x}
				# change initrd name from "initrd" to "gentoo.igz", for example
				if [ -e ${clst_cdroot_path}/boot/initrd* ]
				then
				    mv "${clst_cdroot_path}"/boot/initrd* "${clst_cdroot_path}"/boot/"${x}".igz
				fi

				if [ -e ${clst_cdroot_path}/boot/initramfs* ]
				then
				    mv "${clst_cdroot_path}"/boot/initramfs* "${clst_cdroot_path}"/boot/"${x}".igz
				fi
				eval custom_kopts=\$${x}_kernelopts
				echo "APPENDING CUSTOM KERNEL ARGS: ${custom_kopts}"
				echo >> ${icfg}
				echo "image=/boot/${x}" >> ${icfg}
				echo "initrd=/boot/${x}.igz" >> ${icfg}
				echo "label=${x}" >> ${icfg}
				echo "read-write" >> ${icfg}

				if [ "${clst_livecd_splash_type}" == "gensplash" -a -n "${clst_livecd_splash_theme}" ]
				then
					echo "append=\"init=/linuxrc ${cmdline_opts} ${custom_kopts} cdroot splash=silent,theme:${clst_livecd_splash_theme}\"" >> ${icfg}
				else
					echo "append=\"initrd=${x}.igz init=/linuxrc ${cmdline_opts} ${custom_kopts} cdroot splash=silent\"" >> ${icfg}
				fi
			fi
		done
	;;

	cdfs)
	;;

	iso)
		# Set sensible default volume ID
		if [ -z "${iso_volume_id}" ]
		then
			case ${clst_livecd_type} in
				gentoo-*)
					case ${clst_mainarch} in
						ppc)
							iso_volume_id="Gentoo Linux - PPC"
						;;
						ppc64)
							iso_volume_id="Gentoo Linux - PPC64"
						;;
					esac
				;;
				*)
					iso_volume_id="Catalyst LiveCD"
				;;
			esac
		fi
		# The name of the iso should be retrieved from the specs.
		case ${clst_livecd_cdfstype} in
			zisofs)
				mkisofs -J -r -l -z -chrp-boot -netatalk -hfs -probe -map ${clst_cdroot_path}/boot/map.hfs -part -no-desktop -hfs-volid "${iso_volume_id}" -hfs-bless ${clst_cdroot_path}/boot -V "${iso_volume_id}" -o ${2} ${clst_cdroot_path}
			;;
			*)
				mkisofs -J -r -l -chrp-boot -netatalk -hfs -probe -map ${clst_cdroot_path}/boot/map.hfs -part -no-desktop -hfs-volid "${iso_volume_id}" -hfs-bless ${clst_cdroot_path}/boot -V "${iso_volume_id}" -o ${2} ${clst_cdroot_path}
			;;
		esac
	;;
esac
