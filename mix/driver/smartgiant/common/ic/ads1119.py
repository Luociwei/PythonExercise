# -*- coding: utf-8 -*-
import time
from mix.driver.core.bus.i2c_bus_emulator import I2CBusEmulator

__author__ = 'yongjiu@SmartGiant'
__version__ = '0.2'


class ADS1119Def:
    # command for i2c communication
    RESET_COMMAND = 0x06
    START_COMMAND = 0x08
    POWERDOWN_COMMAND = 0x02
    RDATA_COMMAND = 0x10
    RREG_COMMAND = 0x20
    WREG_COMMAND = 0x40

    # register
    REGISTER0 = 0x20
    REGISTER1 = 0x24

    # register function fields
    DATA_READY_MASK = 0x80  # bit7
    CHANNEL_MUX_MASK = 0xE0  # [7:5]
    CHANNEL_MUX_OFFSET = 5

    SAMPLE_RATE_MASK = 0x0C  # [3:2]
    SAMPLE_RATE_OFFSET = 2
    SAMPLE_RATE = [20, 90, 330, 1000]
    SAMPLE_RATE_DEFAULT = 20

    REFERENCE_MODE_MASK = 1
    REFERENCE_MODE_OFFSET = 0
    REFERENCE_MODE = ["INTERNAL", "EXTERNAL"]

    GAIN_MODE_MASK = 0x10
    GAIN_MODE_OFFSET = 4
    GAIN_MODE = [1, 4]

    CONVERSION_MODE_MASK = 0x02  # bit1
    CONVERSION_MODE_OFFSET = 1
    SINGLE_MODE = 0
    CONTINUOUS_MODE = 1

    # hardware defined
    INTERNAL_REF_VOLTAGE = 2048.0
    CONVERSION_TIME = {
        # {sampling_rate: time}, sampling_rate`s unit is SPS, time`s unit is second
        20: 0.05001,
        90: 0.01129,
        330: 0.00307,
        1000: 0.00104
    }


