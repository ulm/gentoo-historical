/***************************************************************************
 *            /sbin/rc
 *	baselayout-lite replacement for /sbin/rc
 *		very limited functionality
 *		very small
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
 
/*
 * TODO: everything
 *
 *
 *
 *
 *
 *
 */

#include "baselayout-lite.h"

int is_started(char *script);
int mark_started(char *script);


/*
 * argv[1] - runlevel (either sysinit or shutdown)
 *
 */
int main(int argc, char **argv) {
	int ret;
	DIR *rlvldir;
	struct dirent *svc_script;
	
	if(argc != 2) {
		fprintf(stderr, "Wrong number of args\nIt's best to let init handle this\n");
		exit(1);
	}

	//printf("Entering runlevel %s\n", argv[1]);
	
	
	/* we only support 1 runlevel dir for boot+shutdown, so resolve deps for that
	   dir then do stuff */
	if ((rlvldir=opendir(RUNLEVEL_DIR)) == NULL) {
		perror(RUNLEVEL_DIR);
		exit(EXIT_FAILURE);
	}
	while((svc_script=readdir(rlvldir)) != NULL) {
		FILE *f1;
		char path[500];
		char line[500];
		
		if((ret=strncmp(".", svc_script->d_name, 1)) == 0)
			continue;
		//printf("%s\n", svc_script->d_name);
		snprintf(path, sizeof(path)-1, "%s/%s", RUNLEVEL_DIR, svc_script->d_name);
		//printf("%s\n", path);
		if ((f1=fopen(path, "r")) == NULL) {
			perror(path);
			exit(EXIT_FAILURE);
		}
		
		while(fgets(line, sizeof(line)-1, f1)) {
			if(strstr(line, "before *")) {
				mark_started(svc_script->d_name);
			}
		}
		//printf("%d\n", __LINE__);
	}
	
	//printf("%d\n", __LINE__);
	/* We've started what should be the first thing, now we need to start
	 * everything else. We will start off in the order that readdir gives them
	 * to us, and hope to hell that runscript does the right thing */
	rewinddir(rlvldir);
	//printf("%d\n", __LINE__);
	while((svc_script=readdir(rlvldir)) != NULL) {
		//printf("rewind: %s\n", svc_script->d_name);
		if((ret=strncmp(".", svc_script->d_name, 1)) == 0)
			continue;
		if(is_started(svc_script->d_name) == TRUE)
			continue;
		else {
			mark_started(svc_script->d_name);
		}
	}
	return 0;
}

int mark_started(char *script) {
	int ret;
	char *command = NULL;
	char *init_script = NULL;
	//char *cmdline[] = { NULL, "start", 0 };

	/* start everything with "before *", and mark it as started */
	//printf("Starting %s\n", script);

	asprintf(&init_script, "%s%s", INIT_DIR, script);
	asprintf(&command, "%s%s start", INIT_DIR, script);
	//cmdline[0]=command;
	//printf("%d: %s %s %s %s\n",
	//	__LINE__, cmdline[0], cmdline[1], cmdline[2], cmdline[3]);
	/* so we can get return values and decide if we should call mark_started() */
	if ((ret=system(command)) == 0) {
		//printf("%d\n", __LINE__);
		//printf("%s: Succesfully started %s\n", __func__, script);
		mkdir("/var/lib/", 0755);
		mkdir("/var/lib/init.d/", 0755);
		mkdir("/var/lib/init.d/started/", 0755);
		chdir("/var/lib/init.d/started/");
		symlink(init_script, basename(script));
		free(command);
		return TRUE;
	}
	//printf("%d\n", __LINE__);
	printf("Failed to start %s (%s)(return value=%d)\n", script, strerror(errno), ret);
	free(command);
	return FALSE;
}
