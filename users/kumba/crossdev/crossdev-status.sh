#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2

#// Script Variables
#//------------------------------------------------------------------------------------------------

#// Default configuration location && Default settings
DEFAULT_CONF_LOC="/etc/crossdev/crossdev.conf"

#// Extra Colors
USE_COLOR="yes"


#// Read configuration (If this file exists, the above vars are overwritten)
if [ -f "${DEFAULT_CONF_LOC}" ]; then
	source ${DEFAULT_CONF_LOC}
fi


#// My Version
MYVERSION="0.3"

#// Do we want colors?
if [ "${USE_COLOR}" = "yes" ]; then
	BLUE="\033[1;34m"
	CYAN="\033[1;36m"
	DARKGREEN="\033[0;32m"
	GREEN="\033[1;32m"
	PURPLE="\033[1;35m"
	RED="\033[1;31m"
	WHITE="\033[1;37m"
	YELLOW="\033[1;33m"
	XX="\033[0;0m"
else
	BLUE=""
	CYAN=""
	DARKGREEN=""
	GREEN=""
	PURPLE=""
	RED=""
	WHITE=""
	YELLOW=""
	XX=""
fi

#//------------------------------------------------------------------------------------------------




#// Display Functions
#//------------------------------------------------------------------------------------------------


#// Error
berror() {
	echo -e " ${RED}*${XX} ${*}"
	return 0
}

#//------------------------------------------------------------------------------------------------





#// Get Status
#//------------------------------------------------------------------------------------------------

getStatus() {

	#// Valid call
	if [ -z "${*}" ]; then
		echo "Error in getStatus()!"
	fi

	#// Determine the current status
	case "${1}" in
		0)	TMPSTATBIT="${BLUE}[${PURPLE} ? ${BLUE}]${XX}";;
		K)	TMPSTATBIT="${BLUE}[${YELLOW} K ${BLUE}]${XX}";;
		F)	TMPSTATBIT="${BLUE}[${GREEN} F ${BLUE}]${XX}";;
		-)	TMPSTATBIT="${BLUE}[${CYAN} - ${BLUE}]${XX}";;
		X)	TMPSTATBIT="${BLUE}[${RED} * ${BLUE}]${XX}";;
		*)	TMPSTATBIT="${BLUE}[${WHITE} ! ${BLUE}]${XX}";;
	esac

	return 0
}

#//------------------------------------------------------------------------------------------------





#// Status Output
#//------------------------------------------------------------------------------------------------

