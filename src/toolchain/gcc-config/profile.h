/*
 * C Header: profile
 *
 * Description: 
 * C Code for handling each gcc profile, including forking the process to
 * this profile.
 *
 * Author: Jeremy Huddleston <eradicator@gentoo.org>
 *
 * Copyright 1999-2005 Gentoo Foundation
 * Distributed under the terms of the GNU General Public License v2
 * See COPYING file that comes with this distribution
 *
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/Attic/profile.h,v 1.1 2005/08/09 10:42:31 eradicator Exp $
 * $Log: profile.h,v $
 * Revision 1.1  2005/08/09 10:42:31  eradicator
 * Added framework for handling configuration files.
 *
 */

#ifndef _GCC_CONFIG_PROFILE_H_
#define _GCC_CONFIG_PROFILE_H_

typedef struct {
	char *name;
	char *chost;
	char *specs;
	char *libdir;
	char *cflags;
} Profile;

#endif
