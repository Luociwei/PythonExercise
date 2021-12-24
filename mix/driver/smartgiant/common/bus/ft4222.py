# -*- coding: utf-8 -*-
import ctypes
import os
from mix.driver.smartgiant.common.bus.ft4222_lib_emulator import FT4222LibEmulator

__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1'


class FT4222Def:
    FT_OPEN_BY_SERIAL_NUMBER = 1
    FT_OPEN_BY_DESCRIPTION = 2
    FT_OPEN_BY_LOCATION = 4


class FT4222Exception(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class FT4222(object):

    # class variable to host all FT4222 instances created.
    instances = {}

    def __new__(cls, locid):
        if locid is not None:
            locid = int(locid)
        if locid in cls.instances:
            # use existing instance
            pass
        else:
            # create a new one
            instance = _FT4222(locid)
            cls.instances[locid] = instance
        return cls.instances[locid]


class _FT4222(object):
    '''
    FT4222 function class.

    ft4222 is a chip used to access I2C, SPI, GPIO through USB.
    This driver support FT4222 mounted.FT4222 instance need to create before using
    FTI2C, FTSPI, and FTGPIO.( 1.FTI2C, FTSPI, FTGPIO buses automatically match the device through the FT4222
    instance. 2.The functions of FTI2C, FTSPI and FTGPIO buses are realized by calling the dynamic library of
    FT4222.)

    Args:
        locid:   string/int, locid of FT4222 device, if locid < 100, locid means device index.
                                If the locid is 0 or '0', the FTI2C and FTSPI buses automatically
                                match the device.
                                If the locid is 1 or '1', the FTGPIO bus automatically
                                match the device.
    Examples:
        ft4222 = FT4222('4593')
    '''

    def __init__(self, locid=None):
        if locid is not None:
            lib_file = os.environ.get('FT4222_LIB', 'libft4222.so')
            self._base_lib = ctypes.cdll.LoadLibrary(lib_file)
            self._locid = locid
        else:
            self._base_lib = FT4222LibEmulator()
            self._locid = self._base_lib._locid

        self._fthandle = ctypes.c_void_p(0)
        self.is_open = False

    def __del__(self):
        self.close()

    def close(self):
        '''
        FT4222 close device

        Examples:
            ft4222.close()
        '''
        if self._fthandle is not None:
            self._base_lib.FT4222_UnInitialize(self._fthandle)
            self._base_lib.FT_Close(self._fthandle)
        self.is_open = False

    def open(self):
        '''
        FT4222 open device, has been called once when init.

        Examples:
            ft4222.open()
        '''
        if self.is_open is False:
            if self._locid < 100:
                ftstatus = self._base_lib.FT_Open(self._locid, ctypes.byref(self._fthandle))
            else:
                ftstatus = self._base_lib.FT_OpenEx(self._locid, FT4222Def.FT_OPEN_BY_LOCATION,
                                                    ctypes.byref(self._fthandle))
            if ftstatus != 0:
                raise FT4222Exception('FT_Open')

            self.is_open = True
