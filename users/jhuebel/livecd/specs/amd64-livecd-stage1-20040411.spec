subarch: amd64
version_stamp: 20040411
target: livecd-stage1
rel_type: default
rel_version: 2004.1
profile: default-amd64-2004.0
snapshot: 20040411
source_subpath: default-amd64-2004.1/stage3-amd64-20040411
livecd/use:
	-X
	-gtk
	-svga
	fbcon
	livecd
livecd/packages:
	>=sys-apps/baselayout-1.8.6.12-r4
	kudzu
	module-init-tools
	hotplug
	>=glib-2
	irssi
	aumix
	metalog
	pciutils
	parted
	mt-st
	links
	star
	strace
	raidtools
	nfs-utils
	jfsutils
	usbutils
	speedtouch
	xfsprogs
	e2fsprogs
	reiserfsprogs
	hdparm
	nano
	less
	openssh
	dhcpcd
	mingetty
	pwgen
	popt
	dialog
	rp-pppoe
	gpm
	screen
	mirrorselect
	iputils
	hwdata-knoppix
	hwsetup
	bootsplash
	device-mapper
	lvm2
	livecd-tools
	ucl
	wireless-tools
#	gpart
