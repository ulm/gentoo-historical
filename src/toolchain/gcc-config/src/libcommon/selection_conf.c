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
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/selection_conf.c,v 1.2 2005/08/12 00:48:18 eradicator Exp $
 * $Log: selection_conf.c,v $
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

#include "selection_conf.h"
#include "install_conf.h"
#include <stdlib.h>

/** Allocate memory and load the configuration file */
SelectionConf *loadSelectionConf(const char *configFileName) {
	SelectionConf *retval;
	InstallConf *installConf;
	
#ifdef USE_HARDCODED_CONF
	/* Not production code... */
	retval = (SelectionConf *)malloc(sizeof(SelectionConf));
	retval->fileName = (char *)configFileName;
	retval->installHash = hashNew(10);
	retval->selectionHash = hashNew(10);

	installConf = loadInstallConf("/etc/gcc-config/x86_64-pc-linux-gnu-3.4.4.conf");
	hashInsert(retval->installHash, "x86_64-pc-linux-gnu-3.4.4", installConf);
	hashInsert(retval->selectionHash, "x86_64-pc-linux-gnu", hashGet(installConf->profileHash, "amd64-vanilla"));
	hashInsert(retval->selectionHash, "i686-pc-linux-gnu", hashGet(installConf->profileHash, "x86-vanilla"));
#else
	/* TODO: Read in config file */
#endif

	return retval;
}

/** Save the configuration file */
void saveSelectionConf(SelectionConf *config) {
	/* TODO: Save the configuration file */
	return;
}

/** Free selectionConf and its contents */
void freeSelectionConf(SelectionConf *selectionConf) {
	/* TODO: Worry about this once/if we need it. */
	if(!selectionConf)
		return;

	free(selectionConf);
}
