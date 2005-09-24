/*
 * C Header: parse_conf
 *
 * Description: 
 * C code for dealing with ini-like config files
 *
 * Author: Karol Wojtaszek <sekretarz@gentoo.org>
 *
 * Copyright 1999-2005 Gentoo Foundation
 * Distributed under the terms of the GNU General Public License v2
 * See COPYING file that comes with this distribution
 *
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/parse_conf.h,v 1.8 2005/09/24 09:18:05 eradicator Exp $
 * $Log: parse_conf.h,v $
 * Revision 1.8  2005/09/24 09:18:05  eradicator
 * Cleaned up error handling in the config file parsing.
 *
 * Revision 1.7  2005/09/09 02:34:21  eradicator
 * Added comment about return value of callbacks.
 *
 * Revision 1.6  2005/08/23 02:54:09  eradicator
 * Changed 'gcc' references to 'compiler' since this is not gcc-specific.
 *
 * Revision 1.5  2005/08/19 06:08:55  eradicator
 * Added headers to EXTRA_DIST.
 *
 * Revision 1.4  2005/08/18 23:30:24  eradicator
 * Coding style changes to make consistent with the rest of the codebase.  Whitespace cleanup.  Made some functions static.
 *
 * Revision 1.3  2005/08/16 17:44:46  sekretarz
 * *** empty log message ***
 *
 * Revision 1.2  2005/08/16 17:34:57  sekretarz
 * Adding new config framework
 *
 * Revision 1.1  2005/08/16 17:00:52  sekretarz
 * Adding working parser.
 *
 *
 */

#ifndef _COMPILER_CONFIG_PARSE_CONF_H_
#define _COMPILER_CONFIG_PARSE_CONF_H_

#include <stdio.h>

/* Handled internally */
typedef struct _ConfigParser ConfigParser;

/* The return value should be 0 on success.  If the return value is negative,
 * it is propegated back as the return value of parseFile()
 */
typedef int (*SectionCB)(const char * /* Section name */, void * /* data*/);
typedef int (*KeyCB)(const char * /* key */, const char * /* value */, void * /*data*/);

int parseFile(ConfigParser *parser);
ConfigParser *parserNew(const char *filename);
void parserSetData(ConfigParser *parser, void *data);
void parserFree(ConfigParser *parser);
void parserSetCallback(ConfigParser *parser, SectionCB sectionCB, KeyCB keyCB);

#endif /* _COMPILER_CONFIG_PARSE_CONF_H_ */
