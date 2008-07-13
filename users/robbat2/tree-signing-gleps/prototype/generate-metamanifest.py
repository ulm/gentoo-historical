#!/usr/bin/python -O
# $Header: /var/cvsroot/gentoo/users/robbat2/tree-signing-gleps/prototype/generate-metamanifest.py,v 1.4 2008/07/13 01:09:27 robbat2 Exp $
# Protoype of the MetaManifest generation script.
# Robin H. Johnson <robbat2@gentoo.org>
# 2008-07-12
# Runtime is 12 seconds, single-threaded on 2.4Ghz Core2 processor, with a hot
# disk cache.

import os
import sys
import fnmatch
import re

# =========
# Borrowed straight from repoman
os.environ["PORTAGE_LEGACY_GLOBALS"] = "false"
try:
  import portage
except ImportError:
  from os import path as osp
  sys.path.insert(0, osp.join(osp.dirname(osp.dirname(osp.realpath(__file__))), "pym"))
  import portage
del os.environ["PORTAGE_LEGACY_GLOBALS"]
# =========

# This is the only part of Portage we use directly.
from portage.manifest import Manifest

# Ain't life simple?
class MetaManifest(Manifest):
  def getFullname(self):
    return os.path.join(self.pkgdir, "MetaManifest")
  # This is a horrible, horrible hack
  def sign(self):
    try:
      ts = os.path.join(mysettings["PORTDIR"],'metadata','timestamp.x')
      ts = open(ts,'r')
      ts = ts.read().rstrip('\n').strip()
    except Exception:
      ts = 'File not available'
    f = open(self.getFullname(), "a")
    f.write("Timestamp: metadata/timestamp.x: "+ts+"\n")
    f.close()

# Again, borrowed from repoman
mysettings = portage.config(local_config=False, config_incrementals=portage.const.INCREMENTALS)

full_list = set()
covered_list = set()

# See the exclusion list in 05-manifest2-clarifications
EXCLUDE_DIRS = [ '.', '..', 'CVS', '.svn', '.git', '.hg', '.bzr' ]
EXCLUDE_FILES = [ '.#*', '*.rej', '*.orig', '*.bak', '*~' ]

# we do this for speed, doing a looped fnmatch is slow :-(
EXCLUDE_FILES_RE = re.compile('|'.join([fnmatch.translate(i) for i in EXCLUDE_FILES]))

for parent, dirs, files in os.walk(mysettings["PORTDIR"]):
  # Exclude the VCS directories
  for d in dirs:
    if d in EXCLUDE_DIRS:
      dirs.remove(d)
  for f in files:
    ## doing the fnmatch on a full portdir takes 20 seconds but it only takes 6
    # seconds for the compiled RE!
    #SLOW# for fm in EXCLUDE_FILES:
    #SLOW#   if fnmatch.fnmatch(fm, f):
    #SLOW#     continue

    # Exclude the bad file globs
    if EXCLUDE_FILES_RE.match(f):
      continue

    # Exclude ourselves at the toplevel only
    if mysettings["PORTDIR"] == parent and f.startswith('MetaManifest'):
      continue

    # We have to create the covered set directly.
    if f == "Manifest":
      #print 'Adding manifest for %s' % (os.path.join(parent, f),)
      mf = Manifest(parent, mysettings["DISTDIR"])
      # ignore DIST
      misc = mf.getTypeDigests("MISC")
      aux = mf.getTypeDigests("AUX")
      ebuild = mf.getTypeDigests("EBUILD")
      dummy = []
      dummy += [os.path.join(parent, 'files', i)[len(mysettings["PORTDIR"]) + 1:] for i in aux.keys()]
      dummy += [os.path.join(parent, i)[len(mysettings["PORTDIR"]) + 1:] for i in misc.keys()+ebuild.keys()]
      covered_list.update(dummy)

    # Now the full set.
    f = os.path.join(parent, f)[len(mysettings["PORTDIR"]) + 1:]
    full_list.add(f)
    #print "%s" % (f, )

# Do (UNCOVERED) = (ALL)-(COVERED)
# We don't care about items that are only in (COVERED)
uncovered_list = full_list.difference(covered_list)

#for i in uncovered_list:
#  print i

# Actually generate the MetaManifest now
manifest1_compat = False
mm = MetaManifest(mysettings["PORTDIR"], mysettings["DISTDIR"],
    fetchlist_dict={}, manifest1_compat=manifest1_compat)
for i in uncovered_list:
  mm.addFile('MISC', i)
mm.write(sign=True)
