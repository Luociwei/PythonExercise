# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *
from mix.driver.smartgiant.common.ic.max6642 import *

__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.1'


class MAX6642Emulator(object):
    def __init__(self, dev_name):
        self._dev_name = dev_name
        self._recorder = Recorder()
        add_recorder(self._recorder)

        self._state = 0x00
        self._manufacturer_id = 0x4d
        self._config = 0x80
        self._high_limit = {
            'local': 70,
            'remote': 120
        }

    def __del__(self):
        del_recorder(self._recorder)

    def get_temperature(self, channel, extended=False):
        channel = channel.lower()
        assert channel in MAX6642Def.CMD_REGS

        self._recorder.record("%s read_temperature: %s" % (self._dev_name,
                                                           channel))
        return 25.25 if extended else 25

    def read_high_limit(self, channel):
        channel = channel.lower()
        assert channel in MAX6642Def.CMD_REGS

        self._recorder.record("%s read_high_limit: %s" % (self._dev_name,
                                                          channel))
        self._high_limit[channel]

    def write_high_limit(self, channel, limit):
        channel = channel.lower()
        assert channel in MAX6642Def.CMD_REGS
        assert isinstance(limit, int) and 0 <= limit <= 0xff

        self._recorder.record("%s write_high_limit: %s %d" % (self._dev_name,
                                                              channel, limit))
        self._high_limit[channel] = limit

    def manufacturer_id(self):
        self._recorder.record(self._dev_name + " manufacturer_id")
        return self._manufacturer_id

    def read_state(self):
        self._recorder.record(self._dev_name + " read_state")
        return self._state

    def read_config(self):
        self._recorder.record(self._dev_name + " read_config")
        return self._config

    def write_config(self, config_bit, bit_val):
        assert config_bit in MAX6642Def.CONFIG_BIT
        assert isinstance(bit_val, int) and 0 <= bit_val <= 1

        self._recorder.record("%s write_config: %s %d" % (self._dev_name,
                                                          config_bit, bit_val))

        if bit_val:
            self._config |= (0x1 << MAX6642Def.CONFIG_BIT[config_bit])
        else:
            self._config &= ~(0x1 << MAX6642Def.CONFIG_BIT[config_bit])
