#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/support/livecdfs-update.sh,v 1.47 2006/05/09 12:20:07 wolf31o2 Exp $

. /tmp/chroot-functions.sh

update_env_settings

# Allow root logins to the livecd by default
if [ -e /etc/sshd/sshd_config ]
then
	sed -i 's:^#PermitRootLogin\ yes:PermitRootLogin\ yes:' \
		/etc/ssh/sshd_config
fi

# Turn off udev tarball
sed -i 's:RC_DEVICE_TARBALL="yes":RC_DEVICE_TARBALL="no":' /etc/conf.d/rc

# Clean up the time and set to UTC
rm -rf /etc/localtime
cp /usr/share/zoneinfo/UTC /etc/localtime

# Setup the hostname
if [ "${clst_livecd_type}" == "gentoo-gamecd" ]
then
	echo 'HOSTNAME="gamecd"' > /etc/conf.d/hostname
	echo "127.0.0.1 gamecd.gentoo gamecd localhost" > /etc/hosts
else
	echo 'HOSTNAME="livecd"' > /etc/conf.d/hostname
	echo "127.0.0.1 livecd.gentoo livecd localhost" > /etc/hosts
fi
echo 'OVERRIDE=0' > /etc/conf.d/domainname
echo 'DNSDOMAIN="gentoo"' >> /etc/conf.d/domainname

# Add any users
if [ -n "${clst_livecd_users}" ]
then
	# Here we check to see if games exists for bug #125498
	if [ "$(getent group games | cut -d: -f1)" != "games" ]
	then
		echo "Adding games group"
		groupadd -g 35 games
	fi
	for x in ${clst_livecd_users}
	do
		useradd -G users,wheel,audio,games,cdrom,usb -c "Default LiveCD User" \
			-m $x
		if [ -n "${clst_livecd_xdm}" -a -n "${clst_livecd_xsession}" ]
		then
			echo "[Desktop]" > /home/$x/.dmrc
			echo "Session=${clst_livecd_xsession}" >> /home/$x/.dmrc
			chown -R $x:users /home/$x
		fi
	done
fi

# Setup sudoers
if [ -f /etc/sudoers ]
then
	sed -i '/NOPASSWD: ALL/ s/^# //' /etc/sudoers
fi

# Setup links for ethernet devices
cd /etc/init.d
ln -sf net.lo net.eth1
ln -sf net.lo net.eth2
ln -sf net.lo net.eth3
ln -sf net.lo net.eth4

# Add this for hwsetup/mkx86config
mkdir -p /etc/sysconfig

# fstab tweaks
echo "tmpfs	/					tmpfs	defaults	0 0" > /etc/fstab
echo "tmpfs	/lib/firmware			tmpfs	defaults	0 0" >> /etc/fstab
echo "tmpfs	/usr/portage			tmpfs	defaults	0 0" >> /etc/fstab
# If /usr/lib/X11/xkb/compiled then make it tmpfs
if [ -d /usr/lib/X11/xkb/compiled ]
then
	echo "tmpfs	/usr/lib/X11/xkb/compiled	tmpfs	defaults	0 0" >> \
		/etc/fstab
fi

# devfs tweaks
[ -e /etc/devfsd.conf ] && sed -i '/dev-state/ s:^:#:' /etc/devfsd.conf

# Tweak the livecd fstab so that users know not to edit it
# http://bugs.gentoo.org/show_bug.cgi?id=60887
mv /etc/fstab /etc/fstab.old
echo "####################################################" >> /etc/fstab
echo "## ATTENTION: THIS IS THE FSTAB ON THE LIVECD	 ##" >> /etc/fstab
echo "## PLEASE EDIT THE FSTAB at /mnt/gentoo/etc/fstab ##" >> /etc/fstab	 
echo "####################################################" >> /etc/fstab
cat /etc/fstab.old >> /etc/fstab
rm /etc/fstab.old

# Add some helpful aliases
echo "alias cp='cp -i'" >> /etc/profile
echo "alias mv='mv -i'" >> /etc/profile
echo "alias rm='rm -i'" >> /etc/profile
echo "alias ls='ls --color=auto'" >> /etc/profile
echo "alias ll='ls -l'" >> /etc/profile
echo "alias grep='grep --color=auto'" >> /etc/profile

