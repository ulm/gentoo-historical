#!/usr/bin/python -O
# Gentoo Foundation 2007
# Authored by Alec Warner <antarus@gentoo.org> 2007
# This code is hereby released into the public domain

__author__ = "Alec Warner <antarus@gentoo.org>"
__date__ = "March 21st 2007"

# Nasty hack to create termination string; ask harring to make this better
a = ""
for i in xrange(72):
	a = a + '='

BLOCK_SYNC_ENTRY_TERMINATOR = a

del a


import email, sys, os
from time import mktime, time, localtime
try:
	from email.utils import parsedate
except ImportError:
	from email.Utils import parsedate # py2.4

def send_infra_mail( msg ):
	"""
	E-mail infra that the block is in place and is over it's estimate completion date
	"""

	from smtplib import SMTP
	from datetime import datetime

	to = []
	source = "block-sync@gentoo.org"
	infra = "infra@gentoo.org"
	present = datetime(*localtime()[0:6]).strftime("%c") # RFC 2882 date

	# grab the person who is blocking the sync, send them mail.
	reporter = msg["Signed-Off-By"]
	to.append(reporter)

	# Send mail to infra as well
	# to.append(infra)
	to.append("antarus@gentoo.org")

	message = "\
From: block-sync@gentoo.org\n\
Subject: Gentoo-x86 block_sync\n\
%s added a block_sync file at:\n\
\n%s\n\n\
and their work on the tree was to be finished at:\n\
\n%s\n\n\
However the time is currently \n\n%s.\n\n\
\
-Automated message from gmirror" % (reporter, 
		msg["Entry-Date"], msg["Completion-Date"], present)
	mailserver = SMTP("localhost")
	mailserver.sendmail(source, to, message)

def process( msg ):
	"""
	Process a email.message object; figure out if we should send
	mail or stop the sync...etc..
	"""

	if "Completion-Date" in msg:
		finish = mktime( parsedate(msg["Completion-Date"] ) )
		now = time()
		if now > finish:
			send_infra_mail( msg )
			sys.exit(3)


def main():
	args = sys.argv[:]
	if len(args) < 2:
		print "%s /path/to/block_sync" % args[0]
		sys.exit(2)

	block_sync_path = args[1]
	
	if not os.path.exists( block_sync_path ):
		sys.exit(0)
	try:
		fp = open( block_sync_path, 'rb' )
		msg_text = ""
		for line in fp:
			if line != BLOCK_SYNC_ENTRY_TERMINATOR:
				msg_text = msg_text + line
			else:
				msg = email.message_from_string( msg_text )
				process(msg)
				msg_text = ""
		
		if msg_text:
			msg = email.message_from_file( fp )
			process(msg)
	except:
		sys.exit(4)
	finally:
		fp.close()

if __name__ == "__main__":
	main()
