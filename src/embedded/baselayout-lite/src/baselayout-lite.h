/***************************************************************************
 *  header for baselayout-lite
 *
 *  Sat Feb 12 12:14:34 2005
 *  Copyright  2005  Gentoo Foundation
 *  Email <iggy@gentoo.org>
 ****************************************************************************/

/*
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Library General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 */


#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <dirent.h>
#include <unistd.h>
#include <errno.h>

#define CONFD_DIR "/etc/conf.d/"
#define INIT_DIR "/etc/init.d/"
#define RUNLEVEL_DIR "/etc/runlevels/default"
//#define RUNLEVEL_DIR "/tmp/runlevels/default"
#define SHFUNCS "/sbin/functions.sh"

#ifndef TRUE
#define TRUE 1
#endif
#ifndef FALSE
#define FALSE 0
#endif


int is_started(char *script);
int mark_started(char *script);
int start_script(char *script);
