"""config.py  general system configuration parameters
Every fe module should probably import config"""

__version__ = '20031020.1'
PORTAGE_DIR = '/usr/portage'
WEBBASE="/"
FEHOME="http://packages.gentoo.org/"
ICONS="%simages" % FEHOME
ARCHLIST=open('/usr/portage/profiles/arch.list','r').read().split()
MAXPERPAGE=20
MAX_RECENT_RELEASES=20
MAX_CATEGORIES=30
LOCALHOME="/var/www/packages.gentoo.org/htdocs"
EBUILD_FILES="%s/ebuilds" % LOCALHOME
INDEX="main.shtml"
RSS = 'gentoo.rss'
RSS2 = 'gentoo_simple.rss'
RSS_WEBMASTER = 'www@gentoo.org'
RSS_EDITOR = 'marduk@gentoo.org'

HOST = 'localhost'
DATABASE = 'fresh_ebuilds'
USER = ''
PASSWD = ''
