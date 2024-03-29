/* alta-diag.c: Diagnostic and setup for the Sundance "Alta" NIC.

   This is a diagnostic and EEPROM setup program for PCI adapters
   based on the following chips:
     Sundance ST201 "Alta"
   This file also contains the chip-independent diagnostic code.

	Copyright 1998-2002 by Donald Becker.
	This software may be used and distributed according to the terms of
	the GNU General Public License (GPL), incorporated herein by reference.
	Contact the author for use under other terms.

	This program must be compiled with "-O"!
	See the bottom of this file for the suggested compile-command.

	The author may be reached as becker@scyld.com, or C/O
	 Scyld Computing Corporation
	 914 Bay Ridge Road, Suite 220
	 Annapolis MD 21403

	Updates and additional information are available at
	http://www.scyld.com/diag/index.html
	http://scyld.com/expert/mii-status.html
	http://scyld.com/expert/NWay.html

	Common-sense licensing statement: Using any portion of this program in
	your own program means that you must give credit to the original author
	and release the resulting code under the GPL.  To use this code under
	other terms requires an explicit license from the copyright holder.
*/

static char *version_msg =
"alta-diag.c:v2.04 2/28/2005 Donald Becker (becker@scyld.com)\n"
" http://www.scyld.com/diag/index.html\n";
static char *usage_msg =
"Usage: alta-diag [-aEefFGhmqrRtvVwW] [-p <IOport>] [-[AF] <media>]\n"
"  For details and other options see http://www.scyld.com/diag/index.html\n";

static const char long_usage_msg[] =
"Usage: %s [-aDfrRvVw] [-AF <speed+duplex>] [-#<BoardNum>]\n\
\n\
   Show the internal state of a network adapter.\n\
\n\
   The common usage is\n\
      diag -aem\n\
\n\
 Frequently used options are\n\
   -a  --show_all_registers	Print all registers.\n\
   -e  --show-eeprom	Dump EEPROM contents, \"-ee\" shows the details.\n\
   -m  --show_mii		Print the MII transceiver state\n\
					Using -mm monitors the link.\n\
   -f  --force		Perform operation, even on a running NIC.\n\
\n\
 To operate on a single NIC, or one that hasn't been automatically found:\n\
   -#  --card_num	INDEX	Operate on the specified card index.\n\
   -p  --port-base	IOADDR	Assume an adapter at the specified I/O address.\n\
   -t  --chip-type	TYPE	Specify adapter type (with '-p').  Use '-1' to\n\
                            list available types indicies.\n\
\n\
 To change the persistent EEPROM settings\n\
   -G  --parameters PARMS	Set adapter-specific parameters.\n\
   -H  --new-hwaddr 01:23:45:67:89:ab\n\
			Set a new hardware station address.\n\
   -w  --write-EEPROM	 Actually write the new settings into the EEPROM.\n\
\n\
   -D  --debug\n\
   -v  --verbose	Report each action taken.\n\
   -V  --version	Emit version information.\n\
\n\
   -A  --advertise <speed|setting>  (See the mii-diag manual page.)\n\
";

#if ! defined(__OPTIMIZE__)
#warning  You must compile this program with the correct options!
#warning  See the last lines of the source file.
#error You must compile this driver with "-O".
#endif
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <getopt.h>
#include <string.h>
#include <strings.h>
#include <errno.h>

/* The following are required only with unaligned field accesses. */
#include <asm/types.h>
#include <asm/unaligned.h>

#if defined(__linux__)  &&  __GNU_LIBRARY__ == 1
#include <asm/io.h>			/* Newer libraries use <sys/io.h> instead. */
#else
#include <sys/io.h>
#endif

/* No libmii.h or libflash.h yet, thus the declarations here. */
extern int show_mii_details(long ioaddr, int phy_id);
extern int monitor_mii(long ioaddr, int phy_id);

extern int flash_show(long addr_ioaddr, long data_ioaddr);
extern int flash_dump(long addr_ioaddr, long data_ioaddr, char *filename);
extern int flash_program(long addr_ioaddr, long data_ioaddr, char *filename);
extern int (*flash_in_hook)(long addr, int offset);
extern void (*flash_out_hook)(long addr, int offset, int val);

/* We should use __u8 .. __u32, but they are not always defined. */
typedef u_int32_t u32;
typedef u_int16_t u16;
typedef u_int8_t u8;

