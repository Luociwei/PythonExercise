# -*- coding: utf-8 -*-
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class MIXAidSlaveSGDef:
    REG_SIZE = 8192
    CONFIG_REGISTER = 0x10
    ENABLE_CMD = 0x01
    DISABLE_CMD = 0x00
    COMMAND_RAM_MAX_SIZE = 32

    REQ_RAM_ADDR_REGISTER = 0x21
    REQ_RAM_DATA_REGISTER = 0x23
    REQ_RAM_REGISTER = 0x20
    REQ_SAVE_CMD = 0x01

    REP_RAM_ADDR_REGISTER = 0x31
    REP_RAM_DATA_REGISTER = 0x33
    REP_RAM_REGISTER = 0x30
    REP_SAVE_CMD = 0x01

    MAX_AID_CMD_TABLE_INDEX = 63
    MAX_REQ_DATA_PALOAD_LEN = 27
    MAX_REP_DATA_PALOAD_LEN = 31


class MIXAidSlaveSG(object):
    '''
    MIXAidSlaveSG function class.

    ClassType = AID

    Args:
        axi4_bus:   instance(AXI4LiteBus)/None, Class instance of axi4 bus,
                                                if not using this parameter, will create emulator.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT1_AID', 8192)
        aid = MIXAidSlaveSG(axi4_bus)

    '''

    rpc_public_api = ['open', 'close', 'config_command']

    def __init__(self, axi4_bus=None):
        if axi4_bus is None:
            self._axi4_bus = AXI4LiteBusEmulator('mix_aidslave_sg_emulator', MIXAidSlaveSGDef.REG_SIZE)
        elif isinstance(axi4_bus, basestring):
            self._axi4_bus = AXI4LiteBus(axi4_bus, MIXAidSlaveSGDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

    def open(self):
        '''
        MIXAidSlaveSG open device

        Examples:
            aid.open()

        '''
        self._axi4_bus.write_8bit_inc(MIXAidSlaveSGDef.CONFIG_REGISTER, [MIXAidSlaveSGDef.DISABLE_CMD])
        self._axi4_bus.write_8bit_inc(MIXAidSlaveSGDef.CONFIG_REGISTER, [MIXAidSlaveSGDef.ENABLE_CMD])

    def close(self):
        '''
        MIXAidSlaveSG close device

        Examples:
            aid.close()

        '''
        self._axi4_bus.write_8bit_inc(MIXAidSlaveSGDef.CONFIG_REGISTER, [MIXAidSlaveSGDef.DISABLE_CMD])

    def config_command(self, index, req_data, req_mask, rep_data):
        '''
        MIXAidSlaveSG config request and response message

        Args:
            index:      int, [0~63], requst and reponsoe pair index.
            req_data:   list, request message datas.
            rep_data:   list, reponse message datas.

        Examples:
            aid.config_command(0, [0x74,0x00,0x02,0x1F], 0x03, [0x74,0x00,0x02,0x1F])

        '''

        assert index >= 0 and index <= MIXAidSlaveSGDef.MAX_AID_CMD_TABLE_INDEX
        assert req_mask >= 0 and req_mask <= 0xFFFFFFF
        assert len(req_data) > 0 and len(req_data) <= MIXAidSlaveSGDef.MAX_REQ_DATA_PALOAD_LEN
        assert len(rep_data) > 0 and len(rep_data) <= MIXAidSlaveSGDef.MAX_REP_DATA_PALOAD_LEN

        # save req index
        req_addr = index * MIXAidSlaveSGDef.COMMAND_RAM_MAX_SIZE
        self._axi4_bus.write_8bit_inc(MIXAidSlaveSGDef.REQ_RAM_ADDR_REGISTER, [
                                      req_addr & 0xFF, (req_addr >> 8) & 0xFF])

        # save req len
        self._axi4_bus.write_8bit_inc(MIXAidSlaveSGDef.REQ_RAM_DATA_REGISTER, [len(req_data) & 0xFF])

        # save to ram
        self._axi4_bus.write_8bit_inc(MIXAidSlaveSGDef.REQ_RAM_REGISTER, [MIXAidSlaveSGDef.REQ_SAVE_CMD])

        mask_data = [req_mask & 0xFF, (req_mask >> 8) & 0xFF,
                     (req_mask >> 16) & 0xFF, (req_mask >> 24) & 0xFF]

        for i in range(4):
            req_addr += 1
            self._axi4_bus.write_8bit_inc(MIXAidSlaveSGDef.REQ_RAM_ADDR_REGISTER, [
                                          req_addr & 0xFF, (req_addr >> 8) & 0xFF])
            self._axi4_bus.write_8bit_inc(MIXAidSlaveSGDef.REQ_RAM_DATA_REGISTER, [mask_data[i]])
            self._axi4_bus.write_8bit_inc(MIXAidSlaveSGDef.REQ_RAM_REGISTER, [MIXAidSlaveSGDef.REQ_SAVE_CMD])

        for i in range(len(req_data)):
            req_addr += 1
            self._axi4_bus.write_8bit_inc(MIXAidSlaveSGDef.REQ_RAM_ADDR_REGISTER, [
                                          req_addr & 0xFF, (req_addr >> 8) & 0xFF])
            self._axi4_bus.write_8bit_inc(MIXAidSlaveSGDef.REQ_RAM_DATA_REGISTER, [req_data[i]])
            self._axi4_bus.write_8bit_inc(MIXAidSlaveSGDef.REQ_RAM_REGISTER, [MIXAidSlaveSGDef.REQ_SAVE_CMD])

        rep_addr = index * MIXAidSlaveSGDef.COMMAND_RAM_MAX_SIZE
        self._axi4_bus.write_8bit_inc(MIXAidSlaveSGDef.REP_RAM_ADDR_REGISTER, [
                                      rep_addr & 0xFF, (rep_addr >> 8) & 0xFF])
        self._axi4_bus.write_8bit_inc(MIXAidSlaveSGDef.REP_RAM_DATA_REGISTER, [
                                      (len(rep_data) - 1) & 0xFF])
        self._axi4_bus.write_8bit_inc(MIXAidSlaveSGDef.REP_RAM_REGISTER, [MIXAidSlaveSGDef.REP_SAVE_CMD])

        for i in range(len(rep_data) - 1):
            rep_addr += 1
            self._axi4_bus.write_8bit_inc(MIXAidSlaveSGDef.REP_RAM_ADDR_REGISTER, [
                                          rep_addr & 0xFF, (rep_addr >> 8) & 0xFF])
            self._axi4_bus.write_8bit_inc(MIXAidSlaveSGDef.REP_RAM_DATA_REGISTER, [rep_data[i]])
            self._axi4_bus.write_8bit_inc(MIXAidSlaveSGDef.REP_RAM_REGISTER, [MIXAidSlaveSGDef.REP_SAVE_CMD])
