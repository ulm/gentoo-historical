/* config-map.c: Linux PCI address space map device driver. */
/*
	Copyright Scyld Computing Corporation.
	Written 2000-2003 by Donald Becker.

	This software may be used and distributed according to the terms of
	the GNU General Public License (GPL), incorporated herein by reference.
	Drivers based on or derived from this code fall under the GPL and must
	retain the authorship, copyright and license notice.  This file is not
	a complete program and may only be used when the entire operating
	system is licensed under the GPL.

	The author may be reached as becker@scyld.com, or C/O
	Scyld Computing Corporation
	914 Bay Ridge Road, Suite 220
	Annapolis MD 21403

	This driver allows mapping address regions of PCI devices.
	The available regions are memory regions mapped by the six PCI
	Base Address Registers, along with the PCI BIOS Extension (Boot ROM).

	Support information and updates available at
	http://www.scyld.com/diag.html
*/

/* These identify the driver base version and may not be removed. */
static const char version1[] =
"config-map.c:v1.04 12/28/2002 Written by Donald Becker <becker@scyld.com>\n";
static const char version2[] =
"  http://www.scyld.com/diag/drivers.html\n";

/* The user-configurable values.
   These may be modified when a driver module is loaded.*/

/* Bit-mapped message enable: 1 normal messages, 0 quiet .. 0xffff verbose. */
static int msg_level = 1;

/* Operational parameters that are set at compile time. */

#define IOCTL_CFGM (('C'<<24) + ('F'<<16) + ('G'<<8) + 'M')
#define IOCTL_CONFIG_MAP_PCI_BUSDEVFN (IOCTL_CFGM + 0)
#define IOCTL_CONFIG_MAP_PCI_IOADDR (IOCTL_CFGM + 1)

/* None. */

#ifndef __KERNEL__
#define __KERNEL__
#endif
#if !defined(__OPTIMIZE__)
#warning  You must compile this file with the correct options!
#warning  See the last lines of the source file.
#error You must compile this driver with "-O".
#endif

/* Include files, designed to support most kernel versions 2.0.0 and later. */
#include <linux/config.h>
#if defined(CONFIG_SMP) && ! defined(__SMP__)
#define __SMP__
#endif
#if defined(MODULE) && defined(CONFIG_MODVERSIONS) && ! defined(MODVERSIONS)
#define MODVERSIONS
#endif

#include <linux/version.h>
#if defined(MODVERSIONS)
#include <linux/modversions.h>
#endif
#include <linux/module.h>

#include <linux/kernel.h>
#include <linux/string.h>
#include <linux/pci.h>
#include <linux/miscdevice.h>

#include <asm/io.h>

#if LINUX_VERSION_CODE >= 0x20400
#include <linux/slab.h>
#else
#include <linux/malloc.h>
#endif

#include "kern_compat.h"
#ifndef pci_resource_start
#define pci_resource_start(pci_dev, pci_bar) \
   ((pci_dev)->base_address[(pci_bar)] & PCI_BASE_ADDRESS_MEM_MASK)
#define pci_resource_flags(pci_dev, pci_bar) \
   ((pci_dev)->base_address[(pci_bar)] & 0x0FUL)
#endif

MODULE_AUTHOR("Donald Becker <becker@scyld.com>");
MODULE_DESCRIPTION("PCI configuration space mapper");
MODULE_LICENSE("GPL");
MODULE_PARM(msg_level, "i");
MODULE_PARM_DESC(msg_level, "Message enable bitmap.");

/*
  Internal state structure.
*/

struct config_device {
	int populated;
	struct pci_dev *pci_dev;
	unsigned int pci_bar;				/* BAR number, or 7 for BIOS ROM */
	void *mapped_addr;
};

/*
  Operational functions, ordered by sequence of use:
  open(), ioctl(), mmap(), close() (named release())
*/

static int cfgmap_open(struct inode *ino, struct file *filep)
{
	struct config_device *cfg_dev;

	if (msg_level & 0x0002)
		printk(KERN_DEBUG "config-map: open().\n");

	cfg_dev = kmalloc(sizeof(*cfg_dev), GFP_KERNEL);
	if (! cfg_dev)
		return -ENOMEM;

    MOD_INC_USE_COUNT;
	memset(cfg_dev, 0, sizeof(*cfg_dev));
	filep->private_data = cfg_dev;

	if (msg_level & 0x0002)
		printk(KERN_DEBUG "config-map: open() finished.\n");

    return 0;
}

