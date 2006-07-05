#include "etc-update.h"

char *get_real_filename(const char *update) {
	char *file = (char *)calloc(strlen(update) + 1 - strlen("._cfg????_"), sizeof(char));
	strncpy(file, update, strrchr(update, '/') - update + 1);
	strcat(file, strrchr(update, '/') + strlen("._cfg????_") + 1);
	
	return file;
}

char *get_highest_update(char **index, char *update) {
	// update is just any update of the real file we want to get the highest update for
	char *real_file = get_real_filename(update);
	char *my_real_file;
	char *highest_update = update;
	int i;
	
	for (i=0;!is_last_entry(index[i]);i++) {
		if (is_valid_entry(index[i])) {
			my_real_file = get_real_filename(index[i]);
			if (!strcmp(my_real_file, real_file)) {
				if (strcmp(index[i], highest_update) > 0) {
					highest_update = index[i];
				}
			}
			free(my_real_file);
		}
	}
	
	free(real_file);
	
	return highest_update;
}

bool is_last_entry(const char *entry) {
	if (entry == LAST_ENTRY) {
		return true;
	} else {
		return false;
	}
}

bool is_valid_entry(const char *entry) {
	if (entry == LAST_ENTRY || entry == SKIP_ENTRY) {
		return false;
	} else {
		return true;
	}
}

void merge(char *update, char **index) {
	char *real_file = get_real_filename(update);
	char *my_real_file;
	int i;
	
	assert(!rename(update, real_file));
	
	for (i=0;!is_last_entry(index[i]);i++) {
		if (is_valid_entry(index[i])) {
			my_real_file = get_real_filename(index[i]);
			if (!strcmp(my_real_file, real_file)) {
				if (strcmp(update, index[i])) {
					assert(!unlink(index[i]));
				}
				free(index[i]);
				index[i] = SKIP_ENTRY;
			}
			free(my_real_file);
		}
	}
	
	free(real_file);
}

void show_diff(char *update) {
	extern struct configuration config;
	char *realfile = get_real_filename(update);
	char *cmd = (char *)calloc(strlen(config.diff_tool) + strlen(" % % | ") + strlen(update) + strlen(realfile) + strlen(config.pager) + 1, sizeof(char));
	strcpy(cmd, config.diff_tool);
	strcat(cmd, " ");
	strcat(cmd, realfile);
	strcat(cmd, " ");
	strcat(cmd, update);
	if (strcmp(config.pager, "")) {
		strcat(cmd, " | ");
		strcat(cmd, config.pager);
	}
	free(realfile);
	system(cmd);
	free(cmd);
}
