#!/bin/bash

V=0.1

tar \
	-jcf /tmp/lcdsplash-${V}.tar.bz2 \
	-C .. \
	--exclude tarball.sh \
	--exclude CVS \
	lcdsplash

ls -l /tmp/lcdsplash-${V}.tar.bz2
