# -*- coding: utf-8 -*-
import ctypes
from mix.driver.smartgiant.common.bus.ft4222 import FT4222


__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1'


class FTSPIException(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class FTSPIDef:
    IOLINES = {
        'SPI': 1,
        'DSPI': 2,
        'QSPI': 4
    }

    SPEEDS = {
        2: 1,
        4: 2,
        8: 3,
        16: 4,
        32: 5,
        64: 6,
        128: 7,
        256: 8,
        512: 9
    }

    MODES = {
        # CPOL=0, CPHA=0
        'MODE0': [0, 0],
        # CPOL=0, CPHA=1
        'MODE1': [0, 1],
        # CPOL=1, CPHA=0
        'MODE2': [1, 0],
        # CPOL=1, CPHA=1
        'MODE3': [1, 1]
    }

    SSOMAP = {
        'SS0O': 0X01,
        'SS1O': 0X02,
        'SS2O': 0X04,
        'SS3O': 0X08
    }


class FTSPI(object):

    # class variable to host all FT4222 instances created.
    instances = {}

    def __new__(cls, ft4222=None, ioline='SPI', speed=64, mode='MODE3', ssomap='SS0O'):
        if ft4222 in cls.instances:
            # use existing instance
            pass
        else:
            # create a new one
            instance = _FTSPI(ft4222, ioline, speed, mode, ssomap)
            cls.instances[ft4222] = instance
        return cls.instances[ft4222]


class _FTSPI(object):
    '''
    FTSPIBus function class. This driver can be used to drive xilinx spi bus.

    Args:
        ft4222:      instance/None/string/int,  Class instance of FT4222 bus or locid of FT4222 device.
        ioline:      string, ['SPI', 'DSPI', 'QSPI'], spi line number mode.
        speed:       int, [2, 4, 8, 16, 32, 64, 128, 256, 512],  FTSPI clock speed, 1/speed System Clock.
        mode:        string, ['MODE0', 'MODE1', 'MODE2', 'MODE3'],  FTSPI clock Polarity and clock Phase.
        ssomap:      string, ['SS0O', 'SS1O', 'SS2O', 'SS3O'],  FTSPI slave selection output pins bitmap.

    Examples:

        ft4222 = FT4222('4593')
        ft_spi = FTSPI(ft4222, ioline='SPI', speed=64, ssomap='SS0O')

    '''

    def __init__(self, ft4222=None, ioline='SPI', speed=64, mode='MODE3', ssomap='SS0O'):
        if ft4222 is None:
            self._ft_4222 = FT4222(None)
        elif isinstance(ft4222, (int, basestring)):
            self._ft_4222 = FT4222(ft4222)
        else:
            self._ft_4222 = ft4222

        self._base_lib = self._ft_4222._base_lib
        self._fthandle = self._ft_4222._fthandle
        self._ioline = FTSPIDef.IOLINES[ioline]
        self._speed = FTSPIDef.SPEEDS[speed]
        self._clockpolarity = FTSPIDef.MODES[mode][0]
        self._clockphase = FTSPIDef.MODES[mode][1]
        self._ssomap = FTSPIDef.SSOMAP[ssomap]

    def get_mode(self):
        '''
        FTSPIBus get CPOL and CPHA mode

        Examples:
            mode = ftspi.get_mode()
            print(mode)
        '''
        for key in FTSPIDef.MODES.keys():
            if FTSPIDef.MODES[key][0] == self._clockpolarity and FTSPIDef.MODES[key][1] == self._clockphase:
                return key
        return 'none'

    def set_mode(self, mode):
        '''
        PLFTSPIBus set CPOL and CPHA mode

        Args:
            mode:   string, ['MODE0', 'MODE1', 'MODE2', 'MODE3'], CPOL and CPHA mode

        Examples:
            ftspi.set_mode(mode)
        '''
        assert mode in ['MODE0', 'MODE1', 'MODE2', 'MODE3']

        self._clockpolarity = FTSPIDef.MODES[mode][0]
        self._clockphase = FTSPIDef.MODES[mode][1]

    def get_speed(self):
        '''
        FTSPIBus get transmition speed

        Examples:
            speed = ftspi.get_speed()
            print(speed)
        '''

        return self._speed

    def set_speed(self, speed):
        '''
        FTSPIBus set transmit speed

        Args:
             speed:  int, spi transmition speed

        Examples:
            ftspi.set_speed(speed)
        '''
        assert speed in [2, 4, 8, 16, 32, 64, 128, 512]

        self._speed = speed

    def config_protocol(self, mode):
        '''
        Config spi protocol mode. Now ftspi bus driver support SPI/QPI mode.

        Args:
            mode:     string('SPI','DSPI','QSPI'),       spi bus work mode.

        Examples:
            # Example for config ftspi bus to 'SPI' mode.
            ftspi = FTSPIBus('0')
            ftspi.config_protocol('SPI')

        '''
        assert mode in ['SPI', 'DSPI', 'QSPI']

        self._ioline = FTSPIDef.IOLINES[mode]

    def write(self, wr_data):
        '''
        FTSPIBus write data function

        Args:
            wr_data:    list,       Datas to be write

        Examples:
            ftspi.write([1, 2, 3])
        '''
        assert len(wr_data) > 0

        self._ft_4222.open()
        data = (ctypes.c_ubyte * len(wr_data))()
        for i in range(len(wr_data)):
            data[i] = wr_data[i]

        ftstatus = self._base_lib.FT4222_SPIMaster_Init(self._fthandle, self._ioline, self._speed,
                                                        self._clockpolarity, self._clockphase, self._ssomap)
        if ftstatus != 0:
            raise FTSPIException('FT4222_SPIMaster_Init')

        byteswritten = ctypes.c_uint16(0)
        sizetransferred = ctypes.c_bool(1)
        ftstatus = self._base_lib.FT4222_SPIMaster_SingleWrite(self._fthandle, data, len(wr_data),
                                                               ctypes.byref(byteswritten), sizetransferred)
        if ftstatus != 0:
            raise FTSPIException('FT4222_SPIMaster_SingleWrite')

    def read(self, rd_len):
        '''
        FTSPIBus read data function

        Args:
            rd_len:     int, Length of datas to be read

        Returns:
            list, the data has been read.

        Examples:
            datas = ftspi.read(3)
            print(datas)
        '''
        rd_len = int(rd_len)
        assert rd_len > 0

        self._ft_4222.open()
        rd_data = (ctypes.c_ubyte * rd_len)()

        ftstatus = self._base_lib.FT4222_SPIMaster_Init(self._fthandle, self._ioline, self._speed,
                                                        self._clockpolarity, self._clockphase, self._ssomap)
        if ftstatus != 0:
            raise FTSPIException('FT4222_SPIMaster_Init')

        bytesread = ctypes.c_uint16(0)
        sizetransferred = ctypes.c_bool(1)
        ftstatus = self._base_lib.FT4222_SPIMaster_SingleRead(self._fthandle, rd_data, rd_len,
                                                              ctypes.byref(bytesread), sizetransferred)
        if ftstatus != 0:
            raise FTSPIException('FT4222_SPIMaster_SingleRead')

        return list(rd_data)

    def sync_transfer(self, wr_data):
        '''
        This function only supports standard spi mode.

        Write data to the spi bus. At the same time, the same length of data is read.

        Args:
            wr_data:         list, Data to write, the list element is an integer, bit width: 8 bits.

        Returns:
            list,       Data to be read, the list element is an integer, bit width: 8 bits.

        Examples:
            to_send = [0x01, 0x03, 0x04]
            ret = spi.sync_transfer(to_send) # len(ret) == len(to_send)
        '''
        assert isinstance(wr_data, list)

        self._ft_4222.open()
        ftstatus = self._base_lib.FT4222_SPIMaster_Init(self._fthandle, self._ioline, self._speed,
                                                        self._clockpolarity, self._clockphase, self._ssomap)
        if ftstatus != 0:
            raise FTSPIException('FT4222_SPIMaster_Init')

        rd_data = (ctypes.c_ubyte * len(wr_data))()
        data = (ctypes.c_ubyte * len(wr_data))()
        rd_len = len(wr_data)
        for i in range(rd_len):
            data[i] = wr_data[i]

        byteswritten = ctypes.c_uint16(0)
        sizetransferred = ctypes.c_bool(1)
        ftstatus = self._base_lib.FT4222_SPIMaster_SingleReadWrite(self._fthandle, rd_data, data, rd_len,
                                                                   ctypes.byref(byteswritten), sizetransferred)
        if ftstatus != 0:
            raise FTSPIException('FT4222_SPIMaster_SingleReadWrite')
        return list(rd_data)

    def async_transfer(self, wr_data, rd_len):
        '''
        This function supports SPI and QPI mode.

        First write data to the spi bus, then read data from the spi bus.

        Args:
            wr_data:     list, Data to write, the list element is an integer, bit width: 8 bits.
            rd_len:      int, Length of read data.

        Returns:
            list,       Data to be read, the list element is an integer, bit width: 8 bits.

        Examples:
            ret = spi.async_transfer([0x01,0x02,0x03,0x04], 3)   # len(ret) == 3
        '''
        assert isinstance(wr_data, list)
        assert rd_len > 0

        self._ft_4222.open()
        ftstatus = self._base_lib.FT4222_SPIMaster_Init(self._fthandle, self._ioline, self._speed,
                                                        self._clockpolarity, self._clockphase, self._ssomap)
        if ftstatus != 0:
            raise FTSPIException('FT4222_SPIMaster_Init')

        rd_data = (ctypes.c_ubyte * rd_len)()
        bytesread = (ctypes.c_ubyte * (len(wr_data) + rd_len))()
        data = (ctypes.c_ubyte * (len(wr_data) + rd_len))()

        for i in range(len(wr_data)):
            data[i] = wr_data[i]
        for i in range(rd_len):
            data[len(wr_data) + i] = 0x0

        byteswritten = ctypes.c_uint16(0)
        sizetransferred = ctypes.c_bool(1)
        ftstatus = self._base_lib.FT4222_SPIMaster_SingleReadWrite(self._fthandle, bytesread, data,
                                                                   len(wr_data) + rd_len,
                                                                   ctypes.byref(byteswritten), sizetransferred)
        if ftstatus != 0:
            raise FTSPIException('FT4222_SPIMaster_SingleReadWrite')

        for i in range(rd_len):
            rd_data[i] = bytesread[(len(wr_data) + i)]

        return list(rd_data)

    def transfer(self, wr_data, rd_len, sync=True):
        '''
        FTSPIBus transfer data function

        Args:
            wr_data:    list,       Datas to be write
            rd_len:     int,        Length of datas to be read
            sync:       boolean,    True for write and read synchronizily,
                                           False for write then read from spi bus
        Examples:
            data = ftspi.transfer([1, 2, 3], 4, False)
            print(data)
        '''
        assert isinstance(wr_data, list)
        assert rd_len > 0
        assert sync in [True, False]

        if sync is True:
            return self.sync_transfer(wr_data)
        else:
            return self.async_transfer(wr_data, rd_len)
