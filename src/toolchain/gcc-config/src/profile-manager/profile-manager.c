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
 *     GCC_CONFIG_DEFAULT_CHOST:
 *       The default CHOST
 *     GCC_CONFIG_ALL_CHOSTS:
 *       A list of all CHOSTS for which a profile is available
 *     GCC_CONFIG_INSTALLED_CHOSTS:
 *       All CHOSTS for which a profile is installed.  Note that there might
 *       be a CHOST here which is not in GCC_CONFIG_ALL_CHOSTS because the
 *       user has used the --chost option to choose a non-default CHOST.
 *     GCC_CONFIG_PROFILES_<CHOST/-/_>:
 *       A list of available profiles for the given CHOST.  The list is space
 *       delimeted with a forward slash between the install and profile.
 *     GCC_CONFIG_SELECTED_<CHOST/-/_>:
 *       The selected <install>/<profile> for the given CHOST.
 *
 *   get-profile <install>/<profile>
 *     get a set of environment variables (to be eval'd) with the data for the
 *     given profile
 *
 *     GCC_CONFIG_BINPATH
 *     GCC_CONFIG_MANPATH
 *     GCC_CONFIG_INFOPATH
 *     GCC_CONFIG_LDPATH
 *     GCC_CONFIG_CHOST
 *     GCC_CONFIG_GCC_SPECS
 *     GCC_CONFIG_CFLAGS
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
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/profile-manager/Attic/profile-manager.c,v 1.3 2005/08/21 20:38:50 eradicator Exp $
 * $Log: profile-manager.c,v $
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

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "selection_conf.h"

#ifndef MAXPATHLEN
#define MAXPATHLEN 1023
#endif

#define ACTION_NONE          0
#define ACTION_GET_PROFILES  1
#define ACTION_GET_PROFILE   2
#define ACTION_SET           3

static void die(const char *msg, ...) {
	va_list args;
	fprintf(stderr, "profile-manager error: ");
	va_start(args, msg);
	vfprintf(stderr, msg, args);
	va_end(args);
	exit(1);
}

static void doGetProfiles() {
	
}

static void doGetProfile(const char *install, const char *profile) {
	
}

/* If CHOST is null, we use the default chost for the profile */
static void doSet(const char *install, const char *profile, const char *chost) {
	
}

int main(int argc, char **argv) {
	SelectionConf *selectionConf;
	unsigned action = ACTION_NONE;
	size_t i;
	unsigned userProfile = 0;
	const char *configDir = CONFIGURATION_DIR;
	const char *chost = NULL;
	const char *install = NULL;
	const char *profile = NULL;

	for(i=1; i < argc; i++) {
		if(strcmp(argv[i], "-u") == 0) {
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
			doGetProfiles();
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
			profile++;

			doGetProfile(install, profile);
			break;

		case ACTION_SET:
			for(; i < argc; i++) {
				if(strncmp(argv[i], "--chost=", 8) == 0) {
					chost = argv[i] + 8;
				} else {
					/* Find the split */
					install = argv[i];
					for(profile = install; *profile != '\0' && *profile != '/' && profile - install < MAXPATHLEN; profile++);
					if(*profile == '\0' || profile - install == MAXPATHLEN)
						die("There was no / in the profile given");
					profile++;
				}
			}

			if(!install)
				die("You did not give a profile to set.");

			doSet(install, profile, chost);
			break;

		default:
			die("No action selected.");
			break;
	}
	return 0;
}
