/*
 * C Header: install_conf
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
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/install_conf.h,v 1.2 2005/08/12 00:48:18 eradicator Exp $
 * $Log: install_conf.h,v $
 * Revision 1.2  2005/08/12 00:48:18  eradicator
 * Added hardcoded configuration, so I can work on the wrapper while putting off the config file handling.
 *
 * Revision 1.1  2005/08/09 20:15:46  eradicator
 * Moving components into subdirs to make build environment more tidy.
 *
 * Revision 1.1  2005/08/09 10:42:31  eradicator
 * Added framework for handling configuration files.
 *
 */

#ifndef _GCC_CONFIG_INSTALL_CONF_H_
#define _GCC_CONFIG_INSTALL_CONF_H_

#include "hash.h"

typedef struct {
	/* This is the same as the filename for the configuration without the trailing .conf */
	char *name;

	/* Information shared by all profiles */
	char *binpath;
	char *infopath;
	char *manpath;

	/* Hash table of profiles provided by this install
	* Key: (char *) name (such as "x86-vanilla")
	* Value: (Profile *) Profile associated with this profile name
	*/
	Hash *profileHash;
} InstallConf;

typedef struct {
	InstallConf *installConf;

	char *name;
	char *chost;
	char *specs;
	char *libdir;
	char *cflags;
} Profile;

/** Allocate memory and load the configuration file */
InstallConf *loadInstallConf(const char *configFileName);

/** Free installConf and its contents */
void freeInstallConf(InstallConf *installConf);

#endif