struct option longopts[] = {
 /* { name  has_arg  *flag  val } */
	{"card-num", 1, 0, '#'},		/* Operate on the specified card index. */
	{"Advertise", 1, 0, 'A'},
	{"base-address", 1, 0, 'p'},
	{"show_all_registers",	0, 0, 'a'},	/* Print all registers. */
	{"help",	0, 0, 'h'},			/* Print a long usage message. */
	{"show-eeprom",  0, 0, 'e'},	/* Dump EEPROM contents (-ee valid). */
	{"emergency-rewrite",  0, 0, 'E'}, /* Re-write a corrupted EEPROM.  */
	{"force-detection",  0, 0, 'f'},
	{"new-interface",  1, 0, 'F'},	/* New interface (built-in, AUI, etc.) */
	{"new-hwaddr",  1, 0, 'H'},	/* Set a new hardware address. */
	{"show-mii",  0, 0, 'm'},	/* Dump MII management registers. */
	{"port-base",  1, 0, 'p'},	/* Use the specified I/O address. */
	{"quiet",	0, 0, 'q'},		/* Decrease verbosity */
	{"reset",	0, 0, 'R'},		/* Reset the transceiver. */
	{"chip-type",  1, 0, 't'},	/* Assume the specified chip type index. */
	{"test",	0, 0, 'T'},		/* Do register and SRAM test. */
	{"verbose",	0, 0, 'v'},		/* Verbose mode */
	{"version", 0, 0, 'V'},		/* Display version number */
	{"write-EEPROM", 1, 0, 'w'},/* Actually write the EEPROM with new vals */
	{ 0, 0, 0, 0 }
};

extern int sundance_diag(int vend_id, int dev_id, long ioaddr, int part_idx);

/* Chip-specific flags. Yes, it's grungy to have the enum here. */

/* The table of known chips.
   Because of the bogus /proc/pci interface we must have both the exact
   name from the kernel, a common name and the PCI vendor/device IDs.
   This table is searched in order: place specific entries followed by
   'catch-all' general entries. */
struct pcidev_entry {
	const char *part_name;
	const char *proc_pci_name;
	int vendor, device, device_mask;
	int flags;
	int io_size;
	int (*diag_func)(int vendor_id, int device_id, long ioaddr, int part_idx);
} pcidev_tbl[] = {
	{ "Sundance Technology Alta", "Sundance Technology Alta",
	  0x1186, 0x1002, 0xffff, 0, 128, sundance_diag},
	{ 0, 0, 0, 0},
};

int verbose = 1, opt_f = 0, debug = 0;
int show_regs = 0, show_eeprom = 0, show_mii = 0;
unsigned int opt_a = 0,					/* Show-all-interfaces flag. */
	opt_restart = 0,
	opt_reset = 0,
	opt_watch = 0,
	opt_G = 0;
unsigned int opt_GPIO = 0;		/* General purpose I/O setting. */
int do_write_eeprom = 0, do_test = 0;
int nway_advertise = 0, fixed_speed = -1;
int new_default_media = -1;
/* Valid with libflash only. */
static unsigned int opt_flash_show = 0;
static char	*opt_flash_dumpfile = NULL, *opt_flash_loadfile = NULL;

static unsigned char new_hwaddr[6], set_hwaddr = 0;
static int emergency_rewrite = 0;

static int scan_proc_pci(int card_num);
static int parse_media_type(const char *capabilities);
static int get_media_index(const char *name);
/* Chip-specific options, if any, go here. */


int
main(int argc, char **argv)
{
	int port_base = 0, chip_type = 0;
	int errflag = 0, show_version = 0;
	int c, longind;
	int card_num = 0;
	extern char *optarg;

	while ((c = getopt_long(argc, argv, "#:aA:DeEfF:G:hH:mp:qrRt:vVwWBL:S:",
							longopts, &longind))
		   != -1)
		switch (c) {
		case '#': card_num = atoi(optarg);	break;
		case 'a': show_regs++; opt_a++;		break;
		case 'A': nway_advertise = parse_media_type(optarg); break;
		case 'D': debug++;			break;
		case 'e': show_eeprom++;	break;
		case 'E': emergency_rewrite++;	 break;
		case 'f': opt_f++;			break;
		case 'F': new_default_media = get_media_index(optarg);
			if (new_default_media < 0)
				errflag++;
			break;
		case 'G': opt_G++; opt_GPIO = strtoul(optarg, NULL, 16); break;
		case 'h': fprintf(stderr, long_usage_msg, argv[0]); return 0;
		case 'H':
			{
				int hwaddr[6], i;
				if (sscanf(optarg, "%2x:%2x:%2x:%2x:%2x:%2x",
						   hwaddr, hwaddr + 1, hwaddr + 2,
						   hwaddr + 3, hwaddr + 4, hwaddr + 5) == 6) {
					for (i = 0; i < 6; i++)
						new_hwaddr[i] = hwaddr[i];
					set_hwaddr++;
				} else
					errflag++;
				break;
			}
		case 'm': show_mii++;	 break;
		case 'p':
			port_base = strtoul(optarg, NULL, 16);
			break;
		case 'q': if (verbose) verbose--;		 break;
		case 'r': opt_restart++;	break;
		case 'R': opt_reset++;		break;
		case 't': chip_type = atoi(optarg);	break;
		case 'v': verbose++;		break;
		case 'V': show_version++;	break;
		case 'w': do_write_eeprom++;	break;
		case 'W': opt_watch++;		break;
		case 'B': opt_flash_show++;	break;
		case 'L': opt_flash_loadfile = optarg;	break;
		case 'S': opt_flash_dumpfile = optarg;	break;
		case '?':
			errflag++;
		}
	if (errflag) {
		fprintf(stderr, usage_msg);
		return 3;
	}

	if (verbose || show_version)
		printf(version_msg);

	if (chip_type < 0
		|| chip_type >= sizeof(pcidev_tbl)/sizeof(pcidev_tbl[0]) - 1) {
		int i;
		fprintf(stderr, "Valid numeric chip types are:\n");
		for (i = 0; pcidev_tbl[i].part_name; i++) {
			fprintf(stderr, "  %d\t%s\n", i, pcidev_tbl[i].part_name);
		}
		return 3;
	}

	/* Get access to all of I/O space. */
	if (iopl(3) < 0) {
		perror("Network adapter diagnostic: iopl()");
		fprintf(stderr, "This program must be run as root.\n");
		return 2;
	}

	/* Try to read a likely port_base value from /proc/pci. */
	if (port_base) {
		printf("Assuming a %s adapter at %#x.\n",
			   pcidev_tbl[chip_type].part_name, port_base);
		pcidev_tbl[chip_type].diag_func(0, 0, port_base, chip_type);
	} else if ( scan_proc_pci(card_num) == 0) {
		fprintf(stderr,
				"Unable to find a recognized card in /proc/pci.\nIf there is"
				" a card in the machine, explicitly set the I/O port"
				" address\n  using '-p <ioaddr> -t <chip_type_index>'\n"
				" Use '-t -1' to see the valid chip types.\n");
		return ENODEV;
	}

	if (show_regs == 0  &&  show_eeprom == 0  &&  show_mii == 0)
		printf(" Use '-a' or '-aa' to show device registers,\n"
			   "     '-e' to show EEPROM contents, -ee for parsed contents,\n"
			   "  or '-m' or '-mm' to show MII management registers.\n");

	return 0;
}


