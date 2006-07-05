#define ETC_UPDATE_CONFIG_FILE "/etc/etc-update/etc-update.conf"

struct configuration {
	bool automerge_comments;
	bool automerge_trivial;
	bool automerge_unmodified;
	char *pager;
	char *diff_tool;
	char *merge_tool;
} config;

void read_config();
