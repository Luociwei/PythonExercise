# -*- coding: utf-8 -*-
from ..bus.i2c_bus_emulator import I2CBusEmulator
from ..bus.axi4_lite_def import PLI2CDef


'''
A2 A1 A0 Addr
0 0 0         0x48
0 0 1      0x49
0 1 0      0x4A
0 1 1      0x4B
1 0 0      0x4C
1 0 1      0x4D
1 1 0      0x4E
1 1 1      0x4F
'''


class NCT75Def:
    TEMP_REGISTER = 0x00
    TEMP_REGISTER_SIZE = 2
    CONFIG_REGISTER = 0x01
    CONFIG_REGISTER_SIZE = 1
    THYST_REGISTER = 0x02
    THYST_REGISTER_SIZE = 2
    TOS_REGISTER = 0x03
    TOS_REGISTER_SIZE = 2
    ONE_SHOT_REGISTER = 0x04
    ONE_SHOT_REGISTER_SIZE = 1
    WORK_MODE_MASK = (1 << 5)
    WORK_MODE_NORMAL = 0x00
    WORK_MODE_ONESHOT = 0x20
    CONVER_TEMP = 0xff

    CONFIG_OVERTEMPERATURE_MODE_MASK = (1 << 1)

    CONFIG_OVERTEMPERATURE_MODE_CMP = (0 << 1)
    CONFIG_OVERTEMPERATURE_MODE_INT = (1 << 1)

    CONFIG_POLARITY_MASK = (1 << 2)
    CONFIG_POLARITY_ACTIVE_HIGH = (1 << 2)
    CONFIG_POLARITY_ACTIVE_LOW = (0 << 2)

    CONFIG_OVERTEMPERATURE_MODE = {
        'cmp': CONFIG_OVERTEMPERATURE_MODE_CMP,
        'int': CONFIG_OVERTEMPERATURE_MODE_INT
    }

    CONFIG_POLARITY = {
        'low': CONFIG_POLARITY_ACTIVE_LOW,
        'high': CONFIG_POLARITY_ACTIVE_HIGH
    }


class NCT75(object):
    '''
    NCT75 TEMPERATURE SENSOR function class

    ClassType = SENSOR

    Args:
        dev_addr:    hexmial,       I2C device address of TEMPERATURE SENSOR.
        i2c_bus:     instance(I2C)/None,  i2c bus instance, If not using this parameter,
                                          it will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        axi4_i2c = PLI2CBus(axi)
        nct75 = NCT75(0x48, axi4_i2c)

    '''
    rpc_public_api = ['get_temperature', 'get_work_mode', 'set_work_mode']

    def __init__(self, dev_addr, i2c_bus=None):
        if i2c_bus is None:
            self.i2c_bus = I2CBusEmulator("i2c_emulator",
                                          PLI2CDef.REG_SIZE)
        else:
            self.i2c_bus = i2c_bus

        self.dev_addr = dev_addr
        self.mode = 'normal'

    def register_read(self, reg_addr, reg_size):
        '''
        NCT75 read register

        Args:
            reg_addr:   hexmial,  register address.
            reg_size:   int,      read length.

        Returns:
            list, [value, ...], each element takes one byte.

        Examples:
            nct75.register_read(0x00, 2)

        '''
        return self.i2c_bus.write_and_read(self.dev_addr,
                                           [reg_addr], reg_size)

    def register_write(self, reg_addr, reg_data):
        '''
        NCT75 write register

        Args:
            reg_addr:    hexmial,   register address.
            reg_data:    list,       register data.

        Examples:
            nct75.register_write(0x00, [0x22])

        '''
        return self.i2c_bus.write(self.dev_addr, [reg_addr] + reg_data)

    def _temperature_to_value(self, temp):
        '''
        Convert temperature to sensor register value

        Args:
            temp:       float, temperature value

        Returns:
            int, sensor register value
        '''
        temp = temp * 16
        if temp < 0:
            temp += 0x1000
        temp = int(temp) << 4
        return temp

    def get_temperature(self):
        '''
        NCT75 get temperature

        Examples:
            temp = nct75.get_temperature()
            print(temp)

        '''
        if self.mode == 'one_shot':
            self.register_write(
                NCT75Def.ONE_SHOT_REGISTER, [NCT75Def.CONVER_TEMP])
        ret = self.register_read(
            NCT75Def.TEMP_REGISTER, NCT75Def.TEMP_REGISTER_SIZE)
        '''12-bit Temperature Data Format'''
        '''Positive Temperature = ADC Code (decimal)/16'''
        value = ((ret[0] << 8) + ret[1]) >> 4
        '''Negative Temperature = (ADC Code(decimal) − 4096)/16'''
        if value > 0x800:
            value = value - 0x1000
        temp = value / 16
        return temp

    def get_work_mode(self):
        '''
        NCT75 get work mode

        Examples:
            mode = nct75.get_work_mode()
            print(mode)

        '''
        return self.mode

    def set_work_mode(self, mode):
        '''
        NCT75 set work mode

        Args:
            mode:    string, ['normal', 'one_shot'], nct75 work mode.

        Examples:
            nct75.set_work_mode('normal')

        '''
        assert mode in ['normal', 'one_shot']
        self.mode = mode
        value = self.register_read(NCT75Def.CONFIG_REGISTER, 1)[0]
        value &= ~NCT75Def.WORK_MODE_MASK
        if self.mode == 'one_shot':
            value |= NCT75Def.WORK_MODE_ONESHOT
            self.register_write(NCT75Def.CONFIG_REGISTER,
                                [value])
        else:
            value |= NCT75Def.WORK_MODE_NORMAL
            self.register_write(NCT75Def.CONFIG_REGISTER,
                                [NCT75Def.WORK_MODE_NORMAL])

    def config_overtemperature(self, t_os, t_hyst, mode='cmp', polarity='low'):
        '''
        Config nct75 over temperature

        Args:
            t_os:       float, temperature limit at which the part asserts an OS/Alert.
            t_hyst:     float, temperature hysteresis value for the overtemperature output.
            mode:       string, ['cmp', 'int'], default 'cmp', overtemperature modes.
            polarity:   string, ['low', 'high'], default 'low', active polarity of the OS
                                Alert output pin.
        '''
        assert mode in NCT75Def.CONFIG_OVERTEMPERATURE_MODE
        assert polarity in NCT75Def.CONFIG_POLARITY

        value = self.register_read(NCT75Def.CONFIG_REGISTER, NCT75Def.CONFIG_REGISTER_SIZE)[0]
        value &= ~NCT75Def.CONFIG_OVERTEMPERATURE_MODE_MASK
        value &= ~NCT75Def.CONFIG_POLARITY_MASK
        value |= NCT75Def.CONFIG_OVERTEMPERATURE_MODE[mode]
        value |= NCT75Def.CONFIG_POLARITY[polarity]
        self.register_write(NCT75Def.CONFIG_REGISTER, [value])

        value = self._temperature_to_value(t_hyst)
        self.register_write(NCT75Def.THYST_REGISTER, [(value >> 8) & 0xFF, value & 0xFF])

        value = self._temperature_to_value(t_os)
        self.register_write(NCT75Def.TOS_REGISTER, [(value >> 8) & 0xFF, value & 0xFF])
