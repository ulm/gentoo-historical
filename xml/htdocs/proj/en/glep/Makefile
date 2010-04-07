GLEPTOOL=glep.py --exit-status=3 --link-stylesheet --stylesheet-path=tools/glep.css

INPUTS = $(wildcard glep*.txt)
OUTPUTS = $(patsubst %.txt,%.html,$(INPUTS))

all: $(OUTPUTS)

# Build warnings first
%.html: %.txt
	$(GLEPTOOL) --report=1 $< /dev/null
	$(GLEPTOOL) $< $@

# This enables comparisions
.PHONY: versioncmp 
versioncmp: .tmp.versions.html .tmp.versions.txt
	diff -Nuar .tmp.versions.txt .tmp.versions.html

# Extract the revision
.tmp.versions.html:
	awk '/class="field-name">Version:<\/th>/{gsub("<[^>]+?>","",$$0); s=FILENAME; gsub(".html","",s); printf "%s:%s\n",s,$$0;}' *.html >$@
.tmp.versions.txt:
	awk '/^Version:/{gsub(" *\\$$[A-Za-z:]* *","",$$0); s=FILENAME; gsub(".txt","",s); printf "%s:%s\n",s,$$0;}' *.txt >$@

# clean up the temps immediately
.INTERMEDIATE: .tmp.versions.html .tmp.versions.txt
