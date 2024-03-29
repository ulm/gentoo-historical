# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Config.py,v 1.23 2005/03/24 07:05:17 hadfield Exp $
#

__modulename__ = "Config"

Version = "0.3"

MySQL = {
    "host":		"localhost",
    "user":             "glsrusr",
    "passwd":           "glsrusr",
    "db":               "glsr",
    "prefix":           "glsr_",
    "user_table":       "user",
    "category_table":   "category",
    "language_table":   "language",
    "comment_table":    "comment",
    "script_table":     "script",
    "subscript_table":  "subscript",
    "session_table":    "session",
    "news_table":       "news",
    "state_table":	"state"
    }

t_prefix = "/var/www/scripts.gentoo.org/gentoo/src/glsr/src/templates/"
#t_prefix = "/usr/local/share/glsr/templates/"
#t_prefix = "/var/www/localhost/htdocs/glsr/templates/"

Template = {
    "error_user":               t_prefix + "Error_User.tpl",
    "header":                   t_prefix + "Header.tpl",
    "footer":                   t_prefix + "Footer.tpl",
    "main":                     t_prefix + "Main.tpl",
    "script_search":            t_prefix + "Script_Search.tpl",
    "script":                   t_prefix + "Script.tpl",
    "create_script":            t_prefix + "Create_Script.tpl",
    "view_script":              t_prefix + "View_Script.tpl",
    "view_scripts":             t_prefix + "View_Scripts.tpl",
    "login":			t_prefix + "Login.tpl",
    "memberlist":               t_prefix + "Memberlist.tpl",
    "registration":             t_prefix + "Registration.tpl",
    "admin_header":             t_prefix + "admin/Header.tpl",	
    "admin_main":               t_prefix + "admin/Main.tpl",
    "admin_user":               t_prefix + "admin/User.tpl",
    "admin_user_controls":      t_prefix + "admin/User_Controls.tpl",
    "admin_news":               t_prefix + "admin/News.tpl",
    "admin_script":             t_prefix + "admin/Script_Controls.tpl",
    "admin_script_search":      t_prefix + "admin/Script_Search.tpl",
    "admin_script_results":     t_prefix + "admin/Script_Results.tpl",
    "admin_categories":         t_prefix + "admin/Categories.tpl",
    "admin_script_languages":   t_prefix + "admin/Script_Languages.tpl",
    "admin_statistics":         t_prefix + "admin/Statistics.tpl"
    }

URL = "http://scriptstest.gentoo.org/"
#URL = "http://localhost/glsr/htdocs/"
Contact = "port001@gentoo.org"

TmplCacheDir = "/var/www/scripts.gentoo.org/htdocs/tmpl_cache"
#TmplCacheDir = "/var/www/localhost/htdocs/glsr/tmpl_cache"

Logging = True
LogFile = "/var/www/scripts.gentoo.org/htdocs/log/glsr.log"
#LogFile = "/var/www/localhost/htdocs/glsr/log/glsr.log"

Debug = True

ErrorReporting = True
ErrorReportLog = "/var/www/scripts.gentoo.org/htdocs/log/error_reports.log"
#ErrorReportLog = "/var/www/localhost/htdocs/glsr/log/error_reports.log"

# Default report list offset
ErrorReportListOffset = 5

CookieDomain = "scriptstest.gentoo.org"
CookiePath = "/"
CookieSecure = False
CookieSecret = "T0mm3yT4n5"

SessionTimeout = 259200 # Time in seconds (1 day = 86400)

WhoIsOnlineOffset = 300

# Should all scripts being submitted require approval by an admin?
RequireApproval = False

# Time in seconds we should wait for each thread
WaitThreadsTimeout = 3
