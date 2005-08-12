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
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/hash.c,v 1.9 2005/08/12 09:46:30 eradicator Exp $
 * $Log: hash.c,v $
 * Revision 1.9  2005/08/12 09:46:30  eradicator
 * Style cleanup.
 *
 * Revision 1.8  2005/08/11 21:55:46  eradicator
 * Added configure check for inline.
 *
 * Revision 1.7  2005/08/11 21:45:44  eradicator
 * Added sortedKeys() and fixed a bug in hashDel where I forgot to decrepemet nEntries.
 *
 * Revision 1.6  2005/08/11 20:39:38  eradicator
 * added hashDel().
 *
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
#include <stdio.h>

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

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
	if(retval == NULL)
		return NULL;

	retval->nBuckets = size;
	retval->nEntries = 0;
	retval->buckets = (HashEntry **)calloc(size, sizeof(HashEntry *));

	/* Sanity check again */
	if(retval->buckets == NULL) {
		free(retval);
		return NULL;
	}

	return retval;
}

/** Free the hash table. */
void hashFree(Hash *hash) {
	unsigned i;
	HashEntry *entry, *next;

	if(hash == NULL)
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
	if(hash == NULL || key == NULL)
		return NULL;

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

	if(entry == NULL) {
		return NULL;
	}

	entry->key = (char *)malloc(sizeof(char)*(1 + strlen(key)));
	if(entry->key == NULL) {
		free(entry);
		return NULL;
	}
	
	strcpy(entry->key, key);
	entry->data = data;
	entry->next = hash->buckets[hc];

	/* Add it to the table */
	hash->buckets[hc] = entry;
	hash->nEntries++;

	/* TODO: Try to keep nEntries < 2*nBuckets */
	 return NULL;
}

/** Returns the data associated with the given key.  If that key is
 *  not in the hash table, return null.
 */
void *hashGet(Hash *hash, const char *key) {
	unsigned hc;
	HashEntry *entry;

	/* Sanity check */
	if(hash == NULL || key == NULL)
		return NULL;

	hc = hashcode(key) % hash->nBuckets;

	/* Look for the entry in the table */
	for(entry = hash->buckets[hc]; entry; entry = entry->next) {
		if(keysAreEqual(key, entry->key)) {
			return entry->data;
		}
	}

	return NULL;
}

/** Delete a hashtable entry that matches the passed key and return the
 *  data or null if there was none.
 */
void *hashDel(Hash *hash, const char *key) {
	unsigned hc;
	HashEntry *entry, *prev = (HashEntry *)0;
	void *retval;

	/* Sanity check */
	if(hash == NULL || key == NULL)
		return NULL;

	hc = hashcode(key) % hash->nBuckets;

	/* Look for the entry in the table */
	for(entry = hash->buckets[hc]; entry; prev = entry, entry = entry->next) {
		if(keysAreEqual(key, entry->key)) {
			/* Remove it from the table */
			if(prev) {
				/* Not the head */
				prev->next = entry->next;
			} else {
				/* head */
				hash->buckets[hc] = entry->next;
			}
			hash->nEntries--;

			/* Free the memory */
			retval = entry->data;
			if(entry->key)
				free(entry->key);
			free(entry);

			return retval;
		}
	}

	return NULL;
}

static inline void quickSortSwap(char **data, unsigned i, unsigned j) {
	char *tmp = data[i];
	data[i] = data[j];
	data[j] = tmp;
}

static unsigned quickSortPartition(char **data, unsigned left, unsigned right, unsigned pivotIndex) {
	char *pivotValue = data[pivotIndex];
	unsigned newPivotIndex = left;
	unsigned i;
	
	/* Move the pivot to the end to get it out of the way */
	quickSortSwap(data, pivotIndex, right);
	
	for(i=left; i < right; i++) {
		if(strncmp(data[i], pivotValue, MAX_STRLEN) <= 0) {
			quickSortSwap(data, newPivotIndex, i);
			newPivotIndex++;
		}
	}

	/* Move pivot back */
	quickSortSwap(data, newPivotIndex, right);

	return newPivotIndex;
}

static char **quickSort(char **data, unsigned left, unsigned right) {
	char *pivotValue;
	unsigned oldPivotIndex, newPivotIndex;
	
	if(right > left) {
		oldPivotIndex = left + (right - left)/2;
		pivotValue = data[oldPivotIndex];

		newPivotIndex = quickSortPartition(data, left, right, oldPivotIndex);

		quickSort(data, left, newPivotIndex-1);
		quickSort(data, newPivotIndex+1, right);
	}
	return data;
}

/** Return an array of all keys hash table sorted. The array is null
 *  terminated. This memory is malloc()d, so do't forget to free it.
 *  Additionally, doing a hashDel() could leave this data invalid resulting
 *  in a segfault if you're not careful since the (const char*) are
 *  pointing to memory managed by hash.c
 */
const char **sortedKeys(Hash *hash) {
	char **keys = (char **)malloc(sizeof(char *) * (hash->nEntries + 1));
	HashEntry *entry;
	unsigned i, hc;

	/* Make sure we've got our memory */
	if(keys == NULL) {
		return NULL;
	}

	for(i=0, hc=0; hc < hash->nBuckets; hc++) {
		for(entry=hash->buckets[hc]; entry; entry = entry->next) {
			if(i >= hash->nEntries) {
				/* This should never happen. */
				fprintf(stderr, "Data inconsistency. hash->nEntries is not correct.");
				exit(1);
			}

			keys[i] = entry->key;
			i++;
		}
	}

	if(i != hash->nEntries) {
		/* This should never happen. */
		fprintf(stderr, "Data inconsistency. hash->nEntries is not correct.");
		exit(1);
	}

	/* Null terminate */
	keys[i] = NULL;

	return (const char **)quickSort(keys, 0, hash->nEntries - 1);
}

#ifdef DEBUG_HASH

int main(int argc, char **argv) {
	unsigned i;
	const char **keys;
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
	keys = sortedKeys(myHash);
	if(keys) {
		for(i=0; i < myHash->nEntries; i++) {
			printf("%s = %s\n", keys[i], (char *)hashGet(myHash,keys[i]));
		}
		free(keys);
	}

	printf("Freeing: ");
	hashFree(myHash);
	printf("ok\n");

	printf("String keys, null data:\n");
	myHash = hashNew(argc*2 + 1);
	for(i=1; i < argc; i++) {
		printf("hashcode(%s) = %u\n", argv[i], hashcode(argv[i]));
		tmp = (char *)hashInsert(myHash, argv[i], NULL);
		if (tmp) {
			printf("%s was overwritten by %s\n", tmp, argv[i]);
		}
	}

	printf("Sorted:\n");
	keys = sortedKeys(myHash);
	if(keys) {
		for(i=0; i < myHash->nEntries; i++) {
			printf("%s\n", keys[i]);
		}
		free(keys);
	}

	printf("Freeing: ");
	hashFree(myHash);
	printf("ok\n");

	return 0;
}
#endif
