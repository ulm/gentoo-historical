/*
 * C Header: selection_conf
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
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/Attic/selection_conf.h,v 1.1 2005/08/09 10:42:31 eradicator Exp $
 * $Log: selection_conf.h,v $
 * Revision 1.1  2005/08/09 10:42:31  eradicator
 * Added framework for handling configuration files.
 *
 */

#ifndef _GCC_CONFIG_SELECTION_CONF_H_
#define _GCC_CONFIG_SELECTION_CONF_H_

#include "install_conf.h"
#include "hash.h"

typedef struct {
	char *fileName;

	/* Hash table of selected profiles.
	 * Key: (char *) CHOST (such as "i686-pc-linux-gnu")
	 * Value: (Profile *) Profile associated with CHOST
	 */
	Hash *selectionHash;

	/* Hash table of installed gcc packages
	 * Key: (char *) name (such as "i686-pc-linux-gnu-3.4.4")
	 * Value: (Install *) Profile associated with CHOST
	 */
	Hash *installHash;
} SelectionConf;

/** Allocate memory and load the configuration file */
SelectionConf *loadSelectionConf(const char *configFileName);

/** Save the configuration file */
void saveSelectionConf(SelectionConf *config);

/** Free selectionConf and its contents */
void freeSelectionConf(SelectionConf *selectionConf);

#endif
