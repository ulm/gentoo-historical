#include "etc-update.h"

char **get_listing(const char *cmd, const char *delim) {
        FILE *pipe;
        char *buf = NULL;
        size_t bufsize = 0;
        ssize_t read;
        char **listing;
        int count = 1, i = 0;
		unsigned int j;
        char c;

        pipe = popen(cmd, "r");
        if (pipe) {
                read = getdelim(&buf, &bufsize, '\0', pipe);
				char *buf_backup = buf;
                if (read != -1) {
                        // determine number of tokens
                        while ((c = buf[i]) != '\0') {
                                for (j=0;j<strlen(delim);j++) {
                                        if (c == delim[j]) {
                                                count++;
                                        }
                                }
                                i++;
                        }
						
                        listing = (char **) malloc(sizeof(char *) * count);
						char *str;
						i=0;
						while ((str = strsep(&buf, delim))) {
							listing[i] = strdup(str);
							i++;
						}
						free(buf_backup);
						// make sure the last one is always LAST_ENTRY
						listing[count-1] = LAST_ENTRY;
                        pclose(pipe);
                        return listing;
                } else {
					// wth is read = -1 when cmd didn't give any output?
					listing = (char **)malloc(sizeof(char *));
					listing[0] = LAST_ENTRY;
					free(buf_backup);
					return listing;
                }
        } else {
                assert(0);
        }
}

int compare_updates(const void *a, const void *b) {
	char *real_a;
	char *real_b;
	int result;
	
	if (is_valid_entry(*(char **)a)) { 
		real_a	= get_real_filename(*(char **)a);
	} else {
		real_a = NULL;
	}
	if (is_valid_entry(*(char **)b)) {
		real_b = get_real_filename(*(char **)b);
	} else {
		real_b = NULL;
	}
	
	if (!real_a && !real_b) {
		result = -1;
	} else if (!real_a) {
		result = 1;
	} else if (!real_b) {
		result = -1;
	} else {
		// both valid updates
		if ((result = strcmp(real_a, real_b)) == 0) {
			// same target
			result = strcmp(*(char **)a, *(char **)b);
		}
	}
	
	free(real_a);
	free(real_b);
	
	return result;
}

struct node *fold_updates(char **list) {
	struct node *root = malloc(sizeof(struct node));
	struct node *mynode, *newnode;
	char *endtok, *curtok;
	int i;
	int run;
	
	root->name = strdup("/");
	root->children = malloc(sizeof(struct node *));
	root->ct_children = 0;
	root->parent = NULL;
	
	for (i=0;!is_last_entry(list[i]);i++) {
		if (is_valid_entry(list[i])) {
			endtok = list[i]+1;
			run = 1;
			while (run) {
				if (run == 2) {
					// 2 means we're on the last run
					run = 0;
					endtok = list[i] + strlen(list[i]) + 1;
				} else {
					if ((endtok = strchr(endtok+1, '/')) == NULL) {
						run = 2;
					}
				}
				curtok = strndup(list[i], endtok - list[i]);
				
				mynode = find_node(root, curtok);
				if (mynode == (struct node *)FALSE) {
					mynode = root;
				}
				if (mynode != (struct node *)TRUE) {
					// mynode is the parent of the new to be inserted node
					newnode = malloc(sizeof(struct node));
					newnode->name = strdup(curtok);
					newnode->children = malloc(sizeof(struct node *));
					newnode->ct_children = 0;
					newnode->parent = mynode;
					
					mynode->ct_children++;
					mynode->children = realloc(mynode->children, sizeof(struct node *) * mynode->ct_children);
					mynode->children[mynode->ct_children-1] = newnode;
				}
				
				free(curtok);
			}
		}
	}
	
	return root;
	
}

struct node *find_node(struct node *root, char *path) {
	int i;
	struct node *mynode;
	
	if (!strcmp(root->name, path)) {
		// already exists
		return (struct node *)TRUE;
	} else if (!strncmp(root->name, path, strlen(root->name))) {
		// at least it's in the same direction, go through the list of children
		for (i=0;i<root->ct_children;i++) {
			mynode = find_node(root->children[i], path);
			if (mynode == (struct node *)TRUE) {
				return (struct node *)TRUE;
			} else if (mynode != (struct node *)FALSE) {
				return mynode;
			}
		}
		// if we hit this point, nothing was found, meaning that it has to be a child of the current node
		return root;
	} else {
		// completely wrong
		return (struct node *)FALSE;
	}
}
void sanity_checks() {
	unsigned int i;
	char *tools[] = {
		"/usr/bin/diff",
		"/usr/bin/find",
		"/usr/bin/portageq",
		"/bin/sed"
	};
	
	#ifndef DEBUG
	if (getuid() != 0) {
		fprintf(stderr, "!!! Oops, you're not root!\n");
		exit(EXIT_FAILURE);
	}
	#endif

	for (i=0;i<sizeof(tools)/sizeof(tools[0]);i++) {
		if (access(tools[i], X_OK) != 0) {
			perror(tools[i]);
			exit(EXIT_FAILURE);
		}
	}
	// TODO: check config.pager etc. too
	// TODO: make sure /var/lib/etc-update/md5sum_index exists
}

