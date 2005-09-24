/*
 * C Implementation: compiler-wrapper
 *
 * Description: 
 * A wrapper for gcc or any other compiler which executes a binary based on the profile
 * used for the set CHOST.
 *
 * Author: Jeremy Huddleston <eradicator@gentoo.org>
 *
 * Copyright 1999-2005 Gentoo Foundation
 * Distributed under the terms of the GNU General Public License v2
 * See COPYING file that comes with this distribution
 *
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/compiler-wrapper/Attic/compiler-wrapper.c,v 1.2 2005/09/24 06:07:59 eradicator Exp $
 * $Log: compiler-wrapper.c,v $
 * Revision 1.2  2005/09/24 06:07:59  eradicator
 * Honor GCC_SPECS envvar if it's already set.  Also, search through PATH first when locating the executable if scan_path is set in the config file.
 *
 * Revision 1.1  2005/08/23 02:55:04  eradicator
 * Moved compiler-wrapper from gcc-wrapper.
 *
 * Revision 1.10  2005/08/23 02:39:30  eradicator
 * Making error messages consistant.
 *
 * Revision 1.9  2005/08/21 03:52:16  eradicator
 * A couple portability fixes...
 *
 * Revision 1.8  2005/08/20 22:46:35  eradicator
 * Made the global configuration directory configurable.
 *
 * Revision 1.7  2005/08/20 22:03:48  eradicator
 * Let users override settings in ~/.gcc-config.
 *
 * Revision 1.6  2005/08/19 03:35:29  eradicator
 * Cleaned up #include lines and added #include config.h.
 *
 * Revision 1.5  2005/08/18 23:19:28  eradicator
 * Added layout to begin working on the profile manager.
 *
 * Revision 1.4  2005/08/12 23:08:26  eradicator
 * Added code to determine the binary we need to execute including aliasing in the profile.  Set GCC_SPECS based on the profile.
 *
 * Revision 1.3  2005/08/12 10:07:59  eradicator
 * setChost() also sets the profile.
 *
 * Revision 1.2  2005/08/12 09:57:12  eradicator
 * Initial work on the new wrapper...
 *
 * Initial revision is the same as ${FILESDIR}/wrapper-1.4.7.c, so we have historical reference.
 * This initial version was written primarily by Martin Schlemmer <azarah@gentoo.org>,
 * Mike Frysinger <vapier@gentoo.org>, and Jeremy Huddleston <eradicator@gentoo.org>
 *
 */

/* For strndup() */
#define _GNU_SOURCE

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <alloca.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/param.h>
#include <sys/stat.h>
#include <unistd.h>

#include "selection_conf.h"
#include "install_conf.h"

#ifndef MAXPATHLEN
#define MAXPATHLEN 1023
#endif

typedef struct {
	/* The CHOST being compiled for.  This is determined by $ABI (deprecated),
	 * the prefix of the executable, the environment ($CHOST), or the default
	 * set in the config file.
	*/
	char chost[MAXPATHLEN + 1];

	/* The full path name to the binary we're going to exec */
	char execBinary[MAXPATHLEN + 1];

	/* The argv to pass to the forked process */
	char **argv;

	SelectionConf *selectionConf;
	Profile *profile;
	Hash *wrapperAliases;
} WrapperData;

static void die(char *msg, ...) {
	va_list args;
	fprintf(stderr, "gcc-config error: ");
	va_start(args, msg);
	vfprintf(stderr, msg, args);
	va_end(args);
	fputc('\n', stderr);
	exit(1);
}

/** Prepend CFLAGS to the argv list */
static char **buildNewArgv(char **argv, const char *newFlagsStr) {
#define MAX_NEWFLAGS 32
	char *newFlags[MAX_NEWFLAGS];
	char **retargv;
	unsigned int argc;
	size_t i;
	char *state, *flagsTokenized;

	/* Don't modify argv if we see any of these flags */
	const char *abiFlags[] = {
		"-m32", "-m64", "-mabi", NULL
	};

	retargv = argv;

	/* make sure user hasn't specified any ABI flags already ...
	 * if they have, lets just get out of here */
	for (argc = 0; argv[argc]; ++argc)
		for (i = 0; abiFlags[i]; ++i)
			if (!strncmp(argv[argc], abiFlags[i], strlen(abiFlags[i])))
				return retargv;

	/* Tokenize the flag list and put it into newflags array */
	flagsTokenized = strdup(newFlagsStr);
	if (flagsTokenized == NULL)
		return retargv;
	i = 0;
	newFlags[i] = strtok_r(flagsTokenized, " \t\n", &state);
	while (newFlags[i] != NULL && i < MAX_NEWFLAGS-1)
		newFlags[++i] = strtok_r(NULL, " \t\n", &state);

	/* allocate memory for our spiffy new argv */
	retargv = (char**)calloc(argc + i + 1, sizeof(char*));
	/* start building retargv */
	retargv[0] = argv[0];
	/* insert the ABI flags first so cmdline always overrides ABI flags */
	memcpy(retargv+1, newFlags, i * sizeof(char*));
	/* copy over the old argv */
	if (argc > 1)
		memcpy(retargv+1+i, argv+1, (argc-1) * sizeof(char*));

	return retargv;
}

