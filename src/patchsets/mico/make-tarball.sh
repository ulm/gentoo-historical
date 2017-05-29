#! /usr/bin/env bash

if [[ $# -lt 1 ]]; then
	echo "Usage: $0 <mico ver> <patch ver>" >&2
	exit 1
fi

micover=${1%/}
patchver=${2:-$(date '+%Y%m%d')}

if [[ ! -d ./${micover} ]]; then
	echo "Error: ${micover} is not a valid mico version" >&2
	exit 1
fi

tarfile=mico-${micover}-gentoo-patches
rm -f ${tarfile}-*
tarfile=${tarfile}-${patchver}.tar.xz

rm -rf ./tmp
mkdir -p tmp/patches || exit 1

tardirs=

# patches
cp ${micover}/*.patch tmp/patches || exit 1
tardirs="${tardirs} patches"

# helpers
helpers=
for h in \
	gtk-config \
; do
	[[ -r ./${micover}/${h} ]] || continue
	helpers="${helpers} ${h}"
	mkdir -p tmp/helpers || exit 1
	cp ./${micover}/${h} ./tmp/helpers || exit 1
	chmod +x ./tmp/helpers/${h} || die
done

if [[ -n ${helpers} ]]; then
	tardirs+=" helpers"
fi

tar cJf ${tarfile} -C tmp ${tardirs} || exit 1

rm -rf ./tmp

du -b ${tarfile}

exit 0
