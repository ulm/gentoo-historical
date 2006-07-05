CFLAGS = -ggdb -Wall -W -DDEBUG

all: etc-update

config.o: config.c etc-update.h
	gcc $(CFLAGS) -c config.c
core.o: core.c etc-update.h
	gcc $(CFLAGS) -c core.c
helpers.o: helpers.c etc-update.h
	gcc $(CFLAGS) -c helpers.c
etc-update.o: etc-update.c etc-update.h
	gcc $(CFLAGS) -c etc-update.c
index.o: index.c etc-update.h
	gcc $(CFLAGS) -c index.c
modified.o: etc-update.h modified.c
	gcc $(CFLAGS) -c modified.c

etc-update.h: core.h helpers.h index.h modified.h config.h

etc-update: core.o helpers.o etc-update.o index.o modified.o config.o
	gcc -lncurses -lmenu -lcrypto $(CFLAGS) -o etc-update config.o core.o helpers.o etc-update.o index.o modified.o

.PHONY: clean

clean:
	rm -f *.o
	rm -f etc-update
