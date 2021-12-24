# -*- coding: utf-8 -*-

from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus


__author__ = 'shunreng.he@SmartGiant'
__version__ = '0.1'


class MIXMacFCTSpiReturnSGDef:
    CONFIG_REGISTER = 0x10
    SPI_MODE = 0x11
    REG_SIZE = 256
    CLK_FREQUENCY = 125000000


class MIXMacFCTSpiReturnSGException(Exception):
    def __init__(self, dev_name, err_str):
        self._err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self._err_reason


class MIXMacFCTSpiReturnSG(object):
    '''
    MIXMacFctSpiReturnSG class provide function to open close and set mode

    MIXMacFctSpiReturnSG can return what data received

    ClassType = MIXMacFCTSpiReturnSG

    Args:
        axi4_bus:  axi4_bus: instance(AXI4LiteBus)/string/None, AXI4 lite bus instance or device path;
                                                                If None, will create Emulator.

    Examples:
        spi_return = MIXMacFctSpiReturn('/dev/MIX_MacFCT_SpiReturn_SG_0')
        spi_return.open()
        spi_return.set_mode(0)
    '''
    rpc_public_api = ['open', 'close', 'set_mode']

    def __init__(self, axi4_bus):
        if isinstance(axi4_bus, basestring):
            # create axi4lite bus from given device path
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXMacFCTSpiReturnSGDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        self.open()

    def open(self):
        '''
        MIXMacFctSpiReturnSG open function

        Examples:
            spi_return.open()
        '''
        self.axi4_bus.write_8bit_inc(MIXMacFCTSpiReturnSGDef.CONFIG_REGISTER, [0x00])
        self.axi4_bus.write_8bit_inc(MIXMacFCTSpiReturnSGDef.CONFIG_REGISTER, [0x01])

    def close(self):
        '''
        MIXMacFctSpiReturnSG close function

        Examples:
            spi_return.close()
        '''
        self.axi4_bus.write_8bit_inc(MIXMacFCTSpiReturnSGDef.CONFIG_REGISTER, [0x00])

    def set_mode(self, mode):
        '''
        MIXMacFctSpiReturnSG set mode

        Args:
            mode:            int,[0, 1, 2, 3], 0:CPOL=0,CPHA=0;
                                               1:CPOL=1,CPHA=0;
                                               2:CPOL=0,CPHA=1;
                                               3:CPOL=1,CPHA=1.

        Examples:
            spi_return.set_mode(0)
        '''
        self.axi4_bus.write_8bit_inc(MIXMacFCTSpiReturnSGDef.SPI_MODE, [mode])
