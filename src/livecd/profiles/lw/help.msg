Gentoo Linux 1.4 LiveCD boot options - [F1 to redisplay boot graphic]
At the prompt type "gentoo option" or "smp option"
or just hit enter if no options are needed.
Press F3 for additional kernel labels

doscsi        scan for scsi devices (breaks some ethernet cards)
nodetect      causes hwsetup/kudzu and hotplug not to run
dofirewire    modprobes firewire modules in initrd (for firewire cdroms,etc)
nousb         disables usb module load from initrd, disables hotplug
nodhcp        dhcp does not automatically start if nic detected
doataraid     loads ide raid modules from initrd
dopcmcia      starts pcmcia service
noapm         disables apm module load
noraid        disables loading of evms modules
nohotplug     disables loading hotplug service
ide=nodma     Force disabling of dma for malfunctioning ide devices
cdcache       Cache the entire runtime portion of cd in ram, This
              uses 40mb of RAM , but allows you to umount /mnt/cdrom
              and mount another cdrom.
noraid        disables autoloading of evms modules
dokeymap      enable keymap selection for non-us keyboard layouts
