# -*- coding: UTF-8 -*-
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus

__author__ = "dongdong.zhang@SmartGiant"
__version__ = "0.0.1"


class MIXAudioCacheSGDef:
    ENABLE_REGISTER = 0x10
    WRITE_CACHE_ENABLE_REGISTER = 0x11
    READ_NUMBER_REGISTER = 0x12
    AUDIO_LEFT_DATA_REGISTER = 0x20
    AUDIO_RIGHT_DATA_REGISTER = 0x24
    REG_SIZE = 256


class MIXAudioCacheSGException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class MIXAudioCacheSG(object):

    def __init__(self, axi4_bus=None):
        if axi4_bus:
            if isinstance(axi4_bus, basestring):
                self.axi4_bus = AXI4LiteBus(axi4_bus, MIXAudioCacheSGDef.REG_SIZE)
            else:
                self.axi4_bus = axi4_bus
        else:
            raise MIXAudioCacheSGException("parameter 'axi4_bus' can not be None")

        self.enable()

    def enable(self):
        '''
        enable the module.
        '''
        self.axi4_bus.write_8bit_inc(MIXAudioCacheSGDef.ENABLE_REGISTER, [0x01])

    def disable(self):
        '''
        disable the module.
        '''
        self.axi4_bus.write_8bit_inc(MIXAudioCacheSGDef.ENABLE_REGISTER, [0x00])

    def cache_enable(self):
        '''
        Audio data write cache enablement.
        '''
        self.axi4_bus.write_8bit_inc(MIXAudioCacheSGDef.WRITE_CACHE_ENABLE_REGISTER, [0x01])

    def cache_disable(self):
        '''
        Audio data write cache disablement.
        '''
        self.axi4_bus.write_8bit_inc(MIXAudioCacheSGDef.WRITE_CACHE_ENABLE_REGISTER, [0x00])

    def get_data_number(self):
        '''
        Get the maximum amount of data that can be read.

        Returns:
            int, the maximum amount of data.
        '''
        get_data = self.axi4_bus.read_16bit_inc(MIXAudioCacheSGDef.READ_NUMBER_REGISTER, 1)
        return get_data[0]

    def get_left_data(self, number):
        '''
        Get audio left channel data.

        Args:
            number:   int, The number of voltage points.

        Returns:
            list, voltage points.
        '''
        get_data = self.axi4_bus.read_32bit_fix(MIXAudioCacheSGDef.AUDIO_LEFT_DATA_REGISTER, number)
        return get_data

    def get_right_data(self, number):
        '''
        Get audio right channel data.

        Args:
            number:   int, The number of voltage points.

        Returns:
            list, voltage points.
        '''
        get_data = self.axi4_bus.read_32bit_fix(MIXAudioCacheSGDef.AUDIO_RIGHT_DATA_REGISTER, number)
        return get_data

    def get_cache_status(self):
        '''
        Get the FIFO storage state and determine whether the FIFO is full.

        Returns:
            int, [0x00, 0x01], 0x00: FIFO is not full; 0x01: FIFO is full.
        '''
        get_data = self.axi4_bus.read_8bit_fix(MIXAudioCacheSGDef.WRITE_CACHE_ENABLE_REGISTER, 1)
        status = get_data[0] >> 7
        return status