/* Generic (all PCI diags) code to find cards. */

static char bogus_iobase[] =
"This chip has not been assigned a valid I/O address, and will not function.\n"
" If you have warm-booted from another operating system, a complete \n"
" shut-down and power cycle may restore the card to normal operation.\n";

static char bogus_irq[] =
"This chip has not been assigned a valid IRQ, and will not function.\n"
" This must be fixed in the PCI BIOS setup.  The device driver has no way\n"
" of changing the PCI IRQ settings.\n"
" See  http://www.scyld.com/expert/irq-conflict.html  for more information.\n";

static int scan_proc_bus_pci(int card_num)
{
	int card_cnt = 0, chip_idx = 0;
	int port_base;
	char buffer[514];
	unsigned int pci_bus, pci_devid, irq, pciaddr0, pciaddr1;
	int i;
	FILE *fp = fopen("/proc/bus/pci/devices", "r");

	if (fp == NULL) {
		if (debug) fprintf(stderr, "Failed to open /proc/bus/pci/devices.\n");
		return -1;
	}
	while (fgets(buffer, sizeof(buffer), fp)) {
		if (debug > 1)
			fprintf(stderr, " Parsing line -- %s", buffer);
		if (sscanf(buffer, "%x %x %x %x %x",
				   &pci_bus, &pci_devid, &irq, &pciaddr0, &pciaddr1) <= 0)
			break;
		for (i = 0; pcidev_tbl[i].vendor; i++) {
			if ((pci_devid >> 16) != pcidev_tbl[i].vendor
				|| (pci_devid & pcidev_tbl[i].device_mask) !=
				pcidev_tbl[i].device)
				continue;
			chip_idx = i;
			card_cnt++;
			/* Select the I/O address. */
			port_base = pciaddr0 & 1  ?  pciaddr0 & ~1 : pciaddr1 & ~1;
			if (card_num == 0 || card_num == card_cnt) {
				printf("Index #%d: Found a %s adapter at %#x.\n",
					   card_cnt, pcidev_tbl[chip_idx].part_name,
					   port_base);
				if (irq == 0  || irq == 255)
					printf(bogus_irq);
				if (port_base)
					pcidev_tbl[chip_idx].diag_func(0,0,port_base, i);
				else
					printf(bogus_iobase);
				break;
			}
		}
	}
	fclose(fp);
	return card_cnt;
}

