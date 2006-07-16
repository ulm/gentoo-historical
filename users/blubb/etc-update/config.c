#include "etc-update.h"

void read_config() {
	extern struct configuration config;
	// XXX TODO: all
	config.automerge_comments = TRUE;
	config.automerge_trivial = TRUE;
	config.automerge_unmodified = TRUE;
	config.diff_tool = strdup("diff -u");
	config.pager = strdup("less");
	config.merge_tool = strdup("sdiff -s -o");
}
