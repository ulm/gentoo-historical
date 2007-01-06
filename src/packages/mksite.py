#!/bin/env python

# Create the site (as if) from scratch according to config.py

import os
import sys

import config
from genarchbar import genarchbar

archList = config.ARCHLIST[:]
archList.sort()

def mkdir(path):
    """Create directory path if it doesn't already exist"""

    if not os.path.exists(path):
        return os.makedirs(path)

def symlink(src, dst):
    """Create symlink if overwriting dst if it exists"""

    if os.path.exists(dst) or os.path.islink(dst):
        os.unlink(dst)
    return os.symlink(src, dst)

def head():
    """return head.html file as string"""
    s = '<meta content="text/html; charset=utf-8" http-equiv="Content-Type">\n'
    s+= '<link rel="stylesheet" type="text/css" href="%s">\n' % \
            config.STYLESHEET
    if hasattr(config, 'FAVICON'):
        s+= '<link type="image/x-icon" href="%s" rel="shortcut icon">\n' \
                % config.FAVICON
    s+= ('<link rel="alternate" type="application/rss+xml" title="Portage '
        'Updates" href="/gentoo.rss">\n')
    s+= ('<link rel="alternate" type="application/rss-xml" '
        'title="Most Recently Introduced Packages" href="/feeds/new.rss">\n')

    for arch in archList:
        s+= (
            '<link rel="alternate" type="application/rss+xml" title="Portage '
            'Updates for %s" href="/archs/%s/gentoo.rss">\n'
            % (arch, arch)
            )
        s+= (
            '<link rel="alternate" type="application/rss+xml" title="Portage '
            'Updates for %s (stable)" href="/archs/%s/stable/gentoo.rss">\n'
            % (arch, arch)
            )
        s+= (
            '<link rel="alternate" type="application/rss+xml" title="Portage '
            'Updates for %s (testing)" href="/archs/%s/testing/gentoo.rss">\n'
            % (arch, arch)
            )
    s+= '<title>Gentoo Online Package Database</title>\n</head>\n'
    return s

def do_arch():
    """/arch directories"""

    # create arch dirs
    arch_dir = config.LOCALHOME + '/archs'
    for arch in ['.'] + archList:
        either = arch_dir + '/' + arch
        stable = either + '/stable'
        testing = either + '/testing'

        mkdir(either)
        mkdir(stable)
        mkdir(testing)


        # archnav.html
        archbar = genarchbar(config.FEHOME, arch, '')
        open(either + '/archnav.html', 'w').write(archbar)
        archbar = genarchbar(config.FEHOME, arch, 'stable')
        open(stable + '/archnav.html', 'w').write(archbar)
        archbar = genarchbar(config.FEHOME, arch, 'testing')
        open(testing + '/archnav.html', 'w').write(archbar)

    # main /arch dir
    index = open(config.FELIB + '/index.shtml', 'r').read()
    archbar = genarchbar(config.FEHOME, '', '')
    open(arch_dir + '/archnav.html', 'w').write(archbar)
    open(arch_dir + '/index.shtml', 'w').write(index)


