#include <qlistview.h>
#include "objects.h"

LicenseListItem::LicenseListItem( QListView *parent, const char *text)
        : QCheckListItem(parent, text, QCheckListItem::CheckBox)
{	
    requiredV = FALSE;
}

UserListItem::UserListItem( QListView *parent, QString text,
			    QString fullname)
        : QListViewItem(parent, text, fullname)
{
	passwd = Vicon = "";
}

SoftwareListItem::SoftwareListItem(QListView *parent, QString text, QString pkgname)
	: QCheckListItem(parent, text, QCheckListItem::CheckBox)
{
	pkg = pkgname;
}

SoftwareListItem::SoftwareListItem(QCheckListItem *parent, QString text, QString pkgname)
	: QCheckListItem(parent, text, QCheckListItem::CheckBox)
{
	pkg = pkgname;
}
