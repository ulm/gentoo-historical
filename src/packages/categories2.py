#!/usr/bin/python -OO

import time
import MySQLdb
import ebuilddb
import config
import gentoo

COLS=5

def get_categories():
	db = ebuilddb.db_connect()
	c = db.cursor()
	query = ('SELECT category,COUNT(DISTINCT(name)) '
		'FROM ebuild '
		'GROUP BY category '
		'ORDER BY category ')
	#print query
	c.execute(query)
	results = c.fetchall()
	return results


if __name__ == '__main__':
    print '<table class="categories">'
    results = get_categories()
    total = len(results)
    row_count = total / COLS
    if (total % COLS):
        row_count = row_count + 1
    cols = [[] for i in range(5)]
    package_total = 0
    current_col = 0
    for result in results:
        if len(cols[current_col]) == row_count:
            current_col = current_col + 1
        category, count = result
        package_total = package_total + count
        cols[current_col].append(result)
    #cols[current_col].extend([('',0)]* row_count)
    for i in range(row_count):
        print '\n\t'.join(['<tr>'] + [('<td class="category">'
            '<a href="%spackages/?category=%s">%s (%d)</a></td>' % 
            (config.FEHOME, category, category, count)) for
            category, count in [x[i] for x in cols if len(x) > i] ] + ['</tr>'])
    print '</table>\n'
    print ('<div class="summary">A total of %d packages exist '
        'in portage.</div>' % package_total)
