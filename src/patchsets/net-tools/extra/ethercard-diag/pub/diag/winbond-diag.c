/* winbond-diag.c: Diagnostic and setup core code for Linux ethercards.

   This is a diagnostic and EEPROM setup program for Ethernet adapters
   based on the following chips:
	  Winbond w89c840
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

	Support and updates available at
	http://www.scyld.com/diag/index.html
	http://scyld.com/expert/mii-status.html
	http://scyld.com/expert/NWay.html

	Common-sense licensing statement: Using any portion of this program in
	your own program means that you must give credit to the original author
	and release the resulting code under the GPL.
*/

static char *version_msg =
"winbond-diag.c:v2.02 2/28/2005 Donald Becker (becker@scyld.com)\n"
" http://www.scyld.com/diag/index.html\n";
static char *usage_msg =
"Usage: etherdiag [-aEefFGhmqrRtvVwW] [-p <IOport>] [-[AF] <media>]\n"
"  For details and other options see http://www.scyld.com/diag/index.html\n";

static const char long_usage_msg[] =
"Usage: %s [-aDfrRvVw] [-AF <speed+duplex>] [-#<BoardNum>]\n\
\n\
   Show the internal state of a network adapter.\n\
\n\
   The common usage is\n\
      winbond-diag -aem\n\
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
        Set a new hardware station address.  Typically disabled for safety.\n\
   -w  --write-EEPROM	 Actually write the new settings into the EEPROM.\n\
\n\
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
#include <errno.h>
#include <sys/types.h>
#include <ctype.h>

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

extern int winbond_diag(int vend_id, int dev_id, long ioaddr, int part_idx);

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
	{ "Winbond W89c840", 0,
	  0x1050, 0x0840, 0xffff, 0, 128, winbond_diag },
	{ "Compex RL100-ATX", "Compex Unknown device",
	  0x11F6, 0x2011, 0xffff, 0, 128, winbond_diag },
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

/* Winbond w89c840 section. */
enum w840_offsets {
	PCIBusCfg=0x00, TxStartDemand=0x04, RxStartDemand=0x08,
	RxRingPtr=0x0C, TxRingPtr=0x10,
	IntrStatus=0x14, NetworkConfig=0x18, IntrEnable=0x1C,
	RxMissed=0x20, EECtrl=0x24, MIICtrl=0x24, BootRom=0x28, GPTimer=0x2C,
	CurRxDescAddr=0x30, CurRxBufAddr=0x34,			/* Debug use */
	MulticastFilter0=0x38, MulticastFilter1=0x3C, StationAddr=0x40,
	CurTxDescAddr=0x4C, CurTxBufAddr=0x50,
};

enum mii_reg_bits {
	MDIO_ShiftClk=0x10000, MDIO_DataIn=0x80000, MDIO_DataOut=0x20000,
	MDIO_EnbOutput=0x40000, MDIO_EnbIn = 0x00000,
	MDIO_Write0=0x40000, MDIO_Write1=0x60000,
};
#define mdio_delay(addr)  inl(addr) 	/* Extra bus turn-around as a delay. */

enum EEPROM_Ctrl_Bits {
	EE_ShiftClk=0x02, EE_Write0=0x801, EE_Write1=0x805,
	EE_ChipSelect=0x801, EE_DataIn=0x08,
};
#define EE_OFFSET		EECtrl	/* Register offset in I/O space. */

/* Values read from the EEPROM, and a new image to write. */
#define EEPROM_SIZE 64
unsigned short eeprom_contents[EEPROM_SIZE];
#define EEPROM_SA_OFFSET	0
#define EEPROM_CSUM_OFFSET	0	/* 0 means none. */

static const char *tx_state[8] = {
	"Stopped", "Reading a Tx descriptor", "Waiting for Tx to finish",
	"Loading Tx FIFO", "<invalid Tx state 5>", "Processing setup information",
	"Idle", "Closing Tx descriptor" };
static const char *rx_state[8] = {
	"Stopped", "Reading a Rx descriptor", "Waiting for Rx to finish",
	"Waiting for packets", "Suspended -- no Rx buffers",
	"Closing Rx descriptor",
	"Unavailable Rx buffer -- Flushing Rx frame",
	"Transferring Rx frame into memory",  };
static const char *bus_error[8] = {
	"Parity Error", "Master Abort", "Target abort", "Unknown 3",
	"Unknown 4", "Unknown 5", "Unknown 6", "Unknown 7"};
static const char *intr_names[16] ={
	"Tx done", "Tx complete", "Tx out of buffers", "Transmit Jabber",
	"Rx Error", "Tx FIFO Underflow", "Rx Done", "Receiver out of buffers",
	"Receiver stopped", "Unknown-9", "Tx partially done", "Timer expired",
	"Unknown-12", "PCI bus error", "Unknown-14", "Abnormal summary",
};

