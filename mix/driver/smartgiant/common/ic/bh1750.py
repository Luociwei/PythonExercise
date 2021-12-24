# -*- coding: utf-8 -*-
import time
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator
from mix.driver.core.bus.axi4_lite_def import PLI2CDef


__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class BH1750Def:
    OP_POWER_DOWN = 0x00
    OP_POWER_ON = 0x01
    OP_RESET = 0x07
    OP_CONTI_H_RESO_MODE = 0x10
    OP_CONTI_H_RESO_MODE2 = 0x11
    OP_CONTI_L_RESO_MODE = 0x13
    OP_ONCE_H_RESO_MODE = 0x20
    OP_ONCE_H_RESO_MODE2 = 0x21
    OP_ONCE_L_RESO_MODE = 0x23
    OP_MEAS_TIME_HIGH_MASK = 0x07
    OP_MEAS_TIME_HIGH_BIT = 0x40
    OP_MEAS_TIME_LOW_MASK = 0x1F
    OP_MEAS_TIME_LOW_BIT = 0x60

    H_RESO_MEAS_TIME = 120.0

    MEASURE_TIME_DELAY = 60.0

    MTREG_DEFAULT = 69.0


class BH1750(object):
    '''
    BH1750 function class

    ClassType = ADC

    Args:
        dev_addr:     hexmial,            bh1750 i2c bus device address.
        i2c_bus:      instance(I2C)/None, i2c bus instance, if not using,
                                          will create emulator.
        measure_time: float,              exposure  millisecond time.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT_I2C_0', 256)
        i2c_bus = MIXI2CSG(axi4_bus)
        bh1750 = BH1750(0x23, i2c_bus)

    '''

    def __init__(self, dev_addr, i2c_bus=None, measure_time=120):
        assert dev_addr in [0x5c, 0x23]
        assert measure_time >= 53.9 and measure_time <= 441.7
        self._dev_addr = dev_addr
        if i2c_bus is None:
            self.i2c_bus = I2CBusEmulator('bh1750_emulator', PLI2CDef.REG_SIZE)
        else:
            self.i2c_bus = i2c_bus
        self.measure_time = measure_time
        self.open()

    def __del__(self):
        self.close()

    def open(self):
        '''
        BH1750 internal function to power on and set exposure time

        Examples:
            bh1750.open()

        '''
        self.i2c_bus.write(self._dev_addr, [BH1750Def.OP_POWER_ON])
        self._mtreg = int(self.measure_time /
                          BH1750Def.H_RESO_MEAS_TIME * BH1750Def.MTREG_DEFAULT)
        self.i2c_bus.write(
            self._dev_addr, [BH1750Def.OP_MEAS_TIME_HIGH_BIT | (self._mtreg >> 5)])
        self.i2c_bus.write(
            self._dev_addr, [BH1750Def.OP_MEAS_TIME_LOW_BIT | (self._mtreg & 0x1F)])

    def close(self):
        '''
        BH1750 internal function to power down bh1750

        Examples:
            bh1750.close()

        '''
        self.i2c_bus.write(self._dev_addr, [BH1750Def.OP_POWER_DOWN])

    def get_intensity(self):
        '''
        BH1750 to get intensity value

        Examples:
            bh1750.get_intensity()

        '''
        self.i2c_bus.write(self._dev_addr, [BH1750Def.OP_ONCE_H_RESO_MODE])
        time.sleep((BH1750Def.H_RESO_MEAS_TIME + BH1750Def.MEASURE_TIME_DELAY) / 1000.0)
        rd_data = self.i2c_bus.read(self._dev_addr, 2)
        return (((rd_data[0] << 8) | rd_data[1]) / 1.2 * (BH1750Def.MTREG_DEFAULT / self._mtreg))
