# -*- coding: UTF-8 -*-
from mix.driver.core.tracer.recorder import *

__author__ = 'liliang@SmartGiant'
__version__ = '0.1'


class TMP10xEmulator(object):

    def __init__(self):
        self._reg = dict()
        self._recorder = Recorder()
        add_recorder(self._recorder)

    def get_temperature(self):
        self._recorder.record("get temperature")


class TMP108Emulator(TMP10xEmulator):
    pass
