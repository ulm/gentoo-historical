#!/bin/bash

KV=`uname -r`
KMAJOR=`echo ${KV} | cut -d. -f1`
KMINOR=`echo ${KV} | cut -d. -f2`
INSMOD="insmod.static"

if [ "${KMINOR}" -gt "4" ]
then
	KEXT=".ko"
else
	KEXT=".o"
fi

usage()
{
	echo "modprobe gentoo script v1.0"
	echo "Usage:"
	echo "  modprobe moduleprefix"
	echo ""
	echo "Ex:"
	echo "  modprobe eepro100"
	echo ""
	echo "Note: Do not pass the suffix to modprobe"
	exit 1
}

# Pass module name to this function
modules_dep_list()
{
	if [ "$#" != "1" ]
	then
		echo "modules_dep_list(): improper usage"
		exit 1
	fi
	cat /lib/modules/${KV}/modules.dep | grep ${1}${KEXT}\: | cut -d\:  -f2
}


# Pass module deps list
strip_mod_paths()
{
	local x
	local ret
	local myret

	[ "$#" -lt "1" ] && return

	for x in ${*}
	do
		ret=`basename ${x} | cut -d. -f1`
		myret="${myret} ${ret}"
	done
	echo "${myret}"
}

LOADED_MODULES=""

is_module_already_loaded()
{
	local x
	if [ "$#" != "1" ]
	then
		echo "is_module_already_loaded(): improper usage"
	fi

	for x in ${LOADED_MODULES}
	do
		if [ "${x}" == "${1}" ]
		then
			# Yep, module is loaded
			return 0
		fi
	done
	return 1
}

real_mod_path()
{
	find /lib/modules/${KV}/ -path "*${1}${KEXT}"
}

modprobe2()
{
	local x
	if [ "$#" != "1" ]
	then
		echo "modprobe(): improper usage"
	fi

	modlist=`modules_dep_list ${1}`
	if [ "${modlist}" != "" -a "${modlist}" != " " ]
	then
		deps=`strip_mod_paths ${modlist}`
	else
		deps=""
	fi

	echo "$1 -- DEPS=${deps}"
	# Make sure we don't do any endless loops!

	LOADED_MODULES="${LOADED_MODULES} ${1}"

	for x in ${deps}
	do
		if ! is_module_already_loaded ${x}
		then
			modprobe2 "${x}"
		else
			echo "skipping ${x}, module already loaded by us"
		fi
	done

	real_path=`real_mod_path ${1}`
	echo "running insmod on ${real_path}"
	${INSMOD} ${real_path}	
}


if [ "$#" != "1" ]
then
	usage
fi

modprobe2 ${1}
