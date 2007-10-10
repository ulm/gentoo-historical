#!/bin/sh

# some tools to handle topdocs file

_DATE="$(date +%Y%m%d)"
_LANG=fr

function get() {
 output=topdocs-${_DATE}.xml
 if [ -r "$output" ]; then return; fi
 wget -O "$output" http://www.gentoo.org/proj/en/gdp/tests/topdocs.xml?passthru=1
}
function order() {
 get
 output=order-${_DATE}.txt
 if [ -r "$output" ]; then return; fi
 cat topdocs-${_DATE}.xml | grep "^<tr><ti>" | sed -e "s/<[^>]*>/ /g" -e "s/,//g" | awk '{ print $4" "$2 }' | sort -nr > "$output"
}
function metadoc() {
 for doc in $(
    egrep " /(doc|proj)/" order-${_DATE}.txt \
    | grep -v handbook \
    | sed "s/\*\*/en/" \
    | awk '{ print $2 }'); do
  if grep -q $doc ../../../xml/htdocs/doc/${_LANG}/metadoc.xml; then
   echo $doc
  fi
 done
}
function help() {
 echo "Usage: $0 <get|order|metadoc>"
 echo "get: download the plain current topdocs.xml"
 echo "order: top docs ordered by English hits (ie. excluding translations)"
 echo "metadoc: show top docs that are untranslated according to metadoc"
 exit
}

if [ $# -ne 1 ]; then help; fi
case "$1" in
 "metadoc")
  metadoc
  ;;
 "get")
  get
  ;;
 "order")
  order
  ;;
 *)
  help
  ;;
esac

