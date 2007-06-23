#!/usr/bin/python -O
"""These functions mainly take ebuild info (grabbed from the database and
    convert it to HTML.  See the "main" function at the bottom."""

__revision__ = "$Revision: 1.16.2.6 $"
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
from portage_versions import pkgcmp, pkgsplit

def is_new(db, ebuild):
    """Check for newness."""

    c = db.cursor()
    query = ('SELECT new FROM package WHERE category="%s" AND name="%s"'
        % (ebuild['category'], ebuild['name']))
    c.execute(query)
    results = c.fetchall()
    if len(results) == 1 and results[0][0]:
        return 1
    return 0

changelog_to_html = changelogs.bugs_to_html

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
    license = license.replace('(', '')
    license = license.replace(')', '')
    pieces = license.split()
    html = ['<a href="http://sources.gentoo.org/viewcvs.py/*checkout*/'
        'gentoo-x86/licenses/%s">%s</a>' % (piece, piece) for piece in pieces]
    return '<br>\n'.join(html)

def package_to_html(pkginfo, db, full=False):
    """This function needs a database (db) connection because it performs a
    query_to_dict on the package"""

    table_begin = '<table class="ebuild">'
    name = '<tr><td class="fields">%s</td></tr>' % pkginfo['name']
    if full:
        image = ('<img class="pkgimg"alt="" src="%s/%s/%s.jpg" align="right">' %
                (config.ICONS, pkginfo['category'], pkginfo['name'])
        )
    else:
        image = ''
    description = ('<tr><td class="item">'
        '%s<b>Description: </b>%s</td></tr>'
        % (image, escape(pkginfo['description']))
    )
    ebuilds = get_recent_releases(pkginfo, db)
    releases = '<tr><td>%s</td></tr>' % archs_to_html(ebuilds, 'Releases')
    #bug_string = ('<br><h3>Related bugs:</h3>\n%s'
    #    % bugs_to_html(pkginfo['name']))
    general = '<tr><td>%s</td></tr>' % general_info_to_html(pkginfo)
    #similar = '<tr><td>%s</td></tr>' % create_similar_pkgs_link(pkginfo)
    table_end = '</table>'
    rows = '\n\t'.join([name, description, releases, general])
    return '\n\t'.join([table_begin, rows, table_end])

def archs_to_html(ebuilds, heading = None):
    """Create table for availability on each architecture"""
    heading = heading or '&nbsp;'
    table_begin = '<table class="releases">'
    header_row = ''.join(['<tr><td><b>%s</b></td>' % heading] +
        ['<th class="arch">%s</th>' % i.replace('-',' ') for i in config.ARCHLIST] +
        ['</tr>']
    )
    rows = []
    ebuilds.sort(cmp_ebuilds)
    ebuilds.reverse()
    for ebuild in ebuilds:
        archs = ebuild['arch'].split(',')
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
            if arch_string != '-' and ebuild['masked']:
                arch_string = 'M' + arch_string
            row_data.append('\t<td class="archcell" arch="%s">%s</td>'
                % (arch_string, arch_string))
        row_end = '</tr>'
        rows.append('\n\t'.join([row_start] + row_data + [row_end]))
    table_end = '</table>'
    return '\n\t'.join([table_begin] + [header_row] + rows + [table_end])

