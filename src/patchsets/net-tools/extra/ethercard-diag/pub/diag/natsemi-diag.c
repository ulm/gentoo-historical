/* natsemi-diag.c: National Semiconductor DP83815 diagnostic and setup.

   This is a diagnostic and EEPROM setup program for Ethernet adapters
   based on the
	National Semiconductor DP83810 / 83815

	Written 1998-2002 by Donald Becker.
	Copyright Donald Becker and Scyld Computing Corporation

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
"natsemi-diag.c:v2.08 2/28/2005 Donald Becker (becker@scyld.com)\n"
" http://www.scyld.com/diag/index.html\n";
static char *usage_msg =
"Usage: natsemi-diag [-aDEefFGhmqrRtvVwW] [-p <IOport>] [-[AF] <media>]\n"
"  For details and other options see http://www.scyld.com/diag/index.html\n";

static const char long_usage_msg[] =
"Usage: %s [-aDfrRvVw] [-AF <speed+duplex>] [-#<BoardNum>]\n\
\n\
   Show the internal state of a network adapter.\n\
\n\
   The common usage is\n\
      natsemi-diag -aem\n\
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

extern int natsemi_diag(int vend_id, int dev_id, long ioaddr, int part_idx);

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
	{"NatSemi DP83815", "National Semiconductor DP83815",
	 0x100B, 0x0020, 0xffff, 0, 256, natsemi_diag},
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

	while ((c = getopt_long(argc, argv, "#:aA:DeEfF:G:hH:mp:qrRt:TvVwWBL:S:",
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
		case 'T': do_test++;		break;
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
/* A table of media names to EEPROM setting.
   These match the natsemi internal values.  This differs from many other
   diagnostics which use the Tulip values as a reference.
*/
struct { char *name; int value; } mediamap[] = {
	{ "Force 10baseT half duplex", 0 },
	{ "Advertise 10 Mbps half and full duplex", 1 },
	{ "Force 100 Mbps half duplex", 2 },
	{ "Advertise 10/100 Mbps half duplex", 3 },
	{ "Force 10 Mbps, full duplex", 4 },
	{ "Advertise 100 Mbps half and full duplex", 5 },
	{ "Force 100 Mbps full duplex", 6 },
	{ "Advertise 10/100 Mbps half and full duplex", 7 },
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

/* The National Semiconductor DP83810 series. */

static void natsemi_eeprom(unsigned short *ee_data);

/* Offsets to the DP83815 registers.*/
enum register_offsets {
	ChipCmd=0x00, ChipConfig=0x04, EECtrl=0x08, TestControl=0x0C,
	IntrStatus=0x10, IntrMask=0x14, IntrEnable=0x18,
	TxRingPtr=0x20, TxConfig=0x24,
	RxRingPtr=0x30, RxConfig=0x34,
	WOLCmd=0x40, PauseCmd=0x44, RxFilterAddr=0x48, RxFilterData=0x4C,
	BootRomAddr=0x50, BootRomData=0x54, StatsCtrl=0x5C, StatsData=0x60,
	RxPktErrs=0x60, RxMissed=0x68, RxCRCErrs=0x64,
};

/* The textual names of the interrupt indications. */
static const char *intr_names[] ={
	"Rx Done event", "Rx event", "Receive error", "Rx started",
	"Receiver idle", "Rx overrun", "Tx complete", "Tx packet in FIFO",
	"Transmit error", "Tx queue emptied", "Tx underrun",
	"Statistics counters full", "Driver software intr", "Wake-up packet",
	"Link change wakeup", "Error summary",
	"Rx status overrun",  "Intr-17", "Intr-18", "Intr-19",
	"PCI target abort",  "PCI master abort", "PCI system error",
	"PCI parity error", "Receiver reset done", "Transmitter reset done",
};

/* A table for emitting the configuration of a register. */
struct config_name { int val, mask; const char*name;};
static struct config_name rcvr_mode[] = {
	{0x00000000, 0x80000000, "Receive disabled"},
	{0xf0000000, 0xf0000000, "Promiscuous"},
	{0xe0000000, 0xf0100000, "Normal unicast and all multicast"},
	{0xc0200000, 0xf0300000, "Normal unicast and hashed multicast"},
	{0xc0000000, 0xf0300000, "Normal unicast and match filter"},
	{0x00, 0x00, "Unknown/invalid"},
};

/* Autonegotation selection bits in the EEPROM and ChipCmd. */
static const char *aneg_sel[8] = {
	"10 Mbps, half", "10 Mbps half and full",
	"100 Mbps half", "10/100 Mbps half",
	"10 Mbps, full", "100 Mbps half and full",
	"100 Mbps full", "10/100 Mbps half and full" };

/* Read the EEPROM and MII Management Data I/O (MDIO) interfaces.
   The EEPROM code is for the common 93c06/46 EEPROMs with 6 bit addresses. */

/* Delay between EEPROM clock transitions.
   This flushes the write buffer to prevent quick double-writes.
*/
#define eeprom_delay(ee_addr)	inl(ee_addr); inl(ee_addr)

enum EEPROM_Ctrl_Bits {
	EE_ShiftClk=0x04, EE_DataIn=0x01, EE_ChipSelect=0x08, EE_DataOut=0x02,
};
#define EE_Write0 (EE_ChipSelect)
#define EE_Write1 (EE_ChipSelect | EE_DataIn)

/* The EEPROM commands always start with 01.. preamble bits.
   Commands are prepended to the variable-length address. */
enum EEPROM_Cmds { EE_WriteCmd=5, EE_ReadCmd=6, EE_EraseCmd=7, };

/* Values read from the EEPROM, and a new image to write. */
#define EEPROM_SIZE 256
static unsigned short eeprom_contents[EEPROM_SIZE];
static unsigned short new_ee_contents[EEPROM_SIZE];
#define EEPROM_SA_OFFSET	7
#define EE_OFFSET		EECtrl	/* Register offset in I/O space. */

/* Execute a generic EEPROM command.
   Return all data output from the EEPROM, and thus may be used for
   EEPROM sizing, read, erase or write. */
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
		retval = (retval << 1) | ((inl(ee_addr) & EE_DataOut) ? 1 : 0);
	} while (--cmd_len >= 0);
	outl(EE_ChipSelect, ee_addr);

	/* Terminate the EEPROM access. */
	outl(0, ee_addr);
	if (debug > 1)
		printf(" EEPROM result is 0x%5.5x.\n", retval);
	return retval;
}

