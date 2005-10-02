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
 *   Note below that <CTARGET/-/_> means the CTARGET with -s replaced with _s
 *   (and the .s also replaced with _ to work on versioned CTARGETs)
 *   commands:
 *
 *   get-profiles
 *     get a set of environment variables (to be eval'd) which describe the
 *     available and installed profiles
 *
 *     COMPILER_CONFIG_DEFAULT_CTARGET:
 *       The default CTARGET
 *     COMPILER_CONFIG_ALL_CTARGETS:
 *       A sorted list of all CTARGETS for which a profile is available.
 *     COMPILER_CONFIG_SET_CTARGETS:
 *       A sorted list of all CTARGETS for which a profile is set.  Note that
 *       there might be a CTARGET here which is not in COMPILER_CONFIG_ALL_CTARGETS
 *       because the user has used the --ctarget option to choose a non-default
 *       CTARGET.
 *     COMPILER_CONFIG_PROFILES_<CTARGET/-/_>:
 *       A sorted list of available profiles for the given CTARGET.  The list is
 *       space delimeted with a forward slash between the install and profile.
 *     COMPILER_CONFIG_SET_<CTARGET/-/_>:
 *       The selected <install>/<profile> for the given CTARGET.
 *
 *   get-profile <install>/<profile>
 *     get a set of environment variables (to be eval'd) with the data for the
 *     given profile
 *
 *     COMPILER_CONFIG_BINPATH
 *     COMPILER_CONFIG_MANPATH
 *     COMPILER_CONFIG_INFOPATH
 *     COMPILER_CONFIG_LDPATH
 *     COMPILER_CONFIG_CTARGET
 *     COMPILER_CONFIG_GCC_SPECS
 *     COMPILER_CONFIG_CFLAGS
 *     COMPILER_CONFIG_ALIASES
 *     COMPILER_CONFIG_ALIASE_<alias>
 *
 *   set <install>/<profile> [--ctarget=<CTARGET>]
 *     activate a profile (and optionally assign it a CTARGET other than its default)
 *
 *   unset <CTARGET>
 *     deactivate the profile for the given CTARGET
 *
 * Author: Jeremy Huddleston <eradicator@gentoo.org>
 *
 * Copyright 1999-2005 Gentoo Foundation
 * Distributed under the terms of the GNU General Public License v2
 * See COPYING file that comes with this distribution
 *
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/profile-manager/Attic/profile-manager.c,v 1.20 2005/10/02 20:45:56 eradicator Exp $
 * $Log: profile-manager.c,v $
 * Revision 1.20  2005/10/02 20:45:56  eradicator
 * BSD related cleanup.
 *
 * Revision 1.19  2005/10/02 03:10:11  eradicator
 * Added unset action to profile-manager.
 *
 * Revision 1.18  2005/09/30 19:46:38  eradicator
 * Added stdcxx_incdir output.
 *
 * Revision 1.17  2005/09/24 18:31:38  eradicator
 * Changed references to choat->ctarget.  Changed --default to --native.
 *
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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "strndup.h"
#include "selection_conf.h"
#include "install_conf.h"

#include <errno.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef MAXPATHLEN
#define MAXPATHLEN 1023
#endif

#define ACTION_NONE          0
#define ACTION_GET_PROFILES  1
#define ACTION_GET_PROFILE   2
#define ACTION_SET           3
#define ACTION_UNSET         4

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

#define MAX_CTARGETS 128

typedef struct _pnode {
	const Profile *profile;
	struct _pnode *prev;
	struct _pnode *next;
} PNode;

static void doGetProfiles(const SelectionConf *selectionConf, FILE *fd) {
	const char **installs;
	const char **setCtargets;
	const char **allCtargets = NULL;
	Hash *profilesByCtarget;
	const InstallConf *installConf;
	size_t i;

	if(selectionConf == NULL)
		return;

	setCtargets = hashKeysSorted(selectionConf->selectionHash);
	installs = hashKeysSorted(selectionConf->installHash);
	profilesByCtarget = hashNew(16);

	if(setCtargets == NULL || installs == NULL)
		goto end_doGetProfiles;

	/* We need to create our profilesByCtarget hash */
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
			opn = (PNode *)hashInsert(profilesByCtarget, pn->profile->ctarget, pn);
			if(opn) {
				opn->prev = pn;
				pn->next = opn;
			}
		}

		free(profiles);
	}

	allCtargets = hashKeysSorted(profilesByCtarget);
	if(allCtargets == NULL)
		goto end_doGetProfiles;

	/*     COMPILER_CONFIG_DEFAULT_CTARGET:
	 *       The default CTARGET
	 */

	fprintf(fd, "COMPILER_CONFIG_DEFAULT_CTARGET=\"%s\"\n", selectionConf->defaultCtarget);

	/*     COMPILER_CONFIG_ALL_CTARGETS:
	 *       A sorted list of all CTARGETS for which a profile is available.
	 */
	fputs("COMPILER_CONFIG_ALL_CTARGETS=\"", fd);
	for(i=0; allCtargets[i] != NULL; i++) {
		if(i != 0)
			fputc(' ', fd);
		fputs(allCtargets[i], fd);
	}
	fputs("\"\n", fd);

	/*     COMPILER_CONFIG_SET_CTARGETS:
	 *       A sorted list of all CTARGETS for which a profile is set.  Note that
	 *       there might be a CTARGET here which is not in COMPILER_CONFIG_ALL_CTARGETS
	 *       because the user has used the --ctarget option to choose a non-default
	 *       CTARGET.
	 */
	fputs("COMPILER_CONFIG_SET_CTARGETS=\"", fd);
	for(i=0; setCtargets[i] != NULL; i++) {
		if(i != 0)
			fputc(' ', fd);
		fputs(setCtargets[i], fd);
	}
	fputs("\"\n", fd);

	/*     COMPILER_CONFIG_PROFILES_<CTARGET/-/_>:
	 *       A sorted list of available profiles for the given CTARGET.  The list is
	 *       space delimeted with a forward slash between the install and profile.
	 */
	for(i=0; allCtargets[i] != NULL; i++) {
		PNode *pn = hashGet(profilesByCtarget, allCtargets[i]);
		unsigned needSpace = 0;

		char *ctargetul=strndup(allCtargets[i], MAXPATHLEN);
		char *s;
		if(!ctargetul)
			die("Memory allocation failure.");
		for(s = ctargetul; *s; s++) {
			if(*s == '-' || *s == '.')
				*s = '_';
		}

		fprintf(fd, "COMPILER_CONFIG_PROFILES_%s=\"", ctargetul);
		free(ctargetul);

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

	/*     COMPILER_CONFIG_SET_<CTARGET/-/_>:
	 *       The selected <install>/<profile> for the given CTARGET.
	 */
	for(i=0; setCtargets[i] != NULL; i++) {
		Profile *profile = hashGet(selectionConf->selectionHash, setCtargets[i]);
		char *ctargetul=strndup(setCtargets[i], MAXPATHLEN);
		char *s;
		if(!ctargetul)
			die("Memory allocation failure.");
		for(s = ctargetul; *s; s++) {
			if(*s == '-' || *s == '.')
				*s = '_';
		}
		fprintf(fd, "COMPILER_CONFIG_SET_%s=\"%s/%s\"\n", ctargetul, profile->installConf->name, profile->name);
		free(ctargetul);
	}

end_doGetProfiles:
	if(installs) free(installs);
	if(setCtargets) free(setCtargets);

	if(profilesByCtarget) {
		if(!allCtargets)
			allCtargets = hashKeys(profilesByCtarget);
		for(i=0; allCtargets[i] != NULL; i++) {
			PNode *pn;
			PNode *next;
			for(pn = (PNode *)hashGet(profilesByCtarget, allCtargets[i]); pn; pn = next) {
				next = pn->next;
				free(pn);
			}
		}
		hashFree(profilesByCtarget);
	}

	if(allCtargets) free(allCtargets);
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

	/* COMPILER_CONFIG_STDCXX_INCDIR */
	fprintf(fd, "COMPILER_CONFIG_STDCXX_INCDIR=\"%s\"\n", installConf->stdcxx_incdir);

	/* COMPILER_CONFIG_LDPATH */
	fprintf(fd, "COMPILER_CONFIG_LDPATH=\"%s\"\n", profile->libdir);

	/* COMPILER_CONFIG_CTARGET */
	fprintf(fd, "COMPILER_CONFIG_CTARGET=\"%s\"\n", profile->ctarget);

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

/* If CTARGET is null, we use the default ctarget for the profile */
static void doSet(SelectionConf *selectionConf, const char *install, const char *profileStr, const char *ctarget, unsigned makeDefault) {
	InstallConf *installConf;
	Profile *profile;

	installConf = hashGet(selectionConf->installHash, install);
	if(!installConf)
		die("No such install: %s", install);

	profile = hashGet(installConf->profileHash, profileStr);
	if(!profile)
		die("No such profile: %s/%s", install, profile);

	if(ctarget == NULL)
		ctarget = profile->ctarget;

	hashInsert(selectionConf->selectionHash, ctarget, profile);

	if(makeDefault) {
		if(selectionConf->defaultCtarget)
			free(selectionConf->defaultCtarget);
		selectionConf->defaultCtarget = strndup(ctarget, MAXPATHLEN);
	}
}

inline static void doUnSet(SelectionConf *selectionConf, const char *ctarget) {
	hashDel(selectionConf->selectionHash, ctarget);
}

int main(int argc, char **argv) {
	SelectionConf *selectionConf;
	unsigned action = ACTION_NONE;
	size_t i;
	unsigned userProfile = 0;
	unsigned makeDefault = 0;
	const char *configDir = CONFIGURATION_DIR;
	const char *ctarget = NULL;
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
		} else if(strcmp(argv[i], "unset") == 0) {
			action = ACTION_UNSET;
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
				if(strncmp(argv[i], "--ctarget=", 10) == 0) {
					ctarget = argv[i] + 10;
				} else if(strcmp(argv[i], "--native") == 0) {
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

			doSet(selectionConf, install, profile, ctarget, makeDefault);
			if(saveSelectionConf(selectionConf, configDir, userProfile) != 0)
				die("Error saving config: %s", strerror(errno));
			break;

		case ACTION_UNSET:
			if(i+1 != argc)
				die("You did not provide a CTARGET to unset.");

			ctarget=argv[i];
			doUnSet(selectionConf, ctarget);
			if(saveSelectionConf(selectionConf, configDir, userProfile) != 0)
				die("Error saving config: %s", strerror(errno));
			break;
		default:
			die("No action selected.");
			break;
	}
	return 0;
}
