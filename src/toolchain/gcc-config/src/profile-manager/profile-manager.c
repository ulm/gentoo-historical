/*
 * C Implementation: profile-manager
 *
 * Description:
 * binary called by the eselect module to query and update the
 * configuration files in /etc/gcc-config and ~/.gcc-config
 *
 * profile-manager [-u] [--dir=<config dir>] <command> [<options>]
 *
 *   -u: Save changes in the user config directory ${HOME}/.gcc-config instead
 *       of the global config directory.
 *
 *   --config-dir=<config dir>: Use <config dir> instead of CONFIGURATION_DIR for the
 *                              global config dir.
 *
 *   Note below that <CHOST/-/_> means the CHOST with -s replaced with _s
 *   commands:
 *
 *   get-profiles
 *     get a set of environment variables (to be eval'd) which describe the
 *     available and installed profiles
 *
 *     COMPILER_CONFIG_DEFAULT_CHOST:
 *       The default CHOST
 *     COMPILER_CONFIG_ALL_CHOSTS:
 *       A sorted list of all CHOSTS for which a profile is available.
 *     COMPILER_CONFIG_SET_CHOSTS:
 *       A sorted list of all CHOSTS for which a profile is set.  Note that
 *       there might be a CHOST here which is not in COMPILER_CONFIG_ALL_CHOSTS
 *       because the user has used the --chost option to choose a non-default
 *       CHOST.
 *     COMPILER_CONFIG_PROFILES_<CHOST/-/_>:
 *       A sorted list of available profiles for the given CHOST.  The list is
 *       space delimeted with a forward slash between the install and profile.
 *     COMPILER_CONFIG_SET_<CHOST/-/_>:
 *       The selected <install>/<profile> for the given CHOST.
 *
 *   get-profile <install>/<profile>
 *     get a set of environment variables (to be eval'd) with the data for the
 *     given profile
 *
 *     COMPILER_CONFIG_BINPATH
 *     COMPILER_CONFIG_MANPATH
 *     COMPILER_CONFIG_INFOPATH
 *     COMPILER_CONFIG_LDPATH
 *     COMPILER_CONFIG_CHOST
 *     COMPILER_CONFIG_GCC_SPECS
 *     COMPILER_CONFIG_CFLAGS
 *     COMPILER_CONFIG_ALIASES
 *     COMPILER_CONFIG_ALIASE_<alias>
 *
 *   set <install>/<profile> [--chost=<CHOST>]
 *     activate a profile (and optionally assign it a CHOST other than its default)
 *
 * Author: Jeremy Huddleston <eradicator@gentoo.org>
 *
 * Copyright 1999-2005 Gentoo Foundation
 * Distributed under the terms of the GNU General Public License v2
 * See COPYING file that comes with this distribution
 *
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/profile-manager/Attic/profile-manager.c,v 1.16 2005/09/24 05:47:13 eradicator Exp $
 * $Log: profile-manager.c,v $
 * Revision 1.16  2005/09/24 05:47:13  eradicator
 * Added scan_path option (not yet implemented).  When enabled, the PATH envvar will be searched for the executable like it was in gcc-config-1.x
 *
 * Revision 1.15  2005/08/24 04:25:30  eradicator
 * Added COMPILER_CONFIG_ALIAS_<alias>
 *
 * Revision 1.14  2005/08/23 11:48:16  eradicator
 * Addressed a few portability concerns.
 *
 * Revision 1.13  2005/08/23 08:28:14  eradicator
 * Changed -u to --user for consistency
 *
 * Revision 1.12  2005/08/23 08:06:28  eradicator
 * Fixed typo which broke COMPILER_CONFIG_PROFILES_ output in some cases.
 *
 * Revision 1.11  2005/08/23 07:32:26  eradicator
 * Added --default option to set action.
 *
 * Revision 1.10  2005/08/23 02:54:09  eradicator
 * Changed 'gcc' references to 'compiler' since this is not gcc-specific.
 *
 * Revision 1.9  2005/08/23 02:39:30  eradicator
 * Making error messages consistant.
 *
 * Revision 1.8  2005/08/23 02:01:07  eradicator
 * Added error handling for set action.
 *
 * Revision 1.7  2005/08/23 00:59:16  eradicator
 * Added set action.
 *
 * Revision 1.6  2005/08/22 22:09:01  eradicator
 * Added get-profile action.  Made die() output a newline.
 *
 * Revision 1.5  2005/08/21 22:44:08  eradicator
 * Fixed a memleak
 *
 * Revision 1.4  2005/08/21 22:33:17  eradicator
 * Added get-profiles action.
 *
 * Revision 1.3  2005/08/21 20:38:50  eradicator
 * Command line parsing and added documantation of how the command will work.
 *
 * Revision 1.2  2005/08/19 03:35:29  eradicator
 * Cleaned up #include lines and added #include config.h.
 *
 * Revision 1.1  2005/08/18 23:19:28  eradicator
 * Added layout to begin working on the profile manager.
 *
 */

