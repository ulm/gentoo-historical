#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <dirent.h>
#include <unistd.h>
#include <errno.h>

#define CONFD_DIR "/etc/conf.d/"
#define INIT_DIR "/etc/init.d/"
#define RUNLEVEL_DIR "/etc/runlevels/default"
//#define RUNLEVEL_DIR "/tmp/runlevels/default"
#define SHFUNCS "/sbin/functions.sh"

#ifndef TRUE
#define TRUE 1
#endif
#ifndef FALSE
#define FALSE 0
#endif


int is_started(char *script);
int mark_started(char *script);
int start_script(char *script);
