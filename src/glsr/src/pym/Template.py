# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Template.py,v 1.6 2004/08/22 23:23:39 hadfield Exp $
#

"""
The template handler module.
"""

import string
import re
import types

from Logging import err

__modulename__ = "Template"

class Template:
    """Template handler class."""

    def __init__(self):
        
        self._template_name = ""
        self._contents = []
        self._output = []
        self._loops = {}
        self._terms = {}

    def _read(self):
        """Load the content of the template file into self.contents."""
        
        try:
            self._contents = open(self._template_name, "r").readlines()
            
        except IOError, errmsg:
            raise TemplateError, errmsg

        return self._contents
	
    def clear(self):
        """Re-initializes all of the template variables."""
        
        self._template_name = ""
        self._contents = []
        self._output = []
	
    def _process_loops(self, file_content, loops):
        """Processes all top level loops.
        
        Returns 'file_content' with all loops processed.
        """
        
        return self._process_tags(file_content, loops, "LOOP",
                                  lambda x,y: self._process_loop(x, y))

    def _process_ifs(self, file_content, terms):
        """Process all IF tags."""
        
        return self._process_tags(file_content, terms, "IF",
                                  lambda x,y: self._process_if(x, y))

    def _process_tags(self, file_content, terms, tag, function):
        """Replaces all variables in file_content with their actual value."""
        
        tag_open = "{%s " % tag
        tag_close = "{!%s}" % tag

        working_file = file_content
        start = string.find(working_file, tag_open)
        
        while (start != -1):
            
            # Find the end of the tag
            end = self._find_tag_close(working_file[start + len(tag_open):], 0,
                                      tag) + start + len(tag_open)

            # Process that tag
            tag_content = function(working_file[start + len(tag_open):end],
                                   terms)

            working_file = (working_file[:start] + tag_content +
                            working_file[end + len(tag_close):])

            # Find the beginning of the next loop
            start = string.find(working_file, tag_open)


        return working_file

    def _find_tag_close(self, file_content, nest, tag):
        """Recursively finds/returns the location of the matching {!TAG}."""
        
        tag_open = "{%s " % tag
        tag_close = "{!%s}" % tag

        next_open = string.find(file_content, tag_open)
        next_close = string.find(file_content, tag_close)

        if next_close < next_open or next_open == -1:
            
            # No new loops were found
            if nest == 0:
                # Yay! We found the final loop closing tag
                return next_close
            else:
                # A nested !loop found, decrement the nest count
                start = next_close + len(tag_close)
                return start + self._find_tag_close(file_content[start:],
                                                   nest - 1, tag)
            
        else:
            
            # A new nested loop found, increment the nest count.
            start = next_open + len(tag_open)
            return start + self._find_tag_close(file_content[start:],
                                               nest + 1, tag)

    def _process_loop(self, file_content, loops):
        """Returns the content inside the loop (after processing).

        It expects 'file_content' to be the content between (exlusively)
        '{LOOP ' and '{!LOOP}'.
        The nested-most loop is processed first.
        """

        # loop_name is the loop tag name
        loop_name = file_content[:string.find(file_content, "}")].strip()

        # loop_text is the content within the {LOOP}{!LOOP} tags.
        loop_text = file_content[string.find(file_content, "}") + 1:]

        next_open = string.find(file_content, "{LOOP ")
        if next_open != -1:
            # A nested LOOP exists, so recurse futher.
            loop_text = self._process_loops(loop_text, loops)

        # No more nested loops, so we can process this one.
        if loop_name not in loops.keys():
            raise TemplateError, "Loop %s is not defined." % loop_name

        # FIXME:
        # The following four statements are used for finding and replacing
        # tags within the IF tag (i.e. {IF TAG1 == TAG2}).
        # This is *very* hard to read and really needs to be cleaned up.

        # regx for {IF VAR1 == literal_string}
        std_if = re.compile(
            '({IF +)([\w\-_"\']+)( *[!=<>]+ *)([\w\-_"\']+)( *})')
        
        # regx for {IF LOOP1.var1 == literal_string}
        complex_if = re.compile('({IF +)([\w\-_"\']+.[\w\-_"\']+)' +
                                '( *[!=<>]+ *)([\w\-_"\']+.[\w\-_"\']+)( *})')

        # Note: Because repl_func and repl_func2 are called within the 'for'
        # loop below the 'i' and loop_index are actually valid variables.
        repl_func = lambda x: (re.sub('([ !=<>]+)%s|%s([ !=<>]+)' %
                                      (loop_name, loop_name),
                                      "\\1%s" % loops[loop_name][i],
                                      x.group()))
        
        repl_func2 = lambda x: (
            re.sub('([ !=<>]+)%s.%s|%s.%s([ !=<>]+)' %
                   (loop_name, loop_index, loop_name, loop_index), "\\1%s" %
                   loops[loop_name][i][loop_index], x.group()))

        loop_str = ""
        for i in range(0, len(loops[loop_name])):
            """This loop does the actual tag replacement with the
            appropriate values."""

            tmp_text = loop_text
            dot = tmp_text.find("{%s." % loop_name)
            match_obj = None
            
            if dot == -1:
                # If a {loop_name. string wasn't found, look for {IF loopname.
                match_obj = re.search('({IF +)(%s.)([\w\-_"\']+)' %
                                      loop_name, tmp_text)
            
            while dot != -1 or match_obj is not None:
                """Replace all multi-dimensional loop tags."""

                if dot != -1:
                    start = dot + len(loop_name) + 2
                    end = tmp_text.find("}", start)

                else:
                    start = tmp_text.find(match_obj.group(0)) + \
                            len(match_obj.group(1)) - 1 + \
                            len(match_obj.group(2)) + 1

                    end = start + len(match_obj.group(3))

                loop_index = tmp_text[start:end].strip()
                inner_val = loops[loop_name][i][loop_index]

                new_text = tmp_text.replace("{%s.%s}" %
                                            (loop_name, loop_index),
                                            "%s" % inner_val)
                
                # Replace and tags.index within the {IF } tag
                new_text = complex_if.sub(repl_func2, new_text)

                # Adjust the position accordingly
                # Evaluate the new start position by subtracting (len(tmp_text)
                # - len(new_text)) (which should put us to the start
                # of the inserted variable) and then add then length of the
                # inserted variable to that.

                start -= (len(tmp_text) - len(new_text)) + len(str(inner_val))
                tmp_text = new_text

                dot = tmp_text.find("{%s." % loop_name, start)
            
                if dot == -1:
                    match_obj = re.search('({IF +)(%s.)([\w\-_"\']+)' %
                                          loop_name, tmp_text)

            # Replace and tags within the {IF } tag
            tmp_text = std_if.sub(repl_func, tmp_text)

            # This is to replace simple loops.
            loop_str = (loop_str +
                        tmp_text.replace("{%s}" % loop_name,
                                         "%s" % loops[loop_name][i]))
        
        return loop_str

    def _process_if(self, file_content, terms):
        """Returns the processed {IF}{!IF} text.

        file_content contains everything between '{IF' and '{!IF}'.
        """
        
        next_open = string.find(file_content, "{IF ")

        if_text = file_content[string.find(file_content, "}") + 1:]

        if next_open != -1:
            if_text = self._process_ifs(if_text, terms)

        # Find any else's
        else_text = ""
        else_pos = if_text.find("{ELSE}")
        if else_pos != -1:
            else_text = if_text[else_pos + 6:]
            if_text = if_text[:else_pos]


        stmt = file_content[:file_content.find("}")].strip()
        tag = stmt[:stmt.find(" ")]

        # Set the operator
        oper = stmt[stmt.find(" "):].strip(" ")
        oper = oper[:oper.find(" ")].strip()

        def setVal(val):
            """Sets the appropriate literal value for a term."""
            
            if val not in terms.keys():
                return val.strip("\"' ")
            else:
                return "%s" % terms[val]

        # Set the value to the right of the operator
        valueR = setVal(stmt[string.rfind(stmt, " "):].strip())

        # Set the value to the left of the operator
        valueL = setVal(tag)

        if ((oper == "==" and valueL == valueR) or
            (oper == "!=" and valueL != valueR) or
            (oper == "<" and int(valueL) < int(valueR)) or
            (oper == ">" and int(valueL) > int(valueR))):
            return if_text
        else:
            return else_text

    def compile(self, template_name, terms = None, loops = None):
        """Processes the template.
        
        'terms' should be a dictionary of {TAG: value} pairs where value
        will replace the text {TAG} in the specified template file.

        'loops' should be a dictionary of {LOOPTAG: list} pairs. The template
        file will have some text such as the following, but all that will be
        displayed is "this is loop X" len(list) times.
        {LOOP MYLOOP}
        this is loop {MYLOOP}
        {!LOOP}
        Note: {MYLOOP} is replaced with list[i] where 'i' is the current
              iteration.

        If statements are as follows:
        {IF TAG == "value"}
        {TAG} is equal to value
        {!IF}
        Note: The currently supported operators are
          ==  !=  >

        Note: Everything is case sensitive
        """

        self._template_name = template_name
        self._read()

        if terms is not None:
            self._terms.update(terms)

        if loops is not None:
            self._loops.update(loops)

        full_file = string.join(self._contents);

        # Process all non LOOP, non IF tags
        for term in self._terms.keys():

            # Convert all dict terms
            if type(self._terms[term]) == types.DictType:
                for index in self._terms[term].keys():
                    full_file = string.replace(full_file, "{%s.%s}" %
                                               (term, index), "%s" %
                                               (self._terms[term][index]))

            # Convert all simple terms
            else:
                full_file = string.replace(full_file, "{%s}" % term,
                                           "%s" % self._terms[term])

        # Process all LOOP tags
        full_file = self._process_loops(full_file, self._loops)

        # Process all IF tags
        full_file = self._process_ifs(full_file, self._terms)
        
        self._output = string.split(full_file, "\n")


    def param(self, key, value, param_type = "term"):
        """Add a new parameter, either a 'loop' or a 'term'."""
        
        if string.lower(param_type) in ("l", "loop"):
            self._loops.update({key: value})
        elif string.lower(param_type) in ("t", "term"):
            self._terms.update({key: value})


    def output(self):
        """Returns the resulting template."""

        if self._template_name == "":
            raise TemplateError, "No compiled template data found."

        return "\n".join(self._output)
    

class TemplateError(Exception):
    """The standard template exception."""
    
    def __init__(self, errmsg = ""):
        
        self.errmsg = errmsg

    def __str__(self):

        import sys
        err(self.errmsg, __modulename__)            
        sys.exit(1)

