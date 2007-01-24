#!/bin/bash
echo "---------------------------------------------------" >> ~/logs/times.log
export CVS_RSH=ssh
umask 022
cd ~/gentoo-x86
source ~/.keychain/*-sh

PORT="/home/gmirror/gentoo-x86"
DEP="/home/gmirror/depcache"

#echo ">>> Updating cvs..."
echo "START CVS   $(date -u)" >> ~/logs/times.log
cvs -q update -dP >> ~/logs/cvs_up.log 2>&1 || exit 1
echo "END   CVS   $(date -u)" >> ~/logs/times.log
[ ! -d ~/gentoo-x86/metadata/cache ] && install -d ~/gentoo-x86/metadata/cache

#
# no.  this thing doesn't even fricking work.
#~/scripts/cleancache.sh
#

echo "START REGEN $(date -u)" >> ~/logs/times.log
#~/scripts/metadata-regen || exit 5
~/scripts/extern_regen.sh ${DEP} ${PORT} &> ~/logs/regen-run.log || exit 5
rsync -Irua --checksum --delete ${DEP}/${PORT}/ ${PORT}/metadata/cache/ || exit 5
echo "END   REGEN $(date -u)" >> ~/logs/times.log
date -u > ~/gentoo-x86/metadata/timestamp

echo "START DTD   $(date -u)" >> ~/logs/times.log
cd ~/gentoo-x86/metadata/dtd && cvs up -dP >> ~/logs/glsa-cvs.dtd 2>&1
date -R -u > ~/gentoo-x86/metadata/dtd/timestamp.chk
echo "END   DTD   $(date -u)" >> ~/logs/times.log
echo "START GLSA  $(date -u)" >> ~/logs/times.log
cd ~/gentoo-x86/metadata/glsa && cvs up -dP >> ~/logs/glsa-cvs.log 2>&1
date -R -u > ~/gentoo-x86/metadata/glsa/timestamp.chk
echo "END   GLSA  $(date -u)" >> ~/logs/times.log

# Check for block_sync
block="profiles/block_sync"
if [[ -e $block ]] ; then
        ENTRY=$(grep "^Entry-Date:*" $block | cut -f2- -d' ')
        START=$(grep "^Start-Date:*" $block | cut -f2- -d' ')
        END=$(grep "^Completion-Date:*" $block | cut -f2- -d' ')
        NOW=$(date -R)
        NOW_STAMP=$( date +%s -d "$NOW")
        START_STAMP=$(date +%s -d "$START")
        END_STAMP=$(date +%s -d "$END")
        if [[ $NOW_STAMP -gt $END_STAMP ]] ; then
                REPORTER=$(grep "^Signed-Off-By:*" $block | cut -f2- -d ' ' | sed -e 's| <at> |@|g' | \
                        cut -f 2- -d '<' | cut -f 1 -d '>')
                mail -c "$REPORTER" -s "Gentoo-x86 Blocking Alert" warnera6@egr.msu.edu <<-EOF
                        $REPORTER added a block_sync file at:
                        $ENTRY
                        Their work was to be concluded at:
                        $END
                        However, the current time is now:
                        $NOW
EOF
        fi
        if [[ $NOW_STAMP -gt $START_STAMP ]] ; then
                echo "RSYNC ABORTED (BLOCK_SYNC) $(date -u)" >> ~/logs/times.log
                exit
        fi
fi

#echo ">>> Syncing to rsync directory..."
echo "START RSYNC $(date -u)" >> ~/logs/times.log
rsync -Cqa --delete ~/gentoo-x86/ ~/rsync/ > /dev/null 2>&1 || echo "rsync failed to complete from cvs to rsynctree" >&2
echo "END   RSYNC $(date -u)" >> ~/logs/times.log
rm -f ~/rsync/metadata/cache/*-eclass.*
echo "START PERMS $(date -u)" >> ~/logs/times.log
chmod -R u-s,g-s ~/rsync/metadata
echo "END   PERMS $(date -u)" >> ~/logs/times.log

echo "---------------------------------------------------" >> ~/logs/times.log
