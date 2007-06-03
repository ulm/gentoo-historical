#!/usr/bin/python
import subprocess
import threading
import select
import sys


myargv = sys.argv[1:]
results = {}
#r, w = popen2.popen4('gpg --no-auto-check-trustdb --verify',bufsize=2**23)
cmd = 'gpg --no-auto-check-trustdb --verify'
p = subprocess.Popen([cmd], shell=True, bufsize=0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
(r, w) = (p.stdout, p.stdin)

class Shared:
	def __init__(self):
		self.counter = 0

doneinput = False
def feedManifest(shared):
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
			results[filename] = ['signed','untested']
			w.writelines(content)
			w.flush()
			shared.counter += 1
		else:
			results[filename] = ['unsigned']
	w.writelines("\n"*2048)
	w.writelines("-----BEGIN PGP SIGNED MESSAGE-----\n")
	w.writelines("-----BEGIN PGP SIGNATURE-----\n")
	w.writelines("-----END PGP SIGNATURE-----\n")
	w.flush()
	w.writelines("-----BEGIN PGP SIGNED MESSAGE-----\n")
	w.writelines("-----BEGIN PGP SIGNATURE-----\n")
	w.writelines("-----END PGP SIGNATURE-----\n")
	w.flush()
	doneinput = True

#sys.stderr.write('Flushing')
#w.flush()
#sys.stderr.write('Closing')
#w.close()
#print p.returncode
#ret = p.wait()
#print ret

def processoutput(shared):
	#sys.stderr.write('Processing'+"\n")
	#print 'PROCESSING'
	resultcount = -1
	while(1):
		l = r.readline()
		#print l
		#if(len(l) == 0):
		#	continue
		if(len(l) > 0):
			l = l[:-1] # remove \n
		#print 'RES:',resultcount,' LINE:"',l,'"'
		filename = myargv[resultcount]
		if(l.find('gpg: Signature made') == 0):
			resultcount = resultcount + 1
			continue
		elif(l.find('gpg: BAD signature') == 0):
			print 'EXTRA ',l
			print 'BAD ',filename
			results[filename] = ['signed','bad']
			shared.counter -= 1
		elif(l.find('gpg: Good signature') == 0):
			print 'GOOD ',filename
			results[filename] = ['signed','good']
			shared.counter -= 1
		elif(len(l) > 0):
			print 'WEIRD ',l
		if(doneinput):
			print 'counter = %d' % (shared.counter)
			if(shared.counter > 0):
				print 'Waiting for counter %d' % (shared.counter)
				w.writelines('\n'*128)
				continue
			else:
				w.close()
				return

shared = Shared()
in_t=threading.Thread(target=feedManifest, args=[shared], kwargs={})
in_t.start()
out_t=threading.Thread(target=processoutput, args=[shared], kwargs={})
out_t.start()

out_t.join() # after you're doing with everything and want to block for it to complete

#print r.readlines()
#r.close()
#w.close()

keys = results.keys()
keys.sort()
for k in keys:
	print "file: %s result: %s" % (k,results[k])

print p.returncode
ret = p.wait()
print ret

# vim: sts=4 ts=4 sw=4:
