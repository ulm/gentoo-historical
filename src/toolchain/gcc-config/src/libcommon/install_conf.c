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
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/install_conf.c,v 1.2 2005/08/12 00:48:18 eradicator Exp $
 * $Log: install_conf.c,v $
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

#include "install_conf.h"
#include <stdlib.h>

/** Allocate memory and load the configuration file */
InstallConf *loadInstallConf(const char *configFileName) {
	InstallConf *retval;
	Profile *profile;
	
#ifdef USE_HARDCODED_CONF
	/* Not production code... */
	retval = (InstallConf *)malloc(sizeof(InstallConf));
	retval->name = "x86_64-pc-linux-gnu-3.4.4";
	retval->binpath = "/usr/x86_64-pc-linux-gnu/gcc-bin/3.4.4";
	retval->infopath = "/usr/share/gcc-data/x86_64-pc-linux-gnu/3.4.4/info";
	retval->manpath = "/usr/share/gcc-data/x86_64-pc-linux-gnu/3.4.4/man";
	retval->profileHash = hashNew(10);

	profile = (Profile *)malloc(sizeof(Profile));
	profile->name = "amd64-vanilla";
	profile->chost = "x86_64-pc-linux-gnu";
	profile->specs = "/usr/lib/gcc/x86_64-pc-linux-gnu/3.4.4/vanilla.specs";
	profile->libdir = "/usr/lib/gcc/x86_64-pc-linux-gnu/3.4.4";
	profile->cflags = (char *)0;
	hashInsert(retval->profileHash, profile->name, (void *)profile);

	profile = (Profile *)malloc(sizeof(Profile));
	profile->name = "amd64-hardened";
	profile->chost = "x86_64-pc-linux-gnu";
	profile->specs = "/usr/lib/gcc/x86_64-pc-linux-gnu/3.4.4/hardened.specs";
	profile->libdir = "/usr/lib/gcc/x86_64-pc-linux-gnu/3.4.4";
	profile->cflags = (char *)0;
	hashInsert(retval->profileHash, profile->name, (void *)profile);

	profile = (Profile *)malloc(sizeof(Profile));
	profile->name = "x86-vanilla";
	profile->chost = "i686-pc-linux-gnu";
	profile->specs = "/usr/lib/gcc/x86_64-pc-linux-gnu/3.4.4/vanilla.specs";
	profile->libdir = "/usr/lib/gcc/x86_64-pc-linux-gnu/3.4.4/32";
	profile->cflags = "-m32";
	hashInsert(retval->profileHash, profile->name, (void *)profile);

	profile = (Profile *)malloc(sizeof(Profile));
	profile->name = "x86-vanilla";
	profile->chost = "i686-pc-linux-gnu";
	profile->specs = "/usr/lib/gcc/x86_64-pc-linux-gnu/3.4.4/vanilla.specs";
	profile->libdir = "/usr/lib/gcc/x86_64-pc-linux-gnu/3.4.4/32";
	profile->cflags = "-m32";
	hashInsert(retval->profileHash, profile->name, (void *)profile);
#else
	/* TODO: Read in config file */
#endif

	return retval;
}

/** Free installConf and its contents */
void freeInstallConf(InstallConf *installConf) {
	/* TODO: Worry about this once/if we need it. */
	if(!installConf)
		return;

	free(installConf);
}