static void w840_mdio_sync(long ioaddr)
{
	long mdio_addr = ioaddr + MIICtrl;
	int i;

	for (i = 32; i >= 0; i--) {
		outl(MDIO_Write1, mdio_addr);
		mdio_delay(mdio_addr);
		outl(MDIO_Write1 | MDIO_ShiftClk, mdio_addr);
		mdio_delay(mdio_addr);
	}
	return;
}

static int w840_mdio_read(long ioaddr, int phy_id, int location)
{
	int i;
	int read_cmd = (0xf6 << 10) | (phy_id << 5) | location;
	int retval = 0;
	long mdio_addr = ioaddr + MIICtrl;

	if (verbose > 2)		/* Debug: 5 */
		printf(" mdio_read(%#lx, %d, %d)..", ioaddr, phy_id, location);
	w840_mdio_sync(ioaddr);
	/* Shift the read command bits out. */
	for (i = 17; i >= 0; i--) {
		int dataval = (read_cmd & (1 << i)) ? MDIO_Write1 : MDIO_Write0;
		if (verbose > 3)		/* Debug: 5 */
			printf("%d", (read_cmd & (1 << i)) ? 1 : 0);

		outl(dataval, mdio_addr);
		mdio_delay(mdio_addr);
		outl(dataval | MDIO_ShiftClk, mdio_addr);
		if (verbose > 3) printf("-%x ", (inl(mdio_addr) >> 16) & 0x0f);
		mdio_delay(mdio_addr);
	}
	if (verbose > 3) printf("-> %x", (inl(mdio_addr) >> 16) & 0x0f);

	/* Read the two transition, 16 data, and wire-idle bits. */
	for (i = 20; i > 0; i--) {
		outl(MDIO_EnbIn, mdio_addr);
		mdio_delay(mdio_addr);
		retval = (retval << 1) | ((inl(mdio_addr) & MDIO_DataIn) ? 1 : 0);
		if (verbose > 3) printf(" %x", (inl(mdio_addr) >> 16) & 0x0f);
		outl(MDIO_EnbIn | MDIO_ShiftClk, mdio_addr);
		mdio_delay(mdio_addr);
	}
	if (verbose > 3) printf(" == %4.4x.\n", retval);
	return (retval>>1) & 0xffff;
}
/* The external version. */
int mdio_read(long ioaddr, int phy_id, int location)
{  return w840_mdio_read(ioaddr, phy_id, location); }


static void w840_mdio_write(long ioaddr, int phy_id, int location, int value)
{
	int i;
	int cmd = (0x5002 << 16) | (phy_id << 23) | (location<<18) | value;
	long mdio_addr = ioaddr + MIICtrl;

	w840_mdio_sync(ioaddr);

	/* Shift the command bits out. */
	for (i = 31; i >= 0; i--) {
		int dataval = (cmd & (1 << i)) ? MDIO_Write1 : MDIO_Write0;
		outl(MDIO_EnbIn | dataval, mdio_addr);
		mdio_delay(mdio_addr);
		outl(MDIO_EnbIn | dataval | MDIO_ShiftClk, mdio_addr);
		mdio_delay(mdio_addr);
	}
	/* Clear out extra bits. */
	for (i = 2; i > 0; i--) {
		outl(MDIO_EnbIn, mdio_addr);
		mdio_delay(mdio_addr);
		outl(MDIO_EnbIn | MDIO_ShiftClk, mdio_addr);
		mdio_delay(mdio_addr);
	}
	return;
}

/* The EEPROM commands include the always-set leading bit. */
enum EEPROM_Cmds { EE_WriteCmd=5, EE_ReadCmd=6, EE_EraseCmd=7, };
/* Delay between EEPROM clock transitions. */
#define eeprom_delay(ee_addr)	inl(ee_addr)

/* This executes a generic EEPROM command, typically a write or write enable.
   It returns the data output from the EEPROM, and thus may also be used for
   reads. */
static int do_eeprom_cmd(long ioaddr, int cmd, int cmd_len)
{
	unsigned retval = 0;
	long ee_addr = ioaddr + EE_OFFSET;

	if (debug > 1)
		printf(" EEPROM op 0x%x: ", cmd);

	outl(EE_ChipSelect | EE_ShiftClk, ee_addr);

	/* Shift the command bits out. */
	do {
		short dataval = (cmd & (1 << cmd_len)) ? EE_Write1 : EE_Write0;
		outl(dataval, ee_addr);
		eeprom_delay(ee_addr);
		if (debug > 2)
			printf("%X", inl(ee_addr) & 15);
		outl(dataval | EE_ShiftClk, ee_addr);
		eeprom_delay(ee_addr);
		retval = (retval << 1) | ((inl(ee_addr) & EE_DataIn) ? 1 : 0);
	} while (--cmd_len >= 0);
	outl(EE_ChipSelect, ee_addr);

	/* Terminate the EEPROM access. */
	outl(0, ee_addr);
	if (debug > 1)
		printf(" EEPROM result is 0x%5.5x.\n", retval);
	return retval;
}

