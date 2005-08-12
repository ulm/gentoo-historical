/*
 * C Implementation: gcc-wrapper
 *
 * Description: 
 * A wrapper for gcc which uses profiles stored in /etc/gcc-config to determine
 * which compiler to execute.
 *
 * Author: Jeremy Huddleston <eradicator@gentoo.org>
 *
 * Copyright 1999-2005 Gentoo Foundation
 * Distributed under the terms of the GNU General Public License v2
 * See COPYING file that comes with this distribution
 *
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/gcc-wrapper/Attic/gcc-wrapper.c,v 1.3 2005/08/12 10:07:59 eradicator Exp $
 * $Log: gcc-wrapper.c,v $
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
 * TODO:
 * Aliasing:
 *   gfortran = g77 = f77
 *   cc = gcc
 *   Include framework for icc to be used as well.
 */

/* For strdup() */
#define _GNU_SOURCE

#include <alloca.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/param.h>
#include <unistd.h>
#include "selection_conf.h"
#include "install_conf.h"

#define CONFIGURATION_FILE "/etc/gcc-config/selection.conf"

typedef struct {
	/* The CHOST being compiled for.  This is determined by $ABI (deprecated),
	 * the prefix of the executable, the environment ($CHOST), or the default
	 * set in the config file.
	*/
	char chost[MAXPATHLEN + 1];

	/* The basename of the executable we were called as without
	* the CHOST.  So if we call i686-pc-linux-gnu-gcc, this
	* would be gcc.
	*/
	char execBasename[MAXPATHLEN + 1];

	/* The full path name to the binary we're going to exec */
	char execBinary[MAXPATHLEN + 1];

	/* The argv to pass to the forked process */
	char **argv;

	SelectionConf *selectionConf;
	Profile *profile;
} WrapperData;

static void wrapperExit(char *msg, ...) {
	va_list args;
	fprintf(stderr, "gcc-config error: ");
	va_start(args, msg);
	vfprintf(stderr, msg, args);
	va_end(args);
	exit(1);
}

static char *abiFlags[] = {
	"-m32", "-m64", "-mabi", NULL
};

/** Prepend CFLAGS to the argv list */
static char **buildNewArgv(char **argv, const char *newFlagsStr) {
#define MAX_NEWFLAGS 32
	char *newFlags[MAX_NEWFLAGS];
	char **retargv;
	unsigned int argc, i;
	char *state, *flagsTokenized;

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
static void setChost(WrapperData *data) {
	char tmp[MAXPATHLEN + 1];
	unsigned i;

	/* Copy argv[0] to temp space, so we can modify it */
	strncpy(tmp, data->argv[0], MAXPATHLEN);

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
		wrapperExit("No gcc profile selected.");
	}
	return;
}

int main(int argc, char *argv[]) {
	WrapperData *data;
	char *extraCflags = NULL;

	data = (WrapperData *)alloca(sizeof(WrapperData));
	if(data == NULL)
		wrapperExit("%s wrapper: out of memory\n", argv[0]);

	/* Load the config file */
	data->selectionConf = loadSelectionConf(CONFIGURATION_FILE);
	if(data->selectionConf == NULL)
		wrapperExit("%s wrapper: out of memory\n", argv[0]);

	/* The argv to pass to the forked process.  Defaults to be the same */
	data->argv = argv;

	/* Figure out out CHOST */
	setChost(data);

	/* TODO: Figure out the basename of the compiler */
	/* TODO: Figure out the full path of the binary to execute */

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
		if(data->argv)
			wrapperExit("%s wrapper: out of memory\n", data->execBinary);
	}

	/* TODO: Select the appropriate GCC specs file */

	/* Set argv[0] to the correct binary (the full path
	 * of the binary we are executing), else gcc can't
	 * find internal headers
	 * http://bugs.gentoo.org/show_bug.cgi?id=8132
	 */
	data->argv[0] = data->execBinary;

	/* Ok, lets exec it. */
	if (execv(data->execBinary, data->argv) < 0)
		wrapperExit("Could not run/locate \"%s\"\n", data->execBinary);

	return 0;
}
