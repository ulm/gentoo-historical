subarch: amd64
version_stamp: 2004.2-test2
target: livecd-stage2
rel_type: default
profile: default-amd64-2004.2
snapshot: 20040626-r2
source_subpath: default/livecd-stage1-amd64-2004.2-test2
#livecd/cdfstype: zisofs
livecd/cdfstype: zisofs
livecd/archscript: /home/jhuebel/prog/gentoo/src/catalyst/livecd/runscript/x86-archscript.sh
livecd/runscript: /home/jhuebel/prog/gentoo/src/catalyst/livecd/runscript/default-runscript.sh
livecd/cdtar: /home/jhuebel/prog/gentoo/src/catalyst/livecd/cdtar/isolinux-2.08-memtest86+-cdtar.tar.bz2
livecd/iso: /home/jhuebel/2004.2/minimal-amd64-2004.2-test2.iso
#livecd/gk_mainargs: --makeopts=-j3
livecd/bootsplash: livecd-2004.2

#livecd/type: gentoo-release-universal
livecd/type: gentoo-release-minimal
livecd/blacklist: siimage

boot/kernel: gentoo smp
boot/kernel/gentoo/sources: sys-kernel/gentoo-dev-sources
boot/kernel/gentoo/config: /home/jhuebel/2004.2/20040627-amd64-uni-2.6.7-r6.config
#boot/kernel/gentoo/gk_kernargs: --makeopts=-j2
boot/kernel/smp/sources: sys-kernel/gentoo-dev-sources
#boot/kernel/smp/gk_kernargs: --makeopts=-j1
boot/kernel/smp/config: /home/jhuebel/2004.2/20040627-amd64-smp-2.6.7-r6.config

#this next line sets any USE settings you want exported to the environment for
#your kernel build *and* during the build of any kernel-dependent packages
boot/kernel/gentoo/use: pcmcia usb
boot/kernel/smp/use: pcmcia usb

#use this next option to add an extension to the name of your kernel. This
#allows you to have 2 identical kernels on the livecd built with different
#options, and each with their own modules dir in /lib/modules (otherwise
#the second kernel would overwrite the first modules directory.
boot/kernel/gentoo/extraversion: livecd
boot/kernel/smp/extraversion: livecd

#this next line is for merging kernel-dependent packages after your kernel
#is built. This is where you merge third-party ebuilds that contain kernel
#modules.
boot/kernel/gentoo/packages: pcmcia-cs slmodem linux-wlan-ng iptables hostap-driver fcpci
boot/kernel/smp/packages: pcmcia-cs iptables fcpci hostap-driver

livecd/unmerge:
	autoconf automake bin86 binutils libtool m4 bison ld.so make perl patch linux-headers man-pages
	sash bison flex gettext texinfo ccache addpatches man groff lib-compat gcc python miscfiles
livecd/empty:
	/var/tmp
	/var/cache
	/var/db
	/var/empty
	/var/cache
	/var/lock
	/var/log
	/tmp
	/usr/portage
	/usr/share/man
	/usr/share/info
	/usr/share/unimaps
	/usr/include
	/usr/share/zoneinfo
	/usr/share/dict
	/usr/share/doc
	/usr/share/ss
	/usr/share/state
	/usr/share/texinfo
	/usr/lib/python2.2
	/usr/lib/portage
	/usr/share/gettext
	/usr/share/i18n
	/usr/share/rfc
	/usr/X11R6/man
	/usr/X11R6/include
	/usr/X11R6/lib/X11/config
	/usr/X11R6/lib/X11/etc
	/usr/X11R6/lib/X11/doc
	/usr/src
	/usr/share/doc
	/usr/share/man
	/root/.ccache
livecd/rm:
	/lib/*.a
	/usr/lib/*.a
	/usr/lib/gcc-lib/*/*/libgcj*
	/usr/X11R6/lib/*.a
