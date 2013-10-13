#!/usr/bin/env python
import os

arch = [
'alpha',
'amd64',
'amd64-fbsd',
'arm',
'hppa',
'ia64',
'm68k',
'mips',
'ppc',
'ppc64',
's390',
'sh',
'sparc',
'sparc-fbsd',
'x86',
'x86-fbsd']

gen_stats = [
'architectures',
'categories',
'packages',
'ebuilds']

gen_stats_num = []

stable = []
testing = []
total = []
percent = []

svals = []
tvals = []
tot = []

# Get general portage stats
os.system("qcache  -sCq | sed \"s:|::g\" > pkgstats.txt")

# read input files
with open("pkgstats.txt") as f:
	for line in f:
		line=line.split()
		try:
			col = line[0].strip()
		except:
			continue
		if col in gen_stats:
			gen_stats_num.append(str(line[1].strip()))
		elif col in arch:
			#print line[0] + ", " + line[1] + ", " + line[2] +", " + \
			#	line[3] + ", " + line[4]
			stable.append(int(line[1]))
			testing.append(int(line[2]))
			total.append(int(line[3]))
			percent.append(line[4])
f.close()
os.remove("pkgstats.txt")

print "[table th=\"0\"]"
print "Architectures, " + gen_stats_num[0]
print "Categories, "  + gen_stats_num[1]
print "Packages, " + gen_stats_num[2]
print "Ebuilds, " + gen_stats_num[3]
print "[/table]\n"

print "[table]"
print "Architecture, Stable, Testing, Total, % of Packages"
for x in range(0, len(arch)):
	print arch[x] + ", " + str(stable[x]) + ", " + \
	str(testing[x]) + ", " + str(total[x]) + ", " + percent[x]
print "[/table]\n"

for i in range(0, len(arch)):
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
#print string1
#print string2
print "\n== Chart URL == \n"
base = 'http://chart.apis.google.com/chart?cht=bhs&chs=800x350&chd=t:'
tail = '&chco=45347B,6A5C95&chbh=15&chxt=x,y&chxr=0,0,12250&chdl=Stable|Testing'
labx = '&chxl=0:1000|1000|1000|1000|1000|1000|1000|1000|1000|1000|1000|1000|1000|1000|1000|'
laby = '1:'

for x in reversed(range(0, len(arch))):
	laby = laby + "|" + arch[x]

final = base + string1 + '|' + string2 + tail + labx + laby
print final
