#!/bin/sh

PYTHONPATH="$(dirname $0):$PYTHONPATH"
export PYTHONPATH
TZ="UTC"
export TZ

DOCS=$(python -c 'import config; print config.LOCALHOME')
LIB=$(python -c 'import config; print config.FELIB')

rm -f ${DOCS}/ebuilds/*-*.html 2> /dev/null
$LIB/purge_db.py
$LIB/gentoo.py -g
$LIB/weeks.py > ${DOCS}/weeks.html
$LIB/categories2.py > ${DOCS}/categories/main.shtml
$LIB/new_ebuilds.py > ${DOCS}/new/main.shtml
$LIB/new_ebuilds.py bumps > ${DOCS}/bumps/main.shtml
$LIB/new_ebuilds.py rss > ${DOCS}/feeds/new.rss
#/bin/nice ~/freshebuilds/lib/genxml.py
