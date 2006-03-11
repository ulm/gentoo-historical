/* yellowfin-diag.c: Diagnostic/setup program for the Packet Engines Yellowfin.

   This is a diagnostic and EEPROM setup program for Ethernet adapters
   based on the following chips:
	Packet Engines "Yellowfin" G-NIC-I
	Symbios Ethernet chips such as the 53c885 used on DigitalScape's adapters.
    (Note: The EEPROM write code is not currently activated.)

   Copyright 1997-2000 by Donald Becker.
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
"yellowfin-diag.c:v2.01 2/28/2005 Donald Becker (becker@scyld.com)\n"
" http://www.scyld.com/diag/index.html\n";
static char *usage_msg =
"Usage: yellowfin-diag [-aDEefFGhmqrRtvVwW] [-p <IOport>] [-[AF] <media>]\n"
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

extern int symbios_diag(int vend_id, int dev_id, long ioaddr, int part_idx);

/* The table of known chips.
   Because of the bogus /proc/pci interface we must have both the exact
   name from the kernel, a common name and the PCI vendor/device IDs.
   This table is searched in order: place specific entries followed by
   'catch-all' general entries. */
struct pcidev_entry {
	const char *proc_pci_name;
	const char *part_name;
	int vendor, device, device_mask;
	int flags;
	int io_size;
	int (*diag_func)(int vendor_id, int device_id, long ioaddr, int part_idx);
} pcidev_tbl[] = {
	{" Ethernet controller: NCR Unknown device", "Symbios 53885",
	 0x1000, 0x0701, 0xffff, 0, 256, symbios_diag},
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


int
main(int argc, char **argv)
{
	int port_base = 0, chip_type = 0;
	int errflag = 0, show_version = 0;
	int c, longind;
	int card_num = 0;
	extern char *optarg;

	while ((c = getopt_long(argc, argv, "#:aA:DeEfF:G:hH:mp:qrRst:vVwWBL:S:",
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



/* The chip-specific section for the Symbios diagnostic. */

static int read_eeprom(long ioaddr, int location);
static int read_eeprom_serial(long ioaddr, int location, int addr_len);
#if 0
static void write_eeprom_serial(long ioaddr, int index, int value);
static void write_eeprom(long ioaddr, int index, int value);
#endif
int mdio_read(long ioaddr, int phy_id, int location);
void mdio_write(long ioaddr, int phy_id, int location, int value);
static void parse_eeprom(unsigned char *eeprom);

#define EEPROM_SIZE 256

/* Offsets to the various registers.
   All accesses need not be longword aligned. */
enum yellowfin_offsets {
	TxCtrl=0x00, TxStatus=0x04, TxPtr=0x0C,
	TxIntrSel=0x10, TxBranchSel=0x14, TxWaitSel=0x18,
	RxCtrl=0x40, RxStatus=0x44, RxPtr=0x4C,
	RxIntrSel=0x50, RxBranchSel=0x54, RxWaitSel=0x58,
	EventStatus=0x80, IntrEnb=0x82, IntrClear=0x84, IntrStatus=0x86,
	ChipRev=0x8C, DMACtrl=0x90, Cnfg=0xA0, RxDepth=0xB8, FlowCtrl=0xBC,
	MII_Cmd=0xA6, MII_Addr=0xA8, MII_Wr_Data=0xAA, MII_Rd_Data=0xAC,
	MII_Status=0xAE,
	AddrMode=0xD0, StnAddr=0xD2, HashTbl=0xD8,
	EEStatus=0xF0, EECtrl=0xF1, EEAddr=0xF2, EERead=0xF3, EEWrite=0xF4,
	EEFeature=0xF5,
};

/* The interrupt flags for a Yellowfin. */
static const char *intr_names[16] ={
	"Rx DMA event", "Rx Illegal instruction",
	"PCI bus fault during receive", "PCI parity error during receive", 
	"Tx DMA event", "Tx Illegal instruction",
	"PCI bus fault during transmit", "PCI parity error during transmit", 
	"Early receive", "Carrier sense wakeup",
};
/* Non-interrupting events. */
const char *event_names[16] = {
	"Tx Abort", "Rx frame complete", "Transmit done",
};
/* Values read from the EEPROM, and the new image. */
static unsigned char eeprom_contents[EEPROM_SIZE];

int symbios_diag(int vendor_id, int device_id, long ioaddr, int part_idx)
{
	int chip_active = 0;
	int i;

	/* It's mostly safe to examine the registers and EEPROM during
	   operation.  But warn the user, and make then pass '-f'. */
	if (!opt_f  && (inl(ioaddr + TxStatus) & 0x0400) != 0x0000) {
		printf("A potential Yellowfin chip has been found, but it appears to "
			   "be active.\nEither shutdown the network, or use the"
			   " '-f' flag.\n");
		chip_active = 0;
	}

	if (verbose || show_regs) {
		unsigned intr_status, event_status;

		printf("Station address ");
		for (i = 0; i < 5; i++)
			printf("%2.2x:", inb(ioaddr + StnAddr + i));
		printf("%2.2x.\n", inb(ioaddr + StnAddr + i));

		printf("%s chip registers at %#lx",
			   pcidev_tbl[part_idx].part_name, ioaddr);
		for (i = 0; i < pcidev_tbl[part_idx].io_size; i += 4) {
			if ((i & 0x1f) == 0)
				printf("\n 0x%3.3X:", i);
			printf(" %8.8x", inl(ioaddr + i));
		}
		printf("\n");
		intr_status = inw(ioaddr + IntrStatus);
		printf("  %snterrupt sources are pending (%4.4x).\n",
			   (intr_status & 0x03ff) ? "I": "No i", intr_status);
		if (intr_status) {
			for (i = 0; i < 16; i++)
				if (intr_status & (1<<i))
					printf("   %s indication.\n", intr_names[i]);
		}
		event_status = inw(ioaddr + EventStatus);
		if (event_status) {
			for (i = 0; i < 3; i++)
				if (event_status & (1<<i))
					printf("   %s event.\n", event_names[i]);
		}
	}

	if (0)
		eeprom_contents[0] = read_eeprom(ioaddr, 0);
	else
		for (i = 0; i < EEPROM_SIZE; i++)
			eeprom_contents[i] = read_eeprom(ioaddr, i+0x100);

	if (show_eeprom > 1) {
		printf("EEPROM byte zero is %2.2x/%2.2x.\n",
			   read_eeprom(ioaddr, 0), read_eeprom_serial(ioaddr, 0, 6));
		printf("EEPROM contents:");
		for (i = 0; i < EEPROM_SIZE; i++) {
			if ((i&15) == 0)
				printf("\n0x%3.3x: ", i + 0x100);
			printf(" %2.2x", eeprom_contents[i]);
		}
		printf("\n");
	}
	if (show_eeprom)
		parse_eeprom(eeprom_contents);

	if (show_mii) {
		int phys[4], phy, phy_idx = 0;
		for (phy = 0; phy < 32 && phy_idx < 4; phy++) {
			int mii_status = mdio_read(ioaddr, phy, 1);
			if (mii_status != 0xffff  && 
				mii_status != 0x0000) {
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

	return 0;
}

/* Serial EEPROM section.
   A "bit" grungy, but we work our way through bit-by-bit :->. */

/* The EEPROM commands include the always-set leading bit.
   They must be shifted by the number of address bits. */
enum EEPROM_Cmds { EE_WriteCmd=5, EE_ReadCmd=6, EE_EraseCmd=7, };
enum EEPROM_Ctrl_Bits {
	EE_ShiftClk=0x02, EE_ChipSelect=0x00, EE_DataOut=0x01, EE_DataIn=0x01,
	EE_Write0=0x00, EE_Write1=0x01,
};
#define EE_OFFSET		EECtrl	/* Register offset in I/O space. */
/* Delay between EEPROM clock transitions. */
#define eeprom_delay(ee_addr)	inb(ee_addr)

/* This executes a generic EEPROM command, typically a write or write enable.
   It returns the data output from the EEPROM, and thus may also be used for
   reads. */
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

/* The abstracted functions for EEPROM access. */
static int read_eeprom_serial(long ioaddr, int location, int addr_len)
{
	return do_eeprom_cmd(ioaddr, ((EE_ReadCmd << addr_len) | location) << 16,
						 3 + addr_len + 16) & 0xffff;
}

#if 0
static void write_eeprom_serial(long ioaddr, int index, int value)
{
	int i;
	long ee_addr = ioaddr + 0x9e;
	long ee_dir = ioaddr + 0x9f;
	int cmd = ((index | EE_WRITE_CMD)<< 16) | value;
	
	outb(0xfc, ee_dir);
	
	/* Shift the command bits out. */
	for (i = 26; i >= 0; i--) {
		short dataval = (cmd & (1 << i)) ? EE_DATA_WRITE : 0;
		outb(EE_ENB | dataval, ee_addr);
		eeprom_delay();
		outb(EE_ENB | dataval | EE_SHIFT_CLK, ee_addr);
		eeprom_delay();
	}
	outb(EE_ENB, ee_addr);
	
	/* Terminate the EEPROM access. */
	outb(0xff, ee_dir);
}
#endif

static int read_eeprom(long ioaddr, int location)
{
	int bogus_cnt = 1000;

	outb(location, ioaddr + EEAddr);
	outb(0x30 | ((location >> 8) & 7), ioaddr + EECtrl);
	while ((inb(ioaddr + EEStatus) & 0x80)  && --bogus_cnt > 0)
		;
	if (inb(ioaddr + EEStatus) || debug)
		printf("EEStatus is %2.2x after %d ticks, %d is %x.\n",
			   inb(ioaddr + EEStatus), 1000-bogus_cnt, location,
			   inb(ioaddr + EERead));
	return inb(ioaddr + EERead);
}

#if 0
static void write_eeprom(long ioaddr, int location, int value)
{
	int bogus_cnt = 1000;

	outb(1, ioaddr + EEFeature);	/* Enable writing. */
	outb(value, ioaddr + EEWrite);
	outb(location, ioaddr + EEAddr);
	outb(0x20 | ((location >> 8) & 7), ioaddr + EECtrl);
	while ((inb(ioaddr + EEStatus) & 0x80)  && --bogus_cnt > 0)
		;
	outb(0, ioaddr + EEFeature);	/* Disable writing. */
	printf("EEStatus is %2.2x after %d ticks, %d is now %x.\n",
		   inb(ioaddr + EEStatus), 999-bogus_cnt, location,
		   read_eeprom(ioaddr, location));
	return;
}
#endif

/* MII Managemen Data I/O accesses.
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

static void parse_eeprom(unsigned char *eeprom)
{
	int i;

	printf(" Yellowfin EEPROM contents.\n  Station address ");
	for (i = 0; i < 5; i++)
		printf("%2.2X:", eeprom[i]);
	printf("%2.2X.\n", eeprom[i]);

	return;
}


/*
 * Local variables:
 *  compile-command: "cc -O -Wall -Wstrict-prototypes -o yellowfin-diag yellowfin-diag.c `[ -f libmii.c ] && echo -DLIBMII libmii.c` `[ -f libmii.c ] && echo -DLIBFLASH libflash.c`"
 *  simple-compile-command: "cc -O -o yellowfin-diag yellowfin-diag.c"
 *  c-indent-level: 4
 *  c-basic-offset: 4
 *  tab-width: 4
 * End:
 */
