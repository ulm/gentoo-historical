#include <qapplication.h>
#include <qprocess.h>
#include <qtimer.h>
#include <sys/statfs.h>
#include "ui/wizard.h"
#include "main.h"

int InstallStep = 0;
QApplication *QInGenApp;
Wizard *QInGenWizard;
QProcess *InGenProc;
long long SrcUsedSpace;
QTimer *UpdateStatus;
QString InGenStdout;

int main( int argc, char ** argv ) {
	QInGenApp = new QApplication(argc, argv);
    QInGenWizard = new Wizard();
    QInGenWizard->show();
    QInGenApp->connect(QInGenApp, SIGNAL(lastWindowClosed()), QInGenApp, SLOT(quit()) );
    return QInGenApp->exec();
}

long long filesystem_use(const char *mountpt) {
	struct statfs buf;

	if (statfs(mountpt, &buf) == -1) {
		printf("Couldn't get used disk space! :(\n");
		return -1;	// Error
	}
	return (long long) (buf.f_blocks - buf.f_bfree) * (long long) buf.f_bsize;
}

void begin_install() {
	InGenProc = new QProcess(QInGenApp);
	InGenProc->addArgument("ingen");
	InGenProc->addArgument("LaunchInGen");
	InGenProc->connect(InGenProc, SIGNAL(readyReadStdout()), QInGenWizard, SLOT(InGenReport()));
	InGenStdout = QString::null;
	if (!InGenProc->start()) {
		// TODO: What happens if this fails? o.o;;;
		printf("InGen failed to start! :(\n");
	}
	SrcUsedSpace = filesystem_use("/");
	UpdateStatus = new QTimer;
	UpdateStatus->connect(UpdateStatus, SIGNAL(timeout()), QInGenWizard, SLOT(doStatus()));
	UpdateStatus->start(10000);
    InstallStep = 1;
}

void cancel_install() {
	if (InGenProc->isRunning())
		InGenProc->kill();
    InstallStep = 0;
}

