#!/usr/bin/python
import subprocess
import threading
import select
import sys


myargv = sys.argv[1:]
results = {}
#r, w = popen2.popen4('gpg --no-auto-check-trustdb --verify',bufsize=2**23)
cmd = 'gpg --no-auto-check-trustdb --verify'
p = subprocess.Popen([cmd], shell=True, bufsize=2**20, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
(r, w) = (p.stdout, p.stdin)

def feedManifest():
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
			results[filename] = 'signed','untested'
			w.writelines(content)
			#w.flush()
		else:
			results[filename] = 'unsigned',
	w.close()

#sys.stderr.write('Flushing')
#w.flush()
#sys.stderr.write('Closing')
#w.close()
#print p.returncode
#ret = p.wait()
#print ret

def processoutput():
	sys.stderr.write('Processing'+"\n")
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

in_t=threading.Thread(target=feedManifest, args=(), kwargs={})
in_t.start()
out_t=threading.Thread(target=processoutput, args=(), kwargs={})
out_t.start()

out_t.join() # after you're doing with everything and want to block for it to complete

#print r.readlines()
#r.close()
#w.close()

print p.returncode
ret = p.wait()
print ret

# vim: sts=4 ts=4 sw=4:
