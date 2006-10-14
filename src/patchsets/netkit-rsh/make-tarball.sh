#!/bin/sh

if [ $# -ne 1 ]; then
	echo "Usage: $0 <patch ver>"
	exit 1
fi
pver=$1

tar=netcat-0.17-patches-${pver}.tar.bz2

tar -jcf ${tar} . || exit 1

du -b ${tar}
