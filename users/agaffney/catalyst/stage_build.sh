#!/bin/bash

PROFILE="default-linux/x86/2006.1"
VERSION_STAMP="2007.0_pre"
SUBARCH="i686"
EMAIL_FROM="root@kagome"
EMAIL_TO="andrew@agaffney.org"
STAGE1_SEED="default/stage3-i686-2006.1"

DATE=`date +%Y%m%d`
PID=$$

cd /tmp

catalyst -s "${DATE}" &> /tmp/catalyst_build_snapshot.${PID}.log
if [ $? != 0 ]; then
  echo -e "From: ${EMAIL_FROM}\r\nTo: ${EMAIL_TO}\r\nSubject: Catalyst build error - snapshot\r\n\r\n$(</tmp/catalyst_build_snapshot.${PID}.log)" | sendmail ${EMAIL_TO}
  exit 1
fi

for i in 1 2 3; do
  echo -e "subarch: ${SUBARCH}\ntarget: stage${i}\nversion_stamp: ${VERSION_STAMP}\nrel_type: default\nprofile: ${PROFILE}\nsnapshot: ${DATE}" > stage${i}.spec
  if [ ${i} = 1 ]; then
    echo "source_subpath: ${STAGE1_SEED}" >> stage${i}.spec
  else 
    echo "source_subpath: default/stage$(expr ${i} - 1)-${SUBARCH}-${VERSION_STAMP}" >> stage${i}.spec
  fi
done

for i in 1 2 3; do
  catalyst -f stage${i}.spec &> /tmp/catalyst_build_stage${i}.${PID}.log
  if [ $? != 0 ]; then
    echo -e "From: ${EMAIL_FROM}\r\nTo: ${EMAIL_TO}\r\nSubject: Catalyst build error - stage${i}\r\n\r\n$(</tmp/catalyst_build_stage${i}.${PID}.log)" | sendmail ${EMAIL_TO}
    exit 1
  fi
done

echo -e "From: ${EMAIL_FROM}\r\nTo: ${EMAIL_TO}\r\nSubject: Catalyst build success\r\n\r\nEverything finished successfully." | sendmail ${EMAIL_TO}
