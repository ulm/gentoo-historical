#ifndef MAIN_H
#define MAIN_H

#include <qstring.h>
#include <qprocess.h>

extern int InstallStep;
extern long long SrcUsedSpace;
extern QString InGenStdout;
extern QProcess *InGenProc;

extern long long filesystem_use(const char *mountpt);

extern void begin_install();
extern void cancel_install();

#endif
