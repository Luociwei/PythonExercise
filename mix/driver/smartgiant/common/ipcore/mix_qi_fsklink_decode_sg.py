# -*- coding: utf-8 -*-

from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus

__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.1'


class MIXQIFSKLinkDecodeSGDef:
    # register address
    MODULE_EN_REGISTER = 0x10
    STATE_REGISTER = 0x12
    DATA_FIFO_REGISTER = 0x20
    DATA_LEN_REGISTER = 0x21

    # register enable
    MODULE_ENABLE = 0x01
    STATE_OK = 0x01
    REG_SIZE = 256


class MIXQIFSKLinkDecodeSGException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class MIXQIFSKLinkDecodeSG(object):
    '''
    MIX_QI_FSKLink_Decode_SG Driver

    Mainly used for wireless charging protocol QI, Fsk signal decode.

    ClassType = FSKDecode

    Args:
        axi4_bus:        instance(AXI4LiteBus)/None, axi4_lite_bus instance.

    Examples:
        fsk_decode = MIXQIFSKLinkDecodeSG('/dev/MIX_QI_FSKLink_Decode_SG_0')

        # Get Fsk Decode state
        state = fsk_decode.state()

        # Get Fsk Decode state
        data = fsk_decode.read_decode_data()

    '''

    rpc_public_api = ['state', 'read_decode_data']

    def __init__(self, axi4_bus=None):
        if isinstance(axi4_bus, basestring):
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXQIFSKLinkDecodeSGDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        self._enable()

    def __del__(self):
        self._disable()

    def _enable(self):
        '''
         MIXQIFSKLinkDecodeSG IP enable function.
        '''
        reg_data = self.axi4_bus.read_8bit_inc(MIXQIFSKLinkDecodeSGDef.MODULE_EN_REGISTER, 1)[0]
        reg_data &= ~MIXQIFSKLinkDecodeSGDef.MODULE_ENABLE
        self.axi4_bus.write_8bit_inc(MIXQIFSKLinkDecodeSGDef.MODULE_EN_REGISTER,
                                     [reg_data])
        reg_data |= MIXQIFSKLinkDecodeSGDef.MODULE_ENABLE
        self.axi4_bus.write_8bit_inc(MIXQIFSKLinkDecodeSGDef.MODULE_EN_REGISTER, [reg_data])

    def _disable(self):
        '''
        MIXQIFSKLinkDecodeSG IP disable function.
        '''
        reg_data = self.axi4_bus.read_8bit_inc(MIXQIFSKLinkDecodeSGDef.MODULE_EN_REGISTER, 1)[0]
        reg_data &= ~MIXQIFSKLinkDecodeSGDef.MODULE_ENABLE
        self.axi4_bus.write_8bit_inc(MIXQIFSKLinkDecodeSGDef.MODULE_EN_REGISTER,
                                     [reg_data])

    def state(self):
        '''
        Get Fsk Decode state value.

        Returns:
            boolean, [True, False], state value.
                                    True: Fsk decode Parity bit is ok,
                                    False: Fsk decode Parity bit is error.

        '''

        rd_data = self.axi4_bus.read_8bit_inc(MIXQIFSKLinkDecodeSGDef.STATE_REGISTER, 1)[0]
        if rd_data == MIXQIFSKLinkDecodeSGDef.STATE_OK:
            return True
        else:
            return False

    def read_decode_data(self):
        '''
        Read Fsk Decode data from fifo.

        Returns:
            list, [value], the returned data list item is byte.

        '''

        rd_len = self.axi4_bus.read_16bit_inc(MIXQIFSKLinkDecodeSGDef.DATA_LEN_REGISTER, 1)[0]
        if rd_len == 0:
            raise MIXQIFSKLinkDecodeSGException("No data available in fifo.")

        return self.axi4_bus.read_8bit_fix(MIXQIFSKLinkDecodeSGDef.DATA_FIFO_REGISTER, rd_len)
