#!/bin/sh
if [ -n "$1" ]; then
	starttime=$1
else
	starttime=$(date -d 'last monday' +%s)
fi
if [ -n "$2" ]; then
	endtime=$2
else
	endtime=$(date -d 'monday' +%s)
fi
echo starttime=$starttime endtime=$endtime
bf=add-removals.$endtime
lf=$bf.log
hf=$bf.html
tf=$bf.txt
echo 'Building data' 1>&2
tail -n50000 /var/cvsroot/CVSROOT/history | python ./find-cvs-adds-and-removals.py - $starttime $endtime >$lf
#echo '<table><tr><th>Package</th><th>UTC Time</th><th>Contact</th></tr>' >$hf
#cat $logfile | grep ,removed, sample | sed 's|removed,||g' | awk -F,  '{printf "<tr><td>%s</td><td>%s</td><td>%s</td></tr>\n",$1,$3,$2}' >>$hf
#cat $logfile | grep ,added, sample | sed 's|added,||g' | awk -F,  '{printf "<tr><td>%s</td><td>%s</td><td>%s</td></tr>\n",$1,$3,$2}' >>$hf
fw=$(cut -d, -f1 $lf |grep / | awk '{print length($1)}' | sort -n  | tail -n1)
fmt="%-${fw}s\t%19s\t%s"
echo 'Building text output' 1>&2
echo 'Removals:' >$tf
cat $lf | grep ,removed, | sed 's|removed,||g' | awk -F,  "{printf \"$fmt\n\",\$1,\$3,\$2}" >>$tf
echo >>$tf
echo 'Additions:' >>$tf
cat $lf | grep ,added, | sed 's|added,||g' | awk -F, "{printf \"$fmt\n\",\$1,\$3,\$2}" >>$tf
