# -*- coding: utf-8 -*-

import time
from mix.driver.smartgiant.common.module.mix_board import MIXBoard
from mix.driver.core.ic.cat9555 import CAT9555
from mix.driver.core.ic.cat9555_emulator import CAT9555Emulator
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.nct75_emulator import NCT75Emulator

__author__ = 'Zili.Li@SmartGiant'
__version__ = '0.1'

BIT_MAP = {
    'enable': {'VBUS': 1, 'VBATT': 2},
    'reset': 3,
    'AD8253': {
        'VBATT': {'nWR': 4, 'A0': 5, 'A1': 6},
        'VBUS': {'nWR': 7, 'A0': 8, 'A1': 9}
    }
}


class PSU001003Def:
    HIGH_LEVEL = 1
    LOW_LEVEL = 0
    EEPROM_DEV_ADDR = 0x50
    SENSOR_DEV_ADDR = 0x49
    CAT9555_ADDR = 0x22
    # PSU001003 hardware reset delay time at least 120ns
    RESET_DELAY_S = 0.001


class PSU001003Exception(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class PSU001003Base(MIXBoard):
    '''
    Base class of PSU001003 and PSU001003Compatible.

    Providing common PSU001003 methods.

    Args:
        i2c_io_exp:      instance(I2C),  if None, invoke CAT9555 emulator.
        i2c:             instance(I2C),  if None, invoke Eeprom,NCT75 emulator.
        eeprom_dev_addr: int,                Eeprom device address.
        sensor_dev_addr: int,                NCT75 device address.

    Examples:
        i2c = I2C('/dev/i2c-1')
        i2c_io_exp = I2C('/dev/i2c-2')
        psu001003 = PSU001003(i2c_io_exp, i2c)

    '''

    rpc_public_api = ['module_init', 'reset', 'output_enable', 'output_disable',
                      'gain_set'] + MIXBoard.rpc_public_api

    def __init__(self, i2c_io_exp=None, i2c=None,
                 eeprom_dev_addr=PSU001003Def.EEPROM_DEV_ADDR, sensor_dev_addr=PSU001003Def.SENSOR_DEV_ADDR):

        if i2c_io_exp and i2c:
            self.cat9555 = CAT9555(PSU001003Def.CAT9555_ADDR, i2c_io_exp)
            self.eeprom = CAT24C32(eeprom_dev_addr, i2c)
            self.sensor = NCT75(sensor_dev_addr, i2c)
        elif i2c_io_exp is None and i2c_io_exp is None:
            self.cat9555 = CAT9555Emulator(0x20, None, None)
            self.eeprom = EepromEmulator('eeprom_emulator')
            self.sensor = NCT75Emulator('nct75_emulator')
        else:
            raise PSU001003Exception('Not Allowed: either of i2c_io_exp,i2c is None')

        super(PSU001003Base, self).__init__(self.eeprom, self.sensor)

    def _check_channel(self, channel):
        '''
        Check the channel if it is valid.

        Args:
            channel:      string, ['VBATT', 'VBUS'], the channel to check.

        Returns:
            string, ['VBATT', 'VBUS'], the channel in specific format.

        Raise:
            PSU001003Exception:      If channel is invalid, exception will be raised.

        '''
        for ch in ['VBATT', 'VBUS']:
            if channel.lower() == ch.lower():
                return ch
        raise PSU001003Exception("channel {} is invalid".format(channel))

    def module_init(self):
        '''
        This function will set cat9555 all pins to low level and set gain to 100.

        Returns:
            string, "done", api execution successful.

        Examples:
            psu001003.module_init()

        '''
        self.cat9555.set_pins_dir([0x00, 0x00])
        self.cat9555.set_ports([0x00, 0x00])
        self.gain_set('VBATT', 100)
        self.gain_set('VBUS', 100)
        return "done"

    def reset(self):
        '''
        PSU001003 reset hardware when over-current or over-voltage occurs.

        Note: 74HC74 Datasheet(Page.11), clock pulse width HIGH or LOW at least 120us

        Returns:
            string, "done", api execution successful.

        Examples:
            psu001003.reset()

        '''
        self.cat9555.set_pin(BIT_MAP['reset'], PSU001003Def.HIGH_LEVEL)
        # Delay at least 120us
        time.sleep(PSU001003Def.RESET_DELAY_S)
        self.cat9555.set_pin(BIT_MAP['reset'], PSU001003Def.LOW_LEVEL)
        return "done"

    def output_enable(self, channel):
        '''
        Enable channel's output

        Args:
            channel:      string, ['VBATT', 'VBUS'].

        Examples:
            psu001003.output_enable('VBUS')

        '''
        self._check_channel(channel)
        self.cat9555.set_pin(BIT_MAP['enable'][channel], PSU001003Def.HIGH_LEVEL)
        return "done"

    def output_disable(self, channel):
        '''
        Disable channel's output

        Args:
            channel:      string, ['VBATT', 'VBUS'].

        Examples:
            psu001003.output_disable('VBUS')

        '''
        self._check_channel(channel)
        self.cat9555.set_pin(BIT_MAP['enable'][channel], PSU001003Def.LOW_LEVEL)
        return "done"

    def gain_set(self, channel, gain):
        '''
        Set channel gain value.

        see the truth table listing in AD8253 Datasheet(Page.17 Table 6)

        Args:
            channel:      string, ['VBATT', 'VBUS'].
            gain:         int, [1, 10, 100, 1000].

            +-------+------+------+-------------+
            | gain  |  A1  |  A0  |    nWR      |
            +=======+======+======+=============+
            |  1    |  0   |  0   | High to Low |
            +-------+------+------+-------------+
            |  10   |  0   |  1   | High to Low |
            +-------+------+------+-------------+
            |  100  |  1   |  0   | High to Low |
            +-------+------+------+-------------+
            |  1000 |  1   |  1   | High to Low |
            +-------+------+------+-------------+

            Note:

            1 stand for high level

            0 stand for low  level

        Examples:
            psu001003.gain_set('VBATT', 10)

        '''
        self._check_channel(channel)
        assert gain in [1, 10, 100, 1000]

        GAIN_MAP = {
            '1': {'A0': 0, 'A1': 0},
            '10': {'A0': 1, 'A1': 0},
            '100': {'A0': 0, 'A1': 1},
            '1000': {'A0': 1, 'A1': 1}
        }

        # Set A0 and A1
        self.cat9555.set_pin(BIT_MAP['AD8253'][channel]['A0'], GAIN_MAP[str(gain)]['A0'])
        self.cat9555.set_pin(BIT_MAP['AD8253'][channel]['A1'], GAIN_MAP[str(gain)]['A1'])
        # nWR signal: Downward edge
        self.cat9555.set_pin(BIT_MAP['AD8253'][channel]['nWR'], PSU001003Def.HIGH_LEVEL)
        self.cat9555.set_pin(BIT_MAP['AD8253'][channel]['nWR'], PSU001003Def.LOW_LEVEL)
        return "done"


class PSU001003(PSU001003Base):
    '''
    PSU001003 function class is power supply and simulated battery module driver.

    compatible = ["GQQ-PSU001003-000"]

    Args:
        i2c_io_exp:      instance(I2C)/None,  if None, invoke CAT9555 emulator.
        i2c:             instance(I2C)/None,  if None, invoke Eeprom,NCT75 emulator.

    Examples:
        i2c = I2C('/dev/i2c-1')
        i2c_io_exp = I2C('/dev/i2c-2')
        psu001003 = PSU001003(i2c_io_exp, i2c)

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-PSU001003-000"]

    def __init__(self, i2c_io_exp=None, i2c=None):
        super(PSU001003, self).__init__(i2c_io_exp, i2c,
                                        PSU001003Def.EEPROM_DEV_ADDR, PSU001003Def.SENSOR_DEV_ADDR)
