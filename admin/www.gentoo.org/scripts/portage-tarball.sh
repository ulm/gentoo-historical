#!/bin/bash
umask 022
rm -rf ~/tmp/portage
install -d ~/tmp/portage
cp -ax ~/rsync/* ~/tmp/portage
cd ~/tmp/
tarball=portage-`date +"%Y%m%d"`.tar.bz2
tar cjf $tarball portage
rm -rf ~/tmp/portage
scp $tarball drobbins@login.ibiblio.org:gentoo/snapshots/ || exit 1 