/* For strndup() */
#define _GNU_SOURCE

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <errno.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "selection_conf.h"
#include "install_conf.h"

#ifndef MAXPATHLEN
#define MAXPATHLEN 1023
#endif

#define ACTION_NONE          0
#define ACTION_GET_PROFILES  1
#define ACTION_GET_PROFILE   2
#define ACTION_SET           3

#if HAVE_MKDIR
#  if MKDIR_TAKES_ONE_ARG
#    define mkdir(a, b) mkdir(a)
#  endif
#else
#  if HAVE__MKDIR
#    define mkdir(a, b) _mkdir(a)
#  else
#    error "Don't know how to create a directory on this system."
#  endif
#endif

static void die(const char *msg, ...) {
	va_list args;
	fprintf(stderr, "profile-manager error: ");
	va_start(args, msg);
	vfprintf(stderr, msg, args);
	va_end(args);
	fputc('\n', stderr);
	exit(1);
}

#define MAX_CHOSTS 128

typedef struct _pnode {
	const Profile *profile;
	struct _pnode *prev;
	struct _pnode *next;
} PNode;

static void doGetProfiles(const SelectionConf *selectionConf, FILE *fd) {
	const char **installs;
	const char **setChosts;
	const char **allChosts;
	Hash *profilesByChost;
	const InstallConf *installConf;
	size_t i;

	if(selectionConf == NULL)
		return;

	setChosts = hashKeysSorted(selectionConf->selectionHash);
	installs = hashKeysSorted(selectionConf->installHash);
	profilesByChost = hashNew(16);

	if(setChosts == NULL || installs == NULL || allChosts == NULL)
		goto end_doGetProfiles;

	/* We need to create our profilesByChost hash */
	for(i=0; installs[i] != NULL; i++) {
		const char **profiles;
		size_t j;

		installConf = hashGet(selectionConf->installHash, installs[i]);
		if(!installConf)
			continue;

		profiles = hashKeysSorted(installConf->profileHash);
		if(!profiles)
			continue;

		for(j=0; profiles[j] != NULL; j++) {
			PNode *pn, *opn;
			pn = (PNode *)calloc(1, sizeof(PNode));
			if(!pn)
				die("Memory allocation failure.");
			pn->profile = hashGet(installConf->profileHash, profiles[j]);
			opn = (PNode *)hashInsert(profilesByChost, pn->profile->chost, pn);
			if(opn) {
				opn->prev = pn;
				pn->next = opn;
			}
		}

		free(profiles);
	}

	allChosts = hashKeysSorted(profilesByChost);
	if(allChosts == NULL)
		goto end_doGetProfiles;

	/*     COMPILER_CONFIG_DEFAULT_CHOST:
	 *       The default CHOST
	 */

	fprintf(fd, "COMPILER_CONFIG_DEFAULT_CHOST=\"%s\"\n", selectionConf->defaultChost);

	/*     COMPILER_CONFIG_ALL_CHOSTS:
	 *       A sorted list of all CHOSTS for which a profile is available.
	 */
	fputs("COMPILER_CONFIG_ALL_CHOSTS=\"", fd);
	for(i=0; allChosts[i] != NULL; i++) {
		if(i != 0)
			fputc(' ', fd);
		fputs(allChosts[i], fd);
	}
	fputs("\"\n", fd);

	/*     COMPILER_CONFIG_SET_CHOSTS:
	 *       A sorted list of all CHOSTS for which a profile is set.  Note that
	 *       there might be a CHOST here which is not in COMPILER_CONFIG_ALL_CHOSTS
	 *       because the user has used the --chost option to choose a non-default
	 *       CHOST.
	 */
	fputs("COMPILER_CONFIG_SET_CHOSTS=\"", fd);
	for(i=0; setChosts[i] != NULL; i++) {
		if(i != 0)
			fputc(' ', fd);
		fputs(setChosts[i], fd);
	}
	fputs("\"\n", fd);

	/*     COMPILER_CONFIG_PROFILES_<CHOST/-/_>:
	 *       A sorted list of available profiles for the given CHOST.  The list is
	 *       space delimeted with a forward slash between the install and profile.
	 */
	for(i=0; allChosts[i] != NULL; i++) {
		PNode *pn = hashGet(profilesByChost, allChosts[i]);
		unsigned needSpace = 0;

		char *chostul=strndup(allChosts[i], MAXPATHLEN);
		char *s;
		if(!chostul)
			die("Memory allocation failure.");
		for(s = chostul; *s; s++) {
			if(*s == '-')
				*s = '_';
		}

		fprintf(fd, "COMPILER_CONFIG_PROFILES_%s=\"", chostul);
		free(chostul);

		/* Our list is reversed, so start at the end */
		for(; pn->next; pn = pn->next);

		for(; pn; pn = pn->prev) {
			const Profile *profile = pn->profile;
			if(needSpace)
				fputc(' ', fd);
			else
				needSpace = 1;

			fprintf(fd, "%s/%s", profile->installConf->name, profile->name);
		}
		fputs("\"\n", fd);
	}

	/*     COMPILER_CONFIG_SET_<CHOST/-/_>:
	 *       The selected <install>/<profile> for the given CHOST.
	 */
	for(i=0; setChosts[i] != NULL; i++) {
		Profile *profile = hashGet(selectionConf->selectionHash, setChosts[i]);
		char *chostul=strndup(setChosts[i], MAXPATHLEN);
		char *s;
		if(!chostul)
			die("Memory allocation failure.");
		for(s = chostul; *s; s++) {
			if(*s == '-')
				*s = '_';
		}
		fprintf(fd, "COMPILER_CONFIG_SET_%s=\"%s/%s\"\n", chostul, profile->installConf->name, profile->name);
		free(chostul);
	}

end_doGetProfiles:
	if(installs) free(installs);
	if(setChosts) free(setChosts);

	if(profilesByChost) {
		if(!allChosts)
			allChosts = hashKeys(profilesByChost);
		for(i=0; allChosts[i] != NULL; i++) {
			PNode *pn;
			PNode *next;
			for(pn = (PNode *)hashGet(profilesByChost, allChosts[i]); pn; pn = next) {
				next = pn->next;
				free(pn);
			}
		}
		hashFree(profilesByChost);
	}

	if(allChosts) free(allChosts);
}

