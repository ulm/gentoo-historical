#!/bin/bash

tar -jc \
	--exclude '*/CVS*' \
	-f wine-fake_windows.tar.bz2 fake_windows \
	|| exit 1
ls -l wine-fake_windows.tar.bz2

tar -jc \
	--exclude '*/CVS*' \
	-f wine-misc.tar.bz2 -C misc . \
	|| exit 1
ls -l wine-misc.tar.bz2
