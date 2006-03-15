# $Header: /var/cvsroot/gentoo/src/releng/specs/2006.0/ppc64/Attic/ppc64-livecd-grp.spec,v 1.1 2006/03/15 17:04:05 ranger Exp $
subarch: ppc64
version_stamp: 2006.0
target: grp
rel_type: default 
profile:  default-linux/ppc/ppc64/2006.0/32bit-userland
snapshot: 20060123 
source_subpath: default/stage3-ppc64-2006.0-32ul
grp: cd2

chost: powerpc-unknownlinux-gnu
cflags: -O2 -pipe
cxxflags: -O2 -pipe

grp/use: 
	-java
	dvdr
	imap
	ldap

grp/cd2/type: pkgset
grp/cd2/packages:
	xorg-x11
	gentoo-sources
	irssi
	gpm
	parted
	links
	dosfstools
	hfsutils
	hfsplusutils
	screen
	mirrorselect
	vim
	xscreensaver
	ide-smart
	netcat
	gnupg
	sys-apps/eject
	minicom
	whois
	tcpdump
	cvs
	zip
	unzip
	partimage
	samba
	cups
	app-admin/sudo
	app-cdr/cdrtools
	cdrdao
	emacs
	xemacs
	dev-lang/ruby
	enlightenment
	mozilla-firefox
	xfce4
	fluxbox
	sylpheed
	gnome
	xmms
	gaim
	xchat
	tetex
	kile
	nmap
	ettercap
	mplayer

