/*	slbc-n.h - here we define the number for each bytecode

Copyright (C) 2003 Joshua Charles Campbell
		103 Mary Ave.
		Missoula MT 59801
	
	This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
*/
/* this should actualy be in slbc-m.h */

#include "slbc-structs.h"

#define SLBC_0_0_VERSION		0 /* crazy, the version is 0 when it is 0 */
#define SLBC_0_0_BC_BIT_LENGTH		8 /* eight bit bytes, suprisingly enough */
#define SLBC_ANY_HEADER_VERSION_LENGTH	16 /* two bytes */
#define SLBC_ANY_HEADER_ENDIAN_LENGTH	8
#define SLBC_ANY_HEADER_ECHECK_LENGTH	32
#define SLBC_0_0_HEADER_DEFAULT_SIZE	8 /* metasize... a byte in which to store the
number of bits of the 'actual' size, up to 255 obviously */ 
#define SLBC_0_0_SYM_LENGTH		32
#define SLBC_0_0_LOCAL_NAME_LENGTH	16

/* we define the section types */
#define SLBC_0_0_SECTIONCODE_ROOT	0x00
#define SLBC_0_0_SECTIONCODE_FLOW	0x01
#define SLBC_0_0_SECTIONCODE_MANIFEST	0x02
#define SLBC_0_0_SECTIONCODE_XFORM	0x04
#define SLBC_0_0_SECTIONCODE_LOGICOP	0x05
#define SLBC_0_0_SECTIONCODE_HEADER	0x06
#define SLBC_0_0_SECTIONCODE_BODY	0x07
#define SLBC_0_0_SECTIONCODE_OBJECT	0x08
#define SLBC_0_0_SECTIONCODE_LOGIC	0x09
#define SLBC_0_0_SECTIONCODE_DIM	0x0A
#define	SLBC_0_0_SECTIONCODE_CONTROL	0x0B
#define SLBC_0_0_SECTIONCODE_GLOBAL	0x0C

/* code that is valid anywhere */
#define SLBC_0_0_GLOBALCODE_CONTROL	0xFF	/* creates a control section anywhere */

/* we define the primitive symbolic types */
#define SLBC_0_0_TYPEPRIM_CHAR		0x00000000
#define SLBC_0_0_TYPEPRIM_OBJECT	0x00000001
#define SLBC_0_0_TYPEPRIM_STRUCT	0x00000002
#define SLBC_0_0_TYPEPRIM_INT		0x00000003
#define SLBC_0_0_TYPEPRIM_FLOAT		0x00000004
#define SLBC_0_0_TYPEPRIM_BIT		0x00000005
#define SLBC_0_0_TYPEPRIM_SYMBOL	0x00000006
/*#define SLBC_0_0_TYPEPRIM_INPUT		0x00000007 	/* you should never declare an 'input'  */
/*#define SLBC_0_0_TYPEPRIM_OUTPUT	0x00000008	/* or 'output' */
#define SLBC_0_0_TYPEPRIM_AUTODEF	0x00000009	/* or 'autodefined' -- autodefined is just a
wrapper for saying that the value contains its bytecode definition */
/* decide whether the symbol is system-defined or user-defined throught the top bit 
	so 0x00000005 is the primitive 'bit' while 0x80000005 is user defined */
#define SLBC_0_0_TYPEMASK_PRIM_BIT	0x80000000

/* we define the primitive object manifest rules */
#define SLBC_0_0_MANIFESTCODE_AS	0x00
#define SLBC_0_0_MANIFESTCODE_EXPOSES	0x01
#define SLBC_0_0_MANIFESTCODE_EXTENDS	0x02

/* the flow rules */
#define SLBC_0_0_FLOWCODE_CAUSES	0x00
#define SLBC_0_0_FLOWCODE_WRITES	0x01
#define SLBC_0_0_FLOWCODE_UPDATES	0x02
#define SLBC_0_0_FLOWCODE_SYNCS		0x03

/* the declaration options */
#define SLBC_0_0_DIMCODE_SIZE		0x00
#define SLBC_0_0_DIMCODE_BENDIAN	0x01
#define SLBC_0_0_DIMCODE_SIGNED		0x02
#define SLBC_0_0_DIMCODE_ENCODING	0x03
#define SLBC_0_0_DIMCODE_ARRAY_SIZE	0x04 /* upper index limit defaults to 0 */
#define SLBC_0_0_DIMCODE_ARRAY_UNSIZE	0x05 /* lower index limit defaults to 1 */
#define SLBC_0_0_DIMCODE_DIM		0x06 /* subdim */
#define SLBC_0_0_DIMCODE_STATIC		0x07
#define SLBC_0_0_DIMCODE_VALUE		0x08 /* set the value */
#define SLBC_0_0_DIMCODE_ARRAY_DYNSIZE	0x09
#define SLBC_0_0_DIMCODE_ARRAY_DIM	0x0A
#define SLBC_0_0_DIMCODE_LENDIAN	0x0B
#define SLBC_0_0_DIMCODE_INPUT		0x0C /* these got moved here from */
#define SLBC_0_0_DIMCODE_OUTPUT		0x0D /* typeprim */
/*#define SLBC_0_0_DIMCODE_STRUCT		0x0E*/
#define SLBC_0_0_DIMCODE_PRIMITIVE	0x0F

