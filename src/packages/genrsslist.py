#!/usr/bin/python -OO

import config
FEHOME = config.FEHOME

print """<div class="centerpage"><H3>packages.gentoo.org RSS Feeds</H3>
<p>packages.gentoo.org provides the following RSS feeds.   Note that some
feed readers may have problems with the embedded HTML feeds.</p>
</div>
<br>

<table class="ebuild">
	<tr><th class="fields">Platform</th><th class="fields">Branch</th><th class="fields">Format</th><th class="fields">URL</th></tr>
	<tr class="arch">
		<th class="arch" rowspan="2">All</th>
		<td class="arch" rowspan="2">N/A</td>
		<td class="arch">HTML</td>
		<td class="arch"><a href="%(FEHOME)sgentoo.rss">
		%(FEHOME)sgentoo.rss</a></td>
	</tr>
	<tr class="arch">
		<td class="arch">plain</td>
		<td class="arch"><a href="%(FEHOME)sgentoo_simple.rss">
		%(FEHOME)sgentoo_simple.rss</a></td>
	</tr>
""" % vars()

for arch in config.ARCHLIST:
	print """
	<!-- %(arch)s -->
		<tr class="arch">
			<th class="arch" rowspan="6">%(arch)s</th>
			<td class="arch" rowspan="2">All</td>
			<td class="arch">HTML</td>
			<td class="arch"><a href="%(FEHOME)sarchs/%(arch)s/gentoo.rss">
			%(FEHOME)sarchs/%(arch)s/gentoo.rss</a></td>
		</tr>
		<tr class="arch">
			<td class="arch">plain</td>
			<td class="arch"><a href="%(FEHOME)sarchs/%(arch)s/gentoo_simple.rss">
			%(FEHOME)sarchs/%(arch)s/gentoo_simple.rss</a></td>
		</tr>
		<tr class="arch">
			<td class="arch" rowspan="2">stable</td>
			<td class="arch">HTML</td>
			<td class="arch"><a href="%(FEHOME)sarchs/%(arch)s/stable/gentoo.rss">
			%(FEHOME)sarchs/%(arch)s/stable/gentoo.rss</a></td>
		</tr>
		<tr class="arch">
			<td class="arch">plain</td>
			<td class="arch"><a href="%(FEHOME)sarchs/%(arch)s/stable/gentoo_simple.rss">
			%(FEHOME)sarchs/%(arch)s/stable/gentoo_simple.rss</a></td>
		</tr>
			<tr class="arch">
			<td class="arch" rowspan="2">testing</td>
			<td class="arch">HTML</td>
			<td class="arch"><a href="%(FEHOME)sarchs/%(arch)s/testing/gentoo.rss">
			%(FEHOME)sarchs/%(arch)s/testing/gentoo.rss</a></td>
		</tr>
		<tr class="arch">
			<td class="arch">plain</td>
			<td class="arch"><a href="%(FEHOME)sarchs/%(arch)s/testing/gentoo_simple.rss">
			%(FEHOME)sarchs/%(arch)s/testing/gentoo_simple.rss</a></td>
		</tr>
	""" % vars()	

print "</table>"
