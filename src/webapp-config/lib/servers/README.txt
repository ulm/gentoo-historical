README.txt for /usr/lib/webapp-config/supported-servers
=======================================================

Directory Contents
------------------

This directory contains a collection of UNIX shell scripts, as part of
the webapp-config application.  Assume that the scripts must run under
bash-2.05 or later.

Scripts in this directory follow this naming convention:

	<http server name>-<install scheme>.sh

e.g.
	apache-basic.sh

This allows us to support more than one way of installing web-based
applications for each type of web server.

Script Role
-----------

Each script is responsible for providing server-specific code for installing,
upgrading, or removing a web-based application from the local computer.

This is done by providing six functions:

	fn_ws_clean()
	fn_ws_clean_verify()
	- for removing a web application from the local computer

	fn_ws_install()
	fn_ws_install_verify()
	- for installing a web application on the local computer

	fn_ws_upgrade()
	fn_ws_upgrade_verify()
	- for upgrading a web application on the local computer
 
The script will be source'd into the main webapp-config script, and then
the necessary function(s) called.

Only one of fn_ws_clean(), fn_ws_install(), or fn_ws_upgrade() will be called.
The matching fn_ws_*_verify() function *will* be called first.

Variables Available To The Functions
------------------------------------

tbd

Other Notes
-----------

tbd
