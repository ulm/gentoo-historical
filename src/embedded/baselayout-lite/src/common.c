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
	
	printf("Starting %s\n", script);
	asprintf(&command, "%s%s start", INIT_DIR, script);
	if((ret=system(command)) == 0) {
		//printf("%s: Succesfully started %s\n", __func__, script);
		free(command);
		return TRUE;
	}
	printf("Failed to start %s (%s)(return value=%d)\n", script, strerror(errno), ret);
	free(command);
	return FALSE;

}
