#!/usr/bin/python -OO
"""These functions mainly take ebuild info (grabbed from the database and
    convert it to HTML.  See the "main" function at the bottom."""

__revision__ = "$Revision: 1.5 $"
# $Source: /var/cvsroot/gentoo/src/packages/gentoo.py,v $

import config
import os
import time
import sys
import ebuilddb
import bugs
import changelogs
from cgi import escape
from urllib import quote

# import portage, but temporarily redirect stderr
if 'portage' not in dir():
    null = open('/dev/null', 'w')
    tmp = sys.stderr
    sys.stderr = null
    sys.path = ["/usr/lib/portage/pym"]+sys.path
    import portage
    sys.stderr = tmp
    sys.path = sys.path[1:]

tree = portage.portdbapi('/usr/portage')

def is_masked(ebuild):
    """Return true if ebuild is masked"""

    return (not tree.visible(['%(category)s/%(name)s-%(version)s' % ebuild]))
    
def is_new(db, ebuild):
    """Check for newness. An ebuild is considered new if it is the
    only ebuild with that category/name in ebuild and it has no prevarch"""
    
    c = db.cursor()
    query = ('SELECT prevarch FROM ebuild WHERE category="%s" AND name="%s"'
        % (ebuild['category'], ebuild['name']))
    c.execute(query)
    results = c.fetchall()
    if len(results) == 1 and results[0][0] is None:
        return 1
    return 0

def changelog_to_html(changelog):
    """HTML-ize a changelog entry"""
    html = ""
    for char in changelog:
        if char == '\n':
            html = "%s<br>" % html
        else:
            html = "%s%s" % (html, escape(char))
    html = changelogs.bugs_to_html(html)
    return html

def homepage_to_html(homepage):
    """convert HOMEPAGE entry to HTML"""
    if not homepage.strip(): 
        return "?"
    homepage = homepage.replace('|',' ')
    pieces = homepage.split()
    count = len(pieces)
    if count == 1:
        return ('<a class="homepage" href="%s">'
            'Homepage</a>' % pieces[0])
            
    html = ['[<a href="%s">%s</a>]' % (page, index + 1) for index,
        page in enumerate(pieces)]
    return " ".join(['<span class="homepage">Homepages'] + html + 
        ['</span>'])

def license_to_html(license):
    """Create link to license[s]"""
    if not license.strip(): return "?"
    license = license.replace('|',' ')
    pieces = license.split()
    html = ['<a href="http://www.gentoo.org/cgi-bin/viewcvs.cgi/*checkout*/'
        'licenses/%s">%s</a>' % (piece, piece) for piece in pieces]
    return '<br>\n'.join(html)

def package_to_html(pkginfo, db):
    """This function needs a database (db) connection because it performs a 
    query_to_dict on the package"""
    
    table_begin = '<table class="ebuild">'
    name = '<tr><td class="fields">%s</td></tr>' % pkginfo['name']
    description = ('<tr><td class="item">'
        '<img align="right" alt="" src="%s/%s.png">'
        '<b>Description: </b>%s</td></tr>' % (config.ICONS, 
        pkginfo['category'], escape(pkginfo['description'])))
    ebuilds = get_recent_releases(pkginfo, db)
    releases = '<tr><td>%s</td></tr>' % archs_to_html(ebuilds, 'Releases')
    #bug_string = ('<br><h3>Related bugs:</h3>\n%s' 
    #    % bugs_to_html(pkginfo['name']))
    general = '<tr><td>%s</td></tr>' % general_info_to_html(pkginfo)
    table_end = '</table>'
    rows = '\n\t'.join([name, description, releases, general])
    return '\n\t'.join([table_begin, rows, table_end])

def archs_to_html(ebuilds, heading = None):
    """Create table for availability on each architecture"""
    heading = heading or '&nbsp;'
    table_begin = '<table class="releases">'
    header_row = ''.join(['<tr><td><b>%s</b></td>' % heading] +
        ['<th class="arch">%s</th>' % i for i in config.ARCHLIST] +
        ['</tr>']
    )
    rows = []
    for ebuild in ebuilds:
        masked = is_masked(ebuild)
        archs = ebuild['arch'].split()
        row_start = ('<tr>\n\t<th class="releases"><a href="%sebuilds/?%s-%s"'
            ' title="%s">%s</a></th>\n' % (config.FEHOME, 
                ebuild['name'], ebuild['version'], ebuild['time'], 
                ebuild['version']))
        row_data = []
        for arch in config.ARCHLIST:
            if arch in archs:
                arch_string = '+'
            elif '~%s' % arch in archs:
                arch_string = '~'
            else:
                arch_string = '-'
            if arch_string != '-' and masked:
                arch_string = 'M' + arch_string
            row_data.append('\t<td class="archcell" arch="%s">%s</td>'
                % (arch_string, arch_string))
        row_end = '</tr>'
        rows.append('\n\t'.join([row_start] + row_data + [row_end]))
    table_end = '</table>'
    return '\n\t'.join([table_begin] + [header_row] + rows + [table_end])
    
