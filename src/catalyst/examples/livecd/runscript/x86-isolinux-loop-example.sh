# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/examples/livecd/runscript/Attic/x86-isolinux-loop-example.sh,v 1.2 2004/01/11 04:04:16 brad_mssw Exp $

die() {
	echo "$1"
	exit 1
}

#The order that catalyst does things for livecd-stage3 is as follows:
#
# runscript: run
# runscript: preclean (bind mounts still mounted)
# catalyst: do livecd-stage3/unmerge (bind mounts still mounted)
# catalyst: bind mounts unmounted
# catalyst: do livecd-stage3/empty
# catalyst: do livecd-stage3/delete
# runscript: livecd-stage3/clean
# runscript: cdroot_setup

case $1 in
run)
	#For doing things inside the chroot before the "preclean". Normally, "preclean"
	#should be used, or steps should be performed in the livecd-stage2 stage.
	$clst_CHROOT $clst_chroot_path /bin/bash << EOF
	echo "meep"
EOF
	[ $? -ne 0 ] && exit 1
;;
preclean)
	#preclean runs with bind mounts active -- for running any commands inside chroot.
	#The chroot environment has not been trimmed in any way, so you still have a full
	#environment.
	$clst_CHROOT $clst_chroot_path /bin/bash << EOF
	echo "CDBOOT=1" >> /etc/rc.conf
EOF
	[ $? -ne 0 ] && exit 1
;;
clean)
	#livecd-stage3/unmerge, bind-unmount, and livecd-stage3/{empty,delete,prune}
	#have already executed at this point. You now have the opportunity to perform
	#any additional cleaning steps that may be required.
	find $clst_chroot_path/usr/lib -iname "*.pyc" -exec rm -f {} \;
	;;
cdroot_setup)
	#Time to create a filesystem tree for the ISO at $clst_cdroot_path.
	#We extract the "cdtar" to this directory, which will normally contains a pre-built
	#binary boot-loader/filesystem skeleton for the ISO. Then we get genkernel-built
	#kernels and initrds in place, create the loopback fs on $clst_cdroot_path,
	#mount it, copy our bootable filesystem over, umount it, and we then have a
	#ready-to-burn ISO tree at $clst_cdroot_path.
	
	cdtar=$clst_livecd_stage3_cdtar
	[ "$cdtar" = "" ] && die "No livecd-stage3/cdtar specified (required)"
	tar xjpvf $cdtar -C $clst_cdroot_path || die "Couldn't extract cdtar $cdtar"
	if [ "$clst_boot_kernel" = "" ]
	then
		echo "No boot/kernel setting defined, exiting."
		exit 1
	fi
	first=""
	for x in $clst_boot_kernel
	do
		if [ "$first" = "" ]
		then
			#grab name of first kernel
			first="$x"
		fi
		if [ ! -e "$clst_binaries_source_path/$x.tar.bz2" ] 
		then
			echo "Can't find kernel tarball at $clst_binaries_source_path/$x.tar.bz2"
			exit 1
		fi
		tar xjvf $clst_binaries_source_path/$x.tar.bz2 -C $clst_cdroot_path/isolinux
		#change kernel name from "kernel" to "gentoo", for example
		mv $clst_cdroot_path/isolinux/kernel $clst_cdroot_path/isolinux/$x
		#change initrd name from "initrd" to "gentoo.igz", for example
		mv $clst_cdroot_path/isolinux/initrd $clst_cdroot_path/isolinux/$x.igz
	done
	icfg=$clst_cdroot_path/isolinux/isolinux.cfg
	echo "default $first" > $icfg
	for x in $clst_boot_kernel
	do
		echo >> $icfg
		echo "label $x" >> $icfg
		echo "	kernel $x" >> $icfg
		echo "	append initrd=$x.igz root=/dev/ram0 init=/linuxrc cdroot" >> $icfg
	done
	#OK, now we need to prepare the loopback filesystem that we'll be booting. This is
	#tricky.
	echo "Calculating size of loopback filesystem..."
	loopsize=`du -ks $clst_chroot_path | cut -f1`
	[ "$loopsize" = "0" ] && loopsize=1
	#increase the size by 1/3, then divide by 4 to get 4k blocks
	loopsize=$(( ( $loopsize + ( $loopsize / 2 ) ) / 4  ))
	echo "Creating loopback file..."
	dd if=/dev/zero of=$clst_cdroot_path/livecd.loop bs=4k count=$loopsize || die "livecd.loop creation failure"
	#echo "Calculating number of inodes required for ext2 filesystem..."
	#numnodes=`find $clst_chroot_path | wc -l`
	#numnodes=$(( $numnodes + 200 ))
	mke2fs -m 0 -F -b 4096 -q $clst_cdroot_path/livecd.loop || die "Couldn't create ext2 filesystem"
	install -d $clst_cdroot_path/loopmount
	sync; sync; sleep 3 #try to work around 2.6.0+ loopback bug
	mount -t ext2 -o loop $clst_cdroot_path/livecd.loop $clst_cdroot_path/loopmount || die "Couldn't mount loopback ext2 filesystem"
	sync; sync; sleep 3 #try to work around 2.6.0+ loopback bug
	echo "cp -a $clst_chroot_path/* $clst_cdroot_path/loopmount"
	cp -a $clst_chroot_path/* $clst_cdroot_path/loopmount 
	[ $? -ne 0 ] && { umount $clst_cdroot_path/loopmount; die "Couldn't copy files to loopback ext2 filesystem"; }
	umount $clst_cdroot_path/loopmount || die "Couldn't unmount loopback ext2 filesystem"
	rm -rf $clst_cdroot_path/loopmount
	#now, $clst_cdroot_path should contain a proper bootable image for our iso, including
	#boot loader and loopback filesystem.
	;;
iso_create)
	#this is for the livecd-final target, and calls the proper command to build the iso file
	mkisofs -J -R -l -o ${clst_iso_path} -b isolinux/isolinux.bin -c isolinux/boot.cat \
	-no-emul-boot -boot-load-size 4 -boot-info-table $clst_cdroot_path
	;;
esac
exit 0
