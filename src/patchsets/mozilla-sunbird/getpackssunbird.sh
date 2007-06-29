<html>
<head>
<link rel="stylesheet" type="text/css" href="/styles/nopaste.css"/>
<link rel="icon" href="/nopaste_favicon.gif" type="image/gif"/>
<link rel="shortcut icon" href="/nopaste_favicon.gif" type="image/gif"/>
<title>Nopaste - stdin</title>
</head><div style="border-bottom: 2px solid gray;">
<table border="0" cellpadding="1" cellspacing="2" width="100%">
<tr>
  <td><small>Pasted as <b>Plain Text</b> by <b>armin76</b> <span id="controls">[ <a href="/p/jPREOQ63.nln.html">Remove line numbers</a> | <a href="/p/jPREOQ63.txt">Show as plain text</a> | <a href="/paste/">Create new paste</a> ]</span></small></td>
</tr>
<tr>
  <td><small>Description: stdin</small></td>
</tr>
<tr>
  <td><small>URL: http://rafb.net/p/jPREOQ63.html</small></td>
</tr>
</table>
</div>

<table border="0" cellpadding="1" cellspacing="2">
<tr>
  <td><pre class="code">1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26</pre></td>
  <td width="100%"><pre class="code" id="codemain">#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/patchsets/mozilla-sunbird/getpackssunbird.sh,v 1.1 2007/06/29 14:01:34 armin76 Exp ${app}/make-tarball.sh,v 1.2 2006/07/30 10:44:28 redhatter Exp $
&nbsp;
PN=mozilla-sunbird
&nbsp;
if [[ $# -ne 1 ]] ; then
	echo "Usage: $0 &lt;${PN} portage version>"
	exit 1
fi
PV=$1
MY_PV=${PV/_}
P=${PN}-${PV}
S=${P}-xpi
&nbsp;
mkdir ${S}
wget -P "${S}" -m -np -nd \
	"http://releases.mozilla.org/pub/mozilla.org/calendar/sunbird/releases/${MY_PV}/langpacks/"
&nbsp;
cd ${S}
for f in *.xpi; do
	bn="$( basename "${f}" .xpi)"
	locales="${locales} ${bn}"
	mv -v "${f}" "${P}-${bn}.xpi"
done
cd "${OLDPWD}"
echo "Locales: ${locales}"</pre></td>
</tr>
</table>
</html>