displayStatus() {

	#// Possible values for each array index:
	#// 0 = untested at all for a toolchain combination
	#// K = kernel-only toolchain
	#// F = full toolchain
	#// - = invalid (i.e., the host & target arch are the same)
	#// X = failure (faild to build even a kernel toolchain (likely died in gcc-bootstrap))

	#//					    0 1 2 3 4 5 6 7 8 9 0
	#//			  1 2 3 4 5 6 7 8 9 1 1 1 1 1 1 1 1 1 1 2
	#//---------------------------------------------------------------
	declare -a	   alpha=(- 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0) # 1
	declare -a	   amd64=(0 - 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0) # 2
	declare -a	     arm=(0 0 - 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0) # 3
	declare -a	    cris=(0 0 0 - 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0) # 4
	declare -a	    hppa=(0 0 0 0 - 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0) # 5
	declare -a	    i486=(0 0 0 0 0 - 0 0 0 0 0 0 0 0 0 0 0 0 0 0) # 6
	declare -a	    i586=(0 0 0 0 0 0 - 0 0 0 0 0 0 0 0 0 0 0 0 0) # 7
	declare -a	    i686=(K F 0 K 0 K F - X K F K F K F K F K K 0) # 8
	declare -a	    ia64=(0 0 0 0 0 0 0 0 - 0 0 0 0 0 0 0 0 0 0 0) # 9
	declare -a	    m68k=(0 0 0 0 0 0 0 0 0 - 0 0 0 0 0 0 0 0 0 0) # 10
	declare -a	    mips=(0 0 0 0 0 0 0 0 0 0 - K 0 0 0 0 0 0 0 0) # 11
	declare -a	  mips64=(0 0 0 0 0 0 0 0 0 0 0 - 0 0 0 0 0 0 0 0) # 12
	declare -a	  mipsel=(0 0 0 0 0 0 0 0 0 0 0 0 - 0 0 0 0 0 0 0) # 13
	declare -a	mips64el=(0 0 0 0 0 0 0 0 0 0 0 0 0 - 0 0 0 0 0 0) # 14
	declare -a	     ppc=(0 0 0 0 0 0 0 0 0 0 0 0 0 0 - 0 0 0 0 0) # 15
	declare -a	   ppc64=(0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 - 0 0 0 0) # 16
	declare -a	ppc_eabi=(0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 - 0 0 0) # 17
	declare -a	      sh=(0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 - 0 0) # 18
	declare -a	   sparc=(0 F 0 0 0 0 0 X 0 0 F 0 F 0 X 0 0 0 - K) # 19
	declare -a	 sparc64=(0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 F -) # 20
	#//---------------------------------------------------------------


	declare -a archlist=(alpha amd64 arm cris hppa i486 i586 \
			     i686 ia64 m68k mips mips64 mipsel \
			     mips64el ppc ppc64 ppc_eabi sh \
			     sparc sparc64)

	#// Misc variables controlling output
	local hi ti1 ti2 # host index, target index (loop 1 & 2)
	local HOST_ARCH TARG_ARCH
	local arch_arr_val # read arch arrays dynamically
	local tab_char

	#// Number of archs per line
	#// Leave this alone, as it really messes the output up
	#// It's here because I don't like hardcoding values
	local archs_per_line=5

	#// Maximum num of chars a target arch name can have
	#// If less than a certain value, we append a tab character to
	#// make the output look nice
	local t_max_char=8

	#// Minimum num of chars a host arch name needs.
	#// If less then or equal to this value, we append a tab
	#// character to make the output look nice
	local h_min_char=2

	#// Display Status
	echo -e ""
	echo -e "${GREEN}crossdev.sh ${BLUE}v${MYVERSION}${WHITE} - ${CYAN}Cross-Toolchain Generator${WHITE} - ${YELLOW}Status Page${XX}"
	echo -e ""
	echo -e "${WHITE}Status of Targets:${XX}"


	#// Loop through each main arch (This is some really sick code)
	for hosti in $(seq 0 $((${#archlist[*]} - 1))); do
		#// Determine each main arch's name
		HOST_ARCH=${archlist[${hosti}]}

		#// #// If strlen <= ${h_min_char} characters, append a tab character
		if [ ${#HOST_ARCH} -le ${h_min_char} ]; then
			tab_char="\t"
		else
			tab_char=""
		fi

		#// Print the main arch
		echo -e "    ${GREEN}${HOST_ARCH/_/-}:${XX}${tab_char}\t-------------------------------------------------------------------------------"

		#// For each host arch, list what target toolchains can be built
		for ti1 in $(seq 0 ${archs_per_line} $((${#archlist[*]} - 1))); do
			TARG_ARCH=${archlist[${ti1}]}
			arch_arr_val="${HOST_ARCH}[${ti1}]"
			arch_arr_val="${!arch_arr_val}"

			#// If strlen < ${t_max_char} characters, append a tab character
			if [ ${#TARG_ARCH} -lt ${t_max_char} ]; then
				tab_char="\t"
			else
				tab_char=""
			fi

			#// Display first target-arch name
			getStatus "${arch_arr_val}"
			echo -ne "\t\t| ${WHITE}${TARG_ARCH/_/-}${XX}${tab_char}${TMPSTATBIT} |"

			#// Display remaining target-arch names
			for ti2 in $(seq $((ti1 + 1)) $((ti1 + archs_per_line - 1))); do
				TARG_ARCH=${archlist[${ti2}]}
				arch_arr_val="${HOST_ARCH}[${ti2}]"
				arch_arr_val="${!arch_arr_val}"

				#// If strlen < ${t_max_char} characters, append a tab character
				if [ ${#TARG_ARCH} -lt ${t_max_char} ]; then
					tab_char="\t"
				else
					tab_char=""
				fi

				if [ ! -z "${TARG_ARCH}" ]; then
					getStatus "${arch_arr_val}"
					echo -ne " ${WHITE}${TARG_ARCH/_/-}${XX}${tab_char}${TMPSTATBIT} |"
				else
					echo -ne "\t\t      |"
				fi
			done
			echo -e ""
		done
	done


	#// Print the legend
	echo -e "    \t\t-------------------------------------------------------------------------------"
	echo -e ""
	echo -e "${WHITE}Legend:${XX}"
	echo -en "\t${BLUE}[${PURPLE} ? ${BLUE}]${WHITE} - Toolchain untested on this arch."
	echo -e "\t${BLUE}[${YELLOW} K ${BLUE}]${WHITE} - Will build a kernel-only toolchain.${XX}"
	echo -en "\t${BLUE}[${GREEN} F ${BLUE}]${WHITE} - Will build a full toolchain. (C & C++)"
	echo -e "\t${BLUE}[${CYAN} - ${BLUE}]${WHITE} - Invalid/Same host & target arch.${XX}"
	echo -e "\t${BLUE}[${RED} * ${BLUE}]${WHITE} - Failed to build a toolchain${XX}"
	echo -e ""
	echo -e "${WHITE}If you get a new combination to work please inform us at ${CYAN}http://bugs.gentoo.org/${XX}"
	echo -e ""

	return 0
}

#//------------------------------------------------------------------------------------------------




#// Main
#//------------------------------------------------------------------------------------------------

#// Display the Status
displayStatus

#//------------------------------------------------------------------------------------------------
