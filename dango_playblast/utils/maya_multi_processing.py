#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading

try:
    from maya.utils import executeInMainThreadWithResult
except ImportError:
    executeInMainThreadWithResult = None


class Timer(threading.Thread):
    def __init__(self, interval, function, args=[], kwargs={}, repeat=True):
        self.interval = interval
        self.function = function
        self.repeat = repeat
        self.args = args
        self.kwargs = kwargs
        self.event = threading.Event()
        threading.Thread.__init__(self)

    def run(self):
        def _mainLoop():
            self.event.wait(self.interval)
            if not self.event.isSet():
                if executeInMainThreadWithResult:
                    executeInMainThreadWithResult(self.function, *self.args, **self.kwargs)
                else:
                    self.function(*self.args, **self.kwargs)

        if self.repeat:
            while not self.event.isSet():
                _mainLoop()
        else:
            _mainLoop()
            self.stop()

    def start(self):
        self.event.clear()
        threading.Thread.start(self)

    def stop(self):
        self.event.set()
        threading.Thread.__init__(self)
