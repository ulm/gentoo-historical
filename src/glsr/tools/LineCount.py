#!/usr/bin/python
# $Id: LineCount.py,v 1.1 2004/12/30 12:51:38 port001 Exp $

import os

WWW_DIR = os.path.join(os.path.join(os.getcwd(), '../src'), "htdocs")
GLSR_DIR = os.path.join(os.getcwd(), '../src')

MyFiles = ("%s/Setup.py" % GLSR_DIR, "%s/index.py" % WWW_DIR) 
MyDirs = ("%s/pym" % GLSR_DIR, "%s/site_modules" % GLSR_DIR)

FileList = []
LineCount = 0

for File in MyFiles:
    FileList.append(File)

for Dir in MyDirs:
    for Dir, SubDir, Files in os.walk(Dir):
        if not Dir.endswith("CVS"):
	    for File in Files:
	        FileList.append(os.path.join(Dir, File))

for File in FileList:
    fd = open(File, "r")
    FileLineCount = 0
    for line in fd.readlines():
        if not line.strip(" ").startswith("#") and not line.strip(" ").startswith("\n"):
	    FileLineCount += 1
    print "%d\t: %s" % (FileLineCount, File.split('../src/')[1])
    LineCount += FileLineCount
    fd.close()

print
print "GLSR Line Count: %d" % LineCount
        

