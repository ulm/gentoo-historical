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
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/install_conf.c,v 1.21 2005/09/16 17:44:23 eradicator Exp $
 * $Log: install_conf.c,v $
 * Revision 1.21  2005/09/16 17:44:23  eradicator
 * Some fixes to make the code C90 compliant.
 *
 * Revision 1.20  2005/09/09 08:46:44  eradicator
 * Set correct parsing data object.
 *
 * Revision 1.19  2005/09/09 07:59:08  eradicator
 * No longer exposing parsing internals in the InstallConf struct.
 *
 * Revision 1.18  2005/09/09 07:00:38  eradicator
 * Fix possible memory leak.
 *
 * Revision 1.17  2005/09/09 06:54:48  eradicator
 * Added in more error checking code.
 *
 * Revision 1.16  2005/09/09 06:46:53  eradicator
 * A few bugs which slipped through the cracks...
 *
 * Revision 1.15  2005/09/09 06:36:00  eradicator
 * Added code to free memory used by an InstallConf object.
 *
 * Revision 1.14  2005/09/09 06:30:22  eradicator
 * Fixed ambiguity in README.  Cleaned up some redundency in the code.
 *
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

static void freeProfile(Profile *profile);

struct installParseData {
	InstallConf *installConf;
	Profile *profile;
};

#ifndef USE_HARDCODED_CONF
static int installConfSectionCB(const char *section, void *_data) {
	struct installParseData *data = (struct installParseData *)_data;
	InstallConf *conf = data->installConf;

	if (strcmp(section, "global") == 0) {
		data->profile = NULL;
		conf->profileHash = hashNew(10);
		conf->wrapperAliases = hashNew(10);
	} else {
		Profile *tmp;
		data->profile = (Profile *)calloc(1, sizeof(Profile));

		if(!data->profile)
			return -1;

		data->profile->installConf = conf;
		data->profile->name = strndup(section, MAX_STRLEN);

		if(!data->profile->name) {
			free(data->profile);
			return -1;
		}

		tmp = hashInsert(conf->profileHash, data->profile->name, data->profile);
		if(tmp)
			freeProfile(tmp);
	}
	return 0;
}

static int installConfKeyCB(const char *key, const char *_value, void *_data) {
	struct installParseData *data = (struct installParseData *)_data;
	InstallConf *conf = data->installConf;
	char *value = strndup(_value, MAX_STRLEN);
	char *tmp;

	if(!value)
		return -1;

	if (!data->profile) { /* on global section */
		if (strcmp(key, "version") == 0) {
			conf->name = value;
		} else if (strcmp(key, "binpath") == 0) {
			conf->binpath = value;
		} else if (strcmp(key, "infopath") == 0) {
			conf->infopath = value;
		} else if (strcmp(key, "manpath") == 0) {
			conf->manpath  = value;
			/* check aliases */
		} else if (strncmp(key, "alias", 5) == 0) {
			tmp = hashInsert(conf->wrapperAliases, key+5, (void *)value);
			if(tmp)
				free(tmp);
		} else {
			/* unknown key... ignore it */
			return 0;
		}
	} else { /* on other sections */
		if (strcmp(key, "chost") == 0) {
			data->profile->chost = value;
		} else if (strcmp(key, "specs") == 0) {
			data->profile->specs = value;
		} else if (strcmp(key, "ldpath") == 0) {
			data->profile->libdir = value;
		} else if (strcmp(key, "cflags") == 0) {
			data->profile->cflags = value;
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
	struct installParseData data;

	if(!config)
		return NULL;

	data.installConf = retval;
	data.profile = NULL;

	parserSetData(config, &data);
	parserSetCallback(config, installConfSectionCB, installConfKeyCB);

	if(parseFile(config) != 0) {
		parserFree(config);
		return NULL;
	}

	parserFree(config);
#endif

	return retval;
}

/** Free installConf and its contents */
void freeInstallConf(InstallConf *installConf) {
	if(!installConf)
		return;

	if(installConf->name)
		free(installConf->name);
	if(installConf->binpath)
		free(installConf->binpath);
	if(installConf->infopath)
		free(installConf->infopath);
	if(installConf->manpath)
		free(installConf->manpath);

	if(installConf->profileHash) {
		const char **keys = hashKeys(installConf->profileHash);

		if(keys) {
			size_t i;
			for(i=0; keys[i]; i++)
				freeProfile((Profile *)hashGet(installConf->profileHash, keys[i]));
		}

		hashFree(installConf->profileHash);
	}

	if(installConf->wrapperAliases)
		hashFreeAll(installConf->wrapperAliases);

	free(installConf);
}

static void freeProfile(Profile *profile) {
	if(!profile)
		return;
	if(profile->name)
		free(profile->name);
	if(profile->chost)
		free(profile->chost);
	if(profile->specs)
		free(profile->specs);
	if(profile->libdir)
		free(profile->libdir);
	if(profile->cflags)
		free(profile->cflags);
	free(profile);
}
