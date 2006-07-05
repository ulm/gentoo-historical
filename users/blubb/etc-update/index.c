#include "etc-update.h"

char **find_updates(char *searchdir) {
	char *cmd = calloc(strlen("find % -name '._cfg????_*' 2>/dev/null") + strlen(searchdir), sizeof(char));
	char **listing;
	char *myfile;
	struct stat tmpstat, tmpstat2;
	int i, j;
	
	strcpy(cmd, "find ");
	strcat(cmd, searchdir);
	strcat(cmd, " -name '._cfg????_*' 2>/dev/null");
	listing = get_listing(cmd, "\n");
	free(cmd);
	
	for (i=0;!is_last_entry(listing[i]);i++) {
		if (!strcmp(listing[i]+strlen(listing[i])-1,"~") || \
			!strcmp(listing[i]+strlen(listing[i])-4,".bak")) {
			free(listing[i]);
			listing[i] = SKIP_ENTRY;
		} else {
			myfile = get_real_filename(listing[i]);
			if (access(myfile, F_OK) != 0) {
				// we don't want phantom updates
				unlink(listing[i]);
				free(listing[i]);
				listing[i] = SKIP_ENTRY;
			} else {
				// we don't want duplicates either
				stat(listing[i], &tmpstat);
				for(j=0;j<i;j++) {
					if (is_valid_entry(listing[j])) { 
						stat(listing[j], &tmpstat2);
						if (tmpstat.st_dev == tmpstat2.st_dev && \
							tmpstat.st_ino == tmpstat2.st_ino) {
							free(listing[i]);
							listing[i] = SKIP_ENTRY;
						}
					}
				}
			}
		}
	}
	
	return listing;
}

MENU *create_menu(char **protected) {
	int i, j = 0, count = 0, arraycount = 0;
	ITEM **item_array;
	MENU *mymenu;
	
	for (i=0;!is_last_entry(protected[i]);i++) {
		if (is_valid_entry(protected[i])) {
			count++;
		}
		arraycount++;
	}
	// we really want this sorted
	qsort(protected, arraycount, sizeof(char *), compare_updates);
	// TODO: fold
	//struct node *folded_protected = fold_updates(protected);
	item_array = (ITEM **)malloc(sizeof(ITEM *) * (count + 1));
	for (i=0;!is_last_entry(protected[i]);i++) {
		if (is_valid_entry(protected[i])) {
			item_array[j] = new_item(protected[i], "");
			set_item_userptr(item_array[j], protected[i]);
			j++;
		}
	}
	item_array[count] = NULL;
	mymenu = new_menu(item_array);
	set_menu_mark(mymenu, " * ");
	menu_opts_off(mymenu, O_ONEVALUE);
	menu_opts_off(mymenu, O_NONCYCLIC);
	set_menu_fore(mymenu, A_NORMAL);
	set_menu_grey(mymenu, A_STANDOUT);
	set_menu_back(mymenu, A_STANDOUT);
	
	// free folded_protected
	return mymenu;
}
