/*	slbc-en.h the table for english to bytecode conversion

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

static const struct text_to_bc_table english_to_reserved_symbol[9] = {
	{ SLBC_0_0_TYPEPRIM_CHAR,	"character"	},
	{ SLBC_0_0_TYPEPRIM_OBJECT,	"object"	},
	{ SLBC_0_0_TYPEPRIM_STRUCT,	"struct"	},
	{ SLBC_0_0_TYPEPRIM_FLOAT,	"float"		},
	{ SLBC_0_0_TYPEPRIM_BIT,	"bit"		},
	{ SLBC_0_0_TYPEPRIM_SYMBOL,	"symbol"	},
/*	{ SLBC_0_0_TYPEPRIM_INPUT,	"input"		},
	{ SLBC_0_0_TYPEPRIM_OUTPUT,	"output"	},
*/	{ SLBC_0_0_TYPEPRIM_AUTODEF,	"autodefine"	},
};

static const struct text_to_bc_table english_to_bc[12][32] = {
			{ /* root section (  SLBC_0_0_SECTIONCODE_ROOT ) */
	{ SLBC_0_0_SECTIONCODE_ROOT,	"root"		},
	{ SLBC_0_0_SECTIONCODE_FLOW,	"flow"		},
	{ SLBC_0_0_SECTIONCODE_MANIFEST,"manifest"	},
	{ SLBC_0_0_SECTIONCODE_XFORM,	"transform"	},
	{ SLBC_0_0_SECTIONCODE_LOGICOP,	"logicop"	},
	{ SLBC_0_0_SECTIONCODE_HEADER,	"header"	},
	{ SLBC_0_0_SECTIONCODE_BODY,	"body"		},
	{ SLBC_0_0_SECTIONCODE_OBJECT,	"object"	},
	{ SLBC_0_0_SECTIONCODE_LOGIC,	"logic"		},
	{ SLBC_0_0_SECTIONCODE_DIM,	"define"	},
	{ SLBC_0_0_SECTIONCODE_CONTROL,	"control"	},
	{ SLBC_0_0_SECTIONCODE_GLOBAL,	"global"	}
		},	{ /* flow section */
	{ SLBC_0_0_FLOWCODE_CAUSES,	"causes"	},
	{ SLBC_0_0_FLOWCODE_WRITES,	"writes"	},
	{ SLBC_0_0_FLOWCODE_UPDATES,	"updates"	},
	{ SLBC_0_0_FLOWCODE_SYNCS,	"syncs"		}
		},	{ /* manifest section */
	{ SLBC_0_0_MANIFESTCODE_AS,	"as"		},
	{ SLBC_0_0_MANIFESTCODE_EXPOSES,"exposes"	},
	{ SLBC_0_0_MANIFESTCODE_EXTENDS,"extends"	}
		},	{ /* xform section */
	{ SLBC_0_0_XFORMOPCODE_ADD,	"add"		},
	{ SLBC_0_0_XFORMOPCODE_SUBTRACT,"subtract"	},
	{ SLBC_0_0_XFORMOPCODE_MULTIPLY,"multiply"	},
	{ SLBC_0_0_XFORMOPCODE_DIVIDE,	"divide"	},
	{ SLBC_0_0_XFORMOPCODE_RAISE,	"raise"		},
	{ SLBC_0_0_XFORMOPCODE_ROOT,	"root"		},
	{ SLBC_0_0_XFORMOPCODE_INVERT,	"invert"	},
	/* { SLBC_0_0_XFORMOPCODE_CAP,	"capitalize"	},
	{ SLBC_0_0_XFORMOPCODE_DECAP,	"decapitalize"	}, */
	{ SLBC_0_0_XFORMOPCODE_RENCODE,	"rencode"	},
	{ SLBC_0_0_XFORMOPCODE_CLEAN,	"clean"		},
	/* { SLBC_0_0_XFORMOPCODE_SETCODE,	"setcode"	}, */
	{ SLBC_0_0_XFORMOPCODE_NOT,	"not"		},
	{ SLBC_0_0_XFORMOPCODE_XOR,	"xor"		},
	{ SLBC_0_0_XFORMOPCODE_AND,	"and"		},
	{ SLBC_0_0_XFORMOPCODE_OR,	"or"		},
	{ SLBC_0_0_XFORMOPCODE_LENGTH,	"length"	},
	{ SLBC_0_0_XFORMOPCODE_SUB,	"sub"		},
	{ SLBC_0_0_XFORMOPCODE_ROTATEL,	"rotateleft"	},
	{ SLBC_0_0_XFORMOPCODE_ROTATER,	"rotateright"	},
	{ SLBC_0_0_XFORMOPCODE_CRACK,	"crackopen"	},
	{ SLBC_0_0_XFORMOPCODE_EXPOSES,	"exposes"	},
	{ SLBC_0_0_XFORMOPCODE_SUBTYPE,	"distill"	},
	/* { SLBC_0_0_XFORMOPCODE_MEMBERS,"members"	}, */
	{ SLBC_0_0_XFORMOPCODE_SIZE,	"size"		},
	{ SLBC_0_0_XFORMOPCODE_HSIZE,	"definitionsize"},
	{ SLBC_0_0_XFORMOPCODE_SYMBOLIZE,"symbolize"	},
	{ SLBC_0_0_XFORMOPCODE_MELT,	"melt"		},
	{ SLBC_0_0_XFORMOPCODE_CAST,	"crystalize"	},
	{ SLBC_0_0_XFORMOPCODE_SHOVE,	"shove"		}
	/* { SLBC_0_0_XFORMOPCODE_FLOAT,	"float"		},
	{ SLBC_0_0_XFORMOPCODE_SINK,	"sink"		}, */
		},	{ /* logic section */
	{ SLBC_0_0_LOGICOPCODE_AND,	"and"		},
	{ SLBC_0_0_LOGICOPCODE_OR,	"or"		},
	{ SLBC_0_0_LOGICOPCODE_XOR,	"xor"		},
	{ SLBC_0_0_LOGICOPCODE_NOT,	"not"		},
	{ SLBC_0_0_LOGICOPCODE_EQUALS,	"equals"	},
	{ SLBC_0_0_LOGICOPCODE_LESSER,	"lesser"	},
	{ SLBC_0_0_LOGICOPCODE_GREATER,	"greater"	},
	{ SLBC_0_0_LOGICOPCODE_ISA,	"isa"		},
	{ SLBC_0_0_LOGICOPCODE_HASA,	"hasa"		},
	{ SLBC_0_0_LOGICOPCODE_COMPAT,	"compatible"	},
	{ SLBC_0_0_LOGICOPCODE_CONTENTS,"contents"	},
	{ SLBC_0_0_LOGICOPCODE_SUBEXP,	"begin"	},
		},	{ /* header section */
	{ SLBC_0_0_HEADERCODE_CONSTANT,	"constant"	},
	{ SLBC_0_0_HEADERCODE_INCLUDE,	"include"	},
	{ SLBC_0_0_HEADERCODE_INPUT_DIM,"input"		},
	{ SLBC_0_0_HEADERCODE_OUTPUT_DIM,"output"	},
	{ SLBC_0_0_HEADERCODE_SCOPE_DIM,"dim"	},
		},	{ /* body section  -- defaults to sectioncode */
		},	{ /* object section -- defaults to sectioncode*/
		},	{ /* logic section */
	{ SLBC_0_0_LOGICCODE_FLAG,	"flag"		},
	{ SLBC_0_0_LOGICCODE_RESULT,	"result"	},
	{ SLBC_0_0_LOGICCODE_FOREACH,	"foreach"	},
	{ SLBC_0_0_LOGICCODE_FOR,	"for"		},
		},	{ /* dim section */
	{ SLBC_0_0_DIMCODE_SIZE,	"size"		},
	{ SLBC_0_0_DIMCODE_BENDIAN,	"bigendian"	},
	{ SLBC_0_0_DIMCODE_LENDIAN,	"littleendian"	},
	{ SLBC_0_0_DIMCODE_SIGNED,	"signed"	},
	{ SLBC_0_0_DIMCODE_ENCODING,	"encoding"	},
	{ SLBC_0_0_DIMCODE_ARRAY_SIZE,	"arraysize"	},
	{ SLBC_0_0_DIMCODE_ARRAY_UNSIZE,"arrayunsize"	},
	{ SLBC_0_0_DIMCODE_DIM,		"dim"		},
	{ SLBC_0_0_DIMCODE_STATIC,	"static"	},
	{ SLBC_0_0_DIMCODE_VALUE,	"value"		},
	{ SLBC_0_0_DIMCODE_ARRAY_DYNSIZE,"dynamic"	},
	{ SLBC_0_0_DIMCODE_ARRAY_DIM,	"array"		},
	{ SLBC_0_0_DIMCODE_INPUT,	"input"		},
	{ SLBC_0_0_DIMCODE_OUTPUT,	"output"	},
	{ SLBC_0_0_DIMCODE_PRIMITIVE,	"primitive"	},
		},	{ /* control */
	{ SLBC_0_0_CONTROL_END,		"end"		},
	{ SLBC_0_0_CONTROL_VALUE,	"value"		},
	{ SLBC_0_0_CONTROL_ERROR,	"error"		},
	{ SLBC_0_0_CONTROL_SUBSECTION,	"subsection"	},
	{ SLBC_0_0_CONTROL_REMETASIZE,	"remetasize"	},
		},	{ /* global */
	{ SLBC_0_0_GLOBALCODE_CONTROL,	"control"	},
		}
};
