# -*- coding: utf-8 -*-
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus

__author__ = "Zhangsong Deng"
__version__ = "1.0"


class MIXQIASKLinkDecodeSGException(Exception):
    pass


class MIXQIASKLinkDecodeSGDef:
    MODULE_EN_REGISTER = 0x10
    DATA_LEN_REGISTER = 0x21
    DATA_FIFO_REGISTER = 0x20

    MODULE_ENABLE = 0x01
    REG_SIZE = 256


class MIXQIASKLinkDecodeSG(object):
    '''
    MIX QI Ask link decode IP driver.

    ClassType = ASKDecode

    Args:
        axi4_bus:    instance,   used to access the IP register.

    '''
    def __init__(self, axi4_bus):
        if isinstance(axi4_bus, basestring):
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXQIASKLinkDecodeSGDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus
        self._enable()

    def __del__(self):
        self._disable()

    def _enable(self):
        '''
         MIXQIASKLinkDecodeSG IP enable function.
        '''
        reg_data = self.axi4_bus.read_8bit_inc(MIXQIASKLinkDecodeSGDef.MODULE_EN_REGISTER, 1)[0]
        reg_data &= ~MIXQIASKLinkDecodeSGDef.MODULE_ENABLE
        self.axi4_bus.write_8bit_inc(MIXQIASKLinkDecodeSGDef.MODULE_EN_REGISTER,
                                     [reg_data])
        reg_data |= MIXQIASKLinkDecodeSGDef.MODULE_ENABLE
        self.axi4_bus.write_8bit_inc(MIXQIASKLinkDecodeSGDef.MODULE_EN_REGISTER, [reg_data])

    def _disable(self):
        '''
        MIXQIASKLinkDecodeSG IP disable function.
        '''
        reg_data = self.axi4_bus.read_8bit_inc(MIXQIASKLinkDecodeSGDef.MODULE_EN_REGISTER, 1)[0]
        reg_data &= ~MIXQIASKLinkDecodeSGDef.MODULE_ENABLE
        self.axi4_bus.write_8bit_inc(MIXQIASKLinkDecodeSGDef.MODULE_EN_REGISTER,
                                     [reg_data])

    def read_decode_data(self):
        '''
        Read decoded data from FIFO.

        Returns:
            list, the returned data list item is byte.

        '''
        rd_len = self.axi4_bus.read_16bit_inc(MIXQIASKLinkDecodeSGDef.DATA_LEN_REGISTER, 1)[0]
        if rd_len == 0:
            raise MIXQIASKLinkDecodeSGException("No data available in fifo.")

        return self.axi4_bus.read_8bit_fix(MIXQIASKLinkDecodeSGDef.DATA_FIFO_REGISTER, rd_len)