static int cfgmap_ioctl(struct inode *ino, struct file *filep,
						unsigned int cmd, unsigned long arg)
{
	struct config_device *cfg_dev = filep->private_data;
	u32 *arg_u32 = (void *)arg;

    if ((caddr_t)arg == NULL)
        return -EINVAL;
	if ( ! pcibios_present())
		return -ENODEV;

    switch ( cmd ) {
	case IOCTL_CONFIG_MAP_PCI_BUSDEVFN:
		cfg_dev->pci_dev = pci_find_slot(arg_u32[0], arg_u32[1]);
		if (cfg_dev->pci_dev) {
			cfg_dev->pci_bar = arg_u32[2];
			cfg_dev->populated = 1;
			/* Return the PCI resource info. */
			arg_u32[3] = pci_resource_start(cfg_dev->pci_dev, cfg_dev->pci_bar);
			arg_u32[4] = pci_resource_len(cfg_dev->pci_dev, cfg_dev->pci_bar);
			arg_u32[5] = pci_resource_flags(cfg_dev->pci_dev, cfg_dev->pci_bar);
			return 0;
		}
		return -ENODEV;
	case IOCTL_CONFIG_MAP_PCI_IOADDR:
		/* Search for a PCI device with the specified I/O address. */
		if (msg_level & 0x0002)
			printk(KERN_DEBUG "config-map: ioctl() scanning for I/O "
				   "address %8.8x.\n", arg_u32[0]);
		{
			int bar;
			long ioaddr = arg_u32[0];
			struct pci_dev *pdev;
			if (ioaddr == 0)
				return -ENXIO;
#if LINUX_VERSION_CODE >= 0x20400
			pci_for_each_dev(pdev)
				for (bar = 0; bar < 6; bar++)
					if ((pci_resource_flags(pdev, bar) & PCI_BASE_ADDRESS_SPACE_IO) &&
						pci_resource_start(pdev, bar) == ioaddr) {
						if (msg_level & 0x0002)
							printk(KERN_DEBUG "config-map: found I/O address %8.8x "
								   "at %d:%d.%d.\n", arg_u32[0],
								   pdev->bus->number,
								   PCI_SLOT(pdev->devfn),
								   PCI_FUNC(pdev->devfn));
						arg_u32[0] = pdev->bus->number;
						arg_u32[1] = pdev->devfn;
						return 0;
					}
#else
			for (pdev = pci_devices; pdev; pdev = pdev->next)
				for (bar = 0; bar < 6; bar++)
					if (pdev->base_address[bar] ==
						(ioaddr | PCI_BASE_ADDRESS_SPACE_IO)) {
						/* Return the PCI info. */
						arg_u32[0] = cfg_dev->pci_dev->bus->number;
						arg_u32[1] = cfg_dev->pci_dev->devfn;
						return 0;
					}
#endif
		}
		return -ENODEV;
	}

    return -EINVAL;
}

