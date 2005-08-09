aclocal-1.9 || exit 1
autoheader || exit 1
autoconf || exit 1
automake-1.9 -a -c || exit 1
