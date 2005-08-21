/*
 * C Header: sort
 *
 * Description:
 * QuickSort
 *
 * Author: Jeremy Huddleston <eradicator@gentoo.org>
 *
 * Copyright 1999-2005 Gentoo Foundation
 * Distributed under the terms of the GNU General Public License v2
 * See COPYING file that comes with this distribution
 *
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/sort.h,v 1.1 2005/08/21 21:25:39 eradicator Exp $
 * $Log: sort.h,v $
 * Revision 1.1  2005/08/21 21:25:39  eradicator
 * Moved sorting code to a separate file.
 *
 */

#ifndef _GCC_CONFIG_SORT_H_
#define _GCC_CONFIG_SORT_H_

typedef int (*CompareFun)(const void *, const void *);

void **quickSort(void **data, size_t left, size_t right, CompareFun compareFun);
char **quickSortStr(char **data, size_t left, size_t right);

#endif /* _GCC_CONFIG_SORT_H_ */
