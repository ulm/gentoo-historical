#include "baselayout-lite.h"

char *find_dep(char *what);
int runscript(char *init_script, char *func_to_run);
int in_runlevel(char *script);
int find_alias(char *alias, char *script);

/*
 *
 *
 */
int main(int argc, char **argv) {

	char *line;
	char *word;
	FILE *init_script_FILE;

	/* if we don't have the right number of args, fail */
	if(argc < 3) {
		printf("Invalid number of arguments\n");
		exit(EXIT_FAILURE);
	}

	/* find the deps, and make sure all the right stuff is started first */
	init_script_FILE=fopen(argv[1], "r");
	if (init_script_FILE == NULL) {
		perror(argv[1]);
		exit(EXIT_FAILURE);
	}

	line=(void *)malloc(1000);
	memset(line, 0, 1000);

	while(fgets(line, 999, init_script_FILE)) {
		if(strstr(line, "\tneed ")) {
			/* these are non-optional deps that have to be started before */
			//printf("need: %s\n", line);
			word=strtok(line, " ");
			//printf("%s\n", word);
			while((word=strtok(NULL, " ")) != NULL) {
				char *alias;
				
				alias=malloc(1000);
				memset(alias, 0, 1000);
				
				if(word[strlen(word)-1] == '\n')
					word[strlen(word)-1]='\0';
				printf("Starting required dep: \"%s\"\n", word);
				/* find the dep, and start it */
			
				/* if we can't find a dep, it's likely because it's known as some
				 * other name, and it uses an alias... need to track it down
				 */
				find_alias(alias, word);
				printf("%s\n", alias);
				free(alias);
			}
		} else if(strstr(line, "\tuse")) {
			/* optional deps that have to be started before if they are in RUNLEVEL_DIR */
			word=strtok(line, " ");
			//printf("%s\n", word);
			while((word=strtok(NULL, " ")) != NULL) {
				if(word[strlen(word)-1] == '\n')
					word[strlen(word)-1]='\0';
				if(in_runlevel(word) == FALSE)
					continue;
				printf("Starting optional dep: \"%s\"\n", word);
			/* find the optional dep, and start it */
			
			/* if we can't find a dep, it's likely because it's known as some
			 * other name, and it uses an alias... need to track it down
			 */
			}
		}
	}
	free(line);
	runscript(argv[1], argv[2]);

	exit(EXIT_SUCCESS);
}

int runscript(char *init_script, char *func_to_run) {
	char *command = NULL;
	char *confd_file;
	
	confd_file=(void *)malloc(FILENAME_MAX);
	memset(confd_file, 0, FILENAME_MAX);

	/* figure out the conf.d file we need to source */
	sscanf(init_script, INIT_DIR"%s\n", confd_file);
	//printf("%s%s\n", CONFD_DIR, confd_file);
	
	
	/* here we glue all the bits together
	 *	we source /sbin/functions.sh to get some common init script functions
	 *	we source the conf.d file
	 *	we source the script itself (init_script)
	 *	we run the funtion that the user has called for (func_to_run)
	 */
	asprintf(&command, "/bin/sh -c \". %s ; . %s%s ; . %s ; %s\"",
		SHFUNCS, CONFD_DIR, confd_file, init_script, func_to_run);
	printf("%s\n", command);

	//system(command);

	free(command);
	free(confd_file);

	return 0;
}

/* need to look at alias names */
int in_runlevel(char *script) {
	int ret;
	DIR *rlvldir;
	struct dirent *svc_script;
	char *alias;
	
	rlvldir=opendir(RUNLEVEL_DIR);
	if (rlvldir == NULL) {
		perror(RUNLEVEL_DIR);
		return FALSE;
	}	

	while((svc_script=readdir(rlvldir)) != NULL) {
		if((ret=strncmp(".", svc_script->d_name, 1)) == 0)
			continue;
		if((ret=strcmp(svc_script->d_name, script)) == 0) {
			/* we have a match */
			return TRUE;
		}
		printf("%s: %s-%s\n", __func__, script, svc_script->d_name);
		alias=malloc(1000);
		memset(alias, 0, 1000);
		if(find_alias(alias, script))
			printf("%s\n", alias);
		free(alias);

		//printf("%s==%s:%d\n", svc_script->d_name, script, ret);
	}
	return FALSE;

}

/* Find an init script that has an "alias $script" line
 *
 * work in INIT_DIR since what we need may not be in RUNLEVEL_DIR
 */
int find_alias(char *alias, char *script) {
	//int ret;
	char *aliasline;
	DIR *initdir;
	struct dirent *svc_script;
	
	if ((initdir=opendir(INIT_DIR)) == NULL)
		return FALSE;

	while((svc_script=readdir(initdir)) != NULL) {
		char *line, *svc_script_path;
		FILE *svc_script_FILE;
		
		svc_script_path=(void *)malloc(1000);
		memset(svc_script_path, 0, 1000);

		snprintf(svc_script_path, 999, "%s%s", INIT_DIR, svc_script->d_name);
		svc_script_FILE=fopen(svc_script_path, "r");
		if (svc_script_FILE == NULL) {
			perror(svc_script_path);
			return FALSE;
		}

		line=(void *)malloc(1000);
		memset(line, 0, 1000);

		while(fgets(line, 999, svc_script_FILE)) {
			if(strstr(line, "\talias ")) {
				/* we have an alias line, work with it */
				aliasline=strtok(line, " ");
				printf("%s: %s\n", svc_script->d_name, aliasline);
				if(strcmp(aliasline, script) == 0) {
					strcpy(alias, aliasline);
					free(svc_script_path);
					free(line);
					return TRUE;
				}
			}
		}
		free(svc_script_path);
		free(line);
	}
	return FALSE;
}
