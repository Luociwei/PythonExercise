# -*- coding: utf-8 -*-
import ctypes
from mix.driver.core.tracer.recorder import *

__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1'


class FT4222LibEmulator(object):
    def __init__(self):
        self._recorder = Recorder()
        add_recorder(self._recorder)
        self._locid = 0

    def __del__(self):
        del_recorder(self._recorder)

    def FT_Open(self, locid, fthandle):
        self._recorder.record("open locid is %d" % self._locid)

        return 0

    def FT_OpenEx(self, locid, flags, fthandle):
        self._recorder.record("open locid is %d" % self._locid)

        return 0

    def FT4222_UnInitialize(self, fthandle):
        self._recorder.record("FT4222_UnInitialize")

        return 0

    def FT_Close(self, fthandle):
        self._recorder.record("FT_Close")

        return 0

    def FT4222_I2CMaster_Init(self, fthandle, kbps):
        self._recorder.record("FT4222_I2CMaster_Init kbps is %d" % kbps)

        return 0

    def FT4222_I2CMaster_Reset(self, fthandle):
        self._recorder.record("FT4222_I2CMaster_Reset")

        return 0

    def FT4222_I2CMaster_GetStatus(self, fthandle, controllerstatus):
        self._recorder.record("FT4222_I2CMaster_GetStatus")
        p = ctypes.cast(controllerstatus, ctypes.POINTER(ctypes.c_uint8))
        p[0] = 0x20

        return 0

    def FT4222_I2CMaster_Read(self, fthandle, addr, rd_data, rd_len, bytesread):
        self._recorder.record("read from 0x%02x with %d bytes" % (addr, rd_len))

        return 0

    def FT4222_I2CMaster_Write(self, fthandle, addr, wr_data, wr_len, byteswritten):
        assert isinstance(wr_data, (ctypes.c_ubyte * wr_len))
        record_data = '['
        for i in range(len(wr_data)):
            record_data += "0x%02x" % wr_data[i]
            if i != len(wr_data) - 1:
                record_data += ', '
        record_data += ']'
        self._recorder.record("write " + record_data + " to 0x%02x" % addr)

        return 0

    def FT4222_I2CMaster_ReadEx(self, fthandle, addr, flags, rd_data, rd_len, bytesread):
        self._recorder.record("read from 0x%02x with %d bytes" % (addr, rd_len))

        return 0

    def FT4222_I2CMaster_WriteEx(self, fthandle, addr, flags, wr_data, wr_len, byteswritten):
        assert isinstance(wr_data, (ctypes.c_ubyte * wr_len))
        record_data = '['
        for i in range(len(wr_data)):
            record_data += "0x%02x" % wr_data[i]
            if i != len(wr_data) - 1:
                record_data += ', '
        record_data += ']'
        self._recorder.record("write " + record_data + " to 0x%02x" % addr)

        return 0

    def FT4222_SPIMaster_Init(self, fthandle, ioline, speed, clockpolarity, clockphase, ssomap):
        self._recorder.record("FT4222_SPIMaster_Init speed is %d" % speed)

        return 0

    def FT4222_SPIMaster_SingleRead(self, fthandle, rd_data, rd_len, bytesread, sizetransferred):
        self._recorder.record("read %d bytes" % rd_len)

        return 0

    def FT4222_SPIMaster_SingleWrite(self, fthandle, wr_data, wr_len, byteswritten, sizetransferred):
        assert isinstance(wr_data, (ctypes.c_ubyte * wr_len))
        record_data = '['
        for i in range(len(wr_data)):
            record_data += "0x%02x" % wr_data[i]
            if i != len(wr_data) - 1:
                record_data += ', '
        record_data += ']'
        self._recorder.record("write data " + record_data)

        return 0

    def FT4222_SPIMaster_SingleReadWrite(self, fthandle, rd_data, wr_data, rd_len, byteswritten, sizetransferred):
        assert isinstance(wr_data, (ctypes.c_ubyte * len(wr_data)))
        record_data = '['
        for i in range(len(wr_data)):
            record_data += "0x%02x" % wr_data[i]
            if i != len(wr_data) - 1:
                record_data += ', '
        record_data += ']'
        self._recorder.record("write data " + record_data + " and read %d bytes" % rd_len)

        return 0

    def FT4222_GPIO_Init(self, fthandle, gpioDir):
        self._recorder.record("FT4222_GPIO_Init")

        return 0

    def FT4222_SetSuspendOut(self, fthandle, enable):
        self._recorder.record("FT4222_SetSuspendOut")

        return 0

    def FT4222_SetWakeUpInterrupt(self, fthandle, enable):
        self._recorder.record("FT4222_SetWakeUpInterrupt")

        return 0

    def FT4222_GPIO_Read(self, fthandle, pin_id, level):
        self._recorder.record("get pin{0} level".format(pin_id))

        return 0

    def FT4222_GPIO_Write(self, fthandle, pin_id, level):
        self._recorder.record("set pin{0} level {1}".format(pin_id, int(level.value)))

        return 0