static int scan_proc_pci(int card_num)
{
	int card_cnt = 0, chip_idx = 0;
	char chip_name[40];
	FILE *fp;
	int port_base;

	if ((card_cnt = scan_proc_bus_pci(card_num)) >= 0)
		return card_cnt;
	card_cnt = 0;

	fp = fopen("/proc/pci", "r");
	if (fp == NULL)
		return 0;
	{
		char buffer[514];
		int pci_bus, pci_device, pci_function, vendor_id, device_id;
		int state = 0;
		if (debug) printf("Done open of /proc/pci.\n");
		while (fgets(buffer, sizeof(buffer), fp)) {
			if (debug > 1)
				fprintf(stderr, " Parse state %d line -- %s", state, buffer);
			if (sscanf(buffer, " Bus %d, device %d, function %d",
					   &pci_bus, &pci_device, &pci_function) > 0) {
				chip_idx = 0;
				state = 1;
				continue;
			}
			if (state == 1) {
				if (sscanf(buffer, " Ethernet controller: %39[^\n]",
						   chip_name) > 0) {
					int i;
					if (debug)
						printf("Named ethernet controller %s.\n", chip_name);
					for (i = 0; pcidev_tbl[i].part_name; i++)
						if (pcidev_tbl[i].proc_pci_name  &&
							strncmp(pcidev_tbl[i].proc_pci_name, chip_name,
									strlen(pcidev_tbl[i].proc_pci_name))
							== 0) {
							state = 2;
							chip_idx = i;
							continue;
						}
					continue;
				}
				/* Handle a /proc/pci that does not recognize the card. */
				if (sscanf(buffer, " Vendor id=%x. Device id=%x",
						   &vendor_id, &device_id) > 0) {
					int i;
					if (debug)
						printf("Found vendor 0x%4.4x device ID 0x%4.4x.\n",
							   vendor_id, device_id);
					for (i = 0; pcidev_tbl[i].vendor; i++)
						if (vendor_id == pcidev_tbl[i].vendor  &&
							(device_id & pcidev_tbl[i].device_mask)
							== pcidev_tbl[i].device)
							break;
					if (pcidev_tbl[i].vendor == 0)
						continue;
					chip_idx = i;
					state = 2;
				}
			}
			if (state == 2) {
				if (sscanf(buffer, "  I/O at %x", &port_base) > 0) {
					card_cnt++;
					state = 3;
					if (card_num == 0 || card_num == card_cnt) {
						printf("Index #%d: Found a %s adapter at %#x.\n",
							   card_cnt, pcidev_tbl[chip_idx].part_name,
							   port_base);
						if (port_base)
							pcidev_tbl[chip_idx].diag_func
								(vendor_id, device_id, port_base, chip_idx);
						else
							printf(bogus_iobase);
					}
				}
			}
		}
	}
	fclose(fp);
	return card_cnt;
}

/* Convert a text media name to a NWay capability word. */
static int parse_media_type(const char *capabilities)
{
	const char *mtypes[] = {
		"100baseT4", "100baseTx", "100baseTx-FD", "100baseTx-HD",
		"10baseT", "10baseT-FD", "10baseT-HD", 0,
	};
	int cap_map[] = { 0x0200, 0x0180, 0x0100, 0x0080, 0x0060, 0x0040, 0x0020,};
	int i;
	if (debug)
		fprintf(stderr, "Advertise string is '%s'.\n", capabilities);
	for (i = 0; mtypes[i]; i++)
		if (strcasecmp(mtypes[i], capabilities) == 0)
			return cap_map[i];
	if ((i = strtoul(capabilities, NULL, 16)) <= 0xffff)
		return i;
	fprintf(stderr, "Invalid media advertisement '%s'.\n", capabilities);
	return 0;
}

/* Return the index of a valid media name.
   0x0800	Power up autosense (check speed only once)
   0x8000	Dynamic Autosense
*/
/* A table of media names to indices.  This matches the Digital Tulip
   SROM numbering, primarily because that is the most complete list.
   Other chips will have to map these number to their internal values.
*/
struct { char *name; int value; } mediamap[] = {
	{ "10baseT", 0 },
	{ "10base2", 1 },
	{ "AUI", 2 },
	{ "100baseTx", 3 },
	{ "10baseT-FDX", 0x204 },
	{ "100baseTx-FDX", 0x205 },
	{ "100baseT4", 6 },
	{ "100baseFx", 7 },
	{ "100baseFx-FDX", 8 },
	{ "MII", 11 },
	{ "Autosense", 0x0800 },
	{ 0, 0 },
};

static int get_media_index(const char *name)
{
	int i;
	for (i = 0; mediamap[i].name; i++)
		if (strcasecmp(name, mediamap[i].name) == 0)
			return i;
	if (name  &&  atoi(name) >= 00)
		return atoi(name);
	fprintf(stderr, "Invalid interface specified: it must be one of\n  ");
	for (i = 0; mediamap[i].name; i++)
		fprintf(stderr, "  %s", mediamap[i].name);
	fprintf(stderr, ".\n");
	return -1;
}


/* Chip-specific section. */

/* The chip-specific section for the Sundance Alta. */

#include <ctype.h>

static int eeprom_addr_len(long ioaddr);
static int read_eeprom(long ioaddr, int location, int addr_len);
static void write_eeprom(long ioaddr, int index, int value, int addr_len);
int mdio_read(long ioaddr, int phy_id, int location);
void mdio_write(long ioaddr, int phy_id, int location, int value);

/* Offsets to the various registers.
   Accesses need not be longword aligned. */
