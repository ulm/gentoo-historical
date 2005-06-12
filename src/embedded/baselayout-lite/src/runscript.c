/***************************************************************************
 *            /sbin/runscript
 *  baselayout-lite replacement for /sbin/runscript
 *      very limited functionality
 *      very small
 *		very crappy
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


#include "baselayout-lite.h"

char *find_dep(char *what);
int runscript(char *init_script, char *func_to_run);
int in_runlevel(char *script);
int find_alias(char *alias, char *script);

/*
 *	argv[0]: /sbin/runscript
 *	argv[1]: /etc/init.d/foo
 *	argv[2]: start|stop
 */
int main(int argc, char **argv) {
	char *line = NULL;
	char *word = NULL;
	FILE *init_script_FILE;

	/* if we don't have the right number of args, fail */
	if(argc < 3) {
		printf("Invalid number of arguments (%d: %s %s %s)\n",
			argc, argv[0], argv[1], argv[2]);
		exit(EXIT_FAILURE);
	}

	/* if we are stopping, just short circuit and stop the service. No need to
		worry about deps here, everything will get it's turn */
	/* FIXME: this may be a dep of another script, if we stop it now, the other
		one may get pissed off */
	if(strncmp(argv[2], "stop", 4)==0) {
		runscript(argv[1], argv[2]);
	}

	/* find the deps, and make sure all the right stuff is started first */
	init_script_FILE=fopen(argv[1], "r");
	if (init_script_FILE == NULL) {
		perror(argv[1]);
		fclose(init_script_FILE);
		exit(EXIT_FAILURE);
	}

	line=(void *)malloc(1000);
	memset(line, 0, 1000);

	while(fgets(line, 999, init_script_FILE)) {
		if(strstr(line, "\tneed ")) {
			/* these are non-optional deps that have to be started before */
			//printf("need: %s\n", line);
			word=strtok(line, " ");
			while((word=strtok(NULL, " ")) != NULL) {
				char *alias;
				char *dep = NULL;
				
				alias=malloc(1000);
				memset(alias, 0, 1000);
				
				if(word[strlen(word)-1] == '\n')
					word[strlen(word)-1]='\0';
				//printf("\tStarting required dep: \"%s\"\n", word);
				/* find the dep, and start it */
				asprintf(&dep, "%s%s", INIT_DIR, word);
				if((access(dep, F_OK)) == 0) {
					/* our dep exists already, start it */
					runscript(dep, argv[2]);
				}
			
				/* if we can't find a dep, it's likely because it's known as some
				 * other name, and it uses an alias... need to track it down
				 */
				/* FIXME: none of baselayout-lite uses alias'es, so fuck it for now */
			}
		} else if(strstr(line, "\tuse")) {
			/* optional deps that have to be started before if they are in RUNLEVEL_DIR */
			word=strtok(line, " ");
			while((word=strtok(NULL, " ")) != NULL) {
				char *dep = NULL;

				if(word[strlen(word)-1] == '\n')
					word[strlen(word)-1]='\0';
				if(in_runlevel(word) == FALSE)
					continue;
				//printf("\tStarting optional dep: \"%s\"\n", word);
				/* find the optional dep, and start it */
				asprintf(&dep, "%s%s", INIT_DIR, word);
				if((access(dep, F_OK)) == 0) {
					/* our dep exists already, start it */
					runscript(dep, argv[2]);
				}
				
				/* if we can't find a dep, it's likely because it's known as some
				 * other name, and it uses an alias... need to track it down
				 */
				/* FIXME: none of baselayout-lite uses alias'es, so fuck it for now */
			}
		}
	}
	fclose(init_script_FILE);
	free(line);
	free(word);
	
	/* now actually run what we are here for */
	runscript(argv[1], argv[2]);

	exit(EXIT_SUCCESS);
}

int runscript(char *init_script, char *func_to_run) {
	char *command = NULL;
	
	if(strncmp(func_to_run, "start", 5)==0) {
		if(is_started(init_script)==TRUE) {
			//printf("%s is already running\n", init_script);
			return 0;
		}
	} else if(strncmp(func_to_run, "stop", 4)==0) {
		if(is_started(init_script)==FALSE) {
			//printf("%s is already running\n", init_script);
			return 0;
		}
	}
	
	/* here we glue all the bits together
	 *	we source /sbin/functions.sh to get some common init script functions
	 *	we source the conf.d file
	 *	we source the script itself (init_script)
	 *	we run the funtion that the user has called for (func_to_run)
	 */
	asprintf(&command,
		"/bin/sh -c \". %s ; [ -e \"%s%s\" ] && . %s%s ; . %s ; %s\"",
		SHFUNCS,
		CONFD_DIR, basename(init_script),
		CONFD_DIR, basename(init_script),
		init_script, func_to_run);
	//printf("%s\n", command);

	printf("Starting %s\n", init_script);
	system(command);
	mark_started(basename(init_script));

	free(command);
	return 0;
}

/* need to look at alias names */
int in_runlevel(char *script) {
	int ret;
	DIR *rlvldir;
	struct dirent *svc_script;
	char *alias;
	
	rlvldir=opendir(RUNLEVEL_DIR);
	if (rlvldir == NULL) {
		perror(RUNLEVEL_DIR);
		return FALSE;
	}	

	while((svc_script=readdir(rlvldir)) != NULL) {
		if((ret=strncmp(".", svc_script->d_name, 1)) == 0)
			continue;
		if((ret=strcmp(svc_script->d_name, script)) == 0) {
			/* we have a match */
			return TRUE;
		}
		//printf("%s: %s-%s\n", __func__, script, svc_script->d_name);
		alias=malloc(1000);
		memset(alias, 0, 1000);
		if(find_alias(alias, script))
			printf("%s\n", alias);
		free(alias);

		//printf("%s==%s:%d\n", svc_script->d_name, script, ret);
	}
	return FALSE;

}

/* Find an init script that has an "alias $script" line
 *
 * work in INIT_DIR since what we need may not be in RUNLEVEL_DIR
 */
int find_alias(char *alias, char *script) {
	char *aliasline;
	DIR *initdir;
	struct dirent *svc_script;
	
	if ((initdir=opendir(INIT_DIR)) == NULL)
		return FALSE;

	while((svc_script=readdir(initdir)) != NULL) {
		char *line, *svc_script_path;
		FILE *svc_script_FILE;
		
		svc_script_path=(void *)malloc(1000);
		memset(svc_script_path, 0, 1000);

		snprintf(svc_script_path, 999, "%s%s", INIT_DIR, svc_script->d_name);
		svc_script_FILE=fopen(svc_script_path, "r");
		if (svc_script_FILE == NULL) {
			perror(svc_script_path);
			fclose(svc_script_FILE);
			closedir(initdir);
			return FALSE;
		}

		line=(void *)malloc(1000);
		memset(line, 0, 1000);

		while(fgets(line, 999, svc_script_FILE)) {
			if(strstr(line, "\talias ")) {
				/* we have an alias line, work with it */
				aliasline=strtok(line, " ");
				//printf("%s: %s\n", svc_script->d_name, aliasline);
				if(strcmp(aliasline, script) == 0) {
					strcpy(alias, aliasline);
					free(svc_script_path);
					free(line);
					fclose(svc_script_FILE);
					closedir(initdir);
					return TRUE;
				}
			}
		}
		free(svc_script_path);
		free(line);
		fclose(svc_script_FILE);
	}
	closedir(initdir);
	return FALSE;
}