# Make sure we have the latest pci,usb and hotplug ids
[ -x /sbin/update-pciids ] && /sbin/update-pciids
[ -x /sbin/update-usbids ] && /sbin/update-usbids
if [ -d /usr/share/hwdata ]
then
	[ -f /usr/share/hwdata/pci.ids ] && rm -f /usr/share/hwdata/pci.ids
	[ -f /usr/share/hwdata/usb.ids ] && rm -f /usr/share/hwdata/usb.ids
	ln -s /usr/share/misc/pci.ids /usr/share/hwdata/pci.ids
	ln -s /usr/share/misc/usb.ids /usr/share/hwdata/usb.ids
fi

# Setup opengl in /etc (if configured)
[ -x /usr/sbin/openglify ] && /usr/sbin/openglify

# Setup configured display manager
if [ -n "${clst_livecd_xdm}" ]
then
	sed -i "s:#DISPLAYMANAGER=\"xdm\":DISPLAYMANAGER=\"${clst_livecd_xdm}\":" \
		/etc/rc.conf
	rc-update add xdm default
fi

# Setup configured default X Session
if [ -n "${clst_livecd_xsession}" ]
then
	sed -i "s:#XSESSION=\"Gnome\":XSESSION=\"${clst_livecd_xsession}\":" \
		/etc/rc.conf
fi

# touch /etc/asound.state
touch /etc/asound.state

# Tweak the MOTD for Gentoo releases 
case ${clst_livecd_type} in
	gentoo-release-universal )
		cat /etc/generic.motd.txt /etc/universal.motd.txt \
			/etc/minimal.motd.txt > /etc/motd
		sed -i 's:^##GREETING:Welcome to the Gentoo Linux Universal Installation CD!:' /etc/motd
	;;
	gentoo-release-minimal )
		cat /etc/generic.motd.txt /etc/minimal.motd.txt > /etc/motd
		sed -i 's:^##GREETING:Welcome to the Gentoo Linux Minimal Installation CD!:' /etc/motd
	;;
	gentoo-release-livecd )
		cat /etc/generic.motd.txt \
			/etc/minimal.motd.txt /etc/livecd.motd.txt > /etc/motd
		sed -i -e 's:^##GREETING:Welcome to the Gentoo Linux LiveCD!:' \
			-e "s:##DISPLAY_MANAGER:${clst_livecd_xdm}:" /etc/motd
	;;
	gentoo-gamecd )
		cat /etc/generic.motd.txt /etc/gamecd.motd.txt > /etc/motd
		sed -i 's:^##GREETING:Welcome to the Gentoo Linux ##GAME_NAME GameCD!:' /etc/motd
	;;
esac

rm -f /etc/generic.motd.txt /etc/universal.motd.txt /etc/minimal.motd.txt /etc/livecd.motd.txt /etc/gamecd.motd.txt

# Setup splash/bootsplash (if called for)
if [ "${clst_livecd_splash_type}" == "bootsplash" -a -n \
	"${clst_livecd_splash_theme}" ]
then
	if [ -d /etc/bootsplash/${clst_livecd_splash_theme} ]
	then
		sed -i 's:BOOTSPLASH_THEME=\"gentoo\":BOOTSPLASH_THEME=\"${clst_livecd_splash_theme}\":' /etc/conf.d/bootsplash
		rm -f /etc/bootsplash/default
		ln -s "/etc/bootsplash/${clst_livecd_splash_theme}" \
			/etc/bootsplash/default
	else
		echo "Error, cannot setup bootsplash theme ${clst_livecd_splash_theme}"
		exit 1
	fi
elif [ "${clst_livecd_splash_type}" == "gensplash" -a -n \
	"${clst_livecd_splash_theme}" ]
then
	if [ -d /etc/splash/${clst_livecd_splash_theme} ]
	then
		sed -i 's:# SPLASH_THEME="gentoo":SPLASH_THEME=\"${clst_livecd_splash_theme}\":' /etc/conf.d/splash
		rm -f /etc/splash/default
		ln -s /etc/splash/${clst_livecd_splash_theme} /etc/splash/default
	else
		echo "Error, cannot setup splash theme ${clst_livecd_splash_theme}"
		exit 1
	fi
