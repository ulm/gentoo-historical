#!/usr/bin/python

import httplib, string, time, sys, os
import urllib2

def strip(x):
        '''Removes quotation marks
           from beginning and end of fields'''
        if len(x):
                if x[0]=='\"':
                        x=x[1:]
                if x[-1]=='\"':
                        x=x[0:-1]

        return x

def get_page(site, uri, header):
        '''Given a site, the name of the resource to get,
           and a dictionary of header values, returns the
           requested resource.  Will return an empty string
           if something goes wrong.'''
	conn = urllib2.Request("https://"+site+uri, None, header)
	response = urllib2.urlopen(conn)
	page = response.read()
	return page

def group_results(result, group_by, details):
    '''Given a column to group by, will accumulate a count
       of rows sharing the same value in the grouped column.
       By default, this function returns a list of lists, each of which
       have the group_by value in position 0, and the count in position 1.

       There is also a sort of poor aggregation mechanism that works sort of
       like sql group by.  With an empty details parameter, this function works
       like 'select group_by, count(*) bug_count from bugzilla group by group_by'.  Adding
       values to the details list (for instance [assigned_to_realname]) will make
       the result more like 'select group_by, count(*), [column for column in details]
       from bugzilla group by group_by, [column for column in details]'.'''


    lines = result.split("\n")

    field_names = string.split(lines[0],',')

    by_group = {}
    detailDict = {}
    for line in lines[1:]:
        b = dict(map((lambda k,v: (k,v)), field_names, string.split(line,',')))
        by_group[b[group_by]] = by_group.get(b[group_by],0) + 1
        #capture the first result for each unique group_by
        if (by_group[b[group_by]] == 1):
        	detailDict[b[group_by]] = b


    count_by_group = [[bug_count, group] for group, bug_count in by_group.items()]
    count_by_group.sort()
    count_by_group.reverse()
    count_by_group = [[group, bug_count, [detailDict[group][detailKey] for detailKey in details]] for bug_count, group in count_by_group]
    return count_by_group

def sum_results(result):
    '''Given a CSV generated from reports.cgi will return a dictionary
       with the sum for each row. The grand total will also be added
       to the 'Total' entry.'''

    lines = result.split("\n")

    result_dict = {}
    total = 0

    for line in lines[1:]:
        split_list = line.split(',')
        summed = sum(map(lambda x: int(x), split_list[1:]))
        total += summed
        result_dict[split_list[0]] = summed
    result_dict['Total'] = total

    return result_dict

# get dates from command line, else use now (time.time())
starttime = time.gmtime(time.time() - (60 * 60 * 24 * 31))
endtime = time.gmtime(time.time() - (60 * 60 * 24 * 1))

if len(sys.argv) > 1:
  if len(sys.argv) >= 2:
    starttime = time.strptime(str(int(sys.argv[1])), "%Y%m%d")
    if len(sys.argv) == 3:
        endtime = time.strptime(str(int(sys.argv[2])), "%Y%m%d")
else:
    print "Usage: " + os.path.basename(sys.argv[0]) +  " [start-date] [end-date]"
    print "dates must be passed in 'yyyymmdd' format"
    print "if no dates are specified then it defaults to a date range of the last 30 days"

dateimg = time.strftime("%Y-%m",endtime)
datefor = time.strftime("%Y/%m",endtime)

#1.  Set up the dates we care about...a 30 day window that ends yesterday
date_to = time.strftime("%Y-%m-%d", endtime)
date_to_display = time.strftime("%d %B %Y", endtime)
date_from = time.strftime("%Y-%m-%d", starttime)
date_from_display = time.strftime("%d %B %Y", starttime)

#2.  Setup a cookie to tell bugzilla the columns we care about
header = {"Cookie" : "COLUMNLIST=bug_severity assigned_to assigned_to_realname bug_status"}

#3.  Pass off the queries we care about to bugzilla
closed_report = get_page("bugs.gentoo.org", "/buglist.cgi?bug_status=RESOLVED&bug_status=CLOSED&chfield=bug_status&resolution=FIXED&ctype=csv&chfieldfrom=%s&chfieldto=%s" % (date_from, date_to), header)
closed_nofix_report = get_page("bugs.gentoo.org", "/buglist.cgi?bug_status=RESOLVED&bug_status=CLOSED&chfield=bug_status&resolution=NEEDINFO&resolution=WONTFIX&resolution=CANTFIX&resolution=INVALID&resolution=UPSTREAM&ctype=csv&chfieldfrom=%s&chfieldto=%s" % (date_from, date_to), header)
duplicate_report = get_page("bugs.gentoo.org", "/buglist.cgi?bug_status=RESOLVED&bug_status=CLOSED&chfield=bug_status&resolution=DUPLICATE&ctype=csv&chfieldfrom=%s&chfieldto=%s" % (date_from, date_to), header)
opened_report = get_page("bugs.gentoo.org", "/buglist.cgi?bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&chfield=[Bug+creation]&ctype=csv&chfieldfrom=%s&chfieldto=%s" % (date_from, date_to), header)
new_report = get_page("bugs.gentoo.org", "/buglist.cgi?chfield=[Bug+creation]&chfieldfrom=%s&chfieldto=%s&ctype=csv" % (date_from, date_to), header)
total_opened_report = get_page("bugs.gentoo.org", "/report.cgi?x_axis_field=bug_status&bug_status=UNCONFIRMED&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&format=table&action=wrap&ctype=csv", header)
severities_report = get_page("bugs.gentoo.org", "/report.cgi?x_axis_field=bug_status&y_axis_field=bug_severity&bug_status=UNCONFIRMED&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&bug_severity=blocker&bug_severity=critical&bug_severity=major&format=table&action=wrap&ctype=csv", header)

