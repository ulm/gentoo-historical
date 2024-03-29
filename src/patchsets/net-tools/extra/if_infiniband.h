/*
 * This software is available to you under a choice of one of two
 * licenses.  You may choose to be licensed under the terms of the GNU
 * General Public License (GPL) Version 2, available at
 * <http://www.fsf.org/copyleft/gpl.html>, or the OpenIB.org BSD
 * license, available in the LICENSE.TXT file accompanying this
 * software.  These details are also available at
 * <http://openib.org/license.html>.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * Copyright (c) 2004 Topspin Communications.  All rights reserved.
 *
 * $Id: if_infiniband.h,v 1.2 2005/03/16 23:47:34 vapier Exp $
 */

/* 
 * this is a slightly touched up version of the header 
 * found in linux-2.6 ... the point is to make sure it 
 * allows for all systems to build properly.  This 
 * includes glibc-2.2.x, uclibc, etc...
 */

#ifndef _LINUX_IF_INFINIBAND_H
#define _LINUX_IF_INFINIBAND_H

#define INFINIBAND_ALEN		20	/* Octets in IPoIB HW addr	*/

#ifndef ARPHRD_INFINIBAND
#define ARPHRD_INFINIBAND 32
#endif

#endif /* _LINUX_IF_INFINIBAND_H */
