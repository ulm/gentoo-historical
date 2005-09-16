/*
 * C Implementation: selection_conf
 *
 * Description: 
 * C code for dealing with /etc/gcc-config/selection.conf
 *
 * Author: Jeremy Huddleston <eradicator@gentoo.org>
 *
 * Copyright 1999-2005 Gentoo Foundation
 * Distributed under the terms of the GNU General Public License v2
 * See COPYING file that comes with this distribution
 *
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/selection_conf.c,v 1.22 2005/09/16 17:44:23 eradicator Exp $
 * $Log: selection_conf.c,v $
 * Revision 1.22  2005/09/16 17:44:23  eradicator
 * Some fixes to make the code C90 compliant.
 *
 * Revision 1.21  2005/09/09 08:46:44  eradicator
 * Set correct parsing data object.
 *
 * Revision 1.20  2005/09/09 08:32:29  eradicator
 * Made selection config parsing callbacks.
 *
 * Revision 1.19  2005/09/09 06:54:48  eradicator
 * Added in more error checking code.
 *
 * Revision 1.18  2005/09/09 06:46:53  eradicator
 * A few bugs which slipped through the cracks...
 *
 * Revision 1.17  2005/09/09 06:41:11  eradicator
 * Added code to read in all the InstallConf files.
 *
 * Revision 1.16  2005/08/26 19:55:06  sekretarz
 * Parsing global section code
 *
 * Revision 1.15  2005/08/23 11:48:16  eradicator
 * Addressed a few portability concerns.
 *
 * Revision 1.14  2005/08/23 02:33:09  eradicator
 * Create the directory when saving the profile.
 *
 * Revision 1.13  2005/08/23 02:00:39  eradicator
 * Added code to save the selection config.
 *
 * Revision 1.12  2005/08/23 00:57:36  eradicator
 * Let user config dir be configurable.
 *
 * Revision 1.11  2005/08/21 03:52:16  eradicator
 * A couple portability fixes...
 *
 * Revision 1.10  2005/08/20 22:46:35  eradicator
 * Made the global configuration directory configurable.
 *
 * Revision 1.9  2005/08/20 22:03:48  eradicator
 * Let users override settings in ~/.gcc-config.
 *
 * Revision 1.8  2005/08/19 06:08:55  eradicator
 * Added headers to EXTRA_DIST.
 *
 * Revision 1.7  2005/08/19 03:35:29  eradicator
 * Cleaned up #include lines and added #include config.h.
 *
 * Revision 1.6  2005/08/18 23:30:24  eradicator
 * Coding style changes to make consistent with the rest of the codebase.  Whitespace cleanup.  Made some functions static.
 *
 * Revision 1.5  2005/08/18 23:19:28  eradicator
 * Added layout to begin working on the profile manager.
 *
 * Revision 1.4  2005/08/16 17:34:57  sekretarz
 * Adding new config framework
 *
 * Revision 1.3  2005/08/12 09:45:52  eradicator
 * Added defaultChost.
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

#include <dirent.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>

#include "selection_conf.h"
#include "install_conf.h"
#include "parse_conf.h"

#ifndef MAXPATHLEN
#define MAXPATHLEN 1023
#endif

struct selectionParseData {
	SelectionConf *selectionConf;
	char chost[MAXPATHLEN + 1];
};

#ifndef USE_HARDCODED_CONF
static int selectionConfSectionCB(const char *section, void *_data) {
	struct selectionParseData *data = (struct selectionParseData *)_data;

	if (strcmp(section, "global") == 0) {
		data->chost[0] = '\0';
	} else {
		strncpy(data->chost, section, MAXPATHLEN);
	}
	return 0;
}

static int selectionConfKeyCB(const char *key, const char *value, void *_data) {
	struct selectionParseData *data = (struct selectionParseData *)_data;
	SelectionConf *selconf = data->selectionConf;

	if (data->chost[0] == '\0') { /* global */
		if(strcmp(key, "default_chost") == 0) {
			selconf->defaultChost = strndup(value, MAXPATHLEN);
			if(!selconf->defaultChost)
				return -1;
		} else {
			/* unknown key... ignore it */
			return 0;
		}
	} else { /* selected profile */
		 if(strcmp(key, "profile") == 0) {
			char version[MAXPATHLEN + 1];
			char *profile;
			InstallConf *installConf;
			Profile *prof;
			strncpy(version, value, MAXPATHLEN);

			/* First we need to split the profile given as <version>/<profile> */
			for(profile=version; *profile && *profile != '/'; profile++);
			if(*profile != '/')
				return 0; /* -2 */

			*profile = '\0';
			profile++;

			/* Now, find the installConf */
			installConf = (InstallConf *)hashGet(selconf->installHash, version);
			if(!installConf)
				return 0; /* -2 */

			/* Now find the profile */
			prof = (Profile *)hashGet(installConf->profileHash, profile);
			if(!prof)
				return 0; /* -2 */

			hashInsert(selconf->selectionHash, data->chost, (void *)prof);
		 } else {
			/* unknown key... ignore it */
			return 0;
		}
	}
	return 0;
}
#endif

