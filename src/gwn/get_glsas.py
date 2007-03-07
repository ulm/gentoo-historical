#!/usr/bin/python
# you need dev-python/pyxml for this to work

from xml.dom.ext.reader.Sax2 import FromXmlStream
from urllib2 import urlopen
from tempfile import mkstemp
import sys, re, os

RDF_PAGE = "http://www.gentoo.org/rdf/en/glsa-index.rdf?num=100"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
DTD_PREFIX = "http://www.gentoo.org"
GLSA_LINK = "http://www.gentoo.org/security/en/glsa/"
GLSA_LINK2 = "http://security.gentoo.org/glsa/"

no_glsas = """<chapter>
<title>Gentoo Security</title>
<section>
<body>

<p>
Gentoo Security is on hiatus this week due to no GLSAs being released.
</p>

</body>
</section>

</chapter>"""

doctype_re = re.compile("<!DOCTYPE guide SYSTEM \"(.*)\">")
doctype_new = "<!DOCTYPE guide SYSTEM \"" + DTD_PREFIX + "%s\">\n"
glsa_re = re.compile(GLSA_LINK + "glsa-(.*).xml");
glsa_re2 = re.compile(GLSA_LINK2 + "glsa-(.*).xml");
glsa2gwn = "./glsa2gwn.py"

def get_last_glsa_id(last_gwn):
	if last_gwn.startswith("http://"):
		fd = urlopen(last_gwn)
	else:
		fd = open(last_gwn)
	tmp = open(mkstemp()[1], 'r+')
	matched = False

	# need to do this otherwise we get an 'unknown url type' error from urllib2
	# when it encounters the relative link to the dtd
	for line in fd:
		if not matched:
			matches = doctype_re.match(line)

			if matches:
				tmp.write(doctype_new % matches.group(1))
				matched = True
			else:
				tmp.write(line)
		else:
			tmp.write(line)

	tmp.flush()
	tmp.seek(0)

	dom = FromXmlStream(tmp)
	last_glsa_id = "0"

	for node in dom.getElementsByTagName("uri"):
		uri = node.getAttribute("link")

		if uri.startswith(GLSA_LINK):
			new_id = glsa_re.match(uri).group(1)
			if new_id > last_glsa_id:
				last_glsa_id = new_id

	return last_glsa_id

def get_glsa_list(last_id):
	ret = []
	fd = urlopen(RDF_PAGE)
	dom = FromXmlStream(fd)

	for node in dom.getElementsByTagNameNS(RDF_NS, "li"):
		uri = node.getAttributeNS(RDF_NS, "resource")
		id = glsa_re2.match(uri).group(1)

		if id > last_id:
			ret.append(uri + "?passthru=1")
		else:
			break

	ret.reverse()
	return ret

if __name__ == '__main__':
	if len(sys.argv) < 2 or len(sys.argv) > 3:
		print "Usage: " + os.path.basename(sys.argv[0]) +  " <last-gwn> [glsa2gwn.py]"
		print "if the last-gwn is a URI remember to add '?passthru=1' to the end"
		print "if the location of glsa2gwn.py is not specified it defaults to " + glsa2gwn
		sys.exit(1)
	else:
		if len(sys.argv) == 3:
			glsa2gwn = sys.argv[2]

		last_id = get_last_glsa_id(sys.argv[1])

		# if last_id == 0 then there haven't been any new GLSAs since the last GWN
		if last_id != "0":
			glsas = get_glsa_list(last_id)

			if len(glsas) > 0:
				print "<chapter>\n<title>Gentoo security</title>\n"

				# if we don't flush here then the previous print statement doesn't
				# make it when redirecting the output to a file
				sys.stdout.flush()

				glsas.insert(0, glsa2gwn)
				os.spawnv(os.P_WAIT, glsa2gwn, glsas)

				print "</chapter>\n"
			else:
				print no_glsas
		else:
			print no_glsas
