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
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/hash.h,v 1.11 2006/06/21 02:57:57 eradicator Exp $
 * $Log: hash.h,v $
 * Revision 1.11  2006/06/21 02:57:57  eradicator
 * Marking for rc2.
 *
 * Revision 1.10  2005/10/02 20:45:56  eradicator
 * BSD related cleanup.
 *
 * Revision 1.9  2005/09/24 05:47:13  eradicator
 * Added scan_path option (not yet implemented).  When enabled, the PATH envvar will be searched for the executable like it was in gcc-config-1.x
 *
 * Revision 1.8  2005/08/23 02:54:09  eradicator
 * Changed 'gcc' references to 'compiler' since this is not gcc-specific.
 *
 * Revision 1.7  2005/08/21 22:01:02  eradicator
 * Added hashFreeAll() which frees the associated data as well.
 *
 * Revision 1.6  2005/08/21 21:46:53  eradicator
 * Cleaning up some type declarations.
 *
 * Revision 1.5  2005/08/15 21:14:29  eradicator
 * Changed sortedKeys to hashKeysSorted and added hashKeys which provides the data unsorted.  Fixed a bug in the quickSort when the new pivot was 0.
 *
 * Revision 1.4  2005/08/11 21:45:44  eradicator
 * Added sortedKeys() and fixed a bug in hashDel where I forgot to decrepemet nEntries.
 *
 * Revision 1.3  2005/08/11 20:39:38  eradicator
 * added hashDel().
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

#ifndef _COMPILER_CONFIG_HASH_H_
#define _COMPILER_CONFIG_HASH_H_

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#ifdef HAVE_SYS_TYPES_H
#include <sys/types.h>
#endif

/* Implementation is internal */
typedef struct _Hash Hash;

/** Create a new hash table of size size */
Hash *hashNew(size_t size);

/** Free the hash table. */
void hashFree(Hash *hash);

/** Free the hash table, and free() all the data. */
void hashFreeAll(Hash *hash);

/** Insert data into the hash table.  If an entry is replaced, we
 *  return the data that was there, so the user can free it if
 *  neccessary.  Otherwise, we return null.  The key is copied to
 *  memory managed by hash.c.
 */
void *hashInsert(Hash *hash, const char *key, void *data);

/** Returns the data associated with the given key.  If that key is
 *  not in the hash table, return null.
 */
void *hashGet(const Hash *hash, const char *key);

/** Delete a hashtable entry that matches the passed key and return the
 *  data or null if there was none.
 */
void *hashDel(Hash *hash, const char *key);

/** Return an array of all keys hash table. The array is null terminated
 *  This memory is malloc()d, so do't forget to free it.
 *  Additionally, doing a hashDel() could leave this data invalid resulting
 *  in a segfault if you're not careful since the (const char*) are
 *  pointing to memory managed by hash.c
 */
const char **hashKeys(const Hash *hash);

/** Like hashKeys, but sorted */
const char **hashKeysSorted(const Hash *hash);

/* Resize the hash table.  Returns 0 on success. */
int hashResize(Hash *hash, size_t newsize);

#endif
