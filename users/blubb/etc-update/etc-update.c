#include "etc-update.h"

int main() {
	char *config_protect;
	char *config_protect_mask;
	char *cmd;
	char *myfile;
	char *highest;
	const char *name;
	const char *myname;
	char **myupdate;
	int indent;
	int myindent;
	bool cont;
	char **result;
	char **envvars;
	char **protected;
	char **masked;
	char **md5_cache;
	char **md5sum_cache;
	ITEM **items_list;
	int i, j, file_count, c;
	bool menu_changed;
	WINDOW *inner;
	WINDOW *menu_win;
	MENU *mymenu;
	
	read_config();
	sanity_checks();
	
	#ifdef DEBUG
	fprintf(stderr, "Getting CONFIG_PROTECT and CONFIG_PROTECT_MASK variables from portage... ");
	// sandboxing is useful for debugging, believe me
	envvars = get_listing("portageq envvar CONFIG_PROTECT CONFIG_PROTECT_MASK | sed -e \"s:^/:${ROOT}/:\" -e \"s: /: ${ROOT}/:g\"", "\n");
	#else
	envvars = get_listing("portageq envvar CONFIG_PROTECT CONFIG_PROTECT_MASK", "\n");
	#endif
	
	if (is_valid_entry(envvars[0]) && is_valid_entry(envvars[1])) {
		config_protect = strdup(envvars[0]);
		config_protect_mask = strdup(envvars[1]);
		free(envvars[0]);
		free(envvars[1]);
		fprintf(stderr, "done.\n");
	} else {
		fprintf(stderr, "failed. Aborting");
		exit(EXIT_FAILURE);
	}
	free(envvars);
	
	fprintf(stderr, "Automerging updates in CONFIG_PROTECT_MASK... ");
	masked = find_updates(config_protect_mask);
	for (i=0;!is_last_entry(masked[i]);i++) {
		if (is_valid_entry(masked[i])) {
			merge(get_highest_update(masked, masked[i]), masked);
		}
	}
	free(masked);
	fprintf(stderr, "done.\n");
	
	fprintf(stderr, "Searching for updates in CONFIG_PROTECT... ");
	protected = find_updates(config_protect);
	fprintf(stderr, "done.\n");

	// it's important that we do this first
	if (config.automerge_unmodified) {
		fprintf(stderr, "Updating md5 sums... ");
		file_count = 1;
		md5_cache = (char **) malloc(sizeof(char *) * file_count);
		md5sum_cache = (char **) malloc(sizeof(char *) * file_count);
		md5_cache[0] = LAST_ENTRY;
		md5sum_cache[0] = LAST_ENTRY;
		for (i=0;!is_last_entry(protected[i]);i++) {
			if (is_valid_entry(protected[i])) {
				highest = get_highest_update(protected, protected[i]);
				if (!strcmp(protected[i], highest)) {
					md5_cache = (char **) realloc(md5_cache, sizeof(char *) * (file_count + 1));
					md5sum_cache = (char **) realloc(md5sum_cache, sizeof(char *) * (file_count + 1));
					md5_cache[file_count-1] = strdup(highest);
					md5sum_cache[file_count-1] = (char *)malloc(sizeof(char) * 32);
					calc_md5(md5_cache[file_count-1], md5sum_cache[file_count-1]);
					md5_cache[file_count] = LAST_ENTRY;
					md5sum_cache[file_count] = LAST_ENTRY;
					file_count++;
				}
			}
		}
		for (i=0;!is_last_entry(protected[i]);i++) {
			if (is_valid_entry(protected[i])) {
				myfile = get_real_filename(protected[i]);
				
				if (!user_modified(myfile)) {
					merge(get_highest_update(protected, protected[i]), protected);
				}
				
				free(myfile);
			}
		}
		for (i=0;!is_last_entry(md5_cache[i]);i++) {
			myfile = get_real_filename(md5_cache[i]);
			md5sum_update(myfile, md5sum_cache[i]);
			free(myfile);
			free(md5_cache[i]);
			free(md5sum_cache[i]);
		}
		free(md5_cache);
		free(md5sum_cache);
		fprintf(stderr, "done.\n");
	}
	
	if (config.automerge_comments) {
		fprintf(stderr, "Automerging updates which only affect comments... ");
		for (i=0;!is_last_entry(protected[i]);i++) {
			if (is_valid_entry(protected[i])) {
				myfile = get_real_filename(protected[i]);
				highest = get_highest_update(protected, protected[i]);
				cmd = (char *)calloc(strlen("diff -Nu '' '' | grep \"^[+-][^+-]\" | grep -v \"^[-+]#\" | grep -v \"^[-+][:space:]*$\" " ) + strlen(highest) + strlen(myfile), sizeof(char));
				strcpy(cmd, "diff -Nu '");
				strcat(cmd, myfile);
				strcat(cmd, "' '");
				strcat(cmd, highest);
				strcat(cmd, "' | grep \"^[+-][^+-]\" | grep -v \"^[-+]#\" | grep -v \"^[-+][:space:]*$\"");
				
				free(myfile);
				
				result = get_listing(cmd, "\n");
				free(cmd);
				if (is_last_entry(result[0])) {
					merge(highest, protected);
				}
				for (j=0;!is_last_entry(result[j]);j++) {
					free(result[j]);
				}
				free(result);
			}
		}
		fprintf(stderr, "done.\n");
	}
	if (config.automerge_trivial) {
		fprintf(stderr, "Automerging trivial changes... ");
		for (i=0;!is_last_entry(protected[i]);i++) {
			if (is_valid_entry(protected[i])) {
				myfile = get_real_filename(protected[i]);
				highest = get_highest_update(protected, protected[i]);
				cmd = (char *)calloc(strlen("diff -Nu '' '' | grep \"^[+-][^+-]\" | grep -v \"# .Header:.*\" ") + strlen(highest) + strlen(myfile), sizeof(char));
				strcpy(cmd, "diff -Nu '");
				strcat(cmd, myfile);
				strcat(cmd, "' '");
				strcat(cmd, highest);
				strcat(cmd, "' | grep \"^[+-][^+-]\" | grep -v \"# .Header:.*\"");
				
				result = get_listing(cmd, "\n");
				free(cmd);
				if (is_last_entry(result[0])) {
					merge(highest, protected);
				}
				for (j=0;!is_last_entry(result[j]);j++) {
					free(result[j]);
				}
				free(result);
				free(myfile);
			}
		}
		fprintf(stderr, "done.\n");
	}
	if (config.automerge_unmodified) {
		fprintf(stderr, "Automerging unmodified files... ");
		for (i=0;!is_last_entry(protected[i]);i++) {
			if (is_valid_entry(protected[i])) {
				myfile = get_real_filename(protected[i]);
				
				if (!user_modified(myfile)) {
					merge(get_highest_update(protected, protected[i]), protected);
				}
				
				free(myfile);
			}
		}
		fprintf(stderr, "done.\n");
	}
	/***/
	// ncurses n'stuff
	initscr();
	cbreak();
	noecho();
	keypad(stdscr, TRUE);
	start_color();
	init_pair(1, COLOR_CYAN, COLOR_BLUE);
	init_pair(2, COLOR_WHITE, COLOR_WHITE);
	init_pair(3, COLOR_BLACK, COLOR_WHITE);
	init_pair(4, COLOR_YELLOW, COLOR_WHITE);
	init_pair(5, COLOR_WHITE, COLOR_BLACK);
	
	draw_background();
	
	inner = newwin(LINES - 4, COLS - 4, 2, 2);
	keypad(inner, TRUE);
	
	draw_legend(inner);
	
	menu_win = subwin(inner, LINES - 7 - 6, COLS - 4 - 5, 8, 5);

	mymenu = create_menu(protected);
	items_list = menu_items(mymenu);
	set_menu_win(mymenu, inner);
	set_menu_sub(mymenu, menu_win);
	
	post_menu(mymenu);
	touchwin(inner);
	wrefresh(inner);
	menu_changed = FALSE;
	// 27 = ESC
	while ((c = wgetch(inner)) != 'q' && c != 27 && c != 'Q') {
		switch(c) {
			// navigation 1up/down
			case KEY_DOWN:
				menu_driver(mymenu, REQ_DOWN_ITEM);
				break;
			case KEY_UP:
				menu_driver(mymenu, REQ_UP_ITEM);
				break;
			//navigation 1 page up/down
			case KEY_PPAGE:
				menu_driver(mymenu, REQ_SCR_UPAGE);
				break;
			case KEY_NPAGE:
				menu_driver(mymenu, REQ_SCR_DPAGE);
				break;
			// navigation top/bottom
			case KEY_HOME:
				menu_driver(mymenu, REQ_FIRST_ITEM);
				break;
			case KEY_END:
				menu_driver(mymenu, REQ_LAST_ITEM);
				break;
			
			// select single
			case ' ':
				if ((strrchr(item_name(current_item(mymenu)), '/'))) {
					// it's a dir, select all subdirs + files
					name = item_name(current_item(mymenu));
					indent = 0;
					while (name[indent] == INDENT_CHAR) {
						indent++;
					}
					cont = TRUE;
					while (cont) {
						menu_driver(mymenu, REQ_DOWN_ITEM);
						myname = item_name(current_item(mymenu));
						myindent = 0;
						while (myname[myindent] == INDENT_CHAR) {
							myindent++;
						}
						if (myindent > indent) {
							if ((!strrchr(myname, '/'))) {
								set_item_value(current_item(mymenu), TRUE);
							}
						} else {
							menu_driver(mymenu, REQ_UP_ITEM);
							cont = FALSE;
						}
					}
				} else {
					menu_driver(mymenu, REQ_TOGGLE_ITEM);
				}
				break;
			// select all
			case 'a':
			case 'A':
				menu_driver(mymenu, REQ_LAST_ITEM);
				for (i=0;i<item_count(mymenu);i++) {
					if ((!strrchr(item_name(current_item(mymenu)), '/'))) {
						set_item_value(current_item(mymenu), TRUE);
					}
					menu_driver(mymenu, REQ_UP_ITEM);
				}
				menu_driver(mymenu, REQ_FIRST_ITEM);
				break;
			// deselect all
			case 'u':
			case 'U':
				menu_driver(mymenu, REQ_LAST_ITEM);
				for (i=0;i<item_count(mymenu);i++) {
					menu_driver(mymenu, REQ_UP_ITEM);
					set_item_value(current_item(mymenu), FALSE);
				}
				menu_driver(mymenu, REQ_FIRST_ITEM);
				break;
				
			// disp diff
			case '\n':
			case KEY_ENTER:
				if (item_userptr(current_item(mymenu))) {
					endwin();
					show_diff(*((char **)item_userptr(current_item(mymenu))));
					reset_prog_mode();
				}
				break;
			// merge update
			case 'm':
			case 'M':
				/* it is important that we go from last to first:
				 * if e.g. both 0000 and 0001 are selected for merging, this
				 * assures (given a sorted list), that 0001 gets merged before
				 * 0000 and therefore 0000 gets removed
				 */
				for (i=item_count(mymenu)-1;i>=0;i--) {
					if (item_value(items_list[i]) == TRUE || (current_item(mymenu) == items_list[i] && item_userptr(items_list[i]))) {
						myupdate = (char **)item_userptr(items_list[i]);
						if (is_valid_entry(*myupdate)) {
							merge(*myupdate, protected);
							menu_changed = TRUE;
						}
					}
				}
				break;
			// delete update
			case 'd':
			case 'D':
				for (i=0;i<item_count(mymenu);i++) {
					if (item_value(items_list[i]) == TRUE || (current_item(mymenu) == items_list[i] && item_userptr(items_list[i]))) {
						myupdate = (char **)item_userptr(items_list[i]);
						assert(!unlink(*(myupdate)));
						free(*myupdate);
						*myupdate = SKIP_ENTRY;
						menu_changed = TRUE;
					}
				}
				break;
			// merge interactively
			case 'i':
			case 'I':
				for (i=0;i<item_count(mymenu);i++) {
					if (item_value(items_list[i]) == TRUE || (current_item(mymenu) == items_list[i] && item_userptr(items_list[i]))) {
						// TODO: interactive merges
						menu_changed = TRUE;
					}
				}
				break;
			case KEY_RESIZE:
				draw_background();
				remove_menu(mymenu);
				delwin(menu_win);
				delwin(inner);
				inner = newwin(LINES - 4, COLS - 4, 2, 2);
				draw_legend(inner);
				menu_win = subwin(inner, LINES - 7 - 6, COLS - 4 - 5, 8, 5);
				mymenu = create_menu(protected);
				set_menu_win(mymenu, inner);
				set_menu_sub(mymenu, menu_win);	
				post_menu(mymenu);
				break;
		}
		if (menu_changed) {
			remove_menu(mymenu);
			
			draw_legend(inner);
			mymenu = create_menu(protected);
			items_list = menu_items(mymenu);
			set_menu_win(mymenu, inner);
			set_menu_sub(mymenu, menu_win);		
			post_menu(mymenu);			
			menu_changed = FALSE;
		}
		touchwin(inner);
		wrefresh(inner);
	}
	endwin();
	remove_menu(mymenu);
	for (i=0;!is_last_entry(protected[i]);i++) {
		if (is_valid_entry(protected[i])) {
			free(protected[i]);
		}
	}
	free(protected);
	if (config.pager) { 
		free(config.pager);
	}
	if (config.diff_tool) {
		free(config.diff_tool);
	}
	if (config.merge_tool) {
		free(config.merge_tool);
	}
	free(config_protect);
	free(config_protect_mask);
	exit(EXIT_SUCCESS);
}
