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


