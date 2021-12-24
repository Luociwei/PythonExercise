# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class ADS1115Def:
    CONVERSION_REGISTER = 0x00
    CONFIG_REGISTER = 0x01
    LO_THRESH_REGISTER = 0x02
    HI_THRESH_REGISTER = 0x03

    OS_MASK = 0x8000
    OS_SIGNAL_CONVERSION = 0x8000
    OS_CONV_COMPLETED = 0x8000

    MUX_OFFSET = 12
    MUX_MASK = (0x07 << MUX_OFFSET)

    FS_OFFSET = 9
    FS_MASK = (0x07 << FS_OFFSET)

    MODE_OFFSET = 8
    MODE_MASK = (1 << MODE_OFFSET)
    MODE_CONTI_CONV = (0 << MODE_OFFSET)
    MODE_SIGNLE_CONV = (1 << MODE_OFFSET)

    DATA_RATE_OFFSET = 5
    DATA_RATE_MASK = (0x07 << DATA_RATE_OFFSET)

    COMP_MODE_OFFSET = 4
    COMP_MODE_MASK = (1 << COMP_MODE_OFFSET)

    COMP_POL_OFFSET = 3
    COMP_POL_MASK = (1 << COMP_POL_OFFSET)

    COMP_LAT_OFFSET = 2
    COMP_LAT_MASK = (1 << COMP_LAT_OFFSET)

    COMP_QUE_OFFSET = 0
    COMP_QUE_MASK = (0x03 << COMP_QUE_OFFSET)

    CONFIG_DEFAULT_VALUE = 0x8583

    RATES = [
        8, 16, 32, 64, 128, 250, 475, 860
    ]

    FS = {
        'fs0': {'config': 0x00, 'mvref': 6144},
        'fs1': {'config': 0x01, 'mvref': 4096},
        'fs2': {'config': 0x02, 'mvref': 2048},
        'fs3': {'config': 0x03, 'mvref': 1024},
        'fs4': {'config': 0x04, 'mvref': 512},
        'fs5': {'config': 0x05, 'mvref': 256},
        'fs6': {'config': 0x06, 'mvref': 256},
        'fs7': {'config': 0x07, 'mvref': 256}
    }

    DEFAULT_TIMEOUT = 0.250
    DEFAULT_DELAY = 0.001


class ADS1115Emulator(object):
    '''
    ADS1115Emulator function class

    Args:
        dev_name:    Instance(I2C)/None,      i2c bus class instance, if not using, will create emulator
        fs:          string('fs0'-'fs7'),     full scale input config

    Examples:
                axi4_bus = AXI4LiteBus('/dev/MIX_DUT_I2C_0', 256)
                i2c_bus = MIXI2CSG(axi4_bus)
                ads1115 = ADS1115(0x48, i2c_bus, 'fs0')
    '''

    def __init__(self, dev_name, fs='fs0'):
        assert fs in ADS1115Def.FS.keys()
        self._dev_addr = 0x48
        self.fs = fs
        self.mvref = ADS1115Def.FS[fs]['mvref']
        self.rate = 16
        self._dev_name = dev_name
        self._recorder = Recorder()
        add_recorder(self._recorder)

    def write_register(self, addr, value):
        '''
        ADS1115 write register function

        Args:
            addr:   hexmial(0-0xff),    register address.
            value:  hexmial(0-0xffff),  value to be write to register.
        Examples:
            ads1115._write_register(0x01, 0xff0)
        '''
        high_byte = (value >> 8) & 0xFF
        low_byte = value & 0xFF
        self._recorder.record("%s write_register: [0x%02x, 0x%02x, 0x%02x]"
                              % (self._dev_addr, addr, high_byte, low_byte))

    def read_register(self, addr):
        '''
        ADS1115 read register function

        Args:
            addr:   hexmial(0-0xff),    register address.
        Exmaples:
            data = ads1115._read_register(0x00)
            print(data)
        '''

        self._recorder.record("{}.read_register({})".format(self._dev_name, addr))
        return True

    def set_sampling_rate(self, channel, rate):
        '''
        ADS1115 set sampling rate

        Args:
            channel:    int(0~7),   adc channel index.
            rate:       int(8, 16, 32, 64, 128, 250, 475, 860), sample rate value.

        :Examples:
                ads1115.set_sampling_rate(0, 128)
        '''
        assert rate in ADS1115Def.RATES
        self.rate = rate
        self._recorder.record("{}.set_sampling_rate({})".format(self._dev_name, self.rate))

    def get_sampling_rate(self, channel):
        '''
        ADS1115 get sampling rate

             channel:    int(0-7),   adc channel index
        :Examples:
                    rete = ads1115.set_sampling_rate(0)
                    print(rate)
        '''
        assert 0 <= channel < 8
        self._recorder.record("{}.get_sampling_rate({})".format(self._dev_name, self.rate))
        return self.rate

    def read_volt(self, channel):
        '''
        ADS1115 read voltage function

        Args:
            channel:    int (0/1..),    0 mean '0_1',
                                        1 mean '0_3',
                                        2 mean '1_3',
                                        3 mean '2_3',
                                        4 mean '0_G',
                                        5 mean '1_G',
                                        6 mean '2_G',
                                        7 mean '3_G'
        Examples:
                data = ads1115.read_volt(0)
                print(data)
        '''
        assert 0 <= channel < 8
        self._recorder.record("{}.read_volt({})".format(self._dev_name, channel))
        return True