fi

# Create firmware directory if it does not exist
[ ! -d /lib/firmware ] && mkdir -p /lib/firmware

# tar up the firmware so that it does not get clobbered by the livecd mounts
if [ -n "$(ls /lib/firmware)" ]
then
	cd /lib/firmware
	if [ -n "$(ls /usr/lib/hotplug/firmware)" ]
	then
		cp /usr/lib/hotplug/firmware/* /lib/firmware
	fi
	/bin/tar cjpf /lib/firmware.tar.bz2 .
	rm -f /lib/firmware/*
	mkdir -p /usr/lib/hotplug
	rm -rf /usr/lib/hotplug/firmware
	ln -sf /lib/firmware /usr/lib/hotplug/firmware
fi

# Clear out locales
case ${clst_livecd_type} in
	gentoo-release-minimal|gentoo-release-universal|gentoo-gamecd)
		rm -rf /usr/lib/locale/{a,b,c,d,e{l,n_{A,B,C,D,G,H,I,N,P,S,US.,Z},s,t,u},f,g,h,i,j,k,l,m,n,o,p,r,s,t,u,v,w,x,y,z}*
	;;
esac

# Post configuration
case ${clst_livecd_type} in
	gentoo-gamecd )
		# We grab our configuration
		if [ -e /tmp/gamecd.conf ]
		then
			source /tmp/gamecd.conf || exit 1
			rm /tmp/gamecd.conf

			# Here we replace out game information into several files
			sed -i -e "s:##GAME_NAME:${GAME_NAME}:" /etc/motd

			# Here we setup our xinitrc
			echo "exec ${GAME_EXECUTABLE}" > /etc/X11/xinit/xinitrc
		fi

		# This is my hack to reduce tmpfs usage
		mkdir -p /usr/livecd/db/pkg/x11-base
		mv -f /var/db/pkg/x11-base/xorg* /usr/livecd/db/pkg/x11-base
		rm -rf /var/db

		touch /etc/startx
		;;
	gentoo-release-livecd )
		# First we setup the livecd-kernel package
		if [ -e /opt/installer/misc/mkvardb ]
		then
			chmod +x /opt/installer/misc/mkvardb
			/opt/installer/misc/mkvardb -p livecd-kernel -c sys-kernel -v ${clst_version_stamp} --provide "virtual/alsa" /boot/kernel* /boot/initr* $(for i in $(find "/lib/modules/" -type f); do grep --quiet "${i}" /var/db/pkg/*/*/CONTENTS || echo ${i}; done)
		fi

		# Setup Gnome theme
		if [ "${clst_livecd_xsession}" == "gnome" ]
		then
			gconftool-2 --direct \
				--config-source xml:readwrite:/etc/gconf/gconf.xml.defaults \
				--type string --set /desktop/gnome/interface/icon_theme Clearlooks
			gconftool-2 --direct \
				--config-source xml:readwrite:/etc/gconf/gconf.xml.defaults \
				--type string --set /desktop/gnome/interface/theme Clearlooks
			gconftool-2 --direct \
				--config-source xml:readwrite:/etc/gconf/gconf.xml.defaults \
				--type string --set /apps/metacity/general/theme Clearlooks
			gconftool-2 --direct \
				--config-source xml:readwrite:/etc/gconf/gconf.xml.defaults \
				--type string --set /desktop/gnome/interface/gtk_key_theme \
				Clearlooks
			gconftool-2 --direct \
				--config-source xml:readwrite:/etc/gconf/gconf.xml.defaults \
				--type string --set /desktop/gnome/interface/gtk_theme \
				Clearlooks
			gconftool-2 --direct \
				--config-source xml:readwrite:/etc/gconf/gconf.xml.defaults \
				--type string --set /desktop/gnome/interface/font_name "Sans 9"
		fi

		# Setup GDM
		if [ "${clst_livecd_xdm}" == "gdm" ]
		then
			cp -f /etc/X11/gdm/gdm.conf /etc/X11/gdm/gdm.conf.old
			sed -e 's:TimedLoginEnable=false:TimedLoginEnable=true:' \
				-e 's:TimedLoginDelay=30:TimedLoginDelay=10:' \
				-e 's:AllowRemoteRoot=true:AllowRemoteRoot=false:' \
				-e 's:#GraphicalTheme=circles:GraphicalTheme=gentoo-emergence:' \
				-e ':^#GraphicalTheme=: s:^#::' \
				-i /etc/X11/gdm/gdm.conf
			if [ -n "${clst_livecd_users}" -a -n "${first_user}" ]
			then
				sed -e "s:TimedLogin=:TimedLogin=${first_user}:" \
					-i /etc/X11/gdm/gdm.conf
			else
				sed -e "s:TimedLogin=:TimedLogin=gentoo:" \
					-i /etc/X11/gdm/gdm.conf
			fi
		fi

		# This gives us our list of system packages for the installer
		mkdir -p /usr/livecd
		USE="-* $(cat /var/db/pkg/sys-libs/glibc*/USE)" emerge -ep system | grep -e '^\[ebuild' | sed -e 's:^\[ebuild .\+\] ::' > /usr/livecd/systempkgs.txt

		# This is my hack to reduce tmpfs usage
		cp -r /usr/portage/profiles /usr/livecd
		cp -r /usr/portage/eclass /usr/livecd
		rm -rf /usr/livecd/profiles/{co*,default-{1*,a*,b*,d*,h*,i*,m*,p*,s*,x*},g*,hardened-*,n*,x*}
		mv -f /etc/gconf /usr/livecd
		mv -f /var/db /usr/livecd

		# This gives us a proper cache for portage/installer
		tar cjf /usr/livecd/metadata.tar.bz2 /var/cache/edb/dep/usr/portage

		# We remove kernel sources from our vdb
		rm -rf /usr/livecd/db/pkg/sys-kernel/*sources*

		# Clear out lastlog
		rm -f /var/log/lastlog && touch /var/log/lastlog

		# Create our installer icons
		if [ -e /usr/share/applications/installer-gli.desktop ]
		then
			if [ -n "${clst_livecd_users}" ]
			then
				for username in ${clst_livecd_users}
				do
					mkdir -p /home/${username}/Desktop
					cp /usr/share/applications/installer-gtk.desktop \
						/home/${username}/Desktop
					cp /usr/share/applications/installer-faq.desktop \
						/home/${username}/Desktop
					cp /usr/share/applications/installer-dialog.desktop \
						/home/${username}/Desktop
					sed -e 's:Exec=installer:Exec=sudo installer:' \
						/home/${username}/Desktop/installer-dialog.desktop
					sed -e 's:Exec=installer:Exec=sudo installer:' \
						/home/${username}/Desktop/installer-gtk.desktop
					chown -R ${username}:100 /home/${username}
				done
			fi
		fi
		;;
	generic-livecd )
		# This is my hack to reduce tmpfs usage
		mkdir -p /usr/livecd
		mv -f /etc/gconf /usr/livecd
		if [ -e /usr/livecd/grppkgs.txt ]
		then
			rm -f /usr/livecd/grppkgs.txt
		fi
		if [ -e /usr/livecd/kernelpkgs.txt ]
		then
			rm -f /usr/livecd/kernelpkgs.txt
		fi

		touch /etc/startx
		;;
	* )
		if [ -e /usr/livecd/grppkgs.txt ]
		then
			rm -f /usr/livecd/grppkgs.txt
		fi
		if [ -e /usr/livecd/kernelpkgs.txt ]
		then
			rm -f /usr/livecd/kernelpkgs.txt
		fi
		;;
esac

# We want the first user to be used when auto-starting X
if [ -n "${clst_livecd_users}" -a -e /etc/startx ]
then
	first_user=$(echo ${clst_livecd_users} | cut -d' ' -f1)
	sed -i "s/##STARTX/source /etc/profile && su - $first_user -c startx/" \
		/root/.bashrc
fi

if [ -e /lib/rcscripts/addons/udev-start.sh ]
then
	sed -i "s:\t\[\[ -x /sbin/evms_activate:\t\[\[ -x \${CDBOOT} \]\] \&\& \[\[ -x /sbin/evms_activate:" /lib/rcscripts/addons/udev-start.sh
fi