enum alta_offsets {
	DMACtrl=0x00,     TxListPtr=0x04, TxDMACtrl=0x08, TxDescPoll=0x0a,
	RxDMAStatus=0x0c, RxListPtr=0x10, RxDMACtrl=0x14, RxDescPoll=0x16,
	LEDCtrl=0x1a, ASICCtrl=0x30,
	EEData=0x34, EECtrl=0x36, TxThreshold=0x3c,
	FlashAddr=0x40, FlashData=0x44, TxStatus=0x46, DownCounter=0x48,
	IntrClear=0x4a, IntrEnable=0x4c, IntrStatus=0x4e,
	MACCtrl0=0x50, MACCtrl1=0x52, StationAddr=0x54,
	MaxTxSize=0x5A, RxMode=0x5c, MIICtrl=0x5e,
	MulticastFilter0=0x60, MulticastFilter1=0x64,
	RxOctetsLow=0x68, RxOctetsHigh=0x6a, TxOctetsLow=0x6c, TxOctetsHigh=0x6e,
	TxFramesOK=0x70, RxFramesOK=0x72, StatsCarrierError=0x74,
	StatsLateColl=0x75, StatsMultiColl=0x76, StatsOneColl=0x77,
	StatsTxDefer=0x78, RxMissed=0x79, StatsTxXSDefer=0x7a, StatsTxAbort=0x7b,
	StatsBcastTx=0x7c, StatsBcastRx=0x7d, StatsMcastTx=0x7e, StatsMcastRx=0x7f,
};

/* The textual names of the interrupt indications. */
static const char *intr_names[16] ={
	"Interrupt summary", "PCI bus fault", "Tx Done Event", "MAC Control Frame",
	"Receive done", "Receive started", "Software triggered interrupt",
	"Update statistics", "Link status changed", "Tx DMA done",
	"Rx DMA done",
};

/* Bits in the RxMode register. */
enum rx_mode_bits {
	AcceptAllIPMulti=0x20, AcceptMultiHash=0x10, AcceptAll=0x08, 
	AcceptBroadcast=0x04, AcceptMulticast=0x02, AcceptMyPhys=0x01,
};

/* Values read from the EEPROM, and the new image. */
#define MAX_EEPROM_SIZE 256
static u16 eeprom_contents[MAX_EEPROM_SIZE];
static u16 new_ee_contents[MAX_EEPROM_SIZE];
#define EEPROM_SA_OFFSET	0x10 	/* In words! */
#define EEPROM_CSUM_OFFSET	0	/* 0 means none. */

/* Support for Flash operations. */
static int alta_flash_in(long ioaddr, int offset) {
	outl(offset, ioaddr + FlashAddr);
	return inb(ioaddr + FlashData);
}
#ifdef LIBFLASH
static void alta_flash_out(long ioaddr, int offset, int val) {
	outl(offset, ioaddr + FlashAddr);
	outb(val, ioaddr + FlashData);
}
#endif

struct config_name { int val, mask; const char*name;}
static rcvr_mode[] = {
	{0x05, 0xff, "Normal unicast"},
	{0x07, 0xff, "Normal unicast and all multicast"},
	{0x15, 0xff, "Normal unicast and hashed multicast"},
	{0x08, 0x08, "Promiscuous"},
	{0x00, 0xff, "Uninitialized/disabled"},
	{0x00, 0x00, "Unknown/invalid"},
};

