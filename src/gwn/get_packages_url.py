arch = ['alpha', 'amd64', 'arm', 'hppa', 'ia64', 'm68k', 'mips', 'ppc', 'ppc64', 's390', 'sh', 'sparc', 'sparc-fbsd', 'x86', 'x86-fbsd']
stable = [3629, 6969, 1595, 2660, 3223, 493, 1104, 6239, 3431, 1201, 1415, 4805, 0, 9327, 0]
testing = [435, 3867, 72, 488, 552, 16, 671, 2858, 621, 47, 45, 1275, 316, 3054, 2493]
svals = []
tvals = []
tot = []
for i in range(0, 15):
	svals.append(round(stable[i] / 123.81, 2))
	tvals.append(round(testing[i] / 123.81, 2))
	tot.append(stable[i]+testing[i])

string1 = ''
string2 = ''
for i in range(0, len(svals)):
	string1 += str(svals[i])
	string2 += str(tvals[i])
	if i != len(svals) - 1:
		string1 += ','
		string2 += ','
print string1
print string2
#packages = StackedHorizontalBarChart(900, 250)
#packages.set_colours(['45347B', '6A5C95'])
#packages.set_bar_width(50)
#packages.add_data(svals)
#packages.add_data(tvals)
#packages.set_axis_labels(Axis.BOTTOM, arch)
#packages.download('packages.png')
#print packages.get_url()

base = 'http://chart.apis.google.com/chart?cht=bhs&chs=800x350&chd=t:'
tail = '&chco=45347B,6A5C95&chbh=15&chxt=x,y&chxr=0,0,12250&chdl=Stable|Testing'
labx = '&chxl=0:10533|1655|2813|3744|496|1771|8928|4011|1237|1445|6012|304|12212|2431|'
laby = '1:|x86-fbsd|x86|sparc-fbsd|sparc|sh|s390|ppc64|ppc|mips|m68k|ia64|hppa|arm|amd64|alpha'

final = base + string1 + '|' + string2 + tail + labx + laby
print final
