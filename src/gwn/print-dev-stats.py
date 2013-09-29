# Get devaway.xml from http://www.gentoo.org/dyn/devaway/devaway.xml?passthru=1
import xml.dom.minidom
import urllib2
import os

dev_rollcall = "/home/hwoarang/development/gentoo-cvs/gentoo/xml/htdocs/proj/en/devrel/roll-call/userinfo.xml"

devaway = open('devaway.txt', 'w')
devaway.write(urllib2.urlopen("http://www.gentoo.org/dyn/devaway/devaway.xml?passthru=1").read())
devaway.close()
dom = xml.dom.minidom.parse(dev_rollcall)
aom = xml.dom.minidom.parse("devaway.txt")

dev = dom.getElementsByTagName('user')
tot = len(dev)
awa = aom.getElementsByTagName('dev')
awa = len(awa)
cnt = 0

for d in dev:
	ret = d.getElementsByTagName('status')
	if not ret:
		cnt += 1

print tot, cnt, awa

os.remove("devaway.txt")
