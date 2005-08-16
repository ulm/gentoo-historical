/*
 * C Implementation: parse_conf
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
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/parse_conf.c,v 1.1 2005/08/16 17:00:52 sekretarz Exp $
 * $Log: parse_conf.c,v $
 * Revision 1.1  2005/08/16 17:00:52  sekretarz
 * Adding working parser.
 *
 *
 */


#include <stdio.h>
#include <string.h>
#include <malloc.h>
#include "parse_conf.h"

/* Trim spaces, tabs and comments */
void trim(char *s)
{
	char *tmp;
	
	/* Trim spaces and tabs from beginning */
	int i=0,j;
	while((s[i]==' ')||(s[i]=='\t')) {
		i++;
	}

	if(i>0) {
		for(j=0;j<strlen(s);j++) {
			s[j]=s[j+i];
		}
		s[j]='\0';
	}
	/* Remove all comments if any exists */
	tmp = strchr(s, '#');
	if (tmp != NULL)
		tmp[0] = '\0';

	/* Trim spaces and tabs from end */
	i=strlen(s)-1;
	while((s[i]==' ')||(s[i]=='\t')) {
		i--;
	}

	if(i<(strlen(s)-1)) {
    		s[i+1]='\0';
	}
}

void getLine(char *line, int n, FILE *fp)
{
	line[0] = '\0';
	while ( (line[0] == '\0') || (line[0] == '#') ) {
		if ( fgets(line, n, fp) == NULL) {
		    line[0]='\0';
		    break;
		}
		
		/* Remove \n on the end of string */
		if (line[strlen(line)-1] == '\n') {
			line[strlen(line)-1] = '\0';
		}
	
		/* Clean that string */	
		trim(line);
	}
}

int _parseFile(configParser *parser)
{
	char line[256];
	char value[192];
	char tag[64];
	int ret;
	
	while (!feof(parser->fp)) {
		getLine(line, 255, parser->fp);
		if (line[0] == '\0') continue; /* last line */ 
		if (sscanf(line, "[%99[^]]]",value) == 1) {
			if ( (ret = (parser->section_cb)(value, parser->data)) != 0) 
				return ret;
		} else if (sscanf(line, " %63[^= ] = %191[^\n]",tag, value) == 2) {
			if ( (ret = (parser->key_cb)(tag,value, parser->data)) != 0) {
				return ret;
			}
		} else {
			printf("syntax error");
			return 3;
		}
	}
    return 0;
}

int parseFile(configParser *parser)
{
	int ret;
	
	parser->fp = fopen(parser->config_name, "r");
	
	if (parser->fp == NULL) {
		printf("Can't open file");
		return 1;
	}
	
	ret = _parseFile(parser);
	
	fclose(parser->fp);
	return ret;
}

configParser *newParser(char *config_name)
{
	configParser *tmp;

	tmp = (configParser *)malloc(sizeof(configParser));
	tmp->config_name = strdup(config_name);	
	tmp->data = (void *)0;
	return tmp;
}

void freeParser(configParser *parser)
{
	free(parser->config_name);
	free(parser);
}

void setParserData(configParser *parser, void *data)
{
	parser->data = data;
}

void setParserCallback(configParser *parser, int (*section_cb)(char * /* Section name */, void * /* data*/), int (*key_cb)(char * /* key */, char * /* value */, void * /*data*/))
{
	parser->section_cb = section_cb;
	parser->key_cb = key_cb;
}

#define DEBUG_PARSE
#ifdef DEBUG_PARSE

int section_cb(char *section, void *data)
{
	printf("Section_db:\n\t%s\nData_address:\n\t%p\n", section, data);
	return 0;
}

int key_cb(char *key, char *value, void *data)
{
	printf("key_cb:\nkey: %s\nvalue: %s\ndata_address: %p\n", key, value, data);
	return 0;
}

int main(void)
{
	char *dup = (char *)malloc(sizeof(char)*50);
	
	configParser *config = newParser("i686-pc-linux-gnu-3.4.4.conf");
	setParserData(config, dup);
	setParserCallback(config, section_cb, key_cb);
	
	
	printf("Start programu\n");
    	parseFile(config);
	
	freeParser(config);
	
	return 0;
}

#endif /* DEBUG_PARSE */

