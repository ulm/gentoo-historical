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
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/selection_conf.c,v 1.1 2005/08/09 20:15:46 eradicator Exp $
 * $Log: selection_conf.c,v $
 * Revision 1.1  2005/08/09 20:15:46  eradicator
 * Moving components into subdirs to make build environment more tidy.
 *
 * Revision 1.1  2005/08/09 10:42:31  eradicator
 * Added framework for handling configuration files.
 *
 */

#include "selection_conf.h"

/** Allocate memory and load the configuration file */
SelectionConf *loadSelectionConf(const char *configFileName) {
	return (SelectionConf *)0;
}

/** Save the configuration file */
void saveSelectionConf(SelectionConf *config) {
	return;
}

/** Free selectionConf and its contents */
void freeSelectionConf(SelectionConf *selectionConf) {
	if(!selectionConf)
		return;

	free(selectionConf);
}
