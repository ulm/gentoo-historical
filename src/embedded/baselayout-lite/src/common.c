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
	//int ret;
	//char *command = NULL;
	char *init_script = NULL;
	//char *cmdline[] = { NULL, "start", 0 };

	/* start everything with "before *", and mark it as started */
	//printf("Starting %s\n", script);

	asprintf(&init_script, "%s%s", INIT_DIR, script);
	//asprintf(&command, "%s%s start", INIT_DIR, script);
	//cmdline[0]=command;
	//printf("%d: %s %s %s %s\n",
	//	__LINE__, cmdline[0], cmdline[1], cmdline[2], cmdline[3]);
	/* so we can get return values and decide if we should call mark_started() */
	//if ((ret=system(command)) == 0) {
		//printf("%d\n", __LINE__);
		//printf("%s: Succesfully started %s\n", __func__, script);
		mkdir("/var/lib/", 0755);
		mkdir("/var/lib/init.d/", 0755);
		mkdir("/var/lib/init.d/started/", 0755);
		chdir("/var/lib/init.d/started/");
		//printf("symlinking %s to %s", init_script, basename(script));
		symlink(init_script, basename(script));
		//free(command);
		free(init_script);
		return TRUE;
	//}
	//printf("%d\n", __LINE__);
	//printf("Failed to start %s (%s)(return value=%d)\n", script, strerror(errno), ret);
	//free(command);
	free(init_script);
	return FALSE;
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
