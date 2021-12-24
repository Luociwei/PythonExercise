# -*- coding: utf-8 -*-
from ..tracer.recorder import *
import struct
import ctypes


class SPIException(Exception):
    pass


class SpiEmuLib(object):

    def __init__(self):
        self._recorder = Recorder()
        self._delay_usecs = 0
        self._mode = 0
        self._max_frequency = 100
        add_recorder(self._recorder)

    def spi_open(self, dev_name):
        self._dev_name = dev_name
        self._recorder.record("open")

    def spi_close(self, ptr):
        self._recorder.record("close")

    def spi_get_wait_us(self, ptr, c_ptr_us):
        self._recorder.record("spi get wait us")
        return 0

    def spi_set_wait_us(self, ptr, us):
        self._recorder.record("spi set us as %d" % (us))
        return 0

    def spi_get_mode(self, ptr, c_ptr_mode):
        self._recorder.record("spi get mode")
        ctypes.memset(c_ptr_mode, 0, 1)
        return 0

    def spi_set_mode(self, ptr, mode):
        self._recorder.record("spi set mode as %d" % (mode))
        return 0

    def spi_get_frequency(self, ptr, c_ptr_mode):
        self._recorder.record("spi get speed")
        return 0

    def spi_set_frequency(self, ptr, speed):
        self._recorder.record("spi set speed as %d" % (speed))
        return 0

    def spi_write(self, ptr, c_ptr_data, len):
        data_pack = struct.unpack('%dB' % (len), c_ptr_data)
        self._recorder.record("spi write data is " + str(data_pack))
        return 0

    def spi_read(self, ptr, c_ptr_data, len):
        self._recorder.record("spi read %d datas" % len)
        return 0

    def spi_sync_transfer(self, ptr, cwr_data, crd_data, wd_len):
        data_pack = struct.unpack('%dB' % (wd_len), cwr_data)
        self._recorder.record("spi sync_transfer data is " + str(data_pack))
        return 0

    def spi_async_transfer(self, ptr, cwr_data, wr_len, crd_data, rd_len):
        data_pack = struct.unpack('%dB' % (wr_len), cwr_data)
        self._recorder.record("spi async_transfer data is " + str(data_pack))
        return 0
