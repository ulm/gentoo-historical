# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Config.py,v 1.3 2004/07/05 20:34:44 port001 Exp $
#

__modulename__ = "Config"

Version = "0.1"

MySQL = {
	"host":			"localhost",
	"user":			"glsrusr",
	"passwd":		"glsrusr",
	"db":			"glsr",
        "prefix":		"glsr_",
	"user_table":		"user",
	"category_table":	"category",
	"language_table":	"language",
	"comment_table":	"comment",
	"script_table":		"script",
	"subscript_table":	"subscript",
	"session_table":	"session",
	"news_table":		"news"
	}

t_prefix = "/usr/local/share/glsr/templates/"

Template = {
	"test":			t_prefix + "test.tpl",
	"err":			t_prefix + "err.tpl",
	"msg":			t_prefix + "msg.tpl",
	"header":		t_prefix + "Header.tpl",
	"footer":		t_prefix + "Footer.tpl",
	"admin_header":		t_prefix + "admin/Header.tpl",	
	"admin_main":		t_prefix + "admin/Main.tpl",
	"admin_user":		t_prefix + "admin/User.tpl",
	"admin_user_controls":	t_prefix + "admin/User_Controls.tpl",
	"admin_news":		t_prefix + "admin/News.tpl",
        "admin_script":		t_prefix + "admin/Script_Controls.tpl",
        "admin_script_search":	t_prefix + "admin/Script_Search.tpl",
        "admin_script_results":	t_prefix + "admin/Script_Results.tpl",
        "admin_categories":	t_prefix + "admin/Categories.tpl",
        "admin_script_languages":	t_prefix + "admin/Script_Languages.tpl"
	}

URL = "http://localhost/glsr/"
Contact = "port001@gentoo.org"

Memcache = "No" # Not supported yet

Logging = True
Logtype = "All" # All/Error
LogFile = "/var/www/localhost/htdocs/glsr/log/glsr.log"

Debug = True

ErrorReporting = True
ErrorReportLog = "/var/www/localhost/htdocs/glsr/log/ErrorReports.log"

CookieDomain = "glsr.gentoo.org"
CookiePath = "/"
CookieSecure = "No"

SessionTimeOut = 259200 # Time in seconds (1 day = 86400)

WhoIsOnlineOffset = 300

# Do not edit
HTMLHeadersSent = False