#4.  In a few cases, we want more than just counts.  So, we group
#    opened and closed bugs by assigned to.
groups_that_closed_most = group_results(closed_report, "\"assigned_to\"", ["\"assigned_to_realname\""])
groups_that_opened_most = group_results(opened_report, "\"assigned_to\"", ["\"assigned_to_realname\""])

#5.  For bug counts, just counting the lines that were returned is sufficient
new_bug_count = len(new_report.split("\n")) - 1
closed_bug_count = len(closed_report.split("\n")) - 1
duplicate_bug_count = len(duplicate_report.split("\n")) - 1
closed_nofix_bug_count = len(closed_nofix_report.split("\n")) - 1

#6.  For the total open bugs and severities we need to sum the results
#	 generated from reports.cgi
total_open_bug_count = sum_results(total_opened_report).get('Total', 0)
severities = sum_results(severities_report)

# Calculate remaining closed/opened
total_closed = 0
total_opened = 0
for i in range(0, len(groups_that_closed_most) - 1):
	total_closed += groups_that_closed_most[i][1]
for i in range(0, len(groups_that_opened_most) - 1):
	total_opened += groups_that_opened_most[i][1]

#7.  We have every value we need, now build the report

print "<h1>Bugzilla</h1>"

print "The Gentoo community uses <a href=\"https://bugs.gentoo.org\">Bugzilla</a> to record and " + \
"track bugs, notifications, suggestions and other interactions with the " + \
"development team."

print "<h2>Activity</h2>"
print"The following tables and charts summarize the " + \
"activity on Bugzilla between <strong>%s</strong> and <strong>%s</strong>. Not fixed means bugs that were " % (date_from_display, date_to_display) + \
"resolved as NEEDINFO, WONTFIX, CANTFIX, INVALID or UPSTREAM. "

print """<a
href="http://blogs.gentoo.org/news/files/%s/gmn-activity-%s.png"><img
class="size-full wp-image-219 aligncenter" alt="gmn-activity-%s"
src="http://blogs.gentoo.org/news/files/%s/gmn-activity-%s.png"
width="500" height="300" /></a>""" % (datefor,dateimg,dateimg,datefor,dateimg)
print "[table]"
print "Bug Activity, Number"
print "New, %d" % new_bug_count
print "Closed, %d" % closed_bug_count
print "Not fixed, %d" % closed_nofix_bug_count
print "Duplicates, %d" % duplicate_bug_count
print "Total, %d" % total_open_bug_count
print "Blocker, %d" % severities.get('"blocker"',0)
print "Critical, %d" % severities.get('"critical"',0)
print "Major, %d" % severities.get('"major"',0)
print "[/table]"

cleft = 0
#8. Closed Bugs
print "\n<h2>Closed bug ranking</h2>\n"
print "The following table outlines the teams and developers with the most bugs resolved during this period"
print "[table]"
print "Rank, Team/Developer, Bug Count"
for i in range(0,9):
	print "%d, %s, %d" % (i+1, strip(groups_that_closed_most[i][2][0]), int(groups_that_closed_most[i][1]))
	cleft += groups_that_closed_most[i][1]
print "10, Others, %s" % (total_closed - cleft)
print "[/table]"

print """<a
href="http://blogs.gentoo.org/news/files/%s/gmn-closed-%s.png"><img
class="aligncenter size-full wp-image-220" alt="gmn-closed-%s"
src="http://blogs.gentoo.org/news/files/%s/gmn-closed-%s.png"
width="500" height="250" /></a>""" % (datefor,dateimg,dateimg,datefor,dateimg)
#9. Open Bugs
#print "\n\n==Open Bugs==\n"
oleft = 0
print "\n<h2>Assigned bug ranking</h2>\n"
print "The developers and teams who have been assigned the most bugs during this period are as follows.\n"
print "[table]"
print "Rank, Team/Developer, Bug Count"
for i in range(0,9):
	print "%d, %s, %s" % (i+1, strip(groups_that_opened_most[i][2][0]), str(groups_that_opened_most[i][1]))
	oleft += groups_that_opened_most[i][1]
print "10, Others, %s" % (total_opened - oleft)
print "[/table]"
print """<a
href="http://blogs.gentoo.org/news/files/%s/gmn-opened-%s.png"><img
class="aligncenter size-full wp-image-220" alt="gmn-opened-%s"
src="http://blogs.gentoo.org/news/files/%s/gmn-opened-%s.png" width="500"
height="250" /></a> """ % (datefor,dateimg,dateimg,datefor,dateimg)
