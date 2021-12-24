# -*- coding: utf-8 -*-


class TCA9538Def:
    INPUT_PORT_REGISTER = 0x00
    OUTPUT_PORT_REGISTER = 0x01
    POLARITY_INVERSION_REGISTERS = 0x02
    DIR_CONFIGURATION_REGISTERS = 0x03
    PIN_DIR_INPUT = 'input'
    PIN_DIR_OUTPUT = 'output'


class TCA9538EmulatorPlugin(object):

    def __init__(self):
        self._reg = dict()
        self.write(0x00, [TCA9538Def.INPUT_PORT_REGISTER, 0x00])
        self.write(0x00, [TCA9538Def.OUTPUT_PORT_REGISTER, 0xFF])
        self.write(0x00, [TCA9538Def.POLARITY_INVERSION_REGISTERS, 0x00])
        self.write(0x00, [TCA9538Def.DIR_CONFIGURATION_REGISTERS, 0xFF])

    def dump(self):
        print(self._reg)

    def write(self, addr, wr_data):
        reg_addr = wr_data[0]
        wr_to_reg = [i for i in wr_data[1:]]
        for index in range(len(wr_to_reg)):
            self._reg[reg_addr + index] = [wr_to_reg[index]]

    def read(self, addr, wr_data, wr_len):
        raise NotImplementedError('TCA9538 no need to implement this function')

    def write_and_read(self, addr, wr_data, rd_len):
        reg_addr = wr_data[0]
        data = [self._reg[reg_addr + index][0] for index in range(rd_len)]
        return data
