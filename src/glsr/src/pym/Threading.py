Config.WaitThreadsTimeout * State.ActiveThreads# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Threading.py,v 1.4 2004/11/10 15:32:44 port001 Exp $
#

__modulename__ = "Threading"

import sys
from time import time
from threading import Thread, Condition

import State
import Config
from Logging import err

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

def wait_threads():

    max_time = int("%0d" % time()) + (Config.WaitThreadsTimeout * State.ActiveThreads)

    while 1:
        if State.ActiveThreads == 0:
            return
        if int("%0d" % time()) >= max_time:
            err("Timed out waiting for %d threads" % State.ActiveThreads,
                                                          __modulename__)
            sys.exit(0)
