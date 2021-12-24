# -*- coding: utf-8 -*-
import time
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus

__author__ = "Zhangsong Deng"
__version__ = "1.0"


class MIXQIFSKLinkEncodeSGException(Exception):
    pass


class MIXQIFSKLinkEncodeSGDef:
    MODULE_EN_REGISTER = 0x10
    SEND_START_REGISTER = 0x12
    STATUS_REGISTER = 0x13
    DATA_FIFO_REGISTER = 0x20

    MODULE_ENABLE = 0x01
    SEND_START = 0x01
    STATUS_READY = 0x01
    TIMEOUT = 3000
    REG_SIZE = 256


class MIXQIFSKLinkEncodeSG(object):
    '''
    MIX QI Fsk link decode IP driver.

    ClassType = FSKEncode

    Args:
        axi4_bus:    instance(axi4_bus)/None,   used to access the IP register.

    '''
    def __init__(self, axi4_bus):
        if isinstance(axi4_bus, basestring):
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXQIFSKLinkEncodeSGDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus
        self._enable()

    def __del__(self):
        self._disable()

    def _enable(self):
        '''
         MIXQIFSKLinkEncodeSG IP enable function.
        '''
        reg_data = self.axi4_bus.read_8bit_inc(MIXQIFSKLinkEncodeSGDef.MODULE_EN_REGISTER, 1)[0]
        reg_data &= ~MIXQIFSKLinkEncodeSGDef.MODULE_ENABLE
        self.axi4_bus.write_8bit_inc(MIXQIFSKLinkEncodeSGDef.MODULE_EN_REGISTER,
                                     [reg_data])
        reg_data |= MIXQIFSKLinkEncodeSGDef.MODULE_ENABLE
        self.axi4_bus.write_8bit_inc(MIXQIFSKLinkEncodeSGDef.MODULE_EN_REGISTER, [reg_data])

    def _disable(self):
        '''
        MIXQIFSKLinkEncodeSG IP disable function.
        '''
        reg_data = self.axi4_bus.read_8bit_inc(MIXQIFSKLinkEncodeSGDef.MODULE_EN_REGISTER, 1)[0]
        reg_data &= ~MIXQIFSKLinkEncodeSGDef.MODULE_ENABLE
        self.axi4_bus.write_8bit_inc(MIXQIFSKLinkEncodeSGDef.MODULE_EN_REGISTER,
                                     [reg_data])

    def send_data(self, data):
        '''
        Send fsk data with checksum.

        Args:
            data:  list, the data to be send.

        '''
        assert len(data) > 0 and isinstance(data, list)
        self.axi4_bus.write_8bit_fix(MIXQIFSKLinkEncodeSGDef.DATA_FIFO_REGISTER, data)
        self.axi4_bus.write_8bit_inc(MIXQIFSKLinkEncodeSGDef.SEND_START_REGISTER,
                                     [MIXQIFSKLinkEncodeSGDef.SEND_START])
        start_time = time.time()
        while time.time() - start_time <= MIXQIFSKLinkEncodeSGDef.TIMEOUT:
            status = self.axi4_bus.read_8bit_inc(MIXQIFSKLinkEncodeSGDef.STATUS_REGISTER, 1)[0]
            if status & MIXQIFSKLinkEncodeSGDef.STATUS_READY == MIXQIFSKLinkEncodeSGDef.STATUS_READY:
                return
        raise MIXQIFSKLinkEncodeSGException("send data timeout!")