class ADS1119Exception(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class ADS1119(object):
    '''
    ADS1119 function class

    ClassType = ADC

    Args:
        dev_addr:   hexmial,             ADS1119 i2c bus device address.
        i2c_bus:    instance(I2C)/None,  i2c bus class instance, if not using, will create emulator.
        ref_mode:   string, ["EXTERNAL", "INTERNAL"], defualt "INTERNAL", reference mode of ADS1119.
        mvref:      float, unit mV, default 2048.0, the internal reference voltage of ADS1119.
        gain:       int, default 1, the internal voltage gain mode of ADS1119.

    Examples:
        i2c_bus = I2C('/dev/i2c-0')
        ADS1119 = ADS1119(0x40, i2c_bus)

    '''
    rpc_public_api = ['init', 'read_volt', 'set_sampling_rate', 'get_sampling_rate']

    def __init__(self, dev_addr, i2c_bus=None, ref_mode="INTERNAL", mvref=ADS1119Def.INTERNAL_REF_VOLTAGE,
                 sampling_rate=ADS1119Def.SAMPLE_RATE_DEFAULT, gain=1):
        assert (dev_addr & (~0x03)) == 0x40

        self._dev_addr = dev_addr
        if i2c_bus is None:
            self.i2c_bus = I2CBusEmulator('ADS1119_emulator', 256)
        else:
            self.i2c_bus = i2c_bus

        self.ref_mode = ref_mode
        self.mvref = mvref
        self.gain = gain
        self.sampling_rate = sampling_rate

    def init(self):
        '''
        ADS1119 init

        Args:
            None.

        Examples:
            ads1119.init()

        '''
        self.i2c_bus.write(self._dev_addr, [ADS1119Def.RESET_COMMAND])
        self.set_reference(self.ref_mode)
        self.set_gain(self.gain)
        self.set_sampling_rate(self.sampling_rate)

    def set_reference(self, ref_mode="INTERNAL"):
        '''
        ADS1119 set mode of reference voltage

        Args:
            ref_mode:       string, ["INTERNAL,"EXTERNAL"], default is "INTERNAL"

        Examples:
                       ads1119.set_reference("EXTERNAL")
        '''
        assert ref_mode in ADS1119Def.REFERENCE_MODE

        self.ref_mode = ref_mode
        code = ADS1119Def.REFERENCE_MODE.index(self.ref_mode)
        register0 = self.i2c_bus.write_and_read(self._dev_addr, [ADS1119Def.REGISTER0], 1)[0]
        register0 = register0 & (~ADS1119Def.REFERENCE_MODE_MASK) | (code << ADS1119Def.REFERENCE_MODE_OFFSET)
        self.i2c_bus.write(self._dev_addr, [ADS1119Def.WREG_COMMAND, register0])

    def get_reference(self):
        '''
        ADS1119 get reference mode

        Args:
            None

        Returns:
            string, reference mode, "INTERNAL or "EXTERNAL"

        Examples:
            mode = ads1119.get_reference()
            print(mode)

        '''
        register0 = self.i2c_bus.write_and_read(self._dev_addr, [ADS1119Def.REGISTER0], 1)[0]
        code = (register0 & ADS1119Def.REFERENCE_MODE_MASK) >> ADS1119Def.REFERENCE_MODE_OFFSET
        return ADS1119Def.REFERENCE_MODE[code]

    def set_sampling_rate(self, rate):
        '''
        ADS1119 set sampling rate

        Args:
            rate:       int, [20,90,330,1000], unit SPS, sample rate value.

        Examples:
            ads1119.set_sampling_rate(90)

        '''
        assert isinstance(rate, int)
        assert rate in ADS1119Def.SAMPLE_RATE

        self.sampling_rate = rate

        code = ADS1119Def.SAMPLE_RATE.index(rate)
        register0 = self.i2c_bus.write_and_read(self._dev_addr, [ADS1119Def.REGISTER0], 1)[0]
        register0 = register0 & (~ADS1119Def.SAMPLE_RATE_MASK) | (code << ADS1119Def.SAMPLE_RATE_OFFSET)
        self.i2c_bus.write(self._dev_addr, [ADS1119Def.WREG_COMMAND, register0])

    def get_sampling_rate(self):
        '''
        ADS1119 set sampling rate

        Args:
            None

        Returns:
            int, sampling rate, value in [20, 90, 330, 1000], unit is SPS

        Examples:
            rate = ads1119.set_sampling_rate()
            print(rate)

        '''
        register0 = self.i2c_bus.write_and_read(self._dev_addr, [ADS1119Def.REGISTER0], 1)[0]
        sample_code = (register0 & ADS1119Def.SAMPLE_RATE_MASK) >> ADS1119Def.SAMPLE_RATE_OFFSET
        return ADS1119Def.SAMPLE_RATE[sample_code]

    def set_gain(self, gain):
        '''
        ADS1119 set gain mode

        Args:
            gain:       int, [1, 4], voltage gain mode.

        Examples:
            ads1119.set_gain(4)

        '''
        assert isinstance(gain, int)
        assert gain in ADS1119Def.GAIN_MODE

        self.gain = gain

        code = ADS1119Def.GAIN_MODE.index(gain)
        register0 = self.i2c_bus.write_and_read(self._dev_addr, [ADS1119Def.REGISTER0], 1)[0]
        register0 = register0 & (~ADS1119Def.GAIN_MODE_MASK) | (code << ADS1119Def.GAIN_MODE_OFFSET)
        self.i2c_bus.write(self._dev_addr, [ADS1119Def.WREG_COMMAND, register0])

    def get_gain(self):
        '''
        ADS1119 get gain mode

        Args:
            None

        Returns:
            int, voltage gain mode , value in [1, 4]

        Examples:
            mode = ads1119.get_gain()
            print(mode)

        '''
        register0 = self.i2c_bus.write_and_read(self._dev_addr, [ADS1119Def.REGISTER0], 1)[0]
        gain_code = (register0 & ADS1119Def.GAIN_MODE_MASK) >> ADS1119Def.GAIN_MODE_OFFSET
        return ADS1119Def.GAIN_MODE[gain_code]

    def enable_continuous_sampling(self):
        '''
        ADS1119 enable continuous sampling

        Examples:
            ads1119.enable_continuous_sampling(0)

        '''
        code = ADS1119Def.CONTINUOUS_MODE
        register0 = self.i2c_bus.write_and_read(self._dev_addr, [ADS1119Def.REGISTER0], 1)[0]
        register0 = register0 & (~ADS1119Def.CONVERSION_MODE_MASK) | (code << ADS1119Def.CONVERSION_MODE_OFFSET)
        self.i2c_bus.write(self._dev_addr, [ADS1119Def.WREG_COMMAND, register0])

    def disable_continuous_sampling(self):
        '''
        ADS1119 disable continuous sampling, that is set single sample mode.

        Examples:
            ads1119.disable_continuous_sampling()

        '''
        code = ADS1119Def.SINGLE_MODE
        register0 = self.i2c_bus.write_and_read(self._dev_addr, [ADS1119Def.REGISTER0], 1)[0]
        register0 = register0 & (~ADS1119Def.CONVERSION_MODE_MASK) | (code << ADS1119Def.CONVERSION_MODE_OFFSET)
        self.i2c_bus.write(self._dev_addr, [ADS1119Def.WREG_COMMAND, register0])

    def _start_conversion(self):
        self.i2c_bus.write(self._dev_addr, [ADS1119Def.START_COMMAND])

    def _is_conversion_ok(self):
        register1 = self.i2c_bus.write_and_read(self._dev_addr, [ADS1119Def.REGISTER1], 1)[0]
        status = True if (register1 & ADS1119Def.DATA_READY_MASK) != 0 else False
        return status

    def _read_volt(self):
        raw_data = self.i2c_bus.write_and_read(self._dev_addr, [ADS1119Def.RDATA_COMMAND], 2)

        # 16 bits, bipolar code
        code = raw_data[0] << 8 | raw_data[1]
        if code > pow(2, 15):
            code -= pow(2, 16)
        volt = code * self.mvref / float(pow(2, 15)) / self.gain

        return volt

    def _select_channel(self, channel):
        assert isinstance(channel, int)
        assert 0 <= channel and channel <= 7

        register0 = self.i2c_bus.write_and_read(self._dev_addr, [ADS1119Def.REGISTER0], 1)[0]
        register0 = register0 & (~ADS1119Def.CHANNEL_MUX_MASK) | (channel << ADS1119Def.CHANNEL_MUX_OFFSET)
        self.i2c_bus.write(self._dev_addr, [ADS1119Def.WREG_COMMAND, register0])

    def read_volt(self, channel):
        '''
        ADS1119 read voltage function

        Args:
            channel:    int, [0~7], 0 : AIN0-AIN1
                                    1 : AIN2-AIN3
                                    2 : AIN1-AIN2
                                    3 : AIN0-AGND
                                    4 : AIN1-AGND
                                    5 : AIN2-AGND
                                    6 : AIN3-AGND
                                    7 : AINP and AINN shorted to AVDD / 2

        Returns:
            float, voltage, unit is mV

        Examples:
            voltage = ADS1119.read_volt(0)
            print(voltage)

        '''
        assert isinstance(channel, int)
        assert 0 <= channel and channel <= 7

        self._select_channel(channel)
        self._start_conversion()

        time.sleep(ADS1119Def.CONVERSION_TIME[self.sampling_rate])

        if not self._is_conversion_ok():
            raise ADS1119Exception("Data conversion not ready!")

        return self._read_volt()
