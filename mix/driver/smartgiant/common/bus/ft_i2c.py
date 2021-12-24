# -*- coding: utf-8 -*-
import ctypes
import time
from mix.driver.smartgiant.common.bus.ft4222 import FT4222


__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1'


class FTI2CDef:
    TIMEOUT_SEC = 3.0

    START = 0x02
    REPEATED_START = 0x03
    STOP = 0x04
    START_AND_STOP = 0x06


class FTI2CException(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class FTI2C(object):

    # class variable to host all FT4222 instances created.
    instances = {}

    def __new__(cls, ft4222=None, bps=400000):
        if ft4222 in cls.instances:
            # use existing instance
            pass
        else:
            # create a new one
            instance = _FTI2C(ft4222, bps)
            cls.instances[ft4222] = instance
        return cls.instances[ft4222]


class _FTI2C(object):
    '''
    FTI2C function class. This driver support FTI2C mounted to ps.

    Args:
        ft4222:     instance/None/string/int,  Class instance of FT4222 bus or locid of FT4222 device.
        bps:        int,  FTI2C bus clock speed in Hz.

    Examples:
        ft4222 = FT4222('4593')
        fti2c = FTI2C(ft4222, 100000)

        # write data to address 0x50
        fti2c.write(0x50, [0x00, 0x01, 0x02])

        # read 3 bytes from address 0x50
        rd_data = fti2c.read(0x50, 3)
        print(rd_data) # rd_data is a list, each item is one byte

        # write [0x00, 0x01] to 0x50 and read 3 bytes
        rd_data = fti2c.write_and_read(0x50, [0x00, 0x01], 3)
        print(rd_data) # rd_data is a list, each item is one byte

    '''

    def __init__(self, ft4222=None, bps=400000):
        if ft4222 is None:
            self._ft_4222 = FT4222(None)
        elif isinstance(ft4222, (int, basestring)):
            self._ft_4222 = FT4222(ft4222)
        else:
            self._ft_4222 = ft4222

        self._base_lib = self._ft_4222._base_lib
        self._fthandle = self._ft_4222._fthandle
        self._kbps = bps / 1000

        self._dev_name = 'fti2c'

    def read(self, addr, data_len):
        '''
        FTI2C read specific length datas from address

        Args:
            addr:       hex, [0~0xFF], Read data from this address
            data_len:   int, [0~1024],    Length of data to be read

        Returns:
            list, the data has been read.
        '''
        assert addr >= 0 and addr <= 0xFF
        assert data_len > 0

        self._ft_4222.open()
        rd_data = (ctypes.c_ubyte * data_len)()

        ftstatus = self._base_lib.FT4222_I2CMaster_Init(self._fthandle, self._kbps)
        if ftstatus != 0:
            raise FTI2CException('FT4222_I2CMaster_Init')

        ftstatus = self._base_lib.FT4222_I2CMaster_Reset(self._fthandle)
        if ftstatus != 0:
            raise FTI2CException('FT4222_I2CMaster_Reset')

        bytesread = ctypes.c_uint16(0)
        ftstatus = self._base_lib.FT4222_I2CMaster_Read(self._fthandle, addr, rd_data,
                                                        data_len, ctypes.byref(bytesread))
        if ftstatus != 0:
            raise FTI2CException('FT4222_I2CMaster_Read')

        controllerstatus = ctypes.c_uint8(0)
        start_time = time.time()
        while True:
            ftstatus = self._base_lib.FT4222_I2CMaster_GetStatus(self._fthandle, ctypes.byref(controllerstatus))
            if ftstatus != 0:
                raise FTI2CException('FT4222_I2CMaster_GetStatus')

            if ((controllerstatus.value) & 0x20) != 0:
                break

            if time.time() - start_time > FTI2CDef.TIMEOUT_SEC:
                raise FTI2CException('Wait idle ready timeout')

        return list(rd_data)

    def write(self, addr, data):
        '''
        FTI2C write data to address

        Args:
            addr:   hex, [0~0xFF], Write datas to this address
            data:   list, Datas to be write
        '''
        assert addr >= 0 and addr <= 0xFF
        assert len(data) > 0

        self._ft_4222.open()
        wr_data = (ctypes.c_ubyte * len(data))()
        for i in range(len(data)):
            wr_data[i] = data[i]

        ftstatus = self._base_lib.FT4222_I2CMaster_Init(self._fthandle, self._kbps)
        if ftstatus != 0:
            raise FTI2CException('FT4222_I2CMaster_Init')

        ftstatus = self._base_lib.FT4222_I2CMaster_Reset(self._fthandle)
        if ftstatus != 0:
            raise FTI2CException('FT4222_I2CMaster_Reset')

        byteswritten = ctypes.c_uint16(0)
        ftstatus = self._base_lib.FT4222_I2CMaster_Write(self._fthandle, addr, wr_data,
                                                         len(data), ctypes.byref(byteswritten))
        if ftstatus != 0:
            raise FTI2CException('FT4222_I2CMaster_Write')

        controllerstatus = ctypes.c_uint8(0)
        start_time = time.time()
        while True:
            ftstatus = self._base_lib.FT4222_I2CMaster_GetStatus(self._fthandle, ctypes.byref(controllerstatus))
            if ftstatus != 0:
                raise FTI2CException('FT4222_I2CMaster_GetStatus')

            if ((controllerstatus.value) & 0x20) != 0:
                break

            if time.time() - start_time > FTI2CDef.TIMEOUT_SEC:
                raise FTI2CException('Wait idle ready timeout')

    def write_and_read(self, addr, wr_data, rd_len):
        '''
        FTI2C write datas to address and read specific length datas

        Args:
            addr:       hex, [0~0xFF], device address.
            wr_data:    list, datas to be write
            rd_len:     int, [0~1024], Length of data to be read
        '''
        assert addr >= 0 and addr <= 0xFF
        assert len(wr_data) > 0
        assert rd_len > 0

        self._ft_4222.open()
        rd_data = (ctypes.c_ubyte * rd_len)()
        data = (ctypes.c_ubyte * len(wr_data))()
        for i in range(len(wr_data)):
            data[i] = wr_data[i]

        ftstatus = self._base_lib.FT4222_I2CMaster_Init(self._fthandle, self._kbps)
        if ftstatus != 0:
            raise FTI2CException('FT4222_I2CMaster_Init')

        ftstatus = self._base_lib.FT4222_I2CMaster_Reset(self._fthandle)
        if ftstatus != 0:
            raise FTI2CException('FT4222_I2CMaster_Reset')

        byteswritten = ctypes.c_uint16(0)
        ftstatus = self._base_lib.FT4222_I2CMaster_WriteEx(self._fthandle, addr, FTI2CDef.START, data,
                                                           len(wr_data), ctypes.byref(byteswritten))
        if ftstatus != 0:
            raise FTI2CException('FT4222_I2CMaster_WriteEx')

        bytesread = ctypes.c_uint16(0)
        ftstatus = self._base_lib.FT4222_I2CMaster_ReadEx(self._fthandle, addr,
                                                          FTI2CDef.REPEATED_START | FTI2CDef.STOP, rd_data,
                                                          rd_len, ctypes.byref(bytesread))
        if ftstatus != 0:
            raise FTI2CException('FT4222_I2CMaster_ReadEx')

        controllerstatus = ctypes.c_uint8(0)
        start_time = time.time()
        while True:
            ftstatus = self._base_lib.FT4222_I2CMaster_GetStatus(self._fthandle, ctypes.byref(controllerstatus))
            if ftstatus != 0:
                raise FTI2CException('FT4222_I2CMaster_GetStatus')
            if ((controllerstatus.value) & 0x20) != 0:
                break

            if time.time() - start_time > FTI2CDef.TIMEOUT_SEC:
                raise FTI2CException('Wait idle ready timeout')

        return list(rd_data)
