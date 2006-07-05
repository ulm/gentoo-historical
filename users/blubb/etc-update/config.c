#include "etc-update.h"

void read_config() {
	extern struct configuration config;
	// XXX TODO: all
	config.automerge_comments = true;
	config.automerge_trivial = true;
	config.automerge_unmodified = true;
	config.diff_tool = strdup("diff -u");
	config.pager = strdup("less");
	config.merge_tool = strdup("sdiff -s -o");
}
