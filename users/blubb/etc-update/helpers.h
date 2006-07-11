char **get_listing(const char *cmd, const char *delim);
int compare_updates(const void *a, const void *b);
struct node *find_node(struct node *root, char *path);
void sanity_checks();
void draw_legend(WINDOW *inner);
void draw_background();
bool is_dir(const char *path);
struct node *fold_updates(char **list);
struct node *find_node(struct node *root, char *path);
char *get_indent_name(struct node *update);
void build_item_array(ITEM **item_array, struct node *root);
int count_array_items(struct node *root);

struct node {
	char *name;
	struct node **children;
	int ct_children;
	struct node *parent;
};
