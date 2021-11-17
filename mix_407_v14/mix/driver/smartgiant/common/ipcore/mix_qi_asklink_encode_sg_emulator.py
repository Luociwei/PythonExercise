# -*- coding: utf-8 -*-

from mix.driver.core.tracer.recorder import *


__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.1'


class MIXQIASKLinkEncodeSGEmulator(object):
    '''
    MIX_QI_ASKLink_Encode_SG Driver
        Mainly used for wireless charging protocol QI, generating Ask signal
        (square wave).

    ClassType = ASKEncode

    Args:
        xi4_bus:     instance(AXI4LiteBus), axi4_lite_bus instance.

    Examples:
        ask_code = MIXQIAskLinkEncodeSG('/dev/MIX_QI_ASKLink_Encode_SG')

        # Set Ask signal frequency
        ask_code.set_frequency(2000)

        # Send Ask signal
        wr_data = [1,2,3]
        ask_code.write_encode_data(wr_data)

    '''

    def __init__(self, dev_name=None):
        if dev_name:
            self._dev_name = dev_name
        else:
            self._dev_name = "MIX_QI_ASKLink_Encode_SG"
        self._recorder = Recorder()
        add_recorder(self._recorder)

        self._enable()

    def __del__(self):
        self._disable()
        del_recorder(self._recorder)

    def _enable(self):
        '''
        MIXQIASKLinkEncodeSG IP enable function.

        '''

        self._recorder.record(self._dev_name + " enable")

    def _disable(self):
        '''
        MIXQIASKLinkEncodeSG IP disable function.

        '''

        self._recorder.record(self._dev_name + " disable")

    def set_frequency(self, freq):
        '''
        Set the Ask signal frequency.

        Args:
            freq:  int, [100~100000], unit Hz, 2000 means 2000Hz.

        '''
        assert isinstance(freq, int)
        assert 100 <= freq <= 100000

        self._recorder.record(self._dev_name + " set_frequency: freq is %r" % freq)

    def write_encode_data(self, wr_data):
        '''
        Write Ask encoded signal data (square wave) to FIFO.

        Args:
            wr_data:      list, Data to write, the list item is byte.

        Raises:
            MIXQIASKLinkEncodeSGException:    Waiting for the ipcore state timeout.

        '''
        assert isinstance(wr_data, list) and len(wr_data) > 0

        record_data = "["
        for i in range(len(wr_data)):
            record_data += "0x%02x" % (wr_data[i])
            if i != len(wr_data) - 1:
                record_data += ", "
        record_data += "]"
        self._recorder.record(self._dev_name + " write_encode_data " + str(record_data))
