#!/usr/bin/python -OO

import config
import os
import time
import sys
import MySQLdb
import ebuilddb
import changelogs
from cgi import escape
from urllib import quote

def is_new(db,ebuild):
    """Check for newness. An ebuild is considered new if it is the
    only ebuild with that category/name in ebuild and it has no prevarch"""
    
    c = db.cursor()
    query = """SELECT prevarch FROM ebuild WHERE category="%s" AND name="%s" """ \
        % (ebuild['category'], ebuild['name'])
    c.execute(query)
    results = c.fetchall()
    if len(results) == 1 and results[0][0] is None:
        return 1
    return 0

def changelog_to_html(s):
    n = ""
    for c in s:
        if c == '\n':
            n = "%s<br>" % n
        else:
            n = "%s%s" % (n,escape(c))
    n = changelogs.bugs_to_html(n)
    return n

def homepage_to_html(s):
    if not s.strip(): return "?"
    t = s.replace('|',' ')
    if ' ' in t:
        pieces = t.split()
        return ' '.join([ homepage_to_html(piece) for piece in pieces ])
    return ("""<a href="%s"><img border="0" src="%s/home.png" width="24" height="20" alt="Home Page" title="Home Page"></a>""" % (s, config.ICONS))

def license_to_html(s):
    if not s.strip(): return "?"
    t = s.replace('|',' ')
    if ' ' in t:
        pieces = t.split()
        return "<br>".join([ license_to_html(piece) for piece in pieces ])
    return """<a href="http://www.gentoo.org/cgi-bin/viewcvs.cgi/*checkout*/licenses/%s">%s</a>""" % (s,s)

def package_to_html(pkginfo,db):
    """This function needs a database (db) connection because it performs a query_to_dict
    on the package"""
    #colspan = len(config.ARCHLIST) + 1
    s = """<table class="ebuild">
        <tr><td class="fields" colspan="4">%s</td></tr>
        <tr><td class="item" colspan="4"><p><img align="right" alt="" src="%s/%s.png">
        <b>Description: </b>%s</p>
    """  % (pkginfo['name'],config.ICONS,pkginfo['category'],escape(pkginfo['description']))
    ebuilds = get_recent_releases(pkginfo,db)
    if ebuilds:
        s = """%s<p><b>Releases:</b></p>
        <table class="releases"><tr><td>&nbsp;</td>""" % s
        for i in config.ARCHLIST:
            s = """%s<th class="arch">%s</th>""" % (s,i)
        s = "%s</tr>\n" % s
        for ebuild in ebuilds:
            archs = ebuild['arch'].split()
            s = """%s<tr><th class="releases"><a href="%sebuilds/?%s-%s" title="%s">%s</a></th>
            """ % (s,config.FEHOME,ebuild['name'],ebuild['version'],ebuild['time'],ebuild['version'])
            for arch in config.ARCHLIST:
                if arch in config.ARCHLIST:
                    if arch in archs:
                        arch_string = '+'
                        title = 'marked stable for %s' % arch
                    elif '~%s' % arch in archs:
                        arch_string = '~'
                        title = 'undergoing testing for %s' % arch
                    else:
                        arch_string = '-'
                        title = 'not available for %s' % arch
                s = """%s<td class="archcell" arch="%s" title="%s">%s</td>
                """ % (s,arch_string,title,arch_string)
            s = "%s</tr>" % s
        s = "%s</table>\n" % s
    
    s = "%s\n%s</table>" % (s,general_info_to_html(pkginfo))
    return s    

def archs_to_html(archs):
    arch_string= '|'
    for arch in config.ARCHLIST:
        if arch in archs:
            arch_icon = 'check.gif'
            alt = ": yes"
            title = 'marked stable for %s' % arch
        elif '~%s' % arch in archs:
            arch_icon = 'bug.gif'
            alt = ': testing'
            title = 'undergoing testing for %s' % arch
        else:
            arch_icon = 'no.gif'
            alt = ': no'
            title = 'not available for %s' % arch
            
        arch_string = (' %s %s <img src="%simages/archs/%s" '
            'alt="%s" title="%s"> |' % (
            arch_string,
            arch,
            config.FEHOME, 
            arch_icon,
            alt,
            title))
            
    return arch_string
                
def ebuild_to_html(ebinfo,new=0):
    try:
        archs = ebinfo['arch'].split()
    except KeyError:
        archs = ()
    arch_string = archs_to_html(archs)
    changelogurl = ('http://www.gentoo.org/cgi-bin/viewcvs.cgi/*checkout*/'
        '%s/%s/ChangeLog' % (ebinfo['category'],ebinfo['name']))

    if new:
        new_string = """ &nbsp;&nbsp;<span class="new">new!</span> """
    else:
        new_string = ""
        
    return ('<table class="ebuild">\n'
        '<tr><td colspan="4" class="fields">'
        '<a href="%spackages/?category=%s;name=%s">%s</a> %s%s<br>'
        '<span class="time">%s</span><br>\n'
        '</td></tr>\n'
        '<tr><td class="item" align="center" colspan="1">'
        '<img alt="" src="%simages/%s.png">' 
        '<td class="item" valign="top" colspan="3">'
        '<p><b>Description:</b> %s</p>\n'
        '<p><b>Changes:</b><br>\n'
        '%s</p></td></tr>\n'
        '<tr><td colspan="4" class="item"><p class="archs">%s</p>\n'
        '</td></tr>\n'
        '%s</table>\n'
        '<br>\n' % (config.FEHOME,
            quote(ebinfo['category']),
            quote(ebinfo['name']),
            ebinfo['name'],
            ebinfo['version'],
            new_string,
            ebinfo['time'].localtime().strftime("%c %Z"),
            config.FEHOME,
            ebinfo['category'],
            escape(ebinfo['description']),
            changelog_to_html(ebinfo['changelog']),
            arch_string,
            general_info_to_html(ebinfo)))

