#include <qlistview.h>
#include <qlistbox.h>

#ifndef OBJECTS_H
#define OBJECTS_H

class LicenseListItem : public QCheckListItem {
//	Q_OBJECT
//	Q_PROPERTY( bool required READ required WRITE setRequired )
public:
	LicenseListItem( QListView *parent, const char * text );
	
	void setRequired( bool nv ) { requiredV = nv; }
	bool required() const { return requiredV; }
	int rtti() const { return 1700; }

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
	int rtti() const { return 1701; }

private:
        QString passwd, Vicon;
};

class SoftwareListItem : public QCheckListItem {
public:
	SoftwareListItem(QListView *parent, QString text, QString pkgname);
	SoftwareListItem(QCheckListItem *parent, QString text, QString pkgname);
	
	void setPackage(QString nv) { pkg = nv; }
	QString Package() { return pkg; }
	int rtti() const { return 1702; }
	
private:
	QString pkg;
};

#endif
