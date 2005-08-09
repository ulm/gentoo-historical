noinst_LIBRARIES = libcommon.a

libcommon_a_SOURCES = hash.c install_conf.c profile.c selection_conf.c

libexecdir = @prefix@/libexec/gcc-config

libexec_PROGRAMS = gcc-wrapper
gcc_wrapper_SOURCES = wrapper.c
gcc_wrapper_LDADD = libcommon.a
