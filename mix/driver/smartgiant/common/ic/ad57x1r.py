# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg_emulator import MIXQSPISGEmulator

__author__ = 'zijianxu@SmartGiant'
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


class AD57X1RException(Exception):
    '''
    AD57X1RException shows the exception of AD57X1R

    :example:
              raise AD57X1RException("Error str")
    '''

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class AD57X1R(object):
    '''
    AD57X1R class provide function write and read register output voltage.

    ClassType = DAC

    Args:
        mvref:       int, default 2500.0, the reference voltage.
        spi_bus:     instance(QSPI)/None, Class instance of I2C bus, if not using the parameter will create Emulator.

    Examples:
        axi = AXI4LiteBus("/dev/XXX", PLSPIDef.REG_SIZE)
        spi_bus = MIXQSPISG(axi)
        ad57x1r = AD57X1R(16, 2500, spi_bus)

    '''
    def __init__(self, mvref=2500, spi_bus=None):
        if spi_bus is None:
            self.spi_bus = MIXQSPISGEmulator("ad57x1r_emulator", 256)
        else:
            self.spi_bus = spi_bus
        # "MODE2" means CPOL=1, CPHA=0
        self.spi_bus.set_mode(AD57X1RDef.SPI_MODE)
        self.data_width = 16

        if (AD57X1RDef.CONTROL_REG_DATA & 0x20) == 0x20:
            self.vref = AD57X1RDef.VOLTAGE_REFER
        else:
            self.vref = mvref

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
        assert (reg_addr >= 0x0) and (reg_data <= 0xffff)

        if reg_addr == AD57X1RDef.CONTROL_REGISTER:
            self.max_output_volt = AD57X1RDef.OUTPUT_VOLT_RANGE_CONF[
                0x07 & reg_data][1] * AD57X1RDef.VOLTAGE_UNIT
            self.min_output_volt = AD57X1RDef.OUTPUT_VOLT_RANGE_CONF[
                0x07 & reg_data][0] * AD57X1RDef.VOLTAGE_UNIT
            self.full_scale_volt = self.max_output_volt - self.min_output_volt
            self.m = self.full_scale_volt / AD57X1RDef.VOLTAGE_REFER
            self.c = abs(self.min_output_volt / AD57X1RDef.VOLTAGE_REFER)

        # only the low 4 bit is valid in reg_addr
        write_data = [reg_addr & 0x0F, reg_data >> 8 & 0xFF, reg_data & 0xFF]
        self.spi_bus.write(write_data)

    def read_register(self, reg_addr):
        '''
        AD57X1R function to read register

        Args:
            reg_addr:     hexmial, [0x00~0xff], Register address.

        Returns:
            list, [value], data list.

        Raises:
            AD57X1RException: An error occurred when read data.

        Examples:
            ad57x1r.read_register(0x22)

        '''

        assert isinstance(reg_addr, int) and reg_addr >= 0

        # tell the ad57x1 the address we are going to read,
        # 0x0 is invalid, use 0x0 to put together to 3 bytes.
        self.write_register(reg_addr, 0x0)

        # register width is 24 bits wide, 3 bytes
        read_data_list = self.spi_bus.read(3)
        if not read_data_list:
            raise AD57X1RException(
                "An error occurred when read data from AD57X1R register ")
        # The high byte is register address, only low 4 bit is valid.
        if reg_addr != (read_data_list[0] & 0x0F):
            raise AD57X1RException(
                "An error occurred when read the wrong address")

        return read_data_list[1:]

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
        code = int((float(volt) / self.vref + self.c) /
                   self.m * pow(2, self.data_width) + 0.5)
        code = code << (AD57X1RDef.DAC_REGISTER_WIDTH - self.data_width)
        if code >= pow(2, self.data_width):
            code = pow(2, self.data_width) - 1

        self.write_register(AD57X1RDef.DAC_REGISTER, code)

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
        recv_list = self.read_register(AD57X1RDef.READBACK_DAC_REGISTER)

        if recv_list is None:
            raise AD57X1RException(
                "An error occurred when get output voltage from AD57X1R fail.")

        code = (recv_list[0] << 8) | recv_list[1]
        code = float(code >> (AD57X1RDef.DAC_REGISTER_WIDTH - self.data_width))
        volt = self.vref * (self.m * code / pow(2, self.data_width) - self.c)

        return volt


class AD5761(AD57X1R):
    '''
    AD5761 function class

    ClassType = DAC

    Args:
        mvref:       int, default 2500.0, the reference voltage.
        spi_bus:     instance(QSPI)/None, Class instance of I2C bus, if not using the parameter will create Emulator.

    Examples:
        axi4 = AXI4LiteBus("/dev/XXX", PLSPIDef.REG_SIZE)
        spi_bus = MIXQSPISG(axi4)
        ad5761 = AD5761(16, 2500, spi_bus)

    '''

    def __init__(self, mvref=2500, spi_bus=None):

        super(AD5761, self).__init__(mvref, spi_bus)
        self.data_width = 16
