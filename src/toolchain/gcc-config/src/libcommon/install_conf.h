/*
 * C Header: install_conf
 *
 * Description: 
 * C Code for handling the configuration files for each gcc install
 *
 * Author: Jeremy Huddleston <eradicator@gentoo.org>
 *
 * Copyright 1999-2005 Gentoo Foundation
 * Distributed under the terms of the GNU General Public License v2
 * See COPYING file that comes with this distribution
 *
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/install_conf.h,v 1.13 2005/09/30 19:35:54 eradicator Exp $
 * $Log: install_conf.h,v $
 * Revision 1.13  2005/09/30 19:35:54  eradicator
 * Added stdcxx_incdir.  Cleaned up some possible memory problems.
 *
 * Revision 1.12  2005/09/24 18:31:38  eradicator
 * Changed references to choat->ctarget.  Changed --default to --native.
 *
 * Revision 1.11  2005/09/09 07:59:08  eradicator
 * No longer exposing parsing internals in the InstallConf struct.
 *
 * Revision 1.10  2005/08/25 21:08:28  sekretarz
 * Coded callbacks function. Still untested.
 *
 * Revision 1.9  2005/08/25 21:04:13  eradicator
 * Added currentProfile for use in parsing the config file.
 *
 * Revision 1.8  2005/08/23 02:54:09  eradicator
 * Changed 'gcc' references to 'compiler' since this is not gcc-specific.
 *
 * Revision 1.7  2005/08/20 22:03:48  eradicator
 * Let users override settings in ~/.gcc-config.
 *
 * Revision 1.6  2005/08/18 23:30:24  eradicator
 * Coding style changes to make consistent with the rest of the codebase.  Whitespace cleanup.  Made some functions static.
 *
 * Revision 1.5  2005/08/16 17:44:46  sekretarz
 * *** empty log message ***
 *
 * Revision 1.4  2005/08/16 17:34:57  sekretarz
 * Adding new config framework
 *
 * Revision 1.3  2005/08/12 23:10:24  eradicator
 * Added wrapperAliases.  Set missing installConf in hardcoded test configuration.
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

#ifndef _COMPILER_CONFIG_INSTALL_CONF_H_
#define _COMPILER_CONFIG_INSTALL_CONF_H_

#include "hash.h"
#include "parse_conf.h"

typedef struct {
	/* This is the same as the filename for the configuration.  It
	 * should be the basename of the conf file without the trailing .conf
	 */
	char *name;

	/* Information shared by all profiles */
	char *binpath;
	char *infopath;
	char *manpath;
	char *stdcxx_incdir;

	/* Hash table of profiles provided by this install
	 * Key: (char *) name (such as "x86-vanilla")
	 * Value: (Profile *) Profile associated with this profile name
	 */
	Hash *profileHash;

	/* Hash table of executable aliases.
	 * Key: (char *) name (such as "cc" or "g77")
	 * Value: (char *) binary to execute instead (such as "gcc" or "gfortran")
	 */
	Hash *wrapperAliases;
} InstallConf;

typedef struct {
	InstallConf *installConf;

	char *name;
	char *ctarget;
	char *specs;
	char *libdir;
	char *cflags;
} Profile;

/** Allocate memory and load the configuration file */
InstallConf *loadInstallConf(const char *filename);

/** Free installConf and its contents */
void freeInstallConf(InstallConf *installConf);

#endif
