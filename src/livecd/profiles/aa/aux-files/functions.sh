# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/livecd/profiles/aa/aux-files/Attic/functions.sh,v 1.1 2003/10/19 03:10:50 livewire Exp $

umask 022

if [ -z "${EBUILD}" ]
then
	# Setup a basic $PATH.  Just add system default to existing.
	# This should solve both /sbin and /usr/sbin not present when
	# doing 'su -c foo', or for something like:  PATH= rcscript start
	PATH="/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/sbin:${PATH}"
fi

# daemontools dir
SVCDIR="/var/lib/supervise"

# Check /etc/conf.d/rc for a description of these ...
svcdir="/var/lib/init.d"
svcmount="no"
svcfstype="tmpfs"
svcsize=1024
shmdir="/mnt/.shm"

# Different types of dependencies
deptypes="need use"
# Different types of order deps
ordtypes="before after"

#
# Internal variables
#

# Dont output to stdout?
RC_QUIET_STDOUT="no"

# Should we use color?
RC_NOCOLOR="no"

#
# Default values for rc system
#
RC_NET_STRICT_CHECKING="no"

# Override defaults with user settings ...
[ -f /etc/conf.d/rc ] && source /etc/conf.d/rc


getcols() {
	echo "$2"
}

# Should we use colors ?
if [ -n "${EBUILD}" ] && [ "${*/depend}" = "$*" ]
then
	# Check user pref in portage
    RC_NOCOLOR="`python -c 'import portage; print portage.settings["NOCOLOR"]' 2> /dev/null`"

elif [ -n "${EBUILD}" ] && [ "${*/depend}" != "$*" ]
then
	# We do not want colors or stty to run during emerge depend
    RC_NOCOLOR="yes"
	
elif [ "`/bin/consoletype 2> /dev/null`" = "serial" ]
then
	# We do not want colors on serial terminals
	RC_NOCOLOR="yes"
else
	# Lastly check if the user disabled it with --nocolor argument
	for arg in $*
	do
		case "${arg}" in
			--nocolor)
				RC_NOCOLOR="yes"
				;;
		esac
	done
fi

if [ "${RC_NOCOLOR}" = "yes" ]
then
	COLS="25 80"
	ENDCOL=

	if [ -n "${EBUILD}" ] && [ "${*/depend}" = "$*" ]
	then
		stty cols 80 &>/dev/null
		stty rows 25 &>/dev/null
	fi
else
	COLS="`stty size 2> /dev/null`"
	COLS="`getcols ${COLS}`"
	COLS=$((${COLS} - 7))
	ENDCOL=$'\e[A\e['${COLS}'G'    # Now, ${ENDCOL} will move us to the end of the
	                               # column;  irregardless of character width
fi

if [ "${RC_NOCOLOR}" = "yes" ]
then
	GOOD=""
	WARN=""
	BAD=""
	NORMAL=""

	HILITE=""
	BRACKET=""
else
	GOOD=$'\e[32;01m'
	WARN=$'\e[33;01m'
	BAD=$'\e[31;01m'
	NORMAL=$'\e[0m'

	HILITE=$'\e[36;01m'
	BRACKET=$'\e[34;01m'
fi

# void esyslog(char* priority, char* tag, char* message)
#
#    use the system logger to log a message
#
esyslog() {
	if [ -x /usr/bin/logger ]
	then
		pri="$1"
		tag="$2"
		
		shift 2
		[ -z "$*" ] && return 0
		
		/usr/bin/logger -p "${pri}" -t "${tag}" -- "$*"
	fi
}

# void einfo(char* message)
#
#    show an informative message (with a newline)
#
einfo() {
	if [ "${RC_QUIET_STDOUT}" = "yes" ]
	then
		return
	else
		echo -e " ${GOOD}*${NORMAL} ${*}"
	fi
}

# void einfon(char* message)
#
#    show an informative message (without a newline)
#
einfon() {
	if [ "${RC_QUIET_STDOUT}" = "yes" ]
	then
		return
	else
		echo -ne " ${GOOD}*${NORMAL} ${*}"
	fi
}

# void ewarn(char* message)
#
#    show a warning message + log it
#
ewarn() {
	if [ "${RC_QUIET_STDOUT}" = "yes" ]
	then
		echo " ${*}"
	else
		echo -e " ${WARN}*${NORMAL} ${*}"
	fi

	# Log warnings to system log
	esyslog "daemon.warning" "rc-scripts" "${*}"
}

# void eerror(char* message)
#
#    show an error message + log it
#
eerror() {
	if [ "${RC_QUIET_STDOUT}" = "yes" ]
	then
		echo " ${*}" >/dev/stderr
	else
		echo -e " ${BAD}*${NORMAL} ${*}"
	fi

	# Log errors to system log
	esyslog "daemon.err" "rc-scripts" "${*}"
}

