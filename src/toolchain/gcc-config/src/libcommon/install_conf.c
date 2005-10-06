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
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/install_conf.c,v 1.29 2005/10/06 20:23:41 eradicator Exp $
 * $Log: install_conf.c,v $
 * Revision 1.29  2005/10/06 20:23:41  eradicator
 * Added bin_prefix, so alternate targets of multilib crosscompilers will work correctly.  Fixed bug whereby the native gcc could disappear after a set.
 *
 * Revision 1.28  2005/10/02 20:45:56  eradicator
 * BSD related cleanup.
 *
 * Revision 1.27  2005/09/30 19:35:54  eradicator
 * Added stdcxx_incdir.  Cleaned up some possible memory problems.
 *
 * Revision 1.26  2005/09/24 23:59:10  eradicator
 * Check hashNew return value.
 *
 * Revision 1.25  2005/09/24 22:32:41  eradicator
 * Changed key to be alias_<name> instead of alias<name>.
 *
 * Revision 1.24  2005/09/24 18:31:38  eradicator
 * Changed references to choat->ctarget.  Changed --default to --native.
 *
 * Revision 1.23  2005/09/24 09:18:05  eradicator
 * Cleaned up error handling in the config file parsing.
 *
 * Revision 1.22  2005/09/24 05:47:13  eradicator
 * Added scan_path option (not yet implemented).  When enabled, the PATH envvar will be searched for the executable like it was in gcc-config-1.x
 *
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

#include "strndup.h"
#include "selection_conf.h"
#include "install_conf.h"
#include "parse_conf.h"

#include <stdlib.h>
#include <string.h>

#include "install_conf.h"
#include "parse_conf.h"

#ifndef MAX_STRLEN
#define MAX_STRLEN 1023
#endif

#define EPARSE_NOMEM      -1
#define EPARSE_MOREGLOBAL -2
#define EPARSE_UNKNOWNKEY  3

static void freeProfile(Profile *profile);

struct installParseData {
	InstallConf *installConf;
	Profile *profile;
};

static int installConfSectionCB(const char *section, void *_data) {
	struct installParseData *data = (struct installParseData *)_data;
	InstallConf *conf = data->installConf;

	if (strcmp(section, "global") == 0) {
		if(conf->profileHash != NULL) {
			/* Multiple [global] sections */
			return EPARSE_MOREGLOBAL;
		}

		conf->profileHash = hashNew(16);

		if(conf->profileHash == NULL)
			return EPARSE_NOMEM;

		conf->wrapperAliases = hashNew(16);

		if(conf->wrapperAliases == NULL) {
			hashFree(conf->profileHash);
			return EPARSE_NOMEM;
		}
	} else {
		Profile *tmp;
		data->profile = (Profile *)calloc(1, sizeof(Profile));

		if(!data->profile)
			return EPARSE_NOMEM;

		data->profile->installConf = conf;
		data->profile->name = strndup(section, MAX_STRLEN);

		if(!data->profile->name) {
			free(data->profile);
			return EPARSE_NOMEM;
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

	if(value == NULL)
		return EPARSE_NOMEM;

#define set_to_value(var) if(var != NULL) free(var); var = value;
	
	if (!data->profile) { /* on global section */
		if (strcmp(key, "version") == 0) {
			set_to_value(conf->name);
		} else if (strcmp(key, "binpath") == 0) {
			set_to_value(conf->binpath);
		} else if (strcmp(key, "infopath") == 0) {
			set_to_value(conf->infopath);
		} else if (strcmp(key, "manpath") == 0) {
			set_to_value(conf->manpath);
		} else if (strcmp(key, "stdcxx_incdir") == 0) {
			set_to_value(conf->stdcxx_incdir);
		} else if (strcmp(key, "bin_prefix") == 0) {
			set_to_value(conf->bin_prefix);
			/* check aliases */
		} else if (strncmp(key, "alias_", 6) == 0) {
			tmp = hashInsert(conf->wrapperAliases, key+6, (void *)value);
			if(tmp)
				free(tmp);
		} else {
			/* unknown key... ignore it */
			return EPARSE_UNKNOWNKEY;
		}
	} else { /* on other sections */
		if (strcmp(key, "ctarget") == 0) {
			if(conf->bin_prefix == NULL)
				set_to_value(conf->bin_prefix);
			set_to_value(data->profile->ctarget);
		} else if (strcmp(key, "specs") == 0) {
			set_to_value(data->profile->specs);
		} else if (strcmp(key, "ldpath") == 0) {
			set_to_value(data->profile->libdir);
		} else if (strcmp(key, "cflags") == 0) {
			set_to_value(data->profile->cflags);
		} else {
			/* unknown key... ignore it */
			return EPARSE_UNKNOWNKEY;
		}
	}

#undef set_to_value

	return 0;
}

/** Allocate memory and load the configuration file */
InstallConf *loadInstallConf(const char *filename) {
	InstallConf *retval =  (InstallConf *)calloc(1, sizeof(InstallConf));

	ConfigParser *config;
	struct installParseData data;

	if(retval == NULL) {
		return NULL;
	}

	retval->stdcxx_incdir=strdup("g++");
	if(retval->stdcxx_incdir == NULL) {
		free(retval);
		return NULL;
	}

	config = parserNew(filename);
	if(config == NULL) {
		free(retval->stdcxx_incdir);
		free(retval);
		return NULL;
	}

	data.installConf = retval;
	data.profile = NULL;

	parserSetData(config, &data);
	parserSetCallback(config, installConfSectionCB, installConfKeyCB);

	if(parseFile(config) != 0) {
		free(retval->stdcxx_incdir);
		free(retval);
		parserFree(config);
		return NULL;
	}

	parserFree(config);
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
	if(profile->ctarget)
		free(profile->ctarget);
	if(profile->specs)
		free(profile->specs);
	if(profile->libdir)
		free(profile->libdir);
	if(profile->cflags)
		free(profile->cflags);
	free(profile);
}
