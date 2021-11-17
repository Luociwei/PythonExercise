# -*- coding: utf-8 -*-
from ..tracer.recorder import *


class PinEmulator(object):
    def __init__(self, dev_name):
        self._dev_name = dev_name
        self._recorder = Recorder()
        add_recorder(self._recorder)
        self._pins = dict()

    def __del__(self):
        del_recorder(self._recorder)

    def set_pin_dir(self, pin_id, pin_dir):
        self._recorder.record("set pin{0} direction {1}".format(pin_id, pin_dir))
        if pin_id not in self._pins.keys():
            self._pins[pin_id] = dict()

        self._pins[pin_id]['dir'] = pin_dir

    def get_pin_dir(self, pin_id):
        self._recorder.record("get pin{0} direction".format(pin_id))
        if pin_id not in self._pins.keys() or 'dir' not in self._pins[pin_id].keys():
            return 'input'
        return self._pins[pin_id]['dir']

    def set_pin(self, pin_id, level):
        self._recorder.record("set pin{0} level {1}".format(pin_id, level))
        if pin_id not in self._pins.keys():
            self._pins[pin_id] = dict()

        # This just for emulator to write output level same as input level
        self._pins[pin_id]['level'] = level

    def get_pin(self, pin_id):
        self._recorder.record("get pin{0} level".format(pin_id))
        if pin_id not in self._pins.keys() or 'level' not in self._pins[pin_id].keys():
            return 0
        # This just for emulator to read input level same as output level
        return self._pins[pin_id]['level']
