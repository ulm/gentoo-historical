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
		return FALSE;
	}
	if ((access(script_link, F_OK)) == 0) {
		//printf("is_started-TRUE: %s\n", strerror(errno));
		free(script_link);
		return TRUE;
	}
	//printf("is_started-FALSE: %s\n", strerror(errno));
	free(script_link);
	return FALSE;
}
