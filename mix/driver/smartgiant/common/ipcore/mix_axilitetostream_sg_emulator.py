# -*- coding: utf-8 -*-

from mix.driver.core.tracer.recorder import *


__author__ = 'zhiwei.deng@SmartGiant'
__version__ = '0.1'


class MIXAxiLiteToStreamSGEmulator(object):
    '''
    MIXAxiLiteToStreamSG class provides a read/write interface for the stream bus.

    ClassType = MIXAxiLiteToStreamSG

    Args:
        axi4_bus: instance(AXI4LiteBus)/string/None,  AXI4 lite bus instance or device path;
                                                      If None, will create Emulator.

    Examples:
        mix_axil2s = MIXAxiLiteToStreamSG('/dev/MIX_AxiLiteToStream_0')

    '''

    def __init__(self, axi4_bus=None):
        if axi4_bus:
            self.axi4_bus = axi4_bus
        else:
            self.axi4_bus = "MIX_AxiLiteToStream"
        self.recorder = Recorder()
        add_recorder(self.recorder)

    def write(self, write_data):
        '''
        MIXAxiLiteToStreamSG write data to stream bus

        Args:
            data: list, Datas to be write.

        Examples:
            mix_axil2s.write([0x01, 0x02, 0x03, 0x04])
        '''
        self.recorder.record("%s write %s" % (self.axi4_bus, write_data))
        return True

    def read(self):
        '''
        MIXAxiLiteToStreamSG read data from stream bus

        Returns:
            list, value.

        Examples:
            mix_axil2s.read()
        '''
        rd_data = [1, 2, 3, 4]
        rd_len = 4

        self.recorder.record(self.axi4_bus + " read %d bytes %s" % (rd_len, rd_data))
        return rd_data
