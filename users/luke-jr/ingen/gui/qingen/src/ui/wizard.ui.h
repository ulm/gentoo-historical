/****************************************************************************
** ui.h extension file, included from the uic-generated form implementation.
**
** If you wish to add, delete or rename functions or slots use
** Qt Designer which will update this file, preserving your code. Create an
** init() function in place of a constructor, and a destroy() function in
** place of a destructor.
*****************************************************************************/

#include "objects.h"
#include "../main.h"
#include <qfile.h>
#include <qmessagebox.h>
#include <qpixmap.h>
#include <qevent.h>

void Wizard::display_license(const char *license) {
    // display selected license
    QFile f("licenses/" + QString(license));
    QTextStream s(&f);
    QString str;
    
    f.open(IO_ReadOnly);
    str  = s.read();
    f.close();
    str.replace('\t', "        ");	//must be done seperately so the spaces are treated
    for (uint pos = 0; pos < str.length(); pos++)
	switch(str[pos].latin1()) {
	case '\n':
	    if(str[pos + 1].latin1() != '\n'
	       && !(str[pos + 1].latin1() == ' '
	       && str[pos + 2].latin1() == ' '
	       && str[pos + 3].latin1() == ' '
	       && str[pos + 4].latin1() == ' '
	       && str[pos + 5].latin1() == ' '
	       && str[pos + 6].latin1() == ' '
	       && str[pos + 7].latin1() == ' '
	       && str[pos + 8].latin1() == ' ')
		//not even possible :)	       && str[pos + 1].latin1() != '\t'
		&& (!pos || str[pos - 1].latin1() != '\n')) {
		    str[pos] = ' ';
		    for (pos++; str[pos].latin1() == ' '; )
			str = str.replace(pos, 1, "");
		    pos--;
		}
	    break;
	case 0x0c:
	    str[pos] = '\n';
	case ' ':
	    if(str[pos + 1].latin1() == ' ')
		str = str.replace(pos, 2, " ");
	}
    txtbLicenseText->setContentsPos(0, 0);
    txtbLicenseText->setText(str);
}

void Wizard::update_tabs() {    // step 1: maybe hide welcome tab
    if(tabsSteps->indexOf(tabWelcome) + 1 && tabsSteps->currentPage() != tabWelcome)
	tabsSteps->removePage(tabWelcome);
    
    // step 2: maybe show/hide tabs after License
    bool reqok = 1;
    QListViewItem *cur;
    
    for (cur = lstLicenses->firstChild(); cur; cur = cur->nextSibling())
	if(cur->text(0).compare("-----") 
	    && ((LicenseListItem *)cur)->required() && !((QCheckListItem *)cur)->isOn())
	    reqok = 0;
    if(!reqok && tabsSteps->indexOf(tabHardDisk) + 1) {
	tabsSteps->removePage(tabHardDisk);
	tabsSteps->removePage(tabSoftware);
	tabsSteps->removePage(tabUsers);
	tabsSteps->removePage(tabInternet);
	tabsSteps->removePage(tabPrinters);
	tabsSteps->removePage(tabTime);
	tabsSteps->removePage(tabStatus);
	tabsSteps->removePage(tabComplete);
    } else if (reqok && tabsSteps->indexOf(tabHardDisk) == -1) {
	tabsSteps->addTab(tabHardDisk, "Hard Disk");
	tabsSteps->addTab(tabSoftware, "Software");
	tabsSteps->addTab(tabUsers, "Users");
	tabsSteps->addTab(tabInternet, "Internet");
	tabsSteps->addTab(tabPrinters, "Printers");
	tabsSteps->addTab(tabTime, "Time");
    }
    
    // step 4: show/hide completion tab and alert user -- must go before step3
    if(InstallStep == -1 && tabsSteps->indexOf(tabComplete) == -1)
	tabsSteps->addTab(tabComplete, "Done");
    else if (InstallStep != -1 && tabsSteps->indexOf(tabComplete) + 1)
	tabsSteps->removePage(tabComplete);
    
    // step 3: show/hide Status based on Hard Disk config completion
    if(tabsSteps->indexOf(tabHardDisk) + 1) {
	if(InstallStep < 1 && tabsSteps->indexOf(tabStatus) + 1) {
	    if(tabsSteps->currentPage() == tabStatus)
		tabsSteps->setCurrentPage(tabsSteps->indexOf(tabComplete));
	    tabsSteps->removePage(tabStatus);
	    if(!InstallStep) pbTotalBg->hide();
	} else if (InstallStep > 0 && tabsSteps->indexOf(tabStatus) == -1) {
	    tabsSteps->addTab(tabStatus, "Status");
	    pbTotalBg->show();
	}
    }

    //TODO: set focus to tab and alert user
    // step 5: enable/disable Back/Next buttons
    cmdBack->setEnabled(tabsSteps->currentPageIndex());
    cmdNext->setEnabled(tabsSteps->currentPageIndex() + 1 != tabsSteps->count());
    
    // step 6: update message on Status page
    QString Step1 = "You have not configured any users. Please go back to the Users step and add at least one user.";
    QString Step2 = "While Gentoo Linux is being installed, you may wish to play some games or browse the internet. When installation is done, you will be notified.";
    if(lvwUsers->childCount() == 0) {
	if(lblStatusInstructions->text().compare(Step1))
	    lblStatusInstructions->setText(Step1);
    } else {
	if(lblStatusInstructions->text().compare(Step2))
	    lblStatusInstructions->setText(Step2);
    }
}