/* the logic rules */
#define SLBC_0_0_LOGICCODE_FLAG		0x00
#define SLBC_0_0_LOGICCODE_RESULT	0x01
#define SLBC_0_0_LOGICCODE_FOREACH	0x02
#define SLBC_0_0_LOGICCODE_FOR		0x03

/* the logic operators */
#define SLBC_0_0_LOGICOPCODE_AND	0x00
#define SLBC_0_0_LOGICOPCODE_OR		0x01
#define SLBC_0_0_LOGICOPCODE_XOR	0x02
#define SLBC_0_0_LOGICOPCODE_NOT	0x03
#define SLBC_0_0_LOGICOPCODE_EQUALS	0x04
#define SLBC_0_0_LOGICOPCODE_LESSER	0x05
#define SLBC_0_0_LOGICOPCODE_GREATER	0x06
#define SLBC_0_0_LOGICOPCODE_ISA	0x07
#define SLBC_0_0_LOGICOPCODE_HASA	0x08
#define SLBC_0_0_LOGICOPCODE_COMPAT	0x09	/* determine compatability */
#define SLBC_0_0_LOGICOPCODE_CONTENTS	0x0A	/* compare contents */
#define SLBC_0_0_LOGICOPCODE_SUBEXP	0x0B	/* subexpression */
/* the xform instructions */
/* generic format is instruction number_of_in_args in_args num_of_out_args
out_args */
#define SLBC_0_0_XFORMOPCODE_ADD	0x00	/* int and float stuff */
#define SLBC_0_0_XFORMOPCODE_SUBTRACT	0x01
#define SLBC_0_0_XFORMOPCODE_MULTIPLY	0x02
#define SLBC_0_0_XFORMOPCODE_DIVIDE	0x03
#define SLBC_0_0_XFORMOPCODE_RAISE	0x04
#define SLBC_0_0_XFORMOPCODE_ROOT	0x05
#define SLBC_0_0_XFORMOPCODE_INVERT	0x06
/* #define SLBC_0_0_XFORMOPCODE_CAP	0x07	/* char stuff */
/* #define SLBC_0_0_XFORMOPCODE_DECAP	0x08 */
#define SLBC_0_0_XFORMOPCODE_RENCODE	0x09
#define SLBC_0_0_XFORMOPCODE_CLEAN	0x0A
/* #define SLBC_0_0_XFORMOPCODE_SETCODE	0x0B */
#define SLBC_0_0_XFORMOPCODE_NOT	0x0C	/* bit ops */
#define SLBC_0_0_XFORMOPCODE_XOR	0x0D
#define SLBC_0_0_XFORMOPCODE_AND	0x0E
#define SLBC_0_0_XFORMOPCODE_OR		0x0F
#define SLBC_0_0_XFORMOPCODE_LENGTH	0x10 	/* array ops */
#define SLBC_0_0_XFORMOPCODE_SUB	0x11
#define SLBC_0_0_XFORMOPCODE_ROTATEL	0x12
#define SLBC_0_0_XFORMOPCODE_ROTATER	0x13
#define SLBC_0_0_XFORMOPCODE_CRACK	0x14 	/* symbol ops crack open */
#define SLBC_0_0_XFORMOPCODE_EXPOSES	0x15	/* Distill External Struct */
#define SLBC_0_0_XFORMOPCODE_SUBTYPE	0x16	/* Get SubType array */
/* #define SLBC_0_0_XFORMOPCODE_MEMBERS	0x17	/* Number of SubTypes */
#define SLBC_0_0_XFORMOPCODE_SIZE	0x18
#define SLBC_0_0_XFORMOPCODE_HSIZE	0x19
#define SLBC_0_0_XFORMOPCODE_SYMBOLIZE	0x1A	/* conversion ops */
#define SLBC_0_0_XFORMOPCODE_MELT	0x1B
#define SLBC_0_0_XFORMOPCODE_CAST	0x1C
/* #define SLBC_0_0_XFORMOPCODE_CRYSTALIZE	0x1D /* wtf? */
#define SLBC_0_0_XFORMOPCODE_SHOVE	0x1E
#define SLBC_0_0_XFORMOPCODE_FLOAT	0x1F
#define SLBC_0_0_XFORMOPCODE_SINK	0x20

/* header operations */
#define SLBC_0_0_HEADERCODE_CONSTANT	0x00
#define SLBC_0_0_HEADERCODE_INCLUDE	0x01
#define SLBC_0_0_HEADERCODE_INPUT_DIM	0x02
#define SLBC_0_0_HEADERCODE_OUTPUT_DIM	0x03
#define SLBC_0_0_HEADERCODE_SCOPE_DIM	0x04	/* xform internal variable */

/* special codes */
#define	SLBC_0_0_CONTROL_END		0x00 	/* illegal in bytecode files */
#define SLBC_0_0_CONTROL_VALUE		0x01	/* illegal in text, use only in bytecode */
#define SLBC_0_0_CONTROL_ERROR		0x02	/* set error handling behavior */
#define	SLBC_0_0_CONTROL_SUBSECTION	0x03	/* improperly create a section */
#define SLBC_0_0_CONTROL_REMETASIZE	0x04	/* illegal in text, use only in bytecode */


/* the slbc 0.0 file format is as follows */
/* header format is:
version, echeck, sectioncode, sectionsize, section

/* sectioncode length ( subsectioncode length ( ) ) ) */