static void doGetProfile(const SelectionConf *selectionConf, const char *install, const char *profileStr, FILE *fd) {
	InstallConf *installConf;
	Profile *profile;
	size_t i;
	const char **aliases;

	installConf = hashGet(selectionConf->installHash, install);
	if(!installConf)
		die("No such install: %s", install);

	profile = hashGet(installConf->profileHash, profileStr);
	if(!profile)
		die("No such profile: %s/%s", install, profileStr);

	/* COMPILER_CONFIG_BINPATH */
	fprintf(fd, "COMPILER_CONFIG_BINPATH=\"%s\"\n", installConf->binpath);

	/* COMPILER_CONFIG_MANPATH */
	fprintf(fd, "COMPILER_CONFIG_MANPATH=\"%s\"\n", installConf->manpath ? installConf->manpath : "");

	/* COMPILER_CONFIG_INFOPATH */
	fprintf(fd, "COMPILER_CONFIG_INFOPATH=\"%s\"\n", installConf->infopath ? installConf->infopath : "");

	/* COMPILER_CONFIG_LDPATH */
	fprintf(fd, "COMPILER_CONFIG_LDPATH=\"%s\"\n", profile->libdir);

	/* COMPILER_CONFIG_CHOST */
	fprintf(fd, "COMPILER_CONFIG_CHOST=\"%s\"\n", profile->chost);

	/* COMPILER_CONFIG_GCC_SPECS */
	fprintf(fd, "COMPILER_CONFIG_GCC_SPECS=\"%s\"\n", profile->specs ? profile->specs : "");

	/* COMPILER_CONFIG_CFLAGS */
	fprintf(fd, "COMPILER_CONFIG_CFLAGS=\"%s\"\n", profile->cflags ? profile->cflags : "");

	/* COMPILER_CONFIG_ALIASES */
	aliases = hashKeysSorted(installConf->wrapperAliases);
	if(!aliases)
		die("Memory allocation failure.");
	fputs("COMPILER_CONFIG_ALIASES=\"", fd);
	for(i=0; aliases[i] != NULL; i++) {
		if(i != 0)
			fputc(' ', fd);
		fputs(aliases[i], fd);
	}
	fputs("\"\n", fd);

	/* COMPILER_CONFIG_ALIASE_<alias> */
	for(i=0; aliases[i] != NULL; i++) {
		fprintf(fd, "COMPILER_CONFIG_ALIAS_%s=\"%s\"\n", aliases[i], (const char *)hashGet(installConf->wrapperAliases, aliases[i]));
	}
}

