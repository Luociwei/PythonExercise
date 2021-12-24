# -*- coding: utf-8 -*-
import ctypes

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class MIXAd717XSGEmulatorPlugin(object):
    def __init__(self):
        self._select_pos = dict()
        self._reg = (ctypes.c_ubyte * 0x4000)()
        self.write_8bit_inc(0x26, [0x01])
        self.continue_sampling_mode = False
        # this is used to check register mode, 0 used in continuous mode
        # 1 used to check if bus is busy
        self.continue_busy_reg_mode = 0

        self._reg[0x63] = 0x01
        self._reg[0x11] = 0x00      # data ready

    def read_8bit_fix(self, addr, rd_len):
        result = [self._reg[addr] for i in range(rd_len)]
        return result

    def write_8bit_fix(self, addr, data):
        for i in range(len(data)):
            self._reg[addr] = data[i]

    def read_16bit_fix(self, addr, rd_len):
        reg = ctypes.cast(self._reg, ctypes.POINTER(ctypes.c_ushort))
        result = [reg[addr / 2] for i in range(rd_len)]
        return result

    def write_16bit_fix(self, addr, data):
        reg = ctypes.cast(self._reg, ctypes.POINTER(ctypes.c_ushort))
        for i in range(len(data)):
            reg[addr / 2] = data[i]

    def read_32bit_fix(self, addr, rd_len):
        reg = ctypes.cast(self._reg, ctypes.POINTER(ctypes.c_uint))
        result = [int(reg[addr / 4]) for i in range(rd_len)]
        return result

    def write_32bit_fix(self, addr, data):
        reg = ctypes.cast(self._reg, ctypes.POINTER(ctypes.c_uint))
        for i in range(len(data)):
            reg[addr / 4] = data[i]

    def read_8bit_inc(self, addr, rd_len):
        if self.continue_sampling_mode is False:
            self._reg[0x26] = 0x01
        else:
            if self.continue_busy_reg_mode == 0:
                self._reg[0x26] = 0x04
            else:
                self._reg[0x26] = 0x01

        self._reg[0x11] = 0x00      # keep data always ready
        result = [self._reg[addr + i] for i in range(rd_len)]
        return result

    def write_8bit_inc(self, addr, data):
        for i in range(len(data)):
            self._reg[addr + i] = data[i]

    def read_16bit_inc(self, addr, rd_len):
        reg = ctypes.cast(self._reg, ctypes.POINTER(ctypes.c_ushort))
        result = [reg[addr / 2 + i] for i in range(rd_len)]
        return result

    def write_16bit_inc(self, addr, data):
        reg = ctypes.cast(self._reg, ctypes.POINTER(ctypes.c_ushort))
        for i in range(len(data)):
            reg[addr / 2 + i] = data[i]

    def read_32bit_inc(self, addr, rd_len):
        reg = ctypes.cast(self._reg, ctypes.POINTER(ctypes.c_uint))
        result = [reg[addr / 4 + i] for i in range(rd_len)]
        return result

    def write_32bit_inc(self, addr, data):
        reg = ctypes.cast(self._reg, ctypes.POINTER(ctypes.c_uint))
        for i in range(len(data)):
            reg[addr / 4 + i] = data[i]
