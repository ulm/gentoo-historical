CC=gcc
CFLAGS=-Wall -Os -fomit-frame-pointer
OBJS=rc runscript


all:
	$(CC) $(CFLAGS) -o rc rc.c
	$(CC) $(CFLAGS) -o runscript runscript.c
	
strip: rc runscript
	strip -R comment -X -d --strip-unneeded rc runscript

install: $(OBJS)
	install $(OBJS) /sbin

uninstall:
	cp /sbin/runscript.bak /sbin/runscript
	cp /sbin/rc.bak /sbin/rc

clean:
	rm -f *.o rc runscript
