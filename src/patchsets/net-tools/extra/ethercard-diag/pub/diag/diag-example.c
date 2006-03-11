/* diag-example.c: Linux Diagnostic and setup core code for PCI adapters.

   This is a diagnostic and EEPROM setup program for PCI adapters
   based on the following chips:
	Example Ethernet diagnostic for a fictional chip named "NetTechCom Netfin".
   This file contains the chip-independent and example code.

	Copyright 1998-2004 by Donald Becker.
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
"diag-example.c:v2.09 2/28/2005 Donald Becker (becker@scyld.com)\n"
" http://www.scyld.com/diag/index.html\n";
static char *usage_msg =
"Usage: etherdiag [-aDEefFGhmqrRtvVwW] [-p <IOport>] [-[AF] <media>]\n"
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
   -F, --new-interface N	Set the default transceiver type.\n\
   -G  --parameters PARMS	Set adapter-specific parameters.\n\
   -H  --new-hwaddr 01:23:45:67:89:ab\n\
        Set a new hardware station address.  Typically disabled for safety.\n\
   -w  --write-EEPROM	 Actually write the new settings into the EEPROM.\n\
 To read and write the boot BIOS extension Flash ROM\n\
   -B       Show the first few bytes of the ROM\n\
   -L FILE  Load the Flash from FILE.\n\
   -S FILE  Store the Flash image to FILE.\n\
\n\
   -D  --debug\n\
   -v  --verbose	Report each action taken.\n\
   -V  --version	Emit version information.\n\
\n\
   -A  --advertise <speed|setting>  (See the mii-diag manual page.)\n\
\n";

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
#include <errno.h>
#include <sys/types.h>
#include <ctype.h>

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

/* Select one of the these interfaces based on Flash ROM access method. */
extern int flash_pci_rom_show(long addr_ioaddr, long data_ioaddr);
extern int flash_pci_rom_dump(long addr_ioaddr, long data_ioaddr,
							  const char *filename);
extern int flash_pci_rom_program(long addr_ioaddr, long data_ioaddr,
								 const char *filename);

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
	{"restart",	0, 0, 'r'},		/* Restart autonegotiation. */
	{"reset",	0, 0, 'R'},		/* Reset the transceiver. */
	{"chip-type",  1, 0, 't'},	/* Assume the specified chip type index. */
	{"test",	0, 0, 'T'},		/* Do register and SRAM test. */
	{"verbose",	0, 0, 'v'},		/* Verbose mode */
	{"version", 0, 0, 'V'},		/* Display version number */
	{"write-EEPROM", 1, 0, 'w'},/* Actually write the EEPROM with new vals */
	{ 0, 0, 0, 0 }
};

extern int  netfin_diag(int vend_id, int dev_id, long ioaddr, int part_idx);

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
	{"NetTechCom Netfin 1234", " Ethernet controller: NetTechCom Unknown device",
	 0x5678, 0x1234, 0xffff, 0, 256, netfin_diag},
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
	char *endptr;
	int cap_map[] = { 0x0200, 0x0180, 0x0100, 0x0080, 0x0060, 0x0040, 0x0020,};
	int i;
	if (debug)
		fprintf(stderr, "Advertise string is '%s'.\n", capabilities);
	for (i = 0; mtypes[i]; i++)
		if (strcasecmp(mtypes[i], capabilities) == 0)
			return cap_map[i];
	i = strtoul(capabilities, &endptr, 16);
	if (*endptr == 0  &&  0 < i  &&  i <= 0xffff)
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
	char *endptr;
	int i;

	if (! name)
		return -1;
	for (i = 0; mediamap[i].name; i++)
		if (strcasecmp(name, mediamap[i].name) == 0)
			return i;
	i = strtol(name, &endptr, 0);
	if (*endptr == 0)
		return i;
	fprintf(stderr, "Invalid interface specified.  It must be one of\n");
	for (i = 0; mediamap[i].name; i++)
		fprintf(stderr, "  %d %s\n", mediamap[i].value, mediamap[i].name);
	return -1;
}


/* Chip-specific section. */

/* The chip-specific section for the fictional NetTechCom Netfin diagnostic. */

static int eeprom_addr_len(long ioaddr);
static int read_eeprom(long ioaddr, int location, int addr_len);
static void write_eeprom(long ioaddr, int index, int value, int addr_len);
int mdio_read(long ioaddr, int phy_id, int location);
void mdio_write(long ioaddr, int phy_id, int location, int value);

