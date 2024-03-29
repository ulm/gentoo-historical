/* ne2k-pci-diag.c: Diagnostics/EEPROM setup for PCI NE2000 clones.

   This is a diagnostic and EEPROM setup program for PCI NE2000 Ethernet
   adapters.

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

   References
	http://www.scyld.com/diag/index.html
	RealTek RTL8029AS datasheet, available from www.RealTek.com.tw.
	Holtek HT80232 ECON-PCI datasheet, www.holtek.com.tw
	http://www.winbond.com.tw/PDF/sheet/w89c940f.pdf
	http://www.VIA.com.tw/products/prodamazon.htm

	Common-sense licensing statement: Using any portion of this program in
	your own program means that you must give credit to the original author
	and release the resulting code under the GPL.
*/

static char *version_msg =
"ne2k-pci-diag.c:v2.06 2/28/2005 Donald Becker (becker@scyld.com)\n"
" http://www.scyld.com/diag/index.html\n";
static char *usage_msg =
"Usage: ne2k-pci-diag [-aEefFmqrRtvVwW] [-p <IOport> [-t <chip-type>]]\n";

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

struct option longopts[] = {
 /* { name  has_arg  *flag  val } */
	{"show_all_registers",	0, 0, 'a'},	/* Print all registers. */
	{"help",	0, 0, 'h'},	/* Give help */
	{"show-eeprom",  0, 0, 'e'}, /* Dump EEPROM contents (-ee valid). */
	{"emergency-rewrite",  0, 0, 'E'}, /* Re-write a corrupted EEPROM.  */
	{"force-detection",  0, 0, 'f'},
	{"new-interface",  1, 0, 'F'},	/* New interface (built-in, AUI, etc.) */
	{"new-hwaddr",  1, 0, 'H'},	/* Set a new hardware address. */
	{"port-base",  1, 0, 'p'},	/* Use the specified I/O address. */
	{"quiet",	0, 0, 'q'},		/* Decrease verbosity */
	{"chip-type",  1, 0, 't'},	/* Assume the specified chip type index. */
	{"test",	0, 0, 'T'},		/* Do register and SRAM test. */
	{"verbose",	0, 0, 'v'},		/* Verbose mode */
	{"version", 0, 0, 'V'},		/* Display version number */
	{"write-EEPROM", 1, 0, 'w'},/* Actually write the EEPROM with new vals */
	{ 0, 0, 0, 0 }
};

enum ne2k_chip_flags {
	ONLY_16BIT_IO=1, HOLTEK_EE=2, RTL_EE=4, WINBOND_EE=8, VIA_EE=16,
	BOGUS_WINBOND=0x100,
};
extern int    ne2k_diag(int vend_id, int dev_id, long ioaddr, int part_idx);

