# -*- coding: utf-8 -*-

from mix.driver.core.tracer.recorder import *


__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.1'


class MIXQIFSKLinkDecodeSGEmulator(object):
    '''
    MIX_QI_FSKLink_Decode_SG Driver
        Mainly used for wireless charging protocol QI, Fsk signal decode.

    ClassType = ASKDecode

    Args:
        axi4_bus:        instance(AXI4LiteBus)/None, axi4_lite_bus instance.

    Examples:
        fsk_decode = MIXQIFskLinkDecodeSG('/dev/AXI4_Fsk_Decode_SG_0')

        # Get Fsk Decode state
        state = fsk_decode.state()

        # Get Fsk Decode state
        data = fsk_decode.read_decode_data()

    '''

    def __init__(self, dev_name=None):
        if dev_name:
            self._dev_name = dev_name
        else:
            self._dev_name = "MIX_QI_FSKLink_Decode_SG"
        self._recorder = Recorder()
        add_recorder(self._recorder)

        self._enable()

    def __del__(self):
        self._disable()
        del_recorder(self._recorder)

    def _enable(self):
        '''
        MIXQIFSKLinkDecodeSG IP enable function.

        '''

        self._recorder.record(self._dev_name + " enable")

    def _disable(self):
        '''
        MIXQIFSKLinkDecodeSG IP disable function.

        '''

        self._recorder.record(self._dev_name + " disable")

    def state(self):
        '''
        Get FSK Decode state.

        '''
        self._recorder.record(self._dev_name + " state: state is True")
        return True

    def read_decode_data(self):
        '''
        Read FSK Decode data from fifo.

        Returns:
            list, [value], the returned data list item is byte.

        '''

        rd_data = [1, 2, 3]
        rd_len = 3

        self._recorder.record(self._dev_name + " read %d bytes" % (rd_len))
        return rd_data