def ebuild_to_html(ebinfo, new=0, show_bugs=0, full = False):
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
        ebinfo['time'].strftime("%c %Z")))

    if full:
        image = ('<img class="pkgimg" alt="" src="%s/%s/%s.jpg" align="right">' %
                (config.ICONS, ebinfo['category'], ebinfo['name'])
        )
    else:
        image = ''
    desc_and_changes = ('<tr><td class="item" valign="top">'
        '<p><b>Description:</b> %s %s</p>'
        '<p><b>Changes:</b><br>'
        '%s</p></td></tr>' % (
        escape(ebinfo['description']),
        image,
        changelog_to_html(ebinfo['changelog'])))

    archs = '<tr><td>%s</td></tr>' % archs_to_html([ebinfo])
    general = '<tr><td>%s</td></tr>' % general_info_to_html(ebinfo)
    table_end = '</table>'

    bug_string = ''
    if show_bugs:
        bug_string = bugs_to_html(ebinfo['name'])
        if bug_string:
            bug_string = '<br><h3 class="bugs">Related bugs:</h3>%s' \
            % bug_string

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

    import forums

    changelogurl = ('http://sources.gentoo.org/viewcvs.py/*checkout*/'
        'gentoo-x86/%s/%s/ChangeLog' % (pkg['category'],pkg['name']))
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
        '<a href="%s">ChangeLog</a></td>' % changelogurl)
    similar = ('<td class="similar" rowspan="2">'
        '%s</td>' % create_similar_pkgs_link(pkg))
    related_bugs = ('<td class="related_bugs" rowspan="2">'
        '%s</td>' % create_related_bugs_link(pkg))
    forums_link = ('<td class="forums" rowspan="2">'
        '%s</td>' % forums.create_forums_link(pkg))

    return '\n\t'.join(['<table class="general_info">',
        '<tr>',
        cat_header,
        homepage,
        license_header,
        changelog,
        similar,
        related_bugs,
        forums_link,
        '</tr>',
        '<tr>',
        category,
        license,
        '</tr>',
        '</table>'])

def create_similar_pkgs_link(pkg):
    """Create a link to similar packages"""

    return '<a href="/similar/?package=%(category)s/%(name)s">Similar</a>' % pkg

def create_related_bugs_link(pkg):
    """Create a link to related bugs"""

    url = ('http://bugs.gentoo.org/buglist.cgi?query_format='
            '&amp;short_desc_type=allwords'
            '&amp;short_desc=%s'
            '&amp;bug_status=UNCONFIRMED'
            '&amp;bug_status=NEW'
            '&amp;bug_status=ASSIGNED'
            '&amp;bug_status=REOPENED'
            % escape(pkg['name']))

    return '<a title="bugs.gentoo.org" href="%s">Bugs</a>' % url

def bugs_to_html(package):
    """Given package name (no version #s), return html text of bugs as
    reported by bugzilla"""
    # Right now we have an issue with the bugzilla site.  New interface
    # needs to be written, Bail out.
    #return ""
    import urllib2
    url = ('http://bugs.gentoo.org/buglist.cgi?query_format='
            '&amp;short_desc_type=allwords'
            '&amp;short_desc=%s'
            '&amp;bug_status=UNCONFIRMED'
            '&amp;bug_status=NEW'
            '&amp;bug_status=ASSIGNED'
            '&amp;bug_status=REOPENED'
            '&amp;ctype=csv'
            % package)
    fp = urllib2.urlopen(url)
    factory = bugs.BugFactory()
    package_bugs = factory.fromCSV(fp)
    if package_bugs:
        writer = bugs.HTMLWriter(package_bugs, 'bugs.gentoo.org')
        return str(writer)
    else:
        return ""

def get_most_recent(db, max=config.MAXPERPAGE, arch="", branch="", new = False):
    c = db.cursor()
    extra = ''
    if arch:
        stable_extra = ('FIND_IN_SET("%s", ebuild.arch) > 0 AND '
            'FIND_IN_SET("%s", ebuild.prevarch) = 0 ' % (arch, arch))
        testing_extra = ('FIND_IN_SET("~%s", ebuild.arch) > 0 AND '
            'FIND_IN_SET("~%s", ebuild.prevarch) = 0 ' % (arch, arch))
        if branch == 'stable':
            extra = ' AND (%s) ' % stable_extra
        elif branch == 'testing':
            extra = ' AND (%s) ' % testing_extra
        else:
            extra = ' AND ((%s) OR (%s)) ' % (stable_extra, testing_extra)

    if new:
        extra = ('%s AND package.new=1 ' % extra)

    query = """SELECT ebuild.category,ebuild.name,version,ebuild.when_found,description,
    changelog,arch,homepage,license,is_masked FROM ebuild,package WHERE ebuild.name=\
    package.name AND ebuild.category=package.category %s ORDER by ebuild.when_found DESC \
    LIMIT %s""" % (extra,max)
    c.execute(query)
    results = c.fetchall()
    return results

