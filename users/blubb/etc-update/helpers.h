enum { DIRECTORY, UPDATE };

char **get_listing(const char *cmd, const char *delim);
int compare_updates(const void *a, const void *b);
struct node *find_node(struct node *root, char *path);

struct node {
	char **name;
	short type;
	struct node **children;
	int ct_children;
	struct node *parent;
};
