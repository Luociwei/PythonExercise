# -*- coding: utf-8 -*-
from ..tracer.recorder import *
from gpio import GPIODef


class GPIOEmulator(object):
    '''
    GPIO function class

    :param pin_name:    str   pin name

    :example:       io = GPIO('mio')
    '''
    def __init__(self, pin_name='mio'):
        self.pin_name = pin_name

        self._recorder = Recorder()
        add_recorder(self._recorder)

        self._recorder.record(self.pin_name + "." + "__init__()")

    def get_level(self):
        '''
        GPIO get pin level

        :return:    type is int
        :example:   level = io.get_level()
                    print(level)
        '''
        self._recorder.record(self.pin_name + "." + "get_level()")
        return 0

    def set_level(self, level):
        '''
        GPIO set pin level

        :param level:   int(0)    1 is high level, 0 is low level
        :example:       io.set_level(1)
        '''
        assert level in [GPIODef.LOW_LEVEL, GPIODef.HIGH_LEVEL]
        self._recorder.record(self.pin_name + "." + "set_level(%s)" % level)

    def get_dir(self):
        '''
        GPIO get pin direction

        :return:    type is string
        :example:   dir = io.get_dir()
                    print(dir)
        '''
        self._recorder.record(self.pin_name + "." + "get_dir()")
        return GPIODef.OUTPUT

    def set_dir(self, pin_dir):
        '''
        GPIO set pin direction

        :param pin_dir:     string("input"|"output")    Set the io direction
        :example:           io.set_dir('input')
        '''
        assert pin_dir in [GPIODef.INPUT, GPIODef.OUTPUT]
        self._recorder.record(self.pin_name + "." + "set_dir(%s)" % pin_dir)