def get_most_recent_bumps(db, max=config.MAXPERPAGE):
    """Return most recent version bumps (pkgs with no prevarch)"""
    c = db.cursor()
    query = ('SELECT ebuild.category, ebuild.name, version, when_found, '
        'description, changelog, arch, homepage, license,is_masked FROM ebuild, package '
        'WHERE ebuild.name=package.name AND ebuild.category=package.category '
        'AND prevarch="" AND version NOT LIKE "%%-r_" AND version NOT LIKE '
        '"%%-r__" AND NOT new ORDER by when_found '
        'DESC LIMIT %s' % max)

    c.execute(query)
    results = c.fetchall()
    return results

def query_to_dict(d):
    """Convert a SQL query to a dict"""
    einfo = {}
    keys = ('category', 'name', 'version', 'time', 'description', 'changelog',
        'arch', 'homepage', 'license', 'masked')
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
        'NULL,NULL,is_masked FROM ebuild WHERE name="%s" AND category="%s" ORDER BY '
        'version DESC LIMIT %s' % (pkg['name'],pkg['category'],max))
    c.execute(query)
    results = c.fetchall()
    #print results
    return [ query_to_dict(i) for i in results ]

def cmp_ebuilds(a, b):
    """Compare two ebuilds"""
    fields_a = pkgsplit('%s-%s' % (a['name'], a['version']))
    fields_b = pkgsplit('%s-%s' % (b['name'], b['version']))
    return pkgcmp(fields_a, fields_b)

def ebuilds_to_rss(fp, ebuilds, simple=False, subtitle='', arch='', branch=''):
    """write out ebuild info to RSS file (fp)"""

    # web link for RSS feed
    link = config.FEHOME
    subtitle = subtitle
    if arch != '':
        link = '%sarchs/%s/' % (link, arch)
        subtitle = '%s' % arch
        if branch != '':
            link = '%s%s/' % (link, branch)
            subtitle = '%s %s' % (subtitle, branch)

    title = 'packages.gentoo.org'
    if subtitle:
        title = '%s [ %s ]' % (title, subtitle)

    pubDate = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    fp.write("""<rss version="2.0">
        <channel>
        <title>%s</title>
        <link>%s</link>
        <description>Latest ebuilds from the Gentoo Linux portage tree</description>
        <webMaster>www@gentoo.org</webMaster>

        <image>
            <title>Online Package Database</title>
            <url>%s</url>
            <link>%s</link>
        </image>

        <managingEditor>marduk@gentoo.org</managingEditor>
        <pubDate>%s</pubDate>""" % (title, link, config.RSS_IMAGE,
            config.FEHOME, pubDate))

    for ebuild in ebuilds:
        if simple:
            description = escape(ebuild['description'])
        else:
            description = ('\n'
            '<![CDATA[\n'
            '<link rel="stylesheet" type="text/css" href="%s"></link>\n'
        '%s\n]]>' % (config.STYLESHEET, ebuild_to_html(ebuild, full=True))
        )

        fp.write("""<item>
            <title>%s/%s %s</title>
            <link>%sebuilds/?%s-%s</link>
            <description>
                %s
            </description>
            <pubDate>%s</pubDate>
        </item>
        """ % (ebuild['category'],
                ebuild['name'],
                ebuild['version'],
                config.FEHOME,
                ebuild['name'],
                ebuild['version'],
                description,
                ebuild['time'].strftime("%a, %d %b %Y %H:%M:%S +0000"))
        )

    fp.write("\n\
        <textInput>\n\
            <title>Search</title>\n\
            <link>%s/search/</link>\n\
            <description>Search the Online Package Database</description>\n\
            <name>sstring</name>\n\
        </textInput>\n\
        </channel>\n\
        </rss>\n" % config.FEHOME)

def main(argv=None):
    if argv is None:
        argv = sys.argv
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
                ebuild_html = ebuild_to_html(ebuild, new, show_bugs = False)
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
            rss = open(
                os.path.join(
                    config.LOCALHOME,
                    "archs",
                    arch,
                    branch,
                    config.RSS
                ),
                'w'
            )
            ebuilds_to_rss(
                rss,
                ebuilds,
                simple=False,
                arch=arch,
                branch=branch
            )
            rss.close()

            rss2 = open(
                os.path.join(
                    config.LOCALHOME,
                    "archs",
                    arch,
                    branch,
                    config.RSS2
                ),
                'w'
            )
            ebuilds_to_rss(
                rss2,
                ebuilds,
                simple=True,
                arch=arch,
                branch=branch
            )
            rss.close()

if __name__ == '__main__':
    sys.exit(main())
