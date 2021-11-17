# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *

__author__ = 'ZiCheng.Huang@SmartGiant'
__version__ = '0.1'


class AD56X9RDef:

    COMMAND_WRITE_TO_INPUT_REG = 0x00
    COMMAND_UPDATE_DAC_REG = 0x01
    COMMAND_WRITE_TO_INPUT_REG_AND_UPDATE_ALL = 0x02
    COMMAND_WRITE_AND_UPDATE_DAC_CHAN = 0x03
    COMMAND_POWER_UP_OR_DOWN = 0x04
    COMMAND_LOAD_CLEAR_CODE_REG = 0x05
    COMMAND_LDAC_SETUP = 0x06
    COMMAND_RESET = 0x07
    COMMAND_INTERNAL_REFERENCE_REG = 0x08
    COMMAND_MULTIPLE_BYTE_MODE_REG = 0x09

    AD5669R_RESOLUTION = 16
    AD5629R_RES0LUTION = 12

    CHANNEL_A = 0x01
    CHANNEL_B = 0x02
    CHANNEL_C = 0x03
    CHANNEL_D = 0x04
    CHANNEL_E = 0x05
    CHANNEL_F = 0x06
    CHANNEL_G = 0x07
    CHANNEL_H = 0x08
    CHANNEL_ALL = 0xff


class AD56X9RException(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class AD56X9REmulator(object):
    '''
    AD56X9R function class

    Args:
        dev_addr:   int,                 bit i2c device address.
        i2c_bus:    instance(I2C)/None,  created using I2CBus, which is used to access AD56X9R internal register.
        mvref:      float/int, unit mV, default 2500.0, the reference voltage of AD56X9R.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        ad56x9r = AD56X9R(0x50, i2c)

    '''

    def __init__(self, dev_name):
        # 7-bit slave address. The two LSBs are variable
        self.dev_name = dev_name
        self._recorder = Recorder()
        add_recorder(self._recorder)

    def __del__(self):
        del_recorder(self._recorder)

    def initialization(self):
        self._recorder.record("initial the DAC")

    def output_volt_dc(self, channel, volt):
        '''
        AD56X9R output voltage

        Args:
            channel:  int, [0, 1, 2, 3, 4, 5, 6, 7, 0xff], channel index to enable ldac pin, 0xff mean all channel.
            volt:     float/int, unit mV, DAC output voltage.

        Examples:
            ad56x9r.output_volt_dc(1, 1000)

        '''
        self._recorder.record("set channel voltage")


class AD5629REmulator(AD56X9REmulator):
    '''
    AD5629R function class

    Args:
        dev_addr:   int,                 bit i2c device address.
        i2c_bus:    Instance(I2C)/None,  created using I2CBus, which is used to access AD5629R internal register.
        ref_mode:   string, ["extern", "internal"], default "extern",  reference mode of AD5629R.
        mvref:      float/int, unit mV, default 2500.0, the reference voltage of AD5629R.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        ad5629r = AD5629R(0x50, i2c)

    '''

    def __init__(self, dev_name):
        super(AD5629REmulator, self).__init__(dev_name)
        self.resolution = AD56X9RDef.AD5629R_RES0LUTION


class AD5669REmulator(AD56X9REmulator):
    '''
    AD5669R function class

    Args:
        dev_addr:   int,                 bit i2c device address.
        i2c_bus:    Instance(I2C)/None,  created using I2CBus, which is used to access AD5669R internal register.
        mvref:      float/int, unit mV, default 2500.0, the reference voltage of AD5669R.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        ad5669r = AD5669R(0x50, i2c)

    '''

    def __init__(self, dev_name):
        super(AD5669REmulator, self).__init__(dev_name)
        self.resolution = AD56X9RDef.AD5627_RESLUTION