void Wizard::init() {
    LicenseListItem *cur;
    QCheckListItem *cura, *curb, *curc;
    
    lstLicenses->header()->hide();
    lstLicenses->setSorting(-1);	//items are listed in opposite order they are added
    cur = new LicenseListItem(lstLicenses, "DIVX"); cur->setRequired(0);
    cur = new LicenseListItem(lstLicenses, "MOTIF"); cur->setRequired(0);
    new QListViewItem(lstLicenses, "-----");
    cur = new LicenseListItem(lstLicenses, "CRACKLIB"); cur->setRequired(1);
    cur = new LicenseListItem(lstLicenses, "fontconfig"); cur->setRequired(1);
    cur = new LicenseListItem(lstLicenses, "Info-ZIP"); cur->setRequired(1);
    cur = new LicenseListItem(lstLicenses, "PSF-2.2"); cur->setRequired(1);
    cur = new LicenseListItem(lstLicenses, "ZLIB"); cur->setRequired(1);
    cur = new LicenseListItem(lstLicenses, "BZIP2"); cur->setRequired(1);
    cur = new LicenseListItem(lstLicenses, "freedist"); cur->setRequired(1);
    cur = new LicenseListItem(lstLicenses, "OpenSoftware"); cur->setRequired(1);
    cur = new LicenseListItem(lstLicenses, "X11"); cur->setRequired(1);
    cur = new LicenseListItem(lstLicenses, "LGPL-2.1"); cur->setRequired(1);
    cur = new LicenseListItem(lstLicenses, "BSD"); cur->setRequired(1);
    cur = new LicenseListItem(lstLicenses, "MIT"); cur->setRequired(1);
    cur = new LicenseListItem(lstLicenses, "as-is"); cur->setRequired(1);
    cur = new LicenseListItem(lstLicenses, "GPL-2"); cur->setRequired(1);
    
    //TODO: replace w/ partition detection stuff
    sldHDOldResize_valueChanged( sldHDOldResize->value() );
    optHDMulti->setChecked(TRUE);
    pbTotalBg->hide();
    
    lvwSoftwareComponents->header()->hide();
    lvwSoftwareComponents->setSorting(-1);
#define SECTION(name) \
    curc = cura = new QCheckListItem(lvwSoftwareComponents, name ,	\
			       QCheckListItem::CheckBox);
#define ITEM(name)	\
    curc = new QCheckListItem(cura, name , QCheckListItem::CheckBox);
#define SUBSECTION(name) \
    curc = curb = new QCheckListItem(cura, name , QCheckListItem::CheckBox);
#define SUBITEM(name) \
    curc = new QCheckListItem(curb, name , QCheckListItem::CheckBox);
#define DEFAULT	curc->setOn(TRUE);
    SECTION("Accessories")
	    ITEM("Calculator")				DEFAULT
	    ITEM("Desktop Wallpaper")			DEFAULT
	    ITEM("Screen Savers")			DEFAULT
	    ITEM("KWord")
	    SECTION("Games")
	    //    curb = new QCheckListItem(cur, "Arcade");
	    ITEM("Armagetron")
	    ITEM("KAsteroids")
	    ITEM("KBounce")
	    ITEM("KSnakeRace")
	    ITEM("KMines")
	    ITEM("Frozen Bubble")
	    SECTION("Desktop Themes")
	    ITEM("Keramik")
	    ITEM("MGBreizh")
	    ITEM("Nostalgy")
	    ITEM("Wood")
	    SECTION("Multimedia")
	    ITEM("XMMS (Audio Player)")			DEFAULT
	    ITEM("Xine (Video Player)")			DEFAULT
	    ITEM("CD Player")						//KsCD
	    ITEM("Sound Recorder")					//KRec
	    ITEM("Volume Control")			DEFAULT	//KMix
	    ITEM("K3b (CD Burner)")
	    SUBSECTION("Video Compression")		DEFAULT
	    SUBITEM("Quicktime")				DEFAULT
	    SUBITEM("RealMedia")			DEFAULT
	    SUBITEM("DivX")				DEFAULT
	    SUBITEM("Other Codecs")			DEFAULT
	    SECTION("System Tools")
	    ITEM("Character Selector")					//KCharSelect
	    ITEM("KDE System Guard")			DEFAULT
	    ITEM("Network Monitor")					//KNetLoad
	    SUBSECTION("Admin Tools")
	    SUBITEM("Task Scheduler")					//KCron
	    SUBITEM("User Manager")					//KUser
	    SECTION("Internet")
	    ITEM("Instant Messaging")			DEFAULT       //Kopete or Gaim
	    ITEM("Advanced Downloader")				//KGet?
	    ITEM("IRC Client")						//ksirc/KVirc?
	    ITEM("EMail")					DEFAULT	//KMail
	    ITEM("Newsgroups")						//KNode
	    ITEM("Remote Desktop")			DEFAULT	//Krdc
#undef DEFAULT
#undef SUBITEM
#undef SUBSECTION
#undef ITEM
#undef SECTION
	    
    cmbInternetISPType->setCurrentItem(4);	cmbInternetISPType_activated("Custom");
    cmbInternetISPName->setCurrentItem(1); cmbInternetISPName_activated("DHCP");
    
    pixWelcome->setPixmap(QPixmap("images/op-side.png"));
    pixComplete->setPixmap(QPixmap("images/ed-side.png"));
    
    pixLicenseIcon->setPixmap(QPixmap("images/license-icon.png"));
    pixHardDiskIcon->setPixmap(QPixmap("images/harddisk-icon.png"));
    pixSoftwareIcon->setPixmap(QPixmap("images/software-icon.png"));
    pixUsersIcon->setPixmap(QPixmap("images/users-icon.png"));
    pixInternetIcon->setPixmap(QPixmap("images/internet-icon.png"));
    pixPrintersIcon->setPixmap(QPixmap("images/printers-icon.png"));
    pixTimeIcon->setPixmap(QPixmap("images/time-icon.png"));
    pixStatusIcon->setPixmap(QPixmap("images/status-icon.png"));
}