static int cfgmap_mmap(struct file *filep, struct vm_area_struct *vma)
{
	struct config_device *cfg_dev = filep->private_data;

	long extent = vma->vm_end - vma->vm_start;
#if LINUX_VERSION_CODE >= 0x20400
    off_t                   offset = vma->vm_pgoff << PAGE_SHIFT;
#else
    off_t                   offset = vma->vm_offset;
#endif
	long pciaddr;

	if (msg_level & 0x0002)
		printk(KERN_DEBUG "config-map: Virtual mmap PCI device %d:%d.%d "
			   "register %d.\n",
			   cfg_dev->pci_dev->bus->number,
			   cfg_dev->pci_dev->devfn>>3, cfg_dev->pci_dev->bus->number & 7,
			   cfg_dev->pci_bar);

	if (cfg_dev->pci_bar > 6)
		return -EINVAL;

#if LINUX_VERSION_CODE >= 0x2030C
	pciaddr = cfg_dev->pci_dev->resource[cfg_dev->pci_bar].start;
#else
	if (cfg_dev->pci_bar == 6)
		pciaddr = cfg_dev->pci_dev->rom_address;
	else
		pciaddr = cfg_dev->pci_dev->base_address[cfg_dev->pci_bar]
			& PCI_BASE_ADDRESS_MEM_MASK;
#endif

	if (msg_level & 0x0002)
		printk(KERN_DEBUG "config-map: Virtual mmap physical %8.8lx to VM "
			   "0x%lx - 0x%lx.\n", pciaddr, vma->vm_start, vma->vm_end);

	/* Normally mmap() only insists on offset >= 0.
	   We only permit initial/complete maps.
	   To change, use  virt_addr+offset  below.
	*/
    if (offset != 0)
        return -EINVAL;


#ifdef VM_IO
	/* We do not want the mapped registers bloating a core file. */
	vma->vm_flags |= VM_IO;
#endif

#if defined(USE_IOREMAP)
	virt_addr = ioremap_nocache(pciaddr, extent);
	cfg_dev->mapped_addr = virt_addr;

	printk(KERN_DEBUG "config-map: Initial physical deref of %p is %8.8x.\n",
		   cfg_dev->mapped_addr, ((u32*)(cfg_dev->mapped_addr))[0]);
#endif

#if defined(HAVE_PCI_MMAP)
	{
		/* Last two args: enum pci_mmap_state mmap_state, int write_combine. */
		int retval = pci_mmap_page_range(cfg_dev->pci_dev, vma, 0, 0);
		if (retval)
			return retval;
	}
#endif
	if (remap_page_range(vma->vm_start, pciaddr, extent,
						 vma->vm_page_prot)) {
		printk(KERN_ERR "config-map: mapping address %lx failed.\n",
			   pciaddr);
		return -EAGAIN;			/* Alt: ENOMEM */
	}
	/* Perhaps set vma->vm_inode = ... */

    return 0;
}

static int cfgmap_release(struct inode *ino, struct file *filep)
{
	struct config_device *cfg_dev = filep->private_data;

	if (msg_level & 0x0002) {
		if ( ! cfg_dev)
			printk(KERN_DEBUG "config-map: No configuration local data.\n");
		else if (cfg_dev->pci_dev && cfg_dev->pci_dev->bus) {
			printk(KERN_DEBUG "config-map: release() for PCI %d:%d.%d\n",
				   cfg_dev->pci_dev->bus->number,
				   PCI_SLOT(cfg_dev->pci_dev->devfn),
				   PCI_FUNC(cfg_dev->pci_dev->devfn));
		} else
			printk(KERN_DEBUG "config-map: release() with no PCI device.\n");
	}

#if defined(USE_IOREMAP)
	if (cfg_dev->mapped_addr) {
		printk(KERN_DEBUG "config-map: release() unmapping %p.\n",
			   cfg_dev->mapped_addr);
		iounmap(cfg_dev->mapped_addr);
	}
#endif

	kfree(cfg_dev);

    MOD_DEC_USE_COUNT;
    return 0;
}


static struct file_operations cfgmap_fops = {
    ioctl: cfgmap_ioctl,
    mmap: cfgmap_mmap,
    open: cfgmap_open,
	release: cfgmap_release,
};

static struct miscdevice cfgmap_dev = {
	247,
    "config-map",
    &cfgmap_fops,
    0, 0
};

int init_module(void)
{
	if (msg_level != 0)			/* Always emit driver/version info. */
		printk(KERN_INFO "%s" KERN_INFO "%s", version1, version2);
    if (misc_register(&cfgmap_dev)) {
		printk("config-map: Failed to register misc device.\n");
		return -EAGAIN;
    }

	return 0;
}

void cleanup_module(void)
{
#if 0
	/* No need to check MOD_IN_USE, as sys_delete_module() checks. */
	while (root_cfg_dev) {
		struct cfg_device *next_dev = root_cfg_dev->next_module;

#ifdef USE_IO_OPS
		release_region(root_net_dev->base_addr,
					   pci_id_tbl[np->chip_id].io_size);
#else
		iounmap((char *)(root_net_dev->base_addr));
#endif
		if (root_cfg_dev->priv_addr)
			kfree(root_cfg_dev->priv_addr);
		kfree(root_cfg_dev);
		root_cfg_dev = next_dev;
	}
#endif
	misc_deregister(&cfgmap_dev);
	return;
}


/*
 * Local variables:
 *  compile-command: "gcc -DMODULE -Wall -Wstrict-prototypes -O6 -c config-map.c -I../netdrivers -I/lib/modules/2.4.17-0.18.12.beosmp/build/include/"
 *  c-indent-level: 4
 *  c-basic-offset: 4
 *  tab-width: 4
 * End:
 */
