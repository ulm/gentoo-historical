# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Template.py,v 1.2 2004/06/27 20:04:05 hadfield Exp $

import sys
import string
import re
import types

import Config
import Function

__modulename__ = "Template"

class New:

    def __init__(self):
        
	self.Template = ""
	self.Contents = []
	self.Output = []
        self.__Loops = {}
        self.__Terms = {}

    def __Read(self):

        try:
            self.Contents = open(self.Template, "r").readlines()
        except IOError, errmsg:
            Function.logwrite("ERROR: %s: Failed to open %s for reading '%s'" %
                              (__modulename__, self.Template, errmsg), "Error")

            print ("<html>\n<head>\n</head>\n<body>" +
                   "<font size=3><b>FATAL ERROR: Failed to open template " +
                   "'%s' for reading.</b><br>Please contact %s with the " %
                   (self.Template, Config.Contact) +
                   "given error message.</font>" +
                   "</body>\n</html>")
            
	    sys.exit(1)

        return self.Contents
	
    def __Clear(self):

        self.Template = ""
	self.Contents = []
	self.Output = []
	
    def __processLoops(self, file, Loops):
        """Processes all top level loops. Returns 'file' with all loops
        processed"""
        return self.__processTags(file, Loops, "LOOP",
                                  lambda x,y: self.__processLoop(x, y))

    def __processIfs(self, file, Terms):
        return self.__processTags(file, Terms, "IF",
                                  lambda x,y: self.__processIf(x, y))

    def __processTags(self, file, Terms, tag, function):
        tag_open = "{%s " % tag
        tag_close = "{!%s}" % tag

        working_file = file
        start = string.find(working_file, tag_open)
        while (start != -1):
            # Find the end of the tag
            end = self.__findTagClose(working_file[start + len(tag_open):], 0,
                                      tag) + start + len(tag_open)

            # Process that tag
            tag_content = function(working_file[start + len(tag_open):end],
                                   Terms)

            working_file = (working_file[:start] + tag_content +
                            working_file[end + len(tag_close):])

            # Find the beginning of the next loop
            start = string.find(working_file, tag_open)


        return working_file

    def __findTagClose(self, file, nest, tag):
        "Recursively finds the location of the matching {!LOOP}"
        tag_open = "{%s " % tag
        tag_close = "{!%s}" % tag

        next_open = string.find(file, tag_open)
        next_close = string.find(file, tag_close)

        if next_close < next_open or next_open == -1:
            # No new loops were found
            if nest == 0:
                # Yay! We found the final loop closing tag
                return next_close
            else:
                # A nested !loop found, decrement the nest count
                start = next_close + len(tag_close)
                return start + self.__findTagClose(file[start:], nest - 1, tag)
        else:
            # A new nested loop found, increment the nest count.
            start = next_open + len(tag_open)
            return start + self.__findTagClose(file[start:], nest + 1, tag)

    def __processLoop(self, file, Loops):
        """Returns the content inside the loop (after it's been looped).
        It expects 'file' to be the content between (exlusively) '{LOOP '
        and {!LOOP}.
        The nested-most loop is processed first"""

        # loop_name is the loop tag name
        loop_name = file[:string.find(file, "}")].strip()

        # loop_text is the content within the {LOOP}{!LOOP} tags.
        loop_text = file[string.find(file, "}") + 1:]

        next_open = string.find(file, "{LOOP ")
        if next_open != -1:
            "A nested LOOP exists, so recurse futher"
            loop_text = self.__processLoops(loop_text, Loops)

        # No more nested loops, so we can process this one
        if loop_name not in Loops.keys():            
            raise TemplateError, "Loop %s is not defined." % loop_name

        # The following four statements are used for finding and replacing
        # tags within the IF tag (i.e. {IF TAG1 == TAG2}). It's not as
        # fucked up as it looks, really ;-).
        p = re.compile('({IF +)([\w\-_"\']+)( *[!=<>]+ *)([\w\-_"\']+)' +
                       '( *})')
        p_index = re.compile('({IF +)([\w\-_"\']+.[\w\-_"\']+)' +
                             '( *[!=<>]+ *)([\w\-_"\']+.[\w\-_"\']+)( *})')

        repl_func = lambda x: (re.sub('([ !=<>]+)%s|%s([ !=<>]+)' %
                                      (loop_name, loop_name),
                                      "\\1%s" % Loops[loop_name][i],
                                      x.group()))
        repl_func2 = lambda x: (re.sub('([ !=<>]+)%s.%s|%s.%s([ !=<>]+)' %
                                       (loop_name, loop_index, loop_name,
                                        loop_index), "\\1%s" %
                                       Loops[loop_name][i][loop_index],
                                       x.group()))

        loop_str = ""
        for i in range(0, len(Loops[loop_name])):
            """ This loop does the actual tag replacement with the
            appropriate values."""

            tmp_text = loop_text
            dot = tmp_text.find("{%s." % loop_name)
            while dot != -1:
                "Replace all multi-dimensional loop tags"
                start = dot + len(loop_name) + 2
                end = tmp_text.find("}", start)

                loop_index = tmp_text[start:end].strip()
                inner_val = Loops[loop_name][i][loop_index]

                new_text = tmp_text.replace("{%s.%s}" %
                                            (loop_name, loop_index),
                                            "%s" % inner_val)

                # Replace and tags.index within the {IF } tag
                new_text = p_index.sub(repl_func2, new_text)

                # Adjust the position accordingly
                start = start - len(loop_name) - 1 + len("%s" % inner_val)
                tmp_text = new_text

                dot = tmp_text.find("{%s." % loop_name, start)

            # Replace and tags within the {IF } tag
            tmp_text = p.sub(repl_func, tmp_text)

            loop_str = (loop_str +
                        tmp_text.replace("{%s}" % loop_name,
                                         "%s" % Loops[loop_name][i]))
        return loop_str

    def __processIf(self, file, Terms):
        """File contains everything between {IF and {!IF}"""
        next_open = string.find(file, "{IF ")

        if_text = file[string.find(file, "}") + 1:]

        if next_open != -1:
            if_text = self.__processIfs(if_text, Terms)

        # Find any else's
        else_text = ""
        else_pos = if_text.find("{ELSE}")
        if else_pos != -1:
            else_text = if_text[else_pos + 6:]
            if_text = if_text[:else_pos]


        stmt = file[:file.find("}")].strip()
        tag = stmt[:stmt.find(" ")]

        # Set the operator
        oper = stmt[stmt.find(" "):].strip(" ")
        oper = oper[:oper.find(" ")].strip()

        def setVal(val):
            if val not in Terms.keys():
                return val.strip("\"' ")
            else:
                return "%s" % Terms[val]

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

    def Compile(self, Template, Terms = {}, Loops = {}):
        """
         'Terms' should be a dictionary of {TAG: value} pairs where value
         will replace the text {TAG} in the specified template file.

         'Loops' should be a dictionary of {LOOPTAG: list} pairs. The template
         file will have some text such as the following, but all that will be
         displayed is "this is loop X" len(list) times.
         {LOOP MYLOOP}
         this is loop {MYLOOP}
         {!LOOP}
         Note: {MYLOOP} is replaced with list[i] where 'i' is the current
               iteration
               
         If statements are as follows:
         {IF TAG == "value"}
         {TAG} is equal to value
         {!IF}
         Note: The currently supported operators are
           ==  !=  >

         Note: Everything is case sensitive
        """
        
        self.Template = Template
        self.__Read()

        self.__Terms.update(Terms)
        self.__Loops.update(Loops)
        
        full_file = string.join(self.Contents);

        # Process all non LOOP, non IF tags
        for term in self.__Terms.keys():
            if type(self.__Terms[term]) == types.DictType:
                for index in self.__Terms[term].keys():
                    full_file = string.replace(full_file, "{%s.%s}" %
                                               (term, index), "%s" %
                                               (self.__Terms[term][index]))
            else:
                full_file = string.replace(full_file, "{%s}" % term,
                                           "%s" % self.__Terms[term])
        for term in self.__Terms.keys():
            full_file = string.replace(full_file, "{%s}" % term,
                                       "%s" % self.__Terms[term])
            
        # Process all LOOP tags
        full_file = self.__processLoops(full_file, self.__Loops)
        
        # Process all IF tags
        self.__Terms.update(self.__Loops)
        full_file = self.__processIfs(full_file, self.__Terms)
        
        self.Output = string.split(full_file, "\n")


    def Param(self, key, value, type = "term"):

        if string.lower(type) in ("l", "loop"):
            self.__Loops.update({key: value})
        elif string.lower(type) in ("t", "term"):
            self.__Terms.update({key: value})

    
    def Print(self):
        if self.Template == "":
            raise TemplateError, "No compiled template data found."

        #print self.Output
        print "\n".join(self.Output)

        self.__Clear()

class TemplateError(Exception): pass
