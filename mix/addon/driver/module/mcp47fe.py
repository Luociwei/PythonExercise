# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator
import math
__author__ = 'Suncode_D@SunCode'
__version__ = '0.1'

class MCP47FEDef:
    DAC_REG = [0x00, 0x01, 0x02, 0x03,0x04,0x05,0x06,0x07]
    VREF_REG = 0x08
    GAIN_REG = 0x0A
    POWERDOWN_REG = 0x09

    VREF_EXTERN_BUF_ENABLE  = [0xFF ,0xFF]
    VREF_EXTERN_BUF_DISABLE = [0xAA ,0xAA]
    VREF_INTERNAL = [0x55 ,0x55]
    VREF_VDD = [0x00 ,0x00]
    GAIN_VALUE_2 = [0xFF,0x00]
    GAIN_VALUE_1 = [0x00,0x00]

    POWERDOWN_OPEN = [0xFF,0xFF]
    POWERDOWN_125K = [0xAA,0xAA]
    POWERDOWN_1K   = [0x55,0x55]
    POWERDOWN_NORM = [0x00,0x00]

    COMMAND_WRITE_TO_INPUT_REG = 0x00
    COMMAND_UPDATE_DAC_REG = 0x01
    COMMAND_WRITE_TO_INPUT_REG_AND_UPDATE_ALL = 0x02
    COMMAND_WRITE_AND_UPDATE_DAC_CHAN = 0x03
    COMMAND_POWER_UP_OR_DOWN = 0x04
    COMMAND_RESET = 0x05
    COMMAND_LDAC_SETUP = 0x06
    COMMAND_REFERENCE_SETUP = 0x07
    AD5667_RESLUTION = 16
    AD5647_RESLUTION = 14


class MCP47FE(object):
    '''
    AD5667r function class

    ClassType = DAC

    '''
    rpc_public_api = ['output_volt_dc']
    def __init__(self, dev_addr, i2c_bus,ref_mode):
        self.ref_mode = ref_mode
        self.i2c_bus = i2c_bus
        self.dev_addr = dev_addr
        self.set_reference(self.ref_mode)
        self.set_gain(1)
        self.set_power_down("POWERDOWN_NORM")

    def set_power_down(self,mode):
        assert mode in ["POWERDOWN_OPEN", "POWERDOWN_125K","POWERDOWN_1K","POWERDOWN_NORM"]
        if mode == "POWERDOWN_OPEN":
            self.write_operation(MCP47FEDef.POWERDOWN_REG, MCP47FEDef.POWERDOWN_OPEN)
        elif mode == "POWERDOWN_125K":
            self.write_operation(MCP47FEDef.POWERDOWN_REG, MCP47FEDef.POWERDOWN_125K)
        elif mode == "POWERDOWN_1K":
            self.write_operation(MCP47FEDef.POWERDOWN_REG, MCP47FEDef.POWERDOWN_1K)
        elif mode == "POWERDOWN_NORM":
            self.write_operation(MCP47FEDef.POWERDOWN_REG, MCP47FEDef.POWERDOWN_NORM)
        return 'done'

    def set_gain(self, gain):
        if gain == 1:
            self.write_operation(MCP47FEDef.GAIN_REG, MCP47FEDef.GAIN_VALUE_1)
        elif gain==2:
            self.write_operation(MCP47FEDef.GAIN_REG, MCP47FEDef.GAIN_VALUE_2)
        return 'done'
    def set_reference(self, ref_mode="VREF_INTERNAL"):
        assert ref_mode in ["VREF_EXTERN_BUF_ENABLE", "VREF_EXTERN_BUF_DISABLE","VREF_INTERNAL","VREF_VDD"]
        if ref_mode == "VREF_EXTERN_BUF_ENABLE":
            self.write_operation(MCP47FEDef.VREF_REG, MCP47FEDef.VREF_EXTERN_BUF_ENABLE)
        elif ref_mode == "VREF_EXTERN_BUF_DISABLE":
            self.write_operation(MCP47FEDef.VREF_REG, MCP47FEDef.VREF_EXTERN_BUF_DISABLE)
        elif ref_mode == "VREF_INTERNAL":
            self.write_operation(MCP47FEDef.VREF_REG, MCP47FEDef.VREF_INTERNAL)
        elif ref_mode == "VREF_VDD":
            self.write_operation(MCP47FEDef.VREF_REG, MCP47FEDef.VREF_VDD)
        return 'done'

    def output_volt_dc(self, channel, volt):
        '''
        MCP47FE output voltage

        Args:
            channel:    int, [1, 2, 3, 4, 5, 6, 7, 8]
            volt:       float/int, [DAC voltage], unit mV.

        Examples:
            mcp47fe.output_volt_dc(1, 1000)

        '''
        assert int(channel)>0 and int(channel)<9
        value = [0x00,0x00]
        value[1] = int(float(volt)/5120*255)
        print(value)
        print(MCP47FEDef.DAC_REG[int(channel)-1])
        ret = self.write_operation(MCP47FEDef.DAC_REG[int(channel)-1],value)
        if ret == 'done':
            return 'done'

    def read_operation(self):
        return self.i2c_bus.read(self.dev_addr, 3)

    def write_operation(self, reg_addr, data):
        reg_addr = reg_addr<<3
        data1 = [reg_addr] + data
        # data.insert(0,reg_addr)
        self.i2c_bus.write(self.dev_addr, data1)
        return 'done'