def ebuild_to_html(ebinfo, new=0, show_bugs=0):
    """Convert ebuild (dict) to html, if new, print out a "this is new" notice
    if show_bugs, show bugs for this particular ebuild (requires access to
    bugzilla"""
    if new:
        new_string = """ &nbsp;&nbsp;<span class="new">new!</span> """
    else:
        new_string = ""
        
    table_begin = '<table class="ebuild">'
    name_and_date = ('<tr><td class="fields">'
        '<a href="%spackages/?category=%s;name=%s">%s</a> %s%s<br>'
        '<span class="time">%s</span>'
        '</td></tr>' % (config.FEHOME, quote(ebinfo['category']),
        quote(ebinfo['name']),
        ebinfo['name'],
        ebinfo['version'],
        new_string,
        ebinfo['time'].localtime().strftime("%c %Z")))
        
    desc_and_changes = ('<tr><td class="item" valign="top">'
        '<img alt="" align="right" src="%simages/%s.png">' 
        '<p><b>Description:</b> %s</p>'
        '<p><b>Changes:</b><br>'
        '%s</p></td></tr>' % (
        config.FEHOME,
        ebinfo['category'],
        escape(ebinfo['description']),
        changelog_to_html(ebinfo['changelog'])))

    archs = '<tr><td>%s</td></tr>' % archs_to_html([ebinfo])
    general = '<tr><td>%s</td></tr>' % general_info_to_html(ebinfo)
    table_end = '</table>'
    
    if 1 == 1:
        bug_string = ''
    else:
        bug_string = '<br><h3>Related bugs:</h3>%s' \
            % bugs_to_html(ebinfo['name'])
            
    return '\n\t'.join([table_begin, 
        name_and_date, 
        desc_and_changes, 
        archs,
        general, 
        table_end, 
        bug_string])
      
def general_info_to_html(pkg):
    """This actually will (should) take either a package or ebuild dict
    as an argument"""
    
    changelogurl = ('http://www.gentoo.org/cgi-bin/viewcvs.cgi/*checkout*/'
        '%s/%s/ChangeLog' % (pkg['category'],pkg['name']))
    cat_header = '<th class="category">Category</th>'
    license_header = '<th class="license">License</th>'
    category = ('<td class="category">'
        '<a href="%spackages/?category=%s">%s</a></td>'  % (config.FEHOME, 
        pkg['category'], pkg['category']))
    homepage = ('<td class="homepage" rowspan="2">%s</td>' 
        % homepage_to_html(pkg['homepage']))
    license = ('<td class="license">%s</td>' 
        % license_to_html(pkg['license']))
    changelog = ('<td class="changelog" rowspan="2">'
        '<a href="%s">ChangeLog</a><td>' % changelogurl)
    
    return '\n\t'.join(['<table class="general_info">',
        '<tr>',
        cat_header,
        homepage,
        license_header,
        changelog,
        '</tr>',
        '<tr>',
        category,
        license,
        '</tr>',
        '</table>'])
        
def bugs_to_html(package):
    """Given package name (no version #s), return html text of bugs as
    reported by bugzilla"""
    # Right now we have an issue with the bugzilla site.  New interface
    # needs to be written, Bail out.
    return ""
    import urllib2
    url = ('http://bugs.gentoo.org/buglist.cgi?query_format='
            '&short_desc_type=allwords&short_desc=%s'
            '&bug_status=UNCONFIRMED&bug_status=NEW&bug_status=ASSIGNED'
            '&bug_status=REOPENED'
            '&ctype=csv' % package)
    fp = urllib2.urlopen(url)
    factory = bugs.BugFactory()
    package_bugs = factory.fromCSV(fp)
    if package_bugs:
        writer = bugs.HTMLWriter(package_bugs, 'bugs.gentoo.org')
        return str(writer)
    else:
        return "None"
                
def get_most_recent(db, max=config.MAXPERPAGE, arch="", branch=""):
    c = db.cursor()
    extra = ''
    if arch:
        stable_extra = ('ebuild.arch REGEXP "^%s| %s" '
            ' AND ebuild.prevarch NOT REGEXP"^%s| %s"'
            % (arch,arch,arch,arch))
        testing_extra = ('ebuild.arch REGEXP "^~%s| ~%s" '
            ' AND ebuild.prevarch NOT REGEXP "^~%s| ~%s"'
            % (arch,arch,arch,arch))
        if branch == 'stable':
            extra = ' AND (%s) ' % stable_extra
        elif branch == 'testing':
            extra = ' AND (%s) ' % testing_extra
        else:
            extra = ' AND ((%s) OR (%s)) ' % (stable_extra, testing_extra)
    query = """SELECT ebuild.category,ebuild.name,version,when_found,description,
    changelog,arch,homepage,license FROM ebuild,package WHERE ebuild.name=\
    package.name AND ebuild.category=package.category %s ORDER by when_found DESC \
    LIMIT %s""" % (extra,max)
    c.execute(query)
    results = c.fetchall()
    return results
    
