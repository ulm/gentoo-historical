#!/usr/bin/python
import popen2
import sys


myargv = sys.argv[1:]
results = {}
r, w = popen2.popen4('gpg --no-auto-check-trustdb --verify',bufsize=65536)
count = 0
for filename in myargv:
	print 'FILENAME(%d): %s' % (count,filename)
	count = count + 1
	f = file(filename,'r',4096)
	content = f.readlines()
	f.close()
	#print content
	if "-----BEGIN PGP SIGNED MESSAGE-----\n" in content:
		# push to GPG
		w.writelines(content)
		#w.write("\n")
		results[filename] = 'signed','untested'
		#print content
	else:
		results[filename] = 'unsigned',
	#w.flush()
	#w.close()

w.close()

print 'PROCESSING'
resultcount = -1
while(1):
	l = r.readline()
	#print l
	if(len(l) == 0):
		break
	l = l[:-1] # remove \n
	#print 'RES:',resultcount,' LINE:"',l,'"'
	filename = myargv[resultcount]
	if(l.find('gpg: Signature made') == 0):
		resultcount = resultcount + 1
		continue
	elif(l.find('gpg: BAD signature') == 0):
		print 'EXTRA ',l
		print 'BAD ',filename
		results[filename] = 'signed','bad'
	elif(l.find('gpg: Good signature') == 0):
		print 'GOOD ',filename
		results[filename] = 'signed','good'
	else:
		print 'WEIRD ',l

#print r.readlines()
r.close()
#w.close()

# vim: sts=4 ts=4 sw=4:
