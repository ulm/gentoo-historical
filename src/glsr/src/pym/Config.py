# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Config.py,v 1.1.1.1 2004/06/04 06:38:36 port001 Exp $
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
        "admin_languages":	t_prefix + "admin/Languages.tpl"
	}

URL = "http://localhost/glsr/"
Contact = "port001@gentoo.org"

Memcache = "No" # Not supported yet

Logging = "Yes" # Yes/No
Logtype = "All" # All/Error
LogFile = "/var/www/localhost/htdocs/glsr/glsr.log"
Debug = "Yes" # Yes/No

CookieDomain = "glsr.gentoo.org"
CookiePath = "/"
CookieSecure = "No"

SessionTimeOut = 259200 # Time in seconds (1 day = 86400)

WhoIsOnlineOffset = 300
