#!/bin/sh

# some tools to handle topdocs file

DATE="$(date +%Y%m%d)"

function get() {
 output=topdocs-${DATE}.xml
 if [ -r "$output" ]; then return; fi
 wget -O "$output" http://www.gentoo.org/proj/en/gdp/tests/topdocs.xml?passthru=1
}
function order() {
 get
 output=order-${DATE}.txt
 if [ -r "$output" ]; then return; fi
 cat topdocs-${DATE}.xml | grep "^<tr><ti>" | sed -e "s/<[^>]*>/ /g" -e "s/,//g" | awk '{ print $4" "$2 }' | sort -nr > "$output"
}
function help() {
 echo "Usage: $0 <get|order>"
 echo "ie.: $0 order to get the last list of top docs viewed on gentoo.org,"
 echo "ordered by English hits (ie. excluding translations)"
 exit
}

if [ $# -ne 1 ]; then help; fi
case "$1" in
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

