#include <qapplication.h>
#include "gamelaunch.h"

int main( int argc, char ** argv )
{
    QApplication a( argc, argv );
    dialog w;
    w.show();
    a.connect( &a, SIGNAL( lastWindowClosed() ), &a, SLOT( quit() ) );
    return a.exec();
}