/* The abstracted functions for EEPROM access. */
static int read_eeprom(long ioaddr, int location, int addr_len)
{
	return do_eeprom_cmd(ioaddr, ((EE_ReadCmd << addr_len) | location) << 16,
						 3 + addr_len + 16) & 0xffff;
}

#ifdef LIBFLASH
/* Support for Flash operations. */
static int w840_flash_in(long ioaddr, int offset) {
	outl(offset, ioaddr + BootRom);
	outl(0x5000, ioaddr + MIICtrl);
	return inl(ioaddr + MIICtrl) & 0xff;
}
static void w840_flash_out(long ioaddr, int offset, int val) {
	outl(offset, ioaddr + BootRom);
	outl(0x3000 | val, ioaddr + MIICtrl);
}
#endif

int winbond_diag(int vendor_id, int device_id, long ioaddr, int part_idx)
{
	int chip_active = 0;
	int i;

	/* It's mostly safe to use the EEPROM and MDIO register during
	   operation.  But warn the user, and make then pass '-f'. */
	if (inl(ioaddr + NetworkConfig) & 0x2002) {
		chip_active = 1;
	}

	if (chip_active && !opt_f) {
		printf("This device appears to be active, so some registers"
			   " will not be read.\n"
			   "To see all register values use the '-f' flag.\n");
	} else
		chip_active = 0;		/* Ignore the chip status with -f */

	if (show_regs  &&  ! chip_active) {
		int num_regs = pcidev_tbl[part_idx].io_size;
		printf("%s chip registers at %#lx:",
			   pcidev_tbl[part_idx].part_name, ioaddr);
		for (i = 0; i < num_regs; i += 4)
			printf("%s %8.8x", (i % 32) == 0 ? "\n " : "", inl(ioaddr + i));
		printf("\n");
	}
	{
		int csr5 = inl(ioaddr + IntrStatus);
		int net_cfg = inl(ioaddr + NetworkConfig);

		printf(" Port selection is %s%s, %s-duplex.\n",
			   ! (net_cfg & 0x00040000) ? "10mpbs-serial" :
			   (net_cfg & 0x00800000 ? "100mbps-SYM/PCS" : "MII"),
			   net_cfg & 0x01000000 ? " 100baseTx scrambler" : "",
			   net_cfg & 0x0200 ? "full" : "half");
		printf(" Transmit %s, Receive %s, %s-duplex.\n",
			   net_cfg & 0x2000 ? "started" : "stopped",
			   net_cfg & 0x0002 ? "started" : "stopped",
			   net_cfg & 0x0200 ? "full" : "half");
		printf("  The Rx process state is '%s'.\n",
			   rx_state[(csr5 >> 17) & 7]);
		printf("  The Tx process state is '%s'.\n",
			   tx_state[(csr5 >> 20) & 7]);
		if (csr5 & 0x2000)
			printf("  PCI bus error!: %s.\n",
				   bus_error[(csr5 >> 23) & 7]);
		if (net_cfg & 0x00200000)
			printf("  The transmit unit is set to store-and-forward.\n");
		else {
			const short tx_threshold[2][4] = {{ 72, 96, 128, 160 },
											  {128,256, 512, 1024}};
			printf("  The transmit threshold is %d.\n",
				tx_threshold[(NetworkConfig&0x00440000) == 0x00040000]
				   [(NetworkConfig>>14) & 3]);
		}
		if (csr5 & 0x18000) {
			printf(" Interrupt sources are pending!  CSR5 is %8.8x.\n", csr5);
			for (i = 0; i < 16; i++)
				if (csr5 & (1<<i))
					printf("   %s indication.\n", intr_names[i]);
		}
	}

	if (opt_GPIO)
		printf("No General purpose output pins exist on this device.\n");

	/* This should be updated for sizing. */
	for (i = 0; i < EEPROM_SIZE; i++)
		eeprom_contents[i] = read_eeprom(ioaddr, i, 6);

	if (show_eeprom) {
		u32 sum = 0;
		u8 *ee = (u8*)eeprom_contents;
		if (show_eeprom > 1) {
			printf("EEPROM contents:");
			for (i = 0; i < EEPROM_SIZE; i++) {
				if ((i & 7) == 0)
					printf("\n0x%3.3x: ", i);
				printf(" %4.4x", eeprom_contents[i]);
			}
			printf("\n");
		}
		printf("EEPROM IDs: Primary Vendor %2.2x%2.2x Device %2.2x%2.2x "
			   " Subsystem Vendor %2.2x%2.2x Device %2.2x%2.2x.\n",
			   ee[15], ee[14], ee[13], ee[12], ee[11], ee[10], ee[9], ee[8]);
		printf("  EEPROM Station address is ");
		for (i = EEPROM_SA_OFFSET; i < EEPROM_SA_OFFSET + 5; i++)
			printf("%2.2x:", ee[i]);
		printf("%2.2x.\n", ee[i]);
		printf("  PCI maximum latency %d usec, minimum grant %d usec.\n",
			    ee[7], ee[6]);
		printf("  PCI revision %d, Boot ROM setting 0x%2.2x.\n",
			    ee[16], ee[17]);
		for (i = 0; i < EEPROM_SIZE-1; i++)
			sum ^= eeprom_contents[i];
	}

	/* Show up to four (not just the on-board) PHYs. */
	w840_mdio_read(ioaddr, 0, 1);
	if (show_mii) {
		int phys[4], phy, phy_idx = 0;
		w840_mdio_sync(ioaddr);
		for (phy = 0; phy < 32 && phy_idx < 4; phy++) {
			int mii_status = w840_mdio_read(ioaddr, phy, 1);
			if (mii_status != 0xffff  &&
				mii_status != 0x0000) {
				phys[phy_idx++] = phy;
				printf(" MII PHY found at address %d, status 0x%4.4x.\n",
					   phy, mii_status);
			}
		}
		if (phy_idx) {
			if (nway_advertise > 0) {
				printf(" Setting the media capability advertisement register"
					   " of PHY #%d to 0x%4.4x.\n",
					   phys[0], nway_advertise | 1);
				w840_mdio_write(ioaddr, phys[0], 4, nway_advertise | 1);
			}
			if (opt_restart) {
				printf("Restarting negotiation...\n");
				w840_mdio_write(ioaddr, phys[0], 0, 0x0000);
				w840_mdio_write(ioaddr, phys[0], 0, 0x1200);
			}
			/* Force 100baseTx-HD by mdio_write(ioaddr,phys[0], 0, 0x2000); */
			if (fixed_speed >= 0) {
				int reg0_val = 0;
				reg0_val |= (fixed_speed & 0x0180) ? 0x2000 : 0;
				reg0_val |= (fixed_speed & 0x0140) ? 0x0100 : 0;
				printf("Setting the speed to \"fixed\", %4.4x.\n", reg0_val);
				w840_mdio_write(ioaddr, phys[0], 0, reg0_val);
			}
		}
		if (phy_idx == 0)
			printf("   No MII transceivers found!\n");
#ifdef LIBMII
		else {
			if (show_mii > 1)
				show_mii_details(ioaddr, phys[0]);
			if (opt_watch || show_mii > 2)
				monitor_mii(ioaddr, phys[0]);
		}
#else
		else for (phy = 0; phy < phy_idx; phy++) {
			int mii_reg;
			printf(" MII PHY #%d transceiver registers:", phys[phy]);
			for (mii_reg = 0; mii_reg < 32; mii_reg++)
				printf("%s %4.4x", (mii_reg % 8) == 0 ? "\n  " : "",
					   w840_mdio_read(ioaddr, phys[phy], mii_reg));
			printf(".\n");
		}
#endif
	}

#ifdef LIBFLASH
	flash_in_hook = w840_flash_in;
	flash_out_hook = w840_flash_out;

	if (opt_flash_show)
		flash_show(ioaddr, 0);
	if (opt_flash_dumpfile)
		if (flash_dump(ioaddr, 0, opt_flash_dumpfile) < 0) {
			fprintf(stderr, "Failed to save the old Flash BootROM image into"
					" file '%s'.\n", opt_flash_dumpfile);
			return 3;
		}
	if (opt_flash_loadfile) {
		outl(0x3000, ioaddr + MIICtrl);
		if (flash_program(ioaddr, 0, opt_flash_loadfile) < 0) {
			fprintf(stderr, "Failed to load the new Flash BootROM image from"
					" file '%s'.\n", opt_flash_loadfile);
			return 4;
		}
	}
#else
	if (opt_flash_loadfile  || opt_flash_dumpfile  ||  opt_flash_show)
		printf("Flash operations not configured into this program.\n");
#endif

	return 0;
}


/*
 * Local variables:
 *  compile-command: "cc -O -Wall -Wstrict-prototypes -o winbond-diag winbond-diag.c `[ -f libmii.c ] && echo -DLIBMII libmii.c` `[ -f libmii.c ] && echo -DLIBFLASH libflash.c`"
 *  simple-compile-command: "cc -O -o winbond-diag winbond-diag.c"
 *  tab-width: 4
 *  c-indent-level: 4
 *  c-basic-offset: 4
 * End:
 */
