# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/netboot-base/sbin/functions.sh,v 1.1 2004/10/06 14:44:47 vapier Exp $

# Stripped down version of gentoo-src/rc-scripts/sbin/functions.sh

if [ "$(/sbin/consoletype 2> /dev/null)" = "serial" ]
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
	[ -n "`grep nocolor /proc/cmdline`" ] && RC_NOCOLOR="yes"
fi

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

if [ "${RC_ENDCOL}" == "yes" ] ; then
	COLS=${COLUMNS:-0}		# bash's internal COLUMNS variable
	(( COLS == 0 )) && COLS=$(stty size 2>/dev/null | cut -d' ' -f2)
	(( COLS -= 7 ))			# width of [ ok ]
	if (( COLS <= 0 )); then
		# Sanity check ... with serial consoles and such,
		# COLS may up being negative ...
		(( COLS = 80 ))
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
