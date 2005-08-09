/*
 * C Implementation: install_conf
 *
 * Description: 
 * C Code for handling the configuration files for each gcc install
 *
 * Author: Jeremy Huddleston <eradicator@gentoo.org>
 *
 * Copyright 1999-2005 Gentoo Foundation
 * Distributed under the terms of the GNU General Public License v2
 * See COPYING file that comes with this distribution
 *
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/Attic/install_conf.c,v 1.1 2005/08/09 10:42:31 eradicator Exp $
 * $Log: install_conf.c,v $
 * Revision 1.1  2005/08/09 10:42:31  eradicator
 * Added framework for handling configuration files.
 *
 */

#include "install_conf.h"
#include <stdlib.h>

/** Allocate memory and load the configuration file */
InstallConf *loadInstallConf(const char *configFileName) {
	return (InstallConf *)0;
}

/** Save the configuration file */
void saveInstallConf(InstallConf *config) {
	return;
}

/** Free selectionConf and its contents */
void freeInstallConf(InstallConf *installConf) {
	if(!installConf)
		return;

	free(installConf);
}
