subarch: amd64
version_stamp: 20040716
target: grp
rel_type: default
profile: default-amd64-2004.2
snapshot: 20040716-r2
source_subpath: default/stage3-amd64-20040716
grp: src cd2

grp/use: 
	gtk2 
	gnome 
	kde 
	qt 
	bonobo 
	cdr 
	esd 
	gtkhtml 
	mozilla
	mysql
	perl
	ruby
	tcltk
	acl
	cups
	ldap
	ssl
	tcpd
	-svga

grp/src/type: srcset
grp/src/packages:
	xorg-x11
#	gentoo-sources
	gentoo-dev-sources
#	vanilla-sources
#	development-sources
#	mm-sources
	iptables
	gpm
	rp-pppoe
	ppp
	speedtouch
	pciutils
	hdparm
	hotplug
	aumix
	iputils
	vixie-cron
	sysklogd
	metalog
	syslog-ng
	raidtools
	jfsutils
	xfsprogs
	reiserfsprogs
	lvm-user
	dosfstools
#	lilo
	grub-static
	superadduser
	gentoolkit
	chkrootkit
	minicom
	lynx
	rpm2targz
	parted
	rdate
	whois
	tcpdump
	cvs
	unzip
	zip
	netcat
	isdn4k-utils
#	nforce-net
#	nforce-audio
#	iproute
	nvidia-kernel
	nvidia-glx
#	ati-drivers
#	e100
#	e1000
	wireless-tools
	pcmcia-cs
#	emu10k1
	evms
#	linux-wlan-ng
	sys-apps/eject
	genkernel

grp/cd2/type: pkgset
grp/cd2/packages:

