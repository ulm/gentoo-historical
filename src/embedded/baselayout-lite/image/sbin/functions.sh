PATH="/usr/bin:/bin:/usr/sbin:/sbin"
NO_NET_FS_LIST="noafs,nocifs,nocode,noncpfs,nonfs,nonfs4,noshfs,nosmbfs"

#ls -lah /var/lib/init.d/started
#cat /proc/mounts

einfo() {
	echo "EINFO: $*"
}
eerror() {
	echo "EERROR $*"
}
ebegin() {
	echo "EBEGIN: $*"
}
ewarn() {
	echo "EWARN: $*"
}
eend() {
	local retval=$1
	#shift
	if [ "$retval" -eq "0" ] ; then
		return $retval
	fi
	echo "EEND: $*"
	return $retval
}

depend() {
	return 0
}
                    
get_bootparam() {
    local x copt params retval=1

    [ ! -r "/proc/cmdline" ] && return 1

	if `grep $1 /proc/cmdline` ; then
		einfo "Found cmdline option: $1"
		retval=0
	fi

    return ${retval}
}

is_net_fs() {
	grep -q '^[^#]*\/[[:space:]].*nfs' /etc/fstab
	return $?
}

is_uml_sys() {
	[ ! -r "/proc/cpuinfo" ] && return 1
	grep -q 'UML' /proc/cpuinfo &> /dev/null
	return $?
}

