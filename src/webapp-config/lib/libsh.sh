# libsh.sh
#		Library of useful shell functions
#
# Author	Stuart Herbert
#		(stuart@gnqs.org)
#
# Copyright	(c) 2003 Stuart Herbert
#		Released under v2 of the GNU GPL

LIBSH_EQUIET=

# general setup stuff
#
# $1 - '1' for colour, anything else for b/w

libsh_init ()
{
	unset E
	if [ -z "`echo -e`" ]; then
		E="-e"
	fi

	YELLOW="\033[33;01m"
	GREEN="\033[32;01m"
	RED="\033[31;01m"
	OFF="\033[0m"
	CYAN="\033[36;01m"
	BLUE="\033[34;01m"

	ERROR_OCCURRED=
}

libsh_equiet ()
{
	[ "${LIBSH_EQUIET}" = "1" ]
}

libsh_eecho ()
{
	libsh_equiet || echo $E "$*"
}

libsh_einfo ()
{
	libsh_equiet || echo $E "${GREEN}*${OFF} $*"
}

libsh_ewarn ()
{
	libsh_equiet || echo $E "${YELLOW}*${OFF} $*"
}

libsh_eerror ()
{
	# errors can't be suppressed

	ERROR_OCCURRED=1
	echo $E "${RED}*${OFF} $*" >&2
}

libsh_enotice ()
{
	libsh_equiet || echo $E "$*${OFF}"
}

libsh_edie ()
{
	libsh_eerror "$@"
	exit 1
}

libsh_dieiferror ()
{
	if [ "${ERROR_OCCURRED}+" != "+" ]; then
		libsh_edie "Fatal error(s) - exiting"
	fi
}

libsh_erun ()
{
	"$@"
	if [ $? != 0 ]; then
		libsh_edie "Fatal error - exiting"
	fi
}

libsh_file_source ()
{
	readlink "$1"
}

libsh_file_sum ()
{
	md5sum "$1" | awk '{ print $1 }'
}

# ------------------------------------------------------------------------
# libsh_file_timestamp ()
#
# output a UNIX timestamp for a given file
#
# Inputs
#	$1	- the file we want a timestamp for
#
# Outputs
#	prints the timestamp onto stdout
#
# NOTE:
# 	Do not use this function on symlinks; it *will* return the wrong
#	value

libsh_file_timestamp ()
{
	date -r "$1" "+%s"
}

libsh_init
