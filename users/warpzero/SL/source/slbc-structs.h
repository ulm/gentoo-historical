/*	slbc-structs.h C structs used in the other headerfiles

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
/*
static struct keyword_match {
	int kw_matched;
	unsigned long int kw_sectioncode;
	unsigned long int kw_bytecode;
};
*/
struct text_to_bc_table {
	unsigned long int bytecode;
	char en_text[];
};

struct bc_info_table {
	unsigned long int bytecode;
	signed short int in_args; /* -1 means automagic */
	signed short int out_args; 
	signed short int definitive; /* can this operation define something 0=no
	1=yes 2=defined arguments 3=both*/
	signed short int header_vs_body; /* has header for args, body for stuff
	0=no 1=yes 2=args header (each in_ or out_ args !=0 gets an implied 
	header) 3=autodetect args header */
	signed short int useability; /* 1=allow direct use 0=disallow 2=inderect
	named 3=named use */
	signed short int section_change; /* section changes to, -1 for none -2
	for parent (end) -3 for any */
	/* unsigned long int arg_symbol_list[] */
};
