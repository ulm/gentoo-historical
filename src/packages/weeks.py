#!/usr/bin/python -OO

import time
import MySQLdb
from cgi import escape
import ebuilddb
import config
import gentoo

SECS_PER_DAY = 86400
DAYS = ('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')

def get_dayname(day):
	return DAYS[day[6]]

def get_days_ebuilds(day):
	c = db.cursor()
	query = ('SELECT ebuild.category, '
		'ebuild.name, '
		'version, '
		'when_found, '
		'description, '
		'changelog, '
		'arch, '
		'homepage, '
		'license '
		'FROM ebuild,package '
		'WHERE TO_DAYS(when_found) = TO_DAYS("%s-%02d-%02d") '
		'AND ebuild.name = package.name '
		'AND ebuild.category = package.category '
		'ORDER BY when_found DESC' %
		(day[0],day[1],day[2]))
	#print query
	c.execute(query)
	results = c.fetchall()
	return results

today = time.time()
db = ebuilddb.db_connect()
for day in range(today,today - (7*SECS_PER_DAY),-SECS_PER_DAY):
	#print day
	gmtime = time.gmtime(day)
	dayname = get_dayname(gmtime)
	print ('<a href="%sdaily/%s/%02d/%02d/">%s</a>:<br>' 
		% (config.FEHOME,gmtime[0],gmtime[1],gmtime[2],dayname))
	results = get_days_ebuilds(gmtime)
	#print results
	ebuilds = [ gentoo.query_to_dict(i) for i in results ]
	#ebuilds.sort(ebuild_sort)
	for ebuild in ebuilds:
		print ('. <a class="altlink" title="%s" href="%sebuilds/?%s-%s">%s %s</a><br>' % 
		(escape(ebuild['description']),
		config.FEHOME,
		ebuild['name'], 
		ebuild['version'],
		ebuild['name'],
		ebuild['version']))
	print '<br>'
