subarch: ppc64
version_stamp: 2007.0-distfiles
target: grp
rel_type: default
profile: default-linux/ppc/ppc64/2007.0/32bit-userland
snapshot: 2007.0
source_subpath: default/stage3-ppc64-32ul-2007.0
grp: src

grp/use: 
	cdr
	dvd
	dvdr
	ruby
	-X
	-gtk

grp/src/type: srcset
grp/src/packages:
	hfsutils
	hfsplusutils
	dhcpcd
	slocate
	udev
	dcron
	fcron
	vixie-cron
	gentoo-sources
	vanilla-sources
	coldplug
	syslog-ng
	logrotate
	nfs-utils
	jfsutils
	xfsprogs
	e2fsprogs
	reiserfsprogs
	iputils
	lvm2
	evms
	mdadm
	ethtool
	genkernel
	yaboot
	pcmcia-cs
	yaboot
	usbutils
	pciutils
	iprutils
	ssmtp
	ibm-powerpc-utils-papr
	rp-pppoe