/* Wait for the EEPROM to finish what it is doing. */
static int eeprom_busy_poll(long ee_ioaddr)
{
	int i;
	outl(EE_ChipSelect, ee_ioaddr);
	for (i = 0; i < 10000; i++)			/* Typical 2000 ticks */
		if (inl(ee_ioaddr) & EE_DataOut)
			break;
	return i;
}

static int bit_reverse_16(int val)
{
	int i, result = 0;
	for (i = 0; i < 16; i++) {
		result = (result << 1) | (val & 1);
		val >>= 1;
	}
	return result;
}

/* The abstracted functions for EEPROM access. */
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
				  (((EE_WriteCmd<<addr_len) | index) << 16)
				  | bit_reverse_16(value),
				  3 + addr_len + 16);
	i = eeprom_busy_poll(ee_ioaddr);
	if (debug)
		printf(" Write finished after %d ticks.\n", i);
	/* Disable programming.  Note: this command is not instantaneous, so
	   we check for busy before the next op. */
	do_eeprom_cmd(ioaddr, (0x40 << (addr_len-4)), 3 + addr_len);
	eeprom_busy_poll(ee_ioaddr);
}

/*  MII transceiver control section.
	The 83815 series has an internal transceiver, and we present the
	management registers as if they were MII connected. */

int mdio_read(long ioaddr, int phy_id, int location)
{
	if (phy_id == 1 && location < 32)
		return inl(ioaddr + 0x80 + (location<<2)) & 0xffff;
	else
		return 0xffff;
}

