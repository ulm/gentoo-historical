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

stable = []
testing = []

svals = []
tvals = []
tot = []


os.system("qcache -sCq | tail -n 47 | head -n 16 | cut -d \"|\" -f 2-4 | sed \"s:|::g\" > pkgstats.txt")

# read input files
with open("pkgstats.txt") as f:
	for line in f:
		line=line.split()
		stable.append(int(line[1]))
		testing.append(int(line[2]))
f.close()
os.remove("pkgstats.txt")

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
base = 'http://chart.apis.google.com/chart?cht=bhs&chs=800x350&chd=t:'
tail = '&chco=45347B,6A5C95&chbh=15&chxt=x,y&chxr=0,0,12250&chdl=Stable|Testing'
labx = '&chxl=0:1000|1000|1000|1000|1000|1000|1000|1000|1000|1000|1000|1000|1000|1000|1000|'
laby = '1:|x86-fbsd|x86|sparc-fbsd|sparc|sh|s390|ppc64|ppc|mips|m68k|ia64|hppa|arm|amd6-fbsd|amd64|alpha'

final = base + string1 + '|' + string2 + tail + labx + laby
print final
