#!/usr/bin/python -OO

import time
import MySQLdb
import ebuilddb
import config
import gentoo

def get_categories():
	db = ebuilddb.db_connect()
	c = db.cursor()
	query = ('SELECT DISTINCT(category) '
		'FROM ebuild '
		'ORDER BY category ')
	#print query
	c.execute(query)
	results = c.fetchall()
	return results

categories = [x[0] for x in get_categories()]
for category in categories:
	#print category
	print ('. <a class="altlink" href="%spackages/?category=%s">%s</a><br>' % 
		(config.FEHOME,
		category,
		category))
print '<br>'
