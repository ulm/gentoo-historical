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

	printf("Entering runlevel %s\n", argv[1]);
	
	
	/* we only support 1 runlevel dir for boot+shutdown, so resolve deps for that
	   dir then do stuff */
	rlvldir=opendir(RUNLEVEL_DIR);
	while((svc_script=readdir(rlvldir)) != NULL) {
		FILE *f1;
		char path[500];
		char line[500];
		char *command;
		
		command=(void *)malloc(1000);
		memset(command, 0, 1000);
		
		if((ret=strncmp(".", svc_script->d_name, 1)) == 0)
			continue;
		//printf("%s\n", svc_script->d_name);
		sprintf(path, "%s/%s", RUNLEVEL_DIR, svc_script->d_name);
		//printf("%s\n", path);
		f1=fopen(path, "r");
		while(fgets(line, 499, f1)) {
			if(strstr(line, "before *")) {
				/* start everything with "before *", and mark it as started */
				printf("Starting %s\n", svc_script->d_name);
				snprintf(command, 999, "%s%s start", INIT_DIR, svc_script->d_name);
				system(command);
				
				mark_started(svc_script->d_name);
			}
		}
	}
	/* We've started what should be the first thing, now we need to start
	 * everything else. We will start off in the order that readdir gives them
	 * to us, and hope to hell that runscript does the right thing */
	rewinddir(rlvldir);
	while((svc_script=readdir(rlvldir)) != NULL) {
		if((ret=strncmp(".", svc_script->d_name, 1)) == 0)
			continue;
		if(is_started(svc_script->d_name) == TRUE)
			continue;
		else {
			char *command;
			command=(void *)malloc(1000);
			memset(command, 0, 1000);
			snprintf(command, 999, "%s%s start", INIT_DIR, svc_script->d_name);
			system(command);
			mark_started(svc_script->d_name);
		}
	}
	return 0;
}

int mark_started(char *script) {
	return FALSE;
}

int is_started(char *script) {
	return FALSE;
}
