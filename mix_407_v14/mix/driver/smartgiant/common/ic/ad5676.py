# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg_emulator import MIXQSPISGEmulator
from mix.driver.core.bus.axi4_lite_def import PLSPIDef

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class AD5667Def:
    NOP_REGISTER = 0x00
    INPUT_REGISTER = 0x01
    LDAC_REGISTER = 0x02
    DAC_REGISTER = 0x03
    POWER_MODE_REGISTER = 0x04
    HW_LDAC_MASK_REGISTER = 0x05
    RESET_REGISTER = 0x06
    GAIN_SETUP_REGISTER = 0x07
    DCEN_REGISTER = 0x08
    READBACK_EN_REGISTER = 0x09
    UPDATE_INPUT_ALL_REGISTER = 0x0A
    UPDATE_DAC_ALL_REGISTER = 0x0B

    REG_MODE_MASK = 0x03
    REG_GAIN_1 = 0x00
    REG_GAIN_2 = 0x04

    DAC_FULL_SCALE = pow(2, 16) - 1

    MODES = {
        'normal': 0x00,
        'ground': 0x01,
        'tristate': 0x03
    }

    CHANNELS = [id for id in range(8)]


class AD5676Exception(Exception):
    def __init__(self, dev_name, err_str):
        self._err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self._err_reason


class AD5676(object):
    '''
    AD5676 function class

    ClassType = DAC

    Args:
        spi_bus:    instance(QSPI)/None,  MIXQSPISG class instance, if not using, will create emulator.
        mvref:      float,          Reference voltage.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT1_SPI0', 256)
        spi = MIXQSPISG(axi4_bus)

    '''

    def __init__(self, spi_bus=None, mvref=2500):
        if spi_bus is None:
            self._spi_bus = MIXQSPISGEmulator('ad5676_emulator', PLSPIDef.REG_SIZE)
        else:
            self._spi_bus = spi_bus
        self._mvref = mvref
        self._dev_name = self._spi_bus._dev_name
        self._mode_register = 0
        self._gain_register = 0

    def _write_register(self, command, address, high_byte, low_byte):
        '''
        AD5676 write register function

        Args:
            command,    hexmial, [0x00~0x0f], register command.
            address,    hexmial, [0x00-0x0f], register address.
            high_byte,  hexmial, [0x00-0xff], high byte data to write.
            low_byte,   hexmial, [0x00-0xff], low byte data to write.

        Examples:
            ad5676._write_register(0x01, 0x00m, 0x01, 0x00)

        '''
        self._spi_bus.write([(command << 4) | address, high_byte, low_byte])

    def set_mode(self, channel, mode):
        '''
        AD5676 set channel mode

        Args:
            channel:    int, [0~7], channel id.
            mode:       string, ['normal', 'ground', 'tristate'], channel output state.

        Examples:
            ad5676.set_mode(0, 'normal')

        '''
        assert channel in AD5667Def.CHANNELS
        assert mode in AD5667Def.MODES.keys()

        self._mode_register &= ~(AD5667Def.REG_MODE_MASK << (channel * 2))
        self._mode_register |= (AD5667Def.MODES[mode] << (channel * 2))
        self._write_register(AD5667Def.POWER_MODE_REGISTER, channel,
                             (self._mode_register >> 8) & 0xFF, self._mode_register & 0xFF)

    def get_gain(self):
        '''
        AD5676 get gain value

        Examples:
            gain = ad5676.get_gain
            print(gain)

        '''
        return (1 if self._gain_register == AD5667Def.REG_GAIN_1 else 2)

    def set_gain(self, gain):
        '''
        AD5676 set gain value

        Args:
            gain: int(1, 2), AD5676 gain value

        Examples:
            ad5676.set_gain(1)

        '''
        assert gain in [1, 2]
        self._gain_register = (AD5667Def.REG_GAIN_1 if gain == 1 else AD5667Def.REG_GAIN_2)
        self._write_register(AD5667Def.GAIN_SETUP_REGISTER,
                             0x00,
                             (self._gain_register >> 8) & 0xFF,
                             self._gain_register & 0xFF)

    def output_volt_dc(self, channel, volt):
        '''
        AD5676 output dc voltage

        Args:
            channel:    int, [0~7], channel id.
            volt:       float, output voltage value.

        Examples:
            a5676.output_volt_dc(0, 1000)

        '''
        assert channel in AD5667Def.CHANNELS
        assert volt >= 0

        if volt > self._mvref * self.get_gain():
            msg = 'Voltage should not bigger than %f mV.' % (self._mvref * self.get_gain())
            raise AD5676Exception(self._dev_name, msg)

        reg_value = int(volt * AD5667Def.DAC_FULL_SCALE / (self.get_gain() * self._mvref))
        self._write_register(AD5667Def.DAC_REGISTER, channel, (reg_value >> 8) & 0xFF, reg_value & 0xFF)