void Wizard::lstLicenses_clicked( QListViewItem *selected ) {
    update_tabs();
    display_license(selected->text(0));
}

void Wizard::cmdBack_clicked()
{
    update_tabs();
    tabsSteps->showPage(tabsSteps->page(tabsSteps->currentPageIndex() - 1));
}

void Wizard::cmdNext_clicked() {
    //TODO: if HD config has changed, possibly override the '!InstallStep'
    if(tabsSteps->currentPage() == tabHardDisk && !InstallStep)
	if(apply_harddisk(TRUE))
	    return;	//cancelled
    update_tabs();
    tabsSteps->showPage(tabsSteps->page(tabsSteps->currentPageIndex() + 1));
}


void Wizard::tabsSteps_currentChanged( QWidget * ) {
    update_tabs();
}

bool Wizard::apply_harddisk(bool hascancel) {	// returns true if Cancel is selected
    int applyconfirm;
    if(InstallStep)
	applyconfirm = QMessageBox::warning(0, caption(), "<DIV ALIGN=justify>You have already applied hard disk settings before. If you apply them again, the install process will start over.<BR><BR></DIV><CENTER>Apply new settings?</CENTER>", QMessageBox::Yes, QMessageBox::No, hascancel ? QMessageBox::Cancel : QMessageBox::NoButton);
    else
	applyconfirm = QMessageBox::warning(0, caption(), "<DIV ALIGN=justify>Once you apply settings, you cannot cancel or stop the install. You can apply the hard disk settings after you are done configuring everything if you want, but if you apply them now the install will start while you complete the rest.<BR><BR></DIV><CENTER>Do you want to apply the hard disk settings now and start the install? (recommended)</CENTER>", QMessageBox::Yes, QMessageBox::No, hascancel ? QMessageBox::Cancel : QMessageBox::NoButton);
    if(applyconfirm == QMessageBox::Cancel)
	return TRUE;
    if(applyconfirm == QMessageBox::No)
	return FALSE;
    if(optHDClean->isOn()) {
	// TODO: don't ask if partition table is invalid/clear/previous-HDClean-applied-already
	applyconfirm = QMessageBox::warning(0, caption(), "<DIV ALIGN=justify>You have chosen to install a Gentoo Linux PC Only. This will erase any previous operating system such as Microsoft Windows, and also any data on your system.<BR><BR></DIV><CENTER>Are you sure you want to do this?</CENTER>", QMessageBox::Yes, QMessageBox::No, hascancel ? QMessageBox::Cancel : QMessageBox::NoButton);
	if(applyconfirm == QMessageBox::Cancel)
	    return TRUE;
	if(applyconfirm == QMessageBox::No)
	    return FALSE;
    }
    begin_install();
    update_tabs();
    return FALSE;
}

