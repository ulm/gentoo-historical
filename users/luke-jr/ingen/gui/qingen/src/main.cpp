#include <qapplication.h>
#include "ui/wizard.h"
#include "main.h"

int InstallStep = 0;

int main( int argc, char ** argv ) {
    QApplication a( argc, argv );
    Wizard * mw = new Wizard();
    mw->show();
    a.connect( &a, SIGNAL(lastWindowClosed()), &a, SLOT(quit()) );
    return a.exec();
}

void begin_install() {
    InstallStep = 1;
}

void cancel_install() {
    InstallStep = 0;
}

