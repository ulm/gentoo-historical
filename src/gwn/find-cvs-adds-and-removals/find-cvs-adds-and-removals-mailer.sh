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
bf=add-removals.$endtime
lf=$bf.log
hf=$bf.html
tf=$bf.txt

# subtract 5 to ensure we are on the previous day.
enddate=$(date -u -d "@$(($endtime-5))" +"%Y-%m-%d")
dateheader=$(date -u +"%a, %d %b %Y %H:%M:%S %z")
boundary="0F1p//8PRICkK4MWrobbat2$RANDOM$RANDOM$RANDOM"

if [ ! -f "$lf" ]; then 
	echo "No $lf found!" 1>&2
	exit 1
fi
if [ ! -f "$tf" ]; then 
	echo "No $tf found!" 1>&2
	exit 1
fi

TO=gentoo-dev@lists.gentoo.org

/usr/sbin/sendmail -ti <<EOF
From: "Robin H. Johnson" <robbat2@gentoo.org>
To: $TO
Subject: Automated Package Removal and Addition Tracker, for the week ending $enddate 23h59 UTC
Organization: Gentoo Linux Distribution
Date: ${dateheader}
X-Mailer: Automated Script on cvs.gentoo.org ;-)
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="$boundary"
Content-Disposition: inline



--$boundary
Content-Type: text/plain; charset=us-ascii
Content-Disposition: inline

The attached list notes all of the packages that were added or removed
from the tree, for the week ending $enddate 23h59 UTC.

$(<$tf)

--
Robin Hugh Johnson
Gentoo Linux Developer
E-Mail     : robbat2@gentoo.org
GnuPG FP   : 11AC BA4F 4778 E3F6 E4ED  F38E B27B 944E 3488 4E85

--$boundary
Content-Type: text/plain; charset=us-ascii
Content-Disposition: attachment; filename="$lf"

$(<$lf)
--$boundary--

EOF
