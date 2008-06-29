# Get devaway.xml from http://www.gentoo.org/dyn/devaway/devaway.xml?passthru=1
import xml.dom.minidom

dom = xml.dom.minidom.parse('/home/anant/gentoo/gentoo/xml/htdocs/proj/en/devrel/roll-call/userinfo.xml')
aom = xml.dom.minidom.parse('devaway.xml')

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
