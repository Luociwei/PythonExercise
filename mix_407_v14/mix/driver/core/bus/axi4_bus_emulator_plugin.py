# -*- coding: utf-8 -*-
import ctypes


class AXI4BusEmulatorDef:
    IPCORE_ID_ADDR = 0x00
    IPCORE_BOARD_ID_ADDR = 0x01
    IPCORE_VERSION_ADDR = 0x02


class AXI4BusEmulatorPlugin(object):
    def __init__(self):
        self._select_pos = dict()
        self._reg = (ctypes.c_ubyte * 0x4000)()

    def get_ipcore_id(self):
        return self.read_8bit_inc(AXI4BusEmulatorDef.IPCORE_ID_ADDR, 1)[0]

    def get_ipcore_version(self):
        return self.read_8bit_inc(AXI4BusEmulatorDef.IPCORE_VERSION_ADDR, 1)[0]

    def get_ipcore_board_id(self):
        return self.read_8bit_inc(AXI4BusEmulatorDef.IPCORE_BOARD_ID_ADDR, 1)[0]

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
        result = [reg[addr / 4] for i in range(rd_len)]
        return result

    def write_32bit_fix(self, addr, data):
        reg = ctypes.cast(self._reg, ctypes.POINTER(ctypes.c_uint))
        for i in range(len(data)):
            reg[addr / 4] = data[i]

    def read_8bit_inc(self, addr, rd_len):
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

