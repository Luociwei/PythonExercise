
# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *
from mix.driver.core.bus.axi4_lite_bus_emulator import *
import time
import ctypes

__author__ = 'qinxiaojun@SmartGiant'
__version__ = '0.2'


class MIXDMASGDef:
    CHNL_BASE = 0x20
    CHNL_REG_SET_SIZE = 0x10
    MEM_START_REGISTER = 0x00
    MEM_SIZE_REGISTER = 0x04
    CHNL_STATUS_REGISTER = 0x07
    DATA_CNT_REGISTER = 0x08
    CHNL_ENABLE_REGISTER = 0x0B
    RD_CNT_REGISTER = 0x0C
    RD_REFRESH_REGISTER = 0x0F
    REG_SIZE = 4096
    CHNL_ENABLE = 0x01
    CHNL_FULL = 0x80
    RD_REFRESH = 0x01


class MIXDMASGError(Exception):
    pass


class MIXDMASGEmulator(object):

    def __init__(self, dev_name):
        self._dev_name = dev_name
        self._axi4_bus = AXI4LiteBusEmulator("axi4_bus_emulator", MIXDMASGDef.REG_SIZE)
        self._mem_offset = 0
        self._channel = dict()
        self._max_size = 0x100000
        self.recorder = Recorder()
        add_recorder(self.recorder)

    def __del__(self):
        del_recorder(self.recorder)

    def _get_data_cnt(self, id):
        offset = MIXDMASGDef.CHNL_BASE + (MIXDMASGDef.CHNL_REG_SET_SIZE * id)
        addr = offset + MIXDMASGDef.DATA_CNT_REGISTER
        data = self._axi4_bus.write_8bit_inc(addr, [0xFF])
        data = self._axi4_bus.read_8bit_inc(addr, 3)
        data_cnt = ((data[2] << 16) | (data[1] << 8) | data[0]) << 8
        return data_cnt

    def _get_overflow(self, id):
        offset = MIXDMASGDef.CHNL_BASE + (MIXDMASGDef.CHNL_REG_SET_SIZE * id)
        addr = offset + MIXDMASGDef.CHNL_STATUS_REGISTER
        data = self._axi4_bus.read_8bit_inc(addr, 1)
        overflow = not(not (data[0] & MIXDMASGDef.CHNL_FULL))
        return overflow

    def config_channel(self, id, size):
        assert id < 16
        if size > self._max_size:
            raise MIXDMASGError("Invalid argument")

        if id not in self._channel.keys():
            config = dict()
            config["enable"] = False
        else:
            config = self._channel[id]
        if config["enable"] is True:
            raise MIXDMASGError("Operation not permitted")

        config["mem"] = (ctypes.c_ubyte * size)()
        config["mem_size"] = size
        config["read_ptr"] = 0

        self.recorder.record("%s config channel %d with size %d" %
                             (self._dev_name, id, size))

        offset = MIXDMASGDef.CHNL_BASE + (MIXDMASGDef.CHNL_REG_SET_SIZE * id)
        addr = offset + MIXDMASGDef.MEM_START_REGISTER
        data = [self._mem_offset]
        self._axi4_bus.write_32bit_inc(addr, data)

        addr = offset + MIXDMASGDef.MEM_SIZE_REGISTER
        sz = size >> 8
        data = [sz & 0xff, (sz >> 8) & 0xff, (sz >> 16) & 0xff]
        self._axi4_bus.write_8bit_inc(addr, data)

        self._mem_offset += size
        self._channel[id] = config

    def enable_channel(self, id):
        assert id < 16
        if id not in self._channel.keys():
            raise MIXDMASGError("Operation not permitted")

        self.recorder.record("%s enable channel %d" % (self._dev_name, id))
        offset = MIXDMASGDef.CHNL_BASE + (MIXDMASGDef.CHNL_REG_SET_SIZE * id)
        addr = offset + MIXDMASGDef.CHNL_ENABLE_REGISTER
        data = self._axi4_bus.read_8bit_inc(addr, 1)
        data[0] |= MIXDMASGDef.CHNL_ENABLE
        self._axi4_bus.write_8bit_inc(addr, data)
        self._channel[id]["enable"] = True

    def disable_channel(self, id):
        assert id < 16
        self.recorder.record("%s disable channel %d" % (self._dev_name, id))
        offset = MIXDMASGDef.CHNL_BASE + (MIXDMASGDef.CHNL_REG_SET_SIZE * id)
        addr = offset + MIXDMASGDef.CHNL_ENABLE_REGISTER
        data = self._axi4_bus.read_8bit_inc(addr, 1)
        data[0] &= ~MIXDMASGDef.CHNL_ENABLE
        self._axi4_bus.write_8bit_inc(addr, data)
        self._channel[id]["enable"] = False

    def reset_channel(self, id):
        assert id < 16
        self.recorder.record("%s reset channel %d" % (self._dev_name, id))
        self.disable_channel(id)
        self.enable_channel(id)
        self._channel[id]["read_ptr"] = 0

    def read_channel_data(self, id, length, timeout):
        assert id < 16
        self.recorder.record("%s read channel %d data length %d" %
                             (self._dev_name, id, length))

        overflow = self._get_overflow(id)
        data_cnt = self._get_data_cnt(id)

        while timeout > 0:
            timeout -= 1
            time.sleep(0.001)
            data_cnt = self._get_data_cnt(id)
            if data_cnt >= length:
                data_cnt = length
                break

        read_ptr = self._channel[id]["read_ptr"]
        size = self._channel[id]["mem_size"]
        if (read_ptr + data_cnt) > size:
            data_cnt = size - read_ptr
            result = "Data unfinished"
        elif timeout == 0:
            result = "Operation timed out"
        else:
            result = 0

        if data_cnt > 0:
            mem = self._channel[id]["mem"]
            data = mem[read_ptr: read_ptr + data_cnt]
        else:
            data = None
        return result, data, data_cnt, overflow

    def read_channel_all_data(self, id):
        assert id < 16
        self.recorder.record("%s read channel %d all data" % (self._dev_name, id))

        overflow = self._get_overflow(id)
        data_cnt = self._get_data_cnt(id)

        read_ptr = self._channel[id]["read_ptr"]
        size = self._channel[id]["mem_size"]
        if (read_ptr + data_cnt) > size:
            data_cnt = size - read_ptr
            result = "Data unfinished"
        else:
            result = 0

        if data_cnt > 0:
            mem = self._channel[id]["mem"]
            data = mem[read_ptr: read_ptr + data_cnt]
        else:
            data = None
        return result, data, data_cnt, overflow

    def read_done(self, id, length):
        assert id < 16
        self.recorder.record("%s read channel %d done with length %d" %
                             (self._dev_name, id, length))
        offset = MIXDMASGDef.CHNL_BASE + (MIXDMASGDef.CHNL_REG_SET_SIZE * id)
        addr = offset + MIXDMASGDef.RD_CNT_REGISTER
        length = length >> 8
        data = [length & 0xff, (length >> 8) & 0xff, (length >> 16) & 0xff]
        self._axi4_bus.write_8bit_inc(addr, data)

        addr = offset + MIXDMASGDef.RD_REFRESH_REGISTER
        data = [MIXDMASGDef.RD_REFRESH]
        self._axi4_bus.write_8bit_inc(addr, data)

        read_ptr = self._channel[id]["read_ptr"]
        size = self._channel[id]["mem_size"]
        if (read_ptr + length) < size:
            self._channel[id]["read_ptr"] = read_ptr + length
        else:
            self._channel[id]["read_ptr"] = length - (size - read_ptr)