int sundance_diag(int vendor_id, int device_id, long ioaddr, int part_idx)
{
	int chip_active = 0;
	int rx_mode = inb(ioaddr + RxMode);
	int tx_status = inb(ioaddr + TxStatus);
	int mac_mode = inw(ioaddr + MACCtrl0);
	int ee_addr_len = 6, eeprom_size = 64;
	int i;

	if (mac_mode == 0xffff)
		printf("\nThe device appears not to exist!\n"
			   "The following info is probably bogus.\n\n");
	/* Start with the unique, and show the basic status. */
	printf(" Station address ");
	for (i = 0; i < 5; i++)
		printf("%2.2x:", inb(ioaddr + StationAddr + i));
	printf("%2.2x.\n", inb(ioaddr + StationAddr + i));

	for (i = 0; rcvr_mode[i].mask; i++)
		if ((rx_mode & rcvr_mode[i].mask) == rcvr_mode[i].val) break;
	printf("  Receive mode is 0x%2.2x: %s.\n", rx_mode, rcvr_mode[i].name);
	printf("  MAC mode is %4.4x: %s duplex%s.\n", mac_mode,
		   mac_mode & 0x20 ? "full" : "half",
		   mac_mode & ~0x20 ? " NON-ETHERNET-STANDARD FEATURES SET" : "");
	printf("  Tx status %2.2x, threshold %d.\n",
		   tx_status, inw(ioaddr + TxThreshold));
	if (tx_status  &&  ! chip_active) {
		printf(" Tx status stack:");
		for (i = 0; i < 32; i++) {
			printf(" %4.4x", inw(ioaddr + TxStatus));
			outw(0, ioaddr + TxStatus);
			if (inb(ioaddr + TxStatus) == 0)
				break;
		}
		printf("\n");
	}
	if (verbose || opt_a) {
		unsigned intr_status = inw(ioaddr + IntrStatus);

		printf("  Interrupt status is %4.4x:", intr_status);
		if (intr_status == 0)
			printf(" No interrupts pending.");
		else
			for (i = 0; i < 11; i++)
				if ((1<<i) & intr_status)
					printf(" %s", intr_names[i]);
		printf("\n");

		if (opt_a > 1) {
			printf("%s chip registers at %#lx",
				   pcidev_tbl[part_idx].part_name, ioaddr);
			for (i = 0; i < pcidev_tbl[part_idx].io_size; i += 2) {
				if ((i & 0x0f) == 0)
					printf("\n 0x%2.2X:", i);
				if (i == IntrClear)
					printf(" ----");
				else
					printf(" %4.4x", inw(ioaddr + i));
			}
			printf("\n");
		}
	}

	if (set_hwaddr || show_eeprom) {
		ee_addr_len = eeprom_addr_len(ioaddr);
		eeprom_size = 1 << ee_addr_len;
		printf(" EEPROM address length %d, %d words.\n",
			   ee_addr_len, eeprom_size);
		for (i = 0; i < eeprom_size; i++)
			eeprom_contents[i] = read_eeprom(ioaddr, i, ee_addr_len);
	}

	if (emergency_rewrite  &&  ! set_hwaddr)
		printf("*** Emergency EEPROM rewrite is only valid when you also "
			   "specify a new\n*** station address with -H <xx:xx:...>\n");
	if (set_hwaddr) {
		u16 backup_ee_contents[] = {
			0x2af8, 0xc262, 0x1186, 0x1102, 0x0000, 0x0000, 0x0000, 0x0000,
			0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000,
			0x5000, 0x01ba, 0xaf04, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000,
			0x3400, 0x0100, 0x3702, 0x0300, 0x883a, 0x3f04, 0x0303, 0x0103,
		};
		memcpy(new_ee_contents, eeprom_contents, eeprom_size << 1);
		if (emergency_rewrite)
			memcpy(new_ee_contents, backup_ee_contents,
				   sizeof backup_ee_contents);
		for (i = 0; i < 3; i++)
			new_ee_contents[i + EEPROM_SA_OFFSET] =
				(new_hwaddr[i*2+1]<<8) + new_hwaddr[i*2];
#if 0							/* Only do limited write checking */
		for (i = EEPROM_SA_OFFSET; i < EEPROM_SA_OFFSET + 3; i++)
			if (new_ee_contents[i] != eeprom_contents[i])
				write_eeprom(ioaddr, i, new_ee_contents[i], ee_addr_len);
#endif
#if defined(EEPROM_CSUM_OFFSET)  &&  EEPROM_CSUM_OFFSET > 0
		/* The checksum for the st201 is not documented. */
		{
			unsigned short sum = 0;
			for (i = 0; i < EEPROM_CSUM_OFFSET; i++)
				sum ^= new_ee_contents[i];
			sum = (sum ^ (sum>>8)) & 0xff
			new_ee_contents[EEPROM_CSUM_OFFSET] = sum;
			write_eeprom(ioaddr, EEPROM_CSUM_OFFSET, sum, ee_addr_len);
		}
#endif
		if ( ! do_write_eeprom)
			printf("---- These EEPROM writes will be not be done unless "
				   "the '-w' flag is passed!\n");
		for (i = 0; i < eeprom_size; i++)
			if (new_ee_contents[i] != eeprom_contents[i]) {
				if (do_write_eeprom)
					write_eeprom(ioaddr, i, new_ee_contents[i],
								 ee_addr_len);
				else
					printf("Would write %4.4x to replace %4.4x at %d.\n",
						   new_ee_contents[i], eeprom_contents[i], i);
				eeprom_contents[i] = read_eeprom(ioaddr, i, ee_addr_len);
			}
	}

	if (show_eeprom > 1) {
		int elided = 0;
		printf("EEPROM contents (%d words):", eeprom_size);
		for (i = 0; i < eeprom_size; i += 8) {
			int j;
			if (i != 0  &&  show_eeprom < 3  &&
				memcmp(&eeprom_contents[i], &eeprom_contents[i-8], 8*2) == 0)
				elided = 1;
			else {
				if (elided) {
					printf("\n    ...");
					elided = 0;
				}
				printf("\n   0x%2.2x: ", i);
				for (j = 0; j < 8; j++)
					printf(" %4.4x", eeprom_contents[i + j]);
				if (show_eeprom > 2) {
					printf("  ");
					for (j = 0; j < 8; j++) {
						int ew = eeprom_contents[i + j];
						printf("%c%c",
							   isprint(ew & 0xff) ? ew & 0xff : '_',
							   isprint(ew >>   8) ? ew >> 8   : '_' );
					}
				}
			}
		}
		printf("\n");
	}

	if (show_eeprom) {
		u32 sum = 0;
		u8 *ee = (u8*)eeprom_contents;
		for (i = 0; i < 128-1; i++)
			sum ^= eeprom_contents[i];

		printf(" EEPROM Subsystem IDs, Vendor %2.2x%2.2x Device %2.2x%2.2x.\n",
			   ee[5], ee[4], ee[7], ee[6]);
		printf("  EEPROM Station address is ");
		for (i = EEPROM_SA_OFFSET*2; i < EEPROM_SA_OFFSET*2 + 5; i++)
			printf("%2.2x:", ee[i]);
		printf("%2.2x.\n", ee[i]);
		printf("  Configuration %4.4x, ASIC Control %4.4x.\n"
			   "  Checksum %4.4x\n",
			    eeprom_contents[0], eeprom_contents[1], sum);
	}
	if (show_mii) {
		int phys[4], phy, phy_idx = 0;
		for (phy = 0; phy < 32 && phy_idx < 4; phy++) {
			int mii_status = mdio_read(ioaddr, phy, 1);
			if (mii_status != 0xffff  &&  mii_status != 0x0000) {
				phys[phy_idx++] = phy;
				printf(" MII PHY found at address %d, status 0x%4.4x.\n",
					   phy, mii_status);
			}
		}
		if (phy_idx == 0)
			printf(" ***WARNING***: No MII transceivers found!\n");
		for (phy = 0; phy < phy_idx; phy++) {
			int mii_reg;
			printf(" MII PHY #%d transceiver registers:", phys[phy]);
			for (mii_reg = 0; mii_reg < 32; mii_reg++)
				printf("%s %4.4x", (mii_reg % 8) == 0 ? "\n  " : "",
					   mdio_read(ioaddr, phys[phy], mii_reg));
			printf(".\n");
		}
#ifdef LIBMII
		show_mii_details(ioaddr, phys[0]);
		if (show_mii > 1)
			monitor_mii(ioaddr, phys[0]);
#endif
	}

#ifdef LIBFLASH
	{
		flash_in_hook = alta_flash_in;
		flash_out_hook = alta_flash_out;
		if (opt_flash_show)
			flash_show(ioaddr, 0);
		if (opt_flash_dumpfile)
			if (flash_dump(ioaddr, 0, opt_flash_dumpfile) < 0) {
				fprintf(stderr, "Failed to save the old Flash BootROM image "
						"into file '%s'.\n", opt_flash_dumpfile);
				return 3;
			}
		if (opt_flash_loadfile)
			if (flash_program(ioaddr, 0, opt_flash_loadfile) < 0) {
				fprintf(stderr, "Failed to load the new Flash BootROM image "
						"from file '%s'.\n", opt_flash_loadfile);
				return 4;
			}
	}
#else
	if (opt_flash_loadfile  || opt_flash_dumpfile  ||  opt_flash_show)
		printf("Flash operations not configured into this program.\n");
	if (opt_flash_show) {
		printf("The first few boot ROM bytes are:");
		for (i = 0; i < 16; i++)
			printf(" %2.2x", alta_flash_in(ioaddr, i));
		printf(" (%8.8x -> %2.2x).\n",
			   inl(ioaddr + FlashAddr), inb(ioaddr + FlashData));
	}
#endif

	return 0;
}

