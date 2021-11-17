# -*- coding: utf-8 -*-

from mix.driver.core.tracer.recorder import *
from mix.driver.core.bus.axi4_lite_def import PLGPIODef

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class MIXGPIOSGEmulator(object):
    def __init__(self, dev_name, reg_size):
        self._dev_name = dev_name
        self._reg_size = reg_size
        self._recorder = Recorder()
        add_recorder(self._recorder)
        self._regs = {reg: 0x00000000 for reg in PLGPIODef.DIR_REGISTERS}
        self._regs.update({reg: 0x00000000 for reg in PLGPIODef.INPUT_REGISTERS})
        self._regs.update({reg: 0x00000000 for reg in PLGPIODef.OUTPUT_REGISTERS})

    def __del__(self):
        del_recorder(self._recorder)

    def _get_reg_index(self, pin_id):
        assert pin_id >= 0 and pin_id < 128
        return (pin_id / 32, pin_id % 32)

    def set_pin_dir(self, pin_id, dir):
        assert dir in ['output', 'input']

        self._recorder.record("set pin%d direction %s" % (pin_id, dir))

        (reg, bit) = self._get_reg_index(pin_id)
        # get direction register value, data width 32 bits
        reg_value = self._regs[PLGPIODef.DIR_REGISTERS[reg]]

        # change direction value in register temp data
        reg_value &= ~(1 << bit)
        if dir == PLGPIODef.DIR_INPUT:
            reg_value |= (1 << bit)

        # write data to direction register
        self._regs[PLGPIODef.DIR_REGISTERS[reg]] = reg_value

    def get_pin_dir(self, pin_id):

        self._recorder.record("get pin%d direction" % (pin_id))

        (reg, bit) = self._get_reg_index(pin_id)

        # get direction register data, data width 32 bits
        reg_value = self._regs[PLGPIODef.DIR_REGISTERS[reg]]

        # get pin bit direction
        if (reg_value & (1 << bit)) != 0:
            return PLGPIODef.DIR_INPUT
        else:
            return PLGPIODef.DIR_OUTPUT

    def set_pin(self, pin_id, level):
        assert level in [0, 1]

        self._recorder.record("set pin%d level %d" % (pin_id, level))

        (reg, bit) = self._get_reg_index(pin_id)

        # get output register data, data width 32 bits
        reg_value = self._regs[PLGPIODef.OUTPUT_REGISTERS[reg]]

        # change pin output level in register temp data
        reg_value &= ~(1 << bit)
        if level == 1:
            reg_value |= (1 << bit)

        self._regs[PLGPIODef.OUTPUT_REGISTERS[reg]] = reg_value

    def get_pin(self, pin_id):

        self._recorder.record("get pin%d level" % (pin_id))

        (reg, bit) = self._get_reg_index(pin_id)

        # get input register data, data width 32 bits
        reg_value = self._regs[PLGPIODef.INPUT_REGISTERS[reg]]

        if (reg_value & (1 << bit)) != 0:
            return 1
        else:
            return 0
