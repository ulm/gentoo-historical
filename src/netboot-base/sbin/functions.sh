# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/netboot-base/sbin/functions.sh,v 1.3 2005/01/10 14:22:22 gmsoft Exp $

# Stripped down version of gentoo-src/rc-scripts/sbin/functions.sh

if [ "$(/sbin/consoletype)" = "serial" ]
then
	# We do not want colors/endcols on serial terminals
	RC_NOCOLOR="${RC_NOCOLOR:-yes}"
	RC_ENDCOL="no"
else
	RC_NOCOLOR="${RC_NOCOLOR:-no}"
	RC_ENDCOL="yes"
fi
if [ -r /proc/cmdline ]
then
	grep -q nocolor /proc/cmdline && RC_NOCOLOR="yes"
fi

# This function if required to kill devfsd and busybox because busybox
# think the executable name is busybox.
my_pidof() {
	[ "${1}" = "" ] && return
	ps aux | grep "${1}" | grep -v grep | awk '{ print $1 }'

}

eerror() {
	if [ "${RC_QUIET_STDOUT}" = "yes" ]
	then
		echo " ${*}" >/dev/stderr
	else
		echo -e " ${BAD}*${NORMAL} ${*}"
	fi

	return 0
}

ebegin() {
	if [ "${RC_QUIET_STDOUT}" != "yes" ]
	then
		if [ "${RC_ENDCOL}" = "yes" ]
		then
			echo -e " ${GOOD}*${NORMAL} ${*}..."
		else
			echo -ne " ${GOOD}*${NORMAL} ${*}..."
		fi
	fi

	return 0
}

eend() {
	local retval=

	if [ "$#" -eq 0 ] || ([ -n "$1" ] && [ "$1" -eq 0 ])
	then
		if [ "${RC_QUIET_STDOUT}" != "yes" ]
		then
			echo -e "${ENDCOL}  ${BRACKET}[ ${GOOD}ok${BRACKET} ]${NORMAL}"
		fi
	else
		retval="$1"
		
		if [ "$#" -ge 2 ]
		then
			shift
			eerror "${*}"
		fi
		if [ "${RC_QUIET_STDOUT}" != "yes" ]
		then
			echo -e "${ENDCOL}  ${BRACKET}[ ${BAD}!!${BRACKET} ]${NORMAL}"
			# extra spacing makes it easier to read
			echo
		fi
		return ${retval}
	fi

	return 0
}

if [ "${RC_ENDCOL}" = "yes" ] ; then
	COLS=${COLUMNS:-0}		# bash's internal COLUMNS variable
	[ ${COLS} -eq 0 ] && COLS=$(stty size | cut -d' ' -f2)
	COLS=$(( ${COLS} - 7 ))			# width of [ ok ]
	if [ ${COLS} -le 0 ]; then
		# Sanity check ... with serial consoles and such,
		# COLS may up being negative ...
		COLS=80
	fi
	ENDCOL=$'\e[A\e['${COLS}'G'
else
	ENDCOL=""
fi
if [ "${RC_NOCOLOR}" = "yes" ]; then
	unset GOOD WARN BAD NORMAL HILITE BRACKET
else
	GOOD=$'\e[32;01m'
	WARN=$'\e[33;01m'
	BAD=$'\e[31;01m'
	NORMAL=$'\e[0m'
	HILITE=$'\e[36;01m'
	BRACKET=$'\e[34;01m'
fi
