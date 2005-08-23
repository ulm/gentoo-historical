AC_DEFUN([AC_DEFINE_DIR], [
	prefix_NONE=
	exec_prefix_NONE=
	test "x$prefix" = xNONE && prefix_NONE=yes && prefix=$ac_default_prefix
	test "x$exec_prefix" = xNONE && exec_prefix_NONE=yes && exec_prefix=$prefix
	eval ac_define_dir="\"[$]$2\""
	AC_SUBST($1, "$ac_define_dir")
	AC_SUBST($2, "$ac_define_dir")
	AC_DEFINE_UNQUOTED($1, "$ac_define_dir", [$3])
	test "$prefix_NONE" && prefix=NONE
	test "$exec_prefix_NONE" && exec_prefix=NONE
])

# http://autoconf-archive.cryp.to/ac_func_mkdir.html
AC_DEFUN([AC_FUNC_MKDIR],
[AC_CHECK_FUNCS([mkdir _mkdir])
AC_CACHE_CHECK([whether mkdir takes one argument],
               [ac_cv_mkdir_takes_one_arg],
[AC_TRY_COMPILE([
#include <sys/stat.h>
#if HAVE_UNISTD_H
#  include <unistd.h>
#endif
], [mkdir (".");],
[ac_cv_mkdir_takes_one_arg=yes], [ac_cv_mkdir_takes_one_arg=no])])
if test x"$ac_cv_mkdir_takes_one_arg" = xyes; then
  AC_DEFINE([MKDIR_TAKES_ONE_ARG], 1,
            [Define if mkdir takes only one argument.])
fi
])
