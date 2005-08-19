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
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/install_conf.c,v 1.7 2005/08/19 06:08:55 eradicator Exp $
 * $Log: install_conf.c,v $
 * Revision 1.7  2005/08/19 06:08:55  eradicator
 * Added headers to EXTRA_DIST.
 *
 * Revision 1.6  2005/08/19 03:35:29  eradicator
 * Cleaned up #include lines and added #include config.h.
 *
 * Revision 1.5  2005/08/18 23:30:24  eradicator
 * Coding style changes to make consistent with the rest of the codebase.  Whitespace cleanup.  Made some functions static.
 *
 * Revision 1.4  2005/08/16 17:34:57  sekretarz
 * Adding new config framework
 *
 * Revision 1.3  2005/08/12 23:10:24  eradicator
 * Added wrapperAliases.  Set missing installConf in hardcoded test configuration.
 *
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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <stdlib.h>

#include "install_conf.h"
#include "parse_conf.h"

#ifndef USE_HARDCODED_CONF
static int installConfSectionCB(const char *section, void *data)
{
	return 0;
}

static int installConfKeyCB(const char *key, const char *value, void *data)
{
	return 0;
}
#endif

/** Allocate memory and load the configuration file */
InstallConf *loadInstallConf(const char *configFileName) {
	InstallConf *retval =  (InstallConf *)malloc(sizeof(InstallConf));

#ifdef USE_HARDCODED_CONF
	Profile *profile;

	/* Not production code... */
	retval->name = "x86_64-pc-linux-gnu-3.4.4";
	retval->binpath = "/usr/x86_64-pc-linux-gnu/gcc-bin/3.4.4";
	retval->infopath = "/usr/share/gcc-data/x86_64-pc-linux-gnu/3.4.4/info";
	retval->manpath = "/usr/share/gcc-data/x86_64-pc-linux-gnu/3.4.4/man";
	retval->profileHash = hashNew(10);
	retval->wrapperAliases = hashNew(10);
	hashInsert(retval->wrapperAliases, "cc", "gcc");
	hashInsert(retval->wrapperAliases, "gfortran", "g77");
	hashInsert(retval->wrapperAliases, "f77", "g77");

	profile = (Profile *)malloc(sizeof(Profile));
	profile->installConf = retval;
	profile->name = "amd64-vanilla";
	profile->chost = "x86_64-pc-linux-gnu";
	profile->specs = "/usr/lib/gcc/x86_64-pc-linux-gnu/3.4.4/vanilla.specs";
	profile->libdir = "/usr/lib/gcc/x86_64-pc-linux-gnu/3.4.4";
	profile->cflags = (char *)0;
	hashInsert(retval->profileHash, profile->name, (void *)profile);

	profile = (Profile *)malloc(sizeof(Profile));
	profile->installConf = retval;
	profile->name = "amd64-hardened";
	profile->chost = "x86_64-pc-linux-gnu";
	profile->specs = "/usr/lib/gcc/x86_64-pc-linux-gnu/3.4.4/hardened.specs";
	profile->libdir = "/usr/lib/gcc/x86_64-pc-linux-gnu/3.4.4";
	profile->cflags = (char *)0;
	hashInsert(retval->profileHash, profile->name, (void *)profile);

	profile = (Profile *)malloc(sizeof(Profile));
	profile->installConf = retval;
	profile->name = "x86-vanilla";
	profile->chost = "i686-pc-linux-gnu";
	profile->specs = "/usr/lib/gcc/x86_64-pc-linux-gnu/3.4.4/vanilla.specs";
	profile->libdir = "/usr/lib/gcc/x86_64-pc-linux-gnu/3.4.4/32";
	profile->cflags = "-m32";
	hashInsert(retval->profileHash, profile->name, (void *)profile);

	profile = (Profile *)malloc(sizeof(Profile));
	profile->installConf = retval;
	profile->name = "x86-vanilla";
	profile->chost = "i686-pc-linux-gnu";
	profile->specs = "/usr/lib/gcc/x86_64-pc-linux-gnu/3.4.4/vanilla.specs";
	profile->libdir = "/usr/lib/gcc/x86_64-pc-linux-gnu/3.4.4/32";
	profile->cflags = "-m32";
	hashInsert(retval->profileHash, profile->name, (void *)profile);
#else
	ConfigParser *config = parserNew(configFileName);
	parserSetData(config, retval);
	parserSetCallback(config, installConfSectionCB, installConfKeyCB);

	parseFile(config);
	
	parserFre(config);
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