static int eeprom_addr_len(long ioaddr)
{
	return 8;
}
static int read_eeprom(long ioaddr, int location, int ignore_addr_len)
{
	int boguscnt = 1000;		/* Typical 190 ticks. */
	outw(0x0200 | (location & 0xff), ioaddr + EECtrl);
	do {
		if (! (inw(ioaddr + EECtrl) & 0x8000)) {
			if (debug)
				printf("EEPROM read took %d ticks to read %4.4x.\n",
					   1000 - boguscnt, inw(ioaddr + EEData));
			return inw(ioaddr + EEData);
		}
	} while (--boguscnt > 0);
	fprintf(stderr, "Configuration EEPROM read of location %d failed, "
			"status %4.4x.\n", location, inw(ioaddr + EEData));
	return 0;
}

static void write_eeprom(long ioaddr, int location, int value,
						 int ignore_addr_len)
{
	int boguscnt = 10000;
	if ( ! do_write_eeprom) {
		printf("Would write 0x%4.4x to offset %d.\n", value, location);
		return;
	}
	/* Write enable. */
	outw(0x00C0, ioaddr + EECtrl);
	do {
		if (! (inw(ioaddr + EECtrl) & 0x8000))
			break;
	} while (--boguscnt > 0);
	outw(value, ioaddr + EEData);
	outw(0x0100 | (location & 0xff), ioaddr + EECtrl);
	do {
		if (! (inw(ioaddr + EECtrl) & 0x8000)) {
			if (debug)
				fprintf(stderr, "EEPROM write of location %d with %#x took %d"
						" ticks, status %4.4x\n",
						location, inw(ioaddr + EEData),
						10000- boguscnt, inw(ioaddr + EECtrl));
			return;
		}
	} while (--boguscnt > 0);
	fprintf(stderr, "EEPROM write of %#4.4x to location %d with failed "
			"with status %#x.\n", location, value, inw(ioaddr + EECtrl));
	outw(0x0000 | (location & 0xff), ioaddr + EECtrl);
	return;
}

