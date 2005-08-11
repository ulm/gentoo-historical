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
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/hash.c,v 1.5 2005/08/11 20:12:06 eradicator Exp $
 * $Log: hash.c,v $
 * Revision 1.5  2005/08/11 20:12:06  eradicator
 * Added missing return statement to hashNew()
 *
 * Revision 1.4  2005/08/11 20:00:11  eradicator
 * Added hashGet and hashInsert.  Cleaned up some bugs elsewhere.
 *
 * Revision 1.3  2005/08/11 19:34:52  eradicator
 * Added more testing code.  Added hashcode().
 *
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

typedef struct _HashEntry {
	char *key;
	void *data;
	struct _HashEntry *next;
} HashEntry;

struct _Hash {
	unsigned nBuckets; /* Number of buckets */
	unsigned nEntries; /* Number of elements in the table */
	HashEntry **buckets;
};

/** Shamelessly taken from the mozilla foundation's PL_HashString.
 *  http://lxr.mozilla.org/mozilla/source/ef/gc/hash/plhash.c#487
 */
static unsigned hashcode(const char *key) {
	unsigned h;
	const char *s;
	h = 0;
	for (s = key; *s; s++)
		h = (h >> 28) ^ (h << 4) ^ *s;
	return h;
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

	retval->nBuckets = size;
	retval->nEntries = 0;
	retval->buckets = (HashEntry **)calloc(size, sizeof(HashEntry *));

	/* Sanity check again */
	if(!retval->buckets) {
		free(retval);
		return (Hash *)0;
	}

	return retval;
}

/** Free the hash table. */
void hashFree(Hash *hash) {
	unsigned i;
	HashEntry *entry, *next;

	if(!hash)
		return;

	if(hash->buckets) {
		for(i=0; i < hash->nBuckets; i++) {
			entry = hash->buckets[i];
			for(entry = hash->buckets[i]; entry; entry = next) {
				if(entry->key)
					free(entry->key);

				next = entry->next;
				free(entry);
			}
		}

		free(hash->buckets);
	}

	free(hash);
}

/** Insert data into the hash table.  If an entry is replaced, we
 *  return the data that was there, so the user can free it if
 *  neccessary.  Otherwise, we return null.
 */
void *hashInsert(Hash *hash, const char *key, void *data) {
	unsigned hc;
	HashEntry *entry;
	void *retval;

	/* Sanity check */
	if(!hash || !key)
		return (void *)0;

	hc = hashcode(key) % hash->nBuckets;

	/* Look for the entry in the table */
	for(entry = hash->buckets[hc]; entry; entry = entry->next) {
		if(keysAreEqual(key, entry->key)) {
			retval = entry->data;
			entry->data = data;
			return retval;
		}
	}

	/* Create our entry */
	entry = (HashEntry *)malloc(sizeof(HashEntry));

	if(!entry) {
		return (void *)0;
	}

	entry->key = (char *)malloc(sizeof(char)*(1 + strlen(key)));
	if(!entry->key) {
		free(entry);
		return (void *)0;
	}
	
	strcpy(entry->key, key);
	entry->data = data;
	entry->next = hash->buckets[hc];

	/* Add it to the table */
	hash->buckets[hc] = entry;
	hash->nEntries++;

	/* TODO: Try to keep nEntries < 2*nBuckets */
	 return (void *)0;
}

/** Returns the data associated with the given key.  If that key is
 *  not in the hash table, return null.
 */
void *hashGet(Hash *hash, const char *key) {
	unsigned hc;
	HashEntry *entry;

	/* Sanity check */
	if(!hash || !key)
		return (void *)0;

	hc = hashcode(key) % hash->nBuckets;

	/* Look for the entry in the table */
	for(entry = hash->buckets[hc]; entry; entry = entry->next) {
		if(keysAreEqual(key, entry->key)) {
			return entry->data;
		}
	}

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
	Hash *myHash = hashNew(argc*2 + 1);
	char key[2];
	key[1] = '\0';

	printf("First letter keys:\n");
	for(i=1; i < argc; i++) {
		key[0] = argv[i][0];
		printf("hashcode(%s) = %u\n", key, hashcode(key));
		tmp = (char *)hashInsert(myHash, key, (void *)(argv[i]));
		if (tmp) {
			printf("%s was overwritten by %s\n", tmp, argv[i]);
		}
	}

	printf("Sorted:\n");
	hp = sortedArrayOfHashValues(myHash, &len);
	if(hp) {
		for(i=0; i < len; i++) {
			printf("%s = %s\n", hp->key, (char *)hp->data);
		}
		free(hp);
	}

	printf("Freeing: ");
	hashFree(myHash);
	printf("ok\n");

	printf("String keys, null data:\n");
	myHash = hashNew(argc*2 + 1);
	for(i=1; i < argc; i++) {
		printf("hashcode(%s) = %u\n", argv[i], hashcode(argv[i]));
		tmp = (char *)hashInsert(myHash, argv[i], (void *)0);
		if (tmp) {
			printf("%s was overwritten by %s\n", tmp, argv[i]);
		}
	}

	printf("Sorted:\n");
	hp = sortedArrayOfHashValues(myHash, &len);
	if(hp) {
		for(i=0; i < len; i++) {
			printf("%s\n", hp->key);
		}
		free(hp);
	}
	
	printf("Freeing: ");
	hashFree(myHash);
	printf("ok\n");
}
#endif