static void loadInstallConfs(const char *dirname, SelectionConf *selectionConf) {
	DIR *dir;
	struct dirent *ent;
	char filename[MAXPATHLEN + 1];

	dir = opendir(dirname);
	if (dir) {
		while ((ent = readdir(dir)) != NULL) {
			size_t len = strlen(ent->d_name);
			if(strcmp(ent->d_name + len - 5, ".conf") == 0 &&
				 strcmp(ent->d_name, "selection.conf") != 0) {
				/* This is a config file we need to load */
				InstallConf *confNew, *confOld;

				snprintf(filename, MAXPATHLEN, "%s/%s", dirname, ent->d_name);
				confNew = loadInstallConf(filename);

				/* Ignore bogus files here */
				if(!confNew)
					continue;

				/* Insert to hash */
				confOld = hashInsert(selectionConf->installHash, confNew->name, confNew);

				/* Free any memory associated with an entry that was already there */
				if(confOld) {
					freeInstallConf(confOld);
				}
			}
		}

		closedir(dir);
	}
}

inline static int loadSelections(const char *filename, SelectionConf *selectionConf) {
	int retval;
	ConfigParser *config = parserNew(filename);
	struct selectionParseData data;

	if(!config)
		return -1;

	data.selectionConf = selectionConf;
	data.chost[0] = '\0';

	parserSetData(config, &data);
	parserSetCallback(config, selectionConfSectionCB, selectionConfKeyCB);
	retval = parseFile(config);
	parserFree(config);

	return retval;
}

/** Allocate memory and load the configuration file */
SelectionConf *loadSelectionConf(const char *globalConfigDir, unsigned userOverride) {
	SelectionConf *retval = (SelectionConf *)malloc(sizeof(SelectionConf));

#ifdef USE_HARDCODED_CONF
	InstallConf *installConf;

	/* Not production code... */
	retval->installHash = hashNew(10);
	retval->selectionHash = hashNew(10);

	retval->defaultChost = (char *)malloc(sizeof(char) * 30);
	strcpy(retval->defaultChost, "x86_64-pc-linux-gnu");

	installConf = loadInstallConf("/etc/gcc-config/x86_64-pc-linux-gnu-3.4.4.conf");
	hashInsert(retval->installHash, "x86_64-pc-linux-gnu-3.4.4", installConf);
	hashInsert(retval->selectionHash, "x86_64-pc-linux-gnu", hashGet(installConf->profileHash, "amd64-hardened"));
	hashInsert(retval->selectionHash, "i686-pc-linux-gnu", hashGet(installConf->profileHash, "x86-vanilla"));
	hashInsert(retval->selectionHash, "i386-pc-linux-gnu", hashGet(installConf->profileHash, "x86-vanilla"));
#else
	char filename[MAXPATHLEN + 1];

	retval->installHash = hashNew(10);
	retval->selectionHash = hashNew(10);

	/* Load all the installation configuration files from the directory given */
	loadInstallConfs(globalConfigDir, retval);

	/* Now load the installation configurations from the user's directory */
	if(userOverride) {
		snprintf(filename, MAXPATHLEN, "%s/%s", getenv("HOME"), USER_CONFIGURATION_DIR);
		loadInstallConfs(filename, retval);
	}

	/* Now determine what profiles are selected by the global configuration */
	snprintf(filename, MAXPATHLEN, "%s/selection.conf", globalConfigDir);
	loadSelections(filename, retval);

	/* Now checkout the user override */
	if(userOverride) {
		snprintf(filename, MAXPATHLEN, "%s/%s/selection.conf", getenv("HOME"), USER_CONFIGURATION_DIR);
		loadSelections(filename, retval);
	}
#endif

	return retval;
}

/** Save the configuration file */
int saveSelectionConf(SelectionConf *selectionConf, const char *globalConfigDir, unsigned userOverride) {
	char dirname[MAXPATHLEN + 1];
	char filename[MAXPATHLEN + 1];
	const char **chosts;
	FILE *fd;
	size_t i;

	/* What directory are we storing the file in */
	if(userOverride) {
		snprintf(dirname, MAXPATHLEN, "%s/%s", getenv("HOME"), USER_CONFIGURATION_DIR);
	} else {
		strncpy(dirname, globalConfigDir, MAXPATHLEN);
	}

	/* Make the directory if it doesn't exist*/
	if(mkdir(dirname, 0777) < 0) {
		if(errno !=EEXIST)
			return errno;
	}

	/* Open the file */
	snprintf(filename, MAXPATHLEN, "%s/selection.conf", dirname);
	fd = fopen(filename, "w");
	if(!fd)
		return errno;

	/* [global] section */
	fprintf(fd, "[global]\n");
	fprintf(fd, "\tchost=%s\n", selectionConf->defaultChost);

	chosts = hashKeysSorted(selectionConf->selectionHash);
	if(!chosts)
		return errno;

	/* Section for each CHOST */
	for(i=0; chosts[i] != NULL; i++) {
		Profile *profile = hashGet(selectionConf->selectionHash, chosts[i]);
		fprintf(fd, "\n[%s]\n", chosts[i]);
		fprintf(fd, "\tversion=%s\n", profile->installConf->name);
		fprintf(fd, "\tprofile=%s\n", profile->name);
	}

	/* Close the file */
	fclose(fd);

	/* Cleanup */
	free(chosts);

	return 0;
}

/** Free selectionConf and its contents */
void freeSelectionConf(SelectionConf *selectionConf) {
	/* TODO: Worry about this once/if we need it. */
	if(!selectionConf)
		return;

	free(selectionConf);
}