# void ebegin(char* message)
#
#    show a message indicating the start of a process
#
ebegin() {
	if [ "${RC_QUIET_STDOUT}" = "yes" ]
	then
		return
	else
		if [ "${RC_NOCOLOR}" = "yes" ]
		then
			echo -ne " ${GOOD}*${NORMAL} ${*}..."
		else
			echo -e " ${GOOD}*${NORMAL} ${*}..."
		fi
	fi
}

# void eend(int error, char* errstr)
#
#    indicate the completion of process
#    if error, show errstr via eerror
#
eend() {
	if [ "$#" -eq 0 ] || ([ -n "$1" ] && [ "$1" -eq 0 ])
	then
		if [ "${RC_QUIET_STDOUT}" != "yes" ]
		then
			echo -e "${ENDCOL}  ${BRACKET}[ ${GOOD}ok${BRACKET} ]${NORMAL}"
		fi
	else
		local retval="$1"
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
}

# void ewend(int error, char *warnstr)
#
#    indicate the completion of process
#    if error, show warnstr via ewarn
#
ewend() {
	if [ "$#" -eq 0 ] || ([ -n "$1" ] && [ "$1" -eq 0 ])
	then
		if [ "${RC_QUIET_STDOUT}" != "yes" ]
		then
			echo -e "${ENDCOL}  ${BRACKET}[ ${GOOD}ok${BRACKET} ]${NORMAL}"
		fi
	else
		local retval="$1"
		if [ "$#" -ge 2 ]
		then
			shift
			ewarn "${*}"
		fi
		if [ "${RC_QUIET_STDOUT}" != "yes" ]
		then
			echo -e "${ENDCOL}  ${BRACKET}[ ${WARN}!!${BRACKET} ]${NORMAL}"
			# extra spacing makes it easier to read
			echo
		fi
		return "${retval}"
	fi
}

# bool wrap_rcscript(full_path_and_name_of_rc-script)
#
#    check to see if a given rc-script has syntax errors
#    zero == no errors
#    nonzero == errors
#
wrap_rcscript() {
	local retval=1

	( echo "function test_script() {" ; cat "$1"; echo "}" ) > "${svcdir}/foo.sh"

	if source "${svcdir}/foo.sh" &> /dev/null
	then
		test_script &> /dev/null
		retval=0
	fi
	rm -f "${svcdir}/foo.sh"
	return "${retval}"
}

# int checkserver(void)
#
#    Return 0 (no error) if this script is executed 
#    onto the server, one otherwise.
#    See the boot section of /sbin/rc for more details.
# 
checkserver() {
	# Only do check if 'gentoo=adelie' is given as kernel param
	if get_bootparam "adelie"
	then
		[ "`cat ${svcdir}/hostname`" = "(none)" ] || return 1
	fi
	
	return 0
}

# void init_node(void)
#
#   Initialize an Adelie node.
#
init_node() {
	ebegin "Importing local userspace on node"

	try mount -t tmpfs none "${shmdir}"

	for DIR in /etc /var /root
	do

		if grep -q -v "^${DIR}[[:space:]]" /etc/exports
		then
			mount -o nolock -n server:"${DIR}" "${DIR}"
		fi

		if [ -e "/etc/conf.d/exclude/${DIR}" ]
		then
			find "${DIR}/" -type d | grep -v -f "/etc/conf.d/exclude/${DIR}" \
				> "${shmdir}/${DIR}.lst"
		else
			find "${DIR}/" -type d > "${shmdir}/${DIR}.lst"
		fi

		for SUBDIR in `cat ${shmdir}/${DIR}.lst`
		do
			mkdir -p "${shmdir}/${SUBDIR}"
			chmod --reference="${SUBDIR}" "${shmdir}/${SUBDIR}"
			cp -dp "${SUBDIR}"/* "${shmdir}/${SUBDIR}" &> /dev/null
		done

		if [ -e "/etc/conf.d/exclude/${DIR}" ]
		then
			for EMPTYDIR in `cat "/etc/conf.d/exclude/${DIR}"`
			do
				mkdir -p "${shmdir}/${EMPTYDIR}"
				chmod --reference="${SUBDIR}" "${shmdir}/${SUBDIR}"
			done
		fi

		umount -n "${DIR}" > /dev/null
		mount -n -o bind "${shmdir}/${DIR}" "${DIR}"
	done

	mkdir -p "${shmdir}/tmp"
	chmod 0777 "${shmdir}/tmp"
	mount -n -o bind "${shmdir}/tmp" /tmp

	cat /proc/mounts > /etc/mtab

	cp -f /etc/inittab.node /etc/inittab
	[ -e /etc/fstab.node ] && cp -f /etc/fstab.node /etc/fstab
	killall -1 init

	eend 0
}

# char *KV_major(string)
#
#    Return the Major version part of given kernel version.
#
KV_major() {
	[ -z "$1" ] && return 1

	local KV="`echo $1 | \
		awk '{ tmp = $0; gsub(/^[0-9\.]*/, "", tmp); sub(tmp, ""); print }'`"
	echo "${KV}" | awk -- 'BEGIN { FS = "." } { print $1 }'
}

