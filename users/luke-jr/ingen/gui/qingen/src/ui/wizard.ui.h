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
#include <qlistbox.h>

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
		tabsSteps->removePage(tabStatus);
		tabsSteps->removePage(tabComplete);
	} else if (reqok && tabsSteps->indexOf(tabHardDisk) == -1) {
		tabsSteps->addTab(tabHardDisk, "Hard Disk");
		tabsSteps->addTab(tabSoftware, "Software");
		tabsSteps->addTab(tabUsers, "Users");
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
#define ITEM(name)	\
	cur = new LicenseListItem(lstLicenses, name); cur->setRequired(FALSE);
#define REQUIRED cur->setRequired(TRUE);
#define DEFAULT	cur->setOn(TRUE);
#define SEPERATOR(name) new QListViewItem(lstLicenses, name);
	//Nvidia?? "Gentoo has detected that your computer has an nVidia video card. 3D applications may be slow unless you install an accelerated driver from nVidia. Do you wish to do this now?"
	//Include Flash??
	ITEM("DIVX")
	ITEM("MOTIF")			// Is this really required since KDE's MOTIF using is compile-time?
	SEPERATOR("  --- Optional ---")
	ITEM("CRACKLIB")	REQUIRED	DEFAULT
	ITEM("fontconfig")	REQUIRED	DEFAULT
	ITEM("Info-ZIP")	REQUIRED	DEFAULT
	ITEM("PSF-2.2")		REQUIRED	DEFAULT
	ITEM("ZLIB")		REQUIRED	DEFAULT
	ITEM("BZIP2")		REQUIRED	DEFAULT
	ITEM("freedist")	REQUIRED	DEFAULT
	ITEM("OpenSoftware")REQUIRED	DEFAULT
	ITEM("X11")			REQUIRED	DEFAULT
	ITEM("LGPL-2.1")	REQUIRED	DEFAULT
	ITEM("BSD")			REQUIRED	DEFAULT
	ITEM("MIT")			REQUIRED	DEFAULT
	ITEM("as-is")		REQUIRED	DEFAULT
	ITEM("GPL-2")		REQUIRED	DEFAULT
	SEPERATOR("  --- Required ---")
#undef ITEM
#undef REQUIRED
#undef DEFAULT
#undef SEPERATOR
	
	//TODO: replace w/ partition detection stuff
	sldHDOldResize_valueChanged( sldHDOldResize->value() );
	optHDMulti->setChecked(TRUE);
	pbTotalBg->hide();
	
	lvwSoftwareComponents->header()->hide();
	lvwSoftwareComponents->setSorting(-1);
#define SECTION(name) \
	curc = cura = new QCheckListItem(lvwSoftwareComponents, name ,	\
									 QCheckListItem::CheckBoxController);
#define ITEM(name)	\
	curc = new QCheckListItem(cura, name , QCheckListItem::CheckBox);	\
    cura->setState(QCheckListItem::NoChange);
#define SUBSECTION(name) \
	curc = curb = new QCheckListItem(cura, name , QCheckListItem::CheckBoxController);
#define SUBITEM(name) \
	curc = new QCheckListItem(curb, name , QCheckListItem::CheckBox);
#define DEFAULT	curc->setOn(TRUE);
	
	SECTION("Accessories")
			ITEM("Common Utilities")			DEFAULT
	SECTION("Games")
			ITEM("Common Games")				DEFAULT
			ITEM("ArmageTRON")					DEFAULT
			ITEM("Frozen Bubble")				DEFAULT
	SECTION("Desktop Themes")
			ITEM("Common Themes")				DEFAULT
			ITEM("Liquid")
	SECTION("Multimedia")
			ITEM("Common Multimedia")			DEFAULT
			ITEM("CD Burner")
			ITEM("Multimedia Player")			DEFAULT		//VLC?
			SUBSECTION("Video Compression")
			    SUBITEM("Quicktime")			DEFAULT
			    SUBITEM("RealMedia")			DEFAULT
			    SUBITEM("DivX")					DEFAULT
		    	SUBITEM("Other Codecs")			DEFAULT
	SECTION("System Tools")
			ITEM("Common Administration Tools")	DEFAULT
			ITEM("Windows Compatibility")		DEFAULT
			ITEM("Partition Manipulator")				//QtParted
	SECTION("Internet")
			ITEM("Instant Messenger")			DEFAULT		//Psi
			ITEM("Advanced Downloader")					//KGet?
			ITEM("IRC Client")						//ksirc/KVirc?
	SECTION("Office Suite")
			
#undef DEFAULT
#undef SUBITEM
#undef SUBSECTION
#undef ITEM
#undef SECTION
	
			
	/*	cmdBack->setIconSet(QPixmap("images/back.png"));
	cmdNext->setIconSet(QPixmap("images/next.png")); */
			
	pixWelcome->setPixmap(QPixmap("images/op-side.png"));
	pixComplete->setPixmap(QPixmap("images/ed-side.png"));
	
	pixLicenseIcon->setPixmap(QPixmap("images/license-icon.png"));
	pixHardDiskIcon->setPixmap(QPixmap("images/harddisk-icon.png"));
	pixSoftwareIcon->setPixmap(QPixmap("images/software-icon.png"));
	pixUsersIcon->setPixmap(QPixmap("images/users-icon.png"));
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
		applyconfirm = QMessageBox::warning(0, caption(), "<p ALIGN=justify>You have already applied hard disk settings before. If you apply them again, the install process will start over.</p><BR><CENTER>Apply new settings?</CENTER>", QMessageBox::Yes, QMessageBox::No, hascancel ? QMessageBox::Cancel : QMessageBox::NoButton);
	else
		applyconfirm = QMessageBox::warning(0, caption(), "<p ALIGN=justify>Once you apply settings, you cannot cancel or stop the install. You can apply the hard disk settings after you are done configuring everything if you want, but if you apply them now the install will start while you complete the rest.</p><BR><CENTER>Do you want to apply the hard disk settings now and start the install? (recommended)</CENTER>", QMessageBox::Yes, QMessageBox::No, hascancel ? QMessageBox::Cancel : QMessageBox::NoButton);
	if(applyconfirm == QMessageBox::Cancel)
		return TRUE;
	if(applyconfirm == QMessageBox::No)
		return FALSE;
	if(InstallStep) cancel_install();
	if(optHDClean->isOn()) {
		// TODO: don't ask if partition table is invalid/clear/previous-HDClean-applied-already
		applyconfirm = QMessageBox::warning(0, caption(), "<p ALIGN=justify>You have chosen to install a Gentoo Linux PC Only. This will erase any previous operating system such as Microsoft Windows, and also any data on your system.</p><BR><CENTER>Are you sure you want to do this?</CENTER>", QMessageBox::Yes, QMessageBox::No, hascancel ? QMessageBox::Cancel : QMessageBox::NoButton);
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
		QMessageBox::critical(0, caption(), "<p ALIGN=justify>The password fields are not the same. Please try entering them again.</p>", QMessageBox::Ok, QMessageBox::NoButton);
		return;
	}
	for(QListViewItem *cur = lvwUsers->firstChild(); cur; cur = cur->nextSibling())
		if(!cur->text(0).compare(txtUserName->text())) {
		QMessageBox::critical(0, caption(), "<p ALIGN=justify>A user with that name already exists!</p>", QMessageBox::Ok, QMessageBox::NoButton);
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

void Wizard::pushButton16_clicked()
{
	InstallStep = -1;
	update_tabs();
}

bool Wizard::do_cancel() {
	if(InstallStep)
		if(QMessageBox::warning(0, caption(), "<p align=\"justify\">You have already started the installation process. If you cancel, your computer <b>probably</b> won't work anymore.</p><BR><CENTER>Cancel anyway?</CENTER>", QMessageBox::Yes, QMessageBox::No) == QMessageBox::No)
			return FALSE;
	cancel_install();
	this->close();
	return TRUE;
}

void Wizard::cmdCancel_clicked() {
	do_cancel();
}

void Wizard::closeEvent(QCloseEvent *e) {
	if(!do_cancel())
		return e->ignore();
	e->accept();
}


void Wizard::InGenReport() {

}


void Wizard::doStatus() {
	// TODO: Weigh each part differently?
	int ResizeStep = 0;
	int FormatStep = 0;
	int InstallStep = (int) ((long long) 255 *
									  filesystem_use("/mnt/gentoo") / SrcUsedSpace);
	int BootDiskStep = 0;
	int TotalStep = (ResizeStep + FormatStep + InstallStep + BootDiskStep) / 4;
	
	pbStatResize->setProgress(ResizeStep);
	pbStatFormat->setProgress(FormatStep);
	pbStatInstall->setProgress(InstallStep);
	pbStatBootdisk->setProgress(BootDiskStep);
	pbStatTotal->setProgress(TotalStep);
	pbTotalBg->setProgress(TotalStep);
}