/* If CHOST is null, we use the default chost for the profile */
static void doSet(SelectionConf *selectionConf, const char *install, const char *profileStr, const char *chost, unsigned makeDefault) {
	InstallConf *installConf;
	Profile *profile;

	installConf = hashGet(selectionConf->installHash, install);
	if(!installConf)
		die("No such install: %s", install);

	profile = hashGet(installConf->profileHash, profileStr);
	if(!profile)
		die("No such profile: %s/%s", install, profile);

	if(chost == NULL)
		chost = profile->chost;

	hashInsert(selectionConf->selectionHash, chost, profile);

	if(makeDefault) {
		if(selectionConf->defaultChost)
			free(selectionConf->defaultChost);
		selectionConf->defaultChost = strndup(chost, MAXPATHLEN);
	}
}

int main(int argc, char **argv) {
	SelectionConf *selectionConf;
	unsigned action = ACTION_NONE;
	size_t i;
	unsigned userProfile = 0;
	unsigned makeDefault = 0;
	const char *configDir = CONFIGURATION_DIR;
	const char *chost = NULL;
	char *install = NULL;
	char *profile = NULL;

	for(i=1; i < argc; i++) {
		if(strcmp(argv[i], "--user") == 0) {
			userProfile = 1;
		} else if(strncmp(argv[i], "--config-dir=", 13) == 0) {
			configDir = argv[i] + 13;
		} else if(strcmp(argv[i], "get-profiles") == 0) {
			action = ACTION_GET_PROFILES;
			i++;
			break;
		} else if(strcmp(argv[i], "get-profile") == 0) {
			action = ACTION_GET_PROFILE;
			i++;
			break;
		} else if(strcmp(argv[i], "set") == 0) {
			action = ACTION_SET;
			i++;
			break;
		} else {
			die("Invalid command: %s", argv[i]);
		}
	}

	selectionConf = loadSelectionConf(configDir, userProfile);

	switch(action) {
		case ACTION_GET_PROFILES:
			/* No extra options */
			if(i < argc)
				die("get-profile does not take extra options.");
			doGetProfiles(selectionConf, stdout);
			break;

		case ACTION_GET_PROFILE:
			/* Just one option (the profile) */
			if(i + 1 < argc)
				die("get-profiles takes only one option, the profile being queried.");

			/* Find the split */
			install = argv[i];
			for(profile = install; *profile != '\0' && *profile != '/' && profile - install < MAXPATHLEN; profile++);
			if(*profile == '\0' || profile - install == MAXPATHLEN)
				die("There was no / in the profile given");

			*profile = '\0';
			profile++;

			doGetProfile(selectionConf, install, profile, stdout);
			break;

		case ACTION_SET:
			for(; i < argc; i++) {
				if(strncmp(argv[i], "--chost=", 8) == 0) {
					chost = argv[i] + 8;
				} else if(strcmp(argv[i], "--default") == 0) {
					makeDefault = 1;
				} else {
					/* Find the split */
					install = argv[i];
					for(profile = install; *profile != '\0' && *profile != '/' && profile - install < MAXPATHLEN; profile++);
					if(*profile == '\0' || profile - install == MAXPATHLEN)
						die("There was no / in the profile given");

					*profile = '\0';
					profile++;
				}
			}

			if(!install)
				die("You did not give a profile to set.");

			doSet(selectionConf, install, profile, chost, makeDefault);
			if(saveSelectionConf(selectionConf, configDir, userProfile) != 0)
				die("Error saving config: %s", strerror(errno));
			break;

		default:
			die("No action selected.");
			break;
	}
	return 0;
}
