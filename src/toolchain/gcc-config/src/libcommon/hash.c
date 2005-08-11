/*
 * C Implementation: hash
 *
 * Description: 
 * Simple hash table.  All keys are char *.  Data is void *.
 *
 * Author: Jeremy Huddleston <eradicator@gentoo.org>
 *
 * Copyright 1999-2005 Gentoo Foundation
 * Distributed under the terms of the GNU General Public License v2
 * See COPYING file that comes with this distribution
 *
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/hash.c,v 1.2 2005/08/11 19:11:25 eradicator Exp $
 * $Log: hash.c,v $
 * Revision 1.2  2005/08/11 19:11:25  eradicator
 * Added test code for hash.c.  Added initializer and destructor for hash.c
 *
 * Revision 1.1  2005/08/09 20:15:46  eradicator
 * Moving components into subdirs to make build environment more tidy.
 *
 * Revision 1.1  2005/08/09 10:42:31  eradicator
 * Added framework for handling configuration files.
 *
 */

#include "hash.h"
#include <stdlib.h>
#include <string.h>

#define MAX_STRLEN 1024

typedef struct {
	char *key;
	void *data;
} _HashPair;

typedef struct {
	unsigned nBuckets; /* Number of buckets */
	unsigned nEntries; /* Number of elements in the table */
	_HashPair *buckets;
} Hash;

static unsigned hashcode(const char *key) {
	/* TODO */
	return 0;
}

static inline unsigned keysAreEqual(const char *a, const char *b) {
	return !strncmp(a, b, MAX_STRLEN);
}

/** Create a new hash table of size size */
Hash *hashNew(unsigned size) {
	Hash *retval = (Hash *)malloc(sizeof(Hash));

	/* Make sure we got memory */
	if(!retval)
		return (Hash *)0;

	retval->size = size;
	retval->buckets = (_HashPair *)calloc(size, sizeof(_HashPair));

	/* Sanity check again */
	if(!retval->buckets) {
		free(retval);
		return (Hash *)0;
	}
}

/** Free the hash table. */
void hashFree(Hash *hash) {
	if(!hash)
		return;

	if(hash->buckets)
		free(hash->buckets);

	free(hash);
}

/** Insert data into the hash table.  If an entry is replaced, we
 *  return the data that was there, so the user can free it if
 *  neccessary.  Otherwise, we return null.
 */
void *hashInsert(Hash *hash, const char *key, void *data) {
	/* TODO: Try to maintain nBuckets >= 2* nEntries */
	return (void *)0;
}

/** Returns the data associated with the given key.  If that key is
 *  not in the hash table, return null.
 */
void *hashGet(Hash *hash, const char *key) {
	/* TODO */
	return (void *)0;
}

/** Return an array of all elements in the hash table sorted by the key.
 *  The array is null terminated, and *length is set to the number of entries
 *  (which is the size of the array - 1) unless a null pointer is passed.
 *  This memory is malloc()d, so do't forget to free it (just the HashPair *)
 */
HashPair *sortedArrayOfHashValues(Hash *hash, int *length) {
	/* TODO */
	return (HashPair *)0;
}

#ifdef DEBUG_HASH
#include <stdio.h>

int main(int argc, char **argv) {
	unsigned i, len;
	HashPair *hp;
	char *tmp;
	Hash *myHash = hashNew(argc*2);
	char key[2];
	key[1] = '\0';

	for(i=1; i < argc; i++) {
		key[0] = argv[i][0];
		tmp = (char *)hashInsert(myHash, key, (void *)(argv[i]));
		if (tmp) {
			printf("%s was overwritten by %s\n", tmp, argv[i]);
		}
	}


	printf("Sorted:");
	hp = sortedArrayOfHashValues(myHash, &len);
	for(i=0; i < len; i++) {
		printf("%s = %s\n", hp->key, (char *)hp->data);
	}
}
#endif
