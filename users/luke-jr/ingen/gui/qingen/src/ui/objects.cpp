#include "objects.h"
#include <qlistview.h>

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