def query_to_dict(d):
    """Convert a SQL query to a dict"""
    einfo = {}
    keys = ('category', 'name', 'version', 'time', 'description', 'changelog',
        'arch', 'homepage', 'license')
    for i in range(len(keys)):
        try:
            einfo[keys[i]] = d[i]
        except IndexError:
            continue
    return einfo

def get_recent_releases(pkg, db, max=config.MAX_RECENT_RELEASES):
    """Return MAX_RECENT_RELEASES most recent releases for pkg.  Returns and
    ebuild-type dict"""
    c = db.cursor()
    query = ('SELECT category,name,version,when_found,NULL,changelog,arch ,'
        'NULL,NULL FROM ebuild WHERE name="%s" AND category="%s" ORDER BY '
        'version DESC LIMIT %s' % (pkg['name'],pkg['category'],max))
    c.execute(query)
    results = c.fetchall()
    #print results
    return [ query_to_dict(i) for i in results ]
    
def ebuilds_to_rss(fp, ebuilds, simple=False, subtitle=""):
    """write out ebuild info to RSS file (fp)"""
    fp.write("""<?xml version="1.0" encoding="iso-8859-1"?>
        <rss version="0.92">
        <channel>
        <title>Fresh ebuilds %s</title>
        <link>%s</link>
        <description>Latest ebuilds from the Gentoo Linux portage tree</description>
        <![CDATA[<link rel="stylesheet" href="%s" type="text/css" title="styled" />]]>
        <webMaster>www@gentoo.org</webMaster>
        <managingEditor>marduk@gentoo.org</managingEditor>
        <pubDate>%s</pubDate>""" % (subtitle,config.FEHOME, config.STYLESHEET,
            time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())))

    for ebuild in ebuilds:
        if simple:
            description = escape(ebuild['description'])
        else:
            description = '\n<![CDATA[\n%s\n]]>' % ebuild_to_html(ebuild)

        fp.write("""<item>
            <title>%s %s</title>
            <link>%sebuilds/?%s-%s</link>
            <description>
                %s
            </description>
            <pubDate>%s</pubDate>
        </item>
        """ % (ebuild['name'],
                ebuild['version'],
                config.FEHOME,
                ebuild['name'],
                ebuild['version'],
                description,
                ebuild['time'].gmtime().strftime("%a, %d %b %Y %H:%M:%S +0000"))
        )
        
    fp.write("</channel>\n</rss>\n")
    
def main(argv=Null):
    argv = argv or sys.argv
    try:
        if argv[1] == '-g':
            ebuilddb.main()
    except IndexError:
        pass
            
    db = ebuilddb.db_connect()
    branches = ('', 'stable', 'testing')
    for arch in [''] + config.ARCHLIST:
        for branch in branches:
            fullpath = os.path.join(config.LOCALHOME, "archs", arch, branch, 
                config.INDEX)
            index = open(fullpath,'w')
            if arch:
                sarch = arch
            else:
                sarch = 'all'
            if branch:
                sbranch = branch
            else:
                sbranch = 'all'
            
            index.write("""<table border="0" cellpadding="0" cellspacing="5" 
                width="100%">\n""")
            index.write("""<tr><td valign="top">\n""")
            index.write('<!--#include file="archnav.html" -->\n\n</td></tr>\n'
                '<tr><td>') 
            results = get_most_recent(db, arch=arch, branch=branch)
            ebuilds = [ query_to_dict(i) for i in results ]
            for ebuild in ebuilds:
                new = is_new(db, ebuild)
                pkgfilename = "%s/%s-%s.html" % (
                    config.EBUILD_FILES,ebuild['name'],ebuild['version'])
                ebuild_html = ebuild_to_html(ebuild, new)
                if arch == '' and branch == '':
                    pkgfile = open(pkgfilename,'w')
                    pkgfile.write(ebuild_html)
                    pkgfile.close()
                    ebuildfilename = "%s/%s/%s/%s-%s.ebuild" \
                        % (ebuilddb.config.PORTAGE_DIR,
                        ebuild['category'],ebuild['name'],ebuild['name'],
                        ebuild['version'])
                    os.system('touch -r %s %s || touch -d "today -1 year" %s' 
                        % (ebuildfilename,pkgfilename,pkgfilename))
        
                try:
                    index.write('%s\n\n' % (ebuild_html))
                except IOError:
                    continue
            index.write("""</table>\n""")
            index.close()
            
            subtitle = ' %s %s' % (arch, branch)
            rss = open(os.path.join(config.LOCALHOME, "archs", arch, branch,
                config.RSS), 'w')
            ebuilds_to_rss(rss, ebuilds, simple=False, subtitle=subtitle)
            rss.close()
        
            rss2 = open(os.path.join(config.LOCALHOME, "archs", arch, branch,
                config.RSS2), 'w')
            ebuilds_to_rss(rss2, ebuilds, simple=True, subtitle=subtitle)
            rss.close()

if __name__ == '__main__':
    sys.exit(main())
