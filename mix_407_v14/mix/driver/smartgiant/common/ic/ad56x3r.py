# -*- coding: utf-8 -*-
import time
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg_emulator import MIXQSPISGEmulator

__author__ = 'dongdongzhang@SmartGiant'
__version__ = '0.1'


class AD56X3RDef:

    COMMAND_WRITE_TO_INPUT_REG = 0x00
    COMMAND_UPDATE_DAC_REG = 0x01
    COMMAND_WRITE_TO_INPUT_REG_AND_UPDATE_ALL = 0x02
    COMMAND_WRITE_AND_UPDATE_DAC_CHAN = 0x03
    COMMAND_POWER_UP_OR_DOWN = 0x04
    COMMAND_RESET = 0x05
    COMMAND_LDAC_SETUP = 0x06
    COMMAND_REFERENCE_SETUP = 0x07
    AD5663_RESLUTION = 16
    AD5643_RESLUTION = 14
    AD5623_RESLUTION = 12


class AD56X3RException(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class AD56X3R(object):
    '''
    The AD5623R/AD5643R/AD5663R, members of the nanoDAC family, are low power, dual 12-, 14-, and 16-bit buffered
    voltageout digital-to-analog converters (DAC) that operate from a single 2.7 V to 5.5 V supply and are
    guaranteed monotonic by design.

    ClassType = DAC

    Args:
        spi_bus:    instance(QSPI)/None, Class instance of SPI bus,If not using this parameter,will create Emulator.
        mvref:      float, unit mV, default 2500.0, the reference voltage of AD56X3R.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_SPI_0', 256)
        spi = MIXQSPISG(axi)
        ad56x3r = AD56X3R(spi, 5000)

    '''
    def __init__(self, spi_bus=None, mvref=2500.0):
        if spi_bus is None:
            self.spi_bus = MIXQSPISGEmulator("ad56x3r_emulator", 256)
        else:
            self.spi_bus = spi_bus
        self.mvref = mvref
        self.resolution = AD56X3RDef.AD5663_RESLUTION
        self.ref_mode = "EXTERN"

    def write_operation(self, reg_addr, data):
        '''
        AD56X3R write register and data to address

        Args:
            reg_addr:  hexmial, [0~0xff], Write register to chip.
            data:      list, each element takes one byte,eg:[0x01,0x04].

        Examples:
            wr_data = [0x01, 0x04]
            ad56x3r.write_operation(0x00, wr_data)

        '''
        assert isinstance(reg_addr, int) and reg_addr >= 0
        assert isinstance(data, list)
        assert all(isinstance(x, int) and x >= 0 for x in data)
        write_data = [reg_addr] + data
        self.spi_bus.write(write_data)

    def reset(self, mode="ALL_REG"):
        '''
        AD56X3R reset chip

        Args:
            mode: string, ['DAC_AND_INPUT_SHIFT_REG', 'ALL_REG'], default 'ALL_REG'.

        Examples:
            ad56x3r.reset('ALL_REG')

        '''
        assert mode in ["DAC_AND_INPUT_SHIFT_REG", "ALL_REG"]
        software_reset_mode = {
            "DAC_AND_INPUT_SHIFT_REG": 0x00, "ALL_REG": 0x01}
        mode = software_reset_mode[mode]
        command = AD56X3RDef.COMMAND_RESET
        self.write_operation(command << 3, [0x00, mode])

    def select_work_mode(self, channel, mode="NORMAL"):
        '''
        AD56X3R select work mode

        Args:
            channel:    int, [0, 1, 2].                                          2 mean both channel
            mode:       strm ['NORMAL', '1KOHM_GND', '100KOHM_GND', 'HIGH-Z'), default 'NORMAL'.

        Examples:
            ad56x3r.select_work_mode(0, 'NORMAL')

        '''
        assert channel in [0, 1, 2]
        assert mode in ["NORMAL", "1KOHM_GND", "100KOHM_GND", "HIGH-Z"]
        operation_mode = {"NORMAL": 0x00, "1KOHM_GND": 0x01,
                          "100KOHM_GND": 0x02, "HIGH-Z": 0x03}
        mode = operation_mode[mode]
        channel_select = [0x01, 0x02, 0x03]
        command = AD56X3RDef.COMMAND_POWER_UP_OR_DOWN
        self.write_operation(
            command << 3, [0x00, channel_select[channel] | (mode << 4)])

    def set_ldac_pin_enable(self, channel):
        '''
        AD56X3R configure ldac pin enable

        Args:
            channel:    int, [0, 1, 2], 2 mean both channel

        Examples:
            ad56x3r.set_ldac_pin_enable(0)

        '''
        assert channel in [0, 1, 2]
        channel_select = [0x02, 0x01, 0x00]
        command = AD56X3RDef.COMMAND_LDAC_SETUP
        self.write_operation(command << 3, [0x00, channel_select[channel]])

    def set_ldac_pin_disable(self, channel):
        '''
        AD56X3R configure ldac pin disable

        Args:
            channel:    int, [0, 1, 2], 2 mean both channel

        Examples:
            ad56x3r.set_ldac_pin_disable(0)

        '''
        assert channel in [0, 1, 2]
        channel_select = [0x01, 0x02, 0x03]
        command = AD56X3RDef.COMMAND_LDAC_SETUP
        self.write_operation(command << 3, [0x00, channel_select[channel]])

    def set_reference(self, ref_mode="EXTERN"):
        '''
        AD56X3R set mode of reference voltage

        Args:
            ref_mode:  string, ['INTERNAL', 'EXTERN'], default 'EXTERN'.

        Examples:
            ad56x3r.set_reference('EXTERN')

        '''
        assert ref_mode in ["EXTERN", "INTERNAL"]
        self.ref_mode = ref_mode
        command = AD56X3RDef.COMMAND_REFERENCE_SETUP
        ref_mode_select = {"EXTERN": 0x00, "INTERNAL": 0x01}
        ref_mode = ref_mode_select[self.ref_mode]
        self.write_operation(command << 3, [0x00, ref_mode])

    def output_volt_dc(self, channel, volt):
        '''
        AD56X3R output voltage

        Args:
            channel:    int, [0, 1, 2], 2 mean both channel
            volt:       float/int, [0~reference voltage], unit mV.

        Examples:
            ad56x3r.output_volt_dc(0, 1000)

        '''
        assert channel in [0, 1, 2]
        assert isinstance(volt, (int, float)) and volt >= 0
        command = AD56X3RDef.COMMAND_WRITE_AND_UPDATE_DAC_CHAN
        dac_address = [0x00, 0x01, 0x07]
        code = int(volt * (0x1 << self.resolution) / self.mvref)
        if code == 1 << self.resolution:
            code = (1 << self.resolution) - 1
        code = code if self.ref_mode == "EXTERN" else code / 2
        code = code << (16 - self.resolution) & 0xffff

        self.write_operation(command << 3 | dac_address[channel], [code >> 8, code & 0xff])

    def initial(self):
        '''
        AD56X3R initial

        Examples:
            ad56x3r.initial()

        '''
        self.reset("ALL_REG")
        time.sleep(0.1)
        self.set_reference(self.ref_mode)
        self.set_ldac_pin_disable(2)
        self.select_work_mode(2, "NORMAL")


class AD5663R(AD56X3R):
    '''
    AD5663R function class

    ClassType = DAC

    Args:
        spi_bus:     instance(QSPI)/None, Class instance of SPI bus,If not using this parameter,will create Emulator.
        mvref:       float, unit mV, default 2500.0, the reference voltage of AD5663R.
        ref_mode:    string, ['EXTERN', 'INTERNAL'], defualt 'EXTERN', reference mode of AD5663R.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_SPI_0', 256)
        spi = MIXQSPISG(axi)
        ad5663r = AD5663R(spi, 5000, 'EXTERN')

    '''
    def __init__(self, spi_bus=None, mvref=2500.0, ref_mode="EXTERN"):
        super(AD5663R, self).__init__(spi_bus, mvref)
        self.resolution = AD56X3RDef.AD5663_RESLUTION
        self.ref_mode = ref_mode


class AD5643R(AD56X3R):
    '''
    AD5643R function class

    ClassType = DAC

    Args:
        spi_bus:     instance(QSPI)/None, Class instance of SPI bus,If not using this parameter,will create Emulator.
        mvref:       float, unit mV, default 2500.0, the reference voltage of AD5643R.
        ref_mode:    string, ['EXTERN', 'INTERNAL'], defualt 'EXTERN', reference mode of AD5643R.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_SPI_0', 256)
        spi = MIXQSPISG(axi)
        ad5643r = AD5643R(spi, 5000, 'EXTERN')

    '''
    def __init__(self, spi_bus=None, mvref=2500.0, ref_mode="EXTERN"):
        super(AD5643R, self).__init__(spi_bus, mvref)
        self.resolution = AD56X3RDef.AD5643_RESLUTION
        self.ref_mode = ref_mode


class AD5623R(AD56X3R):
    '''
    AD5623R function class

    ClassType = DAC

    Args:
        spi_bus:     instance(QSPI)/None, Class instance of SPI bus,If not using this parameter,will create Emulator.
        mvref:       float, unit mV, default 2500.0, the reference voltage of AD5623R.
        ref_mode:    string, ['EXTERN', 'INTERNAL'], defualt 'EXTERN', reference mode of AD5623R.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_SPI_0', 256)
        spi = MIXQSPISG(axi)
        ad5663r = AD5663R(spi, 5000, 'EXTERN')

    '''
    def __init__(self, spi_bus=None, mvref=2500.0, ref_mode="EXTERN"):
        super(AD5623R, self).__init__(spi_bus, mvref)
        self.resolution = AD56X3RDef.AD5623_RESLUTION
        self.ref_mode = ref_mode