void mdio_write(long ioaddr, int phy_id, int location, int value)
{
	if (phy_id == 1 && location < 32)
		outw(value, ioaddr + 0x80 + (location<<2));
}

/* Support for Flash operations. */
static int natsemi_flash_in(long ioaddr, int offset) {
	outl(offset, ioaddr + BootRomAddr);
	return inl(ioaddr + BootRomData) & 0xff;
}
#ifdef LIBFLASH
static void natsemi_flash_out(long ioaddr, int offset, int val) {
	outl(offset, ioaddr + BootRomAddr);
	outl(val, ioaddr + BootRomData);
}
#endif


int natsemi_diag(int vendor_id, int device_id, long ioaddr, int part_idx)
{
	unsigned int chip_active = inl(ioaddr + IntrEnable);
	unsigned int chip_config = inl(ioaddr + ChipConfig);
	unsigned int rx_mode = inl(ioaddr + RxFilterAddr);
	int ee_addr_len = 6, eeprom_size = 64, eeprom_change = 0;
	int i;

	if (chip_active == 0xffffffff && !opt_f) {
		printf(" * A recognized chip has been found, but it does not "
			   "appear to exist in\n * I/O space.  Use the"
			   " '-f' flag to see the register values anyway.\n");
		return 1;
	}

	/* Always show the basic status. */
	printf(" Natsemi 83815 series with station address ");
	for (i = 0; i < 6; i+=2) {
		unsigned short rf_data;
		outw(i, ioaddr + RxFilterAddr);
		rf_data = inl(ioaddr + RxFilterData);
		printf("%2.2x:%2.2x%c", rf_data & 0xff, (rf_data >> 8) & 0xff,
			   i < 4 ? ':' : '\n');
	}
	printf(" Transceiver setting %s %s duplex.\n",
		   chip_config & 0x2000 ? "Autonegotation advertise" : "force",
		   aneg_sel[(chip_config>>13) & 7]);

	if (opt_G) {
		printf("Setting the configuration register to %8.8x.\n", opt_GPIO);
		outl(opt_GPIO, ioaddr + ChipConfig);
	}

	if (verbose > 1 || show_regs) {
		unsigned int intr_status = inl(ioaddr + IntrStatus);
		char dont_read[8] = {0x10,0x00,0x01,0xff,0x00,0xff,0x00,0x00};

		if (chip_active && !opt_f) {
		  printf(" This device appears to be active, so some registers"
				 " will not be read.\n"
				 " To see all register values use the '-f' flag.\n");
		} else
			chip_active = 0;		/* Ignore the chip status with -f */

		printf("%s chip registers at %#lx",
			   pcidev_tbl[part_idx].part_name, ioaddr);
		for (i = 0; i < pcidev_tbl[part_idx].io_size; i += 4) {
			if ((i & 0x1f) == 0)
				printf("\n 0x%3.3X:", i);
			if (chip_active && (dont_read[i>>5]) & (1<<((i>>2) & 7)))
				printf(" ********");
			else
				printf(" %8.8x", (int)inl(ioaddr + i));
		}
		printf("\n");
		if (intr_status == 0xffffffff && !opt_f) {
			printf(" * A recognized chip has been found, but it does not "
				   "appear to exist in\n * I/O space.  Use the"
				   " '-f' flag to see the register values anyway.\n");
			return 1;
		}

		printf("  %snterrupt sources are pending (%8.8x).\n",
			   (intr_status & 0x03ff) ? "I": "No i", intr_status);
		if (intr_status) {
			for (i = 0; i < sizeof(intr_names)/sizeof(intr_names[0]); i++)
				if (intr_status & (1<<i))
					printf("   %s indication.\n", intr_names[i]);
		}
		for (i = 0; rcvr_mode[i].mask; i++)
			if ((rx_mode & rcvr_mode[i].mask) == rcvr_mode[i].val) break;
		printf("  Receive mode is 0x%2.2x: %s.\n", rx_mode, rcvr_mode[i].name);
		if (opt_f || ! chip_active || opt_a > 1) {
			printf("  Rx filter contents:  ");
			for (i = 0; i < 16; i+=2) {
				outw(i, ioaddr + RxFilterAddr);
				printf(" %4.4x", (int)inl(ioaddr + RxFilterData));
			}
			printf("\n");
		}
	}
	outl(rx_mode, ioaddr + RxFilterAddr);

	if (do_test && chip_active && !opt_f)
		printf(" Running these diagnostic test is not recommended while the "
			   "device is active.\n"
			   " To run them anyway, use the '-f' flag.\n");
	else if (do_test) {
		int result;
		outl(0x80, ioaddr + TestControl);
		for (i = 0; i < 10000; i++) { 		/* Typical 260 iterations. */
			if (inl(ioaddr + TestControl) & 0x40)
				break;
		}
		result = inl(ioaddr + TestControl);
		if (debug)
			printf(" Internal SRAM test took %d ticks.\n", i);
		printf(" Internal SRAM test result is %4.4x: %s.\n",
			   result, result & 0x38 ? "failed" : "passed");
		if (result & 0x38) {
			if (result & 0x20)
				fprintf(stderr, " *** Rx FIFO test failed!\n");
			if (result & 0x10)
				fprintf(stderr, " *** Tx FIFO test failed!\n");
			if (result & 0x10)
				fprintf(stderr, " *** Rx Filter test failed!\n");
			if ( ! opt_f)
				return 2;
		}
		outl(0x02, ioaddr + TestControl);
		for (i = 0; i < 10000; i++) { 		/* Typical 2500 iterations. */
			if ( ! (inl(ioaddr + TestControl) & 0x02))
				break;
		}
		result = inl(ioaddr + TestControl);
		if (debug)
			printf(" EEPROM internal test took %d ticks.\n", i);
		printf(" Configuration EEPROM checksum test result is %4.4x: %s.\n",
			   result, result & 1 ? "failed" : "passed");
	}
	if (set_hwaddr || show_eeprom || new_default_media >= 0) {
		ee_addr_len = do_eeprom_cmd(ioaddr, EE_ReadCmd << (6+16),
										3 + 6 + 16) & 0x10000 ? 8 : 6;
		eeprom_size = 1 << ee_addr_len;
		printf(" EEPROM address length %d, %d words.\n",
			   ee_addr_len, eeprom_size);
		/* Bit-reverse the result.  Damn designers mixed big-endian and LE. */
		for (i = 0; i < eeprom_size; i++)
			eeprom_contents[i] =
				bit_reverse_16(read_eeprom(ioaddr, i, ee_addr_len));
		memcpy(new_ee_contents, eeprom_contents, sizeof eeprom_contents);
	}

	if (emergency_rewrite  &&  ! set_hwaddr)
		printf("*** Emergency EEPROM rewrite is only valid when you also "
			   "specify a new\n*** station address with -H <xx:xx:...>\n");

	if (set_hwaddr) {
		u16 backup_ee_contents[] = {
			0x1385, 0xf311, 0x0b34, 0x41f3, 0x0000, 0x0000, 0x0000, 0x0000,
			0x0000, 0x0000, 0x1915, };
		if (emergency_rewrite)
			memcpy(new_ee_contents, backup_ee_contents,
				   sizeof backup_ee_contents);
		/* Grrr, damn designers dropped a bit and "fixed" the hardware
		   by documenting the EEPROM layout to work that way. */
		new_ee_contents[6] &= ~0x8000;
		new_ee_contents[6] |= new_hwaddr[0] & 1 ? 0x8000 : 0;
		new_ee_contents[7] = (new_hwaddr[0] >> 1) + (new_hwaddr[1]<<7)
			+ (new_hwaddr[2]<<15);
		new_ee_contents[8] = (new_hwaddr[2] >> 1) + (new_hwaddr[3]<<7)
			+ (new_hwaddr[4]<<15);
		new_ee_contents[9] = (new_hwaddr[4] >> 1) + (new_hwaddr[5]<<7)
			+ (new_ee_contents[9] & 0x8000);
		eeprom_change++;
	}
	if (new_default_media >= 0) {
		new_ee_contents[3] &= ~0x0070;
		new_ee_contents[3] |=  (new_default_media << 4) & 0x00F0;
		eeprom_change++;
	}
	if (eeprom_change) {
		int sum = 0;
		/* Calculate the new checksum. */
		for (i = 0; i < 11; i++) {
			unsigned short tmp = bit_reverse_16(new_ee_contents[i]);
			sum += tmp + (tmp>>8);
		}
		new_ee_contents[i] = 0xaa00 + (bit_reverse_16(0xaa - sum + 1) >> 8);
		for (i = 0; i < 16; i++)
			if (new_ee_contents[i] != eeprom_contents[i]) {
				if (do_write_eeprom)
					write_eeprom(ioaddr, i, new_ee_contents[i],
								 ee_addr_len);
				else
					printf("Would write %4.4x to replace %4.4x at %d.\n",
						   new_ee_contents[i], eeprom_contents[i], i);
			}
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
		printf("\n");
	}
	if (show_eeprom)
		natsemi_eeprom(eeprom_contents);

	if (show_mii) {
#ifdef LIBMII
		show_mii_details(ioaddr, 1);
		if (show_mii > 1)
			monitor_mii(ioaddr, 1);
#else
		int mii_reg;
		printf(" Internal PHY with MII management register.");
		for (mii_reg = 0; mii_reg < 32; mii_reg++)
			printf("%s %4.4x", (mii_reg % 8) == 0 ? "\n  " : "",
				   mdio_read(ioaddr, 1, mii_reg));
		printf(".\n");
#endif
	}

#ifdef LIBFLASH
	{
		flash_in_hook = natsemi_flash_in;
		flash_out_hook = natsemi_flash_out;
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
			printf(" %2.2x", natsemi_flash_in(ioaddr, i));
		printf(".\n");
	}
#endif

	return 0;
}

