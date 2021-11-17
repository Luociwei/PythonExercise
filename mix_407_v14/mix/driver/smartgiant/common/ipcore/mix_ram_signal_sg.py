# -*- coding: UTF-8 -*-
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.utility.data_operate import DataOperate

__author__ = "dongdong.zhang@SmartGiant"
__version__ = "0.0.1"


class MIXRamSignalSGDef:
    ENABLE_REGISTER = 0x10
    READ_END_ADDR_REGISTER = 0x11
    READ_ENABLE_REGISTER = 0x13
    WRITE_DATA_REGISTER = 0x14
    WRITE_END_ADDR_REGISTER = 0x18
    REG_SIZE = 256
    NUM_OF_REPEATS = 0x1c


class MIXRamSignalSGException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class MIXRamSignalSG(object):

    def __init__(self, axi4_bus=None):
        if axi4_bus:
            if isinstance(axi4_bus, basestring):
                self.axi4_bus = AXI4LiteBus(axi4_bus, MIXRamSignalSGDef.REG_SIZE)
            else:
                self.axi4_bus = axi4_bus
        else:
            raise MIXRamSignalSGException("parameter 'axi4_bus' can not be None")

        self.enable()

    def enable(self):
        '''
        enable the module.
        '''
        self.axi4_bus.write_8bit_inc(MIXRamSignalSGDef.ENABLE_REGISTER, [0x01])

    def disable(self):
        '''
        disable the module, zeroing out the READ/write address of RAM, but does not empty the RAM data.
        '''
        self.axi4_bus.write_8bit_inc(MIXRamSignalSGDef.ENABLE_REGISTER, [0x00])

    def read_enable(self):
        '''
        Read enable of RAM.
        '''
        self.axi4_bus.write_8bit_inc(MIXRamSignalSGDef.READ_ENABLE_REGISTER, [0x01])

    def read_disable(self):
        '''
        Turn off RAM read enable, read address reset, RAM output 0.
        '''
        self.axi4_bus.write_8bit_inc(MIXRamSignalSGDef.READ_ENABLE_REGISTER, [0x00])

    def set_read_ramend_addr(self, address):
        '''
        Set the end address for cyclic READ RAM.

        Args:
            address:   int, the end address for cyclic READ RAM.
        '''
        wr_data = DataOperate.int_2_list(int(address), 2)
        self.axi4_bus.write_8bit_inc(MIXRamSignalSGDef.READ_END_ADDR_REGISTER, wr_data)

    def get_read_ramend_addr(self):
        '''
        Get the end address of RAM.

        Returns:
            int, the end address of RAM.
        '''
        wr_data = self.axi4_bus.read_16bit_inc(MIXRamSignalSGDef.READ_END_ADDR_REGISTER, 1)
        return wr_data[0]

    def get_write_ramend_addr(self):
        '''
        Get the last write address to determine if it is correct.

        Returns:
            int, the last write address.
        '''
        rd_data = self.axi4_bus.read_16bit_inc(MIXRamSignalSGDef.WRITE_END_ADDR_REGISTER, 1)
        return rd_data[0]

    def set_tx_data(self, wr_data):
        '''
        Write the list of audio data to RAM.

        Args:
            wr_data:   list, Write data.
        '''
        self.axi4_bus.write_32bit_fix(MIXRamSignalSGDef.WRITE_DATA_REGISTER, wr_data)

    def set_number_of_repeats(self, n):
        '''
        set repeats number.

        Args:
            n:   int, repeats number.
        '''
        rd_data = self.axi4_bus.write_32bit_inc(MIXRamSignalSGDef.NUM_OF_REPEATS, n)
