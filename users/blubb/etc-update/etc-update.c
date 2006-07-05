#include "etc-update.h"

int main() {
	read_config();
	
	// create /var/lib/etc-update/md5sum_index if needed
	if (access(MD5SUM_INDEX, R_OK) != 0) {
		if (access(MD5SUM_INDEX_DIR, R_OK) != 0) {
			mkdir(MD5SUM_INDEX_DIR, 0755);
		}
		FILE *f = fopen(MD5SUM_INDEX, "w+");
		fclose(f);
	}
	
	#ifndef DEBUG
	if (getuid() != 0) {
		fprintf(stderr, "!!! Oops, you're not root!\n");
		exit(EXIT_FAILURE);
	}
	#endif
	
	#ifdef DEBUG
	fprintf(stderr, "Getting CONFIG_PROTECT and CONFIG_PROTECT_MASK variables from portage... ");
	// sandboxing is useful for debugging, believe me
	char **envvars = get_listing("portageq envvar CONFIG_PROTECT CONFIG_PROTECT_MASK | sed -e \"s:^/:${ROOT}/:\" -e \"s: /: ${ROOT}/:g\"", "\n");
	#else
	char **envvars = get_listing("portageq envvar CONFIG_PROTECT CONFIG_PROTECT_MASK", "\n");
	#endif
	char *config_protect;
	char *config_protect_mask;
	char *cmd;
	char *myfile, *highest;
	char **result;
	int i, j, file_count;
	
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
	char **masked = find_updates(config_protect_mask);
	for (i=0;!is_last_entry(masked[i]);i++) {
		if (is_valid_entry(masked[i])) {
			merge(get_highest_update(masked, masked[i]), masked);
		}
	}
	fprintf(stderr, "done.\n");
	
	fprintf(stderr, "Searching for updates in CONFIG_PROTECT... ");
	char **protected = find_updates(config_protect);
	fprintf(stderr, "done.\n");
	char **md5_cache;
	char **md5sum_cache;
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
	attron(A_BOLD);
	attron(COLOR_PAIR(1));
	// TODO: why does clear() not work here?
	for (i=0;i<LINES;i++) {
		mvhline(i, 0, ' ', COLS);
	}
	attron(COLOR_PAIR(5));
	mvhline(LINES-2, 3, ' ', COLS-4);
	mvvline(3, COLS-2, ' ', LINES-4);
	attron(COLOR_PAIR(1));
	mvprintw(0,1, "etc-update v 2.0_alpha");
	mvhline(1, 1, ACS_HLINE, COLS - 2);
	refresh();
	WINDOW *inner = newwin(LINES - 4, COLS - 4, 2, 2);
	keypad(inner, TRUE);
	wattron(inner, COLOR_PAIR(2));
	wattron(inner, A_BOLD);
	box(inner, 0, 0);
	// again, TODO from above
	for (i=1;i<LINES-5;i++) {
		mvwhline(inner, i, 1, ' ', COLS-6);
	}
	// This is sick! TODO: make a seperate function later on
	wattroff(inner, A_BOLD);
	wattron(inner, COLOR_PAIR(3));
	mvwprintw(inner, 1, 3, "Select current: ");
	wattron(inner, COLOR_PAIR(4) | A_BOLD);
	mvwprintw(inner, 1, 3 + strlen("Select current: "), "<SPACE>");
	wattron(inner, COLOR_PAIR(3));
	wattroff(inner, A_BOLD);
	mvwprintw(inner, 1, 3 + strlen("Select current: <SPACE> "), "| ");
	wattron(inner, COLOR_PAIR(4) | A_BOLD);
	mvwprintw(inner, 1, 3 + strlen("Select current: <SPACE> | "), "<a>");
	wattron(inner, COLOR_PAIR(3));
	wattroff(inner, A_BOLD);
	mvwprintw(inner, 1, 3 + strlen("Select current: <SPACE> | <a>"), "ll | ");
	wattron(inner, COLOR_PAIR(4) | A_BOLD);
	mvwprintw(inner, 1, 3 + strlen("Select current: <SPACE> | <a>ll | "), "<u>");
	wattron(inner, COLOR_PAIR(3));
	wattroff(inner, A_BOLD);
	mvwprintw(inner, 1, 3 + strlen("Select current: <SPACE> | <a>ll | <u>"), "nselect all | ");
	wattron(inner, COLOR_PAIR(4) | A_BOLD);
	mvwprintw(inner, 1, 3 + strlen("Select current: <SPACE> | <a>ll | <u>nselect all | "), "<i>");
	wattron(inner, COLOR_PAIR(3));
	wattroff(inner, A_BOLD);
	mvwprintw(inner, 1, 3 + strlen("Select current: <SPACE> | <a>ll | <u>nselect all | <i>"), "nvert");
	
	mvwprintw(inner, 2, 3, "Show diff: ");
	wattron(inner, COLOR_PAIR(4) | A_BOLD);
	mvwprintw(inner, 2, 3 + strlen("Show diff: "), "<ENTER>");
	wattron(inner, COLOR_PAIR(3));
	wattroff(inner, A_BOLD);
	
	mvwprintw(inner, 3, 3, "Action shortcuts: ");
	wattron(inner, COLOR_PAIR(4) | A_BOLD);
	mvwprintw(inner, 3, 3 + strlen("Action shortcuts: "), "<m>");
	wattron(inner, COLOR_PAIR(3));
	wattroff(inner, A_BOLD);
	mvwprintw(inner, 3, 3 + strlen("Action shortcuts: <m>"), "erge | ");
	wattron(inner, COLOR_PAIR(4) | A_BOLD);
	mvwprintw(inner, 3, 3 + strlen("Action shortcuts: <m>erge | "), "<d>");
	wattron(inner, COLOR_PAIR(3));
	wattroff(inner, A_BOLD);
	mvwprintw(inner, 3, 3 + strlen("Action shortcuts: <m>erge | <d>"), "elete update");
	
	wrefresh(inner);
	// end of huge legend chunk
	
	WINDOW *menu_win = subwin(inner, LINES - 7 - 6, COLS - 4 - 5, 8, 5);
	MENU *mymenu = create_menu(protected);
	set_menu_win(mymenu, inner);
	set_menu_sub(mymenu, menu_win);
	set_menu_format(mymenu, LINES - 7 - 6, 1);
	
	post_menu(mymenu);
	touchwin(inner);
	wrefresh(inner);
	int c;
	while ((c = wgetch(inner)) != 'q' && c != 27) {
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
			
			// disp diff
			case '\n':
				endwin();
				show_diff(item_userptr(current_item(mymenu)));
				reset_prog_mode();
				break;
			// select single
			case ' ':
				menu_driver(mymenu, REQ_TOGGLE_ITEM);
				break;
			// select all
			case 'a':
				menu_driver(mymenu, REQ_LAST_ITEM);
				for (i=0;i<item_count(mymenu);i++) {
						set_item_value(current_item(mymenu), TRUE);
						menu_driver(mymenu, REQ_UP_ITEM);
				}
				menu_driver(mymenu, REQ_FIRST_ITEM);
				break;
			// deselect all
			case 'u':
				menu_driver(mymenu, REQ_LAST_ITEM);
				for (i=0;i<item_count(mymenu);i++) {
					set_item_value(current_item(mymenu), FALSE);
					menu_driver(mymenu, REQ_UP_ITEM);
				}
				menu_driver(mymenu, REQ_FIRST_ITEM);
				break;
			// invert selection
			case 'i':
				menu_driver(mymenu, REQ_LAST_ITEM);
				for (i=0;i<item_count(mymenu);i++) {
					menu_driver(mymenu, REQ_TOGGLE_ITEM);
					menu_driver(mymenu, REQ_UP_ITEM);
				}
				menu_driver(mymenu, REQ_FIRST_ITEM);
				break;
		}
		touchwin(inner);
		wrefresh(inner);
	}
	endwin();
	unpost_menu(mymenu);
	// TODO: free all items
	free_menu(mymenu);
	exit(EXIT_SUCCESS);
}
