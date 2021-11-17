# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *
from mix.driver.smartgiant.common.ic.ad569x import AD569XDef

__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.1'


class AD569X(object):
    '''
    AD569X Emulator class
    '''

    def __init__(self, dev_name):
        self._dev_addr = AD569XDef.SLAVE_ADDR_5MSB
        self.vref = AD569XDef.VREF
        self.resolution = AD569XDef.AD5696_RESOLUTION
        self.gain = AD569XDef.GAIN_1
        self.dev_name = dev_name
        self._recorder = Recorder()
        add_recorder(self._recorder)

    def _write_register(self, command, data):
        '''
        Write data to Input Shift Register (24-bit wide) of AD569X.

        Args:
            command:   hexmial, [0~0xff], command byte.
            data:      hexmial, [0~0xffff], high_byte and low_byte.

        '''
        assert isinstance(command, int) and 0x00 <= command <= 0xFF
        assert isinstance(data, int) and 0x0000 <= data <= 0xFFFF

        high_byte = (data >> 8) & 0xFF
        low_byte = data & 0xFF

        self._recorder.record("%s write_register: [0x%02x, 0x%02x, 0x%02x]"
                              % (self.dev_name, command, high_byte, low_byte))

    def power_mode(self, channel, mode='NORMAL'):
        '''
        Puts the device in a specific power mode.

        Args:
            channel:   int, [0, 1, 2, 3), DAC Channel.
            mode:      string, ['NORMAL', '1K', '100K', '3_STATE'], Power mode of the device.

        '''
        mode = mode.upper()
        assert channel in [0, 1, 2, 3]
        assert mode in AD569XDef.POWER_MODE

        wr_data = 0
        channel_name = AD569XDef.CHANNEL_LIST[channel]
        pdx = 'PD' + channel_name[-1:]
        wr_data &= ~(AD569XDef.POWER_PDX[pdx]['MASK'])
        wr_data |= (AD569XDef.POWER_MODE[mode] << AD569XDef.POWER_PDX[pdx]['OFFSET'])
        self._recorder.record("%s power_mode: channel %s, mode %s"
                              % (self.dev_name, channel, mode))
        self._write_register(AD569XDef.COMMAND['POWE_RMODE'], wr_data)

    def soft_reset(self):
        '''
        Resets the device(clears the outputs to either zero scale or midscale).
        '''
        self._recorder.record("%s soft_reset")
        self._write_register(AD569XDef.COMMAND['SOFT_RESET'], 0)

    def select_vref_mode(self, vref_mode):
        '''
        Select internal or external voltage reference.

        Args:
            vref_mode:   string, ['INT_REF_ON', 'INT_REF_OFF'], Internal Reference On/Off.

        '''
        vref_mode = vref_mode.upper()
        assert vref_mode in AD569XDef.VREF_MODE
        self._recorder.record("%s select_vref_mode: vref_mode %s"
                              % (self.dev_name, vref_mode))
        self._write_register(AD569XDef.COMMAND['INT_REF_SETUP'], AD569XDef.VREF_MODE[vref_mode])

    def output_volt(self, channel, volt):
        '''
        Set the output voltage of the selected channel.

        Args:
            channel:   int, [0, 1, 2, 3), DAC Channel.
            volt:      int/float, [0~2500], Output voltage value.

        Returns:
            float, value, unit mV, the current voltage of specific channel.

        '''
        assert channel in [0, 1, 2, 3]
        assert isinstance(volt, (int, float)) and 0.0 <= volt <= (self.vref * self.gain)

        channel_name = AD569XDef.CHANNEL_LIST[channel]

        self._recorder.record("%s output_volt: channel %s, volt %f"
                              % (self.dev_name, channel_name, volt))

        command = AD569XDef.COMMAND['WR_UPDT_DAC_N'] + AD569XDef.ADDR_DAC[channel_name]
        # Calculate DAC code value to setup
        dac_value = int(volt * (0x1 << self.resolution) / (self.vref * self.gain))
        code = (dac_value << (16 - self.resolution)) & 0xffff
        self._write_register(command, code)

        # Calculate the voltage
        channel_volt = float(self.vref * self.gain * code) / (0x1 << self.resolution)
        return channel_volt

    def readback_volt(self, channel):
        '''
        Reads back the binary value written to one of the channels, and calculate the voltage.

        Args:
            channel:   int, [0, 1, 2, 3), DAC Channel.

        Returns:
            float, value, unit mV, the current voltage of specific channel.

        '''

        assert channel in [0, 1, 2, 3]

        channel_name = AD569XDef.CHANNEL_LIST[channel]

        self._recorder.record("%s read_volt: channel %s"
                              % (self.dev_name, channel_name))
        # Reads back the binary value
        rd_data = [0xFF, 0xFC]
        channel_value = (rd_data[0] << 8) | rd_data[1]
        channel_value >>= (16 - self.resolution)
        # Calculate the voltage
        channel_volt = float(self.vref * self.gain * channel_value - 1) / (0x1 << self.resolution)

        return channel_volt


class AD5694Emulator(AD569X):
    '''
    AD5694 Emulator class
    '''

    def __init__(self, dev_name):
        super(AD5694Emulator, self).__init__(dev_name)
        self.resolution = AD569XDef.AD5694_RESOLUTION
        self.gain = AD569XDef.GAIN_1


class AD5696Emulator(AD569X):
    '''
    AD5696 Emulator class
    '''

    def __init__(self, dev_name):
        super(AD5696Emulator, self).__init__(dev_name)
        self.resolution = AD569XDef.AD5696_RESOLUTION
        self.gain = AD569XDef.GAIN_1


class AD5694REmulator(AD569X):
    '''
    AD5694R Emulator class
    '''

    def __init__(self, dev_name):
        super(AD5694REmulator, self).__init__(dev_name)
        self.resolution = AD569XDef.AD5694R_RESOLUTION
        self.gain = AD569XDef.GAIN_1


class AD5695REmulator(AD569X):
    '''
    AD5695R Emulator class
    '''

    def __init__(self, dev_name):
        super(AD5695REmulator, self).__init__(dev_name)
        self.resolution = AD569XDef.AD5695R_RESOLUTION
        self.gain = AD569XDef.GAIN_1


class AD5696REmulator(AD569X):
    '''
    AD5696R Emulator class
    '''

    def __init__(self, dev_name):
        super(AD5696REmulator, self).__init__(dev_name)
        self.resolution = AD569XDef.AD5696R_RESOLUTION
        self.gain = AD569XDef.GAIN_1