void Wizard::cmdHarddiskApply_clicked() {
    apply_harddisk(FALSE);
}

void Wizard::sldHDOldResize_valueChanged( int nv ) {
    lblOldOSSpace->setText(QString::number(nv) + " GB");
    lblNewOSSpace->setText(QString::number(100 - nv) + " GB");
}


void Wizard::ckgPartitionMode_clicked( int ) {
    fraHDMulti->setEnabled(optHDMulti->isChecked());
}

void Wizard::lvwSoftwareComponents_clicked( QListViewItem *p ) {
    if(!p) return;
    
    QListViewItem *tmp;
    QCheckListItem *cur = (QCheckListItem *)p;
    bool ps = cur->isOn();
    
    for (tmp = p->firstChild(); tmp; tmp = tmp->nextSibling()) {
	cur = (QCheckListItem *)tmp;
	cur->setOn(ps);
	lvwSoftwareComponents_clicked(cur);
    }
}

void Wizard::cmdUserAdd_clicked() {
    if (txtUserPassA->text().compare(txtUserPassB->text())) {
	QMessageBox::critical(0, caption(), "<DIV ALIGN=justify>The password fields are not the same. Please try entering them again.</DIV>", QMessageBox::Ok, QMessageBox::NoButton);
	return;
    }
    for(QListViewItem *cur = lvwUsers->firstChild(); cur; cur = cur->nextSibling())
	if(!cur->text(0).compare(txtUserName->text())) {
	    QMessageBox::critical(0, caption(), "<DIV ALIGN=justify>A user with that name already exists!</DIV>", QMessageBox::Ok, QMessageBox::NoButton);
	    return;
	}
    
    // TODO: check to make sure password is secure
    
    UserListItem *n = new UserListItem(lvwUsers, txtUserName->text());
    n->setFullName(txtUserFullname->text());
    n->setPassword(txtUserPassA->text());
    n->setIconFile(lblUserIconFile->text());
    
    txtUserName->setText("");
    txtUserFullname->setText("");
    txtUserPassA->setText("");
    txtUserPassB->setText("");
    lblUserIconFile->setText("");
}

void Wizard::checkUserButtons() {
    cmdUserEdit->setEnabled(lvwUsers->selectedItem());
    cmdUserDel->setEnabled(lvwUsers->selectedItem());
}

void Wizard::cmdUserEdit_clicked() {
    UserListItem *toedit = (UserListItem *)lvwUsers->selectedItem();
    if(!toedit) return;
    
    txtUserName->setText(toedit->text(0));
    txtUserFullname->setText(toedit->FullName());
    txtUserPassA->setText(toedit->Password());
    txtUserPassB->setText(toedit->Password());
    lblUserIconFile->setText(toedit->IconFile());
    //TODO: load/display icon
    lvwUsers->takeItem(toedit);
    delete toedit;
    checkUserButtons();
}

void Wizard::cmdUserDel_clicked() {
    QListViewItem *torm = lvwUsers->selectedItem();
    if(!torm) return;
    
    lvwUsers->takeItem(torm);
    delete torm;
    checkUserButtons();
}

void Wizard::lvwUsers_clicked( QListViewItem * ) {
    checkUserButtons();
}

