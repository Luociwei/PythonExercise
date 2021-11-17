# -*- coding: utf-8 -*-
import ctypes

__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.1'


class MIXXADCSGEmulatorPlugin(object):
    def __init__(self):
        self._reg = (ctypes.c_ubyte * 0x4000)()
        self._reg[0x16] = 0x00      # data ready

    def write_8bit_fix(self, addr, data):
        for i in range(len(data)):
            self._reg[addr] = data[i]

    def write_8bit_inc(self, addr, data):
        for i in range(len(data)):
            self._reg[addr + i] = data[i]

    def read_8bit_inc(self, addr, rd_len):
        self._reg[0x16] = 0x00      # keep data always ready
        result = [self._reg[addr + i] for i in range(rd_len)]
        return result

    def read_8bit_fix(self, addr, rd_len):
        self._reg[0x16] = 0x00      # keep data always ready
        result = [self._reg[addr] for i in range(rd_len)]
        return result

    def write_16bit_fix(self, addr, data):
        reg = ctypes.cast(self._reg, ctypes.POINTER(ctypes.c_ushort))
        for i in range(len(data)):
            reg[addr / 2] = data[i]

    def write_32bit_fix(self, addr, data):
        reg = ctypes.cast(self._reg, ctypes.POINTER(ctypes.c_uint))
        for i in range(len(data)):
            reg[addr / 4] = data[i]

    def read_16bit_fix(self, addr, rd_len):
        reg = ctypes.cast(self._reg, ctypes.POINTER(ctypes.c_ushort))
        result = [reg[addr / 2] for i in range(rd_len)]
        return result

    def read_32bit_fix(self, addr, rd_len):
        reg = ctypes.cast(self._reg, ctypes.POINTER(ctypes.c_uint))
        result = [int(reg[addr / 4]) for i in range(rd_len)]
        return result
