// simple program to try to unset a signal mask
// by d_m
//
#include <pthread.h>
#include <signal.h>
#include <stdlib.h>
#include <unistd.h>

#define VERBOSE 0

int main(int argc, char * argv[]) {
  int i, pid, ret_val;
  char str[100];
  sigset_t set, old_set;

  if(VERBOSE) {
    pid = getpid();
    printf("My PID: %d\n", pid);
    sprintf(str, "cat /proc/%d/status | grep SigBlk", pid);
    system(str);
    printf("un-blocking all signals: ");
  }

  sigfillset(&set);
  ret_val = pthread_sigmask(SIG_UNBLOCK, &set, &old_set);

  if(VERBOSE) {
    printf("%d\n", ret_val);
    system(str);
  }

  for(i=1; i<argc; i++) {
    if(VERBOSE) {
      printf("Executing: %s\n", argv[i]);
    }
    system(argv[i]);
  }
  return 0;
}
