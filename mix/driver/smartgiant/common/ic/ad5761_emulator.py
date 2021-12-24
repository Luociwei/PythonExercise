# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *


__author__ = 'Jiasheng.Xie@SmartGiant'
__version__ = '0.1'


class AD57X1RDef:

    INPUT_REGISTER = 0x1
    UPDATE_DAC_REGISTER = 0x2
    DAC_REGISTER = 0x3
    CONTROL_REGISTER = 0x4
    SOFTWARE_DATA_RESET_REGISTER = 0x7
    READBACK_INPUT_REGISTER = 0xA
    READBACK_DAC_REGISTER = 0xB
    READBACK_CONTROL_REGISTER = 0xC
    SOFTWARE_FULL_RESET_REGISTER = 0xF

    CONTROL_REG_DATA = 0x0164
    DAC_REGISTER_WIDTH = 16
    VOLTAGE_UNIT = 1000
    VOLTAGE_REFER = 2500
    SPI_MODE = "MODE2"

    # CONTROL_REGISTER RA[0:2] to control output volt range
    OUTPUT_VOLT_RANGE_CONF = {
        0x0: [-10, 10],     # -10V ~ 10V
        0x1: [0, 10],       # 0V ~ 10V
        0x2: [-5, 5],       # -5V ~ 5V
        0x3: [0, 5],        # 0V ~ 5V
        0x4: [-2.5, 7.5],   # -2.5V ~ 7.5V
        0x5: [-3, 3],       # -3V ~ 3V
        0x6: [0, 16],       # 0V ~ 16V
        0x7: [0, 20]        # 0V ~ 20V
    }


class AD5761Emulator(object):
    '''
    AD5761 Emulator class
    '''

    def __init__(self, name='ad5761'):
        self.name = name

        self._recorder = Recorder()
        add_recorder(self._recorder)
        self._recorder.record("{}.__init__()".format(self.name))
        self.max_output_volt = 5000
        self.min_output_volt = 0
        self.full_scale_volt = self.max_output_volt - self.min_output_volt

        def set_mode(x, y):
            return y

        def set_speed(x, y):
            return y

        def get_mode(x):
            return "MODE2"

        SPI_BUS = type('IP', (), {"set_mode": set_mode, "set_speed": set_speed, "get_mode": get_mode})
        self.spi_bus = SPI_BUS()
        self._reg = {}
        self._volt = 0

    def write_control_register(self, reg_data):
        '''
        AD57X1R function write value to control register

        Args:
            reg_data:     hexmial, [0x00~0xffff],  Write the data.

        Examples:
            ad57x1r.write_control_register(0x1234)

        '''

        assert isinstance(reg_data, int) and (0xffff >= reg_data >= 0)

        self.max_output_volt = AD57X1RDef.OUTPUT_VOLT_RANGE_CONF[
            0x07 & reg_data][1] * AD57X1RDef.VOLTAGE_UNIT
        self.min_output_volt = AD57X1RDef.OUTPUT_VOLT_RANGE_CONF[
            0x07 & reg_data][0] * AD57X1RDef.VOLTAGE_UNIT
        self.full_scale_volt = self.max_output_volt - self.min_output_volt
        self.m = self.full_scale_volt / AD57X1RDef.VOLTAGE_REFER
        self.c = abs(self.min_output_volt / AD57X1RDef.VOLTAGE_REFER)
        self.write_register(AD57X1RDef.CONTROL_REGISTER, reg_data)

    def write_register(self, reg_addr, reg_data):
        '''
        AD57X1R function write value to register

        Args:
            reg_addr:     hexmial, [0x00~0xff], Register address.
            reg_data:     hexmial, [0x00~0xffff], Write to the register.

        Examples:
            ad57x1r.write_register(0x22, 0xff)

        '''

        assert isinstance(reg_addr, int) and isinstance(reg_data, int)
        assert (reg_addr >= 0) and (
            reg_data >= 0x0000) and (reg_data <= 0xffff)
        # only the low 4 bit is valid in reg_addr
        write_data = [reg_addr & 0x0F, reg_data >> 8 & 0xFF, reg_data & 0xFF]
        self._recorder.record("{}.write_register({}, {})".format(self.name, reg_addr, reg_data))
        self._reg[reg_addr] = write_data[1:]
        # self.spi_bus.write(write_data)

    def read_register(self, reg_addr):
        '''
        AD57X1R function to read register

        Args:
            reg_addr:     hexmial, [0x00~0xff], Register address.

        Returns:
            list, [value], data list.

        Examples:
            ad57x1r.read_register(0x22)

        '''

        assert isinstance(reg_addr, int) and reg_addr >= 0

        # tell the ad57x1 the address we are going to read,
        # 0x0 is invalid, use 0x0 to put together to 3 bytes.
        # self.write_register(reg_addr, 0x0)

        # # register width is 24 bits wide, 3 bytes
        # read_data_list = self.spi_bus.read(3)
        # if not read_data_list:
        #     raise AD57X1RException(
        #         "An error occurred when read data from AD57X1R register ")
        # # The high byte is register address, only low 4 bit is valid.
        # if reg_addr != (read_data_list[0] & 0x0F):
        #     raise AD57X1RException(
        #         "An error occurred when read the wrong address")
        self._recorder.record("{}.read_register({})".format(self.name, reg_addr))
        return self._reg[reg_addr]

    def output_volt_dc(self, channel, volt):
        '''
        AD57X1R function set output voltage

        Args:
            channel:    int, [0], Channel index must be zero.
            volt:       int, [0~Vref], unit mV.

        Examples:
            ad57x1r.output_voltage(500)

        '''
        assert channel == 0
        assert isinstance(volt, (float, int))
        assert (volt >= self.min_output_volt) and (
            volt <= self.max_output_volt)

        '''
        Vout = Vref * [(M * D / pow(2, N)) - C]
        Vref is 2.5 V
        M is the slope for a given output range
        D is the decimal equivalent of the code loaded to the DAC
        N is the number of bits
        C is the offset for a given output range
        '''
        # code = int((float(volt) / self.vref + self.c) /
        #            self.m * pow(2, self.data_width))
        # code = code << (AD57X1RDef.DAC_REGISTER_WIDTH - self.data_width)

        # self.write_register(AD57X1RDef.DAC_REGISTER, code)
        self._recorder.record("{}.output_volt_dc({}, {})".format(self.name, channel, volt))
        self._volt = volt

    def readback_output_voltage(self):
        '''
        AD57X1R function readback output voltage

        Returns:
            float, value, unit mV, the voltage value.

        Raises:
            AD57X1RException: An error occurred when get output voltage from AD57X1R fail.

        Examples:
            volt = ad57x1r.readback_output_voltage()
            print(volt)

        '''
        # recv_list = self.read_register(AD57X1RDef.READBACK_DAC_REGISTER)

        # if recv_list is None:
        #     raise AD57X1RException(
        #         "An error occurred when get output voltage from AD57X1R fail.")

        # code = (recv_list[0] << 8) | recv_list[1]
        # code = float(code >> (AD57X1RDef.DAC_REGISTER_WIDTH - self.data_width))
        # volt = self.vref * (self.m * code / pow(2, self.data_width) - self.c)
        self._recorder.record("{}.readback_output_voltage()".format(self.name))

        return self._volt
