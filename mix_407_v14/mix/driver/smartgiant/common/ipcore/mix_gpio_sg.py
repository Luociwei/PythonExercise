# -*- coding: utf-8 -*-

from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator
from mix.driver.core.bus.axi4_lite_def import PLGPIODef

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class MIXGPIOSG(object):
    '''
    Singleton wrapper of SG GPIO driver.

    ClassType = GPIO

    This is to ensure only 1 instance is created for the same char device
    in /dev/MIX_GPIO_0, even if instantiated multiple times.

    Args:
        axi4_bus:   instance(AXI4LiteBus)/string/None, GPIO device full path like '/dev/MIX_GPIO'.

    Examples:
        gpio_1 = I2C('/dev/MIX_GPIO')
        gpio_2 = I2C('/dev/MIX_GPIO')
        assert gpio_1 == gpio_2          # True

    '''
    # class variable to host all i2c bus instances created.
    instances = {}

    def __new__(cls, axi4_bus=None):
        if axi4_bus in cls.instances:
            # use existing instance
            pass
        else:
            # create a new one
            instance = _MIXGPIOSG(axi4_bus)
            cls.instances[axi4_bus] = instance
        return cls.instances[axi4_bus]


class _MIXGPIOSG(object):
    '''
    MIXGPIOSG function class

    Args:
        axi4_bus:   instance(AXI4LiteBus)/None, if not using this parameter, will create emulator.

    Examples:
        gpio = MIXGPIOSG('/dev/MIX_GPIO')

    '''

    rpc_public_api = ['set_pin_dir', 'get_pin_dir', 'set_pin', 'get_pin']

    def __init__(self, axi4_bus=None):
        if axi4_bus is None:
            self._axi4_bus = AXI4LiteBusEmulator("mix_gpio_sg_emulator", PLGPIODef.REG_SIZE)
        elif isinstance(axi4_bus, basestring):
            # device path; create axi4litebus instance here.
            self._axi4_bus = AXI4LiteBus(axi4_bus, PLGPIODef.REG_SIZE)
        else:
            self._axi4_bus = axi4_bus

    def _get_reg_index(self, pin_id):
        '''
        GPIO get register index
        '''
        assert pin_id >= 0 and pin_id < 128
        return (pin_id / 32, pin_id % 32)

    def set_pin_dir(self, pin_id, dir):
        '''
        GPIO set direction of specific pin

        Args:
            pin_id:    int, [0~127], Set direction of this pin.
            dir:       string, ['input', 'output'], Set pin specific direction.

        Examples:
            gpio.set_pin_dir(0, 'output')

        '''
        assert dir in ['output', 'input']

        (reg, bit) = self._get_reg_index(pin_id)
        # get direction register value, data width 32 bits
        rd_data = self._axi4_bus.read_32bit_inc(PLGPIODef.DIR_REGISTERS[reg], 1)[0]
        reg_value = rd_data & 0xFFFFFFFF

        # change direction value in register temp data
        reg_value &= ~(1 << bit)
        if dir == PLGPIODef.DIR_INPUT:
            reg_value |= (1 << bit)

        # write data to direction register
        self._axi4_bus.write_32bit_inc(PLGPIODef.DIR_REGISTERS[reg], [reg_value])

    def get_pin_dir(self, pin_id):
        '''
        GPIO get direction of specific pin

        Args:
            pin_id:     int, [0~127], Get direction of this pin.

        Returns:
            string, ['input', 'output'], pin dir.

        Examples:
            gpio.get_pin_dir(0)

        '''
        (reg, bit) = self._get_reg_index(pin_id)

        # get direction register data, data width 32 bits
        rd_data = self._axi4_bus.read_32bit_inc(PLGPIODef.DIR_REGISTERS[reg], 1)[0]
        reg_value = rd_data & 0xFFFFFFFF

        # get pin bit direction
        if (reg_value & (1 << bit)) != 0:
            return PLGPIODef.DIR_INPUT
        else:
            return PLGPIODef.DIR_OUTPUT

    def set_pin(self, pin_id, level):
        '''
        GPIO set specific pin level

        Args:
            pin_id:    int, [0~127], Get direction of this pin.
            level:     int, [0, 1], 0 for low level, 1 for high level.

        Examples:
            gpio.set_pin(0, 0)  # set pin 0 level low

        '''
        assert level in [0, 1]
        (reg, bit) = self._get_reg_index(pin_id)

        # get output register data, data width 32 bits
        rd_data = self._axi4_bus.read_32bit_inc(PLGPIODef.OUTPUT_REGISTERS[reg], 1)[0]
        reg_value = rd_data & 0xFFFFFFFF

        # change pin output level in register temp data
        reg_value &= ~(1 << bit)
        if level == 1:
            reg_value |= (1 << bit)

        self._axi4_bus.write_32bit_inc(PLGPIODef.OUTPUT_REGISTERS[reg], [reg_value])

    def get_pin(self, pin_id):
        '''
        GPIO get specific pin level

        Args:
            pin_id:     int, [0~127], Get direction of this pin.

        Returns:
            int, [0, 1], pin level.

        Examples:
            level = gpio.get_pin(0)
            print(level)

        '''
        (reg, bit) = self._get_reg_index(pin_id)

        # get input register data, data width 32 bits
        rd_data = self._axi4_bus.read_32bit_inc(PLGPIODef.INPUT_REGISTERS[reg], 1)[0]
        reg_value = rd_data & 0xFFFFFFFF

        if (reg_value & (1 << bit)) != 0:
            return 1
        else:
            return 0
