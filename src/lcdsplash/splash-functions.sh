# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/lcdsplash/splash-functions.sh,v 1.2 2004/11/17 01:52:42 vapier Exp $

lcddir="/lib/rcscripts/lcdsplash"
source /etc/lcdsplash.conf

lcdsplash_start()    { :;}
lcdsplash_stop()     { :;}
lcdsplash_started()  { :;}
lcdsplash_stopped()  { :;}
lcdsplash_init()     { :;}
lcdsplash_exit()     { :;}
lcdsplash_critical() { :;}

if [ -n "${LCD_MODULE}" ] && [ -e "${lcddir}/${LCD_MODULE}" ] ; then
	source "${lcddir}/${LCD_MODULE}"
fi

splash() {
	local func="$1"
	shift

	case "${func}" in
		svc_start)   lcdsplash_start "$@";;
		svc_stop)    lcdsplash_stop "$@";;
		svc_started) lcdsplash_started "$@";;
		svc_stopped) lcdsplash_stopped "$@";;
		rc_init)     lcdsplash_init "$@";;
		rc_exit)     lcdsplash_exit "$@";;
		critical)    lcdsplash_critical "$@";;
	esac

	return 0
}
