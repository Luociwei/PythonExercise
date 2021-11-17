# -*- coding: utf-8 -*-
from ..tracer.recorder import *


class IIOXADCDef:
    SYS_PATH_IIO = '/sys/bus/iio/devices'
    TEMP_FILENAME = 'in_temp0_raw'
    READ_SIZE = 200
    TEMP_REFERENCE_LEVEL = 503.975
    TEMP_OFFSET = 273.15
    REFERENCE_LEVEL = 1000
    ADC_RESOLUTION = 4096

    TEMP_CHANNEL = 'temp'
    VPVN_CHANNEL = 'vpvn'
    VAUX0_CHANNEL = 'vaux0'
    VAUX1_CHANNEL = 'vaux1'
    VAUX2_CHANNEL = 'vaux2'
    VAUX3_CHANNEL = 'vaux3'
    VAUX4_CHANNEL = 'vaux4'
    VAUX5_CHANNEL = 'vaux5'
    VAUX6_CHANNEL = 'vaux6'
    VAUX7_CHANNEL = 'vaux7'
    VAUX8_CHANNEL = 'vaux8'
    VAUX9_CHANNEL = 'vaux9'
    VAUX10_CHANNEL = 'vaux10'
    VAUX11_CHANNEL = 'vaux11'
    VAUX12_CHANNEL = 'vaux12'
    VAUX13_CHANNEL = 'vaux13'
    VAUX14_CHANNEL = 'vaux14'
    VAUX15_CHANNEL = 'vaux15'
    ANALOG_IN_CHANNELS = [VPVN_CHANNEL, VAUX0_CHANNEL, VAUX1_CHANNEL, VAUX2_CHANNEL,
                          VAUX3_CHANNEL, VAUX4_CHANNEL, VAUX5_CHANNEL, VAUX6_CHANNEL,
                          VAUX7_CHANNEL, VAUX8_CHANNEL, VAUX9_CHANNEL, VAUX10_CHANNEL,
                          VAUX11_CHANNEL, VAUX12_CHANNEL, VAUX13_CHANNEL, VAUX14_CHANNEL,
                          VAUX15_CHANNEL]


class CHANNEL(object):
    '''
    The CHANNEL class record the xadc channel sysfs filename and conversion function

    :param filename:    string      the channel sysfs interface filename
    :param conv_func:   function    the xadc channel value conversion function
    '''

    def __init__(self, filename, conv_func):
        self.filename = filename
        self.conv_function = conv_func


class IIOXADC(object):
    '''
    XADC IIO decive API, support 17 analog input channels, need to use kernel driver

    :param device:     str,    xadc device name.
    :example:
                iioxadc = IIOXADC("iio:device0")
    '''

    def __init__(self, device):
        self.dev_name = device
        self._recorder = Recorder()
        add_recorder(self._recorder)
        self._init_channel_instance()

    def _init_channel_instance(self):
        self._recorder.record("init channel instance")

    def conv_temperature(self, value):
        temp = value * IIOXADCDef.TEMP_REFERENCE_LEVEL / IIOXADCDef.ADC_RESOLUTION - IIOXADCDef.TEMP_OFFSET
        self._recorder.record("conv temperature {} to {}".format(value, temp))

    def conv_voltage(self, value):
        voltage = value * IIOXADCDef.REFERENCE_LEVEL / IIOXADCDef.ADC_RESOLUTION
        self._recorder.record("conv voltage {} to {}".format(value, voltage))

    def get_value(self, channel, count=1):
        self._recorder.record("get {} channel {} value".format(count, channel))

    def get_temperature(self):
        self._recorder.record("get temperature")

    def read_volt(self, channel, count=1):
        assert channel in IIOXADCDef.ANALOG_IN_CHANNELS

        self._recorder.record("read {} channel {} value".format(count, channel))
