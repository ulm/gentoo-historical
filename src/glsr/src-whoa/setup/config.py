# Copyright 2004 Ian Leitch
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = '$Id: config.py,v 1.1 2005/03/27 04:02:34 hadfield Exp $'
__version__ = "0.3"
__modulename__ = "config"

db = {
    "db_type":  "mysql",
    "host":     "localhost",
    "port":     "",
    "user":     "glsrusr",
    "passwd":   "glsrusr",
    "db":       "glsr",
    "prefix":   "glsr_"
    }

theme = "gentoo"
contact = "port001@gentoo.org"

root = "/var/www/localhost/htdocs/glsr/"
url = "http://scriptstest.gentoo.org/"

# FIXME: The next three settings should be set in the web UI.
who_is_online_offset = 300

# Should all scripts being submitted require approval by an admin?
require_approval = False

# The number of error messages to display in the admin area.
error_report_list_length = 5


template_loc = root + "template/" + theme + "/templates/"
template_cache = root + "template/tmpl_cache/" 

debug = True

logging = True
error_reporting = True
logging_loc = root + "log/glsr/"
logfile = "glsr.log"
error_logfile = "error_reports.log"

cookie_domain = "scriptstest.gentoo.org"
cookie_path = "/"
cookie_secure = False
cookie_secret = "T0mm3yT4n5"

session_timeout = 259200 # Time in seconds (1 day = 86400)

# Time in seconds we should wait for each thread
threads_timeout = 3
