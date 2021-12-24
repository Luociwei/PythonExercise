# -*- coding: utf-8 -*-
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator
from mix.driver.smartgiant.common.utility.data_operate import DataOperate

__author__ = 'zhiwei.deng@SmartGiant'
__version__ = '0.1'


class MIXAxiLiteToStreamSGDef:

    WRITE_WIDTH_IPCORE_ADDR = 0x0C
    READ_WIDTH_IPCORE_ADDR = 0x0D
    EMPTY_FIFO_NUMBER_IPCORE_ADDR = 0x10
    READ_FIFO_NUMBER_IPCORE_ADDR = 0x12
    WRITE_FIFO_IPCORE_ADDR = 0x14
    READ_FIFO_IPCORE_ADDR = 0x18
    REGISTER_SIZE = 256


class MIXAxiLiteToStreamSGException(Exception):

    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class MIXAxiLiteToStreamSG(object):
    '''
    MIXAxiLiteToStreamSG class provides a read/write interface for the stream bus.

    ClassType = MIXAxiLiteToStreamSG

    Args:
        axi4_bus: instance(AXI4LiteBus)/string/None,  AXI4 lite bus instance or device path;
                                                      If None, will create Emulator.

    Examples:
        mix_axil2s = MIXAxiLiteToStreamSG('/dev/MIX_AxiLiteToStream_0')

    '''

    rpc_public_api = ['write', 'read']

    def __init__(self, axi4_bus=None):

        if axi4_bus is None:
            self.axi4_bus = AXI4LiteBusEmulator(
                "mix_axilitetostream_sg_emulator", MIXAxiLiteToStreamSGDef.REGISTER_SIZE)
        elif isinstance(axi4_bus, basestring):
            # device path passed in; create axi4litebus here.
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXAxiLiteToStreamSGDef.REGISTER_SIZE)
        else:
            self.axi4_bus = axi4_bus
        self.__data_deal = DataOperate()

    def write(self, write_data):
        '''
        MIXAxiLiteToStreamSG write data to stream bus

        Args:
            data: list, Datas to be write.

        Examples:
            mix_axil2s.write([0x01, 0x02, 0x03, 0x04])
        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXAxiLiteToStreamSGDef.WRITE_WIDTH_IPCORE_ADDR, 1)
        bits_width = rd_data[0]
        if(len(write_data) % 4 > 0):
            raise MIXAxiLiteToStreamSGException('write data length error')

        i = int(len(write_data) / bits_width)
        wr_data_index = 0

        if bits_width == 1:
            axi4_bus_write = self.axi4_bus.write_8bit_fix
        elif bits_width == 2:
            axi4_bus_write = self.axi4_bus.write_16bit_fix
        else:
            axi4_bus_write = self.axi4_bus.write_32bit_fix

        write_data_list = []
        for temp in range(i):
            temp_data = write_data[bits_width * temp: bits_width * (temp + 1)]
            temp_data = self.__data_deal.list_2_int(temp_data)
            write_data_list.append(temp_data)

        while(i > 0):
            rd_data = self.axi4_bus.read_8bit_inc(MIXAxiLiteToStreamSGDef.EMPTY_FIFO_NUMBER_IPCORE_ADDR, 2)
            cache_deep = self.__data_deal.list_2_int(rd_data)
            if(cache_deep > i):
                send_cnt = i
            else:
                send_cnt = cache_deep - 3

            axi4_bus_write(MIXAxiLiteToStreamSGDef.WRITE_FIFO_IPCORE_ADDR, write_data_list[wr_data_index:send_cnt])
            wr_data_index += send_cnt
            i -= send_cnt

    def read(self):
        '''
        MIXAxiLiteToStreamSG read data from stream bus

        Returns:
            list, value.

        Examples:
            mix_axil2s.read()
        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXAxiLiteToStreamSGDef.READ_WIDTH_IPCORE_ADDR, 1)
        bits_width = rd_data[0]
        rd_data = self.axi4_bus.read_8bit_inc(MIXAxiLiteToStreamSGDef.READ_FIFO_NUMBER_IPCORE_ADDR, 2)
        cache_deep = self.__data_deal.list_2_int(rd_data)
        read_data = []
        if bits_width == 1:
            axi4_bus_read = self.axi4_bus.read_8bit_fix
        elif bits_width == 2:
            axi4_bus_read = self.axi4_bus.read_16bit_fix
        else:
            axi4_bus_read = self.axi4_bus.read_32bit_fix

        if cache_deep != 0:
            read_data = axi4_bus_read(MIXAxiLiteToStreamSGDef.READ_FIFO_IPCORE_ADDR, cache_deep)
            return read_data
        else:
            return None
