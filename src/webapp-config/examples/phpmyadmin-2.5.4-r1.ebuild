# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/webapp-config/examples/Attic/phpmyadmin-2.5.4-r1.ebuild,v 1.1 2004/03/02 23:53:38 stuart Exp $

inherit eutils
inherit webapp

MY_P=phpMyAdmin-${PV/_p/-pl}
DESCRIPTION="Web-based administration for MySQL database in PHP"
HOMEPAGE="http://phpmyadmin.sourceforge.net/"
SRC_URI="mirror://sourceforge/${PN}/${MY_P}-php.tar.bz2"
RESTRICT="nomirror"
LICENSE="GPL-2"
SLOT="0"
KEYWORDS="alpha arm ppc hppa mips sparc x86 amd64"
DEPEND=">=net-www/apache-1.3
	>=dev-db/mysql-3.21 <dev-db/mysql-5.0
	>=dev-php/mod_php-3.0.8
	sys-apps/findutils"
S=${WORKDIR}/${MY_P}

src_unpack() {
	unpack ${A}
	epatch ${FILESDIR}/config.inc.php-${PV}.patch

	# Remove .cvs* files and CVS directories
	find ${S} -name .cvs\* -or \( -type d -name CVS -prune \) | xargs rm -rf
}

src_compile() {
	# This whole idea needs reviewing.  For some reason, we're not using
	# the default database name, nor the default table names.  There's
	# no comments in the source code to explain why this is the case :(
	#
	# I need to understand whether this really does provide an added level
	# of security or whether it's just an inconvenience
	#
	# I also need to understand how it affects vhost support
	#
	# - Stu

	einfo "Setting random user/password details for the controluser"

	local pmapass="${RANDOM}${RANDOM}${RANDOM}${RANDOM}"
	mv config.inc.php ${T}/config.inc.php
	sed -e "s/@pmapass@/${pmapass}/g" \
		${T}/config.inc.php > config.inc.php
	sed -e "s/@pmapass@/${pmapass}/g" \
		${FILESDIR}/mysql-setup.sql.in-${PV} > ${T}/mysql-setup.sql
}

src_install() {
	local docs="ANNOUNCE.txt CREDITS Documentation.txt RELEASE-DATE-${PV} TODO ChangeLog LICENSE README"

	# install the SQL scripts available to us
	#
	# unfortunately, we do not have scripts to upgrade from older versions
	# these are things we need to add at a later date

	webapp_sqlscript mysql ${T}/mysql-setup.sql

	# handle documentation files
	#
	# NOTE that doc files go into /usr/share/doc as normal; they do NOT
	# get installed per vhost!

	dodoc ${docs}
	for doc in ${docs} INSTALL; do
		rm -f ${doc}
	done

	# Copy the app's main files
	
	einfo "Installing main files"
	cp -r . ${MY_HTDOCSDIR}

	# Identify the configuration files that this app uses

	webapp_configfile ${MY_HTDOCSDIR}/config.inc.php

	# Identify any script files that need #! headers adding to run under
	# a CGI script (such as PHP/CGI)
	#
	# for phpmyadmin, we *assume* that all .php files that don't end in
	# .inc.php need to have CGI/BIN support added

	for x in `find . -name '*.php' -print | grep -v 'inc.php'` ; do
		webapp_runbycgibin php ${MY_HTDOCSDIR}/$x
	done

	# there are no files which need to be owned by the web server

	# all done
	#
	# now we let the eclass strut its stuff ;-)

	webapp_src_install
}

pkg_postinst() {
	einfo
	einfo "To complete installation, you must"
	einfo "1. Update your configuration files:"
	einfo "     etc-update"
	einfo "2. Update MySQL's grant tables and the pmadb database:"
	einfo "     ebuild /var/db/pkg/${CATEGORY}/${PF}/${PF}.ebuild config"
	einfo "3. Reload MySQL:"
	einfo "     /etc/init.d/mysql restart"
	einfo
	einfo "If you are upgrading from an earlier version and are using phpMyAdmin's"
	einfo "features for master/foreign tables be sure to read"
	einfo "  http://localhost/phpmyadmin/Documentation.html#col_com"
	einfo "You will need to perform the ALTER TABLE step yourself."
	einfo
	einfo "Finally, point your browser to http://localhost/phpmyadmin/."
	einfo
}

pkg_config() {
	einfo "This will execute the contents of ${ROOT}etc/phpmyadmin/mysql-setup.sql"
	einfo "Type in your MySQL root password:"
	mysql -u root -p < ${ROOT}etc/phpmyadmin/mysql-setup.sql || die
	einfo "You need to reload MySQL for the changes to take effect"
}
