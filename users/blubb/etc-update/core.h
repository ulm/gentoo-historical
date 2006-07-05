char *get_real_filename(const char *update);
char *get_highest_update(char **index, char *update);
bool is_last_entry(const char *entry);
bool is_valid_entry(const char *entry);
void merge(char *update, char **index);
void show_diff(char *update);
