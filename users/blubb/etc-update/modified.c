#include "etc-update.h"

bool user_modified(char *file) {
	FILE *indexpipe, *filepipe;
	char *line = NULL, *filedump = NULL;
	size_t len = 0, len2 = 0;
	ssize_t read;
	char *md5sum;
	char filemd5[MD5_DIGEST_LENGTH];
	char hexdigest[32];
	bool user_mod = TRUE;
	if (access(MD5SUM_INDEX, R_OK) != 0) {
		return TRUE;
	} else {
		assert( indexpipe = fopen(MD5SUM_INDEX, "r") );
		while ((read = getline(&line, &len, indexpipe)) != -1) {
			if (!strncmp(line, file, strlen(file))) {
				md5sum = strchr(line, ' ') + 1;
				filepipe = fopen(file, "r");
				if ((getdelim(&filedump, &len2, EOF, filepipe)) != -1) {
					MD5(filedump, strlen(filedump), filemd5);
					md52hex(filemd5, hexdigest);
					if (!strncmp(md5sum, hexdigest, 32)) {
						user_mod = FALSE;
					}
				}
				fclose(filepipe);
				free(filedump);
			}
		}
		fclose(indexpipe);
		free(line);
		return user_mod;
	}
}

void md52hex(char *md5sum, char *hexdigest) {
	// this one is stolen from python's md5module.c
	// TODO: sort out possible license issues
	char c;
	int i, j;
	
	for(i=j=0; i<16; i++) {
		c = (md5sum[i] >> 4) & 0xf;
   		c = (c>9) ? c+'a'-10 : c + '0';
   		hexdigest[j++] = c;
		c = (md5sum[i] & 0xf);
		c = (c>9) ? c+'a'-10 : c + '0';
		hexdigest[j++] = c;
    }
}

void calc_md5(char *file, char* hexdigest) {
	FILE *fp;
	char *dump = NULL;
	size_t len = 0;
	
	char md5sum[MD5_DIGEST_LENGTH];
	
	fp = fopen(file, "r");
	if (getdelim(&dump, &len, EOF, fp) != -1) {
		MD5(dump, strlen(dump), md5sum);
		md52hex(md5sum, hexdigest);
		free(dump);
	}
	fclose(fp);
}

void md5sum_update(char *file, char *hexdigest) {
	FILE *oldpipe;
	char *dump = NULL;
	size_t len = 0;
	char *entry;
	
	assert( oldpipe = fopen(MD5SUM_INDEX, "r") );
	
	getdelim(&dump, &len, EOF, oldpipe);
	if ((entry = strstr(dump, file))) {
		entry = strchr(entry, ' ') + 1;
		strncpy(entry, hexdigest, 32);
		assert(freopen(MD5SUM_INDEX, "w", oldpipe));
		assert(fwrite(dump, strlen(dump), sizeof(char), oldpipe));
	} else {
		// there's no entry at all yet
		assert(freopen(MD5SUM_INDEX, "a", oldpipe));
		assert(fwrite(file, strlen(file), sizeof(char), oldpipe));
		assert(fwrite(" ", strlen(" "), sizeof(char), oldpipe));
		assert(fwrite(hexdigest, 32, sizeof(char), oldpipe));
		assert(fwrite("\n", strlen("\n"), sizeof(char), oldpipe));
	}
	free(dump);
	fclose(oldpipe);
}