def main():
    """Main program entry point."""

    # create main directories
    mkdir(config.LOCALHOME)
    mkdir(config.LOCALHOME + '/archs')
    mkdir(config.LOCALHOME + '/bumps')
    mkdir(config.LOCALHOME + '/categories')
    mkdir(config.LOCALHOME + '/daily')
    mkdir(config.LOCALHOME + '/ebuilds')
    mkdir(config.LOCALHOME + '/feeds')
    #mkdir(config.LOCALHOME + '/images')
    mkdir(config.LOCALHOME + '/new')
    mkdir(config.LOCALHOME + '/packages')
    mkdir(config.LOCALHOME + '/search')
    mkdir(config.LOCALHOME + '/similar')

    # set up .htaccess
    htaccess = open(config.LOCALHOME + '/.htaccess', 'w')
    htaccess.write('Options +FollowSymlinks +ExecCGI +Includes\n'
            'AddCharset UTF-8 .html .shtml .rss\n'
            'AddType text/html .shtml\n'
            'AddHandler server-parsed .shtml\n'
            )
    htaccess.close()

    # index.shtml
    index = open(config.FELIB + '/index.shtml', 'r').read()
    open(config.LOCALHOME + '/index.shtml', 'w').write(index)
    
    # menu.html
    open(config.LOCALHOME + '/menu.html', 'w')\
            .write(open(config.FELIB + '/menu.html', 'r').read())
    
    do_arch()

    # /bumps
    open(config.LOCALHOME + '/bumps/index.shtml', 'w').write(index)

    # /categories
    open(config.LOCALHOME + '/categories/index.shtml', 'w').write(index)

    # /daily
    open(config.LOCALHOME + '/daily/.htaccess', 'w').write(
        'Options +ExecCGI\n'
        'ErrorDocument 404 /daily/\n'
    )
    open(config.LOCALHOME + '/daily/index.shtml', 'w').write(
        index.replace(
            '<!--#include virtual="main.shtml"-->',
            '<!--#exec cgi="daily.py" -->' 
        )
    )
    symlink(config.FELIB + '/daily.py', config.LOCALHOME + '/daily/daily.py')

    # /ebuilds
    symlink(config.FELIB + '/query_ebuild.py', 
            config.LOCALHOME + '/ebuilds/query_ebuild.py')
    open(config.LOCALHOME + '/ebuilds/index.shtml', 'w').write(
            index.replace(
                '<!--#include virtual="main.shtml"-->',
                '<!--#exec cmd="./query_ebuild.py $QUERY_STRING" -->')
            )

    # /feeds
    open(config.LOCALHOME + '/feeds/index.shtml', 'w').write(index)
    # This is a hack, but right now I'm too lazy to re-rewrite
    # genrsslist.py
    tmp = sys.stdout
    sys.stdout = open(config.LOCALHOME + '/feeds/main.shtml', 'w')
    import genrsslist
    sys.stdout = tmp

    # /new
    open(config.LOCALHOME + '/new/index.shtml', 'w').write(
            index.replace('<!--#include virtual="main.shtml"-->',
                '<h3 class="category">Most Recently Introduced '
                'Packages</h3>\n'
                '<!--#include virtual="main.shtml"-->'
                )
            )

    # /packages
    open(config.LOCALHOME + '/packages/index.shtml', 'w').write(
            index.replace('<!--#include virtual="main.shtml"-->',
                '<!--#exec cgi="query_package.py" -->'
                )
            )
    symlink(
            config.FELIB + '/query_package.py', 
            config.LOCALHOME + '/packages/query_package.py'
    )

    # /search
    open(config.LOCALHOME + '/search/index.shtml', 'w').write(
            index.replace('<!--#include virtual="main.shtml"-->',
                '<!--#exec cmd="./search.py $QUERY_STRING" -->'
                )
            )

    symlink(
            config.FELIB + '/search.py',
            config.LOCALHOME + '/search/search.py'
    )

    # /similar
    open(config.LOCALHOME + '/similar/index.shtml', 'w').write(
            index.replace('<!--#include virtual="main.shtml"-->',
                '<!--#exec cmd="./similar.py $QUERY_STRING" -->'
                )
            )

    symlink(
            config.FELIB + '/similar.py',
            config.LOCALHOME + '/similar/similar.py'
    )



    # main root (/)
    open(config.LOCALHOME + '/head.html', 'w').write(head())
    symlink('archs/archnav.html', config.LOCALHOME + '/archnav.html')
    symlink('archs/index.shtml', config.LOCALHOME + '/index.shtml')
    symlink('archs/head.shtml', config.LOCALHOME + '/head.shtml')
    symlink('archs/gentoo.rss', config.LOCALHOME + '/gentoo.rss')
    symlink('archs/gentoo_simple.rss', config.LOCALHOME +
        '/gentoo_simple.rss')
    symlink('archs/main.shtml', config.LOCALHOME + '/main.shtml')

if __name__ == '__main__':
    main()
