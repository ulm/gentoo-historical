# Copyright 2004-2005 Ian Leitch
# Copyright 2004-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#

"""The template handler module.

General Info:

There are two types of values you can pass to the template module, 'terms' and
'loops'. Term variables should not be a SequenceType. Loops should be
sequences. Loops can also be sequences of dicts to allow for more complex
variables within loops. You can set variables one of two ways:

1. Use the param('PARAM_NAME', term_val, 'term') function - This will replace
all occurrences of {PARAM_NAME} in the template with the value of term_val. The
last parameter 'term', is used to specifiy if this variable is a term or a
loop.

2. Use the compile('template_path', term_dict, loop_dict) - This will pass a
set of terms and loops to the template object. Compile is the last function
generally executed before the template is printed.

This module also uses caching to speed up template creation. You can disable
the caching by setting _use_cache = False. Also, remember to clean out the
template cache folder as you'll probably get some stale cache files. If you
only want a specific template to not be cached then pass cache = False to the
compile() function. Note that the compile() cache parameter will only override
the _use_cache variable if _cache_override is set to True.


Loops:

To use a loop in your template, you can either do something like:
  {LOOP MYLOOP}
  this is loop {MYLOOP}
  {!LOOP}

If you have the loop {'MYLOOP': range(1, 10)}, then the above will print out
'this is loop X' 10 times. You can also use a more complex loop, say 'MYLOOP'
is set to [{'val1': 1.1, 'val2': 1.2}, {'val1': 2.1, 'val2': '2.2'}], then
  {LOOP MYLOOP}
  loop values: val1 = {MYLOOP.val1}, val2 = {MYLOOP.val2}
  {!LOOP}

will output:
loop values: val1 = 1.1, val2 = 1.2
loop values: val1 = 2.1, val2 = 2.2


Ifs:

If statements can be used as follows:
{IF TAG == 'value'}
  {TAG} is equal to 'value'
{!IF}

The currently supported operators include:
== !=  > <

"""

__revision__ = '$Id: template.py,v 1.1 2005/03/27 04:02:34 hadfield Exp $'
__modulename__ = 'template'

import md5
import os
import re
import string
import thread

import config
#from GLSRException import TemplateModuleError
#from Logging import logwrite

