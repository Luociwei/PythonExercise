# -*- coding: utf-8 -*-


class CAT9555Def:
    INPUT_PORT_0_REGISTER = 0x00
    INPUT_PORT_1_REGISTER = 0x01
    OUTPUT_PORT_0_REGISTER = 0x02
    OUTPUT_PORT_1_REGISTER = 0x03
    INVERSION_PORT_0_REGISTER = 0x04
    INVERSION_PORT_1_REGISTER = 0x05
    DIR_CONFIG_PORT_0_REGISTER = 0x06
    DIR_CONFIG_PORT_1_REGISTER = 0x07
    PIN_DIR_INPUT = 'input'
    PIN_DIR_OUTPUT = 'output'


class CAT9555EmulatorPlugin(object):

    def __init__(self):
        self._reg = dict()
        self.write(0x00, [CAT9555Def.INPUT_PORT_0_REGISTER, 0x00, 0x00])
        self.write(0x00, [CAT9555Def.OUTPUT_PORT_0_REGISTER, 0xFF, 0xFF])
        self.write(0x00, [CAT9555Def.INVERSION_PORT_0_REGISTER, 0x00, 0x00])
        self.write(0x00, [CAT9555Def.DIR_CONFIG_PORT_0_REGISTER, 0xFF, 0xFF])

    def dump(self):
        print(self._reg)

    def write(self, addr, wr_data):
        reg_addr = wr_data[0]
        wr_to_reg = [i for i in wr_data[1:]]
        for index in range(len(wr_to_reg)):
            self._reg[reg_addr + index] = [wr_to_reg[index]]

    def read(self, addr, wr_data, wr_len):
        raise NotImplementedError('CAT9555 no need to implement this function')

    def write_and_read(self, addr, wr_data, rd_len):
        reg_addr = wr_data[0]
        data = [self._reg[reg_addr + index][0] for index in range(rd_len)]
        return data
