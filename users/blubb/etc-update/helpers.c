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
						// make sure the last one is always LAST_ENTRY
						listing[count-1] = LAST_ENTRY;
                        pclose(pipe);
                        return listing;
                } else {
					// wth is read = -1 when cmd didn't give any output?
					listing = (char **)malloc(sizeof(char *));
					listing[0] = LAST_ENTRY;
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
	
	if (is_valid_entry((char *)a)) { 
		real_a	= get_real_filename(*(char **)a);
	} else {
		real_a = NULL;
	}
	if (is_valid_entry((char *)b)) {
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

struct node *fold_protected(char **list) {
	struct node** myarray = malloc(sizeof(struct node *));
	struct node *root = malloc(sizeof(struct node));
	int i;	
	
	for (i=0;!is_last_entry(list[i]);i++) {
		if (is_valid_entry(list[i])) {
			// TODO: only to make it compile
			myarray++;
			root++;
		}
	}
	
	// TODO: same
	return *myarray;
}

struct node *find_node(struct node *root, char *path) {
	int i;
	
	if (!strcmp(*(root->name), path)) {
		// already exists
		return (struct node *)TRUE;
	} else if (!strncmp(*(root->name), path, strlen(*(root->name)))) {
		// at least it's in the same direction, go through the list of children
		for (i=0;i<root->ct_children;i++) {
			if (find_node(root->children[i], path) == (struct node *)TRUE) {
				return (struct node *)TRUE;
			}
			// if we hit this point, nothing was found, meaning that it has to be a child of the current node
			return root;
		}
	} else {
		// completely wrong
		return (struct node *)FALSE;
	}
}
