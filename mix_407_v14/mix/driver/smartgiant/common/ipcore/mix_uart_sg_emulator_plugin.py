# -*- coding: utf-8 -*-
import ctypes

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'

_injection_data = [
    {
        "filter": {
            "addr": 0x3C,
        },
        "action": [
            {"select": [[0x10, 0x00]]}
        ]
    },
    {
        "filter": {
            "addr": 0x38,
        },
        "action": [
            {"select": [[0x02, 0x00]]}
        ]
    },
    {
        "filter": {
            "addr": 0x24,
        },
        "action": [
            {"select": [[0x00], [0x00], [0x00],
                        [0x00], [0x40], [0x00], [0x50], [0x00], [0x60], [0x00], [0x70],
                        [0x00], [0x02], [0x00], [0x00], [0x00], [0x01],
                        [0x00], [0x04], [0x00], [0x08], [0x00], [0x0c]]}
        ]
    }
]


class MIXUARTSGEmulatorPlugin(object):
    def __init__(self):
        self._select_pos = dict()
        self._reg = (ctypes.c_ubyte * 256)()

    def read_8bit_fix(self, addr, rd_len):
        result = [self._reg[addr] for i in range(rd_len)]
        return result

    def write_8bit_fix(self, addr, data):
        for i in range(len(data)):
            self._reg[addr] = data[i]

    def read_16bit_fix(self, addr, rd_len):
        for item in _injection_data:
            filter = item['filter']
            actions = item['action']
            if filter['addr'] == addr:
                for action in actions:
                    if 'select' in action.keys():
                        if addr not in self._select_pos.keys():
                            self._select_pos[addr] = 0
                        data = action['select'][self._select_pos[addr]]
                        self._select_pos[addr] += 1
                        if len(action['select']) == self._select_pos[addr]:
                            self._select_pos[addr] = 0
                        return data
        return [0 for i in range(rd_len)]

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
        global _injection_data
        for item in _injection_data:
            filter = item['filter']
            actions = item['action']
            if filter['addr'] == addr:
                for action in actions:
                    if 'select' in action.keys():
                        if addr not in self._select_pos.keys():
                            self._select_pos[addr] = 0
                        data = action['select'][self._select_pos[addr]]
                        self._select_pos[addr] += 1
                        if len(action['select']) == self._select_pos[addr]:
                            self._select_pos[addr] = 0
                        return data
        return [0 for i in range(rd_len)]

    def write_8bit_inc(self, addr, data):
        for i in range(len(data)):
            self._reg[addr + i] = data[i]

    def read_16bit_inc(self, addr, rd_len):
        global _injection_data
        for item in _injection_data:
            filter = item['filter']
            actions = item['action']
            if filter['addr'] == addr:
                for action in actions:
                    if 'select' in action.keys():
                        if addr not in self._select_pos.keys():
                            self._select_pos[addr] = 0
                        data = action['select'][self._select_pos[addr]]
                        self._select_pos[addr] += 1
                        if len(action['select']) == self._select_pos[addr]:
                            self._select_pos[addr] = 0
                        return data
        return [0 for i in range(rd_len)]

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