# char *KV_minor(string)
#
#    Return the Minor version part of given kernel version.
#
KV_minor() {
	[ -z "$1" ] && return 1

	local KV="`echo $1 | \
		awk '{ tmp = $0; gsub(/^[0-9\.]*/, "", tmp); sub(tmp, ""); print }'`"
	echo "${KV}" | awk -- 'BEGIN { FS = "." } { print $2 }'
}

# char *KV_micro(string)
#
#    Return the Micro version part of given kernel version.
#
KV_micro() {
	[ -z "$1" ] && return 1

	local KV="`echo $1 | \
		awk '{ tmp = $0; gsub(/^[0-9\.]*/, "", tmp); sub(tmp, ""); print }'`"
	echo "${KV}" | awk -- 'BEGIN { FS = "." } { print $3 }'
}

# int KV_to_int(string)
#
#    Convert a string type kernel version (2.4.0) to an int (132096)
#    for easy compairing or versions ...
#
KV_to_int() {
	[ -z "$1" ] && return 1
    
	local KV_MAJOR="`KV_major "$1"`"
	local KV_MINOR="`KV_minor "$1"`"
	local KV_MICRO="`KV_micro "$1"`"
	local KV_int="$((KV_MAJOR * 65536 + KV_MINOR * 256 + KV_MICRO))"
    
	# We make version 2.2.0 the minimum version we will handle as
	# a sanity check ... if its less, we fail ...
	if [ "${KV_int}" -ge 131584 ]
	then 
		echo "${KV_int}"

		return 0
	else
		return 1
	fi
}   

# int get_KV()
#
#    return the kernel version (major, minor and micro concated) as an integer
#   
get_KV() {
	local KV="`uname -r 2> /dev/null`"

	echo "`KV_to_int ${KV}`"

	return $?
}

# bool get_bootparam(param)
#
#   return 0 if gentoo=param was passed to the kernel
#
#   EXAMPLE:  if get_bootparam "nodevfs" ; then ....
#
get_bootparam() {
	local copt=""
	local parms=""
	local retval=1
	
	for copt in `cat /proc/cmdline`
	do
		if [ "${copt%=*}" = "gentoo" ]
		then
			params="`gawk -v PARAMS="${copt##*=}" '
				BEGIN { 
					split(PARAMS, nodes, ",")
					for (x in nodes)
						print nodes[x]
				}'`"
			
			# Parse gentoo option
			for x in ${params}
			do
				if [ "${x}" = "$1" ]
				then
					echo YES
					retval=0
				fi
			done
		fi
	done
	return ${retval}
}

# Safer way to list the contents of a directory,
# as it do not have the "empty dir bug".
#
# char *dolisting(param)
#
#    print a list of the directory contents
#
#    NOTE: quote the params if they contain globs.
#          also, error checking is not that extensive ...
#
dolisting() {
	local x=""
	local y=""
	local tmpstr=""
	local mylist=""
	local mypath="${*}"

	if [ "${mypath%/\*}" != "${mypath}" ]
	then
		mypath="${mypath%/\*}"
	fi
	for x in ${mypath}
	do
		if [ ! -e ${x} ]
		then
			continue
		fi
		if [ ! -d ${x} ] && ( [ -L ${x} -o -f ${x} ] )
		then
			mylist="${mylist} `ls ${x} 2> /dev/null`"
		else
			if [ "${x%/}" != "${x}" ]
			then
				x="${x%/}"
			fi
			cd ${x}
			tmpstr="`ls`"
			for y in ${tmpstr}
			do
				mylist="${mylist} ${x}/${y}"
			done
		fi
	done
	echo "${mylist}"
}

# void save_options(char *option, char *optstring)
#
#    save the settings ("optstring") for "option"
#
save_options() {
	local myopts="$1"
	shift
	if [ ! -d ${svcdir}/options/${myservice} ]
	then
		install -d -m0755 ${svcdir}/options/${myservice}
	fi
	echo "$*" > ${svcdir}/options/${myservice}/${myopts}
}

# char *get_options(char *option)
#
#    get the "optstring" for "option" that was saved
#    by calling the save_options function
#
get_options() {
	if [ -f ${svcdir}/options/${myservice}/$1 ]
	then
		cat ${svcdir}/options/${myservice}/$1
	fi
}

# Prelim code to add bootsplash support to Gentoo :)
rc_splash() {
	test -f /proc/splash || return 0
	if [ -n "`grep 'splash=silent' /proc/cmdline 2>/dev/null`" ]; then
		/sbin/splash "$1"
		export progress=$(( ${progress} + 1 ))
	fi
}

# Allows us to save variable info between runlevels (ie. rc iterations)
save_splash_info() {
	if [ -f /proc/splash ]; then
		echo ${sscripts} > ${svcdir}/sscripts.tmp
		echo ${progress} > ${svcdir}/progress.tmp
	fi
}

# Retrieve splash state info
get_splash_info() {
	if [ -f /proc/splash ]; then
		export sscripts=`cat ${svcdir}/sscripts.tmp`
		export progress=`cat ${svcdir}/progress.tmp`
	fi
}

# vim:ts=4