/* The table of known chips.
   Because of the bogus /proc/pci interface we must have both the exact
   name and a PCI vendor/device IDs.
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
	{ "Generic PCI NE2000 clone", "Generic PCI NE2000 clone",
	  0xffff, 0x2000, 0xffff, 0, 32, ne2k_diag},
	/* First three are ordered for the 'unknown_eeprom_message' message. */
	{ "Realtek 8029", "RealTek RTL8029",
	  0x10ec, 0x8029, 0xffff, RTL_EE, 32, ne2k_diag},
	{ "Winbond 89C940", "Winbond 89C940",
	  0x1050, 0x0940, 0xffff, WINBOND_EE, 32, ne2k_diag},
	{ "Holtek HT80229", "Holtek HT80229",
	  0x12c3, 0x5598, 0xffff, HOLTEK_EE, 64, ne2k_diag},
	{ "Via 82C926", "Via 82C926",
	  0x1106, 0x0926, 0xffff, VIA_EE, 32, ne2k_diag},
	{ "Compex RL2000", "Compex RL2000",
	  0x11f6, 0x1401,  0xffff, 0, 32, ne2k_diag},
	{ "KTI ET32P2", "KTI ET32P2",
	  0x8e2e, 0x3000, 0xffff, 0, 32, ne2k_diag},
	{ "NetVin NV5000", "NetVin NV5000",				/* Renumbered RTL8029. */
	  0x4a14, 0x5000, 0xffff, RTL_EE, 32, ne2k_diag},
	{ "SureCom NE34", "SureCom NE34",
	  0x10bd, 0x0e34, 0xffff, 0, 32, ne2k_diag},
	{ "Winbond 940 (unprogrammed)","Winbond 940 (unprogrammed)",
	  0x1050, 0x5a5a,  0xffff, WINBOND_EE, 32, ne2k_diag},
	{ "Holtek HT80232", "Holtek HT80232",
	  0x12c3, 0x0058, 0xffff, ONLY_16BIT_IO | HOLTEK_EE, 64, ne2k_diag},
	{ "Winbond 89C940 (misprogrammed)", 0,
	  0x8c4a, 0x1980, 0xffff, WINBOND_EE | BOGUS_WINBOND, 32, ne2k_diag},
	{ 0, }
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
int new_default_media = -1;
static unsigned char new_hwaddr[6], set_hwaddr = 0;
static int emergency_rewrite = 0;

static int scan_proc_pci(int card_num);
static int get_media_index(const char *name);


