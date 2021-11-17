# -*- coding: utf-8 -*-
__author__ = 'elee@trantest.com'
__version__ = '0.1'


class MCP4725CommandException(Exception):
    pass


class MCP4725EmulatorPlugin(object):
    reg = {
        0: 'FAST_MODE',
        1: 'FAST_MODE',
        2: 'WRITE_DAC_REG',
        3: 'WRITE_DAC_EEPROM_REG'
    }
    NORMAL_MODE = 0x0
    R1K_TO_GRN = 0x1
    R10K_TO_GRN = 0x2
    R500K_TO_GRN = 0x3
    FAST_MODE = 0x0
    WRITE_DAC_REG = 0x2
    WRITE_DAC_EEPROM_REG = 0x3

    ''' We are assume virtual address to store two part of memory value(14 bit) '''
    DAC_REG = 0x0
    EEPROM_REG = 0x1

    def __init__(self):
        self._reg = {MCP4725EmulatorPlugin.DAC_REG: 0, MCP4725EmulatorPlugin.EEPROM_REG: 0}
        self._power_down_mode = MCP4725EmulatorPlugin.NORMAL_MODE

    def dump(self):
        print(self._reg)

    def check_cmd(self, num):
        try:
            return [(i, MCP4725EmulatorPlugin.reg[i]) for i in self.reg.keys() if num ^ i == 0][0]
        except IndexError as e:
            raise MCP4725CommandException('%s :Command parsing error.' % e)

    def write(self, addr, wr_data):

        cmd_addr = wr_data[0] >> 5
        reg_str = self.check_cmd(cmd_addr)
        if reg_str is 'FAST_MODE':
            self._power_down_mode = (wr_data[0] & (0x3 << 4)) >> 4
            self._reg[MCP4725EmulatorPlugin.DAC_REG] = ((wr_data[0] & 0x0F) << 8) | wr_data[1]
        elif reg_str is 'WRITE_DAC_REG':
            assert len(wr_data) >= 3
            self._power_down_mode = (wr_data[0] & (0x3 << 1)) >> 1
            self._reg[MCP4725EmulatorPlugin.DAC_REG] = ((wr_data[2] & 0xF0) >> 4) | (wr_data[1] << 4)
        elif reg_str is 'WRITE_DAC_EEPROM_REG':
            assert len(wr_data) >= 3
            self._power_down_mode = (wr_data[0] & (0x3 << 1)) >> 1
            self._reg[MCP4725EmulatorPlugin.DAC_REG] = ((wr_data[2] & 0xF0) >> 4) | (wr_data[1] << 4)
            v = ((self._power_down_mode << 13) | ((wr_data[2] & 0xF0) >> 4) | (wr_data[1] << 4))
            self._reg[MCP4725EmulatorPlugin.EEPROM_REG] = v

    def read(self, addr, rd_len):
        dac_register = self._reg[MCP4725EmulatorPlugin.DAC_REG]
        eeprom_regiter = self._reg[MCP4725EmulatorPlugin.EEPROM_REG]
        return [0x80 | (self._power_down_mode << 1), (dac_register >> 4) & 0xFF,
                (dac_register << 4) & 0xFF, eeprom_regiter >> 8, eeprom_regiter & 0xFF]

    def write_and_read(self, addr, wr_data=0, rd_len=0):
        raise NotImplementedError('MCP4725 no need to implement this function')

