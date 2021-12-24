# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator
from mix.driver.core.bus.axi4_lite_def import PLI2CDef

__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1'


class AD5675Def:
    NOP_REGISTER = 0x00
    INPUT_REGISTER = 0x01
    LDAC_REGISTER = 0x02
    DAC_REGISTER = 0x03
    POWER_MODE_REGISTER = 0x04
    HW_LDAC_MASK_REGISTER = 0x05
    RESET_REGISTER = 0x06
    GAIN_SETUP_REGISTER = 0x07
    UPDATE_INPUT_ALL_REGISTER = 0x0A
    UPDATE_DAC_ALL_REGISTER = 0x0B

    REG_MODE_MASK = 0x03
    REG_GAIN_1 = 0x00
    REG_GAIN_2 = 0x04

    ALL_LDAC_PIN_DISABLE = 0x00
    ALL_LDAC_PIN_ENABLE = 0xFF

    DAC_FULL_SCALE = pow(2, 16) - 1

    MODES = {
        'normal': 0x00,
        'ground': 0x01,
        'tristate': 0x03
    }

    CHANNELS = [id for id in range(8)]


class AD5675Exception(Exception):
    def __init__(self, dev_name, err_str):
        self._err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self._err_reason


class AD5675(object):
    '''
    AD5675 is low power, octal, 12-/16-bit buffered voltage output digital-to-analog converters (DACs).
    They include a 2.5 V, 2 ppm/°C internal reference (enabled by default) and a gain select pin
    giving a full-scale output of 2.5 V (gain = 1) or 5 V (gain = 2). The devices operate from a
    single 2.7 V to 5.5 V supply and are guaranteed monotonic by design.

    ClassType = DAC

    Args:
        dev_addr:    hexmial,             ad5675 device address.
        i2c_bus:     instance(I2C)/None,  i2c bus instance, if not using, will create emulator.
        mvref:       float,               reference voltage.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = MIXI2CSG(axi4_bus)
        ad5675 = AD5675(0x0C, i2c, 2500)

    '''

    def __init__(self, dev_addr, i2c_bus=None, mvref=2500):
        assert (dev_addr & (~0x03)) == 0x0C
        if i2c_bus is None:
            self._i2c_bus = I2CBusEmulator('i2c_emulator', PLI2CDef.REG_SIZE)
        else:
            self._i2c_bus = i2c_bus
        self.dev_addr = dev_addr
        self._mvref = mvref
        self._dev_name = self._i2c_bus._dev_name
        self._mode_register = 0
        self._gain_register = 0

    def _write_register(self, command, address, high_byte, low_byte):
        '''
        AD5675 write register function

        Args:
            command,    hexmial, [0x00~0x0f], register command.
            address,    hexmial, [0x00-0x0f], register address.
            high_byte,  hexmial, [0x00-0xff], high byte data to write.
            low_byte,   hexmial, [0x00-0xff], low byte data to write.

        Examples:
            ad5675._write_register(0x01, 0x00, 0x01, 0x00)

        '''
        self._i2c_bus.write(self.dev_addr, [(command << 4) | address, high_byte, low_byte])

    def _read_register(self, command, address):
        rd_data = self._i2c_bus.write_and_read(self.dev_addr, [0x80 | (command << 4) | address], 2)
        return (rd_data[0] << 8) | rd_data[1]

    def set_mode(self, channel, mode):
        '''
        AD5675 set channel mode

        Args:
            channel:    int, [0~7], channel id.
            mode:       string, ['normal', 'ground', 'tristate'], channel output state.

        Examples:
            ad5675.set_mode(0, 'normal')

        '''
        assert channel in AD5675Def.CHANNELS
        assert mode in AD5675Def.MODES.keys()

        self._mode_register &= ~(AD5675Def.REG_MODE_MASK << (channel * 2))
        self._mode_register |= (AD5675Def.MODES[mode] << (channel * 2))
        self._write_register(AD5675Def.POWER_MODE_REGISTER, channel,
                             (self._mode_register >> 8) & 0xFF, self._mode_register & 0xFF)

    def get_gain(self):
        '''
        AD5675 get gain value

        Examples:
            gain = ad5675.get_gain
            print(gain)

        '''
        return (1 if self._gain_register == AD5675Def.REG_GAIN_1 else 2)

    def set_gain(self, gain):
        '''
        AD5675 set gain value

        Args:
            gain: int, [1, 2], AD5675 gain value.

        Examples:
            ad5675.set_gain(1)

        '''
        assert gain in [1, 2]
        self._gain_register = (AD5675Def.REG_GAIN_1 if gain == 1 else AD5675Def.REG_GAIN_2)
        self._write_register(AD5675Def.GAIN_SETUP_REGISTER, 0x00,
                             (self._gain_register >> 8) & 0xFF, self._gain_register & 0xFF)

    def output_volt_dc(self, channel, volt):
        '''
        AD5675 output dc voltage

        Args:
            channel:    int, [0~7], channel id.
            volt:       float, output voltage value.

        Examples:
            ad5675.output_volt_dc(0, 1000)

        '''
        assert channel in AD5675Def.CHANNELS
        assert volt >= 0

        if volt > self._mvref * self.get_gain():
            raise AD5675Exception(self._dev_name, 'Voltage should not bigger than %f mV.' %
                                  (self._mvref * self.get_gain()))

        reg_value = int(volt * AD5675Def.DAC_FULL_SCALE / (self.get_gain() * self._mvref))
        self._write_register(AD5675Def.DAC_REGISTER, channel, (reg_value >> 8) & 0xFF, reg_value & 0xFF)

    def ldac_pin_disable(self, channel='all'):
        reg_value = 0
        # reg_value = self._read_register(AD5675Def.HW_LDAC_MASK_REGISTER, 0)
        if channel != 'all':
            reg_value &= ~(1 << channel)
        else:
            reg_value = AD5675Def.ALL_LDAC_PIN_DISABLE
        self._write_register(AD5675Def.HW_LDAC_MASK_REGISTER, 0, (reg_value >> 8) & 0xFF, reg_value & 0xFF)

    def ldac_pin_enable(self, channel='all'):
        reg_value = 0
        # reg_value = self._read_register(AD5675Def.HW_LDAC_MASK_REGISTER, 0)
        if channel != 'all':
            reg_value |= (1 << channel)
        else:
            reg_value = AD5675Def.ALL_LDAC_PIN_ENABLE
        self._write_register(AD5675Def.HW_LDAC_MASK_REGISTER, 0, (reg_value >> 8) & 0xFF, reg_value & 0xFF)
