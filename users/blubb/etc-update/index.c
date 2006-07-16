#include "etc-update.h"

char **find_updates(char *searchdir) {
	// TODO: find something more efficient
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
			free(myfile);
		}
	}
	
	return listing;
}

MENU *create_menu(char **protected) {
	int i, arraycount = 0;
	ITEM **item_array;
	MENU *mymenu;
	
	for (i=0;!is_last_entry(protected[i]);i++) {
		arraycount++;
	}
	qsort(protected, arraycount, sizeof(char *), compare_updates);
	struct node *folded_protected = fold_updates(protected);
	item_array = (ITEM **)calloc(count_array_items(folded_protected) + 1, sizeof(ITEM *));
	build_item_array(item_array, folded_protected);
	
	mymenu = new_menu(item_array);
	set_menu_mark(mymenu, " * ");
	menu_opts_off(mymenu, O_ONEVALUE);
	menu_opts_off(mymenu, O_NONCYCLIC);
	set_menu_fore(mymenu, A_NORMAL);
	set_menu_grey(mymenu, A_STANDOUT);
	set_menu_back(mymenu, A_STANDOUT);
	
	free_folded(folded_protected);
	set_menu_format(mymenu, LINES - 7 - 6, 1);
	return mymenu;
}

void remove_menu(MENU *mymenu) {
	ITEM **item_list = menu_items(mymenu);
	int i;
	
	unpost_menu(mymenu);
	
	for (i=0;i<item_count(mymenu);i++) {
		free(item_name(item_list[i]));
		free_item(item_list[i]);
	}
	//free(item_list);
	free_menu(mymenu);
}
