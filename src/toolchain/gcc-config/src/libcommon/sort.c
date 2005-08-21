/*
 * C Implementation: sort
 *
 * Description: 
 *
 *
 * Author: Jeremy Huddleston <eradicator@gentoo.org>
 *
 * Copyright 1999-2005 Gentoo Foundation
 * Distributed under the terms of the GNU General Public License v2
 * See COPYING file that comes with this distribution
 *
 * $Header: /var/cvsroot/gentoo/src/toolchain/gcc-config/src/libcommon/Attic/sort.c,v 1.1 2005/08/21 21:25:39 eradicator Exp $
 * $Log: sort.c,v $
 * Revision 1.1  2005/08/21 21:25:39  eradicator
 * Moved sorting code to a separate file.
 *
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <stdlib.h>
#include <string.h>

#include "sort.h"

#ifndef MAX_STRLEN
#define MAX_STRLEN 1023
#endif

inline static void quickSortSwap(void **data, size_t i, size_t j) {
	void *tmp = data[i];
	data[i] = data[j];
	data[j] = tmp;
}

static size_t quickSortPartition(void **data, size_t left, size_t right, size_t pivotIndex, CompareFun compareFun) {
	void *pivotValue = data[pivotIndex];
	size_t newPivotIndex = left;
	size_t i;
	
	/* Move the pivot to the end to get it out of the way */
	quickSortSwap(data, pivotIndex, right);
	
	for(i=left; i < right; i++) {
		if(compareFun(data[i], pivotValue) <= 0) {
			quickSortSwap(data, newPivotIndex, i);
			newPivotIndex++;
		}
	}

	/* Move pivot back */
	quickSortSwap(data, newPivotIndex, right);

	return newPivotIndex;
}

void **quickSort(void **data, size_t left, size_t right, CompareFun compareFun) {
	void *pivotValue;
	size_t oldPivotIndex, newPivotIndex;
	
	if(right > left) {
		oldPivotIndex = left + (right - left)/2;
		pivotValue = data[oldPivotIndex];

		newPivotIndex = quickSortPartition(data, left, right, oldPivotIndex, compareFun);

		if(newPivotIndex > left)
			quickSort(data, left, newPivotIndex-1, compareFun);
		quickSort(data, newPivotIndex+1, right, compareFun);
	}
	return data;
}

inline static int strCompareFun(const void *l, const void *r) {
	return strncmp((const char *)l, (const char *)r, MAX_STRLEN);
}

inline char **quickSortStr(char **data, size_t left, size_t right) {
	return (char **)quickSort((void **)data, left, right, strCompareFun);
}
