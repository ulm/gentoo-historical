/****************************************************************************
** ui.h extension file, included from the uic-generated form implementation.
**
** If you wish to add, delete or rename functions or slots use
** Qt Designer which will update this file, preserving your code. Create an
** init() function in place of a constructor, and a destroy() function in
** place of a destructor.
*****************************************************************************/

#include <unistd.h>

void dialog::launchGame()
{
    
    hide();
    chdir("/opt/armyops170/System");
    system("./armyops-bin");
    show();
}



void dialog::restartCD()
{
    hide();
    system("/sbin/reboot -ndfi");
    exit(0);
}


void dialog::launchBrowser()
{
    hide();
    system("/usr/bin/mozilla http://www.americasarmy.com");
    show();
}