/* Offsets to the various registers.
   Note if accesses must be longword aligned. */
enum register_offsets {
	ChipCmd=0x00, IntrStatus=0x04, IntrEnable=0x08,
	TxStatus=0x10, TxCmd=0x14, TxRingPtr=0x18,
	RxStatus=0x20, RxCmd=0x24, RxRingPtr=0x28,
	FlashAddr=0x30, FlashData=0x34,
	EECtrl=0x40, MIICtrl=0x44, LEDCtrl=0x48,
	StationAddr=0x50, RxMode=0x58, TxMode=0x5C,
	RxMissed=0x60, RxCRCErrs=0x64, MulticastFilter0=0x68,MulticastFilter1=0x6C,
	PCIBusCfg=0x70, FIFOCfg=0x74, ChipReset=0x78,
};

/* Bits in the interrupt status/mask registers. */
enum intr_status_bits {
	IntrRxDone=0x01, IntrRxEmpty=0x02, IntrRxPCIErr=0x04,
	IntrTxDone=0x10, IntrTxEmpty=0x20, IntrTxPCIErr=0x40,
	StatsMax=0x0100, LinkChange=0x0200,
	IntrNormalSummary=0x8000,	IntrAbnormalSummary=0x4000,
};

/* Utility functions for showing register states. */
/* Table formats.  Tables are zero terminated. */
struct bits_to_name { int bits;  const char *msg; };
struct bitfield_to_name { int val, mask; const char *msg;};

/* Use MSG_TBL to describe the bits set in VAL. */
void msg_if_set(const int val, const struct bits_to_name msg_tbl[])
{
	int i;
	for (i = 0; msg_tbl[i].bits; i++)
		if (msg_tbl[i].bits & val)
			printf(" %s\n", msg_tbl[i].msg);
}

/* Find the first matching MSG_TBL entry to describe VAL.
   Return the message from that entry.
   The message table is terminated with an entry using a zero mask, and
   the string from entry is the no-match default.
 */
const char *msg_match(const int val, const struct bitfield_to_name msg_tbl[])
{
	int i;
	for (i = 0; msg_tbl[i].mask; i++)
		if ((val & msg_tbl[i].mask) == msg_tbl[i].val)
			break;
	return msg_tbl[i].msg;
}


/* The textual names of the interrupt indications. */
static const char *intr_names[] ={
	"Rx Done event", "Out of Rx buffers",
	"PCI bus fault during receive", "PCI parity error during receive", 
	"Tx Done event", "Tx queue emptied",
	"PCI bus fault during transmit", "PCI parity error during transmit", 
	"Statistics counters full", "Link change wakeup",
};

/* Bits in the RxMode register. */
enum rx_mode_bits {
	AcceptErr=0x20, AcceptRunt=0x10, AcceptBroadcast=0x08,
	AcceptMulticast=0x04, AcceptAllPhys=0x02, AcceptMyPhys=0x01,
};

/* Values read from the EEPROM, and a new image to write. */
#define MAX_EEPROM_SIZE 256
unsigned short eeprom_contents[MAX_EEPROM_SIZE];
unsigned short new_ee_contents[MAX_EEPROM_SIZE];
#define EEPROM_SA_OFFSET	0x20
#define EEPROM_CSUM_OFFSET	0	/* 0 means none. */

/* Support for Flash operations. */
static int netfin_flash_in(long ioaddr, int offset) {
	outl(offset, ioaddr + FlashAddr);
	return inb(ioaddr + FlashData);
}
#ifdef LIBFLASH
static void netfin_flash_out(long ioaddr, int offset, int val) {
	outl(offset, ioaddr + FlashAddr);
	outb(val, ioaddr + FlashData);
}
#endif

/* A table for emitting the configuration of a register. */
struct config_name { int val, mask; const char*name;}
static rcvr_mode[] = {
	{0x09, 0xff, "Normal unicast"},
	{0x0D, 0xff, "Normal unicast and hashed multicast"},
	{0x0F, 0x08, "Promiscuous"},
	{0x00, 0x00, "Unknown/invalid"},
};

