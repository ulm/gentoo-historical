subarch: pentium3
version_stamp: 2004.3
target: grp
rel_type: default
profile: default-linux/x86/2004.3
snapshot: 20041022
source_subpath: default/stage3-pentium3-2004.3
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
	cups
	ldap
	ssl
	tcpd
	-svga

grp/src/type: srcset
grp/src/packages:
	ucl
	udev
	gentoo-sources
	gentoo-dev-sources
	vanilla-sources
	development-sources
	rp-pppoe
	speedtouch
	fcpci
	globespan-adsl
	pptpclient
	slmodem
	lvm2
	iputils
	vixie-cron
	fcron
	dcron
	sysklogd
	metalog
	syslog-ng
	raidtools
	jfsutils
	xfsprogs
	reiserfsprogs
	lvm2
	dosfstools
	lilo
	grub
	gentoolkit
	chkrootkit
	isdn4k-utils
	iproute2
	nvidia-kernel
	nvidia-glx
	ati-drivers
	wireless-tools
	pcmcia-cs
	genkernel
	
grp/cd2/type: pkgset
grp/cd2/packages:
	pciutils
	hotplug
	dante
	tsocks
	sys-apps/eject
	xorg-x11
	=x11-base/xorg-x11-6.7.0-r1
	minicom
	links
	lynx
	acpid
	parted
	whois
	tcpdump
	cvs
	unzip
	zip
	netcat
	partimage
	DirectFB
	apache
	app-cdr/cdrtools
	gnome
	evolution
	cups
	dev-db/mysql
	dev-lang/ruby
	emacs
	enlightenment
	fluxbox
	kde
	libsdl
	mozilla
	xfce4
	openbox
	fluxbox
	openoffice-bin
	sylpheed
	vim
	xemacs
	xmms
	mozilla-firefox
	mozilla-thunderbird
	abiword
	gaim
	xchat
	tetex
	xcdroast
	k3b
	samba
	nmap
	gradm
	ettercap
	logrotate
