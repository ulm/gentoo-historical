#!/usr/bin/python -OO

import mstring
import re


BUG_REGEX = re.compile(r'\b#[0-9]+|\bbug [0-9]+',re.I)
BUG_URL = 'http://bugs.gentoo.org/show_bug.cgi?id='

def bugs_to_html(s):
    index = 1
    while 1:
        match = BUG_REGEX.search(s,index)
        if not match:
            break
        start = match.start()
        end = match.end()
        substring = s[start:end]
        if substring[0] == '#':  # this of the form "#1234"
            bugid = substring[1:]
        else: # this is of the form "bug 1234"
            bugid = substring[4:]
        url = '<a href="%s%s">%s</a>' % (BUG_URL,bugid,substring)
        (s,index) = mstring.replace_sub(s,url,start,end-1)
    return s

def changelog(filename):
    try:
        #print filename
        fp = open(filename,'r')
    except IOError:
        return ""


    s = ""
    # find first line that isn't blank or a comment
    while True:
        line = fp.readline()
        if not line: break
        #print line
        if line[0] not in ['#','','\n']:
            s = s + line
            break
    
    # append next strings until you reach next "*"
    while True:
        line = fp.readline()
        #print repr(line)
        if not line or line[0] == '*': break
        else: s= s + line
    
    return s
