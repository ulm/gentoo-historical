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
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/parse_conf.h,v 1.2 2005/08/16 17:34:57 sekretarz Exp $
 * $Log: parse_conf.h,v $
 * Revision 1.2  2005/08/16 17:34:57  sekretarz
 * Adding new config framework
 *
 * Revision 1.1  2005/08/16 17:00:52  sekretarz
 * Adding working parser.
 *
 *
 */

#ifndef _GCC_CONFIG_PARSE_CONF_H_
#define _GCC_CONFIG_PARSE_CONF_H_

typedef struct {
	char *config_name;
	void *data;
	
	FILE *fp;
	/* Return 0 is everything is ok */
	int (*section_cb)(char * /* Section name */, void * /* data*/);
	int (*key_cb)(char * /* key */, char * /* value */, void * /*data*/);
	
} configParser;

void trim(char *s);
int parseFile(configParser *parser);
configParser *newParser(char *config_name);
void freeParser(configParser *parser);
void setParserCallback(configParser *parser, int (*section_cb)(char * /* Section name */, void * /* data*/), int (*key_cb)(char * /* key */, char * /* value */, void * /*data*/));


#endif /* _GCC_CONFIG_PARSE_CONF_H_ */

