CC=gcc
CFLAGS=-Wall -Os -fomit-frame-pointer
OBJS=rc runscript


all: rc runscript

rc: rc.o common.o
runscript: runscript.o common.o

strip: rc runscript
	strip -R comment -X -d --strip-unneeded rc runscript

install: $(OBJS)
	install $(OBJS) /sbin

uninstall:
	cp /sbin/runscript.bak /sbin/runscript
	cp /sbin/rc.bak /sbin/rc

clean:
	rm -f *.o rc runscript
