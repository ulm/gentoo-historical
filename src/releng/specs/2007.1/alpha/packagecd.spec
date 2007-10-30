subarch: alpha
version_stamp: 2007.1
target: grp
rel_type: default
profile: default-linux/alpha/2007.1
snapshot: 2007.1
source_subpath: default/stage3-alpha-2007.1
grp: cd2

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
	-tiff
	-directfb

grp/cd2/type: pkgset
grp/cd2/packages:
	pciutils
	hotplug
	dante
	tsocks
	sys-apps/eject
	xorg-x11
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
#	DirectFB
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
	fluxbox
	sylpheed
	vim
	xemacs
	xmms
	mozilla-firefox
	mozilla-thunderbird
	abiword
	pidgin
	xchat
	tetex
	samba
	nmap
	ettercap
	logrotate
