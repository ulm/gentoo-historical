# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Threading.py,v 1.2 2004/11/09 18:01:20 port001 Exp $
#

__modulename__ = "Threading"

from threading import Thread, Condition

class Threader:
    """ A class for running functions in seperate threads.
        Based on the work by David Perry (Python Cookbook). 

        Scott: Don't use this yet, I need to return values
        to a "state" module. """

    def __init__(self, func, *args):

        self._retval = None

        self._condition = Condition()
        self._thread = Thread(target=self._wrapper, args=(func, args))

        self._run_thread()

    def _run_thread(self):

        self._thread.setName("GLSR Thread")
        self._thread.start()

    def _wrapper(self, func, args):

        self._condition.acquire()
        self._retval = func(*args)
        self._condition.notify()
        self._condition.release()