/** Set the chost and profile */
static void setChostAndProfile(WrapperData *data) {
	char tmp[MAXPATHLEN + 1];
	size_t i;

	/* Copy argv[0] to temp space, so we can modify it */
	strncpy(tmp, basename(data->argv[0]), MAXPATHLEN);

	/* Start at the end and go back until we find a prefix that matches */
	for(i = strlen(tmp); i > 0; i--) {
		if(tmp[i] == '-') {
			tmp[i] = '\0';
			if((data->profile = hashGet(data->selectionConf->selectionHash, tmp)) != NULL) {
				strcpy(data->chost, tmp);
				return;
			}
		}
	}

	/* We didn't find a match, so see if we have ${CHOST} set. */
	if(getenv("CHOST") != NULL) {
		if((data->profile = hashGet(data->selectionConf->selectionHash, getenv("CHOST"))) != NULL) {
			strncpy(data->chost, getenv("CHOST"), MAXPATHLEN);
			return;
		}
	}

	/* No match, use the default */
	strncpy(data->chost, data->selectionConf->defaultChost, MAXPATHLEN);
	if((data->profile = hashGet(data->selectionConf->selectionHash, data->chost)) == NULL) {
		die("%s wrapper: Could not determine CHOST or CHOST has no selected profile.", data->argv[0]);
	}
	return;
}

/** Determine what binary we will be executing. */
static void setExecBinary(WrapperData *data) {
	char execBasename[MAXPATHLEN + 1];
	const char *tmp;
	struct stat sbuf;

	/* Figure out the basename of the compiler */
	strncpy(execBasename, basename(data->argv[0]), MAXPATHLEN);

	/* If it's prefixed by ${CHOST}, strip that off */
	if(!strncmp(data->chost, execBasename, strlen(data->chost)) &&
	   execBasename[strlen(data->chost)] == '-' ) {
		strcpy(execBasename, execBasename + strlen(data->chost) + 1);
	}

	/* If it's an alias, replace it with the correct value */
	tmp = hashGet(data->profile->installConf->wrapperAliases, execBasename);
	if(tmp != NULL)
		strcpy(execBasename, (const char *)tmp);

	/* First we try scanning out ${PATH} for a match */
	if((data->selectionConf->scanPath != 0) && (getenv("PATH") != NULL)) {
		char *token = NULL, *state;
		char path[MAXPATHLEN + 1];

		strncpy(path, getenv("PATH"), MAXPATHLEN);

		token = strtok_r(path, ":", &state);
		while ((token != NULL) && strlen(token)) {
			snprintf(data->execBinary, MAXPATHLEN, "%s/%s", token, execBasename);
			if(stat(data->execBinary, &sbuf) == 0 && ((sbuf.st_mode & S_IFREG) || (sbuf.st_mode & S_IFLNK)) &&
			   strcmp(data->execBinary, data->argv[0]) != 0 && strstr(data->execBinary, "/gcc-bin/") != 0 )
				return;

			/* Check the next one */
			token = strtok_r(NULL, ":", &state);
		}
	}
	
	/* Fisrt try without the CHOST prefix */
	snprintf(data->execBinary, MAXPATHLEN, "%s/%s", data->profile->installConf->binpath, execBasename);
	if(stat(data->execBinary, &sbuf) == 0 && ((sbuf.st_mode & S_IFREG) || (sbuf.st_mode & S_IFLNK)))
		return;

	/* Now try with the CHOST prefix used */
	snprintf(data->execBinary, MAXPATHLEN, "%s/%s-%s", data->profile->installConf->binpath, data->chost, execBasename);
	if(stat(data->execBinary, &sbuf) == 0 && ((sbuf.st_mode & S_IFREG) || (sbuf.st_mode & S_IFLNK)))
		return;

	/* Now try with the CHOST prefix in the profile */
	snprintf(data->execBinary, MAXPATHLEN, "%s/%s-%s", data->profile->installConf->binpath, data->profile->chost, execBasename);
	if(stat(data->execBinary, &sbuf) == 0 && ((sbuf.st_mode & S_IFREG) || (sbuf.st_mode & S_IFLNK)))
		return;

	die("%s wrapper: Unable to determine executable.\n\tCHOST=%s\n\texec=%s\n", data->argv[0], data->chost, execBasename);
}

int main(int argc, char *argv[]) {
	WrapperData *data;
	char *extraCflags = NULL;
	
	data = (WrapperData *)alloca(sizeof(WrapperData));
	if(data == NULL)
		die("Memory allocation failure.");

	/* Load the config file */
	data->selectionConf = loadSelectionConf(CONFIGURATION_DIR, 1);
	if(data->selectionConf == NULL)
		die("Memory allocation failure.");

	/* The argv to pass to the forked process.  Defaults to be the same */
	data->argv = argv;

	/* Figure out out CHOST and our Profile */
	setChostAndProfile(data);

	/* Determine what binary we will be executing */
	setExecBinary(data);

	/* Do we need to set any additional CFLAGS? */
	if(getenv("ABI")) {
		/* This functionality is deprecated and subject to be removed
		 * once all profiles in portage nolonger depend on it.
		 */
		char envvar[65];
		snprintf(envvar, sizeof(envvar), "CFLAGS_%s", getenv("ABI"));

		if (getenv(envvar))
			extraCflags = getenv(envvar);
	} else {
		extraCflags = ((Profile *)hashGet(data->selectionConf->selectionHash, data->chost))->cflags;
	}

	if(extraCflags) {
		data->argv = buildNewArgv(data->argv, extraCflags);
		if(data->argv == NULL)
			die("Memory allocation failure.");
	}

	/* Select the appropriate GCC specs file */
	if(data->profile->specs && getenv("GCC_SPECS") == NULL)
		setenv("GCC_SPECS", data->profile->specs, 1);

	/* Set argv[0] to the correct binary (the full path
	 * of the binary we are executing), else gcc can't
	 * find internal headers
	 * http://bugs.gentoo.org/show_bug.cgi?id=8132
	 */
	data->argv[0] = data->execBinary;

	/* Ok, lets exec it. */
	if (execv(data->execBinary, data->argv) < 0)
		die("Could not run/locate \"%s\"", data->execBinary);

	return 0;
}
