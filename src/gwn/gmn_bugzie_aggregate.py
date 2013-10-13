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

j = 1
ontable = 0
onheaders = 0
ontext = 0
for i in data:
	if not i.startswith("[table]") and ontable == 0:
		continue
	ontable = 1
	# Ok found a table, we need to skip the
	# [table] and headers lines
	if onheaders == 0: # [table]
		onheaders = 1
		continue
	if onheaders == 1 and ontext == 0: # [headers]
		ontext = 1
		continue
	# reached the end of the table, need to start over
	if i.startswith("[/table]"):
		ontext = 0
		onheaders = 0
		ontable = 0
		continue
	#Here is the real text
	values = i.strip().split(',')
	# A few tables contain ranking numbers. Remove them
	if len(values) == 3:
		values.pop(0)
	if j > 0 and j <= 4:
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

print "Done!"
