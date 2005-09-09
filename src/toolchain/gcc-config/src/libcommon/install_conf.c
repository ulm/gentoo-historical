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
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/install_conf.c,v 1.12 2005/09/09 04:23:46 eradicator Exp $
 * $Log: install_conf.c,v $
 * Revision 1.12  2005/09/09 04:23:46  eradicator
 * Readded explicit cast which I accidently removed...
 *
 * Revision 1.11  2005/09/09 04:20:32  eradicator
 * Added check for parseFile's return code.
 *
 * Revision 1.10  2005/09/09 02:35:29  eradicator
 * Added checks to ensure sanity and security.
 *
 * Revision 1.9  2005/08/25 21:08:28  sekretarz
 * Coded callbacks function. Still untested.
 *
 * Revision 1.8  2005/08/20 22:03:48  eradicator
 * Let users override settings in ~/.gcc-config.
 *
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

/* For strndup() */
#define _GNU_SOURCE

#include <stdlib.h>
#include <string.h>

#include "install_conf.h"
#include "parse_conf.h"

#ifndef MAX_STRLEN
#define MAX_STRLEN 1023
#endif

#ifndef USE_HARDCODED_CONF
static int installConfSectionCB(const char *section, void *data) {
	InstallConf *conf = (InstallConf *)data;

	if (strcmp(section, "global") == 0) {
		conf->currentProfile = NULL;
		conf->profileHash = hashNew(10);
		conf->wrapperAliases = hashNew(10);
	} else {
		Profile *tmp = (Profile *)calloc(1, sizeof(Profile));

		if(!tmp)
			return -1;

		tmp->installConf = conf;
		tmp->name = strndup(section, MAX_STRLEN);

		if(!tmp->name) {
			free(tmp);
			return -1;
		}

		conf->currentProfile = tmp;
		hashInsert(conf->profileHash, tmp->name, tmp);
	}
	return 0;
}

static int installConfKeyCB(const char *key, const char *value, void *data) {
	InstallConf *conf = (InstallConf *)data;

	if (!conf->currentProfile) { /* on global section */
		if (strcmp(key, "version") == 0) {
			conf->name = strndup(value, MAX_STRLEN);
			if(!conf->name)
				return -1;
		} else if (strcmp(key, "bindir") == 0) {
			conf->binpath  = strndup(value, MAX_STRLEN);
			if(!conf->binpath)
				return -1;
		} else if (strcmp(key, "infopath") == 0) {
			conf->infopath = strndup(value, MAX_STRLEN);
			if(!conf->infopath)
				return -1;
		} else if (strcmp(key, "manpath") == 0) {
			conf->manpath  = strndup(value, MAX_STRLEN);
			if(!conf->manpath)
				return -1;
			/* check aliases */
		} else if (strncmp(key, "alias", 5) == 0) {
			hashInsert(conf->wrapperAliases, key+5, (void *)value);
		} else {
			/* unknown key... ignore it */
			return 0;
		}
	} else { /* on other sections */
		if (strcmp(key, "chost") == 0) {
			conf->currentProfile->chost = strndup(value, MAX_STRLEN);
			if(!conf->currentProfile->chost)
				return -1;
		} else if (strcmp(key, "specs") == 0) {
			conf->currentProfile->specs = strndup(value, MAX_STRLEN);
			if(!conf->currentProfile->specs)
				return -1;
		} else if (strcmp(key, "ldpath") == 0) {
			conf->currentProfile->libdir = strndup(value, MAX_STRLEN);
			if(!conf->currentProfile->libdir)
				return -1;
		} else if (strcmp(key, "cflags") == 0) {
			conf->currentProfile->cflags = strndup(value, MAX_STRLEN);
			if(!conf->currentProfile->cflags)
				return -1;
		} else {
			/* unknown key... ignore it */
			return 0;
		}
	}

	return 0;
}
#endif

/** Allocate memory and load the configuration file */
InstallConf *loadInstallConf(const char *filename) {
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
	ConfigParser *config = parserNew(filename);
	parserSetData(config, retval);
	parserSetCallback(config, installConfSectionCB, installConfKeyCB);

	if(parseFile(config) != 0) {
		return NULL;
	}

	parserFree(config);
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
