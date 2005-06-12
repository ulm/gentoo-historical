/***************************************************************************
 *  common stuff for baselayout-lite
 *      very limited functionality
 *      very small
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

int is_started(char *script) {
	int ret;
	char *script_link = NULL;

	asprintf(&script_link, "/var/lib/init.d/started/%s",
		basename(script));

	if (((ret=open(script_link, O_RDWR)) == -1) && errno==EROFS) {
		/* we are on a read only fs, probably starting to boot, we may still
		   have stuff laying around from a previous boot */
		//printf("readonly fs\n");
		close(ret);
		return FALSE;
	}
	close(ret);
	if ((access(script_link, F_OK)) == 0) {
		//printf("is_started-TRUE: %s (%s)\n", script_link, strerror(errno));
		free(script_link);
		return TRUE;
	}
	//printf("is_started-FALSE: %s (%s)\n", script_link, strerror(errno));
	free(script_link);
	return FALSE;
}

int mark_started(char *script) {
	char *init_script = NULL;
	asprintf(&init_script, "%s%s", INIT_DIR, script);
	mkdir("/var/lib/", 0755);
	mkdir("/var/lib/init.d/", 0755);
	mkdir("/var/lib/init.d/started/", 0755);
	chdir("/var/lib/init.d/started/");
	//printf("symlinking %s to %s", init_script, basename(script));
	symlink(init_script, basename(script));
	free(init_script);
	return TRUE;
}

int start_script(char *script) {
	int ret;
	char *command = NULL;
	
	asprintf(&command, "%s%s start", INIT_DIR, script);
	if((ret=system(command)) == 0) {
		free(command);
		return TRUE;
	}
	printf("Failed to start %s (%s)(return value=%d)\n", script, strerror(errno), ret);
	free(command);
	return FALSE;
}

int stop_script(char *script) {
	int ret;
	char *command = NULL;
	
	asprintf(&command, "%s%s stop", INIT_DIR, script);
	if((ret=system(command)) == 0) {
		free(command);
		return TRUE;
	}
	printf("Failed to stop %s (%s)(return value=%d)\n", script, strerror(errno), ret);
	free(command);
	return FALSE;
}
