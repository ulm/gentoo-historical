# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/lcdsplash/splash-functions.sh,v 1.1 2004/10/14 04:40:51 vapier Exp $

source /etc/lcdsplash.conf

splash() {
	local func="$1"
	shift

	case "${func}" in
		svc_start)   to_lcd "->$1";;
		svc_stop)    to_lcd "<-$1";;
		svc_started) to_lcd ">>$1";;
		svc_stopped) to_lcd "<<$1";;
		rc_init)     to_lcd "INIT: $1";;
		rc_exit)     to_lcd $'\x0';;
		critical)    to_lcd "!!$*";;
	esac

	return 0
}

to_lcd() {
	echo "$@" > "${LCD_FILE}"
}
