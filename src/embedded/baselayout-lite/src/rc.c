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
	
	/* we could possibly have a mess left over from last boot */
	/* FIXME there's got to be a better way */
	system("mount -o remount /");
	system("rm -rf /var/lib/init.d/started/*");
	system("mount -o remount,ro /");
	
	while((svc_script=readdir(rlvldir)) != NULL) {
		FILE *f1;
		char path[500];
		char line[500];
		
		if((ret=strncmp(".", svc_script->d_name, 1)) == 0)
			continue;
		snprintf(path, sizeof(path)-1, "%s/%s", RUNLEVEL_DIR, svc_script->d_name);
		if ((f1=fopen(path, "r")) == NULL) {
			perror(path);
			fclose(f1);
			exit(EXIT_FAILURE);
		}
		
		while(fgets(line, sizeof(line)-1, f1)) {
			if(strstr(line, "before *")) {
				start_script(svc_script->d_name);
			}
		}
		fclose(f1);
	}
	
	/* We've started what should be the first thing, now we need to start
	 * everything else. We will start off in the order that readdir gives them
	 * to us, and hope to hell that runscript does the right thing */
	rewinddir(rlvldir);
	while((svc_script=readdir(rlvldir)) != NULL) {
		//printf("rewind: %s\n", svc_script->d_name);
		if((ret=strncmp(".", svc_script->d_name, 1)) == 0)
			continue;
		start_script(svc_script->d_name);
	}
	
	closedir(rlvldir);
	return 0;
}
