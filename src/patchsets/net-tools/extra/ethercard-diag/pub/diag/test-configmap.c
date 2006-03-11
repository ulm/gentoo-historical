/* test-configmap.c: Test framework for config-map kernel extension. */

/*
  This is a test program for the config-map kernel module.
  Copyright 2002-2003 Scyld Computing Corporation
  Written 2002 by Donald Becker
  All rights reserved.  Not for external distribution.

	The author may be reached as becker@scyld.com, or C/O
	 Scyld Computing Corporation
	 914 Bay Ridge Road, Suite 220
	 Annapolis MD 21403

*/

static char *version_msg =
"test-configmap.c:v1.00 12/28/2002 Donald Becker (becker@scyld.com)\n"
" http://www.scyld.com/diag/index.html\n";
static char *usage_msg =
"Usage: test-configmap [-V]\n";

#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <getopt.h>
#include <string.h>
#include <errno.h>
#include <sys/mman.h>
#include <sys/ioctl.h>

int verbose = 0;

struct option longopts[] = {
 /* { name  has_arg  *flag  val } */
	{"ioaddr",	1, 0, 'a'},
	{"dev-entry",	1, 0, 'd'},
	{"help",	0, 0, 'h'},	/* Give help */
	{"verbose",	0, 0, 'v'},		/* Verbose mode */
	{"version", 0, 0, 'V'},		/* Display version number */
	{ 0, 0, 0, 0 }
};

#define IOCTL_CFGM (('C'<<24) + ('F'<<16) + ('G'<<8) + 'M')
#define IOCTL_CONFIG_MAP_PCI_BUSDEVFN (IOCTL_CFGM + 0)
#define IOCTL_CONFIG_MAP_PCI_IOADDR (IOCTL_CFGM + 1)


int main(int argc, char *argv[])
{
	/* Option parsing housekeeping. */
	int errflag = 0, show_version = 0;
	int c, longind;
	extern char *optarg;
	/* Internal settings. */
	const char *dev_entry = "/dev/pci-map";
	long ioaddr = 0;
	int fd, status;

	while ((c = getopt_long(argc, argv, "d:i:vV",
							longopts, &longind))
		   != -1)
		switch (c) {
		case 'd': dev_entry = optarg;		break;
		case 'i': ioaddr = strtoul(optarg, NULL, 16);	break;
		case 'v': verbose++;		break;
		case 'V': show_version++;	break;
		case '?':
			errflag++;
		}
	if (errflag) {
		fprintf(stderr, usage_msg);
		return 3;
	}

	if (verbose || show_version)
		printf(version_msg);

	fd = open(dev_entry, O_RDWR);
	if (fd < 0) {
		fprintf(stderr, "test-configmap: Failed to open device node '%s':"
				" %s.\n", 
				dev_entry, strerror(errno));
		return 1;
	}

	if (ioaddr) {
		unsigned int ioctl_args[6] = {ioaddr, 0, 0, 0};
		printf("test-configmap: ioctl() searching for device at %#lx.\n", 
			   ioaddr);
		status = ioctl(fd, IOCTL_CONFIG_MAP_PCI_IOADDR, ioctl_args);
		if (status < 0) {
			fprintf(stderr, "%s: Failed to find device with I/O address %#lx: %s.\n", 
					argv[0], ioaddr, strerror(errno));
			return 2;
		}
		printf("Found device using I/O address %#x at PCI bus position %d:%d.%d.\n",
			   ioctl_args[0], ioctl_args[1] >> 3, ioctl_args[1] & 7);
		ioctl_args[2] = 6;		/* Base Address Register, or ROM address. */
		status = ioctl(fd, IOCTL_CONFIG_MAP_PCI_BUSDEVFN, ioctl_args);

		printf(" BAR %d maps region %#x-%#x, %d bytes (%x %x %x %x %x).\n",
			   ioctl_args[2], ioctl_args[3], ioctl_args[3] + ioctl_args[4],
			   ioctl_args[4], ioctl_args[0], ioctl_args[1], ioctl_args[2],
			   ioctl_args[3], ioctl_args[4]);
	} else {
		fprintf(stderr, "No I/O address with which to locate PCI device.\n"
				"Use -i <ioaddr> to identify the desired PCI device.\n");
		return 1;
	}
	/* Map a page of the designated region. */
	{
		void *f = mmap(0, 0x1000, PROT_READ|PROT_WRITE, MAP_SHARED, fd, 0);
		unsigned int *ip = f;
		if (f == MAP_FAILED) {
			fprintf(stderr, "test-configmap: mmap() failed: %s.\n", 
					strerror(errno));
			return 3;
		}
		printf("Initial words of address space %p are\n"
			   " %8.8x %8.8x %8.8x %8.8x %8.8x %8.8x %8.8x %8.8x.\n", f,
			   ip[0], ip[1], ip[2], ip[3], ip[4], ip[5], ip[6], ip[7]);
	}

	return 0;
}


/*
 * Local variables:
 *  compile-command: "cc -o test-configmap test-configmap.c"
 *  tab-width: 4
 *  c-indent-level: 4
 *  c-basic-offset: 4
 * End:
 */
