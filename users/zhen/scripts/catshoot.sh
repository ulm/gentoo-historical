#!/bin/bash

# <zhen@gentoo.org> a tool to upload my snapshots of catalyst and our default profile

BASEDIR="/home/gentoo-cvs/gentoo/users/zhen"
NICEDATE="`date +%Y%m%d`"
PROFILE="hardened-x86-1.4"

cd ${BASEDIR}/profiles
tar cjf /tmp/${PROFILE}-${NICEDATE}.tar.bz2 ${PROFILE}

cd ${BASEDIR}
tar cjf /tmp/catalyst-${NICEDATE}.tar.bz2 catalyst

scp /tmp/${PROFILE}-${NICEDATE}.tar.bz2 /tmp/catalyst-${NICEDATE}.tar.bz2 zhen@dev.gentoo.org:public_html/Hardened/snaps

rm /tmp/${PROFILE}-${NICEDATE}.tar.bz2 /tmp/catalyst-${NICEDATE}.tar.bz2
