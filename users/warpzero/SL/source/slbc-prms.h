/*	slbc-parms.h the table for more information about each bytecode

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
#include "slbc-n.h"

static const struct bc_info_table bc_information[12][32] = {
			{ /* root section (  SLBC_0_0_SECTIONCODE_ROOT ) */
			/* opcode, 	in|out|def|hb|use|section */
	{ SLBC_0_0_SECTIONCODE_ROOT,	 0,  0, 0, 0, 0, SLBC_0_0_SECTIONCODE_ROOT	},
	{ SLBC_0_0_SECTIONCODE_FLOW,	-1, -1, 0, 2, 3, SLBC_0_0_SECTIONCODE_FLOW	},
	{ SLBC_0_0_SECTIONCODE_MANIFEST,-1, -1, 0, 0, 0, SLBC_0_0_SECTIONCODE_MANIFEST},
	{ SLBC_0_0_SECTIONCODE_XFORM,	-1, -1, 3, 0, 0, SLBC_0_0_SECTIONCODE_XFORM},
	{ SLBC_0_0_SECTIONCODE_LOGICOP,	 1,  1, 2, 0, 2, SLBC_0_0_SECTIONCODE_LOGICOP},
	{ SLBC_0_0_SECTIONCODE_HEADER,	 0,  0, 0, 0, 0, SLBC_0_0_SECTIONCODE_HEADER},
	{ SLBC_0_0_SECTIONCODE_BODY,	 0,  0, 0, 0, 0, SLBC_0_0_SECTIONCODE_BODY},
	{ SLBC_0_0_SECTIONCODE_OBJECT,	 0,  0, 1, 0, 3, SLBC_0_0_SECTIONCODE_OBJECT},
	{ SLBC_0_0_SECTIONCODE_LOGIC,	-1,  0, 3, 2, 3, SLBC_0_0_SECTIONCODE_LOGIC},
	{ SLBC_0_0_SECTIONCODE_DIM,	 1,  0, 1, 0, 2, SLBC_0_0_SECTIONCODE_DIM},
	{ SLBC_0_0_SECTIONCODE_CONTROL,	 0,  0, 0, 0, 0, SLBC_0_0_SECTIONCODE_CONTROL},
	{ SLBC_0_0_SECTIONCODE_GLOBAL,	 0,  0, 0, 0, 0, SLBC_0_0_SECTIONCODE_GLOBAL}
		},	{ /* flow section */
	{ SLBC_0_0_FLOWCODE_CAUSES,	 1,  1, 0, 0, 1, -1},
	{ SLBC_0_0_FLOWCODE_WRITES,	 1,  1, 0, 0, 1, -1},
	{ SLBC_0_0_FLOWCODE_UPDATES,	 1,  1, 0, 0, 1, -1},
	{ SLBC_0_0_FLOWCODE_SYNCS,	 1,  1, 0, 0, 1, -1}
		},	{ /* manifest section */
	{ SLBC_0_0_MANIFESTCODE_AS,	 1,  1, 1, 0, 3, SLBC_0_0_SECTIONCODE_DIM},
	{ SLBC_0_0_MANIFESTCODE_EXPOSES, 1,  1, 1, 0, 3, -1},
	{ SLBC_0_0_MANIFESTCODE_EXTENDS, 1,  0, 0, 0, 1, -1}
		},	{ /* xform section */
			/* opcode, 	in|out|def|hb|use|section */
	{ SLBC_0_0_XFORMOPCODE_ADD,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_SUBTRACT, 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_MULTIPLY, 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_DIVIDE,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_RAISE,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_ROOT,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_INVERT,	 2,  1, 0, 0, 1, -1},
	/* { SLBC_0_0_XFORMOPCODE_CAP,	},
	{ SLBC_0_0_XFORMOPCODE_DECAP,	}, */
	{ SLBC_0_0_XFORMOPCODE_RENCODE,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_CLEAN,	 2,  1, 0, 0, 1, -1},
	/* { SLBC_0_0_XFORMOPCODE_SETCODE, 	"setcode"	}, */
	{ SLBC_0_0_XFORMOPCODE_NOT,	 1,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_XOR,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_AND,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_OR,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_LENGTH,	 1,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_SUB,	 3,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_ROTATEL,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_ROTATER,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_CRACK,	 1,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_EXPOSES,	 1,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_SUBTYPE,	 1,  1, 0, 0, 1, -1},
	/* { SLBC_0_0_XFORMOPCODE_MEMBERS,"members"	}, */
	{ SLBC_0_0_XFORMOPCODE_SIZE,	 1,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_HSIZE,	 1,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_SYMBOLIZE,1,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_MELT,	 1,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_CAST,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_XFORMOPCODE_SHOVE,	 2,  1, 0, 0, 1, -1}
	/* { SLBC_0_0_XFORMOPCODE_FLOAT,	"float"		},
	{ SLBC_0_0_XFORMOPCODE_SINK,	"sink"		}, */
		},	{ /* logic section */
	{ SLBC_0_0_LOGICOPCODE_AND,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_LOGICOPCODE_OR,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_LOGICOPCODE_XOR,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_LOGICOPCODE_NOT,	 1,  1, 0, 0, 1, -1},
	{ SLBC_0_0_LOGICOPCODE_EQUALS,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_LOGICOPCODE_LESSER,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_LOGICOPCODE_GREATER,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_LOGICOPCODE_ISA,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_LOGICOPCODE_HASA,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_LOGICOPCODE_COMPAT,	 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_LOGICOPCODE_CONTENTS, 2,  1, 0, 0, 1, -1},
	{ SLBC_0_0_LOGICOPCODE_SUBEXP,	 1,  1, 0, 0, 1, SLBC_0_0_SECTIONCODE_LOGICOP},
		},	{ /* header section */
	{ SLBC_0_0_HEADERCODE_CONSTANT,	 1,  0, 1, 0, 3, SLBC_0_0_SECTIONCODE_DIM},
	{ SLBC_0_0_HEADERCODE_INCLUDE,	 1,  0, 0, 0, 1, -1},
	{ SLBC_0_0_HEADERCODE_INPUT_DIM,-1,  0, 1, 0, 1, -1},
	{ SLBC_0_0_HEADERCODE_OUTPUT_DIM,-1, 0, 0, 0, 1, -1},
	{ SLBC_0_0_HEADERCODE_SCOPE_DIM, 1, 0, 1, 0, 3, SLBC_0_0_SECTIONCODE_DIM},
		},	{ /* body section  -- defaults to sectioncode */
		},	{ /* object section -- defaults to sectioncode*/
		},	{ /* logic section */
	{ SLBC_0_0_LOGICCODE_FLAG, 	 0,  0, 1, 0, 3, SLBC_0_0_SECTIONCODE_LOGICOP},
	{ SLBC_0_0_LOGICCODE_RESULT,	-1,  0, 1, 0, 3, -1},
	{ SLBC_0_0_LOGICCODE_FOREACH,	 1,  0, 1, 0, 3, -1},
	{ SLBC_0_0_LOGICCODE_FOR,	 3,  0, 1, 0, 3, -1},
		},	{ /* dim section */
	{ SLBC_0_0_DIMCODE_SIZE,	 1,  0, 0, 0, 1, -1},
	{ SLBC_0_0_DIMCODE_BENDIAN,	 0,  0, 0, 0, 1, -1},
	{ SLBC_0_0_DIMCODE_LENDIAN,	 0,  0, 0, 0, 1, -1},
	{ SLBC_0_0_DIMCODE_SIGNED,	 1,  0, 0, 0, 1, -1},
	{ SLBC_0_0_DIMCODE_ENCODING,	 1,  0, 0, 0, 1, -1},
	{ SLBC_0_0_DIMCODE_ARRAY_SIZE,	 1,  0, 0, 0, 1, -1},
	{ SLBC_0_0_DIMCODE_ARRAY_UNSIZE, 1,  0, 0, 0, 1, -1},
	{ SLBC_0_0_DIMCODE_DIM,		 1,  0, 0, 0, 1, SLBC_0_0_SECTIONCODE_DIM},
	{ SLBC_0_0_DIMCODE_STATIC,	 0,  0, 0, 0, 1, -1},
	{ SLBC_0_0_DIMCODE_VALUE,	 1,  0, 0, 0, 1, -1},
	{ SLBC_0_0_DIMCODE_ARRAY_DYNSIZE,0,  0, 0, 0, 0, -1},
	{ SLBC_0_0_DIMCODE_ARRAY_DIM,	 0,  0, 0, 0, 1, -1},
	{ SLBC_0_0_DIMCODE_INPUT,	 0,  0, 0, 0, 1, -1},
	{ SLBC_0_0_DIMCODE_OUTPUT,	 0,  0, 0, 0, 1, -1},
	{ SLBC_0_0_DIMCODE_PRIMITIVE,	 1,  0, 0, 0, 0, -1},
		},	{ /* control */
	{ SLBC_0_0_CONTROL_END,		 0,  0, 0, 0, 1, -2},
	{ SLBC_0_0_CONTROL_VALUE,	 1,  0, 1, 0, 0, -1},
	{ SLBC_0_0_CONTROL_ERROR,	 0,  0, 0, 0, 0, -1}, /*disabled en temporum */
	{ SLBC_0_0_CONTROL_SUBSECTION,	 0,  0, 0, 0, 0, SLBC_0_0_SECTIONCODE_ROOT},
	{ SLBC_0_0_CONTROL_REMETASIZE,	 0,  0, 0, 0, 0,  0},
		},	{ /* global */
	{ SLBC_0_0_GLOBALCODE_CONTROL,	 0,  0, 0, 0, 1,  SLBC_0_0_SECTIONCODE_CONTROL},
		}
};
