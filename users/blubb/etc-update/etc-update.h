#ifndef ETC_UPDATE_H
#define ETC_UPDATE_H

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <string.h>
#include <errno.h>
#include <openssl/md5.h>
#include <curses.h>
#include <menu.h>

#define true 1
#define false 0

#define MD5SUM_INDEX "/var/lib/etc-update/md5sum_index"
#define MD5SUM_INDEX_DIR "/var/lib/etc-update/"

#define SKIP_ENTRY (char *)1
#define LAST_ENTRY (char *)2

#define INDENT_CHAR ' '
#define INDENT_STR "  "

#include "helpers.h"
#include "index.h"
#include "core.h"
#include "modified.h"
#include "config.h"

#endif