def general_info_to_html(pkg):
    """This actually will (should) take either a package or ebuild dict
    as an argument"""
    
    changelogurl = ('http://www.gentoo.org/cgi-bin/viewcvs.cgi/*checkout*/'
        '%s/%s/ChangeLog' % (pkg['category'],pkg['name']))
    return ('<tr><th class="category">Category</th>'
        '<td class="homepage" rowspan="2">%s</td>'
        #'<td class="homepage" rowspan="2"><a href="%s">Home Page</a></td>'
        '<th class="license">License</th>'
        '<td class="changelog" rowspan="2"><a href="%s">ChangeLog</a><td>\n'
        '<tr><td class="category"><a href="%spackages/?category=%s">'
        '%s</a></td>'
        #'<td class="homepage"><a href="%s">Home Page</a></td>'
        '<td class="license">%s</td></tr>\n'
        % ( homepage_to_html(pkg['homepage']),
            changelogurl,
            config.FEHOME,
            pkg['category'],
            pkg['category'],
            #pkg['homepage'],
            license_to_html(pkg['license'])))
        
def get_most_recent(db,max=config.MAXPERPAGE,arch="",branch=""):
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
    einfo = {}
    keys = ('category','name','version','time','description','changelog',
        'arch','homepage','license')
    for i in range(len(keys)):
        try:
            einfo[keys[i]] = d[i]
        except IndexError:
            continue
    return einfo

def get_recent_releases(pkg,db,max=config.MAX_RECENT_RELEASES):
    """Return MAX_RECENT_RELEASES most recent releases for pkg.  Returns and
    ebuild-type dict"""
    c = db.cursor()
    query = """SELECT category,name,version,when_found,NULL,changelog,arch ,NULL,NULL
    FROM ebuild WHERE name="%s" AND 
    category="%s" ORDER BY when_found DESC LIMIT %s
    """ % (pkg['name'],pkg['category'],max)
    c.execute(query)
    results = c.fetchall()
    #print results
    return [ query_to_dict(i) for i in results ]
    
def ebuilds_to_rss(fp,ebuilds,simple=False,subtitle=""):
    """write out ebuild info to RSS file (fp)"""
    fp.write("""<?xml version="1.0" encoding="utf-8"?>
        <rss version="0.92">
        <channel>
        <title>Fresh ebuilds %s</title>
        <link>%s</link>
        <description>Latest ebuilds from the Gentoo Linux portage tree</description>
        <webMaster>www@gentoo.org</webMaster>
        <managingEditor>marduk@gentoo.org</managingEditor>
        <pubDate>%s</pubDate>""" % (subtitle,config.FEHOME,
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
    
if __name__ == '__main__':
    try:
        if sys.argv[1] == '-g':
            ebuilddb.main()
    except IndexError:
            pass

    db = ebuilddb.db_connect()
    branches = ('','stable','testing')
    for arch in [''] + config.ARCHLIST:
        for branch in branches:
            fullpath = os.path.join(config.LOCALHOME,"archs",arch,branch,config.INDEX)
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
            index.write('<!--#include file="archnav.html" -->\n\n</td></tr>\n<tr><td>') 
            results = get_most_recent(db,arch=arch,branch=branch)
            ebuilds = [ query_to_dict(i) for i in results ]
            for ebuild in ebuilds:
                new = is_new(db,ebuild)
                pkgfilename = "%s/%s-%s.html" % (
                    config.EBUILD_FILES,ebuild['name'],ebuild['version'])
                ebuild_html = ebuild_to_html(ebuild,new)
                if arch == '' and branch == '':  # and not os.path.exists(pkgfilename):
                    pkgfile = open(pkgfilename,'w')
                    pkgfile.write(ebuild_html)
                    pkgfile.close()
                    ebuildfilename = "%s/%s/%s/%s-%s.ebuild" % (ebuilddb.config.PORTAGE_DIR,
                        ebuild['category'],ebuild['name'],ebuild['name'],
                        ebuild['version'])
                    os.system('touch -r %s %s || touch -d "today -1 year" %s' % (ebuildfilename,pkgfilename,pkgfilename))
        
                try:
                    index.write('%s<br>\n\n\n' % (ebuild_html))
                except IOError:
                    pass
                #index.write('<!--#include virtual="%s/ebuilds/%s-%s.html" --><br>\n\n\n' 
                #   % (config.WEBBASE,ebuild['name'],ebuild['version']))
                #index.write("""<hr class="seperator">\n""")
                
            index.write("""</table>\n""")
            index.close()
            
            subtitle = ' %s %s' % (arch,branch)
            rss = open(os.path.join(config.LOCALHOME,"archs",arch,branch,config.RSS),'w')
            ebuilds_to_rss(rss,ebuilds,simple=False,subtitle=subtitle)
            rss.close()
        
            rss2 = open(os.path.join(config.LOCALHOME,"archs",arch,branch,config.RSS2),'w')
            ebuilds_to_rss(rss2,ebuilds,simple=True,subtitle=subtitle)
            rss.close()
