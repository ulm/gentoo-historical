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
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/selection_conf.h,v 1.12 2005/10/07 01:24:19 eradicator Exp $
 * $Log: selection_conf.h,v $
 * Revision 1.12  2005/10/07 01:24:19  eradicator
 * Ignore ABI environment variable by default.  Give option in selection.conf to not ignore it.
 *
 * Revision 1.11  2005/09/24 18:31:38  eradicator
 * Changed references to choat->ctarget.  Changed --default to --native.
 *
 * Revision 1.10  2005/09/24 05:47:13  eradicator
 * Added scan_path option (not yet implemented).  When enabled, the PATH envvar will be searched for the executable like it was in gcc-config-1.x
 *
 * Revision 1.9  2005/09/09 08:32:29  eradicator
 * Made selection config parsing callbacks.
 *
 * Revision 1.8  2005/08/26 19:55:06  sekretarz
 * Parsing global section code
 *
 * Revision 1.7  2005/08/23 02:54:09  eradicator
 * Changed 'gcc' references to 'compiler' since this is not gcc-specific.
 *
 * Revision 1.6  2005/08/23 02:00:39  eradicator
 * Added code to save the selection config.
 *
 * Revision 1.5  2005/08/23 00:57:36  eradicator
 * Let user config dir be configurable.
 *
 * Revision 1.4  2005/08/20 22:03:48  eradicator
 * Let users override settings in ~/.gcc-config.
 *
 * Revision 1.3  2005/08/12 09:45:52  eradicator
 * Added defaultCtarget.
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

#ifndef _COMPILER_CONFIG_SELECTION_CONF_H_
#define _COMPILER_CONFIG_SELECTION_CONF_H_

#include "hash.h"
#include "install_conf.h"

typedef struct {
	char *defaultCtarget;

	/* Set to 1 if the exec location code should search through the
	 * ${PATH} to find the executable before relying on the path in
	 * the config file.
	 */
	int scanPath;

	/* Set to 1 if you want to use ${ABI} and ${CFLAGS_${ABI}} if set
	 * rather than what is declared in the profile.
	 */
	int useABI;

	/* Hash table of selected profiles.
	 * Key: (char *) CTARGET (such as "i686-pc-linux-gnu")
	 * Value: (Profile *) Profile associated with CTARGET
	 */
	Hash *selectionHash;

	/* Hash table of installed gcc packages
	 * Key: (char *) name (such as "i686-pc-linux-gnu-3.4.4")
	 * Value: (InstallConf *) Profile associated with CTARGET
	 */
	Hash *installHash;
} SelectionConf;

/** Allocate memory and load the configuration in the globalConfigDir.
 *  If userOverride is non-zero, then we will let values in ~/.gcc-config
 *  override those in the globalConfigDir
 */
SelectionConf *loadSelectionConf(const char *globalConfigDir, unsigned userOverride);

/** Save the configuration file */
int saveSelectionConf(SelectionConf *config, const char *globalConfigDir, unsigned userOverride);

/** Free selectionConf and its contents */
void freeSelectionConf(SelectionConf *selectionConf);

#endif
