subarch: hppa
version_stamp: 20040227
target: livecd-stage2
rel_type: default
rel_version: 2004.0
snapshot: 20040227
source_subpath: default-hppa-2004.0/livecd-stage1-hppa-20040227
livecd/cdfstype: normal
livecd/archscript: examples/livecd/runscript/hppa-archscript.sh
livecd/runscript: examples/livecd/runscript/default-runscript.sh
livecd/cdtar: examples/livecd/cdtar/palo-1.2_pre20030630-cdtar.tar.bz2
boot/kernel: vmlinux32
boot/kernel/vmlinux32/sources: sys-kernel/hppa-sources
boot/kernel/vmlinux32/config: examples/livecd/hppa/config-2.4.24
#this next line sets any USE settings you want exported to the environment for
#your kernel build *and* during the build of any kernel-dependent packages
boot/kernel/vmlinux32/use: xfs
#use this next option to add an extension to the name of your kernel. This
#allows you to have 2 identical kernels on the livecd built with different
#options, and each with their own modules dir in /lib/modules (otherwise
#the second kernel would overwrite the first modules directory.
boot/kernel/vmlinux32/extraversion: livecd
#this next line is for merging kernel-dependent packages after your kernel
#is built. This is where you merge third-party ebuilds that contain kernel
#modules.
#boot/kernel/gentoo/packages: =sys-apps/pcmcia-cs-3.2.5-r1
livecd/unmerge:
	autoconf automake bin86 binutils libtool m4 bison ld.so make perl patch linux-headers man-pages
	sash bison flex gettext texinfo ccache addpatches man groff lib-compat gcc python miscfiles ucl
livecd/empty:
	/var/tmp
	/var/cache
	/var/db
	/var/empty
	/var/cache
	/var/lock
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
	/usr/lib/python2.3
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
