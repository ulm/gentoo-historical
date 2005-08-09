/*
 * C Header: hash
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
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/Attic/hash.h,v 1.1 2005/08/09 10:42:31 eradicator Exp $
 * $Log: hash.h,v $
 * Revision 1.1  2005/08/09 10:42:31  eradicator
 * Added framework for handling configuration files.
 *
 */

#ifndef _GCC_CONFIG_HASH_H_
#define _GCC_CONFIG_HASH_H_

typedef struct {
	const char *key;
	void *data;
} HashPair;

/* Implementation is internal */
typedef struct _Hash Hash;

/** Create a new hash table of size size */
Hash *newHash(unsigned size);

/** Free the hash table. */
void freeHash(Hash *hash);

/** Return an array of all elements in the hash table sorted by the key.
 *  This memory is malloc()d, so do't forget to free it (just the HashPair *)
 */
HashPair *sortedArrayOfHashValues(Hash *hash);

#endif
