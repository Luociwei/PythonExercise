# -*- coding: utf-8 -*-

__author__ = 'edison@trantest.com'
__version__ = '0.1'


class PCAL6524Def:
    REGISTER_ADDRESS = {
        "INPUT_PORT_0": 0x00,
        "INPUT_PORT_1": 0x01,
        "INPUT_PORT_2": 0x02,
        "OUTPUT_PORT_0": 0x04,
        "OUTPUT_PORT_1": 0x05,
        "OUTPUT_PORT_2": 0x06,
        "CONFIG_PORT_0": 0x0c,
        "CONFIG_PORT_1": 0x0d,
        "CONFIG_PORT_2": 0x0e,
        "PUPD_ENABLE_REGISTER_PORT_0": 0x4c,
        "PUPD_ENABLE_REGISTER_PORT_1": 0x4d,
        "PUPD_ENABLE_REGISTER_PORT_2": 0x4e,
        "PUPD_SELECTION_REGISTER_PORT_0": 0x50,
        "PUPD_SELECTION_REGISTER_PORT_1": 0x51,
        "PUPD_SELECTION_REGISTER_PORT_2": 0x52,
        "OUTPUT_PORT_CONFIGURATION": 0x5C,
        "INDIVIDUAL_PIN_OUTPUT_PORT_0_CONFIGURATION": 0x70,
        "INDIVIDUAL_PIN_OUTPUT_PORT_1_CONFIGURATION": 0x71,
        "INDIVIDUAL_PIN_OUTPUT_PORT_2_CONFIGURATION": 0x72

    }


class PCAL6524EmulatorPlugin(object):

    def __init__(self):
        self._reg = dict()
        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["INPUT_PORT_0"], 0xF0])
        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["INPUT_PORT_1"], 0xF0])
        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["INPUT_PORT_2"], 0xF0])
        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["OUTPUT_PORT_0"], 0xF0])
        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["OUTPUT_PORT_1"], 0xF0])
        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["OUTPUT_PORT_2"], 0xF0])
        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["CONFIG_PORT_0"], 0xF0])
        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["CONFIG_PORT_1"], 0xF0])
        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["CONFIG_PORT_2"], 0xF0])
        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["PUPD_ENABLE_REGISTER_PORT_0"], 0xF0])
        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["PUPD_ENABLE_REGISTER_PORT_1"], 0xF0])
        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["PUPD_ENABLE_REGISTER_PORT_2"], 0xF0])
        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["PUPD_SELECTION_REGISTER_PORT_0"], 0xF0])
        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["PUPD_SELECTION_REGISTER_PORT_1"], 0xF0])
        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["PUPD_SELECTION_REGISTER_PORT_2"], 0xF0])

        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["OUTPUT_PORT_CONFIGURATION"], 0xF0])
        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["INDIVIDUAL_PIN_OUTPUT_PORT_0_CONFIGURATION"], 0xF0])
        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["INDIVIDUAL_PIN_OUTPUT_PORT_1_CONFIGURATION"], 0xF0])
        self.write(0x00, [PCAL6524Def.REGISTER_ADDRESS["INDIVIDUAL_PIN_OUTPUT_PORT_2_CONFIGURATION"], 0xF0])

    def dump(self):
        print(self._reg)

    def write(self, addr, wr_data):
        reg_addr = wr_data[0]
        wr_to_reg = [i for i in wr_data[1:]]
        for index in range(len(wr_to_reg)):
            self._reg[reg_addr + index] = [wr_to_reg[index]]

    def read(self, addr, wr_data, wr_len):
        raise NotImplementedError('PCAL6524 no need to implement this function')

    def write_and_read(self, addr, wr_data, rd_len):
        reg_addr = wr_data[0]
        data = [self._reg[reg_addr + index][0] for index in range(rd_len)]
        return data
