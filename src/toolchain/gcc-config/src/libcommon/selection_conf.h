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
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/selection_conf.h,v 1.5 2005/08/23 00:57:36 eradicator Exp $
 * $Log: selection_conf.h,v $
 * Revision 1.5  2005/08/23 00:57:36  eradicator
 * Let user config dir be configurable.
 *
 * Revision 1.4  2005/08/20 22:03:48  eradicator
 * Let users override settings in ~/.gcc-config.
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

#ifndef _GCC_CONFIG_SELECTION_CONF_H_
#define _GCC_CONFIG_SELECTION_CONF_H_

#include "hash.h"

typedef struct {
	char *defaultChost;

	/* Hash table of selected profiles.
	 * Key: (char *) CHOST (such as "i686-pc-linux-gnu")
	 * Value: (Profile *) Profile associated with CHOST
	 */
	Hash *selectionHash;

	/* Hash table of installed gcc packages
	 * Key: (char *) name (such as "i686-pc-linux-gnu-3.4.4")
	 * Value: (InstallConf *) Profile associated with CHOST
	 */
	Hash *installHash;
} SelectionConf;

/** Allocate memory and load the configuration in the globalConfigDir.
 *  If userOverride is non-zero, then we will let values in ~/.gcc-config
 *  override those in the globalConfigDir
 */
SelectionConf *loadSelectionConf(const char *globalConfigDir, unsigned userOverride);

/** Save the configuration file */
void saveSelectionConf(SelectionConf *config, const char *globalConfigDir, unsigned userOverride);

/** Free selectionConf and its contents */
void freeSelectionConf(SelectionConf *selectionConf);

#endif
