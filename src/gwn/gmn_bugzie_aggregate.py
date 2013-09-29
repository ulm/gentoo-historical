#!/usr/bin/env python

from pygooglechart import *
data = open('breport')

butota = []
bukeys = []
budata = []
clkeys = []
clkraw = []
cldata = []
opkeys = []
opkraw = []
opdata = []

j = 0
for i in data:
	values = i.strip('\n').split(':')
	# j == 0 -> New, Closed, Not Fixed, Duplicates, Total
	if j == 0:
		# Dates
		dfrom = values[0]
		dnext = values[1]
	elif j > 0 and j <= 4:
		# Populate list of New, Closed, Not Fixed and Duplicates Bugs
		budata.append(int(values[1]))
		bukeys.append(values[0] + ' (' + str(budata[-1]) + ')')
	elif j > 4 and j <= 8:
		# Total bugs
		butota.append(int(values[1]))
	elif j > 8 and j <= 17:
		# Bugs per team
		cldata.append(int(values[1]))
		clkraw.append(values[0]);
		clkeys.append(values[0] + ' (' + str(cldata[-1]) + ')')
	elif j == 18:
		# Bugs for others
		clothers = int(values[1])
	elif j <= 27:
		# Bugs for others
		opdata.append(int(values[1]))
		opkraw.append(values[0])
		opkeys.append(values[0] + ' (' + str(opdata[-1]) + ')')
	else:
		opothers = int(values[1])
	j += 1
data.close()

activity = PieChart2D(500, 300)
activity.set_colours(['45347B'])
activity.add_data(budata)
activity.set_pie_labels(bukeys)
activity.download('activity.png')

clmax = max(cldata)
clnor = map(lambda x: (x / float(clmax)) * 100, cldata)
closed = StackedHorizontalBarChart(500, 250)
closed.set_colours(['45347B'])
closed.set_bar_width(20)
closed.add_data(clnor)
clkeys.reverse()
closed.set_axis_labels(Axis.LEFT, clkeys)
closed.set_axis_labels(Axis.BOTTOM, map(str, range(0, int(round(max(cldata))) + 10, 10)))
closed.download('closed.png')

opmax = max(opdata)
opnor = map(lambda x: (x / float(opmax)) * 100, opdata)
opened = StackedHorizontalBarChart(500, 250)
opened.set_colours(['45347B'])
opened.set_bar_width(20)
opened.add_data(opnor)
opkeys.reverse()
opened.set_axis_labels(Axis.LEFT, opkeys)
opened.set_axis_labels(Axis.BOTTOM, map(str, range(0, int(round(max(opdata))) + 10, 10)))
opened.download('opened.png')

clkeys.reverse()
opkeys.reverse()
print """<chapter>
<title>Bugzilla</title>

<section>
<title>Statistics</title>
<body>

<p>
The Gentoo community uses Bugzilla
(<uri link="http://bugs.gentoo.org">bugs.gentoo.org</uri>) to record
and track bugs, notifications, suggestions and other interactions
with the development team. The following chart summarizes activity on
Bugzilla between %s and %s.
</p>

<figure link="activity.png" short="Bug activity" caption="Bug activity split-up"/>

<p>
Of the <b>%d</b> currently open bugs: <b>%d</b> are labeled <e>blocker</e>,
<b>%d</b> are labeled <e>critical</e>, and <b>%d</b> are labeled <e>major</e>.
</p>

</body>
</section>
""" % (dfrom, dnext, butota[0], butota[1], butota[2], butota[3])

print """<section>
<title>Closed bug ranking</title>
<body>

<p>
The developers and teams who have closed the most bugs during this period are as follows.
</p>

<table>
<tr>
  <th>Rank</th>
  <th>Developer/Team</th>
  <th>Bug Count</th>
</tr>
"""
print """<tr>
  <ti>0</ti>
  <ti>Others</ti>
  <ti>%d</ti>
</tr>""" % clothers

for i in range(0, len(cldata)):
	print """<tr>
  <ti>%d</ti>
  <ti>%s</ti>
  <ti>%d</ti>
</tr>""" % (i+1, clkraw[i], cldata[i])

print """</table>

<figure link="closed.png" short="Bugs closed" caption="Bug closed rankings"/>

</body>
</section>

<section>
<title>Assigned bug ranking</title>
<body>

<p>
The developers and teams who have been assigned the most bugs during this period are as follows.
</p>

<table>
<tr>
  <th>Rank</th>
  <th>Developer/Team</th>
  <th>Bug Count</th>
</tr>
"""
print """<tr>
  <ti>0</ti>
  <ti>Others</ti>
  <ti>%d</ti>
</tr>""" % opothers

for i in range(0, len(opdata)):
	print """<tr>
  <ti>%d</ti>
  <ti>%s</ti>
  <ti>%d</ti>
</tr>""" % (i+1, opkraw[i], opdata[i])

print """</table>

<figure link="opened.png" short="Bugs assigned" caption="Bugs assigned rankings"/>

</body>
</section>
</chapter>
"""