int
main(int argc, char **argv)
{
	int port_base = 0, chip_type = 0;
	int errflag = 0, show_version = 0;
	int c, longind;
	int card_num = 0;
	extern char *optarg;

	while ((c = getopt_long(argc, argv, "#:aA:DeEfF:G:mp:qrRst:TvVwH:",
							longopts, &longind))
		   != -1)
		switch (c) {
		case '#': card_num = atoi(optarg);	break;
		case 'a': show_regs++; opt_a++;		break;
		case 'D': debug++;			break;
		case 'e': show_eeprom++;	break;
		case 'E': emergency_rewrite++;	 break;
		case 'f': opt_f++;			break;
		case 'F': new_default_media = get_media_index(optarg);
			if (new_default_media < 0)
				errflag++;
			break;
		case 'G': opt_G++; opt_GPIO = strtoul(optarg, NULL, 16); break;
		case 'H': {
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
		perror("ne2k-pci-diag: iopl()");
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

/* The chip-specific section for the PCI NE2000 diagnostic. */

/* Constants with useful names (you will still need the datasheet though). */
#define EEPROM_SIZE 64

/* Values read from the EEPROM, and the new image. */
unsigned short eeprom_contents[EEPROM_SIZE];
unsigned short new_ee_contents[EEPROM_SIZE];

/* Values from 8390.h, here to avoid version skew and bogus email. */
#define NS_CMD	 (dev->base_addr)
#define NS_BASE	 (dev->base_addr)
#define NS_DATAPORT		0x10	/* NatSemi-defined port window offset. */
#define NE_DATAPORT		0x10	/* NatSemi-defined port window offset. */
#define NS_RESET		0x1f	/* Issue a read to reset, a write to clear. */

#define NE1SM_START_PG	0x20	/* First page of TX buffer */
#define NE1SM_STOP_PG	0x40	/* Last page +1 of RX ring */
#define NESM_START_PG	0x40	/* First page of TX buffer */
#define NESM_STOP_PG	0x80	/* Last page +1 of RX ring */

#define E8390_CMD		0x00	/* The command register (for all pages) */
#define E8390_STOP		0x01	/* Stop and reset the chip */
#define E8390_START		0x02	/* Start the chip, clear reset */
#define E8390_RREAD		0x08	/* Remote read */
#define E8390_NODMA		0x20	/* Remote DMA */
#define E8390_PAGE0		0x00	/* Select page chip registers */
#define E8390_PAGE1		0x40	/* using the two high-order bits */
#define E8390_PAGE2		0x80	/* Page 2 is has only a few defined. */
#define E8390_PAGE3		0xC0	/* Page 3 is propriatary data. */

#define E8390_RXOFF 0x20		/* EN0_RXCR: Accept no packets */
#define E8390_TXOFF 0x02		/* EN0_TXCR: Transmitter off */

/* Page 0 register offsets. */
#define EN0_CLDALO		0x01	/* Low byte of current local dma addr  RD */
#define EN0_STARTPG		0x01	/* Starting page of ring bfr WR */
#define EN0_CLDAHI		0x02	/* High byte of current local dma addr	RD */
#define EN0_STOPPG		0x02	/* Ending page +1 of ring bfr WR */
#define EN0_BOUNDARY	0x03	/* Boundary page of ring bfr RD WR */
#define EN0_TSR			0x04	/* Transmit status reg RD */
#define EN0_TPSR		0x04	/* Transmit starting page WR */
#define EN0_NCR			0x05	/* Number of collision reg RD */
#define EN0_TCNTLO		0x05	/* Low	byte of tx byte count WR */
#define EN0_FIFO		0x06	/* FIFO RD */
#define EN0_TCNTHI		0x06	/* High byte of tx byte count WR */
#define EN0_ISR			0x07	/* Interrupt status reg RD WR */
#define EN0_CRDALO		0x08	/* low byte of current remote dma address RD */
#define EN0_RSARLO		0x08	/* Remote start address reg 0 */
#define EN0_CRDAHI		0x09	/* high byte, current remote dma address RD */
#define EN0_RSARHI		0x09	/* Remote start address reg 1 */
#define EN0_RCNTLO		0x0a	/* Remote byte count reg WR */
#define EN0_RCNTHI		0x0b	/* Remote byte count reg WR */
#define EN0_RSR			0x0c	/* rx status reg RD */
#define EN0_RXCR		0x0c	/* RX configuration reg WR */
#define EN0_TXCR		0x0d	/* TX configuration reg WR */
#define EN0_COUNTER0	0x0d	/* Rcv alignment error counter RD */
#define EN0_DCFG		0x0e	/* Data configuration reg WR */
#define EN0_COUNTER1	0x0e	/* Rcv CRC error counter RD */
#define EN0_IMR			0x0f	/* Interrupt mask reg WR */
#define EN0_COUNTER2	0x0f	/* Rcv missed frame error counter RD */

/* The EEPROM commands include the alway-set leading bit. */
enum EEPROM_Cmds { EE_WriteCmd=5, EE_ReadCmd=6, EE_EraseCmd=7, };

/* Info for the rtl8029 configuration. */
static const char *const rtl_xcvr[4] = {
		"10baseT/coax (autoselected on 10baseT link beat)",
		"10baseT with link test disabled", "10base5 / AUI", "10base2"};
static int rtl_romsize[4] = { 0, 8, 16, 32};


static void do_ne2k_eeprom(long ioaddr, int part_idx);
static int read_eeprom(int chip_flags, long ioaddr, int offset, int addr_len);
static int do_update(int chip_flags, long ioaddr, int index, int addr_len,
					 const char *field_name, int old_value, int new_value);
static void parse_8029_eeprom(unsigned short *ee_data);
static void parse_holtek_eeprom(unsigned short *ee_data);
static void parse_winbond_eeprom(unsigned short *ee_data);

int ne2k_diag(int vend_id, int dev_id, long ioaddr, int part_idx)
{
	int chip_active = 0;
	int saved_window = inb(E8390_CMD);
	int capabilities = pcidev_tbl[part_idx].flags;
	int i;

	/* It's mostly safe to examine the registers and EEPROM during
	   operation.  But warn the user, and make then pass '-f'. */
	if ((inb(ioaddr + E8390_CMD) & 0xC0) == 0x00)
		chip_active = 1;

	if (verbose || show_regs) {
		unsigned intr_status;
		int j;

		if (chip_active && ! opt_f) {
			printf("The 8390 core appears to be active, so some registers"
				   " will not be read.\n"
				   "To see all register values use the '-f' flag.\n");
		}

		printf("Initial window %d, registers values by window:\n",
			   saved_window >> 6);
		for (j = 0; j < 0x100; j+=0x40) {
			printf("  Window %d:", j>>6);
			outw(j, ioaddr + E8390_CMD);
			for (i = 0; i < 16; i++) {
				printf(" %2.2x", inb(ioaddr + i));
			}
			printf(".\n");
		}
		if (capabilities & RTL_EE) {
			int config2 = inb(ioaddr + 5);
			int config3 = inb(ioaddr + 6);
			printf(" RTL8029 transceiver: %s %s duplex.\n"
				   " %s %dK boot ROM.\n",
				   rtl_xcvr[config2>>6],
				   config3 & 0x40 ? " forced full" :"half",
				   config2 & 0x20 ? " flow control enabled," : "",
				   rtl_romsize[config2 & 3]);
		}
		outb(0, ioaddr + E8390_CMD);
		intr_status = inb(ioaddr + EN0_ISR);
		printf("\n %snterrupt sources are pending (%2.2x).\n",
			   (intr_status & 0xff) ? "I": "No i", intr_status);
		if (intr_status) {
			const char *intr_names[] = {
				"Rx packet", "Tx done", "Rx error", "Tx error", "Rx overflow",
				"Counter full", "Transfer done", "Resetting" };
			for (i = 0; i < 13; i++)
				if (intr_status & (1<<i))
					printf("   %s indication.\n", intr_names[i]);
		}
	}

	do_ne2k_eeprom(ioaddr, part_idx);

	if (do_test) {
		/* Run a loopback test. */
	}
	outb(saved_window, ioaddr + E8390_CMD);
	return 0;
}


/* Serial EEPROM section. */

#include <ctype.h>

/* First, the definitions for the serial EEPROM bits. */
struct ee_ctrl_bits {
	int offset;
	unsigned char shift_clk,	/* Bit that drives SK (shift clock) pin */
		read_bit,				/* Mask bit for DO pin value */
		write_0, write_1,		/* Enable chip and drive DI pin with 0 / 1 */
		disable;				/* Disable chip. */
} ee_ctrl_tbl[] = {
	{ 0x01,  0x04, 0x01, 0x88, 0x8A, 0x00 }, 			/* RTL8029 */
	{ 0x22,  0x12, 0x04, 0x11, 0x19, 0x00 },			/* HolTek */
	{ 0x10,  0x04, 0x01, 0x88, 0x8A, 0x00 },			/* VIA */
};

/* This executes a generic EEPROM command, typically a write or write enable.
   It returns the data output from the EEPROM, and thus may also be used for
   reads and EEPROM sizing. */
static int do_eeprom_cmd(int chip_flags, long ioaddr, int cmd, int cmd_len)
{
	struct ee_ctrl_bits ee = ee_ctrl_tbl[chip_flags & RTL_EE ? 0 : 1];
	long ee_addr = ioaddr + ee.offset;
	unsigned retval = 0;

	if (debug > 1)
		printf(" EEPROM op 0x%x: ", cmd);

	/* Shift the command bits out. */
	do {
		short dataval = (cmd & (1 << cmd_len)) ? ee.write_1 : ee.write_0;
		outb(dataval, ee_addr);
		inb(ee_addr);			/* Timing delay */
		if (debug > 2)
			printf("%X", inb(ee_addr) & 15);
		outb(dataval | ee.shift_clk, ee_addr);
		inb(ee_addr);			/* Timing delay */
		retval = (retval << 1) | ((inb(ee_addr) & ee.read_bit) ? 1 : 0);
	} while (--cmd_len >= 0);
	outb(ee.write_0, ee_addr);

	/* Terminate the EEPROM access. */
	outb(ee.disable, ee_addr);
	if (debug > 1)
		printf(" EEPROM result is 0x%5.5x.\n", retval);
	return retval;
}

/* Wait for the EEPROM to finish what it is doing. */
static int eeprom_busy_poll(int chip_flags, long ioaddr)
{
	struct ee_ctrl_bits ee = ee_ctrl_tbl[chip_flags & RTL_EE ? 0 : 1];
	long ee_addr = ioaddr + ee.offset;
	int i;

	outb(ee.write_0, ee_addr);
	for (i = 0; i < 10000; i++)			/* Typical 2000 ticks */
		if (inb(ee_addr) & ee.read_bit)
			break;
	return i;
}

/* The abstracted functions for serial EEPROM access. */
static int read_eeprom(int chip_flags, long ioaddr, int location, int addr_len)
{
	if (chip_flags & WINBOND_EE) {
		int boguscnt;
		outb(0x80, ioaddr + 2);			/* Read command. */
		outw(location, ioaddr + 4);		/* Address to read. */
		for (boguscnt = 10000; boguscnt >= 0; boguscnt--)
			if ((inb(ioaddr + 2) & 0x80) == 0)
				break;
		inw(ioaddr + 4);
		return inw(ioaddr + 4);
	} else
		return do_eeprom_cmd(chip_flags, ioaddr,
							 ((EE_ReadCmd << addr_len) | location) << 16,
							 3 + addr_len + 16) & 0xffff;
}

static void write_eeprom(int chip_flags, long ioaddr, int index,
						 int value, int addr_len)
{
	int i;

	if (chip_flags & WINBOND_EE) {	/* The chip handles the write for us. */
		int boguscnt;
		/* The chip should already be in PAGE3 from the read. */
		outb(0xC0, ioaddr + 2);		/* Write command. */
		outw(index, ioaddr + 4);	/* Address to write. */
		outw(value, ioaddr + 4);	/* Data to write. */
		for (boguscnt = 10000; boguscnt >= 0; boguscnt--)
			if ((inb(ioaddr + 2) & 0x80) == 0)
				break;
		return;
	}

	/* Poll for previous op finished. */
	eeprom_busy_poll(chip_flags, ioaddr);

	/* Enable programming modes. */
	do_eeprom_cmd(chip_flags, ioaddr, (0x4f << (addr_len-4)), 3 + addr_len);
	/* Do the actual write. */
	do_eeprom_cmd(chip_flags, ioaddr,
				  (((EE_WriteCmd<<addr_len) | index)<<16) | (value & 0xffff),
				  3 + addr_len + 16);
	i = eeprom_busy_poll(chip_flags, ioaddr);
	if (debug)
		printf(" Write finished after %d ticks.\n", i);
	/* Disable programming.  Note: this command is not instantaneous, but
	   we check for busy before the next write. */
	do_eeprom_cmd(chip_flags, ioaddr, (0x40 << (addr_len-4)), 3 + addr_len);
}

static int do_update(int chip_flags, long ioaddr, int index, int addr_len,
					 const char *field_name, int old_value, int new_value)
{
	if (old_value != new_value) {
		if (do_write_eeprom) {
			printf(" Writing new %s entry 0x%4.4x.\n",
				   field_name, new_value);
			write_eeprom(chip_flags, ioaddr, index, new_value, addr_len);
			if (read_eeprom(chip_flags, ioaddr, index, addr_len) != new_value)
				printf(" WARNING: Write of new %s entry 0x%4.4x did not "
					   "succeed!\n", field_name, new_value);
		} else
			printf(" Would write new %s entry 0x%4.4x (old value 0x%4.4x).\n",
				   field_name, new_value, old_value);
		return 1;
	}
	return 0;
}


static void parse_8029_eeprom(unsigned short *ee_data)
{
	unsigned char *p = (void *)ee_data;
	int i;

	printf("Parsing the EEPROM of a RTL8029:\n");
	printf(" Station Address ");
	for (i = 2; i < 7; i++)
		printf("%2.2X:", p[i]);
	printf("%2.2X (used as the ethernet address).\n", p[i]);
	printf(" Configuration is %2.2x %2.2x:\n   %dK boot ROM, %s duplex\n"
		   "   Transceiver: %s.\n", p[1], p[0], rtl_romsize[p[0] & 3],
		   p[1] & 0x40 ? " forced full" :"half",
		   rtl_xcvr[p[1]>>6]);
	printf(" PCI Vendor ID %#4.4x  Device ID %#4.4x\n"
		   "  Subsystem ID: vendor %#4.4x device %#4.4x\n",
		   ee_data[60], ee_data[61], ee_data[62], ee_data[63]);
	return;
}

static void parse_holtek_eeprom(unsigned short *ee_data)
{
	unsigned char *p = (void *)ee_data;
	int i;

	printf("Parsing the EEPROM of a HolTek NE2000 clone:\n");
	printf("  Station Address ");
	for (i = 0; i < 5; i++)
		printf("%2.2X:", p[i]);
	printf("%2.2X (used as the ethernet address).\n", p[i]);
	printf(" PCI Vendor ID %#4.4x, Subsystem IDs: vendor %#4.4x device "
		   "%#4.4x\n  System control 0x%2.2x  MAC config 0x%2.2x\n",
		   ee_data[6], ee_data[4], ee_data[5], ee_data[3]>>8, ee_data[3]&0xff);
	return;
}

static const char *const winbond_xcvr[4] =
{ "10baseT", "10base2", "AUI",
  "10baseT extended length / reduced squelch level",};
static const char *const winbond_rom[8] =
{ "No", "No", "8KB", "16KB", "32KB", "64KB", "128KB", "256KB" };

static const char winbond_bogus_msg[] = "\n\
This board has bogus information written into the configuration EEPROM.\n\
The configuration table is for a Realtek chip, but this board is using\n\
a Winbond 89c940 chip.  This misprogramming usually results in an invalid\n\
station address, and prevents the board from being detected by standard\n\
drivers.\n\
\n\
To reprogram the configuration EEPROM select a new station address such as\n\
40:00:00:12:34:56 and run this diagnostic with the options\n\
    --write-EEPROM --emergency-rewrite --new-hwaddr 40:00:00:12:34:56\n\
";

static void parse_winbond_eeprom(unsigned short *ee_data)
{
	unsigned char *p = (void *)ee_data;
	int i;

	printf("Parsing the EEPROM of a Winbond PCI NE2000:\n");
	printf("  Station Address ");
	for (i = 0; i < 5; i++)
		printf("%2.2X:", p[i]);
	printf("%2.2X (used as the ethernet address).\n", p[i]);
	printf(" PCI ID Vendor %#4.4x device %#4.4x  revision %d.\n"
		   "   PCI maximum latency %d  minimum grant %d.\n"
		   "   System control 0x%2.2x:\n"
		   "     %s transceiver, %s\n"
		   "     %s boot ROM",
		   ee_data[9], ee_data[10], p[22], p[17], p[16], p[23],
		   winbond_xcvr[p[23] & 3],
		   p[23] & 8 ? "no link beat required" : "autoselect by link beat",
		   winbond_rom[p[23]>>5]);
	if (ee_data[9] ==  0x8c4a)
		printf("%s", winbond_bogus_msg);
			   
	return;
}

static char unknown_eeprom_message[] = "\n\
 No information is known about how to read or write the configuration\n\
 EEPROM of this NIC board.  It is likely that this NIC is using a common\n\
 chip with a unique PCI ID.  It may be possible to read the EEPROM by\n\
 explicitly specifying the chip type and I/O address:\n\
   ne2k-pci-diag -t 1 -p <ioaddr>	# For Realtek rtl8029 chip\n\
   ne2k-pci-diag -t 2 -p <ioaddr>	# For Winbond 89C940 chip\n\
   ne2k-pci-diag -t 3 -p <ioaddr>	# For Holtek HT80229 chip\n\
 If one of these is required, please send a report to becker@scyld.com.\n\
";
static char no_rewrite_msg[] = "\n\
*** Emergency EEPROM rewrite is not yet available for this chip type.\n\
 ** See the Scyld diagnostic web page for updates and more information.\n\
 ** http://www.scyld.com/diag/index.html\n";

/* The examples below have 00:11:22:33:44:55 as the station address. */
static unsigned short winbond_default_eeprom[] = {
	0x1100, 0x3322, 0x5544, 0x0000, 0x0000, 0x0000, 0x0000, 0x5757,
	0x0000, 0x1050, 0x0940, 0x0000, };
static unsigned short via_default_eeprom[] = {
	0x1100, 0x3322, 0x5544, 0x0000,	/* [3] == checksum+boardID */
	0x0000, 0x0000, 0x0000, 0x0123,	/* [7] = subvendor ID */
	0x5742, 0x0000, 0x0000, 0x0000,
	0x0000, 0x0000, 0xBBAA, 0x73CC}; /* Config AA BB and CC, 0x73 locks. */


/* Read, display, and possibly change the configuration EEPROM. */
static void do_ne2k_eeprom(long ioaddr, int part_idx)
{
	int capabilities = pcidev_tbl[part_idx].flags;
	int ee_addr_len = 6;		/* No known boards use a larger EEPROM. */
	int i;

	/* Read the EEPROM. */
	if (capabilities & (RTL_EE | HOLTEK_EE | WINBOND_EE)) {
		if (capabilities & (RTL_EE | WINBOND_EE))
			outb(E8390_PAGE3, ioaddr + E8390_CMD);
		for (i = 0; i < EEPROM_SIZE; i++)
			eeprom_contents[i] =
				read_eeprom(capabilities, ioaddr, i, ee_addr_len);
	} else if (capabilities & VIA_EE) {
		/* This may not be true, but we don't have an unprogrammed board
		   to confirm functionality.
		   Contact me (becker@scyld.com) if you want to work with me to
		   get the EEPROM operations working. */
		printf("The VIA Amazon EEPROM is locked."
			   "  It cannot be read or updated.\n");
		return;
	} else {
		if (show_eeprom)
			printf(unknown_eeprom_message);
		return;
	}

	if (emergency_rewrite  &&  ! (capabilities & (WINBOND_EE)))
		fprintf(stderr, no_rewrite_msg);
	if (emergency_rewrite  &&  ! set_hwaddr)
		fprintf(stderr, "*** Emergency EEPROM rewrite is only valid when you"
				" also specify a new\n"
				"*** station address with -H <xx:xx:...>\n");

	if (set_hwaddr) {
		int eeprom_sa_offset = capabilities & RTL_EE ? 1 : 0;
		const char *const field_names[] = {
			"MAC address 0/1", "MAC address 2/3", "MAC address 4/5", };
		memcpy(new_ee_contents, eeprom_contents, sizeof(eeprom_contents));
		if (emergency_rewrite) {
			if (capabilities & WINBOND_EE)
				memcpy(new_ee_contents, winbond_default_eeprom,
					   sizeof winbond_default_eeprom);
			else if (capabilities & VIA_EE)
				memcpy(new_ee_contents, via_default_eeprom,
					   sizeof via_default_eeprom);
		}

		for (i = 0; i < 3; i++) {
			new_ee_contents[i + eeprom_sa_offset] =
				new_hwaddr[i*2] + (new_hwaddr[i*2+1]<<8);
		}
		if (emergency_rewrite && (capabilities & (WINBOND_EE))) {
			printf("Writing new configuration EEPROM contents.\n");
			for (i = 0; i < EEPROM_SIZE; i++)
				if (new_ee_contents[i] != eeprom_contents[i])
					do_update(capabilities, ioaddr, i, ee_addr_len, "EEPROM",
							  eeprom_contents[i], new_ee_contents[i]);
		} else {
			printf("Writing new MAC station address.\n");
			for (i = eeprom_sa_offset; i < eeprom_sa_offset + 3; i++)
				if (new_ee_contents[i] != eeprom_contents[i])
					do_update(capabilities, ioaddr, i, ee_addr_len,
							  field_names[i - eeprom_sa_offset],
							  eeprom_contents[i], new_ee_contents[i]);
		}
		/* Re-read all contents. */
		for (i = 0; i < EEPROM_SIZE; i++)
			eeprom_contents[i] =
				read_eeprom(capabilities, ioaddr, i, ee_addr_len);
	}

#if ! defined(ENABLE_EEPROM_UPDATE)
	if (new_default_media >= 0) {
		printf("This release of the diagnostic does not include the code to\n"
			   "write the default transceiver setting.\n");
	}
#else
	if ((new_default_media & 0xff) > 4) {
		fprintf(stderr "Media type %s (index %d) is invalid for this "
				"board.\n", (new_default_media > 10) ? "<INVALID>" :
				mediamap[new_default_media & 31].name, new_default_media);
		
	} else if (new_default_media >= 0) {
		int offset = -1;
		int word;
		if (capability & WINBOND_EE) {
			offset = 12;
			word = eeprom_contents[offset] & ~0x0300;
			word |= (new_default_media & 3)<<8;
		} else if (capability & RTL_EE) {
			offset = 0;
			word = eeprom_contents[offset] & ~0x40C0;
			/* Full duplex:0x4000. 10base2:0x00C0  10base5:0x0080*/
			word |= (new_default_media == 0) ? 0x00 : 0xC0;
		} else if (capability & HOLTEK_EE) {
			offset = 3;
			word = eeprom_contents[offset] & ~0x8f00;
			/* 0x0400 Link beat required, 0x0800 polarity correction. */
			word |= (new_default_media == 0) ? 0x0C00 : 0x0E00;
		}
		do_update(capabilities, ioaddr, offset, ee_addr_len,
				  "Transceiver setting",
				  eeprom_contents[offset], word);
	}
#endif

	if (show_eeprom) {
		int eeprom_words = EEPROM_SIZE;		/* Really  2<<ee_addr_len. */
		int sum = 0;

		printf("EEPROM contents (%d words):", eeprom_words);
		for (i = 0; i < eeprom_words; i += 8) {
			int j;
			printf("\n0x%2.2x: ", i);
			for (j = 0; j < 8; j++)
				printf(" %4.4x", eeprom_contents[i + j]);
			if (show_eeprom) {			/* Alt: show_eeprom > 1 */
				printf("  ");
				for (j = 0; j < 8; j++) {
					int ew = eeprom_contents[i + j];
					printf("%c%c",
						   isprint(ew & 0xff) ? ew & 0xff : '_',
						   isprint(ew >>   8) ? ew >> 8   : '_' );
				}
			}
		}
		for (i = 0; i < EEPROM_SIZE; i++)
			sum += eeprom_contents[i];
		printf("\n The word-wide EEPROM checksum is %#4.4x.\n", sum);
	}

	/* The user will usually want to see the interpreted EEPROM contents. */
	if (verbose || show_eeprom) {
		if (capabilities & RTL_EE)
			parse_8029_eeprom(eeprom_contents);
		else if (capabilities & HOLTEK_EE)
			parse_holtek_eeprom(eeprom_contents);
		else if (capabilities & WINBOND_EE)
			parse_winbond_eeprom(eeprom_contents);
	}

	return;
}


/*
 * Local variables:
 *  compile-command: "cc -O -Wall -o ne2k-pci-diag ne2k-pci-diag.c"
 *  c-indent-level: 4
 *  c-basic-offset: 4
 *  tab-width: 4
 * End:
 */