#include <ctype.h>
int netfin_diag(int vendor_id, int device_id, long ioaddr, int part_idx)
{
	int chip_active = 0;
	int rx_mode = inl(ioaddr + RxMode);
	int ee_addr_len = 6, eeprom_size = 64;
	int eeprom_change = 0;
	int i;

	if (! opt_f  &&  rx_mode == 0xffffffff) {
		printf("This device does not appear to exist in I/O space.\n"
			   "Perhaps it is set to ACPI power-off mode.\n"
			   "To examine this device anyway use the '-f' flag.\n");
		return 1;
	}

	/* Always show the basic status. */
	printf(" Station address ");
	for (i = 0; i < 5; i++)
		printf("%2.2x:", inb(ioaddr + StationAddr + i));
	printf("%2.2x.\n", inb(ioaddr + StationAddr + i));

	for (i = 0; rcvr_mode[i].mask; i++)
		if ((rx_mode & rcvr_mode[i].mask) == rcvr_mode[i].val) break;
	printf("  Receive mode is 0x%2.2x: %s.\n", rx_mode, rcvr_mode[i].name);

	if (verbose || show_regs) {
		unsigned intr_status;

		if (chip_active && !opt_f) {
			printf(" This device appears to be active, so some registers"
				   " will not be read.\n"
				   " To see all register values use the '-f' flag.\n");
		} else
			chip_active = 0;		/* Ignore the chip status with -f */

		if (opt_a > 1) {
			/* If reading some registers hoses normal chip operation,
			   perhaps clearing error counters or interrupts, add those
			   registers to this bitmap. */
			char dont_read[8] = {0x00,0x00,0x00,0xce,0xfd,0xed,0x7d,0xff};
			printf("%s chip registers at %#lx",
				   pcidev_tbl[part_idx].part_name, ioaddr);
			for (i = 0; i < pcidev_tbl[part_idx].io_size; i += 4) {
				if ((i & 0x1f) == 0)
					printf("\n 0x%3.3X:", i);
				if (chip_active && (dont_read[i>>5]) & (1<<((i>>2) & 7)))
					printf(" ********");
				else
					printf(" %8.8x", inl(ioaddr + i));
			}
			printf("\n");
		}
		intr_status = inw(ioaddr + IntrStatus);
		if (intr_status == 0xffff && !opt_f) {
			printf(" * A recognized chip has been found, but it does not "
				   "appear to exist in\n * I/O space.  Use the"
				   " '-f' flag to see the register values anyway.\n");
			return 1;
		}

		printf("  %snterrupt sources are pending (%4.4x).\n",
			   (intr_status & 0x03ff) ? "I": "No i", intr_status);
		if (intr_status) {
			for (i = 0; i < sizeof(intr_names)/sizeof(intr_names[0]); i++)
				if (intr_status & (1<<i))
					printf("   %s indication.\n", intr_names[i]);
		}
	}

	if (show_eeprom || set_hwaddr || new_default_media >= 0) {
		ee_addr_len = eeprom_addr_len(ioaddr);
		eeprom_size = 1 << ee_addr_len;
		printf(" EEPROM address length %d, %d words.\n",
			   ee_addr_len, eeprom_size);
		for (i = 0; i < eeprom_size; i++)
			eeprom_contents[i] = read_eeprom(ioaddr, i, ee_addr_len);
		memcpy(new_ee_contents, eeprom_contents, eeprom_size << 1);
	}

#if 0
	if (emergency_rewrite)
		fprintf(stderr, "Full EEPROM overwrite is not available in this"
				"version of the diagnostic.\n");
#else
	if (emergency_rewrite  &&  ! set_hwaddr)
		printf("*** Emergency EEPROM rewrite is only valid when you also "
			   "specify a new\n*** station address with -H <xx:xx:...>\n");
#endif
	if (set_hwaddr) {
		u16 backup_ee_contents[] = {
			0x4900, 0x1186, 0x340b, 0x0200, 0x0000, 0x00b4, 0x0000,
			0x0000, 0x0000, 0x24a7, 0x37ba, 0x5000, };
		if (emergency_rewrite)
			memcpy(new_ee_contents, backup_ee_contents,
				   sizeof backup_ee_contents);
		for (i = 0; i < 3; i++)
			new_ee_contents[i + EEPROM_SA_OFFSET] =
				(new_hwaddr[i*2]<<8) + new_hwaddr[i*2+1];
		eeprom_change++;
	}
	if (new_default_media >= 0) {
#ifdef EEPROM_MEDIA_OFFSET
		new_ee_contents[EEPROM_MEDIA_OFFSET] = new_default_media;
		eeprom_change++;
#endif
	}

	if (eeprom_change) {
#if defined(EEPROM_CSUM_OFFSET)  &&  EEPROM_CSUM_OFFSET > 0
		/* First recalculate any EEPROM checksums. */
		unsigned short sum = 0;
		for (i = 0; i < EEPROM_CSUM_OFFSET; i++)
			sum ^= new_ee_contents[i];
		new_ee_contents[EEPROM_CSUM_OFFSET] = (sum ^ (sum>>8)) & 0xff;
#endif
		/* Enable EEPROM write, if the chip requires anything special. */
		for (i = 0; i < eeprom_size; i++)
			if (new_ee_contents[i] != eeprom_contents[i]) {
				if (do_write_eeprom) {
					if (verbose)
						printf(" !!! Writing %4.4x to replace %4.4x at %d.\n",
							   new_ee_contents[i], eeprom_contents[i], i);
					write_eeprom(ioaddr, i, new_ee_contents[i],
								 ee_addr_len);
				} else
					printf("Would write %4.4x to replace %4.4x at %d.\n",
						   new_ee_contents[i], eeprom_contents[i], i);
			}
		/* Disable EEPROM write, if needed. */
	}

	if (show_eeprom > 1) {
		printf("EEPROM contents (%d words):", eeprom_size);
		for (i = 0; i < eeprom_size; i += 8) {
			int j;
			printf("\n0x%2.2x: ", i);
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
		/* Add EEPROM checksum calculations here. */
		printf("\n");
	}
	if (show_mii) {
		int phys[4], phy, phy_idx = 0;
		for (phy = 0; phy < 32 && phy_idx < 4; phy++) {
			int mii_status = mdio_read(ioaddr, phy, 1);
			if (mii_status != 0xffff   &&  mii_status != 0x0000) {
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
		flash_in_hook = netfin_flash_in;
		flash_out_hook = netfin_flash_out;
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
		for (i = 0; i < 8; i++)
			printf(" %2.2x", netfin_flash_in(ioaddr, i));
		printf(".\n");
	}
#endif

	return 0;
}

/* Serial EEPROM section.
   A "bit" grungy, but we work our way through bit-by-bit :->. */

/* The EEPROM commands always start with 01.. preamble bits.
   Commands are prepended to the variable-length address. */
enum EEPROM_Cmds { EE_WriteCmd=5, EE_ReadCmd=6, EE_EraseCmd=7, };

/*  Chip-specific EEPROM_Ctrl bits.
    Some implementations have a data pin direction bit instead of
    separate data in and out bits.
*/
#define EE_OFFSET		EECtrl	/* Register offset in I/O space. */
enum EEPROM_Ctrl_Bits {
	EE_ShiftClk=0x01, EE_ChipSelect=0x02, EE_DataOut=0x04, EE_DataIn=0x08,
	EE_Write0=0x02, EE_Write1=0x06,
};
/* Delay between EEPROM clock transitions.
   This forces out buffered PCI writes.
*/
#define eeprom_delay(ee_addr)	inb(ee_addr)

/* Execute a generic EEPROM command.
   Return all data output from the EEPROM, and thus may be used for
   EEPROM sizing, read, erase or write. */
static int do_eeprom_cmd(long ioaddr, int cmd, int cmd_len)
{
	unsigned retval = 0;
	long ee_addr = ioaddr + EE_OFFSET;

	if (debug > 1)
		printf(" EEPROM op 0x%x: ", cmd);

	outb(EE_ChipSelect | EE_ShiftClk, ee_addr);

	/* Shift the command bits out. */
	do {
		short dataval = (cmd & (1 << cmd_len)) ? EE_Write1 : EE_Write0;
		outb(dataval, ee_addr);
		eeprom_delay(ee_addr);
		if (debug > 2)
			printf("%X", inb(ee_addr) & 15);
		outb(dataval | EE_ShiftClk, ee_addr);
		eeprom_delay(ee_addr);
		retval = (retval << 1) | ((inb(ee_addr) & EE_DataIn) ? 1 : 0);
	} while (--cmd_len >= 0);
	outb(EE_ChipSelect, ee_addr);

	/* Terminate the EEPROM access. */
	outb(0, ee_addr);
	if (debug > 1)
		printf(" EEPROM result is 0x%5.5x.\n", retval);
	return retval;
}

/* Wait for the EEPROM to finish what it is doing. */
static int eeprom_busy_poll(long ee_ioaddr)
{
	int i;
	outb(EE_ChipSelect, ee_ioaddr);
	for (i = 0; i < 10000; i++)			/* Typical 2000 ticks */
		if (inb(ee_ioaddr) & EE_DataIn)
			break;
	return i;
}

/* The abstracted functions for EEPROM access. */
/* Return the number of address bits this EEPROM accepts. */
static int eeprom_addr_len(long ioaddr)
{
	return do_eeprom_cmd(ioaddr, EE_ReadCmd << (6+16), 3 + 6 + 16)
		& 0x10000 ? 8 : 6;
}

static int read_eeprom(long ioaddr, int location, int addr_len)
{
	return do_eeprom_cmd(ioaddr, ((EE_ReadCmd << addr_len) | location) << 16,
						 3 + addr_len + 16) & 0xffff;
}

static void write_eeprom(long ioaddr, int index, int value, int addr_len)
{
	long ee_ioaddr = ioaddr + EE_OFFSET;
	int i;

	/* Poll for previous op finished. */
	eeprom_busy_poll(ee_ioaddr);

	/* Enable programming modes. */
	do_eeprom_cmd(ioaddr, (0x4f << (addr_len-4)), 3 + addr_len);
	/* Do the actual write. */ 
	do_eeprom_cmd(ioaddr,
				  (((EE_WriteCmd<<addr_len) | index) << 16) | (value & 0xffff),
				  3 + addr_len + 16);
	i = eeprom_busy_poll(ee_ioaddr);
	if (debug)
		printf(" Write finished after %d ticks.\n", i);
	/* Disable programming.  Note: this command is not instantaneous, so
	   we check for busy before the next op. */
	do_eeprom_cmd(ioaddr, (0x40 << (addr_len-4)), 3 + addr_len);
	eeprom_busy_poll(ee_ioaddr);
}

/* MII - MDIO  (Media Independent Interface - Management Data I/O) accesses. */

#if ! defined(MII_USE_PARALLEL)
/*
	Read and write the MII registers using software-generated serial
	MDIO protocol.  It is just different enough from the serial EEPROM
	protocol to not share code. */
/* Normally extra abstractions layers such as this obscure the operation,
   but here keeping the code textually consistent among drivers is more
   important. */
#define mdio_out(value, mdio_addr) outb(value, mdio_addr)
#define mdio_in(mdio_addr) inb(mdio_addr)

/* The maxium data clock rate is 2.5 Mhz.
   Force out buffered PCI writes to avoid fast back-to-back operations. */
#define mdio_delay(mdio_addr) mdio_in(mdio_addr)

#define MDIO_IO_OFFSET MIICtrl

#define MDIO_SHIFT_CLK	0x01
#define MDIO_DATA_BIT	0x02
/* Derived values. */
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
		mdio_out(MDIO_ENB | MDIO_WRITE1, mdio_addr);
		mdio_delay(mdio_addr);
		mdio_out(MDIO_ENB | MDIO_WRITE1 | MDIO_SHIFT_CLK, mdio_addr);
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

#else

/* Parallel version, where the chip handles generates the serial protocol.
   These routines assume the MDIO controller is idle, and do not exit until
   the command is finished. */

int mdio_read(long ioaddr, int phy_id, int location)
{
	int i = 10000;

	if (verbose > 2)		/* Debug: 5 */
		printf(" mdio_read(%#lx, %d, %d)..", ioaddr, phy_id, location);
	outw((phy_id<<8) + location, ioaddr + MII_Addr);
	outw(1, ioaddr + MII_Cmd);
	while (--i > 0)
		if ((inw(ioaddr + MII_Status) & 1) == 0)
			break;
	return inw(ioaddr + MII_Rd_Data);
}

void mdio_write(long ioaddr, int phy_id, int location, int value)
{
	int i = 10000;

	outw((phy_id<<8) + location, ioaddr + MII_Addr);
	outw(value, ioaddr + MII_Wr_Data);

	/* Wait for the command to finish. */
	while (--i > 0)
		if ((inw(ioaddr + MII_Status) & 1) == 0)
			break;
	return;
}
#endif

/*
 * Local variables:
 *  compile-command: "cc -O -Wall -Wstrict-prototypes -o diag-example diag-example.c `[ -f libmii.c ] && echo -DLIBMII libmii.c` `[ -f libmii.c ] && echo -DLIBFLASH libflash.c`"
 *  simple-compile-command: "cc -O -Wall -o diag-example diag-example.c"
 *  tab-width: 4
 *  c-indent-level: 4
 *  c-basic-offset: 4
 * End:
 */
