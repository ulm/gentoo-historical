# $Header: /var/cvsroot/gentoo/users/pvdabeel/livecd/files/loop/etc/init.d/halt.sh,v 1.1.1.1 2004/02/13 00:53:19 pvdabeel Exp $

#we try to deactivate swap first because it seems to need devfsd running
#to work.  The TERM and KILL stuff will zap devfsd, so...

ebegin "Deactivating swap"
swapoff -a &>/dev/null
eend $?

#we need to properly terminate devfsd to save the permissions
if [ "$(ps -A |grep devfsd)" ]
then
	ebegin "Stopping devfsd"
	killall -15 devfsd &>/dev/null
	eend $?
fi

ebegin "Sending all processes the TERM signal"
killall5 -15 &>/dev/null
eend $?
sleep 5
ebegin "Sending all processes the KILL signal"
killall5 -9 &>/dev/null
eend $?

#unmounting should use /proc/mounts and work with/without devfsd running

#try to unmount all filesystems (no /proc,tmpfs,devfs,etc)
#this is needed to make sure we dont have a mounted filesystem on a LVM volume
#when shutting LVM down ...
ebegin "Unmounting filesystems"
#awk should still be availible (allthough we should consider moving it to /bin if problems arise)
for x in $(awk '!/(^#|proc|devfs|tmpfs|^none|^\/dev\/root| \/ )/ {print $2}' /proc/mounts |sort -r)
do
	umount -f -r ${x} &>/dev/null
done
eend 0

ups_kill_power() {
	if [ -x /sbin/upsdrvctl ]
	then
		ewarn "Signalling ups driver(s) to kill the load!"
		/sbin/upsdrvctl shutdown
	fi
}

ebegin "Remounting remaining filesystems readonly"
#get better results with a sync and sleep
sync;sync
sleep 2
umount -a -r -n -t nodevfs,noproc,notmpfs &>/dev/null
if [ "$?" -ne 0 ]
then
	killall5 -9  &>/dev/null
	umount -a -r -n -l -d -f -t nodevfs,noproc &>/dev/null
	if [ "$?" -ne 0 ]
	then
		eend 1
		sync; sync
		[ -f /etc/killpower ] && ups_kill_power
		/sbin/sulogin -t 10 /dev/console
	else
		eend 0
	fi
else
	eend 0
fi

[ -f /etc/killpower ] && ups_kill_power


# vim:ts=4
