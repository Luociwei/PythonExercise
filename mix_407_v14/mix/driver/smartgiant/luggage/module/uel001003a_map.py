# -*- coding: utf-8 -*-
from __future__ import division
from luggage_map import Luggage


__author__ = 'xuboyan@SmartGiant'
__version__ = 'V0.0.1'


class UEL001003ADef:

    FUNCTION_RANGE = {
        "init_to": ["cc", "cv", "cr", "cr_c"],
        "set_CC": lambda value: 0 <= value <= 5000,
        "set_CV": lambda value: 100 <= value <= 32000,
        "set_CR": lambda value: 0.005 <= value <= 2048
    }


class UEL001003AException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class UEL001003A(Luggage):
    '''
    Luggage module supports three modes: constant current, constant voltage, constant resistance.

    compatible = ["GQQ-MJ2C-5-03A"]

    Luggage is supplied from single external voltage (12Vdc), can be used as stand alone module controlled by
    single USB connection from mac (I2C+SPI over USB), or by direct I2C + SPI interface from Xavier controller.
    Luggage can be ordered in different BOM options, supporting functionality limited to the exact needs for
    cost saving, and for different maximum dissipated power options (this includes different sizes of
    the attached heat sink and cooling fans).

    Args:
        i2c:                instance(I2C),         Which is used to control cat9555, max6642, ads1119, LTC2606
                                                        and cat24c64.
        spi:                instance(MIXQSPISG),   class of MIXQSPISG.
        gpio_switch:        instance(GPIO)/None,   This can be Pin or xilinx gpio, used to switch control mode.

    Examples:
        i2c_bus = I2C('/dev/i2c-1')
        spi_bus = '/dev/MIX_QSPI_0'
        uel001003e = UEL001003A(i2c_bus, spi_bus)
        uel001003e.reset()
        cc mode, 500 mA:
            uel001003e.init_to("cc")
            uel001003e.set_CC(500)
        cv mode, 6000 mV:
            uel001003e.init_to("cv")
            uel001003e.set_CV(6000)
        cr mode, 500 ohm:
            uel001003e.init_to("cr")
            uel001003e.set_CR(500)
        PS:
            Before switching from one channel to another, you need to call the init_to interface again to
            avoid failure of subsequent operations. For example, after outputting 500mA, you need to call
            uel001003e.init_to("cc") again, and then switch the channel to cv mode.

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-MJ2C-5-03A"]

    def __init__(self, i2c, spi, gpio_switch=None):
        super(UEL001003A, self).__init__(i2c, spi, gpio_switch)

    def _current_set(self, value):
        '''
        UEL001003A set the output current.

        Args:
            value:          float, [0~5000], unit mA

        Returns:
            string, "done", api execution successful.

        Examples:
            uel001003a._current_set(500)

        '''
        assert isinstance(value, (int, float))

        param = float(value)
        self.cat9555.set_ports([0xf1, 0x01])
        param = self.calibrate("set_CC", param, 0)
        amps_to_send = int(1048576 + param * 192)
        byte1 = (amps_to_send >> 16) & 0xFF
        byte2 = (amps_to_send >> 8) & 0xFF
        byte3 = amps_to_send & 0xFF
        self.spi.write([byte1, byte2, byte3])

        return "done"

    def read_curr(self):
        '''
        Do one time sample from adc, return the measurement result.

        Returns:
            dict, {'raw_data': raw_data, 'current': current}, raw data and current value with unit.

        Examples:
            result = uel001003a.read_curr()
            print(result)

        '''
        curr_dict = self._current_read()
        raw_data = curr_dict['raw_data']
        current = [curr_dict['current'] / 0.75, 'mA']
        return {'raw_data': raw_data, 'current': current}

    def set_CC(self, value):
        '''
        Luggage set the output current.

        Args:
            value:          float, [0~5000], unit mA

        Returns:
            string, "done", api execution successful.

        Examples:
            uel001003a.set_CC(500)

        '''
        assert isinstance(value, (int, float))
        assert UEL001003ADef.FUNCTION_RANGE["set_CC"](value)

        self._current_set(value)
        return "done"
