#include "etc-update.h"

void read_config() {
	extern struct configuration config;
	ssize_t read;
	size_t len = 0;
	char *line = NULL;
	FILE *conffile;
	int linecount = 0;
	char *val;
	
	// set reasonable defaults
	config.automerge_comments = TRUE;
	config.automerge_trivial = TRUE;
	config.automerge_unmodified = TRUE;
	config.diff_tool = strdup("diff -u");
	config.pager = strdup("less");
	config.merge_tool = strdup("sdiff -s -o");
	
	conffile = fopen(CONFIG_FILE, "r");
	
	if (conffile) {
		while ((read = getline(&line, &len, conffile)) != -1) {
			linecount++;
			if (line[0] != '#') {
				if (strchr(line, '=')) {
					// houston, we have a token
					val = strndup(strchr(line, '=') + 1, strchr(line, '\n') - (strchr(line, '=') + 1));
					if (strstr(line, "diff_tool")) {
						free(config.diff_tool);
						config.diff_tool = val;
					} else if (strstr(line, "pager")) {
						free(config.pager);
						config.pager = val;
					} else if (strstr(line, "merge_tool")) {
						free(config.merge_tool);
						config.merge_tool = val;
					} else { // automerge_*
						if (strstr(line, "automerge_comments")) {
							config.automerge_comments = atoi(val);
						} else if (strstr(line, "automerge_trivial")) {
							config.automerge_trivial = atoi(val);
						} else if (strstr(line, "automerge_unmodified")) {
							config.automerge_unmodified = atoi(val);
						}
					}
				}
			}
		}
		free(line);
		fclose(conffile);
	}
}