/* Read and write the MII registers using software-generated serial
   MDIO protocol.  It is just different enough from the serial EEPROM protocol
   to not share code.  The maxium data clock rate is 2.5 Mhz. */
#define mdio_out(value, mdio_addr) outb(value, mdio_addr)
#define mdio_in(mdio_addr) inb(mdio_addr)
#define mdio_delay(mdio_addr)  inb(mdio_addr)	/* Flush buffered write.*/
#define MDIO_IO_OFFSET MIICtrl

#define MDIO_SHIFT_CLK	0x01
#define MDIO_WRITE0 0x04
#define MDIO_WRITE1 0x06
#define MDIO_ENB		0x00
#define MDIO_ENB_IN		0x00
#define MDIO_DATA_READ	0x02

/* Syncronize the MII management interface by shifting 32 one bits out. */
static void mdio_sync(long ioaddr)
{
	long mdio_addr = ioaddr + MDIO_IO_OFFSET;
	int i;

	for (i = 32; i >= 0; i--) {
		mdio_out(MDIO_WRITE1, mdio_addr);
		mdio_delay(mdio_addr);
		mdio_out(MDIO_WRITE1 | MDIO_SHIFT_CLK, mdio_addr);
		mdio_delay(mdio_addr);
	}
	return;
}

int mdio_read(long ioaddr, int phy_id, int location)
{
	long mdio_addr = ioaddr + MDIO_IO_OFFSET;
	int mii_cmd = (0xf6 << 10) | (phy_id << 5) | location;
	int i, retval = 0;

	if (verbose > 2)		/* Debug: 5 */
		printf(" mdio_read(%#lx, %d, %d)..", ioaddr, phy_id, location);
	/* Establish sync by sending at least 32 logic ones. */
	mdio_sync(ioaddr);
	/* Shift the read command bits out. */
	for (i = 17; i >= 0; i--) {
		int dataval = (mii_cmd & (1 << i)) ? MDIO_WRITE1 : MDIO_WRITE0;
		if (verbose > 3)		/* Debug: 5 */
			printf("%d", (mii_cmd & (1 << i)) ? 1 : 0);

		mdio_out(MDIO_ENB | dataval, mdio_addr);
		mdio_delay(mdio_addr);
		mdio_out(MDIO_ENB | dataval | MDIO_SHIFT_CLK, mdio_addr);
		if (verbose > 3) printf(" %x", (mdio_in(mdio_addr) >> 16) & 0x0f);
		mdio_delay(mdio_addr);
	}
	if (verbose > 3) printf("-> %x", (mdio_in(mdio_addr) >> 16) & 0x0f);

	/* Read the two transition, 16 data, and wire-idle bits. */
	for (i = 19; i > 0; i--) {
		mdio_out(MDIO_ENB_IN, mdio_addr);
		mdio_delay(mdio_addr);
		retval = (retval << 1) | ((mdio_in(mdio_addr) & MDIO_DATA_READ) ? 1 : 0);
		if (verbose > 3) printf(" %x", (mdio_in(mdio_addr) >> 16) & 0x0f);
		mdio_out(MDIO_ENB_IN | MDIO_SHIFT_CLK, mdio_addr);
		mdio_delay(mdio_addr);
	}
	if (verbose > 3) printf(" == %4.4x.\n", retval);
	return (retval>>1) & 0xffff;
}

void mdio_write(long ioaddr, int phy_id, int location, int value)
{
	long mdio_addr = ioaddr + MDIO_IO_OFFSET;
	int mii_cmd = (0x5002 << 16) | (phy_id << 23) | (location<<18) | value;
	int i;

	/* Establish sync by sending 32 logic ones. */
	mdio_sync(ioaddr);
	/* Shift the command bits out. */
	for (i = 31; i >= 0; i--) {
		int dataval = (mii_cmd & (1 << i)) ? MDIO_WRITE1 : MDIO_WRITE0;
		mdio_out(MDIO_ENB | dataval, mdio_addr);
		mdio_delay(mdio_addr);
		mdio_out(MDIO_ENB | dataval | MDIO_SHIFT_CLK, mdio_addr);
		mdio_delay(mdio_addr);
	}
	/* Clear out extra bits. */
	for (i = 2; i > 0; i--) {
		mdio_out(MDIO_ENB_IN, mdio_addr);
		mdio_delay(mdio_addr);
		mdio_out(MDIO_ENB_IN | MDIO_SHIFT_CLK, mdio_addr);
		mdio_delay(mdio_addr);
	}
	return;
}

/*
 * Local variables:
 *  compile-command: "cc -O -Wall -Wstrict-prototypes -o alta-diag alta-diag.c -DLIBFLASH libflash.c -DLIBMII libmii.c"
 *  simple-compile-command: "cc -O -o alta-diag alta-diag.c"
 *  tab-width: 4
 *  c-indent-level: 4
 *  c-basic-offset: 4
 * End:
 */
