#!/bin/bash

ADDS=$(grep added ${1} | cut -d" " -f1)
REMOVES=$(grep removed ${1} | cut -d" " -f1)

echo "<section>
<title>Additions:</title>
<body>

<table>

<tr>
<th>Package:</th>
<th>Addition date:</th>
<th>Contact:</th>
</tr>
"

get_info() {
	CAT=$(echo ${line} | cut -d / -f1)
	PN=$(echo ${line} | cut -d / -f2 | cut -d, -f1)
	CONTACT=$(echo ${line} | cut -d, -f3)
	DATE=$(echo ${line} | cut -d, -f4)
	YEAR=$(echo ${DATE} | cut -d- -f1)
	MONTH=$(echo ${DATE} | cut -d- -f2)
	DAY=$(echo ${DATE} | cut -d- -f3)
	case ${MONTH} in
		01) MONTH="Jan" ;;
		02) MONTH="Feb" ;;
		03) MONTH="Mar" ;;
		04) MONTH="Apr" ;;
		05) MONTH="May" ;;
		06) MONTH="Jun" ;;
		07) MONTH="Jul" ;;
		08) MONTH="Aug" ;;
		09) MONTH="Sep" ;;
		10) MONTH="Oct" ;;
		11) MONTH="Nov" ;;
		12) MONTH="Dec" ;;
	esac
	YEAR=$(echo ${YEAR} | cut -b3-) 
}

for line in ${ADDS}
do
	get_info
	echo "<tr>"
	echo "<ti><uri link=\"http://packages.gentoo.org/package/?category=${CAT};name=${PN}\">${CAT}/${PN}</uri></ti>"
	echo "<ti>${DAY} ${MONTH} ${YEAR}</ti>"
	echo "<ti><mail link=\"${CONTACT}@gentoo.org\">Real Name</mail></ti>"
	echo "</tr>"
	echo
done

echo "</table>

</body>
</section>

<section>
<title>Removals:</title>
<body>

<table>

<tr>
<th>Package:</th>
<th>Removal date:</th>
<th>Contact:</th>
</tr>
"

for line in ${REMOVES}
do
	get_info
	echo "<tr>"
	echo "<ti>${CAT}/${PN}</ti>"
	echo "<ti>${DAY} ${MONTH} ${YEAR}</ti>"
	echo "<ti><mail link=\"${CONTACT}@gentoo.org\">Real Name</mail></ti>"
	echo "</tr>"
	echo
done

echo "</table>

</body>
</section>
"
