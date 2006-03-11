most all install: .patch
	$(MAKE) -C pub/diag $@

clean: unpatch
	$(MAKE) -C pub/diag clean

.patch:
	for p in patches/*.patch ; do \
		patch -p0 < $$p || exit 1 ; \
	done
	touch .patch

unpatch: .patch
	for p in patches/*.patch ; do \
		patch -p0 -R < $$p || exit 1 ; \
	done
	rm -f .patch pub/diag/.listing

.PHONY: all clean install most unpatch