void Wizard::cmbInternetISPType_activated( const QString &s )
{
    if(s.compare("Custom")) {
	cmbInternetISPCountry->setEnabled(TRUE);
	cmbInternetISPName->clear();    
    } else {
	cmbInternetISPCountry->setEnabled(FALSE);	
	cmbInternetISPName->clear();
	cmbInternetISPName->insertItem("PPP (Normal Dialup)");
	cmbInternetISPName->insertItem("DHCP (Broadband/Ethernet)");
	cmbInternetISPName->insertItem("PPPoE (Usually DSL)");
	cmbInternetISPName->insertItem("RAS");
	cmbInternetISPName->insertItem("PPTP");
	cmbInternetISPName->insertItem("Static IP");
    }
}

void Wizard::cmbInternetISPName_activated( const QString &s ) {
    wgsCustomISP->raiseWidget((s.find("PPPoE") + 1) ? pagePPPoE : (
	    (s.find("DHCP") + 1) ? pageDHCP : (
		    (s.find("PPP") + 1) ? pagePPP : (
			    (s.find("RAS") + 1) ? pageRAS : (
				    (s.find("PPTP") + 1) ? pagePPTP :
					    pageStaticIP)))));
}

void Wizard::chkNetPPPSavePass_toggled( bool nv ) {
    txtNetPPPPassA->setEnabled(nv);
    txtNetPPPPassB->setEnabled(nv);
}

void Wizard::chkNetPPPoESavePass_toggled( bool nv ) {
    txtNetPPPoEPassA->setEnabled(nv);
    txtNetPPPoEPassB->setEnabled(nv);
}

void Wizard::chkNetRASSavePass_toggled( bool nv ) {
    txtNetRASPassA->setEnabled(nv);
    txtNetRASPassB->setEnabled(nv);
}

void Wizard::chkNetPPTPSavePass_toggled( bool nv ) {
    txtNetPPTPPassA->setEnabled(nv);
    txtNetPPTPPassB->setEnabled(nv);
}

void Wizard::cmdNetStaticDNSAdd_clicked() {
    lstNetStaticDNS->insertItem(txtNetStaticDNS->text());
    txtNetStaticDNS->setText("");
}

void Wizard::cmdNetStaticDNSDel_clicked() {
    if(lstNetStaticDNS->selectedItem())
	delete lstNetStaticDNS->selectedItem();
    lstNetStaticDNS_selectionChanged(lstNetStaticDNS->selectedItem());
}

void Wizard::cmdNetStaticDNSUp_clicked() {
    QListBoxItem *se = lstNetStaticDNS->selectedItem();
    if(!se)	return;
    int newpos = lstNetStaticDNS->index(se) - 1;
    lstNetStaticDNS->setSelected(se, FALSE);
    lstNetStaticDNS->takeItem(se);
    lstNetStaticDNS->insertItem(se, newpos);
    lstNetStaticDNS->setSelected(se, TRUE);    
}

void Wizard::cmdNetStaticDNSDown_clicked() {
    QListBoxItem *se = lstNetStaticDNS->selectedItem();
    if(!se)	return;
    int newpos = lstNetStaticDNS->index(se) + 1;
    lstNetStaticDNS->setSelected(se, FALSE);
    lstNetStaticDNS->takeItem(se);
    lstNetStaticDNS->insertItem(se, newpos);    
    lstNetStaticDNS->setSelected(se, TRUE);
}

void Wizard::lstNetStaticDNS_selectionChanged( QListBoxItem *sel ) {
    if(!sel) {
	cmdNetStaticDNSUp->setEnabled(FALSE);	
	cmdNetStaticDNSDown->setEnabled(FALSE);
	return;
    }
    cmdNetStaticDNSUp->setEnabled(lstNetStaticDNS->index(sel));
    cmdNetStaticDNSDown->setEnabled
	    (lstNetStaticDNS->index(sel) + 1 != (int)lstNetStaticDNS->count());
}


void Wizard::pushButton16_clicked()
{
    InstallStep = -1;
    update_tabs();
}

bool Wizard::do_cancel() {
    if(InstallStep)
	if(QMessageBox::warning(0, caption(), "<DIV ALIGN=justify>You have already started the installation process. If you cancel, your computer <B>probably</B> won't work anymore.<BR><BR></DIV><CENTER>Cancel anyway?</CENTER>", QMessageBox::Yes, QMessageBox::No) == QMessageBox::No)
	    return FALSE;
    return TRUE;
}

void Wizard::cmdCancel_clicked() {
    if(do_cancel()) {
	cancel_install();
	this->close();
    }
}

void Wizard::closeEvent(QCloseEvent *e) {
    if(!do_cancel())
	return e->ignore();
    e->accept();
}


}
