#ifndef MAIN_H
#define MAIN_H

extern int InstallStep;
extern long long SrcUsedSpace;

extern long long filesystem_use(const char *mountpt);

extern void begin_install();
extern void cancel_install();

#endif