static void natsemi_eeprom(unsigned short *ee_data)
{
	int i, sum = 0;
	unsigned int val;

	printf("Decoded EEPROM contents:\n"
		   "  PCI Subsystem IDs -- Vendor %#4.4x, Device %#4.4x.\n"
		   "  PCI timer settings -- minimum grant %d, maximum latency %d.\n",
		   ee_data[0], ee_data[1], ee_data[2] >> 8, ee_data[2] & 0xff);
	printf("  Ethernet MAC Station Address "
		   "%2.2x:%2.2x:%2.2x:%2.2x:%2.2x:%2.2x.\n",
		   (ee_data[7]<<1) & 0xff, (ee_data[7]>>7) & 0xff,
		   ((ee_data[8]<<1) + (ee_data[7]>>15)) & 0xff, (ee_data[8]>>7)&0xff, 
		   ((ee_data[9]<<1) + (ee_data[8]>>15)) & 0xff, (ee_data[9]>>7)&0xff);
	printf("  Wake-On-LAN password "
		   "%2.2x:%2.2x:%2.2x:%2.2x:%2.2x:%2.2x.\n",
		   ee_data[4] & 0xff, ee_data[4]>>8,
		   ee_data[5] & 0xff, ee_data[5]>>8,
		   ee_data[6] & 0xff, ee_data[6]>>8);
	val = (ee_data[3] >> 4) & 0x0F;
	printf("  Transceiver setting 0x--%x-: %s %s duplex.\n",
		   val, val & 1 ? "advertise" : "force",
		   aneg_sel[val & 7]);
	if (val & 8)
		printf("   Flow control enabled.\n");
	for (i = 0; i < 11; i++) {
	    unsigned short tmp = bit_reverse_16(ee_data[i]);
	    sum += tmp + (tmp>>8);
	}
	sum = bit_reverse_16(0xaa - sum + 1) >> 8;
	printf("  EEPROM active region checksum read as %4.4x, vs aa%2.2x "
		   "calculated value.\n",
		   ee_data[11], sum);
	return;
}


/*
 * Local variables:
 *  compile-command: "cc -O -Wall -o natsemi-diag natsemi-diag.c"
 *  tab-width: 4
 *  c-indent-level: 4
 *  c-basic-offset: 4
 * End:
 */
