#! /usr/bin/env python2.2
# $Header: /var/cvsroot/gentoo/src/kernel/config-kernel/setup.py,v 1.1 2004/03/16 03:52:52 latexer Exp $

__version__ = '$Revision: 1.1 $'

from distutils.core import setup
import os
import config_kernel

setup (

name = 'config-kernel',
version = config_kernel.version,
description = 'kernel enviroment configuration tool',
long_description = \
"""
config-kernel is a tool for configuring various enviroment
variables, symlinks, and files involved in the kernel
enviroment for Gentoo Linux.
""",
author = 'Peter Johanson',
author_email = 'latexer@gentoo.org',
packages = ['', 'config_kernel'],
package_dir = { '' : os.curdir, 'config_kernel' : os.curdir + '/config_kernel' }

)
