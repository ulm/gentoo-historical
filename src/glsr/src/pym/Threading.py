# Copyright 2004-2005 Ian Leitch
# Copyright 2004-2005 Scott Hadfield
# Copyright 1999-2005 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = '$Id: Threading.py,v 1.6 2005/01/27 04:19:15 port001 Exp $'
__modulename__ = 'Threading'

from time import time
from threading import Thread, Condition

import State
import Config

class Threader:
    """ A class for running functions in seperate threads.
        Based on the work by David Perry (Python Cookbook). 

        Scott: Don't use this yet, I need to return values
        to a "state" module. """

    def __init__(self, func, *args):

        self._retval = None

        self._condition = Condition()
        self._thread = Thread(target=self._wrapper, args=(func, args))

        State.ActiveThreads += 1

        self._run_thread()

    def _run_thread(self):

        self._thread.setName("GLSR Thread")
        self._thread.start()

    def _wrapper(self, func, args):

        self._condition.acquire()
        self._retval = func(*args)
        self._condition.notify()
        self._condition.release()
        State.ActiveThreads -= 1