class Template:
    """Template handler class."""

    def __init__(self):
        
        self._template_loc = ""
        self._contents = []
        self._output = []
        self._loops = {}
        self._terms = {}

        # Do you want to use template caching?
        self._use_cache = True

        # Do you want the compile() cache parameter to override _use_cache?
        self._cache_override = True
        
        # These are the template languages keywords. You can't have a parameter
        # with the same name as a keyword.
        self._keywords = ("ELSE",)

        # The standard regex to match template variables. This should match
        # all alphanumeric strings with potentially embedded .'s (dot's).
        self._var_regex = r'\w+(?:\.\w+)?\w*'

        # The literal regex to match strings and digits
        self._literal_regex = r'"[^"]*"|"?\d+"?'

    def _read(self):
        """Load the content of the template file into self.contents."""
        
        try:
            self._contents = open(self._template_loc, "r").readlines()
            
        except IOError, errmsg:
            raise TemplateModuleError('Caught an IOError exception', errmsg)

        return self._contents
	
    def _sub(self, variable, repl_text, values, index = -1):
        """Substitute all occurences of 'variable' in repl_text with the value.

        The value is obtained by evaluating 'variable' against 'values'. Values
        might be self._terms or self._loops. 'index' is used during loops to
        define what loop iteration we're on and return the appropriate array
        value.
        """

        dot_loc = variable.find(".")
        if dot_loc != -1 and values.has_key(variable[:dot_loc]):

            param_name = variable[:dot_loc]
            # This will build a "python compatible" list to access the dict
            # i.e. ['var1']['var2']
            rest = "['%s']" % variable[dot_loc + 1:].replace(".", "']['")

            if index != -1:
                rest = "[%s]" % index + rest

            try:
                value = eval("values[param_name]%s" % rest)
            except KeyError, errmsg:
                raise TemplateModuleError('Caught an KeyError exception',
                                          errmsg)
            
            # Convert value to a string and then do the replace.
            repl_text = repl_text.replace("{%s}" % variable, "%s" % value)
            
        elif values.has_key(variable):

            if index == -1:
                repl_text = repl_text.replace("{%s}" % variable,
                                              "%s" % values[variable])
            else:
                repl_text = repl_text.replace("{%s}" % variable,
                                              "%s" % values[variable][index])

        return repl_text
        
    def clear(self):
        """Re-initializes all of the template variables."""
        
        self._template_loc = ""
        self._contents = []
        self._output = []
	
    def compile(self, template_loc, terms = None, loops = None, cache = None):
        """Processes the template.

        This includes 4 steps, stripping out the comments, replacing all
        simple variables (i.e. {VAR} or {VAR.sub1}), evaluating all LOOPs,
        and evaluating all IFs.
        """

        if self._cache_override == True and cache is not None:
            self._use_cache = cache
        
        digest_str = str(template_loc) + str(terms) + str(loops)
        digest = md5.new(digest_str).hexdigest()

        if self._check_cache(digest) and self._use_cache:
            self._read_cache(digest)
        
        else:
            self._template_loc = template_loc
            self._read()

            if terms is not None:
                for name, term in terms.iteritems():
                    self.param(name, term, "term")

            if loops is not None:
                for name, loop in loops.iteritems():
                    self.param(name, loop, "loop")

            full_file = string.join(self._contents);

            # Strip out all comments
            full_file = re.sub(r'(?s)\{\*.*?\*\}', '', full_file)

            # Process all variable tags (i.e. non LOOP, non IF tags)
            full_file = self._evaluate_vars(full_file)

            # Evaluate all LOOPs and their nested IFs
            full_file = self._evaluate_loops(full_file)

            # Evaluate the rest of the IFs that weren't in any loops
            full_file = self._evaluate_ifs(full_file)

            # Build the output variable
            self._output = string.split(full_file, "\n")

            if self._use_cache:
                # Write cache file
                thread.start_new_thread(self._write_cache, (digest,))

    def _add_tmpl_values(self, loop):
        """Adds values to the loop to make loops easier to use.

        Each loop automatically gets an '_is_odd', '_is_even', '_counter'
        variable. If that variable is already set it will be overridden.
        This only applies to multi-dimentional loops.
        """

        from types import DictType

        for i in range(0, len(loop)):
            if type(loop[i]) is DictType:
                loop[i]['_counter'] = i
                loop[i]['_is_odd'] = i % 2
                loop[i]['_is_even'] = int(not i % 2)
        
        return loop

    def _evaluate_vars(self, content):
        """Evaluate all variable tags."""
        
        # This regex will find all parameters that are of the form:
        # {VAR} or {VAR.var} or {VAR.var1.var2} or ...
        variables = re.findall(r'\{((?:%s)+)\}' % self._var_regex, content)
        variables = filter(lambda x: x not in self._keywords, variables)

        for variable in variables:
            content = self._sub(variable, content, self._terms)

        return content

    def _evaluate_loops(self, content):
        """Evaluate all LOOPs."""
        
        # This regex will return pairs of ('LOOP_NAME', 'LOOP_CLOSE')
        # However, each pair will only contain either the LOOP_NAME or
        # LOOP_CLOSE because of the '|' in the re. This way we know how many
        # nested loops there will be before the valid loop close.
        # i.e. [('LOOP_NAME1', ''), ('LOOP_NAME2', ''), ('', 'LOOP'),
        #       ('', 'LOOP')]
        # tells use we have a loop that looks something like the following:
        # {LOOP LOOP_NAME1} {LOOP LOOP_NAME2} {!LOOP} {!LOOP}

        loops = re.findall(r'(?s)\{LOOP (%s)\}|\{!(LOOP)\}' % self._var_regex,
                           content)

        # This marks a closed loop
        loop_close = ('', 'LOOP')
        
        loop_array = self._build_nest_count(content, loops, loop_close, "LOOP")

        # Note that every time a loop is evaluated, all other loops' starting
        # positions need to be re-evaluated.
        for i in range(0, len(loop_array)):
            
            loop = loop_array[i]
            content_start_len = len(content)
            
            start_pos = loop["char_pos"]
            end_pos = content.find("{!LOOP}", start_pos)
            if end_pos == -1:
                raise TemplateModuleError("Unable to find end of loop '%'." %
                                          loop)
            
            loop_text = content[start_pos + len("{LOOP %s}" % loop["expr"]):
                                  end_pos]
            
            # Cut out the loop text from the full file text
            content = content[:start_pos] + content[end_pos + 7:]

            dot_loc = loop["expr"].find(".")
            if dot_loc == -1 and self._loops.has_key(loop["expr"]):
                var_name = loop["expr"]
            else:
                continue

            evaluated_text = ""
            for j in range(0, len(self._loops[var_name])):

                variables = re.findall(r'\{((?:%s)+)\}' % self._var_regex,
                                       loop_text)
                variables = filter(lambda x: x not in self._keywords,
                                   variables)
                
                repl_text = loop_text

                for variable in variables:
                    repl_text = self._sub(variable, repl_text, self._loops, j)

                    # We also have to evaluate all if tags within the loop at
                    # this point
                    repl_text = self._evaluate_ifs(repl_text, j)
                    
                evaluated_text += repl_text

            # Insert the evaluated text
            content = (content[:start_pos] + evaluated_text +
                       content[start_pos:])

            loop_array = self._calibrate(content, content_start_len,
                                         loop_array, i)

        return content
    
    def _evaluate_ifs(self, content, index = -1):
        """Evaluate all IFs."""

        var_expr = r'(?:%s|%s)' % (self._var_regex, self._literal_regex)
        expr_regex = r'%s (?:==|!=|<|>) %s' % (var_expr, var_expr)

        # See _evaluate_loops for a comment on how this expression works.
        ifs = re.findall(r'(?s)\{IF (%s)\}|\{!(IF)\}' % expr_regex, content)
        if_close = ('', 'IF')

        if_array = self._build_nest_count(content, ifs, if_close, "IF")

        # Now do the evaluation.
        for i in range(0, len(if_array)):

            cur_if = if_array[i]
            content_start_len = len(content)

            start_pos = cur_if["char_pos"]
            end_pos = content.find("{!IF}", start_pos)
            if end_pos == -1:
                raise TemplateModuleError("Unable to find end of loop '%'." %
                                          cur_if)
            
            if_text = content[start_pos + len("{IF %s}" % cur_if["expr"]):
                              end_pos]
            else_text = ""

            else_start_pos = if_text.find("{ELSE}")
            if else_start_pos != -1:
                else_text = if_text[else_start_pos + len("{ELSE}"):]
                if_text = if_text[:else_start_pos]

            # Evaluate the expression:
            if self._evaluate_expr(cur_if["expr"], index):
                new_text = if_text
            else:
                new_text = else_text

            content = (content[:start_pos] + new_text +
                       content[end_pos + len("{!IF}"):])

            if_array = self._calibrate(content, content_start_len, if_array, i)

        return content

    def _calibrate(self, content, content_start_len, region_array, index):
        """Calibrate the starting character positions for a set of regions.

        This is required because once an IF or LOOP is processed the number
        of characters for the output changes meaning that our region starting
        positions will all be offset.
        """

        difference = len(content) - content_start_len
        for j in range(index, len(region_array)):
            if region_array[j]["char_pos"] > region_array[index]["char_pos"]:
                region_array[j]["char_pos"] += difference
        
        return region_array

    def _build_nest_count(self, content, regions, region_close, region_str):
        """Generates an array of (region, nest) pairs.

        Nest is a count of how many nested loops a region has and each
        region is basically either LOOP, or IF starting position up to 'close'.
        This data is used for the evaluation order of regions. For example,
        the least nested loops will always be evaluated first. This eliminates
        the problem of nested loops by evaluating the inner loops first.
        The same goes for IF's.
        """
    
        def region_sort(reg1, reg2):
            """Sorts loops in order of how nested they are."""
            if reg1["nested"] < reg2["nested"]:
                return -1
            if reg1["nested"] > reg2["nested"]:
                return 0
            if reg1["char_pos"] < reg2["char_pos"]:
                return -1
            if reg1["char_pos"] > reg2["char_pos"]:
                return 0
            return 1
        
        # Determine which regions have nested regions, and how many nested
        # regions we have. This will be used to determine processing order.
        start_pos = 0  # Used for marking the character position of the region.
        region_array = []
        for i in range(0, len(regions)):

            # Skip this iteration if it's a region close
            if regions[i] == region_close:
                continue

            # Figure out how many sub regions are contained within this region.
            region_array.append({"expr": regions[i][0], "nested": 0})

            match_str = "{%s %s}" % (region_str, regions[i][0])
            
            # Now we want to find the starting position for each region.
            # Set the char_pos of the current region. Note that we must use -1
            # here as 'i' isn't valuable due to the skipping of region closes.
            region_array[-1]["char_pos"] = content.find(match_str, start_pos)
            
            # Increment past the {} (i.e. past the {LOOP VARNAME} text)
            start_pos = region_array[-1]["char_pos"] + len(match_str)

            nest_count = 1
            for j in range(i + 1, len(regions)):

                if regions[j] != region_close:
                    region_array[-1]["nested"] += 1
                    nest_count += 1

                else:
                    nest_count -= 1

                if nest_count == 0:
                    break
        
        region_array.sort(region_sort)
        return region_array

    def _evaluate_expr(self, expr, index):
        """Evaluate any boolean expressions.

        expr should contain an operator (i.e. ==, <, >, !=) and this function
        will return True or False.
        """

        variables = r'(?:%s|%s)' % (self._var_regex, self._literal_regex)
        expr_regex = r'(%s) (==|!=|<|>) (%s)' % (variables, variables)

        match = re.search(expr_regex, expr)

        if match is None:
            raise TemplateModuleError("Error parsing IF expression.")

        lhs = self._value_of(match.group(1), index)
        rhs = self._value_of(match.group(3), index)
        oper = match.group(2)

        # Convert all \n's.
        return eval("\"%s\" %s \"%s\"" % (str(lhs).replace("\n", r'\n'), oper,
                                          str(rhs).replace("\n", r'\n')))

    def _value_of(self, var, index):
        """Returns the literal value of any variable or literal."""

        # If it's surrounded by quotes or all digits then we have a literal
        if (var[0] == "\"" and var[-1] == "\"") or \
               re.match(r'^\d*$', var) is not None:
            value = var.strip("\"")
        
        else:
            value = self._sub(var, "{%s}" % var, self._terms)
            if value == "{%s}" % var:
                value = self._sub(var, "{%s}" % var, self._loops, index)

        return value

    def _check_cache(self, digest):
        """Verify the existence of the cache with digest 'digest'."""
        
        if not os.path.exists(config.template_cache):
            raise TemplateModuleError('Template cache directory missing')
            
        for filename in os.listdir(config.template_cache):
            if filename.endswith('.cache'):
                if digest == filename.split('.')[0]:
                    return True

        return False

    def _read_cache(self, digest):
        """Load the cached template and store it in _output."""
        
        try:
            readfd = open(
                os.path.join(config.template_cache, digest + '.cache'), 'r')
            self._output = readfd.readlines()
            readfd.close()
        
        except IOError, errmsg:
            raise TemplateModuleError('Failed to open template cache file',
                                      errmsg)
            
    def _write_cache(self, digest):
        """Write the cached file to disk."""

        try:
            writefd = open(
                os.path.join(config.template_cache, digest + '.cache'), 'w')
            writefd.write('\n'.join(self._output))
            writefd.close()
        
        except IOError, err:
            #logwrite("Cache write failed: '%s'" % err, __modulename__,
            #         'Error')
            raise TemplateModuleError('Template cache write failed', err)

    def param(self, key, value, param_type = "term"):
        """Add a new parameter, either a 'loop' or a 'term'."""
        
        if string.lower(param_type) in ("l", "loop"):
            self._loops.update({key: self._add_tmpl_values(value)})
        
        elif string.lower(param_type) in ("t", "term"):
            self._terms.update({key: value})

    def output(self):
        """Returns the resulting template."""

        if len(self._output) == 0:
            raise TemplateModuleError('No compiled template data found')

        return "\n".join(self._output)


# FIXME: This exception is only here until exception handling is properly setup
class TemplateModuleError(Exception): pass
