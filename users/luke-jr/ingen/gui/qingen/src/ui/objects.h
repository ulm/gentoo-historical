#include <qlistview.h>
#include <qlistbox.h>

class LicenseListItem : public QCheckListItem {
//	Q_OBJECT
//	Q_PROPERTY( bool required READ required WRITE setRequired )
public:
	LicenseListItem( QListView * parent, const char * text );

	void setRequired( bool nv ) { requiredV = nv; }
	bool required() const { return requiredV; }

private:
	bool requiredV;
};

class UserListItem : public QListViewItem {
public:
        UserListItem( QListView * parent, QString text, 
		      QString fullname = "");

	void setFullName( QString nv ) { setText(1, nv); }
	QString FullName() const { return text(1); }
        void setPassword( QString nv ) { passwd = nv; }
        QString Password() const { return passwd; }
        void setIconFile( QString nv ) { Vicon = nv; }
        QString IconFile() const { return Vicon; }

private:
        QString passwd, Vicon;
};

