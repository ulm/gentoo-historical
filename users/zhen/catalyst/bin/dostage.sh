#!/bin/bash

SDOARCH="(was not set, using hardcoded default)"
DOARCH="x86"
if [ ! -z "${1}" ]; then
	DOARCH="${1}"
	SDOARCH="(set via cmdline)"
fi


SSOURCE="(set via environment)"
if [ -z "$SOURCE" ]; then
	SOURCE="1.4_pre20030214"
	SSOURCE="(was not set, using hardcoded default)"
fi

if [ ! -f "stages/stage1-$DOARCH-$SOURCE.tar.bz2" ]; then
	echo
	echo "!!! SOURCE was not set and default does not exist."
	echo "!!! Exiting. Please check SOURCE and the arch specified."
	echo
	echo "!!! The arch is '$DOARCH' $SDOARCH"
	echo "!!! SOURCE='$SOURCE'"
	echo "!!! Not found: stages/stage1-$DOARCH-$SOURCE.tar.bz2"
	echo
	exit 1
fi


SDEST="(set via environment)"
if [ -z "$DEST" ];then
	if [ -f /usr/portage/metadata/timestamp ]; then
		SDEST="(set via metadata timestamp)"
		DEST="1.4_pre$(date -d "$(</usr/portage/metadata/timestamp)" '+%Y%m%d')"
		#" This is for mc... It apparently has a bad regex. Bah.
	else
		SDEST="(CVS: set via current date -- rsync uses metadata)"
		DEST="1.4_pre$(date '+%Y%m%d')"
	fi
fi

if [ -f "stages/stage1-$DOARCH-$DEST.tar.bz2" ]; then
	echo
	echo -e "\a!!! WARNING: destination exists."
	echo -e "\a!!! Will overwrite: stages/stage1-$DOARCH-$DEST.tar.bz2"
	echo
	echo ">>> You have 5 seconds to cancel... (Control-C)"
	sleep 1; echo -ne "\a"
	sleep 1; echo -ne "\a"
	sleep 3
	SDEST="$SDEST (overwriting)"
fi

echo
echo
echo "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"
echo "  Using the following information:"
echo "    SOURCE=${SOURCE} ${SSOURCE}"
echo "      DEST=${DEST} ${SDEST}"
echo "      ARCH=${DOARCH} ${SDOARCH}"
echo
echo "    Note: './stager umount' will unmount bind-mounted partitions that"
echo "          were created during the stager. Remember that. :)"
echo "    Note: packages and build directories will be deleted."
echo "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"
echo
echo ">>> You have 10 seconds to cancel... (Control-C)"
sleep 10

rm -Rf packages build
for x in 1 2 3
do
	echo "$(date '+%H:%M:%S') Performing: ./stager $DOARCH $x $SOURCE $DEST" 1>&2
	if ! ./stager $DOARCH $x $SOURCE $DEST &> log.${DOARCH}.${x}; then
		echo
		echo
		echo -e "\a!!! FAILED TO BUILD STAGE $x"
		echo -e "\a!!! FAILED TO BUILD STAGE $x" 1>&2
		echo
		exit 1
	fi
done