void draw_legend(WINDOW *inner) {
	int i;
	
	wattron(inner, COLOR_PAIR(2));
	wattron(inner, A_BOLD);
	box(inner, 0, 0);
	// again, TODO from above
	for (i=1;i<LINES-5;i++) {
		mvwhline(inner, i, 1, ' ', COLS-6);
	}
	
	wattroff(inner, A_BOLD);
	wattron(inner, COLOR_PAIR(3));
	mvwprintw(inner, 1, 3, "Select current: ??????? | ???ll | ???nselect all | ???nvert");
	mvwprintw(inner, 2, 3, "Show diff: ???????");
	mvwprintw(inner, 3, 3, "Action shortcuts: ???erge | ???elete update | merge interacti???ely");
	mvwprintw(inner, 4, 3, "Quit: ??? or ?????");
	
	wattron(inner, COLOR_PAIR(4) | A_BOLD);
	mvwprintw(inner, 1, 3 + strlen("Select current: "), "[SPACE]");
	mvwprintw(inner, 1, 3 + strlen("Select current: ??????? | "), "[A]");
	mvwprintw(inner, 1, 3 + strlen("Select current: ??????? | ???ll | "), "[U]");
	mvwprintw(inner, 1, 3 + strlen("Select current: ??????? | ???ll | ???nselect all | "), "[I]");
	
	mvwprintw(inner, 2, 3 + strlen("Show diff: "), "[ENTER]");
	
	mvwprintw(inner, 3, 3 + strlen("Action shortcuts: "), "[M]");
	mvwprintw(inner, 3, 3 + strlen("Action shortcuts: ???erge | "), "[D]");
	mvwprintw(inner, 3, 3 + strlen("Action shortcuts: ???erge | ???elete update | merge interacti"), "[V]");
	
	mvwprintw(inner, 4, 3 + strlen("Quit: "), "[Q]");
	mvwprintw(inner, 4, 3 + strlen("Quit: ??? or "), "[ESC]");
	
	wattron(inner, COLOR_PAIR(2));
	// TODO: replace COLS - 4/LINES - 7 with a function to determine size of inner
	mvwhline(inner, 5, 1, 0, COLS - 4 -2);
	mvwhline(inner, LINES - 7, 1, 0, COLS - 4 -2);
	
	wrefresh(inner);
}

void draw_background() {
	int i;
	
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
	mvprintw(0,1, "etc-update v 2.0_alpha1");
	mvhline(1, 1, ACS_HLINE, COLS - 2);
	
	refresh();
}

bool is_dir(const char *path) {
	if (path[strlen(path)-1] == '/') {
		return true;
	} else {
		return false;
	}
}
char *get_indent_name(struct node *update) {
	int ct_indents = 0;
	struct node *mynode = update;
	char *start, *name;
	char *indent_name;
	
	while ((mynode = mynode->parent)) {
		ct_indents++;
	}
	if ((start = strstr(update->name, "._cfg"))) {
		name = strchr(start+strlen("._cfg"),'_') + 1;
		indent_name = calloc(ct_indents * strlen(INDENT_STR) + strlen(name) + strlen(" (????) "), sizeof(char));
		while (ct_indents > 0) {
			strcat(indent_name, INDENT_STR);
			ct_indents--;
		}
		strcat(indent_name, name);
		strcat(indent_name, " (");
		strncat(indent_name, start+strlen("._cfg"), 4);
		strcat(indent_name, ")");
	} else {
		start = strrchr(update->name, '/') + 1;
		indent_name = calloc(ct_indents * strlen(INDENT_STR) + strlen(start) + strlen("/") + 1, sizeof(char));
		while (ct_indents > 0) {
			strcat(indent_name, INDENT_STR);
			ct_indents--;
		}
		
		strcat(indent_name, start);
		strcat(indent_name, "/");
	}
	return indent_name;
}
int count_array_items(struct node *root) {
	int count = 0, i;
	
	for (i=0;i<root->ct_children;i++) {
		count += count_array_items(root->children[i]);
	}
	return 1 + count;
}

void build_item_array(ITEM **item_array, struct node *root) {
	int i = 0;
	
	// fast-forward to the next NULL entry
	while (item_array[i]) {
		i++;
	}
	item_array[i] = new_item(get_indent_name(root), "");
	set_item_userptr(item_array[i], root->name);
	
	for (i=0;i<root->ct_children;i++) {
		build_item_array(item_array, root->children[i]);
	}
}
